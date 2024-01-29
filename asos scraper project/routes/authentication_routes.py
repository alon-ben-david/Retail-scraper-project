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

authentication_routes = Blueprint('authentication_routes', __name__)

@authentication_routes.route('/login', methods=['POST'])
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
    from app import mysql
    try:
        if 'username' in session:
            return jsonify({"message": "Bad request - There is a connection to another user"}), 400

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                return jsonify({"message": "Bad request"}), 400

            # Change the following line to use mysql.connection.cursor()
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
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"message": "Internal Server Error"}), 500

@authentication_routes.route('/register', methods=['POST'])
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
    from app import mysql

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


@authentication_routes.route('/logout', methods=['POST'])
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

