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

@pytest.fixture
def setup_order():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@example.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    
    resp_user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_user_get.status_code == 200, f"Expected 200, got {resp_user_get.status_code}: {resp_user_get.text}"
    
    resp_addr = requests.post(get_url("user", "/addresses"), json={"street": "123 Main St", "city": "Springfield", "country": "USA", "number": "12", "postcode": "12345", "userID": username}, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    
    resp_card = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]
    
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": unit_price}, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    
    order_id = resp_order.json().get("id")
    
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    
    return order_id

def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    email = f"{username}@example.com"
    
    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"
    
    resp_dup = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"
    
    resp_bad_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"
    
    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    
    resp_all = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_all.status_code == 200, f"Expected 200, got {resp_all.status_code}: {resp_all.text}"
    assert username not in resp_all.text, "User should be deleted"

def test_user_addresses_and_cards():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@example.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    
    resp_user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_user_get.status_code == 200, f"Expected 200, got {resp_user_get.status_code}: {resp_user_get.text}"
    
    addr_payload = {
        "street": "123 Main St",
        "city": "Springfield",
        "country": "USA",
        "number": "12",
        "postcode": "12345",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None
    
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    
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
    
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    
    resp_addr_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_del.status_code == 200, f"Expected 200, got {resp_addr_del.status_code}: {resp_addr_del.text}"
    
    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    embedded = resp_cust_addr.json().get("_embedded", {})
    addresses = embedded.get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses), "Address should be deleted"

def test_catalogue_functionality():
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    items = resp_list.json()
    assert isinstance(items, list)
    
    if len(items) > 0:
        item_id = items[0]["id"]
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json()["id"] == item_id
        
        image_urls = items[0].get("imageUrl", [])
        if len(image_urls) > 0:
            image_path = image_urls[0]
            image_name = image_path.split("/")[-1]
            resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
            assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"
            
    resp_not_found = requests.get(get_url("catalogue", "/catalogue/invalid_id_123"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"
    
    resp_img_bad = requests.get(get_url("catalogue", "/catalogue/images/nonexistent_image.jpg"), timeout=10)
    assert resp_img_bad.status_code == 404, f"Expected 404, got {resp_img_bad.status_code}: {resp_img_bad.text}"
    
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    
    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"

def test_carts_lifecycle():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    cat_items = resp_cat.json()
    assert len(cat_items) > 0
    item_id = cat_items[0]["id"]
    unit_price = cat_items[0]["price"]
    
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) > 0
    assert any(i["itemId"] == item_id for i in items)
    
    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": unit_price
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"
    
    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5
    
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"
    
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"
    
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"
    
    resp_get_cart = requests.get(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]
    
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp_add = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    
    resp_sess_get = requests.get(get_url("carts", f"/carts/{session_id}/items"), timeout=10)
    assert resp_sess_get.status_code == 200, f"Expected 200, got {resp_sess_get.status_code}: {resp_sess_get.text}"
    
    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"
    
    resp_cust_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_cust_get.status_code == 200, f"Expected 200, got {resp_cust_get.status_code}: {resp_cust_get.text}"
    items = resp_cust_get.json()
    assert len(items) > 0
    assert any(i["itemId"] == item_id for i in items)
    
    bad_session_id = f"sess_{uuid.uuid4().hex[:8]}"
    resp_bad_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={bad_session_id}"), timeout=10)
    assert resp_bad_merge.status_code == 404, f"Expected 404, got {resp_bad_merge.status_code}: {resp_bad_merge.text}"

def test_orders_create_and_retrieve():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@example.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    
    resp_user_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_user_get.status_code == 200, f"Expected 200, got {resp_user_get.status_code}: {resp_user_get.text}"
    
    addr_payload = {"street": "123 Main St", "city": "Springfield", "country": "USA", "number": "12", "postcode": "12345", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    
    card_payload = {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]
    
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id is not None
    
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id
    
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    
    bad_order_payload = {
        "customer": f"/invalid/{username}",
        "address": f"/invalid/{addr_id}",
        "card": f"/invalid/{card_id}",
        "items": f"/invalid/{username}/items"
    }
    resp_bad_order = requests.post(get_url("orders", "/orders"), json=bad_order_payload, timeout=10)
    assert resp_bad_order.status_code == 406, f"Expected 406, got {resp_bad_order.status_code}: {resp_bad_order.text}"
    
    bad_cust_id = f"nonexistent_{uuid.uuid4().hex[:8]}"
    resp_search_bad = requests.get(get_url("orders", f"/orders/search/customerId?custId={bad_cust_id}"), timeout=10)
    assert resp_search_bad.status_code == 404, f"Expected 404, got {resp_search_bad.status_code}: {resp_search_bad.text}"
    
    bad_order_id = str(uuid.uuid4())
    resp_order_bad = requests.get(get_url("orders", f"/orders/{bad_order_id}"), timeout=10)
    assert resp_order_bad.status_code == 404, f"Expected 404, got {resp_order_bad.status_code}: {resp_order_bad.text}"

def test_payment_authorization(setup_order):
    order_id = setup_order
    payment_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Baker St"},
        "amount": 50.00,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }
    
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth_data = resp_pay.json()
    assert auth_data.get("authorised") is True
    
    resp_get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    auth_list = resp_get_pay.json()
    assert isinstance(auth_list, list)
    assert len(auth_list) > 0
    assert any(a.get("orderId") == order_id for a in auth_list)
    
    payment_payload["amount"] = 150.00
    resp_pay_declined = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay_declined.status_code == 200, f"Expected 200, got {resp_pay_declined.status_code}: {resp_pay_declined.text}"
    assert resp_pay_declined.json().get("authorised") is False
    
    resp_get_pay_declined = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay_declined.status_code == 200, f"Expected 200, got {resp_get_pay_declined.status_code}: {resp_get_pay_declined.text}"
    auth_list_declined = resp_get_pay_declined.json()
    assert any(a.get("authorised") is False for a in auth_list_declined)

def test_shipping_functionality(setup_order):
    order_id = setup_order
    shipping_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Baker St"},
        "itemCount": 3,
        "orderId": order_id
    }
    
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data.get("orderId") == order_id
    assert "trackingNumber" in ship_data
    
    resp_get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    assert resp_get_ship.json().get("orderId") == order_id
