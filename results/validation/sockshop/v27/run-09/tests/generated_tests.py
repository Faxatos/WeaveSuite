# Tests generated in iteration 09
# Captured: 2026-06-21T00:20:03
# Count:    18
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1048  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0
    sock_id = socks[0]["id"]

    sock_url = get_url("catalogue", f"/catalogue/{sock_id}")
    sock_resp = requests.get(sock_url, timeout=10)
    assert sock_resp.status_code == 200, f"Expected 200, got {sock_resp.status_code}: {sock_resp.text}"
    assert sock_resp.json()["id"] == sock_id

# --- id=1049  name='Catalogue Sock Not Found' ---
def test_catalogue_get_sock_not_found():
    sock_id = f"invalid-{uuid.uuid4()}"
    sock_url = get_url("catalogue", f"/catalogue/{sock_id}")
    sock_resp = requests.get(sock_url, timeout=10)
    assert sock_resp.status_code == 404, f"Expected 404, got {sock_resp.status_code}: {sock_resp.text}"

# --- id=1050  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user-{uuid.uuid4()}"
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

    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

# --- id=1051  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user-{uuid.uuid4()}"
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

    reg_resp2 = requests.post(reg_url, json=user_data, timeout=10)
    assert reg_resp2.status_code == 409, f"Expected 409, got {reg_resp2.status_code}: {reg_resp2.text}"

# --- id=1052  name='User Add And Address' ---
def test_user_add_and_get_address():
    username = f"user-{uuid.uuid4()}"
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

    addr_id = addr_resp.json()["id"]

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    get_resp = requests.get(get_addr_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["city"] == "City"

# --- id=1053  name='User Add And Card' ---
def test_user_add_and_get_card():
    username = f"user-{uuid.uuid4()}"
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_url = get_url("user", "/cards")
    card_resp = requests.post(card_url, json=card_data, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"

    card_id = card_resp.json()["id"]

    get_card_url = get_url("user", f"/cards/{card_id}")
    get_resp = requests.get(get_card_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["expires"] == "12/25"
    assert "123456789012" not in get_resp.json()["longNum"]

# --- id=1054  name='User Customer' ---
def test_user_delete_customer():
    username = f"user-{uuid.uuid4()}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    reg_resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    del_url = get_url("user", f"/customers/{username}")
    del_resp = requests.delete(del_url, timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"
    assert del_resp.json()["status"] is True

    get_resp = requests.get(del_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("firstName") is None

# --- id=1055  name='Carts Add And Item' ---
def test_carts_add_and_get_item():
    customer_id = f"cust-{uuid.uuid4()}"
    item_id = f"item-{uuid.uuid4()}"
    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 9.99
    }
    items_url = get_url("carts", f"/carts/{customer_id}/items")
    add_resp = requests.post(items_url, json=item_data, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    get_item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_resp = requests.get(get_item_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["itemId"] == item_id
    assert get_resp.json()["quantity"] == 2

# --- id=1056  name='Carts Update Item' ---
def test_carts_update_item():
    customer_id = f"cust-{uuid.uuid4()}"
    item_id = f"item-{uuid.uuid4()}"
    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 9.99
    }
    items_url = get_url("carts", f"/carts/{customer_id}/items")
    add_resp = requests.post(items_url, json=item_data, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    update_data = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 9.99
    }
    update_resp = requests.patch(items_url, json=update_data, timeout=10)
    assert update_resp.status_code == 202, f"Expected 202, got {update_resp.status_code}: {update_resp.text}"

    get_item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_resp = requests.get(get_item_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["quantity"] == 5

# --- id=1057  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust-{uuid.uuid4()}"
    item_id = f"item-{uuid.uuid4()}"
    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 9.99
    }
    items_url = get_url("carts", f"/carts/{customer_id}/items")
    add_resp = requests.post(items_url, json=item_data, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    del_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    del_resp = requests.delete(del_url, timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(del_url, timeout=10)
    assert get_resp.status_code == 404, f"Expected 404, got {get_resp.status_code}: {get_resp.text}"

# --- id=1058  name='Carts Merge Carts' ---
def test_carts_merge_carts():
    session_id = f"sess-{uuid.uuid4()}"
    customer_id = f"cust-{uuid.uuid4()}"
    item_id = f"item-{uuid.uuid4()}"

    item_data = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    sess_items_url = get_url("carts", f"/carts/{session_id}/items")
    add_resp = requests.post(sess_items_url, json=item_data, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    merge_url = get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}")
    merge_resp = requests.get(merge_url, timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    cust_items_url = get_url("carts", f"/carts/{customer_id}/items")
    get_resp = requests.get(cust_items_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert len(items) > 0
    assert items[0]["itemId"] == item_id

# --- id=1059  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    session_id = f"sess-{uuid.uuid4()}"
    customer_id = f"cust-{uuid.uuid4()}"
    merge_url = get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}")
    merge_resp = requests.get(merge_url, timeout=10)
    assert merge_resp.status_code == 404, f"Expected 404, got {merge_resp.status_code}: {merge_resp.text}"

# --- id=1060  name='Orders Place And Order' ---
def test_orders_place_and_get_order():
    username = f"user-{uuid.uuid4()}"

    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    reg_resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    addr_data = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    item_data = {"itemId": "sock1", "quantity": 2, "unitPrice": 10.0}
    item_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert item_resp.status_code == 201, f"Expected 201, got {item_resp.status_code}: {item_resp.text}"

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_url = get_url("orders", "/orders")
    order_resp = requests.post(order_url, json=order_req, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"

    order_id = order_resp.json()["id"]

    get_order_url = get_url("orders", f"/orders/{order_id}")
    get_resp = requests.get(get_order_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["id"] == order_id
    assert get_resp.json()["customer"]["username"] == username

# --- id=1061  name='Orders Place Order Missing Fields' ---
def test_orders_place_order_missing_fields():
    order_req = {
        "customer": "/customers/someuser"
    }
    order_url = get_url("orders", "/orders")
    order_resp = requests.post(order_url, json=order_req, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=1062  name='Orders Place Order Invalid Uri' ---
def test_orders_place_order_invalid_uri():
    order_req = {
        "customer": "/customers/someuser",
        "address": "/addresses/invalid-format",
        "card": "/cards/invalid-format",
        "items": "/carts/someuser/items"
    }
    order_url = get_url("orders", "/orders")
    order_resp = requests.post(order_url, json=order_req, timeout=10)
    assert order_resp.status_code == 404, f"Expected 404, got {order_resp.status_code}: {order_resp.text}"

# --- id=1063  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = f"order-{uuid.uuid4()}"
    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }
    pay_url = get_url("payment-http", "/payments")
    pay_resp = requests.post(pay_url, json=payment_req, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json()["authorised"] is True

    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    get_resp = requests.get(get_pay_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    auths = get_resp.json()
    assert len(auths) > 0
    assert auths[0]["orderId"] == order_id

# --- id=1064  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = f"order-{uuid.uuid4()}"
    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }
    pay_url = get_url("payment-http", "/payments")
    pay_resp = requests.post(pay_url, json=payment_req, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json()["authorised"] is False

# --- id=1065  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = f"order-{uuid.uuid4()}"
    ship_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    ship_url = get_url("shipping-http", "/shipping")
    ship_resp = requests.post(ship_url, json=ship_req, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    assert ship_resp.json()["orderId"] == order_id

    get_ship_url = get_url("shipping-http", f"/shipping/{order_id}")
    get_resp = requests.get(get_ship_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json()["orderId"] == order_id
