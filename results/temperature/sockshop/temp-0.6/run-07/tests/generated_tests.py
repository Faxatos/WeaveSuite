# Tests generated in iteration 02
# Captured: 2026-07-05T14:20:10
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=910  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = random_string()
    password = random_string()
    email = f"{username}@example.com"

    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "John",
        "lastName": "Doe"
    }

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer.get("username") == username

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=911  name='User Address And Card' ---
def test_user_address_and_card():
    username = random_string()
    password = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": password}, timeout=10)

    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    assert addr_id is not None

    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_data = resp.json()
    assert addr_data["city"] == addr_payload["city"]
    assert addr_data["country"] == addr_payload["country"]
    assert addr_data["number"] == addr_payload["number"]
    assert addr_data["postcode"] == addr_payload["postcode"]
    assert addr_data["street"] == addr_payload["street"]

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_data = resp.json()
    assert card_data["expires"] == card_payload["expires"]
    assert card_data["longNum"].endswith("3456")
    assert "*" in card_data["longNum"]

    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=912  name='User Customer' ---
def test_user_customer_delete():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is True

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is False

# --- id=913  name='Carts Add Update' ---
def test_carts_add_update_delete():
    customer_id = random_string()

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item = items[0]
    item_id = item["id"]
    unit_price = item["price"]

    cart_item = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 2

    cart_item["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=914  name='Carts Increment Quantity' ---
def test_carts_increment_quantity():
    customer_id = random_string()

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp.json()[0]["id"]

    cart_item = {"itemId": item_id, "quantity": 2, "unitPrice": 10.0}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    cart_item_inc = {"itemId": item_id, "quantity": 3, "unitPrice": 10.0}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item_inc, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

# --- id=915  name='Carts Merge' ---
def test_carts_merge():
    customer_id = random_string()
    session_id = random_string()

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp.json()[0]["id"]

    cart_item = {"itemId": item_id, "quantity": 2, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=cart_item, timeout=10)

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 2

# --- id=916  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = random_string()

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp.json()[0]["id"]

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=917  name='Catalogue And Size' ---
def test_catalogue_get_and_size():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0

    item_id = items[0]["id"]

    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    item = resp.json()
    assert item["id"] == item_id

    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    size_data = resp.json()
    assert "size" in size_data

    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    assert "tags" in tags_data

# --- id=918  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=919  name='Orders Checkout E2e' ---
def test_orders_checkout_e2e():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]
    item_id = item["id"]

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    assert order["customer"]["username"] == username
    assert order["address"]["city"] == addr_payload["city"]
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == item_id

    order_id = order["id"]

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == order_id

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    embedded = resp.json().get("_embedded", {})
    customer_orders = embedded.get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

# --- id=920  name='Orders Negative Invalid Uris' ---
def test_orders_negative_invalid_uris():
    username = random_string()

    order_req_bad_prefix = {
        "customer": f"/bad/{username}",
        "address": f"/bad/{username}:1",
        "card": f"/bad/{username}:1234",
        "items": f"/bad/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req_bad_prefix, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    order_req_bad_id = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_id_without_colon",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req_bad_id, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=921  name='Orders Not Found' ---
def test_orders_not_found():
    resp = requests.get(get_url("orders", "/orders/invalid_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=922  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = str(uuid.uuid4())

    pay_req = {
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is True

    pay_req["amount"] = 80.0
    resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 2

# --- id=923  name='Payment Authorization Declined' ---
def test_payment_authorization_declined():
    order_id = str(uuid.uuid4())

    pay_req = {
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is False

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is False

# --- id=924  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = str(uuid.uuid4())

    ship_req = {
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_shipment = resp.json()
    assert fetched_shipment["orderId"] == order_id
    assert fetched_shipment["trackingNumber"] == shipment["trackingNumber"]
