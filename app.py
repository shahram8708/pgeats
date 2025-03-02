from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "pgeats6708"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pgeats_user:WgFdsAcOjUPKYK611PiwkKkjhCPmPqfH@dpg-cv241h0gph6c73bcfcb0-a.singapore-postgres.render.com/pgeats'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

class PGDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    email = db.Column(db.String(100))
    pg_name = db.Column(db.String(200))
    city = db.Column(db.String(100))
    area = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    address = db.Column(db.Text)
    facilities = db.Column(db.Text)
    rules = db.Column(db.Text)
    rooms = db.relationship('Room', backref='pg', lazy=True)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pg_id = db.Column(db.Integer, db.ForeignKey('pg_details.id'), nullable=False)
    room_type = db.Column(db.String(20))
    food = db.Column(db.String(20))
    room_size = db.Column(db.String(20))
    price = db.Column(db.String(20))
    room_sharing = db.Column(db.Integer)
    images = db.relationship('RoomImage', backref='room', lazy=True)

class RoomImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    image_path = db.Column(db.String(300))

class EATSDetails(db.Model):
    __tablename__ = 'EATS_details'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    EATS_name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    order_time_morning_start = db.Column(db.String(10), nullable=True)
    order_time_morning_end = db.Column(db.String(10), nullable=True)
    order_time_night_start = db.Column(db.String(10), nullable=True)
    order_time_night_end = db.Column(db.String(10), nullable=True)

    delivery_time_morning_start = db.Column(db.String(10), nullable=True)
    delivery_time_morning_end = db.Column(db.String(10), nullable=True)
    delivery_time_night_start = db.Column(db.String(10), nullable=True)
    delivery_time_night_end = db.Column(db.String(10), nullable=True)

    foods = db.relationship('Food', backref='EATS', lazy=True, cascade="all, delete")

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    EATS_id = db.Column(db.Integer, db.ForeignKey('EATS_details.id'), nullable=False)
    food_type = db.Column(db.String(50), nullable=False)
    food_name = db.Column(db.String(100), nullable=False) 
    price = db.Column(db.Float, nullable=False)  

    images = db.relationship('FoodImage', backref='food', lazy=True, cascade="all, delete")

class FoodImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)

with app.app_context():
    db.create_all()

ADMIN_EMAIL = "admin@pgeats.com"
ADMIN_PASSWORD = "pgeats6708"

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash("Login Successful!", "success")
            return redirect(url_for('pg_list'))
        else:
            flash("Invalid Credentials!", "danger")

    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged Out Successfully!", "info")
    return redirect(url_for('admin_login'))

@app.route("/pg", methods=["GET", "POST"])
def pg_form():
    if request.method == "POST":
        name = request.form["name"]
        whatsapp = request.form["whatsapp"]
        email = request.form["email"]
        pg_name = request.form["pg_name"]
        city = request.form["city"]
        area = request.form["area"]
        pincode = request.form["pincode"]
        address = request.form["address"]
        facilities = request.form["facilities"]
        rules = request.form["rules"]

        new_pg = PGDetails(
            name=name, whatsapp=whatsapp, email=email, 
            pg_name=pg_name, city=city, area=area, 
            pincode=pincode, address=address, 
            facilities=facilities, rules=rules
        )
        db.session.add(new_pg)
        db.session.commit()

        room_count = int(request.form.get("room_count", 1))  

        for i in range(room_count):
            room_key = f"room_type_{i}"  
            if room_key in request.form:
                room_type = request.form[f"room_type_{i}"]
                food = request.form[f"food_{i}"]
                room_size = request.form[f"room_size_{i}"]
                price = request.form[f"price_{i}"]
                room_sharing = request.form[f"room_sharing_{i}"]

                new_room = Room(
                    pg_id=new_pg.id, room_type=room_type, 
                    food=food, room_size=room_size, 
                    price=price, room_sharing=room_sharing
                )
                db.session.add(new_room)
                db.session.commit()
                
                image_files = request.files.getlist(f"images_{i}")
                for file in image_files:
                    if file and file.filename != "":
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)

                        relative_path = f"uploads/{filename}".replace("\\", "/")

                        new_image = RoomImage(room_id=new_room.id, image_path=relative_path)
                        db.session.add(new_image)
                        db.session.commit()

        return "PG Details Submitted Successfully!"

    return render_template("form.html")

