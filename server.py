import json
import sqlite3
from flask import Flask, request, jsonify

with sqlite3.connect("htn.db") as db:
	app = Flask(__name__)

@app.route("/users", methods=["GET"])
def get_all_users_endpoint():
	c = db.execute("SELECT id FROM users")
	users_values = c.fetchall()
	users = list(map(lambda x: get_user(x[0]), users_values))

	return jsonify(users)

@app.route("/users/<id>", methods=["GET"])
def get_one_user_endpoint(id):
	user = get_user(id)

	return jsonify(user)

@app.route("/users/<user_id>", methods=["POST"])
def update_user_endpoint(user_id):
	user = get_user(user_id)
	if user is None:
		return jsonify({})

	user_obj = request.get_json()
	user = update_user(user_id, user_obj)

	return jsonify(user)

@app.route("/skills", methods=["GET"])
def skill_aggregate_endpoint():
	if request.args.get("frequency"):
		min_freq = int(request.args["frequency"])
	else:
		min_freq = 0

	if request.args.get("rating"):
		min_rating = float(request.args["rating"])
	else:
		min_rating = 0

	query = '''
		SELECT name, AVG(rating) as `avg`, COUNT(*) as `count`
		FROM skills
		GROUP BY name
		HAVING count > ? AND
			   avg > ?
	'''

	c = db.execute(query, (min_freq, min_rating)).fetchall()
	skill_avgs = [
		{
			"name": name,
			"rating": round(average, 1),
			"frequency": frequency
		} for (name, average, frequency) in c
	]

	return jsonify(skill_avgs)

def serialize_user(user_values):
	keys = ["id", "name", "picture", "company", "email", "phone", "latitude", "longitude"]
	
	return { keys[i]: user_values[i] for i in range(len(user_values)) }

def serialize_skill(skill_values):
	keys = ["id", "name", "rating", "user_id"]

	return { keys[i]: skill_values[i] for i in range(len(skill_values)) }

def get_user(id):
	query = '''
		SELECT *
		FROM users
		WHERE id = ?
	'''

	c = db.execute(query, (id,))
	user_values = c.fetchone()
	if user_values is None:
		return None

	user = serialize_user(user_values)
	user["skills"] = get_skills(id)

	return user

def update_user(user_id, user_obj):
	query = '''
		UPDATE users
		SET %s = ?
		WHERE id = ?;
	'''
	
	for key, value in user_obj.items():
		if key.lower() == "skills":
			for skill_obj in user_obj["skills"]:
				update_skill(user_id, skill_obj)
		else:
			db.execute(query % key, (value, id))

	db.commit()

	return get_user(user_id)

def get_skills(user_id):
	query = '''
		SELECT * 
		FROM skills
		WHERE user_id = ?
	'''

	c = db.execute(query, (user_id,))
	skills = c.fetchall()

	if c is None:
		return []

	return list(map(serialize_skill, skills))

def get_skill(user_id, name):
	query = '''
		SELECT *
		FROM skills
		WHERE user_id = ? and
			  name = ?
	'''

	c = db.execute(query, (user_id, name))
	skill_values = c.fetchone()

	if skill_values is None:
		return None

	return serialize_skill(skill_values)

def create_skill(user_id, skill_obj):
	query = '''
		INSERT INTO skills(name, rating, user_id)
		VALUES (?, ?, ?)
	'''

	skill_tuple = (skill_obj["name"], skill_obj["rating"], user_id)

	db.execute(query, skill_tuple)
	db.commit()

	return get_skill(user_id, skill_obj["name"])

def update_skill(user_id, skill_obj):
	skill = get_skill(user_id, skill_obj["name"])
	if skill is None:
		return create_skill(user_id, skill_obj)

	update_query = '''
		UPDATE skills
		SET rating = ?
		WHERE user_id = ? and
			  name = ?;
	'''

	skill_tuple = (skill_obj["rating"], user_id, skill_obj["name"])

	db.execute(update_query, skill_tuple)
	db.commit()

	return get_skill(user_id, skill_obj["name"])

