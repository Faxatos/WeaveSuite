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
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    
    # Register
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # Verify creation
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer = resp_get.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == "Test"
    assert customer.get("lastName") == "User"
    assert "password" not in customer
    
    # Conflict: Register same user
    resp_conflict = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"
    
    # Login success
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    
    # Login failure
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

def test_user_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    
    # Add Address
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1",
        "street": "Baker St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None
    
    # Verify Address
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_data = resp_addr_get.json()
    assert addr_data.get("city") == "London"
    assert addr_data.get("postcode") == "W1"
    
    # Add Card
    card_payload = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None
    
    # Verify Card
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data.get("expires") == "12/25"
    assert card_data.get("longNum").endswith("3456")
    assert "*" in card_data.get("longNum")
    
    # Delete Address
    resp_addr_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_del.status_code == 200, f"Expected 200, got {resp_addr_del.status_code}: {resp_addr_del.text}"
    
    # Delete Card
    resp_card_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_del.status_code == 200, f"Expected 200, got {resp_card_del.status_code}: {resp_card_del.text}"

def test_catalogue_retrieval():
    # Get tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags_data = resp_tags.json()
    assert "tags" in tags_data
    assert isinstance(tags_data["tags"], list)
    
    # Get catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    cat_data = resp_cat.json()
    assert isinstance(cat_data, list)
    if len(cat_data) > 0:
        item_id = cat_data[0]["id"]
        
        # Get specific item
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json()["id"] == item_id
        
    # Get non-existent item
    resp_404 = requests.get(get_url("catalogue", "/catalogue/nonexistent-id-123"), timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

def test_carts_management():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    
    # Add item to cart
    item_payload = {
        "itemId": "item_1",
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    
    # Verify item in cart
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) == 1
    assert items[0]["itemId"] == "item_1"
    assert items[0]["quantity"] == 2
    
    # Update item quantity
    update_payload = {
        "itemId": "item_1",
        "quantity": 5,
        "unitPrice": 10.5
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"
    
    # Verify updated quantity
    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/item_1"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5
    
    # Delete item
    resp_del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/item_1"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"
    
    # Verify item deleted
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/item_1"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"
    
    # Delete cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

def test_orders_end_to_end():
    # Setup User, Address, Card
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json()["id"]
    
    card_payload = {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json()["id"]
    
    # Add item to cart
    item_payload = {"itemId": "item_1", "quantity": 2, "unitPrice": 15.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    
    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data["id"]
    assert order_data["customer"]["username"] == username
    assert order_data["total"] == 30.0
    assert order_data["status"] in ["CREATED", "PAID", "SHIPPED"]
    
    # Verify Order
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json()["id"] == order_id
    
    # Verify Customer Orders
    resp_cust_orders = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_cust_orders.status_code == 200, f"Expected 200, got {resp_cust_orders.status_code}: {resp_cust_orders.text}"
    cust_orders = resp_cust_orders.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in cust_orders)

def test_orders_negative_scenarios():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json()["id"]
    
    card_payload = {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json()["id"]
    
    # Empty cart order (406)
    order_payload_empty = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order_empty = requests.post(get_url("orders", "/orders"), json=order_payload_empty, timeout=10)
    assert resp_order_empty.status_code == 406, f"Expected 406, got {resp_order_empty.status_code}: {resp_order_empty.text}"
    
    # Invalid address URI format (404)
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item_1", "quantity": 1, "unitPrice": 10.0}, timeout=10)
    
    order_payload_invalid_addr = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid-format",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order_invalid = requests.post(get_url("orders", "/orders"), json=order_payload_invalid_addr, timeout=10)
    assert resp_order_invalid.status_code == 404, f"Expected 404, got {resp_order_invalid.status_code}: {resp_order_invalid.text}"

def test_payment_authorization():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    
    payment_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }
    
    # Authorize payment
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    pay_data = resp_pay.json()
    assert pay_data["authorised"] is True
    assert pay_data["orderId"] == order_id
    
    # Verify payment recorded
    resp_pay_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay_get.status_code == 200, f"Expected 200, got {resp_pay_get.status_code}: {resp_pay_get.text}"
    auths = resp_pay_get.json()
    assert len(auths) >= 1
    assert auths[-1]["orderId"] == order_id
    assert auths[-1]["authorised"] is True
    
    # Negative: Amount > 100 should be declined
    payment_payload_declined = payment_payload.copy()
    payment_payload_declined["amount"] = 150.0
    resp_pay_declined = requests.post(get_url("payment-http", "/payments"), json=payment_payload_declined, timeout=10)
    assert resp_pay_declined.status_code == 200, f"Expected 200, got {resp_pay_declined.status_code}: {resp_pay_declined.text}"
    assert resp_pay_declined.json()["authorised"] is False

def test_shipping_creation():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    
    shipping_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St"},
        "itemCount": 3,
        "orderId": order_id
    }
    
    # Create shipment
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data["orderId"] == order_id
    assert "carrier" in ship_data
    assert "trackingNumber" in ship_data
    
    # Verify shipment
    resp_ship_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship_get.status_code == 200, f"Expected 200, got {resp_ship_get.status_code}: {resp_ship_get.text}"
    assert resp_ship_get.json()["orderId"] == order_id
    assert resp_ship_get.json()["trackingNumber"] == ship_data["trackingNumber"]
