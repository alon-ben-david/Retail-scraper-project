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
from config import Config
from basket_database_management import get_basket_by_userid, delete_basket_by_basket_id
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
# MySQL Configuration
app.config.from_object(Config)

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
from routes import authentication_routes, product_management_routes, basket_management_routes

app.register_blueprint(authentication_routes)
app.register_blueprint(basket_management_routes)
app.register_blueprint(product_management_routes)
# Initialize password hashing
hasher = sha256_crypt.using(rounds=1000, salt_size=16)

if __name__ == '__main__':
    app.run(debug=True)
