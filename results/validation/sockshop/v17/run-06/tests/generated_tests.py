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

def test_user_register_and_duplicate_409():
    username = f"user_{generate_random_string()}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    
    # Register
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify by login
    login_resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    
    # Duplicate register
    resp_dup = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

def test_user_add_address_and_card():
    username = f"user_{generate_random_string()}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    
    login_resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    
    # Add address
    address_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    assert addr_id is not None, "Expected address id in response"
    
    # Verify address
    get_addr_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"
    addresses = get_addr_resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses), "Created address not found in customer addresses"
    
    # Add card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    assert card_id is not None, "Expected card id in response"
    
    # Verify card
    get_card_resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"
    cards = get_card_resp.json().get("_embedded", {}).get("card", [])
    created_card = next((c for c in cards if c.get("id") == card_id), None)
    assert created_card is not None, "Created card not found in customer cards"
    assert "1234567890123456" not in created_card.get("longNum", ""), "Raw card number should not be echoed"

def test_catalogue_list_and_get():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "Expected at least one item in catalogue"
    
    item_id = items[0]["id"]
    item_resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"
    assert item_resp.json()["id"] == item_id

def test_carts_add_item_cumulative():
    customer_id = f"cust_{generate_random_string()}"
    
    # Get an item from catalogue
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item = cat_resp.json()[0]
    item_id = item["id"]
    unit_price = item["price"]
    
    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
    
    # Add item first time
    add1_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add1_resp.status_code == 201, f"Expected 201, got {add1_resp.status_code}: {add1_resp.text}"
    
    # Verify quantity is 1
    get1_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get1_resp.status_code == 200, f"Expected 200, got {get1_resp.status_code}: {get1_resp.text}"
    items = get1_resp.json()
    assert len(items) == 1
    assert items[0]["quantity"] == 1
    
    # Add item second time
    add2_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add2_resp.status_code == 201, f"Expected 201, got {add2_resp.status_code}: {add2_resp.text}"
    
    # Verify quantity is 2 (cumulative state)
    get2_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get2_resp.status_code == 200, f"Expected 200, got {get2_resp.status_code}: {get2_resp.text}"
    items = get2_resp.json()
    assert len(items) == 1
    assert items[0]["quantity"] == 2

def test_carts_delete_item():
    customer_id = f"cust_{generate_random_string()}"
    item_id = "test_item_123"
    
    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 10.0
    }
    
    # Add item
    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"
    
    get_add_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_add_resp.status_code == 200, f"Expected 200, got {get_add_resp.status_code}: {get_add_resp.text}"
    assert len(get_add_resp.json()) == 1
    
    # Delete item
    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"
    
    # Verify item is removed
    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert len(items) == 0

def test_orders_create_success():
    # 1. Register User
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Order",
        "lastName": "Tester"
    }
    reg_resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    
    login_resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, "password"), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    
    # 2. Add Address
    addr_payload = {
        "city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street", "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]
    
    get_addr_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"
    assert any(a.get("id") == addr_id for a in get_addr_resp.json().get("_embedded", {}).get("address", []))
    
    # 3. Add Card
    card_payload = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]
    
    get_card_resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"
    assert any(c.get("id") == card_id for c in get_card_resp.json().get("_embedded", {}).get("card", []))
    
    # 4. Add Item to Cart
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    
    item_payload = {
        "itemId": item["id"],
        "quantity": 1,
        "unitPrice": 10.0
    }
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"
    
    get_cart_resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert get_cart_resp.status_code == 200, f"Expected 200, got {get_cart_resp.status_code}: {get_cart_resp.text}"
    assert any(i.get("itemId") == item["id"] for i in get_cart_resp.json())
    
    # 5. Create Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_id = order_resp.json().get("id")
    
    # 6. Verify Order
    get_order_resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    assert get_order_resp.json()["id"] == order_id

def test_orders_create_payment_declined_406():
    # 1. Register User
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Order",
        "lastName": "Tester"
    }
    reg_resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    
    login_resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, "password"), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
    
    # 2. Add Address
    addr_payload = {
        "city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street", "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]
    
    get_addr_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"
    assert any(a.get("id") == addr_id for a in get_addr_resp.json().get("_embedded", {}).get("address", []))
    
    # 3. Add Card
    card_payload = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]
    
    get_card_resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"
    assert any(c.get("id") == card_id for c in get_card_resp.json().get("_embedded", {}).get("card", []))
    
    # 4. Add Item to Cart (ensure total > 100 to decline payment)
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    
    item_payload = {
        "itemId": item["id"],
        "quantity": 10,
        "unitPrice": 20.0 # Total = 200.0 > 100.0 -> declined
    }
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"
    
    get_cart_resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert get_cart_resp.status_code == 200, f"Expected 200, got {get_cart_resp.status_code}: {get_cart_resp.text}"
    assert any(i.get("itemId") == item["id"] for i in get_cart_resp.json())
    
    # 5. Create Order - Expect 406
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"
