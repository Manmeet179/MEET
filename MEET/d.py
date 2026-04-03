import re
from flask import Flask, render_template, request, session, redirect, url_for,jsonify, session
from flask_babel import Babel, _
import psycopg2
from functools import wraps
import bcrypt
from werkzeug.utils import secure_filename
import os
from translations import translations  # Import the translation dictionary

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# @app.route('/home', methods=['GET', 'POST'])
# def home():
#     # Get the selected language from the form, default to 'en' if not provided
#     language = request.form.get('language', 'en')
#
#     # Get the translations for the selected language (default to English if not found)
#     selected_translations = translations.get(language, translations['en'])
#
#     # Pass the translations and language to the template
#     return render_template('language.html',
#                            language=language,
#                            translations=selected_translations)


app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')



# ✅ Create folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="user_database",
            user="postgres",
            password="2625",
            port=5433
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        conn = get_db_connection()
        if conn is None:
            return render_template("login.html", error="Database connection error.")

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            hashed_password = user[6].encode('utf-8')  # password is 7th column
            if bcrypt.checkpw(password, hashed_password):
                session['user'] = {
                    'first_name': user[1],
                    'last_name': user[2],
                    'email': user[3],
                    'role': user[8],
                    'city': user[7]
                }
                return redirect(url_for('dashboard'))
            else:
                return render_template("login.html", error="Incorrect password.")
        else:
            return render_template("login.html", error="User does not exist.")
    return render_template("login.html")

# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        contact_number = request.form['contact_number']
        gender = request.form['gender']
        password = request.form['password']
        re_password = request.form['re_password']
        city = request.form['city']

        # Validate mobile number (10 digits, numeric only)
        if not re.match(r'^\d{10}$', contact_number):
            return render_template('signup.html', error='Invalid mobile number. It should be 10 digits long and contain only numbers.')

        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return render_template('signup.html', error='Invalid email format.')

        # Validate password length (max 8 characters)
        if len(password) != 8:
            return render_template('signup.html', error='Password should not exceed 8 characters.')

        if password != re_password:
            return render_template('signup.html', error='Passwords do not match.')

        conn = get_db_connection()
        if conn is None:
            return render_template('signup.html', error='Database connection error.')

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return render_template('signup.html', error='Email already exists.')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, contact_number, gender, password, city, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, email, contact_number, gender, hashed_password.decode('utf-8'), city, 'user'))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('login'))

    return render_template('signup.html')
#
# # DASHBOARD
# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template("dashboard.html", user=session['user'])

# ABOUT US
@app.route('/about')
@login_required
def about_us():
    return render_template('about_us.html')

