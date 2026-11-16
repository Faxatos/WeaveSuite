# Tests generated in iteration 11
# Captured: 2026-07-05T07:05:52
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=768  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "SecurePassword123!"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify via GET
    get_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    customer = get_resp.json()
    assert customer["username"] == username
    assert customer["firstName"] == "John"
    assert customer["lastName"] == "Doe"
    assert customer["email"] == f"{username}@example.com"
    assert "password" not in customer

    # Login
    auth = (username, password)
    login_resp = requests.get(get_url("user", "/login"), auth=auth, timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

# --- id=769  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "SecurePassword123!"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    # Register first time
    resp1 = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    # Register second time
    resp2 = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=770  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "SecurePassword123!"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    wrong_auth = (username, "WrongPassword!")
    login_resp = requests.get(get_url("user", "/login"), auth=wrong_auth, timeout=10)
    assert login_resp.status_code == 401, f"Expected 401, got {login_resp.status_code}: {login_resp.text}"

# --- id=771  name='User Address Management' ---
def test_user_address_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    address_data = {
        "userID": username,
        "number": "123",
        "street": "Main St",
        "city": "Metropolis",
        "postcode": "12345",
        "country": "USA"
    }

    add_resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert add_resp.status_code == 200, f"Expected 200, got {add_resp.status_code}: {add_resp.text}"
    address_id = add_resp.json()["id"]

    get_resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    addr = get_resp.json()
    assert addr["id"] == address_id
    assert addr["number"] == "123"
    assert addr["street"] == "Main St"
    assert addr["city"] == "Metropolis"
    assert addr["postcode"] == "12345"
    assert addr["country"] == "USA"

    list_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    addresses = list_resp.json().get("_embedded", {}).get("address", [])
    assert any(a["id"] == address_id for a in addresses)

    del_resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

    list_resp_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert list_resp_after.status_code == 200, f"Expected 200, got {list_resp_after.status_code}: {list_resp_after.text}"
    addresses_after = list_resp_after.json().get("_embedded", {}).get("address", [])
    assert all(a["id"] != address_id for a in addresses_after)

# --- id=772  name='User Card Management' ---
def test_user_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    card_data = {
        "userID": username,
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123"
    }

    add_resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert add_resp.status_code == 200, f"Expected 200, got {add_resp.status_code}: {add_resp.text}"
    card_id = add_resp.json()["id"]

    get_resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    card = get_resp.json()
    assert card["id"] == card_id
    assert card["expires"] == "12/25"
    assert card["longNum"].endswith("3456")
    assert "123456789012" not in card["longNum"]

    list_resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    cards = list_resp.json().get("_embedded", {}).get("card", [])
    assert any(c["id"] == card_id for c in cards)

    del_resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

    list_resp_after = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert list_resp_after.status_code == 200, f"Expected 200, got {list_resp_after.status_code}: {list_resp_after.text}"
    cards_after = list_resp_after.json().get("_embedded", {}).get("card", [])
    assert all(c["id"] != card_id for c in cards_after)

# --- id=773  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0

    item_id = items[0]["id"]
    get_resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    item = get_resp.json()
    assert item["id"] == item_id
    assert "name" in item
    assert "price" in item
    assert "count" in item

# --- id=774  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    fake_id = f"fake_{uuid.uuid4().hex}"
    resp = requests.get(get_url("catalogue", f"/catalogue/{fake_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=775  name='Carts Management' ---
def test_carts_management():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200
    item = cat_resp.json()[0]
    item_id = item["id"]
    price = item["price"]

    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": price
    }

    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2
    assert items[0]["unitPrice"] == price

    patch_data = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": price
    }
    patch_resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_data, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_item_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_item_resp.status_code == 200, f"Expected 200, got {get_item_resp.status_code}: {get_item_resp.text}"
    assert get_item_resp.json()["quantity"] == 5

    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_item_after = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_item_after.status_code == 404, f"Expected 404, got {get_item_after.status_code}: {get_item_after.text}"

    del_cart_resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert del_cart_resp.status_code == 202, f"Expected 202, got {del_cart_resp.status_code}: {del_cart_resp.text}"

# --- id=776  name='Carts Merge' ---
def test_carts_merge():
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    get_cust_cart = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_cust_cart.status_code == 200, f"Expected 200, got {get_cust_cart.status_code}: {get_cust_cart.text}"
    cust_items = get_cust_cart.json()
    assert len(cust_items) == 1
    assert cust_items[0]["itemId"] == item["id"]

    fake_session = f"fake_{uuid.uuid4().hex[:8]}"
    merge_fake = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={fake_session}"), timeout=10)
    assert merge_fake.status_code == 404, f"Expected 404, got {merge_fake.status_code}: {merge_fake.text}"

# --- id=777  name='Orders Placement E2e' ---
def test_orders_placement_e2e():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"userID": username, "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"}, timeout=10)
    address_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 2, "unitPrice": item["price"]}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order = order_resp.json()
    order_id = order["id"]

    assert order["customer"]["username"] == username
    assert order["address"]["street"] == "S"
    assert order["card"]["expires"] == "12/25"
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == item["id"]
    assert order["items"][0]["quantity"] == 2
    assert abs(order["total"] - (2 * item["price"])) < 0.01
    assert order["payment"]["authorised"] is True
    assert order["status"] in ["CREATED", "PAID", "SHIPPED"]

    get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order.status_code == 200, f"Expected 200, got {get_order.status_code}: {get_order.text}"
    assert get_order.json()["id"] == order_id

    search_resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    customer_orders = search_resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

    pay_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    authorizations = pay_resp.json()
    assert len(authorizations) > 0
    assert authorizations[0]["authorised"] is True
    assert authorizations[0]["orderId"] == order_id

    ship_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    shipment = ship_resp.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment

