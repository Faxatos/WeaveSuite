# Tests generated in iteration 10
# Captured: 2026-06-03T22:55:58
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=68  name='Carts Add Item' ---
def test_carts_add_get_delete_item():
    cat_url = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(cat_url, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    socks = resp_cat.json()
    assert len(socks) > 0, "No items found in catalogue"
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    username = f"cartuser_{uuid.uuid4().hex[:8]}"
    resp_reg = requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com",
        "firstName": "Cart", "lastName": "User"
    }, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    customer_id = username

    add_url = get_url("carts", f"/carts/{customer_id}/items")
    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": unit_price}
    resp = requests.post(add_url, json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    get_url_items = get_url("carts", f"/carts/{customer_id}/items")
    resp_get = requests.get(get_url_items, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i.get("itemId") == item_id for i in items), "Item not found in cart"

    del_item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_del = requests.delete(del_item_url, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_item = requests.get(del_item_url, timeout=10)
    assert resp_get_item.status_code == 404, f"Expected 404, got {resp_get_item.status_code}: {resp_get_item.text}"

    del_cart_url = get_url("carts", f"/carts/{customer_id}")
    resp_del_cart = requests.delete(del_cart_url, timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    resp_get_cart_after = requests.get(del_cart_url, timeout=10)
    assert resp_get_cart_after.status_code == 200, f"Expected 200, got {resp_get_cart_after.status_code}: {resp_get_cart_after.text}"

# --- id=69  name='Catalogue Socks And Tags' ---
def test_catalogue_get_socks_and_tags():
    cat_url = get_url("catalogue", "/catalogue")
    resp = requests.get(cat_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)

    if socks:
        sock_id = socks[0]["id"]
        sock_url = get_url("catalogue", f"/catalogue/{sock_id}")
        resp_sock = requests.get(sock_url, timeout=10)
        assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
        assert resp_sock.json().get("id") == sock_id

    tags_url = get_url("catalogue", "/tags")
    resp_tags = requests.get(tags_url, timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags_data = resp_tags.json()
    tags = tags_data.get("tags", [])

    if tags:
        tag = tags[0]
        size_url = get_url("catalogue", f"/catalogue/size?tags={tag}")
        resp_size = requests.get(size_url, timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        assert "size" in resp_size.json()

# --- id=70  name='User Register Login Add Address Card' ---
def test_user_register_login_add_address_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    reg_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(reg_url, json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    assert resp_reg.json().get("id") == username

    get_user_url = get_url("user", f"/customers/{username}")
    resp_get_user = requests.get(get_user_url, timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    login_url = get_url("user", "/login")
    resp_login = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    addr_url = get_url("user", "/addresses")
    addr_payload = {
        "street": "123 Main St",
        "number": "42",
        "country": "USA",
        "city": "Anytown",
        "postcode": "12345",
        "userID": username
    }
    resp_addr = requests.post(addr_url, json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    resp_get_addr = requests.get(get_addr_url, timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json().get("city") == "Anytown"

    card_url = get_url("user", "/cards")
    card_payload = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(card_url, json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    get_card_url = get_url("user", f"/cards/{card_id}")
    resp_get_card = requests.get(get_card_url, timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert "longNum" in resp_get_card.json()

    del_user_url = get_url("user", f"/customers/{username}")
    resp_del_user = requests.delete(del_user_url, timeout=10)
    assert resp_del_user.status_code == 200, f"Expected 200, got {resp_del_user.status_code}: {resp_del_user.text}"

    resp_get_all = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_get_all.status_code == 200, f"Expected 200, got {resp_get_all.status_code}: {resp_get_all.text}"
    customers = resp_get_all.json().get("_embedded", {}).get("customer", [])
    assert not any(c.get("username") == username for c in customers)

# --- id=71  name='Orders Create And Search' ---
def test_orders_create_and_search():
    username, addr_id, card_id = setup_user_and_cart()

    order_url = get_url("orders", "/orders")
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(order_url, json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("payment", {}).get("authorised") is True

    get_order_url = get_url("orders", f"/orders/{order_id}")
    resp_get_order = requests.get(get_order_url, timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json().get("id") == order_id

    search_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    resp_search = requests.get(search_url, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded = resp_search.json().get("_embedded", {})
    customer_orders = embedded.get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders)

# --- id=72  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = setup_order()

    pay_url = get_url("payment-http", "/payments")
    pay_payload = {
        "orderId": order_id,
        "amount": 50.00,
        "customer": {"firstName": "Pay", "lastName": "User"},
        "address": {"street": "123 Main St", "number": "42", "country": "USA", "city": "Anytown", "postcode": "12345"},
        "card": {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    }
    resp_pay = requests.post(pay_url, json=pay_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True

    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    resp_get_pay = requests.get(get_pay_url, timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    auths = resp_get_pay.json()
    assert isinstance(auths, list)
    assert len(auths) > 0
    assert any(a.get("orderId") == order_id for a in auths)

# --- id=73  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = setup_order()

    ship_url = get_url("shipping-http", "/shipping")
    ship_payload = {
        "orderId": order_id,
        "itemCount": 1,
        "address": {"street": "123 Main St", "number": "42", "country": "USA", "city": "Anytown", "postcode": "12345"}
    }
    resp_ship = requests.post(ship_url, json=ship_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id

    get_ship_url = get_url("shipping-http", f"/shipping/{order_id}")
    resp_get_ship = requests.get(get_ship_url, timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    assert resp_get_ship.json().get("orderId") == order_id