# CONTACT
@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        name = f"{session['user']['first_name']} {session['user']['last_name']}"
        email = session['user']['email']
        subject = request.form['subject']
        message = request.form['message']

        conn = get_db_connection()
        if conn is None:
            return render_template('contact.html', error="Database connection failed.", user=session['user'])

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO contact_messages (name, email, subject, message)
                VALUES (%s, %s, %s, %s)
            """, (name, email, subject, message))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return render_template('contact.html', error=str(e), user=session['user'])
        finally:
            cursor.close()
            conn.close()

        return render_template('contact.html', success=True, user=session['user'])

    return render_template('contact.html', user=session['user'])

# LOGOUT
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/language', methods=['GET', 'POST'])
def language():
    # URL parameter કે formથી ભાષા લેજો
    language_code = request.args.get('language', 'en')  # or use 'form.get(...)'

    # જો ભાષા dictionaryમાં ન હોય તો default English
    selected_translations = translations.get(language_code, translations['en'])

    return render_template('language.html',
                           translations=selected_translations,
                           language=language_code)

# ACCOUNT PAGE
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    email = session['user']['email']
    conn = get_db_connection()
    if conn is None:
        return render_template('account.html', error="Database connection failed.")

    cursor = conn.cursor()

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        contact_number = request.form['contact_number']
        gender = request.form['gender']
        city = request.form['city']

        cursor.execute("""
            UPDATE users
            SET first_name = %s, last_name = %s, contact_number = %s, gender = %s, city = %s
            WHERE email = %s
        """, (first_name, last_name, contact_number, gender, city, email))
        conn.commit()

        session['user'].update({
            'first_name': first_name,
            'last_name': last_name,
            'city': city
        })

    cursor.execute("SELECT first_name, last_name, contact_number, gender, city FROM users WHERE email = %s", (email,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if user_data:
        user = {
            'first_name': user_data[0],
            'last_name': user_data[1],
            'contact_number': user_data[2],
            'gender': user_data[3],
            'city': user_data[4],
            'email': email
        }
        return render_template('account.html', user=user)

    return render_template('account.html', error="User not found.")

# SETTINGS PAGE
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

# HELP PAGE
@app.route('/help')
@login_required
def help():
    return render_template('help.html')

# FAVORITE PAGE
@app.route('/favorite')
@login_required
def favorite():
    return render_template('favorite.html')

# PRODUCTS PAGE (admin only)
@app.route('/products')
def products():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    conn.close()
    return render_template('dashboard.html', products=products)

# VIEW USERS (admin only)
@app.route('/Users')
@login_required
def Users():
    if session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    if conn is None:
        return render_template('Users.html', error="Database connection failed.")

    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name, email, contact_number, gender, password, city, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('Users.html', users=users)

# UPDATE ROLE (admin only)
@app.route('/update_role', methods=['POST'])
@login_required
def update_role():
    if session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))

    user_id = request.form['user_id']
    new_role = request.form['new_role']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('Users'))

# DELETE USER (admin only)
@app.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    if session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))

    user_id = request.form['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('Users'))

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_description = request.form['product_description']
        product_category = request.form['product_category']

        image = request.files['product_image']
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO products (product_name, product_price, product_description, product_image, product_category)
            VALUES (%s, %s, %s, %s, %s)
        ''', (product_name, product_price, product_description, image_filename, product_category))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('add_product'))

    return render_template('add_product.html')


@app.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Delete product from the database
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()  # In case something goes wrong
        return render_template('products.html', error=f"Error deleting product: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('products'))  # Redirect back to the products page


@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # GET method: Load product by ID
    if request.method == 'GET':
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        conn.close()

        if product:
            return render_template('edit_product.html', product=product)  # Pass product data to the template
        else:
            return redirect(url_for('products'))

    # POST method: Update product details
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_description = request.form['product_description']
        product_category = request.form['product_category']

        # Optionally handle file upload for image
        image = request.files['product_image']
        if image:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)
        else:
            image_filename = request.form['existing_image']  # Keep the existing image if no new one is uploaded

        # Update product in the database
        cursor.execute('''
            UPDATE products 
            SET product_name = %s, product_price = %s, product_description = %s, 
                product_image = %s, product_category = %s 
            WHERE id = %s
        ''', (product_name, product_price, product_description, image_filename, product_category, product_id))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('products'))  # Redirect to products page after successful update

@app.route('/buy', methods=['POST'])
def buy():
    data = request.get_json()
    selected_products = data['products']  # list of product IDs and quantity
    user_name = data['user']              # Assume a logged-in user or session

    invoice = []
    total = 0

    for item in selected_products:
        product = next((p for p in products if p["product_id"] == item["product_id"]), None)
        if product:
            subtotal = product["product_price"] * item["quantity"]
            invoice.append({
                "name": product["product_name"],
                "quantity": item["quantity"],
                "price": product["product_price"],
                "subtotal": subtotal
            })
            total += subtotal

    delivery_charge = 0
    if total < 500:
        delivery_charge = 100
        total += delivery_charge

    return jsonify({
        "invoice": invoice,
        "total": total,
        "delivery_charge": delivery_charge,
        "user": user_name
    })



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
