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
    
    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_data = resp.json()
    assert user_data.get("username") == username
    assert user_data.get("firstName") == "John"
    assert user_data.get("lastName") == "Doe"
    assert user_data.get("email") == email
    
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrong"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
    
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_user_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}, timeout=10)
    
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    
    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_data = resp.json()
    assert addr_data.get("city") == "London"
    assert addr_data.get("country") == "UK"
    assert addr_data.get("number") == "10"
    assert addr_data.get("postcode") == "SW1A 1AA"
    assert addr_data.get("street") == "Downing St"
    
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_data = resp.json()
    assert card_data.get("expires") == "12/25"
    assert card_data.get("longNum").endswith("3456")
    
    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses)
    
    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

def test_catalogue_functionality():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    
    item_id = items[0]["id"]
    
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == item_id
    
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_item_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

def test_catalogue_image_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/images/non_existent_image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_functionality():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]
    
    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    item_data = resp.json()
    assert item_data["itemId"] == item_id
    assert item_data["quantity"] == 2
    assert item_data["unitPrice"] == unit_price
    
    payload["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5
    
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
    
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

def test_carts_merge_not_found():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=invalid_session"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_orders_end_to_end():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}, timeout=10)
    
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json().get("id")
    
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json().get("id")
    
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    item = next((i for i in items if i["price"] <= 50), items[0])
    
    cart_payload = {"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_data = resp.json()
    order_id = order_data.get("id")
    
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order.get("id") == order_id
    assert "payment" in fetched_order
    assert "shipment" in fetched_order
    
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_orders_payment_declined():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}, timeout=10)
    
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json().get("id")
    
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json().get("id")
    
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]
    
    cart_payload = {"itemId": item["id"], "quantity": 1000, "unitPrice": item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

def test_orders_not_found():
    resp = requests.get(get_url("orders", "/orders/non_existent_order_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_payment_and_shipping_directly():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}, timeout=10)
    
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json().get("id")
    
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json().get("id")
    
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = next((i for i in resp.json() if i["price"] <= 50), resp.json()[0])
    
    cart_payload = {"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    order_id = resp.json().get("id")
    
    payment_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St"},
        "amount": 50.00,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payment_data = resp.json()[0]
    assert payment_data.get("orderId") == order_id
    assert payment_data.get("authorised") is True
    
    shipping_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St"},
        "itemCount": 1,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipping_data = resp.json()
    assert shipping_data.get("orderId") == order_id
    assert shipping_data.get("carrier") is not None
