from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
import base64
from utils import send_email
 
app = Flask(__name__)
app.secret_key = "pgeats6708"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pgeats_sb9b_user:8eYRKUxK27GAOLQqNTzVLCxglCKBly7Q@dpg-cvt68oqdbo4c73cirjj0-a.singapore-postgres.render.com/pgeats_sb9b'
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
    image_data = db.Column(db.LargeBinary)

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
    image_data = db.Column(db.LargeBinary)

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
                        image_data = file.read() 
                        new_image = RoomImage(room_id=new_room.id, image_data=image_data)
                        db.session.add(new_image)
                        db.session.commit()

        send_email(
            subject="New PG Listing Submitted",
            body=f"A new PG has been added.\n\nPG Name: {pg_name}\nView Details: https://yumma.onrender.com/pg-details/{new_pg.id}"
        )

        return "PG Details Submitted Successfully!"

    return render_template("form.html")

@app.route("/get_image/<int:image_id>")
def get_image(image_id):
    image = RoomImage.query.get(image_id)
    if image:
        return f'<img src="data:image/jpeg;base64,{base64.b64encode(image.image_data).decode()}" />'
    return "Image Not Found", 404

@app.template_filter("b64encode")
def b64encode_filter(data):
    return base64.b64encode(data).decode("utf-8")

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

            send_email(
                subject="New Tiffin Services Listing Submitted",
                body=f"A new Tiffin Services has been added.\n\nFood Name: {EATS_name}\nView Details: https://yumma.onrender.com/EATS-details/{new_EATS.id}"
            )

            image_files = request.files.getlist(f"images_{i}")
            for file in image_files:
                if file and file.filename != "":
                    image_data = file.read() 
                    new_image = FoodImage(food_id=new_food.id, image_data=image_data)
                    db.session.add(new_image)
                    db.session.commit()

        return "EATS Details Submitted Successfully!"

    return render_template("food_form.html")

@app.route("/get_food_image/<int:image_id>")
def get_food_image(image_id):
    image = FoodImage.query.get(image_id)
    if image:
        return f'<img src="data:image/jpeg;base64,{base64.b64encode(image.image_data).decode()}" />'
    return "Image Not Found", 404

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

@app.route('/delete-pg/<int:pg_id>', methods=['POST'])
def delete_pg(pg_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))

    pg = PGDetails.query.get_or_404(pg_id)

    rooms = Room.query.filter_by(pg_id=pg_id).all()
    for room in rooms:
        RoomImage.query.filter_by(room_id=room.id).delete()
        db.session.delete(room)

    db.session.delete(pg)
    db.session.commit()
    
    flash("PG deleted successfully!", "success")
    return redirect(url_for('pg_list'))  

@app.route('/delete-EATS/<int:EATS_id>', methods=['POST'])
def delete_EATS(EATS_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))

    EATS = EATSDetails.query.get_or_404(EATS_id)

    foods = Food.query.filter_by(EATS_id=EATS_id).all()
    for food in foods:
        FoodImage.query.filter_by(food_id=food.id).delete()
        db.session.delete(food)

    db.session.delete(EATS)
    db.session.commit()
    
    flash("EATS deleted successfully!", "success")
    return redirect(url_for('EATS_list'))

class HotelDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    email = db.Column(db.String(100))
    hotel_name = db.Column(db.String(200))
    city = db.Column(db.String(100))
    area = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    address = db.Column(db.Text)
    facilities = db.Column(db.Text)
    rules = db.Column(db.Text)
    rooms = db.relationship('HotelRoom', backref='hotel', lazy=True)

class HotelRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel_details.id'), nullable=False)
    room_type = db.Column(db.String(20))
    food = db.Column(db.String(20))
    room_size = db.Column(db.String(20))
    price = db.Column(db.String(20))
    available_room = db.Column(db.Integer)
    images = db.relationship('HotelRoomImage', backref='room', lazy=True)

class HotelRoomImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('hotel_room.id'), nullable=False)
    image_path = db.Column(db.String(300))
    image_data = db.Column(db.LargeBinary)

