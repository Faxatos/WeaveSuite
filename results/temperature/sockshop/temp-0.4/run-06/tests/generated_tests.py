# Tests generated in iteration 06
# Captured: 2026-06-29T19:38:07
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=336  name='Catalogue List And' ---
def test_catalogue_list_and_get():
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

# --- id=337  name='Catalogue Not Found' ---
def test_catalogue_get_not_found():
    url = get_url("catalogue", "/catalogue/invalid-id-not-found")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=338  name='User Register Login Conflict' ---
def test_user_register_login_conflict_delete():
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
    reg_resp = requests.post(reg_url, json=payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json().get("username") == username

    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    login_fail_resp = requests.get(login_url, auth=(username, "wrongpass"), timeout=10)
    assert login_fail_resp.status_code == 401, f"Expected 401, got {login_fail_resp.status_code}: {login_fail_resp.text}"

    reg_conflict_resp = requests.post(reg_url, json=payload, timeout=10)
    assert reg_conflict_resp.status_code == 409, f"Expected 409, got {reg_conflict_resp.status_code}: {reg_conflict_resp.text}"

    del_url = get_url("user", f"/customers/{username}")
    del_resp = requests.delete(del_url, timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"
    assert del_resp.json().get("status") is True

    del_again_resp = requests.delete(del_url, timeout=10)
    assert del_again_resp.status_code == 200, f"Expected 200, got {del_again_resp.status_code}: {del_again_resp.text}"
    assert del_again_resp.json().get("status") is False

# --- id=339  name='User Address And Card Lifecycle' ---
def test_user_address_and_card_lifecycle():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_url = get_url("user", "/addresses")
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Main St",
        "userID": username
    }
    addr_resp = requests.post(addr_url, json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    assert addr_id is not None

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    get_addr_resp = requests.get(get_addr_url, timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"
    assert get_addr_resp.json().get("city") == "London"

    cust_addr_url = get_url("user", f"/customers/{username}/addresses")
    cust_addr_resp = requests.get(cust_addr_url, timeout=10)
    assert cust_addr_resp.status_code == 200, f"Expected 200, got {cust_addr_resp.status_code}: {cust_addr_resp.text}"
    addresses = cust_addr_resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

    card_url = get_url("user", "/cards")
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(card_url, json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    assert card_id is not None

    get_card_url = get_url("user", f"/cards/{card_id}")
    get_card_resp = requests.get(get_card_url, timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"
    assert get_card_resp.json().get("longNum", "").endswith("3456")
    assert "*" in get_card_resp.json().get("longNum", "")

    cust_card_url = get_url("user", f"/customers/{username}/cards")
    cust_card_resp = requests.get(cust_card_url, timeout=10)
    assert cust_card_resp.status_code == 200, f"Expected 200, got {cust_card_resp.status_code}: {cust_card_resp.text}"
    cards = cust_card_resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

    del_addr_resp = requests.delete(get_addr_url, timeout=10)
    assert del_addr_resp.status_code == 200, f"Expected 200, got {del_addr_resp.status_code}: {del_addr_resp.text}"

    del_card_resp = requests.delete(get_card_url, timeout=10)
    assert del_card_resp.status_code == 200, f"Expected 200, got {del_card_resp.status_code}: {del_card_resp.text}"

# --- id=340  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    customer_id = f"cust_{random_string()}"
    item_id = f"item_{random_string()}"

    items_url = get_url("carts", f"/carts/{customer_id}/items")
    add_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    add_resp = requests.post(items_url, json=add_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    get_items_resp = requests.get(items_url, timeout=10)
    assert get_items_resp.status_code == 200, f"Expected 200, got {get_items_resp.status_code}: {get_items_resp.text}"
    items = get_items_resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 10.5}
    patch_resp = requests.patch(items_url, json=patch_payload, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    get_item_resp = requests.get(item_url, timeout=10)
    assert get_item_resp.status_code == 200, f"Expected 200, got {get_item_resp.status_code}: {get_item_resp.text}"
    assert get_item_resp.json()["quantity"] == 5

    del_item_resp = requests.delete(item_url, timeout=10)
    assert del_item_resp.status_code == 202, f"Expected 202, got {del_item_resp.status_code}: {del_item_resp.text}"

    get_del_item_resp = requests.get(item_url, timeout=10)
    assert get_del_item_resp.status_code == 404, f"Expected 404, got {get_del_item_resp.status_code}: {get_del_item_resp.text}"

    cart_url = get_url("carts", f"/carts/{customer_id}")
    del_cart_resp = requests.delete(cart_url, timeout=10)
    assert del_cart_resp.status_code == 202, f"Expected 202, got {del_cart_resp.status_code}: {del_cart_resp.text}"

# --- id=341  name='Orders Create And Search' ---
def test_orders_create_and_search():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = card_resp.json().get("id")

    item_payload = {"itemId": "sock1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_url = get_url("orders", "/orders")
    order_resp = requests.post(order_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("customer", {}).get("username") == username

    get_order_url = get_url("orders", f"/orders/{order_id}")
    get_order_resp = requests.get(get_order_url, timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    assert get_order_resp.json().get("id") == order_id

    search_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    search_resp = requests.get(search_url, timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    orders = search_resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in orders)

# --- id=342  name='Orders Create Missing Fields 406' ---
def test_orders_create_missing_fields_406():
    order_payload = {
        "customer": "/customers/someuser"
    }
    order_url = get_url("orders", "/orders")
    order_resp = requests.post(order_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=343  name='Orders Create Invalid Uri 404' ---
def test_orders_create_invalid_uri_404():
    order_payload = {
        "customer": "/customers/someuser",
        "address": "/addresses/invalid-format-no-colon",
        "card": "/cards/someuser:1234",
        "items": "/carts/someuser/items"
    }
    order_url = get_url("orders", "/orders")
    order_resp = requests.post(order_url, json=order_payload, timeout=10)
    assert order_resp.status_code == 404, f"Expected 404, got {order_resp.status_code}: {order_resp.text}"

# --- id=344  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = f"ord_{random_string()}"

    payment_payload = {
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    pay_url = get_url("payment-http", "/payments")
    pay_resp = requests.post(pay_url, json=payment_payload, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json().get("authorised") is True

    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    get_pay_resp = requests.get(get_pay_url, timeout=10)
    assert get_pay_resp.status_code == 200, f"Expected 200, got {get_pay_resp.status_code}: {get_pay_resp.text}"
    auths = get_pay_resp.json()
    assert isinstance(auths, list)
    assert len(auths) >= 1
    assert auths[-1].get("orderId") == order_id
    assert auths[-1].get("authorised") is True

# --- id=345  name='Shipping Ship And' ---
def test_shipping_ship_and_get():
    order_id = f"ord_{random_string()}"

    shipping_payload = {
        "address": {"city": "L", "country": "UK", "number": "1", "postcode": "123", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    ship_url = get_url("shipping-http", "/shipping")
    ship_resp = requests.post(ship_url, json=shipping_payload, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    assert ship_resp.json().get("orderId") == order_id

    get_ship_url = get_url("shipping-http", f"/shipping/{order_id}")
    get_ship_resp = requests.get(get_ship_url, timeout=10)
    assert get_ship_resp.status_code == 200, f"Expected 200, got {get_ship_resp.status_code}: {get_ship_resp.text}"
    assert get_ship_resp.json().get("orderId") == order_id
