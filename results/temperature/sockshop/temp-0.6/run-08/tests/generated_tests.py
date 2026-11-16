# Tests generated in iteration 08
# Captured: 2026-07-05T04:39:16
# Count:    21
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=716  name='Carts Merge Success' ---
def test_carts_merge_success():
    username = register_user()
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    item_id = get_catalogue_item_id()

    payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.0}
    resp_add = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    resp_add_get = requests.get(get_url("carts", f"/carts/{session_id}/items"), timeout=10)
    assert resp_add_get.status_code == 200, f"Expected 200, got {resp_add_get.status_code}: {resp_add_get.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i.get("itemId") == item_id and i.get("quantity") == 2 for i in items)

# --- id=717  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    username = register_user()
    addr_id = add_address(username)
    card_id = add_card(username)
    item_id = get_catalogue_item_id()
    add_to_cart(username, item_id, 1, 10.0)
    order_id, _ = create_order(username, addr_id, card_id)

    payload = {
        "address": {"city": "C", "country": "UK", "number": "1", "postcode": "P", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 2
    assert auths[-1].get("orderId") == order_id

# --- id=718  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    username = register_user()
    addr_id = add_address(username)
    card_id = add_card(username)
    item_id = get_catalogue_item_id()
    add_to_cart(username, item_id, 1, 10.0)
    order_id, _ = create_order(username, addr_id, card_id)

    payload = {
        "address": {"city": "C", "country": "UK", "number": "1", "postcode": "P", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert auths[-1].get("authorised") is False

# --- id=719  name='Shipping Create And' ---
def test_shipping_create_and_get():
    username = register_user()
    addr_id = add_address(username)
    card_id = add_card(username)
    item_id = get_catalogue_item_id()
    add_to_cart(username, item_id, 1, 10.0)
    order_id, _ = create_order(username, addr_id, card_id)

    payload = {
        "address": {"city": "C", "country": "UK", "number": "1", "postcode": "P", "street": "S"},
        "itemCount": 1,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id

# --- id=720  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    username = register_user()
    order_payload = {
        "customer": f"/customers/{username}"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 404, f"Expected 404, got {resp_search.status_code}: {resp_search.text}"

# --- id=721  name='Orders Create Malformed Uri' ---
def test_orders_create_malformed_uri():
    username = register_user()
    item_id = get_catalogue_item_id()
    add_to_cart(username, item_id, 1, 10.0)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/malformed_id",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 404, f"Expected 404, got {resp_search.status_code}: {resp_search.text}"

# --- id=722  name='Orders Create Payment Declined' ---
def test_orders_create_payment_declined():
    username = register_user()
    addr_id = add_address(username)
    card_id = add_card(username)
    item_id = get_catalogue_item_id()
    add_to_cart(username, item_id, 15, 10.0)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 404, f"Expected 404, got {resp_search.status_code}: {resp_search.text}"

# --- id=723  name='Orders Search Customer' ---
def test_orders_search_customer():
    username = register_user()
    addr_id = add_address(username)
    card_id = add_card(username)
    item_id = get_catalogue_item_id()
    add_to_cart(username, item_id, 1, 10.0)
    order_id, _ = create_order(username, addr_id, card_id)

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded = resp_search.json().get("_embedded", {})
    customer_orders = embedded.get("customerOrders", [])
    assert len(customer_orders) >= 1
    assert any(o.get("id") == order_id for o in customer_orders)

# --- id=703  name='User Register Conflict' ---
def test_user_register_conflict():
    username = register_user()
    payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}
    resp2 = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=704  name='User Login Success' ---
def test_user_login_success():
    username = register_user()
    auth = (username, "pwd")
    resp_login = requests.get(get_url("user", "/login"), auth=auth, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=705  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = register_user()
    auth = (username, "wrong_pwd")
    resp_login = requests.get(get_url("user", "/login"), auth=auth, timeout=10)
    assert resp_login.status_code == 401, f"Expected 401, got {resp_login.status_code}: {resp_login.text}"

# --- id=706  name='User Address' ---
def test_user_delete_address():
    username = register_user()
    addr_id = add_address(username)

    resp_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    addresses = resp_get.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses)

# --- id=707  name='User Card' ---
def test_user_delete_card():
    username = register_user()
    card_id = add_card(username)

    resp_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cards = resp_get.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

# --- id=708  name='User Customer' ---
def test_user_delete_customer():
    username = register_user()

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cust = resp_get.json()
    assert cust.get("username") == username
    assert not cust.get("firstName")

    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=709  name='User Customers' ---
def test_user_get_customers():
    register_user()
    resp = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=710  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)
    if len(socks) > 0:
        sock_id = socks[0].get("id")
        resp_sock = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
        assert resp_sock.json().get("id") == sock_id

# --- id=711  name='Catalogue Size' ---
def test_catalogue_get_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

# --- id=712  name='Catalogue Tags' ---
def test_catalogue_get_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=713  name='Carts Update Item' ---
def test_carts_update_item():
    username = register_user()
    item_id = get_catalogue_item_id()
    add_to_cart(username, item_id, 1, 5.0)

    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 5.0}
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 5

# --- id=714  name='Carts Item' ---
def test_carts_delete_item():
    username = register_user()
    item_id = get_catalogue_item_id()
    add_to_cart(username, item_id, 1, 5.0)

    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=715  name='Carts Cart' ---
def test_carts_delete_cart():
    username = register_user()
    item_id = get_catalogue_item_id()
    add_to_cart(username, item_id, 1, 5.0)

    resp_del = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0
