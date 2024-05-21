import csv
import concurrent.futures
from sqlalchemy import create_engine, text

# Create a database connection
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

def clear_tables():
    with engine.connect() as connection:
        connection.execute(text("TRUNCATE TABLE order_details RESTART IDENTITY CASCADE;"))
        connection.execute(text("TRUNCATE TABLE orders RESTART IDENTITY CASCADE;"))
        connection.execute(text("TRUNCATE TABLE products RESTART IDENTITY CASCADE;"))
        connection.execute(text("TRUNCATE TABLE customers RESTART IDENTITY CASCADE;"))

def process_row(row):
    # Normalize and transform data
    order = {
        'order_id': int(row['Order ID']),
        'customer_id': row['Customer ID'],
        'date_of_sale': row['Date of Sale'],
        'payment_method': row['Payment Method'],
        'shipping_cost': float(row['Shipping Cost']),
        'discount': float(row['Discount']),
        'total_amount': float(row['Quantity Sold']) * float(row['Unit Price']) - float(row['Quantity Sold']) * float(row['Unit Price']) * float(row['Discount'])
    }

    product = {
        'product_id': row['Product ID'],
        'product_name': row['Product Name'],
        'category': row['Category'],
        'unit_price': float(row['Unit Price'])
    }

    customer = {
        'customer_id': row['Customer ID'],
        'customer_name': row['Customer Name'],
        'customer_email': row['Customer Email'],
        'customer_address': row['Customer Address'],
        'region': row['Region']
    }

    order_detail = {
        'order_id': int(row['Order ID']),
        'product_id': row['Product ID'],
        'quantity_sold': int(row['Quantity Sold'])
    }

    return order, product, customer, order_detail

def insert_data(data, table_name):
    with engine.connect() as connection:
        for row in data:
            keys = ', '.join(row.keys())
            values = ', '.join([f":{key}" for key in row.keys()])
            sql = f"INSERT INTO {table_name} ({keys}) VALUES ({values})"
            connection.execute(text(sql), row)

def main():
    clear_tables()

    orders = []
    products = []
    customers = []
    order_details = []

    with open('sales_data.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_row, row) for row in reader]
            for future in concurrent.futures.as_completed(futures):
                order, product, customer, order_detail = future.result()
                orders.append(order)
                products.append(product)
                customers.append(customer)
                order_details.append(order_detail)

    # Remove duplicates
    products = {product['product_id']: product for product in products}.values()
    customers = {customer['customer_id']: customer for customer in customers}.values()

    # Insert data into database
    insert_data(customers, 'customers')
    insert_data(products, 'products')
    insert_data(orders, 'orders')
    insert_data(order_details, 'order_details')

    print("Data has been successfully loaded into the database.")

if __name__ == '__main__':
    main()