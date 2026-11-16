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

def test_user_registration_and_conflict():
    username = f"user_{generate_random_string()}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    
    # Register user
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify user creation
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    
    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    
    # Register same user again to trigger 409
    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

def test_carts_cumulative_state():
    username = f"cartuser_{generate_random_string()}"
    
    # Get a product from catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]
    
    # Add item to cart
    cart_item = {
        "itemId": item_id,
        "unitPrice": item.get("price", 10.0),
        "quantity": 1
    }
    resp_add1 = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp_add1.status_code == 201, f"Expected 201, got {resp_add1.status_code}: {resp_add1.text}"
    
    # Verify quantity is 1
    resp_get1 = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    cart_items = resp_get1.json()
    assert len(cart_items) == 1
    assert cart_items[0]["quantity"] == 1
    
    # Add same item again
    resp_add2 = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp_add2.status_code == 201, f"Expected 201, got {resp_add2.status_code}: {resp_add2.text}"
    
    # Verify quantity is 2 (cumulative state)
    resp_get2 = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    cart_items2 = resp_get2.json()
    assert len(cart_items2) == 1
    assert cart_items2[0]["quantity"] == 2
    
    # Delete cart
    resp_del = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"
    
    # Verify cart is empty
    resp_get3 = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get3.status_code == 200, f"Expected 200, got {resp_get3.status_code}: {resp_get3.text}"
    assert len(resp_get3.json()) == 0

def test_orders_successful_workflow():
    username = f"orderuser_{generate_random_string()}"
    password = "password123"
    
    # Register user
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": password}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    
    # Verify user
    resp_user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_user_get.status_code == 200, f"Expected 200, got {resp_user_get.status_code}: {resp_user_get.text}"
    
    # Add address
    address_payload = {
        "userID": username,
        "number": "123",
        "street": "Main St",
        "city": "Springfield",
        "postcode": "12345",
        "country": "USA"
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json().get("id")
    
    # Verify address
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert len(resp_addr_get.json().get("_embedded", {}).get("address", [])) > 0
    
    # Add card
    card_payload = {
        "userID": username,
        "longNum": "1234567812345678",
        "expires": "12/25",
        "ccv": "123"
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    
    # Verify card
    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    assert len(resp_card_get.json().get("_embedded", {}).get("card", [])) > 0
    
    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item = resp_cat.json()[0]
    
    # Add item to cart (ensure total <= 100 for successful payment)
    cart_item = {
        "itemId": item["id"],
        "unitPrice": 10.0,
        "quantity": 1
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    
    # Verify cart
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    assert len(resp_cart_get.json()) > 0
    
    # Place order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")
    
    # Verify order
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    order_get_data = resp_order_get.json()
    assert order_get_data["id"] == order_id
    assert order_get_data.get("payment", {}).get("authorised") is True
    assert "shipment" in order_get_data

def test_orders_payment_declined():
    username = f"failuser_{generate_random_string()}"
    password = "password123"
    
    # Register user
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": password}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    
    # Verify user
    resp_user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_user_get.status_code == 200, f"Expected 200, got {resp_user_get.status_code}: {resp_user_get.text}"
    
    # Add address
    address_payload = {
        "userID": username,
        "number": "456",
        "street": "High St",
        "city": "Metropolis",
        "postcode": "54321",
        "country": "USA"
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json().get("id")
    
    # Verify address
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    
    # Add card
    card_payload = {
        "userID": username,
        "longNum": "8765432187654321",
        "expires": "11/26",
        "ccv": "321"
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    
    # Verify card
    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    
    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item = resp_cat.json()[0]
    
    # Add item to cart with high price to exceed 100.00
    cart_item = {
        "itemId": item["id"],
        "unitPrice": 150.0,
        "quantity": 1
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    
    # Verify cart
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    
    # Place order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    # Expect 406 Not Acceptable due to payment failure
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