@app.route("/hotel", methods=["GET", "POST"])
def hotel_form():
    if request.method == "POST":
        name = request.form["name"]
        whatsapp = request.form["whatsapp"]
        email = request.form["email"]
        hotel_name = request.form["hotel_name"]
        city = request.form["city"]
        area = request.form["area"]
        pincode = request.form["pincode"]
        address = request.form["address"]
        facilities = request.form["facilities"]
        rules = request.form["rules"]

        new_hotel = HotelDetails(
            name=name, whatsapp=whatsapp, email=email, 
            hotel_name=hotel_name, city=city, area=area, 
            pincode=pincode, address=address, 
            facilities=facilities, rules=rules
        )
        db.session.add(new_hotel)
        db.session.commit()

        room_count = int(request.form.get("room_count", 1))  

        for i in range(room_count):
            room_key = f"room_type_{i}"  
            if room_key in request.form:
                room_type = request.form[f"room_type_{i}"]
                food = request.form[f"food_{i}"]
                room_size = request.form[f"room_size_{i}"]
                price = request.form[f"price_{i}"]
                available_room = request.form[f"available_room_{i}"]

                new_room = HotelRoom(
                    hotel_id=new_hotel.id, room_type=room_type, 
                    food=food, room_size=room_size, 
                    price=price, available_room=available_room
                )
                db.session.add(new_room)
                db.session.commit()
             
                send_email(
                    subject="New Hotel Listing Submitted",
                    body=f"A new Hotel has been added.\n\nHotel Name: {hotel_name}\nView Details: https://yumma.onrender.com/hotel-details/{new_hotel.id}"
                )
                
                image_files = request.files.getlist(f"images_{i}")
                for file in image_files:
                    if file and file.filename != "":
                        image_data = file.read() 
                        new_image = HotelRoomImage(room_id=new_room.id, image_data=image_data)
                        db.session.add(new_image)
                        db.session.commit()

        return "Hotel Details Submitted Successfully!"

    return render_template("hotel_form.html")

@app.route("/hotel_get_image/<int:image_id>")
def hotel_get_image(image_id):
    image = HotelRoomImage.query.get(image_id)
    if image:
        return f'<img src="data:image/jpeg;base64,{base64.b64encode(image.image_data).decode()}" />'
    return "Image Not Found", 404

@app.route('/hotel-list')
def hotel_list():
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))
    
    hotel_details = HotelDetails.query.all()
    return render_template('hotel_display.html', hotel_details=hotel_details)

@app.route('/hotel-details/<int:hotel_id>')
def hotel_details(hotel_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))
    
    hotel = HotelDetails.query.get_or_404(hotel_id)
    rooms = HotelRoom.query.filter_by(hotel_id=hotel_id).all()

    for room in rooms:
        room.images = HotelRoomImage.query.filter_by(room_id=room.id).all()

    return render_template('hotel_details.html', hotel=hotel, rooms=rooms)

@app.route('/delete-hotel/<int:hotel_id>', methods=['POST'])
def delete_hotel(hotel_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))

    hotel = HotelDetails.query.get_or_404(hotel_id)

    rooms = HotelRoom.query.filter_by(hotel_id=hotel_id).all()
    for room in rooms:
        HotelRoomImage.query.filter_by(room_id=room.id).delete()
        db.session.delete(room)

    db.session.delete(hotel)
    db.session.commit()
    
    flash("Hotel deleted successfully!", "success")
    return redirect(url_for('hotel_list'))  

class RestaurantDetails(db.Model):
    __tablename__ = 'Restaurant_details'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    Restaurant_name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    order_time_morning_start = db.Column(db.String(10), nullable=True)
    order_time_morning_end = db.Column(db.String(10), nullable=True)

    meals = db.relationship('Meal', backref='Restaurant', lazy=True, cascade="all, delete")

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Restaurant_id = db.Column(db.Integer, db.ForeignKey('Restaurant_details.id'), nullable=False)
    meal_type = db.Column(db.String(50), nullable=False)
    meal_name = db.Column(db.String(100), nullable=False) 
    price = db.Column(db.Float, nullable=False)  

    images = db.relationship('MealImage', backref='meal', lazy=True, cascade="all, delete")

class MealImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    image_data = db.Column(db.LargeBinary)

