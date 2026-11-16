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

def test_user_register_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer = resp_get.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == "Test"
    assert customer.get("lastName") == "User"
    assert customer.get("email") == f"{username}@example.com"
    assert "password" not in customer

def test_user_register_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

def test_user_login_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_user_login_failure():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpassword"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

def test_user_add_and_get_address():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    address_data = {
        "street": "123 Main St",
        "number": "42",
        "country": "USA",
        "city": "Anytown",
        "postcode": "12345",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None
    
    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    addr = resp_get.json()
    assert addr.get("street") == "123 Main St"
    assert addr.get("number") == "42"
    assert addr.get("country") == "USA"
    assert addr.get("city") == "Anytown"
    assert addr.get("postcode") == "12345"
    assert addr.get("id") == address_id

def test_user_add_and_get_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    card_data = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None
    
    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    card = resp_get.json()
    assert card.get("expires") == "12/25"
    assert card.get("ccv") == "123"
    assert card.get("id") == card_id
    assert card.get("longNum") == "************3456"

def test_user_customer_addresses_and_cards():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    addr_resp = requests.post(get_url("user", "/addresses"), json={"street": "S", "number": "1", "country": "C", "city": "C", "postcode": "1", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")
    
    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")
    
    resp_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addresses = resp_addr.json().get("_embedded", {}).get("address", [])
    assert len(addresses) > 0
    assert any(a.get("id") == address_id for a in addresses)
    
    resp_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    cards = resp_card.json().get("_embedded", {}).get("card", [])
    assert len(cards) > 0
    assert any(c.get("id") == card_id for c in cards)

def test_user_delete_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    addr_resp = requests.post(get_url("user", "/addresses"), json={"street": "S", "number": "1", "country": "C", "city": "C", "postcode": "1", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")
    
    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")
    
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"
    
    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"
    
    resp_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    addresses = resp_addr.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses)
    
    resp_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    cards = resp_card.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True
    
    resp_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_again.status_code == 200, f"Expected 200, got {resp_again.status_code}: {resp_again.text}"
    assert resp_again.json().get("status") is False

def test_user_get_customers():
    resp = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_carts_add_and_get_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_data = {
        "itemId": "item_123",
        "quantity": 2,
        "unitPrice": 15.5
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) == 1
    assert items[0]["itemId"] == "item_123"
    assert items[0]["quantity"] == 2
    assert items[0]["unitPrice"] == 15.5

def test_carts_update_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_data = {
        "itemId": "item_123",
        "quantity": 2,
        "unitPrice": 15.5
    }
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    
    item_data["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/item_123"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 5

def test_carts_delete_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_data = {
        "itemId": "item_123",
        "quantity": 2,
        "unitPrice": 15.5
    }
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/item_123"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/item_123"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

def test_carts_delete_cart():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": "item_1", "quantity": 1, "unitPrice": 10.0}, timeout=10)
    
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0

def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": "item_1", "quantity": 1, "unitPrice": 10.0}, timeout=10)
    
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) == 1
    assert items[0]["itemId"] == "item_1"

def test_carts_merge_not_found():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_async_add_and_get_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_data = {
        "itemId": "item_123",
        "quantity": 2,
        "unitPrice": 15.5
    }
    resp = requests.post(get_url("carts", f"/carts-async/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts-async/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) == 1
    assert items[0]["itemId"] == "item_123"

def test_catalogue_get_items():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)
    if len(socks) > 0:
        sock_id = socks[0]["id"]
        resp_get = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
        assert resp_get.json()["id"] == sock_id

def test_catalogue_get_invalid_item():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_id_12345"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_catalogue_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()
    assert isinstance(resp.json()["size"], int)

def test_catalogue_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()
    assert isinstance(resp.json()["tags"], list)

def test_catalogue_get_image():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    if len(socks) > 0 and "imageUrl" in socks[0] and len(socks[0]["imageUrl"]) > 0:
        image_url = socks[0]["imageUrl"][0]
        image_name = image_url.split("/")[-1]
        resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

def test_catalogue_get_image_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/images/invalid_image_123.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_orders_create_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "A", "lastName": "B", "email": "a@b.com"}, timeout=10)
    
    addr_resp = requests.post(get_url("user", "/addresses"), json={"street": "S", "number": "1", "country": "C", "city": "C", "postcode": "1", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")
    
    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")
    
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = cat_resp.json()
    sock = socks[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)
    
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order["customer"]["username"] == username
    
    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == order_id
    
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert len(orders) > 0
    assert orders[0]["id"] == order_id

def test_orders_create_missing_fields():
    username = f"user_{uuid.uuid4().hex[:8]}"
    order_req = {
        "customer": f"/customers/{username}"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

def test_orders_create_invalid_composite_id():
    username = f"user_{uuid.uuid4().hex[:8]}"
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_id",
        "card": f"/cards/invalid_id",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_orders_create_payment_declined():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "A", "lastName": "B", "email": "a@b.com"}, timeout=10)
    
    addr_resp = requests.post(get_url("user", "/addresses"), json={"street": "S", "number": "1", "country": "C", "city": "C", "postcode": "1", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")
    
    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")
    
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = cat_resp.json()
    sock = socks[0]
    
    quantity = int(105 / sock["price"]) + 1
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": quantity, "unitPrice": sock["price"]}, timeout=10)
    
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

def test_orders_create_deleted_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "A", "lastName": "B", "email": "a@b.com"}, timeout=10)
    
    addr_resp = requests.post(get_url("user", "/addresses"), json={"street": "S", "number": "1", "country": "C", "city": "C", "postcode": "1", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")
    
    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")
    
    requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = cat_resp.json()
    sock = socks[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)
    
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    assert not order.get("address") or len(order.get("address")) == 0
    assert not order.get("card") or len(order.get("card")) == 0

def test_orders_get_not_found():
    resp = requests.get(get_url("orders", "/orders/invalid_order_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_payments_authorize_and_get():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "Test", "lastName": "User"},
        "address": {"street": "123 Main", "number": "1", "city": "City", "postcode": "123", "country": "USA"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id
    
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["orderId"] == order_id

def test_payments_authorize_multiple():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "Test", "lastName": "User"},
        "address": {"street": "123 Main", "number": "1", "city": "City", "postcode": "123", "country": "USA"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }
    requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 2

def test_payments_authorize_declined_amount():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "Test", "lastName": "User"},
        "address": {"street": "123 Main", "number": "1", "city": "City", "postcode": "123", "country": "USA"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is False
    
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is False

def test_shipping_ship_and_get():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    shipping_req = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"street": "123 Main", "number": "1", "city": "City", "postcode": "123", "country": "USA"}
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
