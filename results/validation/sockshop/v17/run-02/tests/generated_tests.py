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

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def setup_user():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"
    }, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_reg_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_reg_get.status_code == 200, f"Expected 200, got {resp_reg_get.status_code}: {resp_reg_get.text}"
    return username

def setup_order():
    username = setup_user()
    
    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "street": "123 Main", "number": "1", "country": "USA", "city": "City", "postcode": "12345", "userID": username
    }, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    
    resp_card = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item = resp_cat.json()[0]
    
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"], "quantity": 1, "unitPrice": 10.0
    }, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item['id']}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    
    resp_order = requests.post(get_url("orders", "/orders"), json={
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json()["id"]
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    
    return order_id

# --- Tests ---

def test_user_register_and_login():
    username = f"user_{random_string()}"
    password = "password123"
    
    reg_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=reg_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

def test_user_register_duplicate_failure():
    username = setup_user()
    
    reg_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_dup = requests.post(get_url("user", "/register"), json=reg_payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

def test_user_add_address_and_card():
    username = setup_user()
    
    addr_payload = {
        "street": "123 Main St",
        "number": "42",
        "country": "USA",
        "city": "Anytown",
        "postcode": "12345",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert resp_addr_get.json().get("street") == "123 Main St"
    
    card_payload = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    assert resp_card_get.json().get("expires") == "12/25"

def test_catalogue_list_and_get():
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    items = resp_list.json()
    assert len(items) > 0, "Catalogue is empty"
    
    item_id = items[0]["id"]
    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == item_id

def test_catalogue_get_not_found():
    invalid_id = f"invalid_{random_string()}"
    resp = requests.get(get_url("catalogue", f"/catalogue/{invalid_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_add_item_multiple_times():
    customer_id = setup_user()
    
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200
    item = resp_cat.json()[0]
    item_id = item["id"]
    price = item["price"]
    
    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": price
    }
    resp_add1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add1.status_code == 201, f"Expected 201, got {resp_add1.status_code}: {resp_add1.text}"
    
    resp_get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    assert resp_get1.json()["quantity"] == 1
    
    item_payload["quantity"] = 2
    resp_add2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add2.status_code == 201, f"Expected 201, got {resp_add2.status_code}: {resp_add2.text}"
    
    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["quantity"] == 3

def test_carts_delete_item():
    customer_id = setup_user()
    
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp_cat.json()[0]
    item_id = item["id"]
    
    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item["price"]
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"
    
    resp_get_after = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_after.status_code == 404, f"Expected 404, got {resp_get_after.status_code}: {resp_get_after.text}"

def test_orders_create_and_get():
    order_id = setup_order()
    assert order_id is not None

def test_orders_payment_declined():
    username = setup_user()
    
    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "street": "123 Main", "number": "1", "country": "USA", "city": "City", "postcode": "12345", "userID": username
    }, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    
    resp_card = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item = resp_cat.json()[0]
    
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"], "quantity": 100, "unitPrice": 50.0
    }, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item['id']}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    
    resp_order = requests.post(get_url("orders", "/orders"), json={
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

def test_payment_authorize_success():
    order_id = setup_order()
    
    payment_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"street": "Main", "number": "1", "country": "USA", "city": "City", "postcode": "12345"},
        "card": {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    }
    
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True
    
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) > 0
    assert any(a.get("orderId") == order_id for a in auths)

def test_shipping_create_and_get():
    order_id = setup_order()
    
    shipping_payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"street": "Main", "number": "1", "country": "USA", "city": "City", "postcode": "12345"}
    }
    
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id
    
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
