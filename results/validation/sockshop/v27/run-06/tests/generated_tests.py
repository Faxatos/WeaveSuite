# Tests generated in iteration 06
# Captured: 2026-06-20T22:29:29
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1012  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    reg_url = get_url("user", "/register")
    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(reg_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    cust_url = get_url("user", f"/customers/{username}")
    resp_get = requests.get(cust_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    login_url = get_url("user", "/login")
    resp_login = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    data = resp_get.json()
    assert data.get("username") == username
    assert data.get("email") == email

# --- id=1013  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{random_string()}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_url = get_url("user", "/register")
    resp1 = requests.post(reg_url, json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    resp2 = requests.post(reg_url, json=payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1014  name='User Add Address' ---
def test_user_add_address():
    username = f"user_{random_string()}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    addr_url = get_url("user", "/addresses")
    payload = {
        "city": "Cityville",
        "country": "Countryland",
        "number": "42",
        "postcode": "12345",
        "street": "Main St",
        "userID": username
    }
    resp = requests.post(addr_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    assert addr_id is not None

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    resp_get = requests.get(get_addr_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("city") == "Cityville"
    assert data.get("postcode") == "12345"

# --- id=1015  name='User Add Card' ---
def test_user_add_card():
    username = f"user_{random_string()}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com"}, timeout=10)
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
    resp_get = requests.get(get_card_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("expires") == "12/25"
    assert "3456" in data.get("longNum")

# --- id=1016  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{random_string()}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    del_url = get_url("user", f"/customers/{username}")
    resp = requests.delete(del_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp_get = requests.get(del_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp2 = requests.delete(del_url, timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    assert resp2.json().get("status") is False

# --- id=1017  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    customer_id = f"cust_{random_string()}"
    item_id = f"item_{random_string()}"

    items_url = get_url("carts", f"/carts/{customer_id}/items")
    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.5
    }
    resp = requests.post(items_url, json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_get = requests.get(item_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("itemId") == item_id
    assert data.get("quantity") == 2
    assert data.get("unitPrice") == 15.5

# --- id=1018  name='Carts Update Item' ---
def test_carts_update_item():
    customer_id = f"cust_{random_string()}"
    item_id = f"item_{random_string()}"

    items_url = get_url("carts", f"/carts/{customer_id}/items")
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    post_resp = requests.post(items_url, json=payload, timeout=10)
    assert post_resp.status_code == 201, f"Expected 201, got {post_resp.status_code}: {post_resp.text}"

    item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_resp = requests.get(item_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 10.0}
    resp = requests.patch(items_url, json=patch_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(item_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 5

# --- id=1019  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{random_string()}"
    item_id = f"item_{random_string()}"

    items_url = get_url("carts", f"/carts/{customer_id}/items")
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    post_resp = requests.post(items_url, json=payload, timeout=10)
    assert post_resp.status_code == 201, f"Expected 201, got {post_resp.status_code}: {post_resp.text}"

    item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_resp = requests.get(item_url, timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

    resp = requests.delete(item_url, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(item_url, timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=1020  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{random_string()}"
    session_id = f"sess_{random_string()}"
    merge_url = get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}")
    resp = requests.get(merge_url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1021  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    cat_url = get_url("catalogue", "/catalogue")
    resp = requests.get(cat_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    if socks and isinstance(socks, list):
        sock_id = socks[0].get("id")
        if sock_id:
            sock_url = get_url("catalogue", f"/catalogue/{sock_id}")
            resp2 = requests.get(sock_url, timeout=10)
            assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
            assert resp2.json().get("id") == sock_id

# --- id=1022  name='Catalogue Sock Not Found' ---
def test_catalogue_get_sock_not_found():
    sock_id = f"invalid_{random_string()}"
    sock_url = get_url("catalogue", f"/catalogue/{sock_id}")
    resp = requests.get(sock_url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1023  name='Orders Create Order' ---
def test_orders_create_order():
    username = f"user_{random_string()}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"
    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S", "userID": username}, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    get_addr_resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    get_card_resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"

    item_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item1", "quantity": 2, "unitPrice": 10.0}, timeout=10)
    assert item_resp.status_code == 201, f"Expected 201, got {item_resp.status_code}: {item_resp.text}"
    get_item_resp = requests.get(get_url("carts", f"/carts/{username}/items/item1"), timeout=10)
    assert get_item_resp.status_code == 200, f"Expected 200, got {get_item_resp.status_code}: {get_item_resp.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    orders_url = get_url("orders", "/orders")
    resp = requests.post(orders_url, json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_data = resp.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("total") == 20.0

    get_order_url = get_url("orders", f"/orders/{order_id}")
    resp_get = requests.get(get_order_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("id") == order_id

# --- id=1024  name='Orders Create Order Missing Fields' ---
def test_orders_create_order_missing_fields():
    orders_url = get_url("orders", "/orders")
    resp = requests.post(orders_url, json={}, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=1025  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = f"order_{random_string()}"
    pay_url = get_url("payment-http", "/payments")
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(pay_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    resp_get = requests.get(get_pay_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert isinstance(auths, list)
    assert len(auths) >= 1
    assert auths[-1].get("orderId") == order_id

# --- id=1026  name='Shipping Ship Order' ---
def test_shipping_ship_order():
    order_id = f"order_{random_string()}"
    ship_url = get_url("shipping-http", "/shipping")
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(ship_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    ship_data = resp.json()
    assert ship_data.get("orderId") == order_id
    assert ship_data.get("carrier") is not None

    get_ship_url = get_url("shipping-http", f"/shipping/{order_id}")
    resp_get = requests.get(get_ship_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
