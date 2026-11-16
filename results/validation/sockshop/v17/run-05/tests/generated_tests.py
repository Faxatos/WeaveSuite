import pytest
import requests
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
    
    # Register
    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify registration via GET /customers/{id}
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    
    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

def test_user_registration_duplicate_failure():
    username = f"user_{generate_random_string()}"
    password = "password123"
    
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Jane",
        "lastName": "Doe"
    }
    
    # First registration
    resp1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"
    
    # Verify
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    
    # Duplicate registration
    resp2 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

def test_carts_add_item_cumulative_state():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"
    
    # Add item first time
    item_payload_1 = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_1, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"
    
    # Verify state
    resp_get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    assert resp_get1.json().get("quantity") == 2, f"Expected quantity 2, got {resp_get1.json()}"
    
    # Add item second time (cumulative)
    item_payload_2 = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": 10.5
    }
    resp2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_2, timeout=10)
    assert resp2.status_code == 201, f"Expected 201, got {resp2.status_code}: {resp2.text}"
    
    # Verify cumulative state
    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 5, f"Expected quantity 5, got {resp_get2.json()}"
    
    # Cleanup
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"
    
    # Verify cleanup
    resp_get3 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get3.status_code == 200, f"Expected 200, got {resp_get3.status_code}: {resp_get3.text}"
    assert len(resp_get3.json()) == 0, f"Expected empty cart, got {resp_get3.json()}"

def test_orders_successful_placement():
    # 1. Register User
    username = f"user_{generate_random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"
    }, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    
    # 2. Add Address
    addr_payload = {
        "city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    
    # Verify Address
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    
    # 3. Add Card
    card_payload = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    
    # Verify Card
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    
    # 4. Add Item to Cart (Amount <= 100 for successful payment)
    item_payload = {"itemId": "item1", "quantity": 1, "unitPrice": 50.0}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    
    # Verify Cart
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    
    # 5. Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")
    assert order_id is not None, "Order ID should not be None"
    
    # Verify Order
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id

def test_orders_payment_declined_failure():
    # 1. Register User
    username = f"user_{generate_random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"
    }, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    
    # 2. Add Address
    addr_payload = {
        "city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    
    # 3. Add Card
    card_payload = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    
    # 4. Add Item to Cart (Amount > 100 for declined payment)
    item_payload = {"itemId": "item2", "quantity": 2, "unitPrice": 60.0} # Total 120.0
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    
    # Verify Cart
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    
    # 5. Place Order - Expect 406 Not Acceptable
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

def test_catalogue_list_and_get():
    # List catalogue
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    items = resp_list.json()
    
    if items:
        item_id = items[0].get("id")
        # Get specific item
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json().get("id") == item_id
        
        # Get image if available
        image_urls = resp_item.json().get("imageUrl", [])
        if image_urls:
            # Extract image name from URL
            image_path = image_urls[0]
            image_name = image_path.split("/")[-1]
            resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
            assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

def test_payment_http_authorization():
    order_id = f"order_{generate_random_string()}"
    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }
    
    # Authorize payment
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True
    
    # Verify payment authorization
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert isinstance(auths, list)
    assert len(auths) > 0
    assert auths[0].get("orderId") == order_id

def test_shipping_http_shipment():
    order_id = f"order_{generate_random_string()}"
    shipping_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    
    # Create shipment
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id
    
    # Verify shipment
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
