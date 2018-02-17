import json
import sqlite3
from flask import Flask, jsonify

with sqlite3.connect("htn.db") as db:
	app = Flask(__name__)

def serialize_user(user_values):
	keys = ("id", "name", "picture", "company", "email", "phone", "latitude", "longitude")
	user_obj = {keys[i]: user_values[i] for i in range(len(user_values))}
	return user_obj

@app.route("/users", methods=["GET"])
def get_all_users():
	c = db.execute("SELECT * FROM users")
	users_values = c.fetchall()
	users = list(map(serialize_user, users_values))

	return jsonify(users)


@app.route("/users/<id>", methods=["GET"])
def get_one_user(id):
	c = db.execute("SELECT * FROM users WHERE id = ?", id)
	user_values = c.fetchone()
	user = serialize_user(user_values)

	return jsonify(user)
