# Tests generated in iteration 01
# Captured: 2026-06-06T17:13:18
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1047  name='User Registration And Login' ---
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

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify via GET
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    user_resp = resp_get.json()
    assert user_resp.get("username") == username
    assert user_resp.get("email") == user_data["email"]
    assert user_resp.get("firstName") == user_data["firstName"]
    assert user_resp.get("lastName") == user_data["lastName"]
    assert "password" not in user_resp or user_resp.get("password") != password

    # Negative: Register same user
    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Login success
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Login failure
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

# --- id=1048  name='User Address And Card' ---
def test_user_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Add address
    addr_data = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    # Verify address via GET
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_resp = resp_addr_get.json()
    assert addr_resp.get("city") == addr_data["city"]
    assert addr_resp.get("country") == addr_data["country"]
    assert addr_resp.get("number") == addr_data["number"]
    assert addr_resp.get("postcode") == addr_data["postcode"]
    assert addr_resp.get("street") == addr_data["street"]

    # Add card
    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    # Verify card via GET
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_resp = resp_card_get.json()
    assert card_resp.get("ccv") == card_data["ccv"]
    assert card_resp.get("expires") == card_data["expires"]

# --- id=1049  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Catalogue is empty"

    item_id = items[0]["id"]
    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id

    # Negative
    resp_not_found = requests.get(get_url("catalogue", "/catalogue/invalid_id_123"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=1050  name='Carts Cumulative Operations' ---
def test_carts_cumulative_operations():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = "item_1"
    item_data = {"itemId": item_id, "quantity": 1, "unitPrice": 10.5}

    # Add item
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    add_resp = resp_add.json()
    assert add_resp["itemId"] == item_data["itemId"]
    assert add_resp["quantity"] == item_data["quantity"]
    assert add_resp["unitPrice"] == item_data["unitPrice"]

    # Verify via GET
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_resp = resp_get.json()
    assert get_resp["itemId"] == item_data["itemId"]
    assert get_resp["quantity"] == item_data["quantity"]
    assert get_resp["unitPrice"] == item_data["unitPrice"]

    # Add same item again (Cumulative state)
    resp_add_again = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_add_again.status_code == 201, f"Expected 201, got {resp_add_again.status_code}: {resp_add_again.text}"

    # Verify cumulative state via GET
    resp_get_cum = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_cum.status_code == 200, f"Expected 200, got {resp_get_cum.status_code}: {resp_get_cum.text}"
    assert resp_get_cum.json()["quantity"] == 2, "Quantity should be incremented to 2"

    # Update item via PATCH
    patch_data = {"itemId": item_id, "quantity": 5, "unitPrice": 10.5}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_data, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify PATCH
    resp_get_patch = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_patch.status_code == 200, f"Expected 200, got {resp_get_patch.status_code}: {resp_get_patch.text}"
    assert resp_get_patch.json()["quantity"] == 5

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify DELETE
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=1051  name='Carts Merge' ---
def test_carts_merge():
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Add item to session cart
    item_sess = {"itemId": "item_s", "quantity": 1, "unitPrice": 5.0}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_sess, timeout=10)

    # Add item to customer cart
    item_cust = {"itemId": "item_c", "quantity": 2, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_cust, timeout=10)

    # Merge session into customer
    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    # Verify customer cart has both items
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    item_ids = [i["itemId"] for i in items]
    assert "item_s" in item_ids
    assert "item_c" in item_ids

    # Negative: Merge non-existent session
    bad_session = f"bad_{uuid.uuid4().hex[:8]}"
    resp_bad_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={bad_session}"), timeout=10)
    assert resp_bad_merge.status_code == 404, f"Expected 404, got {resp_bad_merge.status_code}: {resp_bad_merge.text}"

# --- id=1052  name='Orders Placement Success' ---
def test_orders_placement_success():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # 2. Add Address
    addr_data = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    addr_id = resp_addr.json().get("id")

    # 3. Add Card
    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp_card.json().get("id")

    # 4. Get Catalogue Item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    cat_items = resp_cat.json()
    assert len(cat_items) > 0
    sock = cat_items[0]

    # 5. Add Item to Cart (ensure total <= 100 for payment auth)
    item_data = {"itemId": sock["id"], "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

    # 6. Place Order
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")
    assert order_id is not None

    # 7. Verify Order via GET
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    order_data = resp_order_get.json()
    assert order_data["id"] == order_id
    assert order_data.get("payment", {}).get("authorised") is True

# --- id=1053  name='Orders Placement Payment Declined' ---
def test_orders_placement_payment_declined():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # 2. Add Address
    addr_data = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    addr_id = resp_addr.json().get("id")

    # 3. Add Card
    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp_card.json().get("id")

    # 4. Get Catalogue Item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    cat_items = resp_cat.json()
    assert len(cat_items) > 0
    sock = cat_items[0]

    # 5. Add Item to Cart (ensure total > 100 for payment decline)
    item_data = {"itemId": sock["id"], "quantity": 15, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

    # 6. Place Order
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1054  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    # Verify via GET
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) > 0
    assert auths[0]["orderId"] == order_id

# --- id=1055  name='Shipping Request' ---
def test_shipping_request():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    shipping_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 2,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

    # Verify via GET
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    shipment_get = resp_get.json()
    assert shipment_get["orderId"] == order_id
