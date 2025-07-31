#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

def test_email():
    """Test email sending"""
    try:
        with app.app_context():
            msg = Message(
                subject='CPL Email Test',
                recipients=[os.getenv('MAIL_USERNAME')],
                body='This is a test email from CPL system.',
                sender=os.getenv('MAIL_USERNAME')
            )
            mail.send(msg)
            print("✅ Email sent successfully!")
            return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing email configuration...")
    print(f"Username: {os.getenv('MAIL_USERNAME')}")
    print(f"Password: {os.getenv('MAIL_PASSWORD')[:4]}...")
    test_email() 