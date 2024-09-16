import socket
import sqlite3
import threading
import json
from datetime import datetime


def handle_client(client_socket):
	conn = sqlite3.connect("pizza.db")
	cursor = conn.cursor()

	while True:
		request = client_socket.recv(1024).decode('utf-8')
		if not request:
			break

		request_data = json.loads(request)
		action = request_data['action']

		if action == 'place_order':
			customer_id = request_data['customer_id']
			items = request_data['items']
			discount_code = request_data.get('discount_code')
			place_order(cursor, customer_id, items, discount_code)
			conn.commit()
			client_socket.send(b"Order placed successfully!")
		elif action == 'get_menu':
			menu = get_menu(cursor)
			client_socket.send(json.dumps(menu).encode('utf-8'))


	conn.close()
	client_socket.close()


def place_order(cursor, customer_id, items, discount_code=None):
	total_price = 0
	for item in items:
		item_type, item_id, quantity = item
		if item_type == 'pizza':
			cursor.execute('SELECT price FROM Pizzas WHERE id = ?', (item_id,))
		elif item_type == 'drink':
			cursor.execute('SELECT price FROM Drinks WHERE id = ?', (item_id,))
		elif item_type == 'dessert':
			cursor.execute('SELECT price FROM Deserts WHERE id = ?', (item_id,))
		price = cursor.fetchone()[0]
		total_price += price * quantity

	discount_applied = False
	if discount_code:
		cursor.execute('SELECT discount_code FROM Customers WHERE id = ?', (customer_id,))
		code_store = cursor.fetchone()[0]
		if code_store == discount_code:
			total_price *= 0.9  # 10% discount
			discount_applied = True
			cursor.execute('UPDATE Costumers SET discount_code = NULL WHERE id = ?', (customer_id,))

	order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	cursor.execute('''
	INSERT INTO Orders (customer_id, order_date, status, discount_applied, total_price)
	VALUES (?,?,?,?,?)
	''', (customer_id, order_date, 'placed', discount_applied, total_price))
	order_id = cursor.lastrowid

	for item in items:
		item_type, item_id, quantity = item
		cursor.execute('''
		INSERT INTO OrderItems (order_id, item_type, item_id, quantity)
		VALUES (?,?,?,?)
		''', (order_id, item_type, item_id, quantity))

def get_menu(cursor):
	cursor.execute('SELECT * FROM Pizzas')
	pizzas = cursor.fetchall()
	cursor.execute('SELECT * FROM Drinks')
	drinks = cursor.fetchall()
	cursor.execute('SELECT * FROM Desserts')
	deserts = cursor.fetchall()
	return {
		'pizzas': pizzas,
		'drinks': drinks,
		'deserts': deserts
	}

def server():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(('0.0.0.0', 9999))
	server_socket.listen(5)
	print("Server listening on port 9999")

	while True:
		client_socket, addr = server_socket.accept()
		print(f"Accepted connection from {addr}")
		client_handler = threading.Thread(target=handle_client, args=(client_socket,))
		client_handler.start()

if __name__ == "__main__":
	server()
