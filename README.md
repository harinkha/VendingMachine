Vending Machine

A simple Vending Machine API built with Python and Flask.

SonarCloud Coverage:
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=harinkha_VendingMachine&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=harinkha_VendingMachine)

Features:
- Add, update, and remove products
- Process purchases and return change
- Track inventory and transactions

Installation:

To install the Vending Machine API, make sure you have Python 3.10 and Poetry installed on your system.

1. Clone the repository:
git clone https://github.com/harinkha/VendingMachine.git
cd VendingMachine

2. Install dependencies:
poetry install

3. Start the Flask development server:
flask run

The Vending Machine API should now be accessible at http://127.0.0.1:5000/.


Running Tests:

To run tests, use the following command:
poetry run pytest -k "test_app.py"

License:

This project is licensed under the MIT License.
