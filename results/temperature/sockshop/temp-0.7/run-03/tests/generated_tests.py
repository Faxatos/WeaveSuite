# Tests generated in iteration 03
# Captured: 2026-06-30T10:47:27
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=542  name='User Login' ---
def test_user_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_fail.status_code == 401, f"Expected 401, got {resp_fail.status_code}: {resp_fail.text}"

# --- id=543  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    addr_payload = {
        "number": "123",
        "street": "Main St",
        "city": "Springfield",
        "postcode": "12345",
        "country": "USA",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    resp_get_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addrs = resp_get_addr.json().get("_embedded", {}).get("address", [])
    assert len(addrs) == 1
    assert addrs[0]["id"] == addr_id
    assert addrs[0]["city"] == "Springfield"

    card_payload = {
        "longNum": "1234567812345678",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    resp_get_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    cards = resp_get_card.json().get("_embedded", {}).get("card", [])
    assert len(cards) == 1
    assert cards[0]["id"] == card_id
    assert cards[0]["longNum"] == "************5678"

# --- id=544  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    del_resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"
    assert del_resp.json().get("status") is True

    del_resp2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_resp2.status_code == 200, f"Expected 200, got {del_resp2.status_code}: {del_resp2.text}"
    assert del_resp2.json().get("status") is False

# --- id=545  name='Carts Add And Retrieve Item' ---
def test_carts_add_and_retrieve_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.5
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("itemId") == item_id
    assert data.get("quantity") == 2
    assert data.get("unitPrice") == 15.5

    item_update = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 15.5
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_update, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get3.status_code == 404, f"Expected 404, got {resp_get3.status_code}: {resp_get3.text}"

# --- id=546  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item1 = {"itemId": "item1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item1, timeout=10)

    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    item2 = {"itemId": "item2", "quantity": 2, "unitPrice": 20.0}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item2, timeout=10)

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    item_ids = [i.get("itemId") for i in items]
    assert "item1" in item_ids
    assert "item2" in item_ids

# --- id=547  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=548  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert len(get_resp.json()) == 0

# --- id=549  name='Orders Place Order' ---
def test_orders_place_order():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"number": "1", "street": "S", "city": "C", "postcode": "123", "country": "US", "userID": username}, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    cat_items = cat_resp.json()
    item_id = cat_items[0]["id"] if cat_items else "item1"
    price = cat_items[0]["price"] if cat_items else 10.0

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": price}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("customer", {}).get("username") == username
    assert len(order_data.get("items", [])) == 1

    get_order_resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    assert get_order_resp.json().get("id") == order_id

# --- id=550  name='Orders Place Order Empty Cart' ---
def test_orders_place_order_empty_cart():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"number": "1", "street": "S", "city": "C", "postcode": "123", "country": "US", "userID": username}, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=551  name='Orders Place Order Invalid Uri Format' ---
def test_orders_place_order_invalid_uri_format():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format_without_colon",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 404, f"Expected 404, got {order_resp.status_code}: {order_resp.text}"

# --- id=552  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "123", "country": "US"},
        "card": {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data.get("authorised") is True
    assert auth_data.get("orderId") == order_id

    get_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    payments = get_resp.json()
    assert isinstance(payments, list)
    assert len(payments) == 1
    assert payments[0].get("authorised") is True
    assert payments[0].get("orderId") == order_id

# --- id=553  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payload = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "123", "country": "US"},
        "card": {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data.get("authorised") is False
    assert auth_data.get("orderId") == order_id

    get_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    payments = get_resp.json()
    assert isinstance(payments, list)
    assert len(payments) == 1
    assert payments[0].get("authorised") is False
    assert payments[0].get("orderId") == order_id

# --- id=554  name='Shipping Ship' ---
def test_shipping_ship():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payload = {
        "orderId": order_id,
        "itemCount": 2,
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "123", "country": "US"}
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    ship_data = resp.json()
    assert ship_data.get("orderId") == order_id
    assert "carrier" in ship_data
    assert "trackingNumber" in ship_data

    get_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    ship_data_get = get_resp.json()
    assert ship_data_get.get("orderId") == order_id
    assert ship_data_get.get("trackingNumber") == ship_data.get("trackingNumber")

# --- id=555  name='Catalogue Browse' ---
def test_catalogue_browse():
    resp = requests.get(get_url("catalogue", "/catalogue?size=5"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0]["id"]
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json().get("id") == item_id

        fake_id = f"fake_{uuid.uuid4().hex[:8]}"
        resp_fake = requests.get(get_url("catalogue", f"/catalogue/{fake_id}"), timeout=10)
        assert resp_fake.status_code == 404, f"Expected 404, got {resp_fake.status_code}: {resp_fake.text}"

# --- id=540  name='User Register And Retrieve' ---
def test_user_register_and_retrieve():
    username = f"user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    payload = {
        "username": username,
        "password": "password123",
        "email": email,
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("username") == username
    assert data.get("firstName") == "John"
    assert data.get("lastName") == "Doe"
    assert data.get("email") == email
    assert "password" not in data

# --- id=541  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"
