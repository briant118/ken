from flask import Flask, request, jsonify, make_response, render_template
from flask_mysqldb import MySQL
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'VCJ7E1E57OwtFPHMx5E'
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "202280287PSU"
app.config["MYSQL_DB"] = "kwikkwikcafe"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=["HS256"])
            current_user = data['user']
        except jwt.ExpiredSignatureError:
            return jsonify({'Message': 'Token has expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'Message': 'Invalid token'}), 403

        return func(current_user=current_user, *args, **kwargs)
    return decorated


@app.route('/')
def hello_world():
    return "<p>Welcome</p>"


def data_fetch(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data


@app.route('/public')
def public():
    return 'For Public'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')

        if username == 'Bryan' and password == 'root':
            token = jwt.encode({
                'user': username,
                'exp': datetime.utcnow() + timedelta(minutes=30)
            }, app.config['SECRET_KEY'], algorithm="HS256")

            return jsonify({'token': token})
        else:
            return make_response('Unable to verify', 403,
                                 {'WWW-Authenticate':
                                     'Basic realm: "Authentication Failed "'})
    else:
        return render_template('login.html')


@app.route("/branch", methods=["GET"])
def get_countries():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM kwikkwikcafe.branch"
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return make_response(jsonify(data), 200)


@app.route("/branch/<int:id>", methods=["GET"])
@token_required
def get_branch_by_id(id):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM branch WHERE BranchID = %s"
    cur.execute(query, (id,))
    data = cur.fetchall()
    cur.close()
    return make_response(jsonify(data), 200)


@app.route("/branch", methods=["POST"])
@token_required
def add_branch(current_user):
    cur = mysql.connection.cursor()
    info = request.get_json()
    Branch_location = info["Branch_Location"]
    Branch_name = info['Branch_Name']
    sales = int(info['Total_Sales'])
    cur.execute("""
        INSERT INTO branch (Branch_Name, Branch_Location, Total_Sales)
        VALUES (%s, %s, %s)
    """, (Branch_name, Branch_location, sales))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(jsonify({"message": "Branch added successfully",
                                  "rows_affected": rows_affected,
                                  "user": current_user}), 200)


@app.route("/branch/<int:id>", methods=["PUT"])
@token_required
def update_branch(current_user, id):
    cur = mysql.connection.cursor()
    info = request.get_json()
    Branch_location = info["Branch_Location"]
    Branch_name = info['Branch_Name']
    cur.execute("""
        UPDATE branch SET Branch_Location = %s, Branch_Name = %s
        WHERE BranchID = %s
    """, (Branch_location, Branch_name, id))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(jsonify({"message": "Branch updated successfully",
                                  "rows_affected": rows_affected,
                                  "user": current_user}), 200)


@app.route("/branch/<int:id>", methods=["DELETE"])
@token_required
def delete_branch(current_user, id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM branch WHERE BranchID = %s", (id,))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(jsonify({"message": "Branch deleted successfully",
                                  "rows_affected": rows_affected, "user":
                                      current_user}), 200)


if __name__ == "__main__":
    app.run(debug=True)
