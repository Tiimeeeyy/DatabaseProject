import socket
import json


def place_order(client_socket, customer_id, items, discount_code=None):
	request_data = {
		'action': 'place_order',
		'customer_id': customer_id,
		'items': items,
		'discount_code': discount_code
	}

	request = json.dumps(request_data)
	client_socket.send(request.encode('utf-8'))
	response = client_socket.recv(1024)
	print(response.decode('utf-8'))

def get_menu(client_socket):
	request_data = {
		'action': 'get_menu'
	}

	request = json.dumps(request_data)
	client_socket.send(request.encode('utf-8'))
	response = client_socket.recv(4096)
	menu = json.loads(response.decode('utf-8'))
	print(menu)

def client():
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect(('127.0.0.1', 9999))

	place_order(client_socket, 1, [('pizza', 1, 2), ('drink', 1, 1)], discount_code='DISCOUNT10')
	get_menu(client_socket)

	client_socket.close()

