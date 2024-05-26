from flask import Flask, request, jsonify, make_response, render_template
from flask_mysqldb import MySQL
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