# --- id=778  name='Orders Placement Empty Cart' ---
def test_orders_placement_empty_cart():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"userID": username, "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"}, timeout=10)
    address_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}, timeout=10)
    card_id = card_resp.json()["id"]

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=779  name='Orders Placement Invalid Uri' ---
def test_orders_placement_invalid_uri():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_format_without_colon",
        "card": "/cards/invalid_format",
        "items": f"/carts/{username}/items"
    }

    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert order_resp.status_code == 404, f"Expected 404, got {order_resp.status_code}: {order_resp.text}"

# --- id=780  name='Payment Authorization Boundaries' ---
def test_payment_authorization_boundaries():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    req_valid = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"},
        "card": {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    }
    resp_valid = requests.post(get_url("payment-http", "/payments"), json=req_valid, timeout=10)
    assert resp_valid.status_code == 200, f"Expected 200, got {resp_valid.status_code}: {resp_valid.text}"
    assert resp_valid.json()["authorised"] is True

    req_invalid_high = dict(req_valid)
    req_invalid_high["amount"] = 150.0
    resp_invalid_high = requests.post(get_url("payment-http", "/payments"), json=req_invalid_high, timeout=10)
    assert resp_invalid_high.status_code == 200, f"Expected 200, got {resp_invalid_high.status_code}: {resp_invalid_high.text}"
    assert resp_invalid_high.json()["authorised"] is False

    req_invalid_low = dict(req_valid)
    req_invalid_low["amount"] = 0.0
    resp_invalid_low = requests.post(get_url("payment-http", "/payments"), json=req_invalid_low, timeout=10)
    assert resp_invalid_low.status_code == 200, f"Expected 200, got {resp_invalid_low.status_code}: {resp_invalid_low.text}"
    assert resp_invalid_low.json()["authorised"] is False

    get_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    authorizations = get_resp.json()
    assert len(authorizations) == 3
    assert authorizations[0]["authorised"] is True
    assert authorizations[1]["authorised"] is False
    assert authorizations[2]["authorised"] is False

# --- id=781  name='Shipping' ---
def test_shipping_service():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    ship_req = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"}
    }

    post_resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert post_resp.status_code == 200, f"Expected 200, got {post_resp.status_code}: {post_resp.text}"
    shipment = post_resp.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment
    assert "carrier" in shipment

    get_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    shipment_get = get_resp.json()
    assert shipment_get["orderId"] == order_id
    assert shipment_get["trackingNumber"] == shipment["trackingNumber"]
    assert shipment_get["carrier"] == shipment["carrier"]
