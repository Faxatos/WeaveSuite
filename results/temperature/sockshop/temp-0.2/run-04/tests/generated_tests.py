# Tests generated in iteration 04
# Captured: 2026-06-29T02:30:38
# Count:    21
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=53  name='Carts Add Item And Cart' ---
def test_carts_add_item_and_get_cart():
    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": item_price}
    url = get_url("carts", f"/carts/{username}/items")
    resp = requests.post(url, json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 2
    assert cart_items[0]["unitPrice"] == item_price

# --- id=54  name='Carts Update Item And' ---
def test_carts_update_item_and_delete():
    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": item_price}
    url = get_url("carts", f"/carts/{username}/items")
    requests.post(url, json=item_payload, timeout=10)

    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": item_price}
    resp_patch = requests.patch(url, json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    item_url = get_url("carts", f"/carts/{username}/items/{item_id}")
    resp_get = requests.get(item_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 5

    resp_del = requests.delete(item_url, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_deleted = requests.get(item_url, timeout=10)
    assert resp_get_deleted.status_code == 404, f"Expected 404, got {resp_get_deleted.status_code}: {resp_get_deleted.text}"

# --- id=55  name='Carts Merge Carts Not Found' ---
def test_carts_merge_carts_not_found():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    session_id = "session_" + "".join(random.choices(string.ascii_lowercase, k=8))
    url = get_url("carts", f"/carts/{username}/merge")
    resp = requests.get(url, params={"sessionId": session_id}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=56  name='Carts Merge Carts Success' ---
def test_carts_merge_carts_success():
    cat_url = get_url("catalogue", "/catalogue")
    cat_resp = requests.get(cat_url, timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    session_id = "session_" + "".join(random.choices(string.ascii_lowercase, k=8))

    session_url = get_url("carts", f"/carts/{session_id}/items")
    requests.post(session_url, json={"itemId": item_id, "quantity": 1, "unitPrice": item_price}, timeout=10)

    merge_url = get_url("carts", f"/carts/{username}/merge")
    resp = requests.get(merge_url, params={"sessionId": session_id}, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    cust_url = get_url("carts", f"/carts/{username}/items")
    resp_get = requests.get(cust_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert any(i["itemId"] == item_id for i in cart_items)

# --- id=57  name='Catalogue All And Size' ---
def test_catalogue_get_all_and_size():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)

    size_url = get_url("catalogue", "/catalogue/size")
    resp_size = requests.get(size_url, timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

# --- id=58  name='Catalogue Item And Image' ---
def test_catalogue_get_item_and_image():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue to test")

    item = items[0]
    item_id = item["id"]

    item_url = get_url("catalogue", f"/catalogue/{item_id}")
    resp_item = requests.get(item_url, timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"

    if "imageUrl" in item and item["imageUrl"]:
        image_path = item["imageUrl"][0].split("/")[-1]
        image_url = get_url("catalogue", f"/catalogue/images/{image_path}")
        resp_img = requests.get(image_url, timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

# --- id=59  name='Catalogue Nonexistent Item' ---
def test_catalogue_get_nonexistent_item():
    url = get_url("catalogue", "/catalogue/invalid_id_12345")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=60  name='Catalogue Nonexistent Image' ---
def test_catalogue_get_nonexistent_image():
    image_url = get_url("catalogue", "/catalogue/images/invalid_image_12345.jpg")
    resp_img = requests.get(image_url, timeout=10)
    assert resp_img.status_code == 404, f"Expected 404, got {resp_img.status_code}: {resp_img.text}"

# --- id=61  name='User Register And Login' ---
def test_user_register_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    reg_url = get_url("user", "/register")
    resp_reg = requests.post(reg_url, json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    login_url = get_url("user", "/login")
    resp_login = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=62  name='User Register Conflict' ---
def test_user_register_conflict():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    reg_url = get_url("user", "/register")
    requests.post(reg_url, json=user_payload, timeout=10)

    resp_conflict = requests.post(reg_url, json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=63  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    login_url = get_url("user", "/login")
    resp = requests.get(login_url, auth=("invalid_user", "invalid_pass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=64  name='User Add Address And' ---
def test_user_add_address_and_get():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@example.com"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Test Street",
        "userID": username
    }
    addr_url = get_url("user", "/addresses")
    resp_addr = requests.post(addr_url, json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    cust_addr_url = get_url("user", f"/customers/{username}/addresses")
    resp_get = requests.get(cust_addr_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    addresses = resp_get.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

    del_url = get_url("user", f"/addresses/{addr_id}")
    resp_del = requests.delete(del_url, timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_get_after = requests.get(cust_addr_url, timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    addresses_after = resp_get_after.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses_after)

# --- id=65  name='User Add Card And' ---
def test_user_add_card_and_get():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@example.com"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_url = get_url("user", "/cards")
    resp_card = requests.post(card_url, json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    cust_card_url = get_url("user", f"/customers/{username}/cards")
    resp_get = requests.get(cust_card_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cards = resp_get.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

    created_card = next(c for c in cards if c.get("id") == card_id)
    assert created_card["longNum"].endswith("3456")
    assert "*" in created_card["longNum"]

    del_url = get_url("user", f"/cards/{card_id}")
    resp_del = requests.delete(del_url, timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_get_after = requests.get(cust_card_url, timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    cards_after = resp_get_after.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards_after)

# --- id=66  name='User Customer' ---
def test_user_delete_customer():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@example.com"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    del_url = get_url("user", f"/customers/{username}")
    resp_del1 = requests.delete(del_url, timeout=10)
    assert resp_del1.status_code == 200, f"Expected 200, got {resp_del1.status_code}: {resp_del1.text}"
    assert resp_del1.json().get("status") is True

    resp_del2 = requests.delete(del_url, timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=67  name='Orders Create Order Success' ---
def test_orders_create_order_success():
    order_id, username = _setup_order()
    if not order_id:
        pytest.skip("Could not create order")

    get_order_url = get_url("orders", f"/orders/{order_id}")
    resp_get = requests.get(get_order_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == order_id
    assert resp_get.json()["customer"]["username"] == username

# --- id=68  name='Orders Create Order Missing Cart' ---
def test_orders_create_order_missing_cart():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "EC1A", "street": "St", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_url = get_url("orders", "/orders")
    resp_order = requests.post(order_url, json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=69  name='Orders Create Order Invalid Address Uri' ---
def test_orders_create_order_invalid_address_uri():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": item_price}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format_no_colon",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_url = get_url("orders", "/orders")
    resp_order = requests.post(order_url, json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=70  name='Orders Search By Customer' ---
def test_orders_search_by_customer():
    order_id, username = _setup_order()
    if not order_id:
        pytest.skip("Could not create order")

    search_url = get_url("orders", "/orders/search/customerId")
    resp_search = requests.get(search_url, params={"custId": username}, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

    orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert len(orders) >= 1
    assert any(o["id"] == order_id for o in orders)

# --- id=71  name='Payment Authorize Success' ---
def test_payment_authorize_success():
    order_id, _ = _setup_order()
    if not order_id:
        pytest.skip("Could not create order")

    pay_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A", "street": "St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    pay_url = get_url("payment-http", "/payments")
    resp_pay = requests.post(pay_url, json=pay_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True

    get_url_pay = get_url("payment-http", f"/payments/{order_id}")
    resp_get = requests.get(get_url_pay, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 1
    assert auths[-1]["authorised"] is True

# --- id=72  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id, _ = _setup_order()
    if not order_id:
        pytest.skip("Could not create order")

    pay_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A", "street": "St"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    pay_url = get_url("payment-http", "/payments")
    resp_pay = requests.post(pay_url, json=pay_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is False

    get_url_pay = get_url("payment-http", f"/payments/{order_id}")
    resp_get = requests.get(get_url_pay, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 1
    assert auths[-1]["authorised"] is False

# --- id=73  name='Shipping And' ---
def test_shipping_post_and_get():
    order_id, _ = _setup_order()
    if not order_id:
        pytest.skip("Could not create order")

    ship_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A", "street": "St"},
        "itemCount": 3,
        "orderId": order_id
    }

    ship_url = get_url("shipping-http", "/shipping")
    resp_ship = requests.post(ship_url, json=ship_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data["orderId"] == order_id
    assert "trackingNumber" in ship_data

    get_url_ship = get_url("shipping-http", f"/shipping/{order_id}")
    resp_get = requests.get(get_url_ship, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
    assert resp_get.json()["trackingNumber"] == ship_data["trackingNumber"]