@app.route("/meal", methods=["GET", "POST"])
def Restaurant_form():
    if request.method == "POST":
        name = request.form["name"]
        whatsapp = request.form["whatsapp"]
        email = request.form["email"]
        Restaurant_name = request.form["Restaurant_name"]
        city = request.form["city"]
        area = request.form["area"]
        pincode = request.form["pincode"]
        address = request.form["address"]

        order_time_morning_start = request.form.get("order_time_morning_start", "").strip() or None
        order_time_morning_end = request.form.get("order_time_morning_end", "").strip() or None

        new_Restaurant = RestaurantDetails(
            name=name, whatsapp=whatsapp, email=email, 
            Restaurant_name=Restaurant_name, city=city, area=area, 
            pincode=pincode, address=address,
            order_time_morning_start=order_time_morning_start,
            order_time_morning_end=order_time_morning_end
        )
        db.session.add(new_Restaurant)
        db.session.commit()

        meal_count = int(request.form.get("meal_count", 1))

        for i in range(meal_count):
            meal_option = request.form.get(f"meal_option_{i}", "").strip() or "Unknown"
            price = request.form.get(f"price_{i}", "0").strip() or "0"
            meal_items = request.form.get(f"meal_items_{i}", "").strip() or "Not Specified"

            try:
                price = float(price)
            except ValueError:
                price = 0.0

            new_meal = Meal(
                Restaurant_id=new_Restaurant.id,
                meal_type=meal_option, 
                meal_name=meal_items,  
                price=price
            )
            db.session.add(new_meal)
            db.session.commit()

            send_email(
                subject="New Restaurant Listing Submitted",
                body=f"A new Restaurant has been added.\n\nRestaurant Name: {Restaurant_name}\nView Details: https://yumma.onrender.com/Restaurant-details/{new_Restaurant.id}"
            )

            image_files = request.files.getlist(f"images_{i}")
            for file in image_files:
                if file and file.filename != "":
                    image_data = file.read() 
                    new_image = MealImage(meal_id=new_meal.id, image_data=image_data)
                    db.session.add(new_image)
                    db.session.commit()

        return "Restaurant Details Submitted Successfully!"

    return render_template("meal_form.html")

@app.route("/get_meal_image/<int:image_id>")
def get_meal_image(image_id):
    image = MealImage.query.get(image_id)
    if image:
        return f'<img src="data:image/jpeg;base64,{base64.b64encode(image.image_data).decode()}" />'
    return "Image Not Found", 404

@app.route('/Restaurant-list')
def Restaurant_list():
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))
    
    Restaurant_details = RestaurantDetails.query.all()  
    
    return render_template('meal_display.html', restaurant=Restaurant_details)

@app.route('/Restaurant-details/<int:Restaurant_id>')
def Restaurant_details(Restaurant_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))
    
    Restaurant = RestaurantDetails.query.get(Restaurant_id)

    if not Restaurant:
        print(f"Restaurant ID {Restaurant_id} not found!")
        return "Restaurant not found", 404

    meals = Meal.query.filter_by(Restaurant_id=Restaurant_id).all()

    print(f"Restaurant Found: {Restaurant.Restaurant_name}, Meals Count: {len(meals)}")

    for meal in meals:
        meal.images = MealImage.query.filter_by(meal_id=meal.id).all()
        print(f"Meal: {meal.meal_name}, Type: {meal.meal_type}, Price: {meal.price}, Images: {len(meal.images)}")

    return render_template('Restaurant_details.html', Restaurant=Restaurant, meals=meals)

@app.route('/delete-Restaurant/<int:Restaurant_id>', methods=['POST'])
def delete_Restaurant(Restaurant_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access! Please Login.", "danger")
        return redirect(url_for('admin_login'))

    Restaurant = RestaurantDetails.query.get_or_404(Restaurant_id)

    meals = Meal.query.filter_by(Restaurant_id=Restaurant_id).all()
    for meal in meals:
        MealImage.query.filter_by(meal_id=meal.id).delete()
        db.session.delete(meal)

    db.session.delete(Restaurant)
    db.session.commit()
    
    flash("Restaurant deleted successfully!", "success")
    return redirect(url_for('Restaurant_list'))

@app.route('/')
def home():
    return render_template('home.html')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
