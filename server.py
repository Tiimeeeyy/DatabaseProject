import json
import socket
import sqlite3
import threading
from datetime import datetime

from encryption import decrypt
from password_handler import create_user, authenticate_user


def handle_client(client_socket):
    try:
        conn = sqlite3.connect("pizza.db")
        cursor = conn.cursor()

        global_key_server = client_socket.recv(16)
        print(f"Received global key: {global_key_server}")

        while True:
            try:
                encrypted_request = client_socket.recv(1024).decode('utf-8')
                if not encrypted_request:
                    break
                request = decrypt(encrypted_request, global_key_server)
                request_data = json.loads(request)
                action = request_data['action']
                match action:
                    case 'place_order':
                        customer_id = request_data['customer_id']
                        items = request_data['items']
                        discount_code = request_data.get('discount_code')
                        confirmation_details = place_order(cursor, customer_id, items, discount_code)
                        conn.commit()
                        response = json.dumps(confirmation_details)
                    case 'get_menu':
                        menu = get_menu(cursor)
                        client_socket.send(json.dumps(menu).encode('utf-8'))
                    case 'get_history':
                        customer_id = request_data['customer_id']
                        order_history = get_history(cursor, customer_id)
                        client_socket.send(json.dumps(order_history).encode('utf-8'))
                    case 'register':
                        username = request_data['username']
                        gender = request_data['gender']
                        birthdate = request_data['birthdate']
                        phone = request_data['phone']
                        address = request_data['address']
                        password = request_data['password']
                        create_user(username, gender, birthdate, phone, address, password)
                        client_socket.send(b"User registered successfully!")
                    case 'authenticate':
                        username = request_data['username']
                        pw_hash = request_data['pw_hash']
                        authenticate_user(cursor, username, pw_hash)
                    case 'get_favourite_item':
                        customer_id = request_data['customer_id']
                        favourite_items = get_favourite_item(cursor, customer_id)
                        if favourite_items:
                            client_socket.send(json.dumps({favourite_items}).encode('utf-8'))
                        else:
                            client_socket.send(
                                json.dumps({'message': 'No purchases found to determine favorite item.'}).encode(
                                    'utf-8'))
                    case _:
                        client_socket.send(json.dumps({'error': 'Unknown action/procedure'}).encode('utf-8'))
            except (json.JSONDecodeError, KeyError) as e:
                client_socket.send(json.dumps({"'error': 'Invalid request format'"}).encode('utf-8'))
                print(f"Error decoding request: {e}")
            except sqlite3.DatabaseError as e:
                client_socket.send(json.dumps({"'error': 'Database error'"}).encode('utf-8'))
                print(f"Database error: {e}")
            except Exception as e:
                client_socket.send(json.dumps({"'error': 'Server error'"}).encode('utf-8'))
                print(f"Exception! {e}")
    except sqlite3.DatabaseError as e:
        client_socket.send(json.dumps({"'error': 'failed to connect to database!'"}))
        print(f"Failed to connect to database: {e}!")
    finally:
        if conn:
            conn.close()
        client_socket.close()

def place_order(cursor, customer_id, items, discount_code = None):
    cursor.execute('INSERT INTO Orders (customer_id, discount_code, order_time) VALUES (?, ?, ?)',
                   (customer_id, discount_code, datetime.now()))
    order_id = cursor.lastrowid

    for item_type, item_id, quantity in items:
        cursor.execute('INSERT INTO OrderItems (order_id, item_type, item_id, quantity) VALUES (?,?,?,?)',
                       (order_id, item_type, item_id, quantity))
    estimated_delivery_time = datetime.now() * datetime.timedelta(minutes = 30)

    cursor.execute('''
        SELECT o.id, oi.order_time, oi.item_id, p.name AS pizza_name, d.name AS drink_name, ds.name AS desert_name
        FROM Orders o
        JOIN OrderItems oi ON o.id = oi.order_id
        LEFT JOIN Pizzas p ON oi.item_type = 'pizza' AND oi.item_id = p.id
        LEFT JOIN Drinks d ON io.item_type = 'drink' AND oi.item_id = d.id
        LEFT JOIN Desserts ds ON io.item_type = 'dessert' AND io.item_id = ds.id
        WHERE o.id = ?
    ''', (order_id,))
    order_details = cursor.fetchall()

    confirmation_details = {
        'order_id': order_id,
        'order_time': order_details[0][1],
        'estimated_delivery_time': estimated_delivery_time,
        'items': []
    }

    for detail in order_details:
        item = {
            'item_type': detail[2],
            'item_id': detail[3],
            'quantity': detail[4],
            'name': detail[5] or detail[6] or detail[7]
        }
        confirmation_details['items'].append(item)

    return confirmation_details




def get_menu(cursor):
    cursor.execute('SELECT * FROM Pizzas')
    pizzas = cursor.fetchall()
    cursor.execute('SELECT * FROM Drinks')
    drinks = cursor.fetchall()
    cursor.execute('SELECT * FROM Desserts')
    deserts = cursor.fetchall()
    return {'pizzas': pizzas, 'drinks': drinks, 'deserts': deserts}


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
                cursor.execute('SELECT name, price FROM Pizzas WHERE id = ?', (item_id,))
            elif item_type == 'drink':
                cursor.execute('SELECT name, price FROM Drinks WHERE id = ?', (item_id,))
            elif item_type == 'dessert':
                cursor.execute('SELECT name, price FROM Desserts WHERE id = ?', (item_id,))
            item_info = cursor.fetchone()
            if item_info:
                name, price = item_info
                order_items.append(
                    {'item_type': item_type, 'item_id': item_id, 'name': name, 'quantity': quantity, 'price': price})

        order_history.append(
            {'order_id': order_id, 'order_date': order_date, 'status': status, 'discount_applied': discount_applied,
             'total_price': total_price, 'items': order_items})

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
        favourite_items.append(
            {'item_type': item_type, 'item_id': item_id, 'item_name': item_name, 'total_quantity': total_quantity})

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
