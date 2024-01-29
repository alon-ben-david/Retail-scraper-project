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

product_management_routes = Blueprint('product_management_routes', __name__)


@product_management_routes.route('/add_product', methods=['POST'])
def add_product():
    """
    User add product to track endpoint.

    ---

    tags:
      - Product Management
    parameters:
      - name: product_url
        in: formData
        type: string
        description: Search for product details using the provided URL.
      - name: price_target
        in: formData
        type: double
        description: Set target price.
    responses:
      200:
        description: Add product to track successfully.
        content:
          application/json:
            example:
              {
                "currency": "ILS",
                "price target": 88,
                "product_name": "Topman oversized collarless jersey blazer in grey",
                "product_price": 175.81,
                "message": "Product added successfully"
              }

      401:
        description: User not logged in. Please log in.
        content:
          application/json:
            example: {"message": "User not logged in. Please log in."}

      400:
        description: Invalid product URL.
        content:
          application/json:
            example:
              value: {"message": "Invalid product URL."}

      402:
        description: Product already exists.
        content:
          application/json:
            example:
              value: {"message": "Product already exists for the user."}

      404:
        description: Product not found in the provided URL.
        content:
          application/json:
            example:
              value: {"message": "Product not found in the provided URL."}

      403:
        description: Error extracting product information.
        content:
          application/json:
            example:
              value: {"message": "Error extracting product information."}
    """
    from app import mysql,app
    from database_management import get_user_id_by_username,product_exists,save_tracked_product

    if 'username' in session:
        if request.method == 'POST':
            app.logger.info(request.form)
            product_url = request.form.get('product_url')
            price_target = request.form.get('price_target')

            if not is_valid_asos_product_link(product_url):
                return jsonify({"message": "Invalid product URL."}), 400

            try:
                currency, product_name, initial_price = extract_info_from_url(product_url)
            except Exception as e:
                return jsonify({"message": "Error extracting product information."}), 403

            response_data = {
                'product_name': product_name,
                'product_price': initial_price,
                'currency': currency,
                'price target': price_target
            }

            username = session['username']
            user_id = get_user_id_by_username(username)

            if product_exists(user_id, product_name):
                return jsonify({"message": "Product already exists for the user."}), 402

            save_tracked_product(
                user_id,
                product_name,
                product_url,
                initial_price,
                price_target,
                initial_price,
                currency
            )

            response_data["message"] = "Product added successfully"
            return jsonify(response_data), 200

    else:
        return jsonify({"message": "User not logged in. Please log in."}), 401
