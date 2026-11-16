import pytest
import requests
import uuid
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

def generate_user():
    username = f"user_{uuid.uuid4().hex[:8]}"
    return {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

# --- Tests ---

def test_user_register_and_login():
    user = generate_user()
    
    # POST to register
    resp = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # GET to verify creation
    resp_get = requests.get(get_url("user", f"/customers/{user['username']}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["username"] == user["username"]

    # GET to login (Authentication)
    resp_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(user["username"], user["password"]), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

def test_user_register_conflict_negative():
    user = generate_user()
    
    # Setup: Create user
    resp = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify state
    resp_get = requests.get(get_url("user", f"/customers/{user['username']}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Action: Register again with the same user
    resp_conflict = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

def test_carts_cumulative_addition_and_patch():
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Get a real item from catalogue
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]
    price = items[0]["price"]

    # POST item (quantity 1)
    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    resp1 = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    # GET to verify
    get1 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get1.status_code == 200, f"Expected 200, got {get1.status_code}: {get1.text}"
    assert get1.json()["quantity"] == 1

    # POST item again (quantity 2) -> Cumulative state should be 3
    cart_item["quantity"] = 2
    resp2 = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp2.status_code == 201, f"Expected 201, got {resp2.status_code}: {resp2.text}"

    # GET to verify cumulative state
    get2 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get2.status_code == 200, f"Expected 200, got {get2.status_code}: {get2.text}"
    assert get2.json()["quantity"] == 3

    # PATCH item to replace quantity
    cart_item["quantity"] = 5
    resp3 = requests.patch(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp3.status_code == 202, f"Expected 202, got {resp3.status_code}: {resp3.text}"

    # GET to verify replaced state
    get3 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get3.status_code == 200, f"Expected 200, got {get3.status_code}: {get3.text}"
    assert get3.json()["quantity"] == 5

    # DELETE item
    resp4 = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp4.status_code == 202, f"Expected 202, got {resp4.status_code}: {resp4.text}"

    # GET to verify deletion
    get4 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get4.status_code == 404, f"Expected 404, got {get4.status_code}: {get4.text}"

def test_orders_end_to_end_positive():
    user = generate_user()
    username = user["username"]

    # 1. Register User
    resp_user = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    requests.get(get_url("user", f"/customers/{username}"), timeout=10)

    # 2. Add Address
    addr_data = {"street": "123 Main", "city": "City", "number": "12", "country": "UK", "postcode": "12345", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]
    
    get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr.status_code == 200, f"Expected 200, got {get_addr.status_code}: {get_addr.text}"

    # 3. Add Card
    card_data = {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]
    
    get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card.status_code == 200, f"Expected 200, got {get_card.status_code}: {get_card.text}"

    # 4. Add Item to Cart (ensure amount <= 100 for positive test)
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]
    
    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    
    get_cart = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert get_cart.status_code == 200, f"Expected 200, got {get_cart.status_code}: {get_cart.text}"

    # 5. Place Order
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json()["id"]

    # 6. Verify Order
    get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order.status_code == 200, f"Expected 200, got {get_order.status_code}: {get_order.text}"
    order_data = get_order.json()
    assert order_data["id"] == order_id
    assert "payment" in order_data

def test_orders_payment_declined_negative():
    user = generate_user()
    username = user["username"]

    # Setup: Register User, Add Address, Add Card
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    requests.get(get_url("user", f"/customers/{username}"), timeout=10)

    addr_data = {"street": "123 Main", "city": "City", "number": "12", "country": "UK", "postcode": "12345", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10).json()["id"]
    requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)

    card_data = {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_data, timeout=10).json()["id"]
    requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)

    # Setup: Add Item to Cart (ensure amount > 100 for negative test)
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]
    
    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": 105.0}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)

    # Action: Place Order -> Should fail with 406 Not Acceptable due to payment decline
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

def test_payment_and_shipping_direct_endpoints():
    # Setup: Create a real order to get a valid orderId
    user = generate_user()
    username = user["username"]
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    
    addr_data = {"street": "1", "city": "C", "number": "1", "country": "U", "postcode": "1", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10).json()["id"]
    
    card_data = {"longNum": "1234", "expires": "12/25", "ccv": "123", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_data, timeout=10).json()["id"]
    
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]
    
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)
    
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_id = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10).json()["id"]

    # Action: Test Payment POST directly
    payment_req = {
        "address": {"city": "C", "country": "U", "number": "1", "postcode": "1", "street": "1"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    
    get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay.status_code == 200, f"Expected 200, got {get_pay.status_code}: {get_pay.text}"
    assert len(get_pay.json()) >= 1

    # Action: Test Shipping POST directly
    shipping_req = {
        "address": {"city": "C", "country": "U", "number": "1", "postcode": "1", "street": "1"},
        "itemCount": 1,
        "orderId": order_id
    }
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    
    get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_ship.status_code == 200, f"Expected 200, got {get_ship.status_code}: {get_ship.text}"
    assert get_ship.json()["orderId"] == order_id
