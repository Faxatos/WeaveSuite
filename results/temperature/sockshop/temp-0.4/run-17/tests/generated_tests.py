# Tests generated in iteration 17
# Captured: 2026-06-30T02:05:07
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=456  name='User Registration And Login' ---
def test_user_registration_and_login():
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

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == "Test"
    assert customer.get("lastName") == "User"
    assert "password" not in customer

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=457  name='User Add Address And Card' ---
def test_user_add_address_and_card():
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

    addr_req = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr = resp.json()
    assert addr["city"] == "City"
    assert addr["postcode"] == "12345"
    assert addr["id"] == addr_id

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addrs = resp.json().get("_embedded", {}).get("address", [])
    assert any(a["id"] == addr_id for a in addrs)

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card = resp.json()
    assert card["expires"] == "12/25"
    assert card["id"] == card_id
    assert card["longNum"].endswith("5678")
    assert "*" in card["longNum"]

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert any(c["id"] == card_id for c in cards)

    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addrs = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a["id"] == addr_id for a in addrs)

# --- id=458  name='Catalogue Endpoints' ---
def test_catalogue_endpoints():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    assert "tags" in tags_data
    tags = tags_data["tags"]
    assert len(tags) > 0

    tag = tags[0]
    resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    size_data = resp.json()
    assert "size" in size_data

    resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item = items[0]
    assert tag in item["tag"]

    if "imageUrl" in item and len(item["imageUrl"]) > 0:
        image_path = item["imageUrl"][0]
        image_name = image_path.split("/")[-1]
        resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=459  name='Catalogue And Cart Workflow' ---
def test_catalogue_and_cart_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item = items[0]
    item_id = item["id"]
    item_price = item["price"]

    cart_item = {"itemId": item_id, "quantity": 2, "unitPrice": item_price}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    cart_item_update = {"itemId": item_id, "quantity": 5, "unitPrice": item_price}
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=cart_item_update, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_item = resp.json()
    assert fetched_item["itemId"] == item_id
    assert fetched_item["quantity"] == 5

    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=460  name='Carts Merge' ---
def test_carts_merge():
    username = f"user_{uuid.uuid4().hex[:8]}"
    session_id = f"session_{uuid.uuid4().hex[:8]}"

    items = requests.get(get_url("catalogue", "/catalogue"), timeout=10).json()
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    cart_item = {"itemId": item_id, "quantity": 2, "unitPrice": item_price}
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 2

# --- id=461  name='Orders Successful Checkout' ---
def test_orders_successful_checkout():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}, timeout=10)

    addr_req = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10).json()["id"]

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_req, timeout=10).json()["id"]

    items = requests.get(get_url("catalogue", "/catalogue"), timeout=10).json()
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": item_price}
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
    order_id = order["id"]
    assert order["customer"]["username"] == username
    assert order["address"]["city"] == "City"
    assert order["card"]["longNum"].endswith("5678")
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == item_id
    assert order["total"] == item_price

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id
    assert fetched_order["status"] in ["CREATED", "PAID", "SHIPPED"]

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id
    assert payments[0]["authorised"] is True

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert shipment["carrier"] is not None

# --- id=462  name='Orders Missing Fields Negative' ---
def test_orders_missing_fields_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}, timeout=10)

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_req, timeout=10).json()["id"]

    items = requests.get(get_url("catalogue", "/catalogue"), timeout=10).json()
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": item_price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=463  name='Orders Invalid Uri Format Negative' ---
def test_orders_invalid_uri_format_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}, timeout=10)

    addr_req = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10).json()["id"]

    items = requests.get(get_url("catalogue", "/catalogue"), timeout=10).json()
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": item_price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/invalid_format",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=464  name='Orders Payment Declined Negative' ---
def test_orders_payment_declined_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}, timeout=10)

    addr_req = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10).json()["id"]

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_req, timeout=10).json()["id"]

    items = requests.get(get_url("catalogue", "/catalogue"), timeout=10).json()
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    quantity = int(105 / item_price) + 1
    cart_item = {"itemId": item_id, "quantity": quantity, "unitPrice": item_price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()
