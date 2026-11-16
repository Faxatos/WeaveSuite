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

def generate_user():
    username = f"user_{uuid.uuid4().hex[:8]}"
    return {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

def test_user_registration_and_profile_lifecycle():
    user_data = generate_user()
    username = user_data["username"]

    # 1. Register User
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Negative: Register same user
    resp_dup = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

    # 2. Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, user_data["password"]), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Bad Login
    resp_bad_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

    # 3. Add Address
    addr_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    # Verify Address GET
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_data = resp_addr_get.json()
    assert addr_data["city"] == addr_payload["city"]
    assert addr_data["country"] == addr_payload["country"]
    assert addr_data["number"] == addr_payload["number"]
    assert addr_data["postcode"] == addr_payload["postcode"]
    assert addr_data["street"] == addr_payload["street"]

    # 4. Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    # Verify Card GET
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data["ccv"] == card_payload["ccv"]
    assert card_data["expires"] == card_payload["expires"]
    assert card_data["longNum"].endswith(card_payload["longNum"][-4:])

    # 5. Delete Address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Verify Address Deletion
    resp_all_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_all_addr.status_code == 200, f"Expected 200, got {resp_all_addr.status_code}: {resp_all_addr.text}"
    addresses = resp_all_addr.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses)

    # 6. Delete Card
    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    # Verify Card Deletion
    resp_all_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_all_cards.status_code == 200, f"Expected 200, got {resp_all_cards.status_code}: {resp_all_cards.text}"
    cards = resp_all_cards.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

def test_catalogue_endpoints():
    # GET /tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags = resp_tags.json().get("tags", [])
    assert len(tags) > 0

    # GET /catalogue/size
    resp_size = requests.get(get_url("catalogue", f"/catalogue/size?tags={tags[0]}"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

    # GET /catalogue
    resp_cat = requests.get(get_url("catalogue", f"/catalogue?tags={tags[0]}"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    # GET /catalogue/{id}
    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id

    # Negative GET /catalogue/{id}
    resp_not_found = requests.get(get_url("catalogue", "/catalogue/invalid-id-12345"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

def test_carts_lifecycle():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get a real item from catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200
    item = resp_cat.json()[0]
    item_id = item["id"]
    price = item["price"]

    # 1. POST item to cart
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    resp_post = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_post.status_code == 201, f"Expected 201, got {resp_post.status_code}: {resp_post.text}"

    # Verify POST
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["itemId"] == item_id
    assert resp_get.json()["quantity"] == 1
    assert resp_get.json()["unitPrice"] == price

    # 2. PATCH item in cart
    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": price}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify PATCH
    resp_get_patch = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_patch.status_code == 200, f"Expected 200, got {resp_get_patch.status_code}: {resp_get_patch.text}"
    assert resp_get_patch.json()["quantity"] == 5

    # 3. DELETE item from cart
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify DELETE
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

    # 4. DELETE entire cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200
    item = resp_cat.json()[0]

    # Add to session cart
    item_payload = {"itemId": item["id"], "quantity": 2, "unitPrice": item["price"]}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)

    # Merge
    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    # Verify merge
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) >= 1
    assert any(i["itemId"] == item["id"] for i in items)

    # Negative merge
    resp_bad_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=invalid_session_123"), timeout=10)
    assert resp_bad_merge.status_code == 404, f"Expected 404, got {resp_bad_merge.status_code}: {resp_bad_merge.text}"

def test_orders_e2e_workflow_success():
    # Setup User, Address, Card
    user_data = generate_user()
    username = user_data["username"]
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_payload = {"city": "C", "country": "US", "number": "1", "postcode": "123", "street": "S", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json()["id"]

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json()["id"]

    # Setup Cart (ensure total <= 100 for successful payment)
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp_cat.json()[0]
    safe_qty = 1 if item["price"] <= 100 else 0
    if safe_qty == 0:
        pytest.skip("No items cheap enough for successful order")

    item_payload = {"itemId": item["id"], "quantity": safe_qty, "unitPrice": item["price"]}
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

    # Verify Order
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json()["id"] == order_id
    assert resp_order_get.json()["payment"]["authorised"] is True

    # Verify Payment Authorization
    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auths = resp_pay.json()
    assert len(auths) > 0
    assert auths[-1]["authorised"] is True
    assert auths[-1]["orderId"] == order_id

    # Verify Shipping
    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json()["orderId"] == order_id

def test_orders_e2e_workflow_payment_failure():
    # Setup User, Address, Card
    user_data = generate_user()
    username = user_data["username"]
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_payload = {"city": "C", "country": "US", "number": "1", "postcode": "123", "street": "S", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json()["id"]

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json()["id"]

    # Setup Cart (ensure total > 100 for payment failure)
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp_cat.json()[0]
    price = item["price"]
    huge_qty = int(105 // price) + 1

    item_payload = {"itemId": item["id"], "quantity": huge_qty, "unitPrice": price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

def test_payment_and_shipping_standalone():
    order_id = f"test-order-{uuid.uuid4().hex[:8]}"

    # Payment <= 100 (Authorized)
    pay_req_auth = {
        "address": {"city": "C", "country": "US", "number": "1", "postcode": "123", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=pay_req_auth, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json()["authorised"] is True

    # Verify Payment GET
    resp_pay_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay_get.status_code == 200, f"Expected 200, got {resp_pay_get.status_code}: {resp_pay_get.text}"
    auths = resp_pay_get.json()
    assert len(auths) > 0
    assert auths[-1]["authorised"] is True
    assert auths[-1]["orderId"] == order_id

    # Payment > 100 (Declined)
    pay_req_decl = pay_req_auth.copy()
    pay_req_decl["amount"] = 150.0
    resp_pay_decl = requests.post(get_url("payment-http", "/payments"), json=pay_req_decl, timeout=10)
    assert resp_pay_decl.status_code == 200, f"Expected 200, got {resp_pay_decl.status_code}: {resp_pay_decl.text}"
    assert resp_pay_decl.json()["authorised"] is False

    # Shipping
    ship_req = {
        "address": {"city": "C", "country": "US", "number": "1", "postcode": "123", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment

    # Verify Shipping GET
    resp_ship_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship_get.status_code == 200, f"Expected 200, got {resp_ship_get.status_code}: {resp_ship_get.text}"
    assert resp_ship_get.json()["orderId"] == order_id
    assert resp_ship_get.json()["carrier"] == shipment["carrier"]
