# Tests generated in iteration 04
# Captured: 2026-06-03T19:29:21
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=23  name='Carts Add Item' ---
def test_carts_add_get_delete_item():
    # Get a real item ID from catalogue
    url_cat = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(url_cat, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]

    # Create a real user to get a customer ID
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_reg_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_reg_get.status_code == 200, f"Expected 200, got {resp_reg_get.status_code}: {resp_reg_get.text}"

    customer_id = username
    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 15.5}

    # Add item
    url_items = get_url("carts", f"/carts/{customer_id}/items")
    resp = requests.post(url_items, json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify item added
    resp_get = requests.get(url_items, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i.get("itemId") == item_id for i in items), "Item not found in cart"

    # Delete item
    url_item = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_del = requests.delete(url_item, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify item deleted
    resp_get_item = requests.get(url_item, timeout=10)
    assert resp_get_item.status_code == 404, f"Expected 404, got {resp_get_item.status_code}: {resp_get_item.text}"

# --- id=24  name='Carts Merge' ---
def test_carts_merge():
    # Get a real item ID from catalogue
    url_cat = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(url_cat, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]

    # Create a real user
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_reg_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_reg_get.status_code == 200, f"Expected 200, got {resp_reg_get.status_code}: {resp_reg_get.text}"

    customer_id = username
    session_id = "session_" + "".join(random.choices(string.ascii_lowercase, k=8))

    # Add item to session cart
    url_session_items = get_url("carts", f"/carts/{session_id}/items")
    resp_add = requests.post(url_session_items, json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verify item in session cart
    resp_add_get = requests.get(url_session_items, timeout=10)
    assert resp_add_get.status_code == 200, f"Expected 200, got {resp_add_get.status_code}: {resp_add_get.text}"

    # Merge carts
    url_merge = get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}")
    resp_merge = requests.get(url_merge, timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    # Verify item in customer cart
    url_customer_items = get_url("carts", f"/carts/{customer_id}/items")
    resp_cust_get = requests.get(url_customer_items, timeout=10)
    assert resp_cust_get.status_code == 200, f"Expected 200, got {resp_cust_get.status_code}: {resp_cust_get.text}"
    items = resp_cust_get.json()
    assert any(i.get("itemId") == item_id for i in items), "Item not merged into customer cart"

# --- id=25  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    url_cat = get_url("catalogue", "/catalogue")
    resp = requests.get(url_cat, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0, "Expected at least one sock in catalogue"

    sock_id = socks[0]["id"]
    url_sock = get_url("catalogue", f"/catalogue/{sock_id}")
    resp_sock = requests.get(url_sock, timeout=10)
    assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
    assert resp_sock.json().get("id") == sock_id

# --- id=26  name='Catalogue Tags' ---
def test_catalogue_tags():
    url_tags = get_url("catalogue", "/tags")
    resp = requests.get(url_tags, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    assert "tags" in tags_data

# --- id=27  name='User Register Login' ---
def test_user_register_login_delete():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register
    url_reg = get_url("user", "/register")
    resp_reg = requests.post(url_reg, json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Verify Register
    url_cust = get_url("user", f"/customers/{username}")
    resp_cust = requests.get(url_cust, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"

    # Login
    url_login = get_url("user", "/login")
    resp_login = requests.get(url_login, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Delete Customer
    resp_del = requests.delete(url_cust, timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    # Verify Delete
    url_cust_all = get_url("user", "/customers")
    resp_all = requests.get(url_cust_all, timeout=10)
    assert resp_all.status_code == 200, f"Expected 200, got {resp_all.status_code}: {resp_all.text}"
    customers = resp_all.json().get("_embedded", {}).get("customer", [])
    assert not any(c.get("username") == username for c in customers), "Customer was not deleted"

# --- id=28  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_reg_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_reg_get.status_code == 200, f"Expected 200, got {resp_reg_get.status_code}: {resp_reg_get.text}"

    # Add Address
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1",
        "street": "Main St",
        "userID": username
    }
    url_addr = get_url("user", "/addresses")
    resp_addr = requests.post(url_addr, json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Verify Address
    url_addr_get = get_url("user", f"/addresses/{addr_id}")
    resp_addr_get = requests.get(url_addr_get, timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert resp_addr_get.json().get("city") == "London"

    # Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    url_card = get_url("user", "/cards")
    resp_card = requests.post(url_card, json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Verify Card
    url_card_get = get_url("user", f"/cards/{card_id}")
    resp_card_get = requests.get(url_card_get, timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    assert resp_card_get.json().get("ccv") == "123"

# --- id=29  name='Orders Create And Search' ---
def test_orders_create_and_search():
    order_id, username = create_real_order()

    # Search Orders
    url_order_search = get_url("orders", f"/orders/search/customerId?custId={username}")
    resp_search = requests.get(url_order_search, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    orders_embedded = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in orders_embedded)

# --- id=30  name='Payment Authorize' ---
def test_payment_authorize():
    order_id, _ = create_real_order()

    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }
    url_pay = get_url("payment-http", "/payments")
    resp_pay = requests.post(url_pay, json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True

    # Verify payment
    url_pay_get = get_url("payment-http", f"/payments/{order_id}")
    resp_pay_get = requests.get(url_pay_get, timeout=10)
    assert resp_pay_get.status_code == 200, f"Expected 200, got {resp_pay_get.status_code}: {resp_pay_get.text}"
    auths = resp_pay_get.json()
    assert len(auths) > 0
    assert any(a.get("orderId") == order_id for a in auths)

# --- id=31  name='Shipping Ship' ---
def test_shipping_ship():
    order_id, _ = create_real_order()

    shipping_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 2,
        "orderId": order_id
    }
    url_ship = get_url("shipping-http", "/shipping")
    resp_ship = requests.post(url_ship, json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id

    # Verify shipping
    url_ship_get = get_url("shipping-http", f"/shipping/{order_id}")
    resp_ship_get = requests.get(url_ship_get, timeout=10)
    assert resp_ship_get.status_code == 200, f"Expected 200, got {resp_ship_get.status_code}: {resp_ship_get.text}"
    assert resp_ship_get.json().get("orderId") == order_id
