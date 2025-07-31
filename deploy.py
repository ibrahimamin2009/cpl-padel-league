#!/usr/bin/env python3
"""
Deployment preparation script for CPL
"""
import os
import secrets

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def create_env_template():
    """Create environment variables template"""
    secret_key = generate_secret_key()
    
    env_content = f"""# CPL Environment Variables
# Copy these to your deployment platform's environment variables

SECRET_KEY={secret_key}
MAIL_USERNAME=ibrahimamin9621@gmail.com
MAIL_PASSWORD=dotsxdjzmmxrgsrk

# Database (Railway will provide DATABASE_URL automatically)
# DATABASE_URL=postgresql://...

# Flask settings
FLASK_ENV=production
FLASK_DEBUG=False
"""
    
    with open('env_template.txt', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment template created: env_template.txt")
    print(f"🔐 Your secret key: {secret_key}")
    print("\n📋 Next steps:")
    print("1. Copy the environment variables to your Railway project")
    print("2. Deploy your code to Railway")
    print("3. Your app should now work without the IndentationError!")

if __name__ == '__main__':
    create_env_template() 