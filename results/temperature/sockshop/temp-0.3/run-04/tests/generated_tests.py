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

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# --- Tests ---

def test_payment_http_authorize_and_retrieve():
    order_id = str(uuid.uuid4())
    payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data["authorised"] is True
    assert auth_data["orderId"] == order_id
    
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 1
    assert auths[-1]["orderId"] == order_id
    assert auths[-1]["authorised"] is True

def test_payment_http_authorize_decline():
    order_id = str(uuid.uuid4())
    payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data["authorised"] is False
    assert auth_data["orderId"] == order_id
    
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 1
    assert auths[-1]["orderId"] == order_id
    assert auths[-1]["authorised"] is False

def test_shipping_http_ship_and_retrieve():
    order_id = str(uuid.uuid4())
    payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    ship_data = resp.json()
    assert ship_data["orderId"] == order_id
    assert "trackingNumber" in ship_data
    
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    ship_get = resp_get.json()
    assert ship_get["orderId"] == order_id
    assert ship_get["trackingNumber"] == ship_data["trackingNumber"]

def test_catalogue_list_and_get_item():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if items:
        item_id = items[0]["id"]
        resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
        item = resp_get.json()
        assert item["id"] == item_id
        
        resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
        assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
        assert "tags" in resp_tags.json()
        
        resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        assert "size" in resp_size.json()

def test_catalogue_not_found_404():
    resp = requests.get(get_url("catalogue", "/catalogue/nonexistent-id-123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_add_get_delete():
    customer_id = random_string()
    item_id = str(uuid.uuid4())
    payload = {"itemId": item_id, "quantity": 2, "unitPrice": 15.5}
    
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    added_item = resp.json()
    assert added_item["itemId"] == item_id
    assert added_item["quantity"] == 2
    
    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 15.5}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i["itemId"] == item_id and i["quantity"] == 5 for i in items)
    
    resp_get_single = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_single.status_code == 200, f"Expected 200, got {resp_get_single.status_code}: {resp_get_single.text}"
    assert resp_get_single.json()["itemId"] == item_id
    assert resp_get_single.json()["quantity"] == 5
    
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"
    
    resp_del2 = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del2.status_code == 202, f"Expected 202, got {resp_del2.status_code}: {resp_del2.text}"
    
    resp_get_single_after = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_single_after.status_code == 404, f"Expected 404, got {resp_get_single_after.status_code}: {resp_get_single_after.text}"
    
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"
    
    resp_del_cart2 = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart2.status_code == 202, f"Expected 202, got {resp_del_cart2.status_code}: {resp_del_cart2.text}"

def test_carts_item_not_found_404():
    resp = requests.get(get_url("carts", f"/carts/someuser/items/nonexistent-item"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_user_register_login_address_card():
    username = random_string()
    password = "password123"
    email = f"{username}@example.com"
    
    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    
    resp_reg_dup = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg_dup.status_code == 409, f"Expected 409, got {resp_reg_dup.status_code}: {resp_reg_dup.text}"
    
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"
    
    addr_payload = {
        "city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St", "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]
    
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json()["id"] == addr_id
    
    resp_get_addrs = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get_addrs.status_code == 200, f"Expected 200, got {resp_get_addrs.status_code}: {resp_get_addrs.text}"
    addrs = resp_get_addrs.json().get("_embedded", {}).get("address", [])
    assert any(a["id"] == addr_id for a in addrs)
    
    card_payload = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]
    
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert resp_get_card.json()["id"] == card_id
    
    resp_get_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get_cards.status_code == 200, f"Expected 200, got {resp_get_cards.status_code}: {resp_get_cards.text}"
    cards = resp_get_cards.json().get("_embedded", {}).get("card", [])
    assert any(c["id"] == card_id for c in cards)
    
    resp_del_cust = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_cust.status_code == 200, f"Expected 200, got {resp_del_cust.status_code}: {resp_del_cust.text}"
    assert resp_del_cust.json()["status"] is True
    
    resp_del_cust2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_cust2.status_code == 200, f"Expected 200, got {resp_del_cust2.status_code}: {resp_del_cust2.text}"
    assert resp_del_cust2.json()["status"] is False

def test_orders_create_and_search():
    username = random_string()
    password = "password123"
    
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": password, "email": f"{username}@example.com",
        "firstName": "Test", "lastName": "User"
    }, timeout=10)
    
    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St", "userID": username
    }, timeout=10)
    addr_id = resp_addr.json()["id"]
    
    resp_card = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username
    }, timeout=10)
    card_id = resp_card.json()["id"]
    
    item_id = str(uuid.uuid4())
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item_id, "quantity": 1, "unitPrice": 10.0
    }, timeout=10)
    
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    assert "id" in order
    assert order["customer"]["username"] == username
    
    order_id = order["id"]
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id
    
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    orders_list = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in orders_list)

def test_orders_missing_fields_406():
    order_payload = {
        "customer": "/customers/nonexistent"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "message" in resp_order.json()

def test_orders_not_found_404():
    resp = requests.get(get_url("orders", "/orders/nonexistent-order"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
