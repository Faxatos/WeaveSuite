# Tests generated in iteration 09
# Captured: 2026-06-03T22:12:31
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=57  name='Carts Add And Items' ---
def test_carts_add_and_get_items():
    cat_url = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(cat_url, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]

    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@example.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 15.5}
    post_url = get_url("carts", f"/carts/{username}/items")
    resp = requests.post(post_url, json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    get_url_items = get_url("carts", f"/carts/{username}/items")
    resp_get = requests.get(get_url_items, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert any(i.get("itemId") == item_id for i in resp_get.json())

# --- id=58  name='Carts Item' ---
def test_carts_delete_item():
    cat_url = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(cat_url, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]

    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pw", "email": f"{username}@example.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    post_url = get_url("carts", f"/carts/{username}/items")
    resp_post = requests.post(post_url, json=item_payload, timeout=10)
    assert resp_post.status_code == 201, f"Expected 201, got {resp_post.status_code}: {resp_post.text}"

    resp_get_items = requests.get(post_url, timeout=10)
    assert resp_get_items.status_code == 200, f"Expected 200, got {resp_get_items.status_code}: {resp_get_items.text}"

    delete_url = get_url("carts", f"/carts/{username}/items/{item_id}")
    resp_del = requests.delete(delete_url, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(delete_url, timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=59  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0

    item_id = items[0]["id"]
    item_url = get_url("catalogue", f"/catalogue/{item_id}")
    resp_item = requests.get(item_url, timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json().get("id") == item_id

# --- id=60  name='Catalogue Tags' ---
def test_catalogue_get_tags():
    url = get_url("catalogue", "/tags")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=61  name='User Register And Login' ---
def test_user_register_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    reg_url = get_url("user", "/register")
    resp_reg = requests.post(reg_url, json=payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    user_url = get_url("user", f"/customers/{username}")
    resp_user = requests.get(user_url, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    login_url = get_url("user", "/login")
    resp_login = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=62  name='User Add Address' ---
def test_user_add_address():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    reg_url = get_url("user", "/register")
    resp_reg = requests.post(reg_url, json={"username": username, "password": "pw", "email": f"{username}@example.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1",
        "street": "Baker St",
        "userID": username
    }
    addr_url = get_url("user", "/addresses")
    resp_addr = requests.post(addr_url, json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"

    addr_id = resp_addr.json().get("id")

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    resp_get = requests.get(get_addr_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("city") == "London"

# --- id=63  name='User Add Card' ---
def test_user_add_card():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    reg_url = get_url("user", "/register")
    resp_reg = requests.post(reg_url, json={"username": username, "password": "pw", "email": f"{username}@example.com"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

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

    get_card_url = get_url("user", f"/cards/{card_id}")
    resp_get = requests.get(get_card_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("ccv") == "123"

# --- id=64  name='Orders Create Order' ---
def test_orders_create_order():
    username, addr_id, card_id = _setup_user_and_cart()

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"

    order_id = resp_order.json().get("id")
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id

# --- id=65  name='Orders Search By Customer' ---
def test_orders_search_by_customer():
    username, addr_id, card_id = _setup_user_and_cart()

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")

    search_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    resp_search = requests.get(search_url, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

    orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in orders)

# --- id=66  name='Payment Http Authorize' ---
def test_payment_http_authorize():
    username, addr_id, card_id = _setup_user_and_cart()

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")

    payment_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    pay_url = get_url("payment-http", "/payments")
    resp_pay = requests.post(pay_url, json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True

    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    resp_get = requests.get(get_pay_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) > 0
    assert auths[-1].get("orderId") == order_id

# --- id=67  name='Shipping Http Ship' ---
def test_shipping_http_ship():
    username, addr_id, card_id = _setup_user_and_cart()

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")

    shipping_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St"},
        "itemCount": 2,
        "orderId": order_id
    }

    ship_url = get_url("shipping-http", "/shipping")
    resp_ship = requests.post(ship_url, json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id

    get_ship_url = get_url("shipping-http", f"/shipping/{order_id}")
    resp_get = requests.get(get_ship_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
