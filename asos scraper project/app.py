from flask import Flask, render_template, request, session, redirect, url_for, flash
import secrets
from flask_mysqldb import MySQL
import os
from passlib.hash import sha256_crypt  # Added for password hashing
from database_management import *
from asos_scraper import *
from flask import jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flasgger import Swagger

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
mysql = MySQL(app)
swagger_url = '/swagger'
swaggerui_blueprint = get_swaggerui_blueprint(
    swagger_url,
    '/static/swagger.json',
    config={
        'app_name': "Retail Analysis Platform"
    }
)
Swagger(app)

app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)

# Initialize password hashing
hasher = sha256_crypt.using(rounds=1000, salt_size=16)


@app.route('/api/example', methods=['GET'])
def example_route():
    """
    This is an example route that demonstrates how to use docstrings for documentation.

    ---
    tags:
      - Example
    responses:
      200:
        description: Successful response
    """
    return jsonify({"message": "Hello, this is an example route!"})


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle form submission or any other logic here
        # For example, you can access form data using request.form
        # data = request.form['input_name']
        # Perform some processing with the form data

        # Redirect to another page after processing
        return redirect(url_for('success'))
    return render_template('index.html')


@app.route('/success')
def success():
    """
    Endpoint for successful form submission.

    ---
    tags:
      - Success
    responses:
      200:
        description: Form submitted successfully
        content:
          text/html:
            schema:
              type: string
    """
    return "Form submitted successfully!"


#  user login
@app.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.

    ---
    tags:
      - Authentication
    parameters:
      - name: username
        in: formData
        type: string
        required: true
        description: The username for login.
      - name: password
        in: formData
        type: string
        required: true
        description: The password for login.
    responses:
      200:
        description: Login successful
        content:
          application/json:
            example: {"message": "Login successful"}
      401:
        description: Unauthorized, invalid credentials
        content:
          application/json:
            example: {"message": "Invalid username or password"}
      400:
        description: Bad request, missing or invalid parameters
        content:
          application/json:
            example: {"message": "Bad request"}
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({"message": "Bad request"}), 400

        cur = mysql.connection.cursor()
        cur.execute("SELECT username, password_hash FROM tbl_users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and sha256_crypt.verify(password, user[1]):
            session['username'] = user[0]
            return jsonify({"message": "Login successful"}), 200

        return jsonify({"message": "Invalid username or password"}), 401

    # If not a POST request, return method not allowed
    return jsonify({"message": "Method not allowed"}), 405


@app.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint.

    ---
    tags:
      - Authentication
    parameters:
      - name: username
        in: formData
        type: string
        required: true
        description: The username for registration.
      - name: email
        in: formData
        type: string
        required: true
        description: The email for registration.
      - name: password
        in: formData
        type: string
        required: true
        description: The password for registration.
    responses:
      201:
        description: Registration successful
        content:
          application/json:
            example: {"message": "Registration successful! You can now log in."}
      400:
        description: Bad request, missing or invalid parameters
        content:
          application/json:
            example: {"message": "Bad request"}
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            return jsonify({"message": "Bad request"}), 400

        # Hash the password before storing it
        hashed_password = sha256_crypt.hash(password)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tbl_users (username, email, password_hash) VALUES (%s, %s, %s)",
                    (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Registration successful! You can now log in."}), 201

    # If not a POST request, return method not allowed
    return jsonify({"message": "Method not allowed"}), 405


@app.route('/logout', methods=['POST'])
def logout():
    """
    User logout endpoint.

    ---
    tags:
      - Authentication
    responses:
      200:
        description: Logout successful
        content:
          application/json:
            example: {"message": "Logout successful"}
      401:
        description: Unauthorized, user not logged in
        content:
          application/json:
            example: {"message": "Unauthorized, user not logged in"}
      405:
        description: Method not allowed
        content:
          application/json:
            example: {"message": "Method not allowed"}
    """
    if request.method == 'POST':
        if 'username' in session:
            session.pop('username', None)
            return jsonify({"message": "Logout successful"}), 200
        else:
            return jsonify({"message": "Unauthorized, user not logged in"}), 401

    # If not a POST request, return method not allowed
    return jsonify({"message": "Method not allowed"}), 405


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
                data = (extract_product_id_from_url(product_url))
                price = id_list_to_price_list(data)
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
        product_url = request.form.get('product_details')

        df_result = handle_product_basket_search(product_url)

        json_result = df_result.to_json(orient='records')
        print(json_result)
        response_data = {
            'success': True,
            'data': json_result
        }

        return jsonify(response_data)

    return render_template('price_comparison.html')


if __name__ == '__main__':
    app.run(debug=True)
