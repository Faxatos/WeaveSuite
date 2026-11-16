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

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# --- Tests ---

def test_user_registration_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    email = f"{username}@example.com"
    
    reg_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=reg_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    
    resp_dup = requests.post(get_url("user", "/register"), json=reg_payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"
    
    resp_bad_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

def test_user_add_address_and_card():
    username = f"user_{generate_random_string()}"
    password = "password123"
    
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": f"{username}@example.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_reg_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_reg_get.status_code == 200, f"Expected 200, got {resp_reg_get.status_code}: {resp_reg_get.text}"
    
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Test Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None, "Expected address ID in response"
    
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert resp_addr_get.json().get("city") == "London"
    
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None, "Expected card ID in response"
    
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    assert "password" not in resp_card_get.text.lower()

def test_catalogue_list_and_get():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert isinstance(items, list)
    
    if items:
        item_id = items[0]["id"]
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json()["id"] == item_id
        
        resp_not_found = requests.get(get_url("catalogue", "/catalogue/nonexistent-id-123"), timeout=10)
        assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

def test_cart_add_and_delete():
    customer_id = f"cust_{generate_random_string()}"
    
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    
    resp_item_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_item_get.status_code == 200, f"Expected 200, got {resp_item_get.status_code}: {resp_item_get.text}"
    assert resp_item_get.json().get("itemId") == item_id
    
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"
    
    resp_get_after = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    assert len(resp_get_after.json()) == 0

def test_end_to_end_order_placement():
    username = f"user_{generate_random_string()}"
    password = "password123"
    
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": f"{username}@example.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_reg_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_reg_get.status_code == 200, f"Expected 200, got {resp_reg_get.status_code}: {resp_reg_get.text}"
    
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Test Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 15.0}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id is not None
    
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id

def test_payment_authorization():
    order_id = str(uuid.uuid4())
    
    payment_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Test Street"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth_data = resp_pay.json()
    assert auth_data.get("authorised") is True
    
    resp_pay_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay_get.status_code == 200, f"Expected 200, got {resp_pay_get.status_code}: {resp_pay_get.text}"
    auths = resp_pay_get.json()
    assert isinstance(auths, list)
    assert len(auths) > 0
    assert auths[0].get("orderId") == order_id

def test_shipping_request():
    order_id = str(uuid.uuid4())
    
    shipping_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Test Street"},
        "itemCount": 2,
        "orderId": order_id
    }
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data.get("orderId") == order_id
    
    resp_ship_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship_get.status_code == 200, f"Expected 200, got {resp_ship_get.status_code}: {resp_ship_get.text}"
    assert resp_ship_get.json().get("orderId") == order_id
