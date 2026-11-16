# Tests generated in iteration 16
# Captured: 2026-07-05T10:11:34
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=833  name='Catalogue Items And Single Item' ---
def test_catalogue_get_items_and_single_item():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Catalogue should not be empty"
    item_id = items[0]["id"]

    url_item = get_url("catalogue", f"/catalogue/{item_id}")
    resp_item = requests.get(url_item, timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id

# --- id=834  name='Catalogue Item Not Found' ---
def test_catalogue_get_item_not_found():
    url = get_url("catalogue", "/catalogue/non-existent-id-12345")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=835  name='User Register And Login' ---
def test_user_register_and_login():
    username = generate_random_string()
    password = "password123"
    payload = {"username": username, "password": password, "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}
    reg_url = get_url("user", "/register")
    resp = requests.post(reg_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=HTTPBasicAuth(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

# --- id=836  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    login_url = get_url("user", "/login")
    resp = requests.get(login_url, auth=HTTPBasicAuth("invalid_user", "wrong_pwd"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=837  name='User Register Conflict' ---
def test_user_register_conflict():
    username = generate_random_string()
    payload = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}
    reg_url = get_url("user", "/register")
    resp1 = requests.post(reg_url, json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(reg_url, json=payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=838  name='User Add Address And' ---
def test_user_add_address_and_get():
    username = generate_random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    addr_url = get_url("user", "/addresses")
    resp = requests.post(addr_url, json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json()["id"]

    get_url_addr = get_url("user", f"/addresses/{addr_id}")
    get_resp = requests.get(get_url_addr, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    data = get_resp.json()
    assert data["city"] == "City"
    assert data["id"] == addr_id

# --- id=839  name='User Add Card And' ---
def test_user_add_card_and_get():
    username = generate_random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_url = get_url("user", "/cards")
    resp = requests.post(card_url, json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    get_url_card = get_url("user", f"/cards/{card_id}")
    get_resp = requests.get(get_url_card, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    data = get_resp.json()
    assert data["id"] == card_id
    assert data["longNum"].endswith("3456")
    assert "*" in data["longNum"]

# --- id=840  name='User Customer' ---
def test_user_delete_customer():
    username = generate_random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    del_url = get_url("user", f"/customers/{username}")
    resp = requests.delete(del_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is True

    resp2 = requests.delete(del_url, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    assert resp2.json()["status"] is False

# --- id=841  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    customer_id = generate_random_string()
    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10).json()
    item_id = cat_resp[0]["id"]

    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    cart_url = get_url("carts", f"/carts/{customer_id}/items")
    resp = requests.post(cart_url, json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    get_resp = requests.get(cart_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert len(items) > 0
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

    single_item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    single_resp = requests.get(single_item_url, timeout=10)
    assert single_resp.status_code == 200, f"Expected 200, got {single_resp.status_code}: {single_resp.text}"
    assert single_resp.json()["itemId"] == item_id

# --- id=842  name='Carts Item Not Found' ---
def test_carts_get_item_not_found():
    customer_id = generate_random_string()
    url = get_url("carts", f"/carts/{customer_id}/items/nonexistent-item")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=843  name='Orders Create Success' ---
def test_orders_create_success():
    username = generate_random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json()
    addr_uri = f"/addresses/{addr_resp['id']}"

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json()
    card_uri = f"/cards/{card_resp['id']}"

    customer_uri = f"/customers/{username}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10).json()
    item_id = cat_resp[0]["id"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)
    items_uri = f"/carts/{username}/items"

    order_payload = {
        "address": addr_uri,
        "card": card_uri,
        "customer": customer_uri,
        "items": items_uri
    }

    order_url = get_url("orders", "/orders")
    resp = requests.post(order_url, json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    assert "id" in order
    assert order["customer"]["username"] == username
    assert order["status"] in ["CREATED", "PAID", "SHIPPED"]

    get_order_url = get_url("orders", f"/orders/{order['id']}")
    get_resp = requests.get(get_order_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["id"] == order["id"]

# --- id=844  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    order_payload = {"address": "/addresses/someuser:123"}
    order_url = get_url("orders", "/orders")
    resp = requests.post(order_url, json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=845  name='Orders Create Bad Uri' ---
def test_orders_create_bad_uri():
    order_payload = {
        "address": "/addresses/invalid-format",
        "card": "/cards/invalid-format",
        "customer": "/customers/testuser",
        "items": "/carts/testuser/items"
    }
    order_url = get_url("orders", "/orders")
    resp = requests.post(order_url, json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=846  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = str(uuid.uuid4())
    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    pay_url = get_url("payment-http", "/payments")
    resp = requests.post(pay_url, json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["orderId"] == order_id
    assert auth["authorised"] is True

    get_url_pay = get_url("payment-http", f"/payments/{order_id}")
    get_resp = requests.get(get_url_pay, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    auths = get_resp.json()
    assert len(auths) > 0
    assert auths[0]["orderId"] == order_id
    assert auths[0]["authorised"] is True

# --- id=847  name='Payment Authorize Declined Boundary' ---
def test_payment_authorize_declined_boundary():
    order_id = str(uuid.uuid4())
    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S"},
        "amount": 105.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    pay_url = get_url("payment-http", "/payments")
    resp = requests.post(pay_url, json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is False

    get_url_pay = get_url("payment-http", f"/payments/{order_id}")
    get_resp = requests.get(get_url_pay, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()[0]["authorised"] is False

# --- id=848  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = str(uuid.uuid4())
    shipping_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    ship_url = get_url("shipping-http", "/shipping")
    resp = requests.post(ship_url, json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

    get_url_ship = get_url("shipping-http", f"/shipping/{order_id}")
    get_resp = requests.get(get_url_ship, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["orderId"] == order_id
