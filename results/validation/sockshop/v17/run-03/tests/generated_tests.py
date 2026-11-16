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

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    resp_bad_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

def test_carts_cumulative_operations():
    customer_id = f"cust_{generate_random_string()}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]
    price = item.get("price", 10.0)

    cart_payload = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    add_resp1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_payload, timeout=10)
    assert add_resp1.status_code == 201, f"Expected 201, got {add_resp1.status_code}: {add_resp1.text}"

    get_resp1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp1.status_code == 200, f"Expected 200, got {get_resp1.status_code}: {get_resp1.text}"
    assert get_resp1.json()["quantity"] == 1, f"Expected quantity 1, got {get_resp1.json()}"

    add_resp2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_payload, timeout=10)
    assert add_resp2.status_code == 201, f"Expected 201, got {add_resp2.status_code}: {add_resp2.text}"

    get_resp2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    assert get_resp2.json()["quantity"] == 2, f"Expected quantity 2, got {get_resp2.json()}"

    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": price}
    patch_resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_resp3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp3.status_code == 200, f"Expected 200, got {get_resp3.status_code}: {get_resp3.text}"
    assert get_resp3.json()["quantity"] == 5, f"Expected quantity 5, got {get_resp3.json()}"

    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp4 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp4.status_code == 404, f"Expected 404, got {get_resp4.status_code}: {get_resp4.text}"

def test_orders_successful_checkout():
    username = f"user_{generate_random_string()}"

    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    reg_resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert user_get.status_code == 200, f"Expected 200, got {user_get.status_code}: {user_get.text}"

    addr_payload = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]

    addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item = cat_resp.json()[0]

    cart_payload = {"itemId": item["id"], "quantity": 1, "unitPrice": item.get("price", 10.0)}
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

    cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item['id']}"), timeout=10)
    assert cart_get.status_code == 200, f"Expected 200, got {cart_get.status_code}: {cart_get.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_id = order_resp.json()["id"]

    order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert order_get.status_code == 200, f"Expected 200, got {order_get.status_code}: {order_get.text}"
    assert order_get.json()["payment"]["authorised"] is True, "Payment should be authorised"

def test_orders_payment_declined():
    username = f"user_{generate_random_string()}"

    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    reg_resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert user_get.status_code == 200, f"Expected 200, got {user_get.status_code}: {user_get.text}"

    addr_payload = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]

    addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item = cat_resp.json()[0]

    cart_payload = {"itemId": item["id"], "quantity": 1000, "unitPrice": item.get("price", 10.0)}
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

    cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item['id']}"), timeout=10)
    assert cart_get.status_code == 200, f"Expected 200, got {cart_get.status_code}: {cart_get.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"
