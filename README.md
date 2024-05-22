# lumel-assessment

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL database
- `pip` for installing Python packages

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/ravikiranmekala/lumel-assessment.git
    ```

2. **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure the database:**
   Edit `config.py` to set up your database connection:
    ```python
    class Config:
        SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/postgres'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    ```

5. **Initialize and apply database migrations:**
    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

### Running the ETL Script

1. **Place your CSV file (`sales_data.csv`) in the scripts directory.**

2. **Run the ETL script to load the data:**
    ```bash
    python scripts/data_population.py
    ```

### Running the Flask Application

1. **Set the `FLASK_APP` environment variable:**
    ```bash
    export FLASK_APP=run.py  # On Windows, use `set FLASK_APP=run.py`
    ```

2. **Run the Flask application:**
    ```bash
    flask run
    ```

## ETL Script

The ETL script (`data_population.py`) performs the following tasks:
- Clears existing data from the `orders`, `products`, `customers`, and `order_details` tables.
- Reads and processes the CSV file
- Inserts the processed data into the respective tables in the correct order to respect foreign key constraints.


