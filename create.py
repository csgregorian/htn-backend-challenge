import sqlite3
import json

def create_users_table(db):
	db.execute('DROP TABLE IF EXISTS users')

	query = '''
		CREATE TABLE users (
			id integer primary key,
			name text,
			picture text,
			company text,
			email text,
			phone text,
			latitude real,
			longitude real
		)
	'''

	db.execute(query)
	db.commit()

def create_skills_table(db):
	db.execute('DROP TABLE IF EXISTS skills')

	query = '''
		CREATE TABLE skills(
			id integer primary key,
			name text,
			rating integer,
			user_id integer,
			FOREIGN KEY(user_id) REFERENCES users(id)
		)
	'''

	db.execute(query)
	db.commit()

def add_data_from_file(filename):
	with open(filename) as file:
		users = json.loads(file.read())

		for user in users:
			fields = ("name", "picture", "company", "email", "phone", "latitude", "longitude")
			user_tuple = tuple(map(lambda x: user.get(x), fields))

			query = '''
				INSERT INTO users(name, picture, company, email, phone, latitude, longitude)
				VALUES(?, ?, ?, ?, ?, ?, ?)
			'''

			db.execute(query, user_tuple)
			user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
		
			for skill_obj in user["skills"]:
				skill_tuple = (skill_obj["name"], skill_obj["rating"], user_id)
				query = '''
					INSERT INTO skills(name, rating, user_id)
					VALUES (?, ?, ?)
				'''

				db.execute(query, skill_tuple)

		db.commit()


if __name__ == "__main__":
	with sqlite3.connect("htn.db") as db:
		create_users_table(db)
		create_skills_table(db)
		add_data_from_file("users.json")

