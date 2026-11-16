# Tests generated in iteration 07
# Captured: 2026-06-20T23:09:32
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1027  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Expected at least one item in catalogue"

    item = items[0]
    item_id = item["id"]

    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_item = resp.json()
    assert fetched_item["id"] == item_id
    assert fetched_item["name"] == item["name"]

    resp = requests.get(get_url("catalogue", "/catalogue/invalid-id-12345"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1028  name='Catalogue Size And Tags' ---
def test_catalogue_size_and_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    assert "tags" in tags_data

    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    size_data = resp.json()
    assert "size" in size_data
    assert isinstance(size_data["size"], int)

# --- id=1029  name='User Registration And Profile' ---
def test_user_registration_and_profile():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    email = f"{username}@example.com"

    user_data = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, "wrong"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    address_data = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_address = resp.json()
    assert fetched_address["city"] == address_data["city"]

    card_data = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_card = resp.json()
    assert fetched_card["expires"] == card_data["expires"]
    assert "*" in fetched_card["longNum"]

    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is True

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is False

# --- id=1030  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 9.99
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

    item_data["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=1031  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    item_id_1 = f"item_{uuid.uuid4().hex[:8]}"
    item_id_2 = f"item_{uuid.uuid4().hex[:8]}"

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item_id_1, "quantity": 1, "unitPrice": 10.0}, timeout=10)
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": item_id_2, "quantity": 2, "unitPrice": 20.0}, timeout=10)

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    item_ids = [item["itemId"] for item in items]
    assert item_id_1 in item_ids
    assert item_id_2 in item_ids

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=nonexistent_{uuid.uuid4().hex}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1032  name='Orders E2e And Failures' ---
def test_orders_e2e_and_failures():
    username = f"user_{uuid.uuid4().hex[:8]}"

    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "F", "lastName": "L"
    }, timeout=10)

    resp = requests.post(get_url("user", "/addresses"), json={
        "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username
    }, timeout=10)
    address_id = resp.json()["id"]

    resp = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    card_id = resp.json()["id"]

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "item1", "quantity": 1, "unitPrice": 50.0
    }, timeout=10)

    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]
    assert order["customer"]["username"] == username
    assert len(order["items"]) == 1
    assert order["total"] == 50.0

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == order_id

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in orders)

    bad_req = order_req.copy()
    bad_req["address"] = "/addresses/invalidformat"
    resp = requests.post(get_url("orders", "/orders"), json=bad_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    requests.delete(get_url("carts", f"/carts/{username}/items/item1"), timeout=10)
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "item2", "quantity": 1, "unitPrice": 150.0
    }, timeout=10)

    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=1033  name='Payment Http Authorization' ---
def test_payment_http_authorization():
    order_id = f"order_{uuid.uuid4().hex[:8]}"

    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is True

    payment_req["amount"] = 150.0
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is False

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 2
    assert auths[1]["authorised"] is False

# --- id=1034  name='Shipping Http Lifecycle' ---
def test_shipping_http_lifecycle():
    order_id = f"order_{uuid.uuid4().hex[:8]}"

    shipping_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment
    assert "carrier" in shipment

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_shipment = resp.json()
    assert fetched_shipment["orderId"] == order_id
    assert fetched_shipment["trackingNumber"] == shipment["trackingNumber"]
