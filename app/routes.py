import os
import uuid
from datetime import datetime

import numpy as np
import cv2

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app import db
from app.models import User, Crop

main = Blueprint('main', __name__)


# -------------------------
# CURRENT USER
# -------------------------
def current_user():
    if 'user' not in session:
        return None
    return User.query.filter_by(username=session['user']).first()


# -------------------------
# IMAGE PREPROCESSING
# -------------------------
def preprocess_image(path):
    img = cv2.imread(path)

    if img is None:
        print("❌ Image failed to load")
        return None

    print("Original shape:", img.shape)

    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    print("Processed shape:", img.shape)

    return img


# -------------------------
# HOME
# -------------------------
@main.route('/')
def home():
    return redirect(url_for('main.login'))


# -------------------------
# REGISTER
# -------------------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("User already exists", "error")
            return redirect(url_for('main.register'))

        user = User(
            username=username,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created!", "success")
        return redirect(url_for('main.login'))

    return render_template('register.html')


# -------------------------
# LOGIN
# -------------------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            return redirect(url_for('main.dashboard'))

        flash("Invalid credentials", "error")

    return render_template('login.html')


# -------------------------
# DASHBOARD
# -------------------------
@main.route('/dashboard')
def dashboard():
    user = current_user()

    if not user:
        return redirect(url_for('main.login'))

    crops = Crop.query.filter_by(user_id=user.id).all()

    return render_template('dashboard.html', user=user, crops=crops)


# -------------------------
# ADD CROP
# -------------------------
@main.route('/add_crop', methods=['POST'])
def add_crop():
    user = current_user()

    if not user:
        return redirect(url_for('main.login'))

    name = request.form['name']
    growth_stage = request.form['growth_stage']
    image = request.files.get('image')

    filename = None
    upload_path = current_app.config["UPLOAD_FOLDER"]

    if image and image.filename:
        filename = f"{uuid.uuid4()}_{secure_filename(image.filename)}"
        image.save(os.path.join(upload_path, filename))

    CROP_DAYS = {
        "Seed 🌱": 90,
        "Sprout 🌿": 70,
        "Vegetative 🌾": 50,
        "Flowering 🌸": 30,
        "Harvest 🌽": 0
    }

    crop = Crop(
        name=name,
        growth_stage=growth_stage,
        image=filename,
        user_id=user.id,
        days_to_harvest=CROP_DAYS.get(growth_stage, 60),
        date_planted=datetime.utcnow()
    )

    db.session.add(crop)
    db.session.commit()

    flash("Crop added 🌾", "success")
    return redirect(url_for('main.dashboard'))


# -------------------------
# SCANNER (FIXED FOR DEPLOYMENT)
# -------------------------
@main.route('/scanner', methods=['GET', 'POST'])
def scanner():
    user = current_user()

    if not user:
        return redirect(url_for('main.login'))

    if 'scanned_images' not in session:
        session['scanned_images'] = []

    result = None
    image_file = None

    if request.method == 'POST':
        image = request.files.get('image')

        if not image or image.filename == '':
            flash("No image uploaded 🌾", "error")
            return redirect(url_for('main.scanner'))

        upload_path = current_app.config["UPLOAD_FOLDER"]

        filename = f"{uuid.uuid4()}_{secure_filename(image.filename)}"
        filepath = os.path.join(upload_path, filename)
        image.save(filepath)

        print("✅ Image saved:", filepath)

        img = preprocess_image(filepath)

        # -------------------------
        # SAFE MODEL HANDLING (FIXED)
        # -------------------------
        model = getattr(current_app, "model", None)

        if img is not None and model:
            try:
                pred = model.predict(img)

                class_index = int(np.argmax(pred))
                confidence = float(np.max(pred))

                CLASSES = ["Healthy 🌱", "Blight 🍂", "Rust 🦠"]

                result = {
                    "status": CLASSES[class_index],
                    "confidence": f"{confidence * 100:.2f}%",
                    "message": "Detection successful"
                }

            except Exception as e:
                print("❌ Prediction error:", e)

                result = {
                    "status": "Error",
                    "confidence": "0%",
                    "message": "Model prediction failed"
                }

        else:
            print("⚠️ Model not available in deployment")

            result = {
                "status": "Model Disabled",
                "confidence": "0%",
                "message": "AI model not loaded on server"
            }

        image_file = filename

        gallery = session.get('scanned_images', [])
        gallery.insert(0, filename)
        session['scanned_images'] = gallery

    return render_template(
        'scanner.html',
        user=user,
        result=result,
        image_file=image_file,
        scanned_images=session.get('scanned_images', [])
    )


# -------------------------
# SETTINGS
# -------------------------
@main.route('/settings', methods=['GET', 'POST'])
def settings():
    user = current_user()

    if not user:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        session['theme'] = request.form.get('theme')
        session['notifications'] = request.form.get('notifications')

        flash("Settings saved successfully 🌿", "success")
        return redirect(url_for('main.settings'))

    return render_template(
        'settings.html',
        user=user,
        theme=session.get('theme', 'light'),
        notifications=session.get('notifications', 'on')
    )


# -------------------------
# OTHER PAGES (UNCHANGED)
# -------------------------
@main.route('/fields')
def fields():
    user = current_user()
    if not user:
        return redirect(url_for('main.login'))
    crops = Crop.query.filter_by(user_id=user.id).all()
    return render_template('fields.html', user=user, crops=crops)


@main.route('/stats')
def stats():
    user = current_user()
    if not user:
        return redirect(url_for('main.login'))
    crops = Crop.query.filter_by(user_id=user.id).all()
    return render_template('stats.html', user=user, crops=crops)


@main.route('/plan')
def plan():
    user = current_user()
    if not user:
        return redirect(url_for('main.login'))
    return render_template('plan.html', user=user)


@main.route('/profile')
def profile():
    user = current_user()
    if not user:
        return redirect(url_for('main.login'))
    return render_template('profile.html', user=user)


# -------------------------
# LOGOUT
# -------------------------
@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))