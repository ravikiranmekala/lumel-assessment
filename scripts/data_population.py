import csv
import logging
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a database connection
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

# Function to clear tables with commit
def clear_tables():
    logging.info("Clearing tables")
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text("TRUNCATE TABLE order_details RESTART IDENTITY CASCADE;"))
            connection.execute(text("TRUNCATE TABLE orders RESTART IDENTITY CASCADE;"))
            connection.execute(text("TRUNCATE TABLE products RESTART IDENTITY CASCADE;"))
            connection.execute(text("TRUNCATE TABLE customers RESTART IDENTITY CASCADE;"))
            transaction.commit()
            logging.info("Tables cleared successfully.")
        except Exception as e:
            transaction.rollback()
            logging.error(f"Error clearing tables: {e}")
            raise

def process_chunk(rows):
    customers = {}
    products = {}
    orders = []
    order_details = []

    for row in rows:
        # Process customers
        customer_id = row['Customer ID']
        if customer_id not in customers:
            customers[customer_id] = {
                'customer_id': customer_id,
                'customer_name': row['Customer Name'],
                'customer_email': row['Customer Email'],
                'customer_address': row['Customer Address'],
                'region': row['Region']
            }

        # Process products
        product_id = row['Product ID']
        if product_id not in products:
            products[product_id] = {
                'product_id': product_id,
                'product_name': row['Product Name'],
                'category': row['Category'],
                'unit_price': float(row['Unit Price'])
            }

        # Process orders
        order = {
            'order_id': int(row['Order ID']),
            'customer_id': customer_id,
            'date_of_sale': row['Date of Sale'],
            'payment_method': row['Payment Method'],
            'shipping_cost': float(row['Shipping Cost']),
            'discount': float(row['Discount']),
            'total_amount': float(row['Quantity Sold']) * float(row['Unit Price']) - float(row['Quantity Sold']) * float(row['Unit Price']) * float(row['Discount'])
        }
        orders.append(order)

        # Process order details
        order_detail = {
            'order_id': int(row['Order ID']),
            'product_id': product_id,
            'quantity_sold': int(row['Quantity Sold'])
        }
        order_details.append(order_detail)

    return customers.values(), products.values(), orders, order_details

def insert_data(data, table_name):
    logging.info(f"Inserting data into {table_name}")
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            for row in data:
                keys = ', '.join(row.keys())
                values = ', '.join([f":{key}" for key in row.keys()])
                sql = f"INSERT INTO {table_name} ({keys}) VALUES ({values})"
                connection.execute(text(sql), row)
            transaction.commit()
            logging.info(f"Data inserted into {table_name} successfully.")
        except Exception as e:
            transaction.rollback()
            logging.error(f"Error inserting data into {table_name}: {e}")
            raise

def refresh_data_from_file(file_name, chunk_size=1000):
    logging.info("Starting ETL process")
    clear_tables()

    customers = []
    products = []
    orders = []
    order_details = []

    logging.info("Processing CSV file")
    with open(file_name, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, quotechar='"')
        chunk = []
        for row in reader:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                c, p, o, od = process_chunk(chunk)
                customers.extend(c)
                products.extend(p)
                orders.extend(o)
                order_details.extend(od)
                chunk = []

        if chunk:
            c, p, o, od = process_chunk(chunk)
            customers.extend(c)
            products.extend(p)
            orders.extend(o)
            order_details.extend(od)

    # Remove duplicates
    customers = {customer['customer_id']: customer for customer in customers}.values()
    products = {product['product_id']: product for product in products}.values()

    # Insert data into database in the correct order to avoid integrity errors
    insert_data(customers, 'customers')
    insert_data(products, 'products')
    insert_data(orders, 'orders')
    insert_data(order_details, 'order_details')

    logging.info("Data inserted successfully.")

if __name__ == '__main__':
    refresh_data_from_file('sales_data.csv', chunk_size=1000)  # You can adjust the chunk size as needed
