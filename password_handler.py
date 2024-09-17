import random

import bcrypt
import sqlite3

# Hashes a given password using the bcrypt library
def hash_pw(password):
	salt = bcrypt.gensalt()
	hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
	return hashed_pw

# Verifies if the entered password is the actual password
def verify_pw(stored_pw, provided_pw):
	return bcrypt.checkpw(provided_pw.encode('utf-8'), stored_pw)

# Generates a unique ID when a customer is added to the database
def generate_unique_id():
	return random.randint(10000, 99999)

# Creates a user and adds it to the database along with the password hash
def create_user(username, gender, birthdate, phone, address, password):
	conn = sqlite3.connect("pizza.db")
	cursor = conn.cursor()
	hashed_pw = hash_pw(password)
	user_id = generate_unique_id()
	pizzas_ordered = 0
	discount_code = 0
	try:
		cursor.execute('''
		INSERT INTO Customers (id, name, gender, birthdate, phone, address, pizzas_ordered, discount_code, password_hash)
		VALUES (?,?,?, ?, ?, ?, ?, ?, ?)
		''', (user_id, username, gender, birthdate, phone, address, pizzas_ordered, discount_code, hashed_pw))
		conn.commit()
	except sqlite3.IntegrityError:
		print("username already exists")
	finally:
		conn.close()

# Checks if the given password and username match.
def authenticate_user(cursor, username, password):
	cursor.execute('SELECT password_hash FROM Customers WHERE username = ?', (username,))
	result = cursor.fetchnone()
	if result:
		stored_pw = result[0]
		return verify_pw(stored_pw, password)
	else:
		return False