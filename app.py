import logging
import time
import threading
from sqlalchemy import func
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from scripts.data_population import refresh_data_from_file


db = SQLAlchemy()
migrate = Migrate()

def refresh_data():
    while True:
        try:
            print("Refreshing data started")
            refresh_data_from_file('scripts/sales_data.csv')
            print("Refreshing data done")
        except KeyboardInterrupt:
            print("Stopping data refresh")
        finally:
            print("Refreshing data done")
            time.sleep(24*60*60)

# Function to start the background thread
def start_data_refresh_thread():
    refresh_thread = threading.Thread(target=refresh_data)
    refresh_thread.daemon = True  # Ensure thread exits when the main program does
    refresh_thread.start()

# Start the background thread
start_data_refresh_thread()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    with app.app_context():
        from routes import register_routes
        register_routes(app)
    return app


app = create_app()

if __name__ == '__main__':
    app.run()
