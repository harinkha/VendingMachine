"""This module contains the main application logic for the vending machine."""


import os

from flask import Flask, request
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


# Machine CRUD


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

    new_product = Products(name, quantity, stored)

    db.session.add(new_product)
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


# Run Server
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
