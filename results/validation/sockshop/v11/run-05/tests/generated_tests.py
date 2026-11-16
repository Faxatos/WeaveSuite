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

def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex}"
    password = "password123"
    email = f"{username}@example.com"
    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

def test_user_register_duplicate():
    username = f"user_{uuid.uuid4().hex}"
    payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "F",
        "lastName": "L"
    }
    requests.post(get_url("user", "/register"), json=payload, timeout=10)
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

def test_user_login_unauthorized():
    resp = requests.get(get_url("user", "/login"), auth=("invalid", "invalid"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

def test_user_add_address():
    username = f"user_{uuid.uuid4().hex}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None
    
    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("city") == "London"
    assert data.get("country") == "UK"

def test_user_add_card():
    username = f"user_{uuid.uuid4().hex}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None
    
    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("ccv") == "123"
    assert data.get("expires") == "12/25"

def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

def test_user_delete_address():
    username = f"user_{uuid.uuid4().hex}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    payload = {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    address_id = resp.json().get("id")
    
    resp_del = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

def test_user_delete_card():
    username = f"user_{uuid.uuid4().hex}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    card_id = resp.json().get("id")
    
    resp_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

def test_catalogue_list_and_get():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if items:
        item_id = items[0]["id"]
        resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
        assert resp_get.json().get("id") == item_id

def test_catalogue_get_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_catalogue_get_image_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/images/invalid_image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_catalogue_get_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_carts_add_and_get_items():
    customer_id = f"cust_{uuid.uuid4().hex}"
    item_id = f"item_{uuid.uuid4().hex}"
    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.5
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("itemId") == item_id
    assert data.get("quantity") == 2
    assert data.get("unitPrice") == 15.5

def test_carts_patch_item():
    customer_id = f"cust_{uuid.uuid4().hex}"
    item_id = f"item_{uuid.uuid4().hex}"
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    
    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 10.0}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 5

def test_carts_delete_item():
    customer_id = f"cust_{uuid.uuid4().hex}"
    item_id = f"item_{uuid.uuid4().hex}"
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

def test_carts_delete_cart():
    customer_id = f"cust_{uuid.uuid4().hex}"
    payload = {"itemId": "item1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

def test_carts_get_item_not_found():
    customer_id = f"cust_{uuid.uuid4().hex}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/invalid_item"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_merge_not_found():
    customer_id = f"cust_{uuid.uuid4().hex}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=invalid_session"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_orders_create_and_get():
    username = f"user_{uuid.uuid4().hex}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    addr_payload = {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    address_id = resp_addr.json().get("id")
    
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")
    
    item_payload = {"itemId": "item1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")
    assert order_id is not None
    
    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("id") == order_id

def test_orders_payment_declined():
    username = f"user_{uuid.uuid4().hex}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    addr_payload = {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    address_id = resp_addr.json().get("id")
    
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")
    
    item_payload = {"itemId": "item1", "quantity": 1, "unitPrice": 150.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

def test_orders_get_not_found():
    resp = requests.get(get_url("orders", "/orders/invalid_order_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_orders_search_not_found():
    resp = requests.get(get_url("orders", "/orders/search/customerId?custId=invalid_cust"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_payment_authorize_success():
    order_id = f"order_{uuid.uuid4().hex}"
    payload = {
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True
    
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert isinstance(auths, list)
    assert len(auths) > 0
    assert auths[0].get("authorised") is True

def test_payment_authorize_decline():
    order_id = f"order_{uuid.uuid4().hex}"
    payload = {
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

def test_shipping_create_and_get():
    order_id = f"order_{uuid.uuid4().hex}"
    payload = {
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("orderId") == order_id
    assert "trackingNumber" in data
    
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
