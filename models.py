"""Database models for user authentication and subscription management."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and account management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Subscription related fields
    stripe_customer_id = db.Column(db.String(255), unique=True, nullable=True)
    stripe_subscription_id = db.Column(db.String(255), unique=True, nullable=True)
    subscription_status = db.Column(db.String(50), nullable=True)  # active, canceled, past_due, etc.
    subscription_start_date = db.Column(db.DateTime, nullable=True)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        """Hash and set the user's password."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def account_age_days(self):
        """Calculate the age of the account in days."""
        return (datetime.utcnow() - self.created_at).days
    
    def requires_payment(self):
        """Check if the account requires payment (over 30 days old without active subscription)."""
        if self.account_age_days() <= 30:
            return False
        
        # If account is over 30 days old, check subscription status
        return self.subscription_status != 'active'
    
    def __repr__(self):
        return f'<User {self.email}>'
