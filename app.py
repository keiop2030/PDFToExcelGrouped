"""Main Flask application with user authentication and Stripe subscription."""
import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
import stripe

from models import db, User
from forms import RegistrationForm, LoginForm

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


def payment_required(f):
    """Decorator to check if user needs to pay before accessing a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.requires_payment():
            flash('Your free trial has ended. Please subscribe to continue using the service.', 'warning')
            return redirect(url_for('subscribe'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower())
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You have 30 days of free access.', 'success')
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
@payment_required
def dashboard():
    """User dashboard (main application area)."""
    days_remaining = 30 - current_user.account_age_days()
    if days_remaining < 0:
        days_remaining = 0
    
    return render_template('dashboard.html', days_remaining=days_remaining)


@app.route('/subscribe')
@login_required
def subscribe():
    """Subscription page for users who need to pay."""
    # Check if user already has an active subscription
    if current_user.subscription_status == 'active':
        flash('You already have an active subscription.', 'info')
        return redirect(url_for('dashboard'))
    
    return render_template('subscribe.html', 
                         stripe_public_key=STRIPE_PUBLIC_KEY,
                         subscription_amount=30)


@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create a Stripe checkout session for subscription."""
    try:
        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={'user_id': current_user.id}
            )
            current_user.stripe_customer_id = customer.id
            db.session.commit()
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('subscription_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('subscribe', _external=True),
        )
        
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/subscription-success')
@login_required
def subscription_success():
    """Handle successful subscription."""
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            # Retrieve the session to get subscription details
            session = stripe.checkout.Session.retrieve(session_id)
            subscription = stripe.Subscription.retrieve(session.subscription)
            
            # Update user subscription info
            current_user.stripe_subscription_id = subscription.id
            current_user.subscription_status = subscription.status
            current_user.subscription_start_date = datetime.fromtimestamp(subscription.current_period_start)
            current_user.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
            db.session.commit()
            
            flash('Subscription activated successfully! Thank you for subscribing.', 'success')
        except Exception as e:
            flash(f'Error processing subscription: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))


@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhooks for subscription events."""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    if not webhook_secret:
        # Webhook signature verification is required for security
        return jsonify({'error': 'Webhook secret not configured'}), 500
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle subscription events
    if event.type == 'customer.subscription.updated':
        subscription = event.data.object
        user = User.query.filter_by(stripe_subscription_id=subscription.id).first()
        if user:
            user.subscription_status = subscription.status
            user.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
            db.session.commit()
    
    elif event.type == 'customer.subscription.deleted':
        subscription = event.data.object
        user = User.query.filter_by(stripe_subscription_id=subscription.id).first()
        if user:
            user.subscription_status = 'canceled'
            db.session.commit()
    
    return jsonify({'status': 'success'}), 200


@app.route('/account')
@login_required
def account():
    """User account page showing subscription details."""
    return render_template('account.html')


@app.route('/cancel-subscription', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel user's subscription."""
    if current_user.stripe_subscription_id:
        try:
            stripe.Subscription.delete(current_user.stripe_subscription_id)
            current_user.subscription_status = 'canceled'
            db.session.commit()
            flash('Your subscription has been canceled.', 'info')
        except Exception as e:
            flash(f'Error canceling subscription: {str(e)}', 'danger')
    
    return redirect(url_for('account'))


def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")


if __name__ == '__main__':
    init_db()
    # Debug mode should only be enabled in development
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)
