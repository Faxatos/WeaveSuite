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

def generate_user():
    username = f"user_{uuid.uuid4().hex[:8]}"
    return {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

# --- Tests ---

def test_user_register_and_login():
    user = generate_user()
    resp = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("user", f"/customers/{user['username']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("user", "/login"), auth=(user["username"], user["password"]), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_user_register_conflict():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    resp = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

def test_user_login_unauthorized():
    resp = requests.get(get_url("user", "/login"), auth=("invalid", "invalid"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

def test_user_add_address_and_get():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    
    address = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "NW1 6XE",
        "street": "Baker St",
        "userID": user["username"]
    }
    resp = requests.post(get_url("user", "/addresses"), json=address, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    
    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["city"] == address["city"]
    assert data["country"] == address["country"]
    assert data["number"] == address["number"]
    assert data["postcode"] == address["postcode"]
    assert data["street"] == address["street"]

def test_user_add_card_and_get():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    
    card = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567812345678",
        "userID": user["username"]
    }
    resp = requests.post(get_url("user", "/cards"), json=card, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["ccv"] == card["ccv"]
    assert data["expires"] == card["expires"]

def test_user_delete_address():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    
    address = {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker", "userID": user["username"]}
    addr_resp = requests.post(get_url("user", "/addresses"), json=address, timeout=10)
    addr_id = addr_resp.json()["id"]
    
    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("user", f"/customers/{user['username']}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    if "_embedded" in data and "address" in data["_embedded"]:
        assert not any(a.get("id") == addr_id for a in data["_embedded"]["address"])

def test_user_delete_card():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    
    card = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": user["username"]}
    card_resp = requests.post(get_url("user", "/cards"), json=card, timeout=10)
    card_id = card_resp.json()["id"]
    
    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("user", f"/customers/{user['username']}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    if "_embedded" in data and "card" in data["_embedded"]:
        assert not any(c.get("id") == card_id for c in data["_embedded"]["card"])

def test_user_get_customer_addresses():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    
    address = {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker", "userID": user["username"]}
    addr_resp = requests.post(get_url("user", "/addresses"), json=address, timeout=10)
    addr_id = addr_resp.json()["id"]
    
    resp = requests.get(get_url("user", f"/customers/{user['username']}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "_embedded" in data
    assert "address" in data["_embedded"]
    assert any(a.get("id") == addr_id for a in data["_embedded"]["address"])

def test_user_get_customer_cards():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    
    card = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": user["username"]}
    card_resp = requests.post(get_url("user", "/cards"), json=card, timeout=10)
    card_id = card_resp.json()["id"]
    
    resp = requests.get(get_url("user", f"/customers/{user['username']}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "_embedded" in data
    assert "card" in data["_embedded"]
    assert any(c.get("id") == card_id for c in data["_embedded"]["card"])

def test_user_get_customers():
    resp = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_user_get_addresses_empty():
    resp = requests.get(get_url("user", "/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "_embedded" in data
    assert "address" in data["_embedded"]
    assert len(data["_embedded"]["address"]) == 0

def test_user_get_cards_empty():
    resp = requests.get(get_url("user", "/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "_embedded" in data
    assert "card" in data["_embedded"]
    assert len(data["_embedded"]["card"]) == 0

def test_user_delete_customer():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    
    resp = requests.delete(get_url("user", f"/customers/{user['username']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_carts_add_item_and_get():
    customer_id = f"user_{uuid.uuid4().hex[:8]}"
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    cat_items = cat_resp.json()
    if not cat_items:
        pytest.skip("No items in catalogue")
    real_item = cat_items[0]
    
    item = {
        "itemId": real_item["id"],
        "quantity": 2,
        "unitPrice": real_item["price"]
    }
    
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    resp_data = resp.json()
    assert resp_data["itemId"] == item["itemId"]
    assert resp_data["quantity"] == item["quantity"]
    assert resp_data["unitPrice"] == item["unitPrice"]
    
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item['itemId']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["itemId"] == item["itemId"]
    assert data["quantity"] == item["quantity"]
    assert data["unitPrice"] == item["unitPrice"]

def test_carts_get_item_not_found():
    customer_id = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/invalid_item"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_delete_item():
    customer_id = f"user_{uuid.uuid4().hex[:8]}"
    item = {"itemId": "test_item", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item, timeout=10)
    
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item['itemId']}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item['itemId']}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_merge_not_found():
    customer_id = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=invalid_session"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_async_get_item_not_found():
    customer_id = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts-async/{customer_id}/items/invalid_item"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_async_merge_not_found():
    customer_id = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts-async/{customer_id}/merge?sessionId=invalid_session"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_carts_delete_cart():
    customer_id = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

def test_carts_patch_item():
    customer_id = f"user_{uuid.uuid4().hex[:8]}"
    item = {"itemId": "test_item", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item, timeout=10)
    
    item["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"
    
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item['itemId']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

def test_catalogue_get_all():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert isinstance(resp.json(), list)

def test_catalogue_get_item():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == item_id

def test_catalogue_get_item_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_catalogue_get_image_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/images/invalid_image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_catalogue_get_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

def test_catalogue_get_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

def test_orders_create_and_get():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    
    address = {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker", "userID": user["username"]}
    addr_resp = requests.post(get_url("user", "/addresses"), json=address, timeout=10)
    addr_id = addr_resp.json()["id"]
    
    card = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": user["username"]}
    card_resp = requests.post(get_url("user", "/cards"), json=card, timeout=10)
    card_id = card_resp.json()["id"]
    
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    cart_item = {"itemId": item["id"], "quantity": 1, "unitPrice": min(item["price"], 50.0)}
    requests.post(get_url("carts", f"/carts/{user['username']}/items"), json=cart_item, timeout=10)
    
    order_req = {
        "customer": get_url("user", f"/customers/{user['username']}"),
        "address": get_url("user", f"/addresses/{addr_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{user['username']}/items")
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]
    
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["id"] == order_id
    assert data["payment"]["authorised"] is True

def test_orders_create_payment_declined():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    
    address = {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker", "userID": user["username"]}
    addr_resp = requests.post(get_url("user", "/addresses"), json=address, timeout=10)
    addr_id = addr_resp.json()["id"]
    
    card = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": user["username"]}
    card_resp = requests.post(get_url("user", "/cards"), json=card, timeout=10)
    card_id = card_resp.json()["id"]
    
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    cart_item = {"itemId": item["id"], "quantity": 100, "unitPrice": max(item["price"], 2.0)}
    requests.post(get_url("carts", f"/carts/{user['username']}/items"), json=cart_item, timeout=10)
    
    order_req = {
        "customer": get_url("user", f"/customers/{user['username']}"),
        "address": get_url("user", f"/addresses/{addr_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{user['username']}/items")
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

def test_orders_get_not_found():
    resp = requests.get(get_url("orders", "/orders/invalid_order_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_orders_search_not_found():
    resp = requests.get(get_url("orders", "/orders/search/customerId?custId=invalid_cust"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

def test_orders_search_by_customer():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)
    
    address = {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker", "userID": user["username"]}
    addr_resp = requests.post(get_url("user", "/addresses"), json=address, timeout=10)
    addr_id = addr_resp.json()["id"]
    
    card = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": user["username"]}
    card_resp = requests.post(get_url("user", "/cards"), json=card, timeout=10)
    card_id = card_resp.json()["id"]
    
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    cart_item = {"itemId": item["id"], "quantity": 1, "unitPrice": min(item["price"], 50.0)}
    requests.post(get_url("carts", f"/carts/{user['username']}/items"), json=cart_item, timeout=10)
    
    order_req = {
        "customer": get_url("user", f"/customers/{user['username']}"),
        "address": get_url("user", f"/addresses/{addr_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{user['username']}/items")
    }
    requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={user['username']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

def test_payment_authorize_success():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["orderId"] == payment_req["orderId"]
    assert auth["authorised"] is True
    
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) > 0
    assert auths[0]["orderId"] == payment_req["orderId"]
    assert auths[0]["authorised"] is True

def test_payment_authorize_decline():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is False

def test_shipping_create_and_get():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    shipping_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == shipping_req["orderId"]
    
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["orderId"] == shipping_req["orderId"]
    assert data["trackingNumber"] == shipment["trackingNumber"]
