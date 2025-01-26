from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ## means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        business_name = request.form.get('business_name')
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        address = request.form.get('address')
        username = request.form.get('username')
        password = request.form.get('password')
        registration_id = request.form.get('registration_id')
        industry = request.form.get('industry')

        # Check if email already exists in the database
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif not firstname.isalpha():
            flash('First name must contain only letters.', category='error')
        elif not lastname.isalpha():
            flash('Last name must contain only letters.', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 1 character.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')

        else:
            # Create a new user with default sustainability level set to 0
            new_user = User(
                business_name=business_name,
                email=email,
                firstname = firstname, 
                lastname = lastname,
                address=address,
                username=username,
                password=generate_password_hash(password, method='pbkdf2:sha256'),
                registration_id=registration_id,
                industry=industry,
                sustainability_level=0  # Set default sustainability level to 0
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('auth.questionnaire'))  # Redirect to questionnaire page

    return render_template("signup.html", user=current_user)


@auth.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    if request.method == 'POST':
        # Collect answers from the form
        total_score = 0
        answers = request.form

        # Iterate over the form data to calculate the total score
        for key, value in answers.items():
            total_score += int(value)

        # Calculate sustainability level
        if total_score >= 20:
            sustainability_level = 'High Sustainability'
        elif total_score >= 12:
            sustainability_level = 'Moderate Sustainability'
        else:
            sustainability_level = 'Low Sustainability'

        if sustainability_level == 'High Sustainability':
            total_score = 3
        elif sustainability_level == 'Moderate Sustainability':
            total_score = 2
        else:
            total_score = 1

        # Update user's sustainability level in the database
        current_user.sustainability_level = total_score
        db.session.commit()

        # Redirect to a success page or dashboard
        flash(f'Your Sustainability Level: {sustainability_level}', category='success')
        return redirect(url_for('views.home'))  # Or any other page you want to redirect to

    return render_template("questionnaire.html")
