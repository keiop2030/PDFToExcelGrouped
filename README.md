# PDFToExcelGrouped

A web-based application for converting bank PDFs into Excel spreadsheets grouped by GAAP type of expenses. The application includes user authentication, registration, and a subscription-based payment system using Stripe.

## Features

- **User Authentication**: Secure registration and login system with password hashing
- **30-Day Free Trial**: New users get 30 days of free access
- **Stripe Integration**: Monthly subscription at $30/month after the trial period
- **Account Management**: Users can manage their subscriptions and view account details
- **Secure Payment Processing**: Credit card payments processed securely through Stripe

## Prerequisites

- Python 3.8 or higher
- Stripe account (for payment processing)
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/keiop2030/PDFToExcelGrouped.git
cd PDFToExcelGrouped
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` file and add your configuration:
- `SECRET_KEY`: A secure random key for Flask sessions
- `STRIPE_PUBLIC_KEY`: Your Stripe publishable key
- `STRIPE_SECRET_KEY`: Your Stripe secret key
- `STRIPE_PRICE_ID`: Your Stripe price ID for the $30/month subscription

## Stripe Configuration

1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe Dashboard
3. Create a product and recurring price ($30/month) in Stripe
4. Copy the Price ID to your `.env` file

For testing, use Stripe's test mode keys.

## Usage

1. Initialize the database:
```bash
python app.py
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Application Structure

```
PDFToExcelGrouped/
├── app.py              # Main application file with routes
├── models.py           # Database models (User)
├── forms.py            # WTForms for registration and login
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── .gitignore         # Git ignore rules
├── templates/         # HTML templates
│   ├── base.html      # Base template
│   ├── index.html     # Home page
│   ├── register.html  # Registration page
│   ├── login.html     # Login page
│   ├── dashboard.html # User dashboard
│   ├── subscribe.html # Subscription page
│   └── account.html   # Account management
└── README.md          # This file
```

## User Flow

1. **Registration**: Users create an account with email and password
2. **Free Trial**: New accounts get 30 days of free access
3. **Subscription**: After 30 days, users must subscribe to continue
4. **Payment**: Stripe checkout for secure credit card processing
5. **Access**: Active subscribers can use the PDF conversion service

## Testing Payment

For testing, use Stripe's test card numbers:
- Success: `4242 4242 4242 4242`
- Any future expiration date and any 3-digit CVC

## Security Features

- Password hashing using bcrypt
- CSRF protection on all forms
- Secure session management
- Stripe secure payment processing
- Environment variables for sensitive data

## License

MIT License

## Support

For issues or questions, please open an issue on GitHub.
