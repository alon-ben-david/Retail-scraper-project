from datetime import datetime
from app import *

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




