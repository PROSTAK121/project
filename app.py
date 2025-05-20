from flask import Flask, request, jsonify, render_template
from geopy.geocoders import Nominatim
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///locations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель для хранения местоположений
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Создание таблиц при первом запуске
with app.app_context():
    db.create_all()

# Геолокатор
geolocator = Nominatim(user_agent="geoapi")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/location', methods=['POST'])
def get_location():
    data = request.get_json()
    lat = data['latitude']
    lon = data['longitude']

    location = geolocator.reverse((lat, lon), language='ru')
    address = location.address if location else "Адрес не найден"

    new_loc = Location(latitude=lat, longitude=lon, address=address)
    db.session.add(new_loc)
    db.session.commit()

    return jsonify({'address': address})

@app.route('/history')
def history():
    locations = Location.query.order_by(Location.timestamp.desc()).limit(20).all()
    return render_template('history.html', locations=locations)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
