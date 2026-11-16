# Tests generated in iteration 15
# Captured: 2026-06-30T17:49:58
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=671  name='Catalogue Query And Images' ---
def test_catalogue_query_and_images():
    tags_resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue?size=5"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0]["id"]
        get_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert get_item.status_code == 200, f"Expected 200, got {get_item.status_code}: {get_item.text}"
        assert get_item.json()["id"] == item_id

# --- id=672  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    bad_id = f"nonexistent_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("catalogue", f"/catalogue/{bad_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=673  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "MySecretPassword123"

    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    reg_resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_user.status_code == 200, f"Expected 200, got {get_user.status_code}: {get_user.text}"
    assert get_user.json()["username"] == username

    login_resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    reg_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert reg_conflict.status_code == 409, f"Expected 409, got {reg_conflict.status_code}: {reg_conflict.text}"

# --- id=674  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"
    }, timeout=10)

    addr_req = {
        "userID": username, "number": "10", "street": "High St", "city": "London", "postcode": "W1", "country": "UK"
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]

    get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr.status_code == 200, f"Expected 200, got {get_addr.status_code}: {get_addr.text}"
    assert get_addr.json()["city"] == "London"

    card_req = {
        "userID": username, "longNum": "1111222233334444", "expires": "10/26", "ccv": "999"
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card.status_code == 200, f"Expected 200, got {get_card.status_code}: {get_card.text}"
    assert get_card.json()["expires"] == "10/26"

    del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert del_addr.status_code == 200, f"Expected 200, got {del_addr.status_code}: {del_addr.text}"

    del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert del_card.status_code == 200, f"Expected 200, got {del_card.status_code}: {del_card.text}"

# --- id=675  name='Carts Workflow' ---
def test_carts_workflow():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={
        "itemId": item_id, "quantity": 1, "unitPrice": 9.99
    }, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 1

    patch_resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json={
        "itemId": item_id, "quantity": 5, "unitPrice": 9.99
    }, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_item_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_item_resp.status_code == 200, f"Expected 200, got {get_item_resp.status_code}: {get_item_resp.text}"
    assert get_item_resp.json()["quantity"] == 5

    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_item_resp_after = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_item_resp_after.status_code == 404, f"Expected 404, got {get_item_resp_after.status_code}: {get_item_resp_after.text}"

# --- id=676  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={
        "itemId": item_id, "quantity": 2, "unitPrice": 5.0
    }, timeout=10)

    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id

# --- id=677  name='Orders E2e Workflow' ---
def test_orders_e2e_workflow():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    if not items:
        pytest.skip("No catalogue items available")
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@example.com",
        "firstName": "Test", "lastName": "User"
    }, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={
        "userID": username, "number": "123", "street": "Main St", "city": "City", "postcode": "12345", "country": "Country"
    }, timeout=10)
    address_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={
        "userID": username, "longNum": "1234567812345678", "expires": "12/25", "ccv": "123"
    }, timeout=10)
    card_id = card_resp.json()["id"]

    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item_id, "quantity": 2, "unitPrice": item_price
    }, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

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

    get_order_resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    fetched_order = get_order_resp.json()
    assert fetched_order["id"] == order_id
    assert fetched_order["customer"]["username"] == username

    pay_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    payments = pay_resp.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id

    ship_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    shipment = ship_resp.json()
    assert shipment["orderId"] == order_id

# --- id=678  name='Orders Negative Paths' ---
def test_orders_negative_paths():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"
    }, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={
        "userID": username, "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"
    }, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={
        "userID": username, "longNum": "1234567812345678", "expires": "12/25", "ccv": "123"
    }, timeout=10)
    card_id = card_resp.json()["id"]

    order_req_empty_cart = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    order_resp_406 = requests.post(get_url("orders", "/orders"), json=order_req_empty_cart, timeout=10)
    assert order_resp_406.status_code == 406, f"Expected 406, got {order_resp_406.status_code}: {order_resp_406.text}"

    order_req_404 = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/malformed_id_without_colon",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp_404 = requests.post(get_url("orders", "/orders"), json=order_req_404, timeout=10)
    assert order_resp_404.status_code == 404, f"Expected 404, got {order_resp_404.status_code}: {order_resp_404.text}"

# --- id=679  name='Payment Declined Large Amount' ---
def test_payment_declined_large_amount():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    pay_req = {
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"},
        "amount": 150.0,
        "card": {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    pay_resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json()["authorised"] is False

    get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay.status_code == 200, f"Expected 200, got {get_pay.status_code}: {get_pay.text}"
    assert len(get_pay.json()) == 1
    assert get_pay.json()[0]["authorised"] is False
