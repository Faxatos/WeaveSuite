# Tests generated in iteration 06
# Captured: 2026-06-07T05:19:45
# Count:    18
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1264  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{random_string()}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    login_resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

# --- id=1265  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{random_string()}"
    payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Jane",
        "lastName": "Doe"
    }

    resp1 = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1266  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = f"user_{random_string()}"
    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1267  name='Carts Add And Increment Item' ---
def test_carts_add_and_increment_item():
    customer_id = f"cust_{random_string()}"
    item_id = f"item_{random_string()}"

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.50
    }

    resp1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get1.status_code == 200, f"Expected 200, got {get1.status_code}: {get1.text}"
    assert get1.json().get("quantity") == 2, f"Expected quantity 2, got {get1.json()}"

    item_payload["quantity"] = 3
    resp2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp2.status_code == 201, f"Expected 201, got {resp2.status_code}: {resp2.text}"

    get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get2.status_code == 200, f"Expected 200, got {get2.status_code}: {get2.text}"
    assert get2.json().get("quantity") == 5, f"Expected cumulative quantity 5, got {get2.json()}"

# --- id=1268  name='Carts Merge Success' ---
def test_carts_merge_success():
    customer_id = f"cust_{random_string()}"
    session_id = f"sess_{random_string()}"
    item_id = f"item_{random_string()}"

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)

    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

# --- id=1269  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{random_string()}"
    session_id = f"sess_{random_string()}"

    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 404, f"Expected 404, got {merge_resp.status_code}: {merge_resp.text}"

# --- id=1270  name='Catalogue And Verify Item' ---
def test_catalogue_get_and_verify_item():
    list_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"

    items = list_resp.json()
    if not items:
        pytest.skip("No items in catalogue to test")

    item_id = items[0].get("id")

    item_resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"
    assert item_resp.json().get("id") == item_id, "Item ID mismatch"

# --- id=1271  name='Catalogue Item Not Found' ---
def test_catalogue_item_not_found():
    item_id = f"invalid_{random_string()}"
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1272  name='Catalogue Image Not Found' ---
def test_catalogue_image_not_found():
    image_id = f"invalid_{random_string()}"
    resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1273  name='Orders Place Order Success' ---
def test_orders_place_order_success():
    username = f"user_{random_string()}"

    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com"
    }, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={
        "city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "St", "userID": username
    }, timeout=10)
    assert addr_resp.status_code == 200
    addr_id = addr_resp.json().get("id")

    get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr.status_code == 200

    card_resp = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    assert card_resp.status_code == 200
    card_id = card_resp.json().get("id")

    get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card.status_code == 200

    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "item1", "quantity": 1, "unitPrice": 50.00
    }, timeout=10)

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

    get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order.status_code == 200, f"Expected 200, got {get_order.status_code}: {get_order.text}"
    assert get_order.json().get("id") == order_id

# --- id=1274  name='Orders Place Order Payment Declined' ---
def test_orders_place_order_payment_declined():
    username = f"user_{random_string()}"

    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com"
    }, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={
        "city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "St", "userID": username
    }, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    card_id = card_resp.json().get("id")

    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "item1", "quantity": 2, "unitPrice": 60.00
    }, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=1275  name='Orders Search Not Found' ---
def test_orders_search_not_found():
    cust_id = f"nonexistent_{random_string()}"
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={cust_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1276  name='Payment Authorize Success' ---
def test_payment_authorize_success():
    order_id = f"order_{random_string()}"
    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.00,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    get_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    auths = get_resp.json()
    assert len(auths) > 0
    assert auths[0].get("orderId") == order_id

# --- id=1277  name='Shipping Ship Order' ---
def test_shipping_ship_order():
    order_id = f"order_{random_string()}"
    shipping_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id

    get_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("orderId") == order_id

# --- id=1278  name='User Address' ---
def test_user_delete_address():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com"
    }, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={
        "city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "St", "userID": username
    }, timeout=10)
    addr_id = addr_resp.json().get("id")

    del_resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert get_resp.status_code == 200
    addresses = get_resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses), "Address was not deleted"

# --- id=1279  name='User Card' ---
def test_user_delete_card():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com"
    }, timeout=10)

    card_resp = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    card_id = card_resp.json().get("id")

    del_resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert get_resp.status_code == 200
    cards = get_resp.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards), "Card was not deleted"

# --- id=1280  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{random_string()}"
    item_id = f"item_{random_string()}"

    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={
        "itemId": item_id, "quantity": 1, "unitPrice": 10.0
    }, timeout=10)

    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp.status_code == 404, f"Expected 404, got {get_resp.status_code}: {get_resp.text}"

# --- id=1281  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{random_string()}"

    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={
        "itemId": "item1", "quantity": 1, "unitPrice": 10.0
    }, timeout=10)

    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200
    assert len(get_resp.json()) == 0, "Cart should be empty after deletion"
