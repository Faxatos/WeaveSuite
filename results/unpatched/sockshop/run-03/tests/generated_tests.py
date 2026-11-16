# Tests generated in iteration 03
# Captured: 2026-07-10T16:01:42
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=25  name='User Register Login And Conflict' ---
def test_user_register_login_and_conflict():
    username = random_string()
    password = random_string()
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    # Register user
    url_register = get_url("user", "/register")
    resp = requests.post(url_register, json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    url_login = get_url("user", "/login")
    resp_login = requests.get(url_login, auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Register again -> 409 Conflict
    resp_conflict = requests.post(url_register, json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=26  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    url_login = get_url("user", "/login")
    resp_login = requests.get(url_login, auth=HTTPBasicAuth("invalid", "invalid"), timeout=10)
    assert resp_login.status_code == 401, f"Expected 401, got {resp_login.status_code}: {resp_login.text}"

# --- id=27  name='Catalogue Browse And Not Found' ---
def test_catalogue_browse_and_not_found():
    url_cat = get_url("catalogue", "/catalogue")
    resp = requests.get(url_cat, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)

    if socks:
        sock_id = socks[0].get("id")
        url_sock = get_url("catalogue", f"/catalogue/{sock_id}")
        resp_sock = requests.get(url_sock, timeout=10)
        assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"

    url_not_found = get_url("catalogue", "/catalogue/nonexistent-id-12345")
    resp_not_found = requests.get(url_not_found, timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=28  name='Catalogue Tags And Size' ---
def test_catalogue_tags_and_size():
    url_tags = get_url("catalogue", "/tags")
    resp_tags = requests.get(url_tags, timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"

    url_size = get_url("catalogue", "/catalogue/size")
    resp_size = requests.get(url_size, timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

# --- id=29  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    customer_id = str(uuid.uuid4())
    item_id = str(uuid.uuid4())

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }

    url_items = get_url("carts", f"/carts/{customer_id}/items")
    resp_add = requests.post(url_items, json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(url_items, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert isinstance(items, list)
    assert any(i.get("itemId") == item_id for i in items)

    item_payload["quantity"] = 5
    resp_patch = requests.patch(url_items, json=item_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    url_item = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_get_item = requests.get(url_item, timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json().get("quantity") == 5

    resp_del_item = requests.delete(url_item, timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    resp_get_item_after = requests.get(url_item, timeout=10)
    assert resp_get_item_after.status_code == 404, f"Expected 404, got {resp_get_item_after.status_code}: {resp_get_item_after.text}"

    url_cart = get_url("carts", f"/carts/{customer_id}")
    resp_del_cart = requests.delete(url_cart, timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    resp_del_cart_again = requests.delete(url_cart, timeout=10)
    assert resp_del_cart_again.status_code == 404, f"Expected 404, got {resp_del_cart_again.status_code}: {resp_del_cart_again.text}"

# --- id=30  name='Carts Merge' ---
def test_carts_merge():
    customer_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    item_id = str(uuid.uuid4())
    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 5.0
    }
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)

    url_merge = get_url("carts", f"/carts/{customer_id}/merge")
    resp_merge = requests.get(url_merge, params={"sessionId": session_id}, timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    url_cust_items = get_url("carts", f"/carts/{customer_id}/items")
    resp_cust_items = requests.get(url_cust_items, timeout=10)
    assert resp_cust_items.status_code == 200, f"Expected 200, got {resp_cust_items.status_code}: {resp_cust_items.text}"
    items = resp_cust_items.json()
    assert any(i.get("itemId") == item_id for i in items)

    resp_merge_not_found = requests.get(url_merge, params={"sessionId": "nonexistent-session"}, timeout=10)
    assert resp_merge_not_found.status_code == 404, f"Expected 404, got {resp_merge_not_found.status_code}: {resp_merge_not_found.text}"

# --- id=31  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = str(uuid.uuid4())
    payment_req = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "W1",
            "street": "Oxford St"
        },
        "amount": 100.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "John",
            "lastName": "Doe"
        },
        "orderId": order_id
    }

    url_payments = get_url("payment-http", "/payments")
    resp = requests.post(url_payments, json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_resp = resp.json()
    assert auth_resp.get("orderId") == order_id

    url_payment_get = get_url("payment-http", f"/payments/{order_id}")
    resp_get = requests.get(url_payment_get, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=32  name='Shipping Request' ---
def test_shipping_request():
    order_id = str(uuid.uuid4())
    shipping_req = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "W1",
            "street": "Oxford St"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    url_shipping = get_url("shipping-http", "/shipping")
    resp = requests.post(url_shipping, json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id

    url_shipping_get = get_url("shipping-http", f"/shipping/{order_id}")
    resp_get = requests.get(url_shipping_get, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id

# --- id=33  name='Orders Not Found' ---
def test_orders_not_found():
    url_search = get_url("orders", "/orders/search/customerId")
    resp_search = requests.get(url_search, params={"custId": "nonexistent-customer"}, timeout=10)
    assert resp_search.status_code == 404, f"Expected 404, got {resp_search.status_code}: {resp_search.text}"

    url_order = get_url("orders", "/orders/nonexistent-order")
    resp_order = requests.get(url_order, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"
