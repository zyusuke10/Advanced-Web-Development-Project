import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
MYSQL_DATABASE_USER = os.getenv('MYSQL_DATABASE_USER')
MYSQL_DATABASE_PASSWORD = os.getenv('MYSQL_DATABASE_PASSWORD')
MYSQL_DATABASE_DB = os.getenv('MYSQL_DATABASE_DB')
MYSQL_DATABASE_HOST = os.getenv('MYSQL_DATABASE_HOST')
MYSQL_DATABASE_PORT = os.getenv('MYSQL_DATABASE_PORT')
MYSQL_DATABASE_CHARSET = os.getenv('MYSQL_DATABASE_CHARSET')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')



app = Flask(
	__name__
	)

app.config['SECRET_KEY'] = SECRET_KEY



@app.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
	return response




