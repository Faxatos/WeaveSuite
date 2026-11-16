# Tests generated in iteration 05
# Captured: 2026-06-21T12:57:49
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1306  name='Catalogue List Filter And' ---
def test_catalogue_list_filter_and_get():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list) and len(items) > 0

    item = items[0]
    item_id = item["id"]

    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_item = resp.json()
    assert fetched_item["id"] == item_id
    assert fetched_item["name"] == item["name"]

    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    tags = tags_data.get("tags", [])
    assert len(tags) > 0

    tag = tags[0]

    resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    filtered_items = resp.json()
    for fi in filtered_items:
        assert tag in fi.get("tag", []), f"Item {fi['id']} missing tag {tag}"

# --- id=1307  name='Catalogue Negative Cases' ---
def test_catalogue_negative_cases():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid-id-123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/catalogue/images/invalid-image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1308  name='User Registration And Profiles' ---
def test_user_registration_and_profiles():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["username"] == username

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    address_payload = {
        "city": "Cityville",
        "country": "Countryland",
        "number": "123",
        "postcode": "12345",
        "street": "Main St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr = resp.json()
    assert addr["city"] == address_payload["city"]
    assert addr["street"] == address_payload["street"]

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card = resp.json()
    assert card["expires"] == card_payload["expires"]
    assert card["longNum"].endswith("3456")
    assert "*" in card["longNum"]

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addrs = resp.json().get("_embedded", {}).get("address", [])
    assert any(a["id"] == address_id for a in addrs)

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert any(c["id"] == card_id for c in cards)

# --- id=1309  name='User Deletion And Negative Cases' ---
def test_user_deletion_and_negative_cases():
    username = f"deluser_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com",
        "firstName": "D", "lastName": "U"
    }, timeout=10)

    resp = requests.post(get_url("user", "/addresses"), json={
        "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username
    }, timeout=10)
    address_id = resp.json()["id"]

    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addrs = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a["id"] == address_id for a in addrs)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is True

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is False

# --- id=1310  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    username = f"cartuser_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com",
        "firstName": "C", "lastName": "U"
    }, timeout=10)
    customer_id = username

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json() == []

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 2

    item_payload_2 = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_2, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    item_payload_patch = {
        "itemId": item_id,
        "quantity": 10,
        "unitPrice": unit_price
    }
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_patch, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 10

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json() == []

# --- id=1311  name='Orders End To End' ---
def test_orders_end_to_end():
    username = f"orderuser_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com",
        "firstName": "O", "lastName": "U"
    }, timeout=10)

    resp = requests.post(get_url("user", "/addresses"), json={
        "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username
    }, timeout=10)
    address_id = resp.json()["id"]

    resp = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    card_id = resp.json()["id"]

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"], "quantity": 1, "unitPrice": item["price"]
    }, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]

    assert order["customer"]["username"] == username
    assert order["total"] == item["price"]
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == item["id"]

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id
    assert fetched_order["customer"]["username"] == username

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in orders)

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) > 0
    assert auths[0]["orderId"] == order_id

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

# --- id=1312  name='Orders Negative Cases' ---
def test_orders_negative_cases():
    username = f"neguser_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com",
        "firstName": "N", "lastName": "U"
    }, timeout=10)

    resp = requests.post(get_url("user", "/addresses"), json={
        "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username
    }, timeout=10)
    address_id = resp.json()["id"]

    resp = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    card_id = resp.json()["id"]

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"], "quantity": 1, "unitPrice": item["price"]
    }, timeout=10)

    order_payload_invalid_addr = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload_invalid_addr, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1313  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json() == []

    pay_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=pay_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is True

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is True

    pay_payload["amount"] = 150.0
    resp = requests.post(get_url("payment-http", "/payments"), json=pay_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is False

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 2
    assert auths[1]["authorised"] is False

# --- id=1314  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    ship_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()
    assert fetched["orderId"] == order_id
    assert fetched["trackingNumber"] == shipment["trackingNumber"]
