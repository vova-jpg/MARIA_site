import os
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

app = Flask(__name__, static_folder='../frontend', static_url_path='')
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tarot.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=True)
    subscription_status = db.Column(db.String(20), default='free')
    persona_tag = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class CardContent(db.Model):
    __tablename__ = 'cards_content'
    card_id = db.Column(db.Integer, primary_key=True)
    card_name = db.Column(db.String(80), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    text_sos_state = db.Column(db.Text, nullable=True)
    text_sos_resource = db.Column(db.Text, nullable=True)
    text_sos_action = db.Column(db.Text, nullable=True)
    text_daily = db.Column(db.Text, nullable=True)
    text_love_self = db.Column(db.Text, nullable=True)

class ReadingHistory(db.Model):
    __tablename__ = 'readings_history'
    reading_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    spread_type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.now())
    cards_drawn = db.Column(db.String(100), nullable=False)  # Storing as a JSON string for simplicity
    user_notes = db.Column(db.Text, nullable=True)

import json

...

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    reading = data.get('reading')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    new_user = User(email=email, name=name)
    db.session.add(new_user)
    db.session.commit()

    if reading:
        cards_drawn = [card['card_id'] for card in reading]
        new_reading = ReadingHistory(
            user_id=new_user.user_id,
            spread_type='sos',
            cards_drawn=json.dumps(cards_drawn)
        )
        db.session.add(new_reading)
        db.session.commit()

    return jsonify({'user_id': new_user.user_id, 'message': 'User created successfully'}), 201

@app.route('/api/reading', methods=['POST'])
def get_reading():
    available_cards = CardContent.query.all()
    if len(available_cards) < 3:
        return jsonify({'error': 'Not enough cards in the database'}), 500

    selected_cards = random.sample(available_cards, 3)

    reading = {
        'cards': [
            {
                'card_id': selected_cards[0].card_id,
                'name': selected_cards[0].card_name,
                'position': 1,
                'meaning': selected_cards[0].text_sos_state
            },
            {
                'card_id': selected_cards[1].card_id,
                'name': selected_cards[1].card_name,
                'position': 2,
                'meaning': selected_cards[1].text_sos_resource
            },
            {
                'card_id': selected_cards[2].card_id,
                'name': selected_cards[2].card_name,
                'position': 3,
                'meaning': selected_cards[2].text_sos_action
            }
        ]
    }
    return jsonify(reading)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
