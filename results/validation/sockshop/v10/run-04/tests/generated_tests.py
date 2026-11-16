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

def test_user_registration_and_profile_lifecycle():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "SecurePass123!"
    email = f"{username}@example.com"
    
    # 1. Register User
    reg_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "John",
        "lastName": "Doe"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=reg_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    
    # Negative: Register existing user
    resp_reg_conflict = requests.post(get_url("user", "/register"), json=reg_payload, timeout=10)
    assert resp_reg_conflict.status_code == 409, f"Expected 409, got {resp_reg_conflict.status_code}: {resp_reg_conflict.text}"
    
    # 2. Verify Registration via Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    
    # Negative: Bad Login
    resp_bad_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"
    
    # 3. Add Address
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "221B",
        "postcode": "NW1 6XE",
        "street": "Baker Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None, "Expected address ID in response"
    
    # Verify Address Creation
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addr_data = resp_get_addr.json()
    assert addr_data.get("city") == addr_payload["city"]
    assert addr_data.get("street") == addr_payload["street"]
    
    # 4. Add Card
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
    
    # Verify Card Creation
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    card_data = resp_get_card.json()
    assert card_data.get("expires") == card_payload["expires"]
    assert card_data.get("longNum").endswith("3456"), "Expected masked card number ending in 3456"

def test_carts_and_catalogue_lifecycle():
    # 1. Fetch Catalogue to get a real item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    sock = items[0]
    sock_id = sock["id"]
    sock_price = sock["price"]
    
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    
    # 2. Add Item to Cart
    item_payload = {
        "itemId": sock_id,
        "quantity": 1,
        "unitPrice": sock_price
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    
    # Verify Item Added
    resp_get_items = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_items.status_code == 200, f"Expected 200, got {resp_get_items.status_code}: {resp_get_items.text}"
    cart_items = resp_get_items.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == sock_id
    assert cart_items[0]["quantity"] == 1
    
    # 3. Update Item Quantity
    update_payload = {
        "itemId": sock_id,
        "quantity": 5,
        "unitPrice": sock_price
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"
    
    # Verify Quantity Updated
    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5
    
    # 4. Delete Item from Cart
    resp_del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"
    
    # Verify Item Deleted (Negative Test)
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"
    
    # 5. Delete Cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

def test_orders_e2e_success():
    # 1. Setup User, Address, and Card
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]
    
    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]
    
    # 2. Get Catalogue Item
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = cat_resp.json()
    # Find a sock to ensure total amount <= 100 for successful payment
    sock = next((s for s in socks if s["price"] <= 50.0), socks[0])
    
    # 3. Add Item to Cart
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)
    
    # 4. Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data["id"]
    assert order_data["payment"]["authorised"] is True, "Expected payment to be authorised"
    
    # 5. Verify Order Creation
    get_order_resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    assert get_order_resp.json()["id"] == order_id
    
    # 6. Verify Payment Authorization Record
    pay_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    pay_data = pay_resp.json()
    assert len(pay_data) > 0, "Expected at least one payment authorization record"
    assert pay_data[0]["authorised"] is True
    assert pay_data[0]["orderId"] == order_id
    
    # 7. Verify Shipment Record
    ship_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    assert ship_resp.json()["orderId"] == order_id
    assert "carrier" in ship_resp.json()

def test_orders_e2e_payment_failure():
    # 1. Setup User, Address, and Card
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]
    
    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]
    
    # 2. Get Catalogue Item
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    sock = cat_resp.json()[0]
    
    # 3. Add Item to Cart with quantity that forces total > 100
    high_qty = int(105 / sock["price"]) + 1
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": high_qty, "unitPrice": sock["price"]}, timeout=10)
    
    # 4. Place Order (Should fail payment authorization)
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406 for unauthorized payment, got {order_resp.status_code}: {order_resp.text}"
