import os
import json
import secrets
from flask import Flask, render_template, request, session, redirect, url_for, flash, Blueprint, jsonify
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt  # Added for password hashing
from database_management import *
from asos_scraper import *
from flask_swagger_ui import get_swaggerui_blueprint
from basket_database_management import get_basket_by_userid, delete_basket_by_basket_id


basket_management_routes = Blueprint('basket_management_routes', __name__)




@basket_management_routes.route('/add_basket', methods=['POST'])
def price_comparison():
    """
    Price comparison endpoint.

    ---

    tags:
      - Basket Management
    parameters:
      - name: basket_link
        in: formData
        type: string
        description: basket to add.

    responses:
      200:
        description: The basket add successful.
        content:
          application/json:
            example:
              {
                "success": true,
                "data": [{"product_name": "Product 1", "price": 99.99}, {"product_name": "Product 2", "price": 129.99}]
              }

      400:
        description: Bad request, missing or invalid parameters.
        content:
          application/json:
            example: {"message": "Bad request"}

      401:
        description: User not logged in. Please log in.
        content:
          application/json:
            example: {"message": "User not logged in. Please log in."}

    402:
        description: Product already exists.
        content:
          application/json:
            example:
              value: {"message": "Basket already exists for the user."}
    """
    from app import mysql, app
    from database_management import get_user_id_by_username
    if 'username' in session:
        # Check if the request method is POST
        if request.method == 'POST':
            username = session['username']
            user_id = get_user_id_by_username(username)
            basket_link = request.form.get('basket_link')
            if basket_exists(user_id, basket_link):
                return jsonify({"message": "Basket already exists for the user."}), 402

            df_result = extract_product_id_from_url(basket_link, user_id)

            products_data = df_result.to_dict(orient='records')

            # Prepare response data
            response_data = {
                'success': True,
                'data': products_data
            }

            return jsonify(response_data), 200

        # If not a POST request, return bad request
        return jsonify({"message": "Bad request"}), 400
    else:
        return jsonify({"message": "User not logged in. Please log in."}), 401


@basket_management_routes.route('/display_baskets', methods=['GET'])
def display_baskets():
    """
    display baskets endpoint.

    ---

    tags:
      - Basket Management


    responses:
      200:
        description: The basket display successful.
        content:
          application/json:
            example:
              {
                "data": [{"basket_id":2, "basket_name":"shoes", "basket_link":"www.asos.com/basket", "user_id":3, "last_basket_check":2024-01-25 16:04:28}]
              }

      400:
        description: Bad request, missing or invalid parameters.
        content:
          application/json:
            example: {"message": "Bad request"}

      401:
        description: User not logged in. Please log in.
        content:
          application/json:
            example: {"message": "User not logged in. Please log in."}


    """
    from app import mysql, app
    from database_management import get_user_id_by_username
    if 'username' in session:
        # Check if the request method is POST
        if request.method == 'GET':
            username = session['username']
            user_id = get_user_id_by_username(username)

            baskets_list = get_basket_by_userid(user_id)
            json_result = json.dumps(baskets_list, indent=2, ensure_ascii=False)
            if json_result == "null":
                return jsonify({"message": "Does not have a shopping basket."}),200

            else:
                # Prepare response data
                response_data = {
                    'Basket to display': json_result
                 }

                return jsonify(response_data), 200

        # If not a POST request, return bad request
        return jsonify({"message": "Bad request"}), 400
    else:
        return jsonify({"message": "User not logged in. Please log in."}), 401


@basket_management_routes.route('/delete_baskets', methods=['DELETE'])
def delete_baskets():
    """
    Delete baskets endpoint.

    ---

    tags:
      - Basket Management
    parameters:
      - name: basket_id
        in: formData
        type: int
        description: basket to delete.

    responses:
      200:
        description: The basket delete successful.
        content:
          application/json:
            example: {"message": "The basket delete successful."}

      400:
        description: Bad request, missing or invalid parameters.
        content:
          application/json:
            example: {"message": "Bad request"}

      401:
        description: User not logged in. Please log in.
        content:
          application/json:
            example: {"message": "User not logged in. Please log in."}
    """
    from app import mysql, app
    from database_management import get_user_id_by_username

    if 'username' in session:
        # Check if the request method is POST
        if request.method == 'DELETE':
            username = session['username']
            user_id = get_user_id_by_username(username)
            basket_id = request.form.get('basket_id')
            json_result = delete_basket_by_basket_id(basket_id, user_id)

            if json_result:
                return jsonify({"message": "The basket delete successful."}), 200

        # If not a POST request, return bad request
        return jsonify({"message": "Bad request"}), 400
    else:
        return jsonify({"message": "User not logged in. Please log in."}), 401


@basket_management_routes.route('/send_to_israel', methods=['GET'])
def if_products_send_to_israel():
    """

if products send to israel
---

tags:
  - Basket Management
parameters:
  - name: basket_id
    in: formData
    type: int
    description: Basket to delete.

responses:
  200:
    description: The basket delete successful.
    content:
      application/json:
        example: {"message": "The basket delete successful."}

  400:
    description: Bad request, missing or invalid parameters.
    content:
      application/json:
        example: {"message": "Bad request"}

  401:
    description: User not logged in. Please log in.
    content:
      application/json:
        example: {"message": "User not logged in. Please log in."}
"""
    from app import mysql, app
    from database_management import get_user_id_by_username
    if 'username' in session:
        # Check if the request method is POST
        if request.method == 'GET':
            username = session['username']
            user_id = get_user_id_by_username(username)
            basket_id = request.form.get('basket_id')
            products = if_products_send_to_israel_by_basket_id(basket_id, user_id)

            if products:
                not_send_to_israel = []
                for product in products:
                    if not send_to_israel(product[0]):
                        not_send_to_israel.append(product[1])

                if len(not_send_to_israel) == 0:
                    return jsonify({"message": "All products shipped to Israel."}), 200
                else:
                    json_result = json.dumps(not_send_to_israel, indent=2, ensure_ascii=False)
                    if json_result:
                        return jsonify({"message": "The products not shipped to Israel are:"}, json_result), 200

            return jsonify({"message": "Bad request"}), 400
        else:
            return jsonify({"message": "Bad request"}), 400
    else:
        return jsonify({"message": "User not logged in. Please log in."}), 401
