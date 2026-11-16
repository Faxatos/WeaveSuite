# Tests generated in iteration 05
# Captured: 2026-06-20T21:47:05
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1011  name='Shipping Ship Order' ---
def test_shipping_ship_order():
    order_id = f"order_{generate_id()}"
    url = get_url("shipping-http", "/shipping")
    payload = {
        "address": {
            "city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"
        },
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id

    get_url_ship = get_url("shipping-http", f"/shipping/{order_id}")
    get_resp = requests.get(get_url_ship, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("orderId") == order_id

# --- id=996  name='Catalogue Items' ---
def test_catalogue_get_items():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if items:
        item_id = items[0].get("id")
        item_url = get_url("catalogue", f"/catalogue/{item_id}")
        item_resp = requests.get(item_url, timeout=10)
        assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"
        assert item_resp.json().get("id") == item_id

# --- id=997  name='Catalogue Item Not Found' ---
def test_catalogue_get_item_not_found():
    item_id = f"invalid-{generate_id()}"
    url = get_url("catalogue", f"/catalogue/{item_id}")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=998  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{generate_id()}"
    password = "password123"
    register_url = get_url("user", "/register")
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(register_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    customer_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(customer_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

# --- id=999  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{generate_id()}"
    register_url = get_url("user", "/register")
    payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp1 = requests.post(register_url, json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    resp2 = requests.post(register_url, json=payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1000  name='User Add Address' ---
def test_user_add_address():
    username = f"user_{generate_id()}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    addr_url = get_url("user", "/addresses")
    payload = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    resp = requests.post(addr_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    assert addr_id is not None

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    get_resp = requests.get(get_addr_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("city") == "City"

# --- id=1001  name='User Add Card' ---
def test_user_add_card():
    username = f"user_{generate_id()}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    card_url = get_url("user", "/cards")
    payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(card_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    get_card_url = get_url("user", f"/cards/{card_id}")
    get_resp = requests.get(get_card_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("expires") == "12/25"

# --- id=1002  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{generate_id()}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    del_url = get_url("user", f"/customers/{username}")
    resp = requests.delete(del_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    get_resp = requests.get(del_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("firstName") is None

# --- id=1003  name='Carts Add Item' ---
def test_carts_add_item():
    customer_id = f"cust_{generate_id()}"
    item_id = f"item_{generate_id()}"
    url = get_url("carts", f"/carts/{customer_id}/items")
    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    get_url_item = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_resp = requests.get(get_url_item, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("quantity") == 2

# --- id=1004  name='Carts Update Item' ---
def test_carts_update_item():
    customer_id = f"cust_{generate_id()}"
    item_id = f"item_{generate_id()}"
    url = get_url("carts", f"/carts/{customer_id}/items")
    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    post_resp = requests.post(url, json=payload, timeout=10)
    assert post_resp.status_code == 201, f"Expected 201, got {post_resp.status_code}: {post_resp.text}"
    get_url_item = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_resp1 = requests.get(get_url_item, timeout=10)
    assert get_resp1.status_code == 200, f"Expected 200, got {get_resp1.status_code}: {get_resp1.text}"

    patch_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 10.5
    }
    patch_resp = requests.patch(url, json=patch_payload, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_resp2 = requests.get(get_url_item, timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    assert get_resp2.json().get("quantity") == 5

# --- id=1005  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{generate_id()}"
    item_id = f"item_{generate_id()}"
    url = get_url("carts", f"/carts/{customer_id}/items")
    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    post_resp = requests.post(url, json=payload, timeout=10)
    assert post_resp.status_code == 201, f"Expected 201, got {post_resp.status_code}: {post_resp.text}"
    get_url_item = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_resp1 = requests.get(get_url_item, timeout=10)
    assert get_resp1.status_code == 200, f"Expected 200, got {get_resp1.status_code}: {get_resp1.text}"

    del_resp = requests.delete(get_url_item, timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp2 = requests.get(get_url_item, timeout=10)
    assert get_resp2.status_code == 404, f"Expected 404, got {get_resp2.status_code}: {get_resp2.text}"

# --- id=1006  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{generate_id()}"
    session_id = f"sess_{generate_id()}"
    url = get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1007  name='Orders Create Order' ---
def test_orders_create_order():
    username = f"user_{generate_id()}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    addr_resp = requests.post(get_url("user", "/addresses"), json={
        "city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username
    }, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    get_addr_resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"

    card_resp = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    get_card_resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"

    item_id = f"item_{generate_id()}"
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item_id, "quantity": 1, "unitPrice": 10.0
    }, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"
    get_cart_resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get_cart_resp.status_code == 200, f"Expected 200, got {get_cart_resp.status_code}: {get_cart_resp.text}"

    order_url = get_url("orders", "/orders")
    payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(order_url, json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")
    assert order_id is not None

    get_order_url = get_url("orders", f"/orders/{order_id}")
    get_resp = requests.get(get_order_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("id") == order_id

# --- id=1008  name='Orders Create Order Missing Fields' ---
def test_orders_create_order_missing_fields():
    username = f"user_{generate_id()}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    order_url = get_url("orders", "/orders")
    payload = {
        "customer": f"/customers/{username}"
    }
    resp = requests.post(order_url, json=payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=1009  name='Orders Create Order Invalid Uri' ---
def test_orders_create_order_invalid_uri():
    username = f"user_{generate_id()}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    order_url = get_url("orders", "/orders")
    payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_format",
        "card": "/cards/invalid_format",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(order_url, json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1010  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = f"order_{generate_id()}"
    url = get_url("payment-http", "/payments")
    payload = {
        "address": {
            "city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123", "expires": "12/25", "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "First", "lastName": "Last"
        },
        "orderId": order_id
    }
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    get_url_pay = get_url("payment-http", f"/payments/{order_id}")
    get_resp = requests.get(get_url_pay, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    auths = get_resp.json()
    assert isinstance(auths, list)
    assert len(auths) > 0
    assert auths[-1].get("orderId") == order_id
