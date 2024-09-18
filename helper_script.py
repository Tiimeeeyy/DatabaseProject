def calculate_pizza_price(ingredient_cost):
    base_price = sum(ingredient_cost)

    price_w_profit = base_price * 1.40

    final_price = price_w_profit * 1.09

    return round(final_price, 2)