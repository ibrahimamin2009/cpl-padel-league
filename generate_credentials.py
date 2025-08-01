#!/usr/bin/env python3
"""
Generate secure credentials for Render deployment
"""
import secrets
import string

def generate_secret_key():
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(50))

def main():
    print("🔐 GENERATING SECURE CREDENTIALS FOR RENDER")
    print("=" * 50)
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    print("\n📋 RENDER ENVIRONMENT VARIABLES:")
    print("-" * 30)
    print(f"SECRET_KEY={secret_key}")
    print("RENDER_ENVIRONMENT=production")
    print("MAIL_USERNAME=your-gmail@gmail.com")
    print("MAIL_PASSWORD=your-app-password")
    print("DATABASE_URL=auto-set-by-render")
    
    print("\n📧 EMAIL SETUP INSTRUCTIONS:")
    print("-" * 30)
    print("1. Go to your Gmail account")
    print("2. Enable 2-Factor Authentication")
    print("3. Go to Security → App passwords")
    print("4. Generate a new app password")
    print("5. Use that password for MAIL_PASSWORD")
    
    print("\n🔑 ADMIN LOGIN CREDENTIALS:")
    print("-" * 30)
    print("Team Name: admin")
    print("Password: admin")
    
    print("\n📝 DEPLOYMENT STEPS:")
    print("-" * 30)
    print("1. Go to render.com and sign up")
    print("2. Create new Web Service")
    print("3. Connect your GitHub repository")
    print("4. Set environment variables above")
    print("5. Add PostgreSQL database")
    print("6. Deploy!")
    
    print("\n✅ Your app will be ready to use!")
    print("🎉 Admin login: admin/admin")

if __name__ == "__main__":
    main() 