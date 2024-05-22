from flask import jsonify, request
from sqlalchemy import func
from models import db, Order, Product, OrderDetail, Customer
from scripts.data_population import refresh_data_from_file
import logging

def register_routes(app):
    @app.route('/')
    def home():
        return 'home !'

    @app.route('/refresh', methods=['POST'])
    def refresh_data_on_demand():
        try:
            refresh_data_from_file('scripts/sales_data.csv')
            return jsonify({"status": "success"}), 200
        except Exception as e:
            logging.error(f"Error during data refresh: {e}")
            return jsonify({"status": "failure", "error": str(e)}), 500

    @app.route('/revenue/total', methods=['GET'])
    def total_revenue():
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        revenue = db.session.query(func.sum(Order.total_amount)).filter(Order.date_of_sale.between(start_date, end_date)).scalar()
        return jsonify({"total_revenue": revenue}), 200

    @app.route('/revenue/product', methods=['GET'])
    def revenue_by_product():
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        results = db.session.query(Product.product_name, func.sum(OrderDetail.quantity_sold * Product.unit_price)).join(OrderDetail).join(Order).filter(Order.date_of_sale.between(start_date, end_date)).group_by(Product.product_name).all()
        return jsonify({"revenue_by_product": {product: revenue for product, revenue in results}}), 200

    @app.route('/revenue/category', methods=['GET'])
    def revenue_by_category():
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        results = db.session.query(Product.category, func.sum(OrderDetail.quantity_sold * Product.unit_price)).join(OrderDetail).join(Order).filter(Order.date_of_sale.between(start_date, end_date)).group_by(Product.category).all()
        return jsonify({"revenue_by_category": {category: revenue for category, revenue in results}}), 200

    @app.route('/revenue/region', methods=['GET'])
    def revenue_by_region():
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        results = db.session.query(Customer.region, func.sum(Order.total_amount)).join(Customer).filter(Order.date_of_sale.between(start_date, end_date)).group_by(Customer.region).all()
        return jsonify({"revenue_by_region": {region: revenue for region, revenue in results}}), 200
