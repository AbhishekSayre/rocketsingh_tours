# 🚀 RocketSingh Tours

**A full-stack Django web application for booking travel tours in India.**  
Built with Django, SQLite (for development), HTML/CSS/JS, and Razorpay integration for payments.

---

## 🌟 Features

- User authentication (signup, login, logout) with email or phone  
- Editable user profile and personal information  
- Browse and book tour packages with dynamic pricing  
- Admin-defined tour dates and seat limits  
- Razorpay integration for test payments  
- Email confirmation for successful bookings  
- Responsive green-blue themed UI  
- Feedback and contact forms  
- Password reset and change functionality  

---

## 🛠️ Tech Stack

- Python 3.x  
- Django 5.x  
- SQLite (development)  
- HTML / CSS / JavaScript  
- Razorpay (payments)  

---

## ⚡ Installation

### 1. Clone the repository

```bash
git clone https://github.com/AbhishekSayre/rocketsingh_tours.git
cd rocketsingh_tours
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file in the project root

**Do not push this file to GitHub.** Include your sensitive credentials:

```
# Django
SECRET_KEY=your_django_secret_key
DEBUG=True  # False in production

# Email
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password

# Razorpay
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser for admin access

```bash
python manage.py createsuperuser
```

> Follow the prompts to set your username, email, and password.

### 7. Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 🚀 Usage

- Browse tour packages via the **Packages** page  
- Book tours (login required)  
- Admin can:
  - Add new tour packages  
  - Set tour dates  
  - Limit available seats  
  - Manage bookings and users via Django admin  

> Admin access requires logging in with the superuser account created earlier.

---

## 📸 Screenshots

*i will add later*

---

## ⚠️ Notes

- `.env` is used for sensitive credentials and **must not be pushed** to GitHub  
- Debug mode should be set to `False` in production  
- For production, consider using PostgreSQL or MySQL instead of SQLite  

---

## 📝 License

*(Add your preferred license here, e.g., MIT, GPL, or leave blank if personal use)*
