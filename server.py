import socket
import sqlite3
import threading
import json
from datetime import datetime
from dis import disco


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
		elif action == 'get_history':
			customer_id = request_data['customer_id']
			order_history = get_history(cursor, customer_id)
			client_socket.send(json.dumps(order_history).encode('utf-8'))
		elif action == 'get_favourite_item':
			customer_id = request_data['customer_id']
			favourite_items = get_favourite_item(cursor, customer_id)
			if favourite_items:
				client_socket.send(json.dumps({favourite_items}).encode('utf-8'))
			else:
				client_socket.send(json.dumps({'message': 'No purchases found to determine favorite item.'}).encode('utf-8'))
		else:
			client_socket.send(json.dumps({'error': 'Unknown action/procedure'}).encode('utf-8'))

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

def get_history(cursor, customer_id, discount_applied):
	cursor.execute('''
	SELECT id, order_date, status, discount_applied, total_price
	FROM Orders
	WHERE customer_id = ?
	ORDER BY order_date DESC
''', (customer_id,))
	orders = cursor.fetchall()

	order_history = []
	for order in orders:
		order_id, order_date, status, discount_applies, total_price = order
		cursor.execute('''
			SELECT item_type, item_id, quantity
			FROM OrderItems
			WHERE order_id = ?
		''', (order_id,))
		items = cursor.fetchall()

		order_items = []
		for item in items:
			item_type, item_id, quantity = item
			if item_type == 'pizza':
				cursor.execute('SELECT name, price FROM Pizzas WHERE id = ?', (item_id))
			elif item_type == 'drink':
				cursor.execute('SELECT name, price FROM Drinks WHERE id = ?', (item_id,))
			elif item_type == 'dessert':
				cursor.execute('SELECT name, price FROM Desserts WHERE id = ?', (item_id,))
			item_info = cursor.fetchone()
			if item_info:
				name, price = item_info
				order_items.append({
					'item_type': item_type,
					'item_id': item_id,
					'name': name,
					'quantity': quantity,
					'price': price
				})

		order_history.append(
			{
				'order_id': order_id,
				'orer_date': order_date,
				'status': status,
				'discount_applied': discount_applied,
				'total_price': total_price,
				'items': order_items
			})

	return order_history


def get_favourite_item(cursor, customer_id):
	query = """
	WITH FilteredOrderItems AS(
		SELECT
			oi.customer_id,
			oi.item_type,
			oi.item_id
			oi.quantity
		FROM
			OrderItems oi
		LEFT JOIN
			Drinks d ON oi.item_type = 'drink' AND oi.item_id = d.id
		WHERE
			NOT (oi.item_type = 'drink' AND d.is_special = 0)
	),
	AggregatedItems AS(
		SELECT
			customer_id,
			item_type,
			item_id,
			SUM(quantity) AS total_quantity
		FROM
			FilteredOrderItems
		WHERE
			customer_id = ?
		GROUP BY
			customer_id, item_type, item_id
	),
	MaxQuantities AS (
		SELECT
			customer_id
			MAX(total_quantity) AS max_quantity
		FROM
			AggregatedItems
		GROUP BY
			customer_id
	)
	SELECT
		ai.customer_id,
		ai.item_type,
		ai.item_id,
		ai.total_quantity,
		CASE
			WHEN ai.item_type = 'pizza' THEN p.name
			WHEN ai.item_type = 'drink' THEN d.name
			WHEN ai.item_type = 'dessert' THEN ds.name
		END AS item_name
	FROM AggregatedItems ai
	JOIN 
		MaxQuantities mq on ai.customer_id = mq.customer_id AND ai.total_quantity = mq.max_quantity
    LEFT JOIN 
        Pizzas p ON ai.item_type = 'pizza' AND ai.item_id = p.id
    LEFT JOIN 
       	Drinks d ON ai.item_type = 'drink' AND ai.item_id = d.id
    LEFT JOIN 
        Desserts ds ON ai.item_type = 'dessert' AND ai.item_id = ds.id
    WHERE 
        ai.customer_id = ?
	"""

	cursor.execute(query, (customer_id, customer_id))
	result = cursor.fetchall()

	favourite_items = []
	for row in result:
		customer_id, item_type, item_id, total_quantity, item_name = row
		favourite_items.append({
			'item_type': item_type,
			'item_id': item_id,
			'item_name': item_name,
			'total_quantity': total_quantity
		})

	return favourite_items

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
