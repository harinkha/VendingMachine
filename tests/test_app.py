import json

import pytest

from vending_machine.app import Machine, Products, app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        db.drop_all()


def test_add_machine(client):
    response = client.post(
        "/addmachine", json={"name": "Machine A", "location": "Location A"}
    )
    assert response.status_code == 200
    assert b"Machine A" in response.data


# Add the remaining test cases here
def test_get_machine(client):
    machine = Machine(name="Machine A", location="Location A")
    db.session.add(machine)
    db.session.commit()

    response = client.get(f"/machine/{machine.id}")
    assert response.status_code == 200
    assert b"Machine A" in response.data


def test_update_machine(client):
    machine = Machine(name="Machine A", location="Location A")
    db.session.add(machine)
    db.session.commit()

    updated_machine = {"name": "Machine A Updated", "location": "Location A Updated"}
    response = client.put(
        f"/machine/{machine.id}",
        data=json.dumps(updated_machine),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert b"Machine A Updated" in response.data


def test_delete_machine(client):
    machine = Machine(name="Machine A", location="Location A")
    db.session.add(machine)
    db.session.commit()

    response = client.delete(f"/machine/{machine.id}")
    assert response.status_code == 200
    assert b"Machine A" in response.data


def test_get_all_machines(client):
    machine = Machine(name="Machine A", location="Location A")
    db.session.add(machine)
    db.session.commit()

    response = client.get("/getmachines")
    assert response.status_code == 200
    assert b"Machine A" in response.data


def test_get_product(client):
    product = Products(name="Product A", quantity=10, stored="Machine A")
    db.session.add(product)
    db.session.commit()

    response = client.get(f"/product/{product.id}")
    assert response.status_code == 200
    assert b"Product A" in response.data


def test_update_product(client):
    product = Products(name="Product A", quantity=10, stored="Machine A")
    db.session.add(product)
    db.session.commit()

    updated_product = {
        "name": "Product A Updated",
        "quantity": 20,
        "stored": "Machine B",
    }
    response = client.put(
        f"/product/{product.id}",
        data=json.dumps(updated_product),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert b"Product A Updated" in response.data


def test_delete_product(client):
    product = Products(name="Product A", quantity=10, stored="Machine A")
    db.session.add(product)
    db.session.commit()

    response = client.delete(f"/product/{product.id}")
    assert response.status_code == 200
    assert b"Product A" in response.data


def test_get_all_products(client):
    product = Products(name="Product A", quantity=10, stored="Machine A")
    db.session.add(product)
    db.session.commit()

    response = client.get("/getproducts")
    assert response.status_code == 200
    assert b"Product A" in response.data


def test_check_products_of_machine(client):
    product_a = Products(name="Product A", quantity=10, stored="Machine A")
    product_b = Products(name="Product B", quantity=15, stored="Machine B")
    product_c = Products(name="Product C", quantity=5, stored="Machine A")
    db.session.add(product_a)
    db.session.add(product_b)
    db.session.add(product_c)
    db.session.commit()

    response = client.post(
        "/products/Machine A", data=json.dumps({}), content_type="application/json"
    )
    assert response.status_code == 200
    assert b"Product A" in response.data
    assert b"Product C" in response.data
    assert b"Product B" not in response.data


def test_add_product_to_machine(setup_teardown):
    with app.test_client() as client:
        response = client.post(
            "/addproduct",
            json={"name": "Sample Product", "quantity": 10, "stored": "Test Machine"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Sample Product"
        assert data["quantity"] == 10
        assert data["stored"] == "Test Machine"


def test_purchase_product(setup_teardown):
    with app.test_client() as client:
        # Add a product to test with
        product = Products(name="Sample Product", quantity=10, stored="Test Machine")
        db.session.add(product)
        db.session.commit()

        response = client.post(f"/purchaseproduct/{product.id}/5")

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Product purchased"

        # Check if the quantity was updated correctly
        updated_product = Products.query.get(product.id)
        assert updated_product.quantity == 5


def test_purchase_product_insufficient_stock(setup_teardown):
    with app.test_client() as client:
        # Add a product to test with
        product = Products(name="Sample Product", quantity=10, stored="Test Machine")
        db.session.add(product)
        db.session.commit()

        response = client.post(f"/purchaseproduct/{product.id}/15")

        assert response.status_code == 400
        data = response.get_json()
        assert data["message"] == "Insufficient stock"

        # Check if the quantity was not updated
        updated_product = Products.query.get(product.id)
        assert updated_product.quantity == 10
