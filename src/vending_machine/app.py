"""This module contains the main application logic for the vending machine."""

import os

from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "../../db.sqlite"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)

app.app_context().push()


class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    location = db.Column(db.String(100))

    def __init__(self, name, location):
        self.name = name
        self.location = location


class MachineSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "location")


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    stored = db.Column(db.String(50))

    def __init__(self, name, quantity, stored):
        self.name = name
        self.quantity = quantity
        self.stored = stored


class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "quantity", "stored")


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
machine_schema = MachineSchema()
machines_schema = MachineSchema(many=True)


class StockHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    quantity = db.Column(db.Integer)

    def __init__(self, product_id, machine_id, quantity):
        self.product_id = product_id
        self.machine_id = machine_id
        self.quantity = quantity


class StockHistorySchema(ma.Schema):
    class Meta:
        fields = ("id", "product_id", "machine_id", "timestamp", "quantity")


stock_history_schema = StockHistorySchema()
stock_history_schema_many = StockHistorySchema(many=True)


@app.route("/addmachine", methods=["POST"])
def add_machine():
    name = request.json["name"]
    location = request.json["location"]

    new_machine = Machine(name, location)

    db.session.add(new_machine)
    db.session.commit()

    return machine_schema.jsonify(new_machine)


@app.route("/machine/<id>", methods=["GET"])
def get_machine(id):
    machine = Machine.query.get(id)
    return machine_schema.jsonify(machine)


@app.route("/machine/<id>", methods=["PUT"])
def update_machine(id):
    machine = Machine.query.get(id)

    name = request.json["name"]
    location = request.json["location"]

    machine.name = name
    machine.location = location

    db.session.commit()

    return machine_schema.jsonify(machine)


@app.route("/machine/<id>", methods=["DELETE"])
def delete_machine(id):
    machine = Machine.query.get(id)
    db.session.delete(machine)
    db.session.commit()

    return machine_schema.jsonify(machine)


@app.route("/getmachines", methods=["GET"])
def get_all_machines():
    all_machines = Machine.query.all()
    return machines_schema.jsonify(all_machines)


# Products CRUD


@app.route("/addproduct", methods=["POST"])
def add_product():
    name = request.json["name"]
    quantity = request.json["quantity"]
    stored = request.json["stored"]

    existing_product = Products.query.filter_by(name=name, stored=stored).first()

    if existing_product:
        existing_product.quantity = quantity
        db.session.commit()
        product_id = existing_product.id
    else:
        new_product = Products(name, quantity, stored)
        db.session.add(new_product)
        db.session.commit()
        product_id = new_product.id

    machine = Machine.query.filter_by(name=stored).first()
    new_stock_history = StockHistory(
        product_id=product_id, machine_id=machine.id, quantity=quantity
    )
    db.session.add(new_stock_history)
    db.session.commit()

    return product_schema.jsonify(new_product)


@app.route("/product/<id>", methods=["GET"])
def get_product(id):
    product = Products.query.get(id)
    return product_schema.jsonify(product)


@app.route("/product/<id>", methods=["PUT"])
def update_product(id):
    product = Products.query.get(id)
    name = request.json["name"]
    quantity = request.json["quantity"]
    stored = request.json["stored"]

    product.name = name
    product.quantity = quantity
    product.stored = stored
    product.stored = stored
    db.session.commit()

    return product_schema.jsonify(product)


@app.route("/product/<id>", methods=["DELETE"])
def delete_product(id):
    product = Products.query.get(id)
    db.session.delete(product)
    db.session.commit()

    return product_schema.jsonify(product)


@app.route("/getproducts", methods=["GET"])
def get_all_products():
    all_products = Products.query.all()
    return products_schema.jsonify(all_products)


@app.route("/products/<machine>", methods=["POST"])
def check_products_of_machine(machine):
    products = Products.query.filter_by(stored=machine).all()
    return products_schema.jsonify(products)


@app.route("/purchaseproduct/<product_id>/<int:quantity>", methods=["POST"])
def purchase_product(product_id, quantity):
    product = Products.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    machine = Machine.query.filter_by(name=product.stored).first()
    if not machine:
        return jsonify({"message": "Machine not found"}), 404

    if product.quantity < quantity:
        return jsonify({"message": "Insufficient stock"}), 400

    product.quantity -= quantity
    db.session.add(product)

    new_stock_history = StockHistory(
        product_id=product.id, machine_id=machine.id, quantity=product.quantity
    )
    db.session.add(new_stock_history)

    db.session.commit()

    return jsonify({"message": "Product purchased"})


@app.route("/stockhistory/<machine_id>/<product_id>", methods=["GET"])
def get_stock_history(machine_id, product_id):
    history = (
        StockHistory.query.filter_by(machine_id=machine_id, product_id=product_id)
        .order_by(StockHistory.timestamp.asc())
        .all()
    )
    return stock_history_schema_many.jsonify(history)


# Run Server
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
