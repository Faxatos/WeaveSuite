import pytest
import requests
import uuid
import random
import string
from urllib.parse import urljoin

MICROSERVICES = {
    "carts": "http://carts.sockshop-core.svc.cluster.local:80",
    "catalogue": "http://catalogue.sockshop-core.svc.cluster.local:80",
    "orders": "http://orders.sockshop-core.svc.cluster.local:80",
    "payment-http": "http://payment-http.sockshop-core.svc.cluster.local:80",
    "shipping-http": "http://shipping-http.sockshop-core.svc.cluster.local:80",
    "user": "http://user.sockshop-core.svc.cluster.local:80",
}

def get_url(service: str, path: str) -> str:
    base = MICROSERVICES.get(service)
    if not base:
        raise ValueError(f"Service {service} not found")
    return urljoin(base, path)

# --- Tests ---

def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    email = f"{username}@example.com"

    # Register User
    user_payload = {"username": username, "password": password, "email": email, "firstName": "John", "lastName": "Doe"}
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify User Registration
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login User
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_user_login_unauthorized():
    resp = requests.get(get_url("user", "/login"), auth=("invalid_user", "invalid_pass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

def test_user_registration_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    
    # First registration
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Second registration conflict
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

def test_orders_end_to_end_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    
    # Register
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Address
    addr_payload = {"street": "123 Main St", "city": "Anytown", "country": "USA", "number": "123", "postcode": "12345", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")

    # Verify Address
    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Card
    card_payload = {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    # Verify Card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Get Catalogue Item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    item_id = items[0]["id"]
    unit_price = 10.0

    # Add to Cart
    cart_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify Cart
    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")

    # Verify Order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_orders_payment_declined():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    
    # Register
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Address
    addr_payload = {"street": "123 Main St", "city": "Anytown", "country": "USA", "number": "123", "postcode": "12345", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")

    # Verify Address
    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Card
    card_payload = {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    # Verify Card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add to Cart with high amount to trigger decline (> 100)
    cart_payload = {"itemId": "item-123", "quantity": 10, "unitPrice": 50.0}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify Cart
    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    # Verify Order not created
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_delete_item():
    username = f"user_{uuid.uuid4().hex[:8]}"
    item_id = "item-456"
    
    # Add to Cart
    cart_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 15.0}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify Cart
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Delete Item
    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify Deletion
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_item_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    invalid_item_id = f"invalid_{uuid.uuid4().hex}"
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{invalid_item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_catalogue_item_not_found():
    invalid_id = f"invalid_{uuid.uuid4().hex}"
    resp = requests.get(get_url("catalogue", f"/catalogue/{invalid_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_payment_authorization_success():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"street": "123 Main St", "city": "Anytown", "country": "USA", "number": "123", "postcode": "12345"},
        "card": {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123"}
    }
    
    # Authorize Payment
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify Payment
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_shipping_request_success():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    shipping_payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"street": "123 Main St", "city": "Anytown", "country": "USA", "number": "123", "postcode": "12345"}
    }
    
    # Create Shipment
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify Shipment
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
