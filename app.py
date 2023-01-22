from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db. sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)

app.app_context().push()


@app.route('/addmachine', methods=['POST'])
def add_machine():
    name = request.json['name']
    location = request.json['location']

    new_machine = Machine(name, location)

    db.session.add(new_machine)
    db.session.commit()

    return MachineSchema().jsonify(new_machine)


@app.route('/addproduct', methods=['POST'])
def add_product_to_machine():
    name = request.json['name']
    quantity = request.json['quantity']
    stored=request.json['stored']

    new_product = Products(name, quantity, stored)

    db.session.add(new_product)
    db.session.commit()

    return ProductSchema().jsonify(new_product)


class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    location = db.Column(db.String(100))

    def __init__(self, name, location):
        self.name = name
        self.location = location


class MachineSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'location')


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
        fields = ('id', 'name', 'quantity', 'stored')


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
