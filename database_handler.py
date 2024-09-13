import sqlite3

# Establish a connection to the database
conn = sqlite3.connect("pizza.db")
cursor = conn.cursor()

# Insert sample data for ingredients
ingredients = [
    (1, 'Tomato Sauce', 0.5),
    (2, 'Cheese', 1.0),
    (3, 'Pepperoni', 1.5),
    (4, 'Mushrooms', 0.7),
    (5, 'Onions', 0.3),
    (6, 'Olives', 0.6),
    (7, 'Bell Peppers', 0.5),
    (8, 'Bacon', 1.2),
    (9, 'Pineapple', 0.8),
    (10, 'Spinach', 0.4)
]

cursor.executemany('''
INSERT INTO Ingredients (id, name, cost) VALUES (?, ?, ?)
''', ingredients)

# Insert sample data for pizzas
pizzas = [
    (1, 'Margherita', 5.0, True, True),
    (2, 'Pepperoni', 6.5, False, False),
    (3, 'Vegetarian', 6.0, True, True),
    (4, 'Hawaiian', 7.0, False, False),
    (5, 'BBQ Chicken', 7.5, False, False),
    (6, 'Meat Lovers', 8.0, False, False),
    (7, 'Supreme', 8.5, False, False),
    (8, 'Four Cheese', 7.0, True, False),
    (9, 'Spinach Alfredo', 6.5, True, False),
    (10, 'Bacon Cheeseburger', 8.0, False, False)
]

cursor.executemany('''
INSERT INTO Pizzas (id, name, price, is_vegetarian, is_vegan) VALUES (?, ?, ?, ?, ?)
''', pizzas)

# Insert sample data for drinks
drinks = [
    (1, 'Coke', 1.5),
    (2, 'Sprite', 1.5),
    (3, 'Water', 1.0),
    (4, 'Orange Juice', 2.0)
]

cursor.executemany('''
INSERT INTO Drinks (id, name, price) VALUES (?, ?, ?)
''', drinks)

# Insert sample data for desserts
desserts = [
    (1, 'Chocolate Cake', 3.0),
    (2, 'Ice Cream', 2.5)
]

cursor.executemany('''
INSERT INTO Desserts (id, name, price) VALUES (?, ?, ?)
''', desserts)

# Insert sample data for customers
customers = [
    (1, 'John Doe', 'Male', '1990-01-01', '1234567890', '123 Main St', 0, None),
    (2, 'Jane Smith', 'Female', '1985-05-15', '0987654321', '456 Elm St', 0, None)
]

cursor.executemany('''
INSERT INTO Customers (id, name, gender, birthdate, phone, address, pizzas_ordered, discount_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', customers)

# Commit the changes and close the connection
conn.commit()
conn.close()