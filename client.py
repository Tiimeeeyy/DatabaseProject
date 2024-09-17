import socket
import json
from http.client import responses


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
	print(json.dumps(menu, indent=4))

def get_history(client_socket, customer_id, discount_applied):
	request_data = {
		'action': 'get_history',
		'customer_id': customer_id,
		'discount_code': discount_applied,
	}

	request = json.dumps(request_data)
	client_socket.send(request.encode('utf-8'))
	response = client_socket.recv(4096)
	print(response.decode('utf-8'))

def get_fav_item(client_socket, customer_id):
	request_data = {
		'action': 'get_favourite_item',
		'customer_id': customer_id
	}

	request = json.dumps(request_data)
	client_socket.send(request.encode('utf-8'))
	response = client_socket.recv(4096)
	print(response.decode('utf-8'))

def register_user(client_socket, username, gender, birthdate, phone, address, password):
	request_data = {
		'action': 'register',
		'username': username,







	}

def client():
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect(('127.0.0.1', 9999))

	place_order(client_socket, 1, [('pizza', 1, 2), ('drink', 1, 1)], discount_code='DISCOUNT10')
	get_menu(client_socket)

	client_socket.close()

