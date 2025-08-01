import ipinfo
import geocoder
from flask import Flask, request, render_template
import sqlite3
from datetime import datetime
import joblib
import numpy as np
import os
from twilio.rest import Client  # Twilio for SMS

app = Flask(__name__)

# Load trained model
model = joblib.load('model_rf.pkl')

# SQLite DB path
DB_NAME = 'db/logs.db'

# Create DB if not exists
def init_db():
    if not os.path.exists('db'):
        os.makedirs('db')
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS attack_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT,
                ip_address TEXT,
                timestamp TEXT,
                prediction TEXT,
                location_city TEXT,
                location_country TEXT
            )
        ''')
        conn.commit()

init_db()

# Send SMS if malicious
def send_sms_alert(username, ip_address, timestamp, city, country):
    account_sid = 'AC3162353369a7e1bc62bad2f0e5e15979'
    auth_token = 'b075e6faf343a57f5451e0688394b5f9'
    from_number = '+12179125130'   # Twilio trial number
    to_number = '+917795134556'    # Your verified number

    message_body = (
        f'🚨 Malicious login detected!\n'
        f'👤 Username: {username}\n'
        f'📍 IP: {ip_address}\n'
        f'🌐 Location: {city}, {country}\n'
        f'🕒 Time: {timestamp}'
    )

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message_body,
        from_=from_number,
        to=to_number
    )
    print("✅ SMS alert sent:", message.sid)

# Prediction logic
def predict_attack(features):
    prediction = model.predict([features])
    return prediction[0]

@app.route('/')
def fake_login():
    return render_template('fake_login.html')

@app.route('/log-attempt', methods=['POST'])
def log_attempt():
    username = request.form.get('username')
    password = request.form.get('password')

    # Use this for testing with public IP:
    ip_address = request.remote_addr
  # Simulated IP for testing

    # Use this for actual deployment:
    # ip_address = request.remote_addr

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # GeoIP lookup
    try:
        access_token = '339c51ca2bb90e'  # 🔐 Replace with your actual token
        handler = ipinfo.getHandler(access_token)
        details = handler.getDetails(ip_address)
        city = details.city or 'Unknown'
        country = details.country_name or 'Unknown'
    except Exception as e:
        print("⚠️ GeoIP lookup failed:", e)
        city = 'Unknown'
        country = 'Unknown'

    # Simulate features
    simulated_features = [100] * 58
    prediction = predict_attack(simulated_features)

    if prediction == 1:  # Malicious
        send_sms_alert(username, ip_address, timestamp, city, country)

    # Log attempt
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            INSERT INTO attack_logs (username, password, ip_address, timestamp, prediction, location_city, location_country)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, ip_address, timestamp, prediction, city, country))
        conn.commit()

    return f"""
        <h3>Login Attempt Recorded</h3>
        <p>From IP: {ip_address}</p>
        <p>Prediction: {prediction}</p>
        <p>Location: {city}, {country}</p>
        <a href="/">Go back</a>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
