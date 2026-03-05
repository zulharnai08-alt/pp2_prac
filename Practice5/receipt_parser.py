import re
import json

# Читаем файл с чеком | Read receipt file
with open("raw.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Разделяем текст на строки | Split text into lines
lines = text.split("\n")

products = []   # список товаров | list of products
prices = []     # список цен | list of prices

# Regex для цены | regex for price
price_pattern = re.compile(r'\d+\.\d{2}')

# Ищем товары и цены | find products and prices
for line in lines:
    price_match = price_pattern.search(line)

    if price_match:
        price = float(price_match.group())  # найденная цена | found price
        prices.append(price)

        # Убираем цену из строки чтобы получить название | remove price to get product name
        product = line.replace(price_match.group(), "").strip()
        if product:
            products.append(product)

# Считаем общую сумму | calculate total
total = sum(prices)

# Regex для даты | regex for date
date_match = re.search(r'\d{2}/\d{2}/\d{4}', text)

# Regex для времени | regex for time
time_match = re.search(r'\d{2}:\d{2}', text)

# Regex для способа оплаты | regex for payment method
payment_match = re.search(r'(Cash|Card|Visa|MasterCard)', text, re.IGNORECASE)

# Формируем результат | create result
result = {
    "products": products,
    "prices": prices,
    "total": total,
    "date": date_match.group() if date_match else None,
    "time": time_match.group() if time_match else None,
    "payment_method": payment_match.group() if payment_match else None
}

# Печатаем результат красиво | print result nicely
print(json.dumps(result, indent=4))
