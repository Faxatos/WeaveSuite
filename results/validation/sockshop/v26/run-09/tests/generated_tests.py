# Tests generated in iteration 09
# Captured: 2026-06-20T16:59:45
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=925  name='End To End Order Creation' ---
def test_end_to_end_order_creation():
    user = generate_user()
    resp = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(user["username"], user["password"]), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    address_req = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Test Street", "userID": user["username"]}
    resp = requests.post(get_url("user", "/addresses"), json=address_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["city"] == "London"

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": user["username"]}
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "3456" in resp.json()["longNum"]

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item = items[0]
    item_id = item["id"]

    cart_item = {"itemId": item_id, "quantity": 2, "unitPrice": item.get("price", 10.0)}
    resp = requests.post(get_url("carts", f"/carts/{user['username']}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{user['username']}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 1
    assert resp.json()[0]["itemId"] == item_id

    order_req = {
        "customer": f"/customers/{user['username']}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{user['username']}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]
    assert order["customer"]["username"] == user["username"]

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == order_id

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={user['username']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert len(orders) > 0
    assert orders[0]["id"] == order_id

# --- id=926  name='Order Creation Empty Cart' ---
def test_order_creation_empty_cart():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)

    address_req = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Test", "userID": user["username"]}
    resp = requests.post(get_url("user", "/addresses"), json=address_req, timeout=10)
    address_id = resp.json()["id"]

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": user["username"]}
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    card_id = resp.json()["id"]

    order_req = {
        "customer": f"/customers/{user['username']}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{user['username']}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=927  name='Order Creation Invalid Address Uri' ---
def test_order_creation_invalid_address_uri():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": user["username"]}
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    card_id = resp.json()["id"]

    cart_item = {"itemId": "test-item", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{user['username']}/items"), json=cart_item, timeout=10)

    order_req = {
        "customer": f"/customers/{user['username']}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{user['username']}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=928  name='User Registration Conflict' ---
def test_user_registration_conflict():
    user = generate_user()
    resp = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{user['username']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=929  name='Cart Merge And Update' ---
def test_cart_merge_and_update():
    session_id = str(uuid.uuid4())
    item_id = "test-item-" + str(uuid.uuid4())

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)

    resp = requests.get(get_url("carts", f"/carts/{user['username']}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{user['username']}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id

    cart_item["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{user['username']}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{user['username']}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    resp = requests.delete(get_url("carts", f"/carts/{user['username']}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{user['username']}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=930  name='Payment Authorization Declined' ---
def test_payment_authorization_declined():
    order_id = str(uuid.uuid4())
    payment_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Test"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is False

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) == 1
    assert payments[0]["authorised"] is False

# --- id=931  name='Payment Authorization Approved' ---
def test_payment_authorization_approved():
    order_id = str(uuid.uuid4())
    payment_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Test"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is True

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) == 1
    assert payments[0]["authorised"] is True

# --- id=932  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = str(uuid.uuid4())
    shipping_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Test"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id
    assert resp.json()["trackingNumber"] == shipment["trackingNumber"]

# --- id=933  name='Customer' ---
def test_delete_customer():
    user = generate_user()
    resp = requests.post(get_url("user", "/register"), json=user, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/customers/{user['username']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is True

    resp = requests.delete(get_url("user", f"/customers/{user['username']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is False

# --- id=934  name='Address And Card' ---
def test_delete_address_and_card():
    user = generate_user()
    requests.post(get_url("user", "/register"), json=user, timeout=10)

    address_req = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Test", "userID": user["username"]}
    resp = requests.post(get_url("user", "/addresses"), json=address_req, timeout=10)
    address_id = resp.json()["id"]

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": user["username"]}
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    card_id = resp.json()["id"]

    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{user['username']}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert len(addresses) == 0

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{user['username']}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert len(cards) == 0

# --- id=935  name='Catalogue Size And Tags' ---
def test_catalogue_size_and_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags = resp.json().get("tags", [])
    assert len(tags) > 0

    tag = tags[0]
    resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    size = resp.json().get("size", 0)
    assert size > 0

    resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == size

# --- id=936  name='Cart' ---
def test_cart_delete():
    user = generate_user()
    item_id = "test-item-" + str(uuid.uuid4())

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    resp = requests.post(get_url("carts", f"/carts/{user['username']}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{user['username']}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{user['username']}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0
