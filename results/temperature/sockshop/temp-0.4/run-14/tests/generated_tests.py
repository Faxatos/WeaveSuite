# Tests generated in iteration 14
# Captured: 2026-06-30T00:20:26
# Count:    17
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=438  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = helper_create_order()
    ship_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    ship_url = get_url("shipping-http", "/shipping")
    ship_resp = requests.post(ship_url, json=ship_req, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    assert ship_resp.json().get("orderId") == order_id

    get_ship_url = get_url("shipping-http", f"/shipping/{order_id}")
    get_ship_resp = requests.get(get_ship_url, timeout=10)
    assert get_ship_resp.status_code == 200, f"Expected 200, got {get_ship_resp.status_code}: {get_ship_resp.text}"
    assert get_ship_resp.json()["orderId"] == order_id

# --- id=422  name='Catalogue Items' ---
def test_catalogue_get_items():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if items:
        item_id = items[0]["id"]
        item_url = get_url("catalogue", f"/catalogue/{item_id}")
        item_resp = requests.get(item_url, timeout=10)
        assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"
        assert item_resp.json()["id"] == item_id

# --- id=423  name='Catalogue Item Not Found' ---
def test_catalogue_get_item_not_found():
    url = get_url("catalogue", "/catalogue/non-existent-id-12345")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=424  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{random_string()}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_url = get_url("user", "/register")
    reg_resp = requests.post(reg_url, json=user_data, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

# --- id=425  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{random_string()}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_url = get_url("user", "/register")
    reg_resp = requests.post(reg_url, json=user_data, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    reg_resp2 = requests.post(reg_url, json=user_data, timeout=10)
    assert reg_resp2.status_code == 409, f"Expected 409, got {reg_resp2.status_code}: {reg_resp2.text}"

# --- id=426  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=("invalid_user", "wrong_pass"), timeout=10)
    assert login_resp.status_code == 401, f"Expected 401, got {login_resp.status_code}: {login_resp.text}"

# --- id=427  name='User Add And Address' ---
def test_user_add_and_get_address():
    username = f"user_{random_string()}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_data = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    addr_url = get_url("user", "/addresses")
    addr_resp = requests.post(addr_url, json=addr_data, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    assert addr_id is not None

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    get_addr_resp = requests.get(get_addr_url, timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"
    assert get_addr_resp.json()["city"] == "City"

    cust_addr_url = get_url("user", f"/customers/{username}/addresses")
    cust_addr_resp = requests.get(cust_addr_url, timeout=10)
    assert cust_addr_resp.status_code == 200, f"Expected 200, got {cust_addr_resp.status_code}: {cust_addr_resp.text}"
    embedded = cust_addr_resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in embedded)

# --- id=428  name='User Add And Card' ---
def test_user_add_and_get_card():
    username = f"user_{random_string()}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_url = get_url("user", "/cards")
    card_resp = requests.post(card_url, json=card_data, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    assert card_id is not None

    get_card_url = get_url("user", f"/cards/{card_id}")
    get_card_resp = requests.get(get_card_url, timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"
    assert get_card_resp.json()["expires"] == "12/25"
    assert "3456" in get_card_resp.json()["longNum"]

    cust_card_url = get_url("user", f"/customers/{username}/cards")
    cust_card_resp = requests.get(cust_card_url, timeout=10)
    assert cust_card_resp.status_code == 200, f"Expected 200, got {cust_card_resp.status_code}: {cust_card_resp.text}"
    embedded = cust_card_resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in embedded)

# --- id=429  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{random_string()}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    del_url = get_url("user", f"/customers/{username}")
    del_resp = requests.delete(del_url, timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"
    assert del_resp.json().get("status") is True

    del_resp2 = requests.delete(del_url, timeout=10)
    assert del_resp2.status_code == 200, f"Expected 200, got {del_resp2.status_code}: {del_resp2.text}"
    assert del_resp2.json().get("status") is False

# --- id=430  name='Carts Add Item' ---
def test_carts_add_get_delete_item():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200
    items = cat_resp.json()
    item_id = items[0]["id"] if items else f"item_{random_string()}"

    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    item_data = {"itemId": item_id, "quantity": 2, "unitPrice": 9.99}

    add_url = get_url("carts", f"/carts/{username}/items")
    add_resp = requests.post(add_url, json=item_data, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    get_items_url = get_url("carts", f"/carts/{username}/items")
    get_items_resp = requests.get(get_items_url, timeout=10)
    assert get_items_resp.status_code == 200, f"Expected 200, got {get_items_resp.status_code}: {get_items_resp.text}"
    assert any(i.get("itemId") == item_id for i in get_items_resp.json())

    get_item_url = get_url("carts", f"/carts/{username}/items/{item_id}")
    get_item_resp = requests.get(get_item_url, timeout=10)
    assert get_item_resp.status_code == 200, f"Expected 200, got {get_item_resp.status_code}: {get_item_resp.text}"
    assert get_item_resp.json()["quantity"] == 2

    del_item_url = get_url("carts", f"/carts/{username}/items/{item_id}")
    del_item_resp = requests.delete(del_item_url, timeout=10)
    assert del_item_resp.status_code == 202, f"Expected 202, got {del_item_resp.status_code}: {del_item_resp.text}"

    get_item_resp2 = requests.get(get_item_url, timeout=10)
    assert get_item_resp2.status_code == 404, f"Expected 404, got {get_item_resp2.status_code}: {get_item_resp2.text}"

# --- id=431  name='Carts Item' ---
def test_carts_patch_item():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200
    items = cat_resp.json()
    item_id = items[0]["id"] if items else f"item_{random_string()}"

    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    item_data = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    add_url = get_url("carts", f"/carts/{username}/items")
    requests.post(add_url, json=item_data, timeout=10)

    patch_data = {"itemId": item_id, "quantity": 5, "unitPrice": 5.0}
    patch_url = get_url("carts", f"/carts/{username}/items")
    patch_resp = requests.patch(patch_url, json=patch_data, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_item_url = get_url("carts", f"/carts/{username}/items/{item_id}")
    get_item_resp = requests.get(get_item_url, timeout=10)
    assert get_item_resp.status_code == 200, f"Expected 200, got {get_item_resp.status_code}: {get_item_resp.text}"
    assert get_item_resp.json()["quantity"] == 5

# --- id=432  name='Orders Create And' ---
def test_orders_create_and_get():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    item_id = items[0]["id"] if items else f"item_{random_string()}"

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_url = get_url("orders", "/orders")
    order_resp = requests.post(order_url, json=order_req, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data.get("id")
    assert order_id is not None

    get_order_url = get_url("orders", f"/orders/{order_id}")
    get_order_resp = requests.get(get_order_url, timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    assert get_order_resp.json()["id"] == order_id

    search_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    search_resp = requests.get(search_url, timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    orders_list = search_resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in orders_list)

# --- id=433  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:1"
    }
    order_url = get_url("orders", "/orders")
    order_resp = requests.post(order_url, json=order_req, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=434  name='Orders Create Bad Composite Id' ---
def test_orders_create_bad_composite_id():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_format",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    order_url = get_url("orders", "/orders")
    order_resp = requests.post(order_url, json=order_req, timeout=10)
    assert order_resp.status_code == 404, f"Expected 404, got {order_resp.status_code}: {order_resp.text}"

# --- id=435  name='Orders Not Found' ---
def test_orders_get_not_found():
    url = get_url("orders", "/orders/non-existent-order-id")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=436  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = helper_create_order()
    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    pay_url = get_url("payment-http", "/payments")
    pay_resp = requests.post(pay_url, json=payment_req, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json().get("authorised") is True

    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    get_pay_resp = requests.get(get_pay_url, timeout=10)
    assert get_pay_resp.status_code == 200, f"Expected 200, got {get_pay_resp.status_code}: {get_pay_resp.text}"
    auths = get_pay_resp.json()
    assert isinstance(auths, list)
    assert len(auths) > 0
    assert auths[-1]["orderId"] == order_id

# --- id=437  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = helper_create_order()
    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    pay_url = get_url("payment-http", "/payments")
    pay_resp = requests.post(pay_url, json=payment_req, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json().get("authorised") is False
