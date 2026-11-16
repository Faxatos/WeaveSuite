# Tests generated in iteration 15
# Captured: 2026-07-05T09:31:38
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=817  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    url = get_url("user", "/register")
    resp = requests.post(url, json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    url_cust = get_url("user", f"/customers/{username}")
    resp_cust = requests.get(url_cust, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    assert resp_cust.json().get("username") == username

    url_login = get_url("user", "/login")
    resp_login = requests.get(url_login, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=818  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=819  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = f"user_{uuid.uuid4().hex[:8]}"
    url_login = get_url("user", "/login")
    resp_login = requests.get(url_login, auth=(username, "wrongpass"), timeout=10)
    assert resp_login.status_code == 401, f"Expected 401, got {resp_login.status_code}: {resp_login.text}"

# --- id=820  name='User Address And Card Lifecycle' ---
def test_user_address_and_card_lifecycle():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    url_addr_get = get_url("user", f"/addresses/{addr_id}")
    resp_addr_get = requests.get(url_addr_get, timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert resp_addr_get.json().get("city") == "London"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    url_card_get = get_url("user", f"/cards/{card_id}")
    resp_card_get = requests.get(url_card_get, timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    long_num = resp_card_get.json().get("longNum")
    assert long_num.endswith("3456")
    assert "*" in long_num

    resp_del_addr = requests.delete(url_addr_get, timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_cust_addrs = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addrs.status_code == 200, f"Expected 200, got {resp_cust_addrs.status_code}: {resp_cust_addrs.text}"
    embedded = resp_cust_addrs.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in embedded)

# --- id=821  name='User Customer Deletion' ---
def test_user_customer_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    url_cust = get_url("user", f"/customers/{username}")
    resp_del = requests.delete(url_cust, timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_del2 = requests.delete(url_cust, timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=822  name='Carts Operations' ---
def test_carts_operations():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    item_payload = {
        "itemId": "item1",
        "quantity": 2,
        "unitPrice": 10.5
    }
    url_items = get_url("carts", f"/carts/{customer_id}/items")
    resp_add = requests.post(url_items, json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get_items = requests.get(url_items, timeout=10)
    assert resp_get_items.status_code == 200, f"Expected 200, got {resp_get_items.status_code}: {resp_get_items.text}"
    items = resp_get_items.json()
    assert len(items) == 1
    assert items[0]["itemId"] == "item1"
    assert items[0]["quantity"] == 2

    item_update = {
        "itemId": "item1",
        "quantity": 5,
        "unitPrice": 10.5
    }
    resp_patch = requests.patch(url_items, json=item_update, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    url_item = get_url("carts", f"/carts/{customer_id}/items/item1")
    resp_get_item = requests.get(url_item, timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5

    resp_del_item = requests.delete(url_item, timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    resp_get_item_after = requests.get(url_item, timeout=10)
    assert resp_get_item_after.status_code == 404, f"Expected 404, got {resp_get_item_after.status_code}: {resp_get_item_after.text}"

    url_cart = get_url("carts", f"/carts/{customer_id}")
    resp_del_cart = requests.delete(url_cart, timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    resp_get_items_after = requests.get(url_items, timeout=10)
    assert resp_get_items_after.status_code == 200, f"Expected 200, got {resp_get_items_after.status_code}: {resp_get_items_after.text}"
    assert len(resp_get_items_after.json()) == 0

# --- id=823  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    item_payload = {"itemId": "item1", "quantity": 2, "unitPrice": 10.5}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)

    url_merge = get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}")
    resp_merge = requests.get(url_merge, timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) >= 1
    assert any(i["itemId"] == "item1" for i in items)

# --- id=824  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    url_merge = get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}")
    resp_merge = requests.get(url_merge, timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=825  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    url_cat = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(url_cat, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    socks = resp_cat.json()
    assert isinstance(socks, list)

    if len(socks) > 0:
        sock_id = socks[0]["id"]

        url_sock = get_url("catalogue", f"/catalogue/{sock_id}")
        resp_sock = requests.get(url_sock, timeout=10)
        assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
        assert resp_sock.json()["id"] == sock_id

        images = resp_sock.json().get("imageUrl", [])
        if images:
            image_path = images[0]
            image_name = image_path.split("/")[-1]
            url_img = get_url("catalogue", f"/catalogue/images/{image_name}")
            resp_img = requests.get(url_img, timeout=10)
            assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

    url_size = get_url("catalogue", "/catalogue/size")
    resp_size = requests.get(url_size, timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

    url_tags = get_url("catalogue", "/tags")
    resp_tags = requests.get(url_tags, timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=826  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    url_sock = get_url("catalogue", "/catalogue/invalid_sock_id")
    resp_sock = requests.get(url_sock, timeout=10)
    assert resp_sock.status_code == 404, f"Expected 404, got {resp_sock.status_code}: {resp_sock.text}"

# --- id=827  name='Orders E2e Placement' ---
def test_orders_e2e_placement():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp_cat.json()
    assert len(socks) > 0
    sock = socks[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    item_payload = {"itemId": sock_id, "quantity": 1, "unitPrice": sock_price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order["customer"]["username"] == username
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == sock_id

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auths = resp_pay.json()
    assert len(auths) >= 1
    assert auths[0]["orderId"] == order_id
    assert auths[0]["authorised"] is True

    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment["orderId"] == order_id

# --- id=828  name='Orders Placement Empty Cart' ---
def test_orders_placement_empty_cart():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=829  name='Orders Placement Invalid Uri Format' ---
def test_orders_placement_invalid_uri_format():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    item_payload = {"itemId": "item1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_format",
        "card": "/cards/invalid_format",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=830  name='Payment Authorization Repetition' ---
def test_payment_authorization_repetition():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    pay_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    resp_pay1 = requests.post(get_url("payment-http", "/payments"), json=pay_payload, timeout=10)
    assert resp_pay1.status_code == 200, f"Expected 200, got {resp_pay1.status_code}: {resp_pay1.text}"
    assert resp_pay1.json()["authorised"] is True

    resp_get1 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    assert len(resp_get1.json()) == 1

    resp_pay2 = requests.post(get_url("payment-http", "/payments"), json=pay_payload, timeout=10)
    assert resp_pay2.status_code == 200, f"Expected 200, got {resp_pay2.status_code}: {resp_pay2.text}"

    resp_get2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert len(resp_get2.json()) == 2

# --- id=831  name='Payment Authorization Amount Limit' ---
def test_payment_authorization_amount_limit():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    pay_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=pay_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json()["authorised"] is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 1
    assert resp_get.json()[0]["authorised"] is False

# --- id=832  name='Shipping Api' ---
def test_shipping_api():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    ship_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=ship_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json()["orderId"] == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
