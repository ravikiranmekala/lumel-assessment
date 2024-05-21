from app import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.String(50), db.ForeignKey('customers.customer_id'), nullable=False)
    date_of_sale = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, nullable=False)

    customer = db.relationship('Customer', back_populates='orders')
    order_details = db.relationship('OrderDetail', back_populates='order', cascade="all, delete-orphan")


class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.String(50), primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

    order_details = db.relationship('OrderDetail', back_populates='product', cascade="all, delete-orphan")


class OrderDetail(db.Model):
    __tablename__ = 'order_details'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.String(50), db.ForeignKey('products.product_id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)

    order = db.relationship('Order', back_populates='order_details')
    product = db.relationship('Product', back_populates='order_details')


class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.String(50), primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False, unique=True)
    customer_address = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(255), nullable=False)

    orders = db.relationship('Order', back_populates='customer', cascade="all, delete-orphan")