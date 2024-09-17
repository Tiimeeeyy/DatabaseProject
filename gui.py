import tkinter as tk
from tkinter import messagebox
import socket
import json

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        self.username_label = tk.Label(root, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        self.password_label = tk.Label(root, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.verify_credentials(username, password):
            self.root.destroy()
            main_window = tk.Tk()
            PizzaApp(main_window, username)
            main_window.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def verify_credentials(self, username, password):
        # Here you would typically send the credentials to the server for verification
        # For simplicity, we'll just check if they match a hardcoded value
        return username == "user" and password == "pass"

class PizzaApp:
    def __init__(self, root, username):
        self.root = root
        self.root.title(f"Pizza Ordering System - {username}")

        self.username = username
        self.menu = self.get_menu()
        self.cart = []

        self.create_widgets()

    def create_widgets(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.cart_frame = tk.Frame(self.root)
        self.cart_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.menu_label = tk.Label(self.menu_frame, text="Menu")
        self.menu_label.pack()

        self.menu_listbox = tk.Listbox(self.menu_frame, selectmode=tk.MULTIPLE)
        self.menu_listbox.pack()

        for category, items in self.menu.items():
            self.menu_listbox.insert(tk.END, f"--- {category} ---")
            for item in items:
                self.menu_listbox.insert(tk.END, f"{item[1]} - ${item[2]}")

        self.add_to_cart_button = tk.Button(self.menu_frame, text="Add to Cart", command=self.add_to_cart)
        self.add_to_cart_button.pack(pady=5)

        self.cart_label = tk.Label(self.cart_frame, text="Cart")
        self.cart_label.pack()

        self.cart_listbox = tk.Listbox(self.cart_frame)
        self.cart_listbox.pack()

        self.place_order_button = tk.Button(self.cart_frame, text="Place Order", command=self.place_order)
        self.place_order_button.pack(pady=5)

    def get_menu(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 9999))

        request_data = {'action': 'get_menu'}
        request = json.dumps(request_data)
        client_socket.send(request.encode('utf-8'))

        response = client_socket.recv(4096)
        menu = json.loads(response.decode('utf-8'))

        client_socket.close()
        return menu

    def add_to_cart(self):
        selected_indices = self.menu_listbox.curselection()
        for index in selected_indices:
            item = self.menu_listbox.get(index)
            if not item.startswith("---"):
                self.cart.append(item)
                self.cart_listbox.insert(tk.END, item)

    def place_order(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Your cart is empty!")
            return

        items = []
        for item in self.cart:
            item_details = item.split(" - $")
            item_name = item_details[0]
            item_price = float(item_details[1])
            # Assuming item_type and item_id are known or can be derived
            item_type = 'pizza'  # Example, should be determined based on actual item
            item_id = 1  # Example, should be determined based on actual item
            quantity = 1  # Example, can be modified to allow user to select quantity
            items.append((item_type, item_id, quantity))

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 9999))

        request_data = {
            'action': 'place_order',
            'customer_id': 1,  # Example, should be determined based on actual user
            'items': items,
            'discount_code': None  # Example, can be modified to allow user to enter discount code
        }
        request = json.dumps(request_data)
        client_socket.send(request.encode('utf-8'))

        response = client_socket.recv(1024)
        messagebox.showinfo("Order Status", response.decode('utf-8'))

        client_socket.close()
        self.cart.clear()
        self.cart_listbox.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()