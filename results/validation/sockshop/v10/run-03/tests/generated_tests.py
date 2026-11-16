import pytest
import requests
import uuid
import random
import string
from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth

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
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# --- Tests ---

def test_user_registration_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    user_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"
    
    login_resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

def test_user_register_duplicate():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "A",
        "lastName": "B"
    }
    
    resp1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"
    
    user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert user_get.status_code == 200, f"Expected 200, got {user_get.status_code}: {user_get.text}"
    
    resp2 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

def test_user_add_address_and_card():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "A",
        "lastName": "B"
    }
    reg_resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    
    user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert user_get.status_code == 200, f"Expected 200, got {user_get.status_code}: {user_get.text}"
    
    address_payload = {
        "city": "New York",
        "country": "USA",
        "number": "123",
        "postcode": "10001",
        "street": "5th Ave",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    
    get_addr_resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"
    addr_data = get_addr_resp.json()
    assert addr_data.get("city") == address_payload["city"]
    assert addr_data.get("country") == address_payload["country"]
    assert addr_data.get("number") == address_payload["number"]
    assert addr_data.get("postcode") == address_payload["postcode"]
    assert addr_data.get("street") == address_payload["street"]
    
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    
    get_card_resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"
    card_data = get_card_resp.json()
    assert card_data.get("ccv") == card_payload["ccv"]
    assert card_data.get("expires") == card_payload["expires"]

def test_catalogue_browsing():
    tags_resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"
    tags = tags_resp.json().get("tags", [])
    if not tags:
        pytest.skip("No tags found in catalogue")
    
    tag = tags[0]
    
    cat_resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    if not items:
        pytest.skip("No items found for tag")
        
    item_id = items[0].get("id")
    
    item_resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"
    item_data = item_resp.json()
    assert item_data.get("id") == item_id

def test_cart_lifecycle():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"
    
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.50
    }
    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"
    add_data = add_resp.json()
    assert add_data.get("itemId") == item_payload["itemId"]
    assert add_data.get("quantity") == item_payload["quantity"]
    assert add_data.get("unitPrice") == item_payload["unitPrice"]
    
    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert get_data.get("itemId") == item_payload["itemId"]
    assert get_data.get("quantity") == item_payload["quantity"]
    assert get_data.get("unitPrice") == item_payload["unitPrice"]
    
    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 15.50
    }
    patch_resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"
    
    get_updated_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_updated_resp.status_code == 200, f"Expected 200, got {get_updated_resp.status_code}: {get_updated_resp.text}"
    assert get_updated_resp.json().get("quantity") == update_payload["quantity"]
    assert get_updated_resp.json().get("unitPrice") == update_payload["unitPrice"]
    
    del_item_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_item_resp.status_code == 202, f"Expected 202, got {del_item_resp.status_code}: {del_item_resp.text}"
    
    get_deleted_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_deleted_resp.status_code == 404, f"Expected 404, got {get_deleted_resp.status_code}: {get_deleted_resp.text}"
    
    del_cart_resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert del_cart_resp.status_code == 202, f"Expected 202, got {del_cart_resp.status_code}: {del_cart_resp.text}"
    
    get_items_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_items_resp.status_code == 200, f"Expected 200, got {get_items_resp.status_code}: {get_items_resp.text}"
    assert len(get_items_resp.json()) == 0

def test_order_placement_success():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "A",
        "lastName": "B"
    }
    reg_resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert user_get.status_code == 200, f"Expected 200, got {user_get.status_code}: {user_get.text}"
    
    address_payload = {
        "city": "New York",
        "country": "USA",
        "number": "123",
        "postcode": "10001",
        "street": "5th Ave",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"
    
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"
    
    item_id = f"item_{generate_random_string()}"
    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 50.00
    }
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"
    item_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert item_get.status_code == 200, f"Expected 200, got {item_get.status_code}: {item_get.text}"
    
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data.get("id")
    assert order_id is not None
    
    get_order_resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    get_order_data = get_order_resp.json()
    assert get_order_data.get("id") == order_id
    assert get_order_data.get("payment", {}).get("authorised") is True
    assert "shipment" in get_order_data
    assert "trackingNumber" in get_order_data["shipment"]

def test_order_placement_payment_declined():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "A",
        "lastName": "B"
    }
    reg_resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert user_get.status_code == 200, f"Expected 200, got {user_get.status_code}: {user_get.text}"
    
    address_payload = {
        "city": "New York",
        "country": "USA",
        "number": "123",
        "postcode": "10001",
        "street": "5th Ave",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"
    
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"
    
    item_id = f"item_{generate_random_string()}"
    item_payload = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": 50.00
    }
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"
    item_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert item_get.status_code == 200, f"Expected 200, got {item_get.status_code}: {item_get.text}"
    
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

def test_payment_authorization():
    order_id = f"order_{generate_random_string()}"
    payment_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "W1",
            "street": "Baker St"
        },
        "amount": 99.99,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "Sherlock",
            "lastName": "Holmes"
        },
        "orderId": order_id
    }
    
    pay_resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    pay_data = pay_resp.json()
    assert pay_data.get("orderId") == payment_payload["orderId"]
    assert pay_data.get("authorised") is True
    
    get_pay_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay_resp.status_code == 200, f"Expected 200, got {get_pay_resp.status_code}: {get_pay_resp.text}"
    auths = get_pay_resp.json()
    assert len(auths) > 0
    assert auths[0].get("orderId") == order_id
    assert auths[0].get("authorised") is True

def test_shipping_creation():
    order_id = f"order_{generate_random_string()}"
    shipping_payload = {
        "address": {
            "city": "Paris",
            "country": "France",
            "number": "5",
            "postcode": "75001",
            "street": "Rue de Rivoli"
        },
        "itemCount": 3,
        "orderId": order_id
    }
    
    ship_resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    ship_data = ship_resp.json()
    assert ship_data.get("orderId") == shipping_payload["orderId"]
    assert "trackingNumber" in ship_data
    
    get_ship_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_ship_resp.status_code == 200, f"Expected 200, got {get_ship_resp.status_code}: {get_ship_resp.text}"
    get_ship_data = get_ship_resp.json()
    assert get_ship_data.get("orderId") == order_id
    assert get_ship_data.get("trackingNumber") == ship_data.get("trackingNumber")
