# Tests generated in iteration 01
# Captured: 2026-06-02T10:13:49
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1  name='Orders End To End Placement' ---
def test_orders_end_to_end_placement():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "NW1 6XE",
        "street": "Baker Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    card_payload = {
        "ccv": "123",
        "expires": "12/26",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    catalogue = resp.json()
    assert len(catalogue) > 0, "Catalogue is empty"
    item = catalogue[0]

    cart_item_payload = {
        "itemId": item["id"],
        "quantity": 1,
        "unitPrice": item.get("price", 10.0)
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    order_id = resp.json()["id"]

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=2  name='Carts Merge Functionality' ---
def test_carts_merge_functionality():
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    username = f"user_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    catalogue = resp.json()
    assert len(catalogue) > 0, "Catalogue is empty"
    item = catalogue[0]

    cart_item_payload = {
        "itemId": item["id"],
        "quantity": 1,
        "unitPrice": item.get("price", 10.0)
    }
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=cart_item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    assert items[0]["itemId"] == item["id"]

# --- id=3  name='Orders Payment Decline' ---
def test_orders_payment_decline():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Rich",
        "lastName": "Guy"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "NW1 6XE",
        "street": "Baker Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    card_payload = {
        "ccv": "123",
        "expires": "12/26",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    catalogue = resp.json()
    assert len(catalogue) > 0, "Catalogue is empty"
    item = catalogue[0]

    price = item.get("price", 10.0)
    if price <= 0:
        price = 10.0
    quantity = int(105.0 / price) + 1

    cart_item_payload = {
        "itemId": item["id"],
        "quantity": quantity,
        "unitPrice": price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=4  name='Shipping Http Shipment Creation' ---
def test_shipping_http_shipment_creation():
    order_id = str(uuid.uuid4())
    shipping_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "NW1 6XE",
            "street": "Baker Street"
        },
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=5  name='Catalogue Tags And Filtering' ---
def test_catalogue_tags_and_filtering():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    tags = tags_data.get("tags", [])
    if tags:
        tag = tags[0]
        resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=6  name='User Login Functionality' ---
def test_user_login_functionality():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "mysecretpassword"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
