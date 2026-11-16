# Tests generated in iteration 04
# Captured: 2026-06-20T21:07:03
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=981  name='Catalogue Items' ---
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

# --- id=982  name='Catalogue Item Not Found' ---
def test_catalogue_get_item_not_found():
    item_id = f"invalid-{uuid.uuid4()}"
    url = get_url("catalogue", f"/catalogue/{item_id}")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=983  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user-{uuid.uuid4()}"
    password = "password123"
    email = f"{username}@example.com"

    reg_url = get_url("user", "/register")
    reg_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    reg_resp = requests.post(reg_url, json=reg_payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json().get("username") == username

    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

# --- id=984  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user-{uuid.uuid4()}"
    password = "password123"
    reg_url = get_url("user", "/register")
    reg_payload = {"username": username, "password": password, "email": f"{username}@example.com"}

    resp1 = requests.post(reg_url, json=reg_payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    resp2 = requests.post(reg_url, json=reg_payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=985  name='User Add Address And' ---
def test_user_add_address_and_get():
    username = f"user-{uuid.uuid4()}"
    reg_url = get_url("user", "/register")
    requests.post(reg_url, json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    addr_url = get_url("user", "/addresses")
    addr_payload = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    addr_resp = requests.post(addr_url, json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    get_addr_resp = requests.get(get_addr_url, timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"
    assert get_addr_resp.json().get("city") == "City"

# --- id=986  name='User Add Card And' ---
def test_user_add_card_and_get():
    username = f"user-{uuid.uuid4()}"
    reg_url = get_url("user", "/register")
    requests.post(reg_url, json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    card_url = get_url("user", "/cards")
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(card_url, json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    get_card_url = get_url("user", f"/cards/{card_id}")
    get_card_resp = requests.get(get_card_url, timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"
    assert get_card_resp.json().get("longNum", "").endswith("3456")

# --- id=987  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    customer_id = f"cust-{uuid.uuid4()}"
    item_id = f"item-{uuid.uuid4()}"

    items_url = get_url("carts", f"/carts/{customer_id}/items")
    payload = {"itemId": item_id, "quantity": 2, "unitPrice": 9.99}

    post_resp = requests.post(items_url, json=payload, timeout=10)
    assert post_resp.status_code == 201, f"Expected 201, got {post_resp.status_code}: {post_resp.text}"

    get_resp = requests.get(items_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert any(item.get("itemId") == item_id and item.get("quantity") == 2 for item in items)

    item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_item_resp = requests.get(item_url, timeout=10)
    assert get_item_resp.status_code == 200, f"Expected 200, got {get_item_resp.status_code}: {get_item_resp.text}"
    assert get_item_resp.json().get("itemId") == item_id

# --- id=988  name='Carts Update Item' ---
def test_carts_update_item():
    customer_id = f"cust-{uuid.uuid4()}"
    item_id = f"item-{uuid.uuid4()}"

    items_url = get_url("carts", f"/carts/{customer_id}/items")
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    requests.post(items_url, json=payload, timeout=10)

    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 5.0}
    patch_resp = requests.patch(items_url, json=patch_payload, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_resp = requests.get(item_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("quantity") == 5

# --- id=989  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust-{uuid.uuid4()}"
    item_id = f"item-{uuid.uuid4()}"

    items_url = get_url("carts", f"/carts/{customer_id}/items")
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    requests.post(items_url, json=payload, timeout=10)

    item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    del_resp = requests.delete(item_url, timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(item_url, timeout=10)
    assert get_resp.status_code == 404, f"Expected 404, got {get_resp.status_code}: {get_resp.text}"

# --- id=990  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust-{uuid.uuid4()}"
    session_id = f"sess-{uuid.uuid4()}"

    merge_url = get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}")
    resp = requests.get(merge_url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=991  name='Orders Create And' ---
def test_orders_create_and_get():
    username = f"user-{uuid.uuid4()}"
    reg_url = get_url("user", "/register")
    requests.post(reg_url, json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    addr_url = get_url("user", "/addresses")
    addr_resp = requests.post(addr_url, json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_url = get_url("user", "/cards")
    card_resp = requests.post(card_url, json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cart_url = get_url("carts", f"/carts/{username}/items")
    requests.post(cart_url, json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_url = get_url("orders", "/orders")
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    order_resp = requests.post(order_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    assert "id" in order_data
    created_order_id = order_data["id"]

    get_order_url = get_url("orders", f"/orders/{created_order_id}")
    get_resp = requests.get(get_order_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("id") == created_order_id

# --- id=992  name='Orders Create Missing Cart' ---
def test_orders_create_missing_cart():
    username = f"user-{uuid.uuid4()}"
    reg_url = get_url("user", "/register")
    requests.post(reg_url, json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    addr_url = get_url("user", "/addresses")
    addr_resp = requests.post(addr_url, json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_url = get_url("user", "/cards")
    card_resp = requests.post(card_url, json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    order_url = get_url("orders", "/orders")
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    order_resp = requests.post(order_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=993  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = f"order-{uuid.uuid4()}"
    pay_url = get_url("payment-http", "/payments")
    pay_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    post_resp = requests.post(pay_url, json=pay_payload, timeout=10)
    assert post_resp.status_code == 200, f"Expected 200, got {post_resp.status_code}: {post_resp.text}"
    auth_data = post_resp.json()
    assert auth_data.get("authorised") is True

    get_url_pay = get_url("payment-http", f"/payments/{order_id}")
    get_resp = requests.get(get_url_pay, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    auths = get_resp.json()
    assert len(auths) >= 1
    assert auths[-1].get("orderId") == order_id
    assert auths[-1].get("authorised") is True

# --- id=994  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = f"order-{uuid.uuid4()}"
    pay_url = get_url("payment-http", "/payments")
    pay_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    post_resp = requests.post(pay_url, json=pay_payload, timeout=10)
    assert post_resp.status_code == 200, f"Expected 200, got {post_resp.status_code}: {post_resp.text}"
    auth_data = post_resp.json()
    assert auth_data.get("authorised") is False

    get_url_pay = get_url("payment-http", f"/payments/{order_id}")
    get_resp = requests.get(get_url_pay, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    auths = get_resp.json()
    assert len(auths) >= 1
    assert auths[-1].get("authorised") is False

# --- id=995  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = f"order-{uuid.uuid4()}"
    ship_url = get_url("shipping-http", "/shipping")
    ship_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 2,
        "orderId": order_id
    }

    post_resp = requests.post(ship_url, json=ship_payload, timeout=10)
    assert post_resp.status_code == 200, f"Expected 200, got {post_resp.status_code}: {post_resp.text}"
    ship_data = post_resp.json()
    assert ship_data.get("orderId") == order_id

    get_url_ship = get_url("shipping-http", f"/shipping/{order_id}")
    get_resp = requests.get(get_url_ship, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("orderId") == order_id
