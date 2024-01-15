from flask import Flask, render_template, request, session, redirect, url_for, flash
import secrets
from flask_mysqldb import MySQL
import os
from passlib.hash import sha256_crypt  # Added for password hashing
from database_management import *
from asos_scraper import *
from flask import jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
mysql = MySQL(app)

# Initialize password hashing
hasher = sha256_crypt.using(rounds=1000, salt_size=16)


# Existing route for index
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle form submission or any other logic here
        # For example, you can access form data using request.form
        # data = request.form['input_name']
        # Perform some processing with the form data

        # Redirect to another page after processing
        return redirect(url_for('success'))
    #extract_info_codembo_url('https://codembo.com/en/prd/204398386?cur=EURhttps://codembo.com/en/prd/204398386?cur=EUR')
    #print(extract_product_id_from_url('https://www.asos.com/shared-board/3deda666-7ca5-4522-8719-93463619d953?acquisitionsource=whatsapp'))
    price = id_list_to_price_list(['205015352', '205009650', '202753966', '24485963', '202089905', '202685547', '202882345', '23450912', '204972030', '204982557', '204825501', '203783492', '202437701', '205321404', '205350944', '204398386', '203197247', '201204217', '204825569'])

    create_dataframe(price)

    return render_template('index.html')


# Existing route for success
@app.route('/success')
def success():
    return "Form submitted successfully!"


# New route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT username, password_hash FROM tbl_users WHERE username = %s", (username,))
        user = cur.fetchone()

        cur.close()

        if user and sha256_crypt.verify(password, user[1]):
            session['username'] = user[0]

            return redirect(url_for('index'))

        flash('Invalid username or password', 'error')

    return render_template('login.html')


# New route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash the password before storing it
        hashed_password = sha256_crypt.hash(password)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tbl_users (username, email, password_hash) VALUES (%s, %s, %s)",
                    (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful! You can now log in.', 'success')

        return redirect(url_for('login'))

    return render_template('register.html')


# Existing route for user logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'username' in session:
        product_url = ''
        currency = ''
        product_name = ''
        initial_price = 0

        if request.method == 'POST':
            app.logger.info(request.form)
            if 'search_product' in request.form:
                # Handle product search
                product_url = request.form['product_details']
                currency, product_name, initial_price = extract_info_from_url(product_url)
                response_data = {
                    'product_name': product_name,
                    'product_price': initial_price,
                    'currency': currency
                }
                return jsonify(response_data)

            else:  # Assuming the other button is 'add_product'
                username = session['username']
                user_id = get_user_id_by_username(username)

                if user_id:
                    url = request.form['product_url']
                    target_price = request.form['target_price_value']
                    product_name = request.form['product_name_value']
                    current_price = request.form['product_price_value']
                    currency = request.form['currency_display_value']
                    initial_price = request.form['product_price_value']
                    if not product_exists(user_id, product_name):
                        # Extract current price and currency here
                        print(target_price)
                        save_tracked_product(user_id, product_name, url, initial_price, target_price, current_price,
                                             currency)

                        return redirect(url_for('success'))

                    flash('Product already exists for the user.', 'error')
                else:
                    flash('User not found.', 'error')

        return render_template('add_product.html')
    else:
        flash('Please log in to add or search a product.', 'error')
        return redirect(url_for('login'))


@app.route('/price_comparison', methods=['GET', 'POST'])
def price_comparison():
    if request.method == 'POST':
        # Handle form submission or any other logic here
        return redirect(url_for('success'))

    return render_template('price_comparison.html')


if __name__ == '__main__':
    app.run(debug=True)
