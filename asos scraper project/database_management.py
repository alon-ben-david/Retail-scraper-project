from datetime import datetime, timedelta
from app import *
import schedule
from time import sleep


mysql.init_app(app)


def product_exists(user_id, product_name):
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            # Check if the product already exists for the given user
            check_query = """
                SELECT COUNT(*) FROM tracked_products 
                WHERE user_id = %s AND product_name = %s
            """

            # Values to be used in the query
            values = (user_id, product_name)

            cursor.execute(check_query, values)

            # Fetch the result
            result = cursor.fetchone()

            # Close the cursor
            cursor.close()

            # If the count is greater than 0, the product already exists
            return result[0] > 0
        else:
            print("Connection to the database failed.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def save_tracked_product(user_id, product_name, product_url, initial_price, target_price, current_price, currency):
    try:
        # Check if the product already exists for the given user
        if product_exists(user_id, product_name):
            print("Product already exists.")
            return

        # Get MySQL connection from the Flask-MySQL extension
        connection = mysql.connection

        if connection:
            # Create a cursor object to execute SQL queries
            cursor = connection.cursor()

            # SQL query to insert a new product into the tracked_products table
            insert_query = """
                INSERT INTO tracked_products 
                (user_id, product_name, product_url, current_price, currency, initial_price, target_price) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            # Values to be inserted into the table
            values = (user_id, product_name, product_url, current_price, currency, initial_price, target_price)

            # Execute the query with the provided values
            cursor.execute(insert_query, values)

            # Commit the changes to the database
            connection.commit()

            # Close the cursor (Note: Flask-MySQL automatically closes the connection after the request)
            cursor.close()

            print("Product saved successfully.")
        else:
            print("Connection to the database failed.")

    except Exception as e:
        print(f"Error: {e}")


def get_user_id_by_username(username):
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            # SQL query to get the user_id by username
            query = "SELECT user_id FROM tbl_users WHERE username = %s"

            # Execute the query with the provided username
            cursor.execute(query, (username,))

            # Fetch the result
            user_id = cursor.fetchone()

            # Close the cursor
            cursor.close()

            # If a user is found, return the user_id; otherwise, return None
            return user_id[0] if user_id else None
        else:
            print("Connection to the database failed.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_product_url_by_product_id(product_id):
    try:
        connection = mysql.connection

        if connection:
            cursor = connection.cursor()

            # SQL query to get the product_url by product_id
            query = "SELECT product_url FROM tracked_products WHERE product_id = %s"

            # Execute the query with the provided product_id
            cursor.execute(query, (product_id,))

            # Fetch the result
            product_url = cursor.fetchone()
            # Close the cursor
            cursor.close()

            # If a product_url is found, return the product_url; otherwise, return None
            return product_url[0] if product_url else None
        else:
            print("Connection to the database failed.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_target_price_by_product_id(product_id):
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            # SQL query to get the target_price by product_id
            query = "SELECT target_price FROM tracked_products WHERE product_id = %s"

            # Execute the query with the provided product_id
            cursor.execute(query, (product_id,))

            # Fetch the result
            target_price = cursor.fetchone()

            # Close the cursor
            cursor.close()

            # If a target_price is found, return it; otherwise, return None
            return target_price[0] if target_price else None
        else:
            print("Connection to the database failed.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def update_target_price_reached(product_id, target_price_reached):
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            # SQL query to update the target_price_reached by product_id
            update_query = "UPDATE tracked_products SET target_price_reached = %s WHERE product_id = %s"

            # Execute the query with the provided values
            cursor.execute(update_query, (target_price_reached, product_id))

            # Commit the changes to the database
            connection.commit()

            # Close the cursor
            cursor.close()

            print(f"Target price reached updated for product ID {product_id} to {target_price_reached}")
        else:
            print("Connection to the database failed.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def update_product_price(product_id, current_price, currency):
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            # SQL query to update the current_price, currency, and last_checked by product_id
            update_query = "UPDATE tracked_products SET current_price = %s, currency = %s, last_checked = %s WHERE " \
                           "product_id = %s"

            # Values to be updated
            values = (current_price, currency, datetime.now(), product_id)

            # Execute the query with the provided values
            cursor.execute(update_query, values)

            # Commit the changes to the database
            connection.commit()

            # Close the cursor
            cursor.close()

            print(f"Product details updated for product ID {product_id}: "
                  f"Price: {current_price} {currency}, Last Checked: {datetime.now()}")
        else:
            print("Connection to the database failed.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_products_to_check():
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            # SQL query to get products and their last_checked times
            query = "SELECT product_id, user_id, product_name, product_url, current_price, currency, " \
                    "initial_price, target_price, target_price_reached, last_checked " \
                    "FROM tracked_products"

            # Execute the query
            cursor.execute(query)

            # Fetch the result
            rows = cursor.fetchall()

            # Get the column names
            columns = [desc[0] for desc in cursor.description]

            # Convert each row to a dictionary
            products = [dict(zip(columns, row)) for row in rows]

            # Close the cursor
            cursor.close()

            # Return the list of products as dictionaries
            return products

        else:
            print("Connection to the database failed.")
            return []

    except Exception as e:
        print(f"Error: {e}")
        return []


def check_price(product_id):
    """

    :param product_id:
    """
    try:

        product_url = get_product_url_by_product_id(product_id)
        print(f"Price checked for product ID {product_id} at {datetime.now()}")

        currency, product_name, current_price = extract_info_from_url(product_url)
        print(f"Price checked for product ID {product_id} at {datetime.now()}")

        # Check if the current_price is less than or equal to the target_price in the database
        target_price = get_target_price_by_product_id(product_id)
        print(f"Price checked for product ID {product_id} at {datetime.now()}")

        if current_price <= target_price:
            # Update the target_price_reached column in the database if the condition is met
            update_target_price_reached(product_id, True)

        # Update the current_price, currency, and last_checked time in the database
        update_product_price(product_id, current_price, currency)

        print(f"Price checked for product ID {product_id} at {datetime.now()}")

    except Exception as e:
        print(f"Error in check_price for product ID {product_id}: {e}")


