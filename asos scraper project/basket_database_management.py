from flask import Flask
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)


def save_basket(basket_name, basket_link, user_id):
    try:
        if basket_exists(user_id, basket_name):
            print("basket already exists.")
            return

        connection = mysql.connection

        if connection:
            cursor = connection.cursor()

            insert_query = """
                INSERT INTO basket_tbl 
                (basket_name, basket_link, user_id) 
                VALUES (%s, %s, %s)
            """

            values = (basket_name, basket_link, user_id)

            cursor.execute(insert_query, values)

            connection.commit()

            cursor.close()

            print("Basket saved successfully.")
        else:
            print("Connection to the database failed.")

    except Exception as e:
        print(f"Error: {e}")


def basket_exists(user_id, basket_link):
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            check_query = """
                SELECT COUNT(*) FROM basket_tbl 
                WHERE user_id = %s AND basket_link = %s
            """

            # Values to be used in the query
            values = (user_id, basket_link)

            cursor.execute(check_query, values)

            # Fetch the result
            result = cursor.fetchone()

            # Close the cursor
            cursor.close()

            return result[0] > 0
        else:
            print("Connection to the database failed.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def save_product_to_basket(product_name, image_link, link, product_id, basket_id, user_id,product_price,product_currency):
    try:
        connection = mysql.connection

        if connection:
            cursor = connection.cursor()

            insert_query = """
                INSERT INTO product_tbl 
                (product_name, image_link, link, product_id, basket_id, user_id, product_price, product_currency) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (product_name, image_link, link, product_id, basket_id, user_id, product_price, product_currency)

            cursor.execute(insert_query, values)

            connection.commit()

            cursor.close()

            print("Product saved successfully to basket.")
        else:
            print("Connection to the database failed.")

    except Exception as e:
        print(f"Error: {e}")


def get_basket_id_by_link(link):
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            query = "SELECT basket_id FROM basket_tbl WHERE basket_link = %s"

            cursor.execute(query, (link,))

            basket_id = cursor.fetchone()

            cursor.close()

            return basket_id[0] if basket_id else None
        else:
            print("Connection to the database failed.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_basket_by_userid(user_id):
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            query = "SELECT basket_id, basket_name, basket_link, last_basket_check FROM basket_tbl WHERE user_id = %s"

            cursor.execute(query, (user_id,))

            baskets = cursor.fetchall()

            cursor.close()

            if baskets:
                baskets_list = [
                    {
                        'basket_id': item[0],
                        'basket_name': item[1],
                        'basket_link': item[2],
                        'last_basket_check': item[3].strftime('%Y-%m-%d %H:%M:%S')
                    } for item in baskets
                ]
                return baskets_list
            else:
                return None
        else:
            print("Connection to the database failed.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None
def get_products_by_userid(user_id,basket_id):
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            query = "SELECT product_id product_name link product_price product_currency FROM product_tbl WHERE basket_id = %s AND user_id = %s"
            cursor.execute(check_basket_query, (basket_id, user_id))

            products = cursor.fetchall()

            cursor.close()

            if products:
                products_list = [
                    {
                        'product_id': item[0],
                        'product_name': item[1],
                        'link': item[2],
                        'product_price': item[3],
                        'product_currency': item[4]
                    } for item in baskets
                ]
                return products_list
            else:
                return None
        else:
            print("Connection to the database failed.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def delete_basket_by_basket_id(basket_id, user_id):
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            # Check if the basket exists
            check_basket_query = "SELECT * FROM basket_tbl WHERE basket_id = %s AND user_id = %s"
            cursor.execute(check_basket_query, (basket_id, user_id))
            existing_basket = cursor.fetchone()

            if existing_basket:
                # Delete the related products
                delete_products_query = "DELETE FROM product_tbl WHERE basket_id = %s AND user_id = %s"
                cursor.execute(delete_products_query, (basket_id, user_id))

                # Delete the basket by basket_id
                delete_basket_query = "DELETE FROM basket_tbl WHERE basket_id = %s AND user_id = %s"
                cursor.execute(delete_basket_query, (basket_id, user_id))

                connection.commit()
                cursor.close()

                return True
            else:
                return False

    except Exception as e:
        print(f"Error: {e}")
        return False




def if_products_send_to_israel_by_basket_id(basket_id, user_id):
    try:
        connection = mysql.connection
        if connection:
            cursor = connection.cursor()

            # Check if the basket exists
            check_basket_query = "SELECT * FROM basket_tbl WHERE basket_id = %s AND user_id = %s"
            cursor.execute(check_basket_query, (basket_id, user_id))
            existing_basket = cursor.fetchone()

            if existing_basket:
                products_link_query = "SELECT link,product_name FROM  product_tbl WHERE basket_id = %s"
                cursor.execute(products_link_query, basket_id)
                products = cursor.fetchall()

                connection.commit()
                cursor.close()

                return products
            else:
                connection.commit()
                cursor.close()
                return False
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")

    finally:

        return False