@app.route("/food", methods=["GET", "POST"])
def EATS_form():
    if request.method == "POST":
        name = request.form["name"]
        whatsapp = request.form["whatsapp"]
        email = request.form["email"]
        EATS_name = request.form["EATS_name"]
        city = request.form["city"]
        area = request.form["area"]
        pincode = request.form["pincode"]
        address = request.form["address"]

        order_time_morning_start = request.form.get("order_time_morning_start", "").strip() or None
        order_time_morning_end = request.form.get("order_time_morning_end", "").strip() or None
        order_time_night_start = request.form.get("order_time_night_start", "").strip() or None
        order_time_night_end = request.form.get("order_time_night_end", "").strip() or None

        delivery_time_morning_start = request.form.get("delivery_time_morning_start", "").strip() or None
        delivery_time_morning_end = request.form.get("delivery_time_morning_end", "").strip() or None
        delivery_time_night_start = request.form.get("delivery_time_night_start", "").strip() or None
        delivery_time_night_end = request.form.get("delivery_time_night_end", "").strip() or None

        new_EATS = EATSDetails(
            name=name, whatsapp=whatsapp, email=email, 
            EATS_name=EATS_name, city=city, area=area, 
            pincode=pincode, address=address,
            order_time_morning_start=order_time_morning_start,
            order_time_morning_end=order_time_morning_end,
            order_time_night_start=order_time_night_start,
            order_time_night_end=order_time_night_end,
            delivery_time_morning_start=delivery_time_morning_start,
            delivery_time_morning_end=delivery_time_morning_end,
            delivery_time_night_start=delivery_time_night_start,
            delivery_time_night_end=delivery_time_night_end
        )
        db.session.add(new_EATS)
        db.session.commit()

        food_count = int(request.form.get("food_count", 1))

        for i in range(food_count):
            food_key = f"food_option_{i}"
            if food_key in request.form:
                food_option = request.form.get(f"food_option_{i}", "").strip() or "Unknown"
                price = request.form.get(f"price_{i}", "0").strip() or "0"
                food_items = request.form.get(f"food_items_{i}", "").strip() or "Not Specified"

                try:
                    price = float(price)
                except ValueError:
                    price = 0.0

                new_food = Food(
                    EATS_id=new_EATS.id,
                    food_type=food_option, 
                    food_name=food_items,  
                    price=price
                )
                db.session.add(new_food)
                db.session.commit()

                image_files = request.files.getlist(f"images_{i}")
                for file in image_files:
                    if file and file.filename != "":
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)

                        relative_path = f"uploads/{filename}".replace("\\", "/")

                        new_image = FoodImage(food_id=new_food.id, image_path=relative_path)
                        db.session.add(new_image)
                        db.session.commit()

        return "EATS Details Submitted Successfully!"

    return render_template("food_form.html")

@app.route('/pg-list')
def pg_list():
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))
    
    pg_details = PGDetails.query.all()
    return render_template('display.html', pg_details=pg_details)

@app.route('/EATS-list')
def EATS_list():
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))
    
    EATS_details = EATSDetails.query.all()  
    
    return render_template('food_display.html', eats=EATS_details)

@app.route('/pg-details/<int:pg_id>')
def pg_details(pg_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))
    
    pg = PGDetails.query.get_or_404(pg_id)
    rooms = Room.query.filter_by(pg_id=pg_id).all()

    for room in rooms:
        room.images = RoomImage.query.filter_by(room_id=room.id).all()

    return render_template('pg_details.html', pg=pg, rooms=rooms)

@app.route('/EATS-details/<int:EATS_id>')
def EATS_details(EATS_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))
    
    EATS = EATSDetails.query.get_or_404(EATS_id)
    foods = Food.query.filter_by(EATS_id=EATS_id).all()

    for food in foods:
        food.images = FoodImage.query.filter_by(food_id=food.id).all()

    return render_template('EATS_details.html', EATS=EATS, foods=foods)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
