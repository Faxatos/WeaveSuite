# Tests generated in iteration 04
# Captured: 2026-06-07T04:04:12
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1241  name='Catalogue Items And Not Found' ---
def test_catalogue_get_items_and_not_found():
    # Positive: Get catalogue
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Expected at least one item in catalogue"

    item_id = items[0]["id"]

    # Positive: Get specific item
    url_item = get_url("catalogue", f"/catalogue/{item_id}")
    resp_item = requests.get(url_item, timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id

    # Negative: Item not found
    url_not_found = get_url("catalogue", "/catalogue/invalid-item-id-12345")
    resp_not_found = requests.get(url_not_found, timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=1242  name='User Registration And Login Negative' ---
def test_user_registration_and_login_negative():
    username = f"user_{generate_random_string()}"
    password = "password123"

    # Positive: Register user
    url_register = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(url_register, json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Verify creation
    url_customer = get_url("user", f"/customers/{username}")
    resp_cust = requests.get(url_customer, timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"

    # Negative: Register same user again
    resp_reg_conflict = requests.post(url_register, json=user_payload, timeout=10)
    assert resp_reg_conflict.status_code == 409, f"Expected 409, got {resp_reg_conflict.status_code}: {resp_reg_conflict.text}"

    # Positive: Login
    url_login = get_url("user", "/login")
    resp_login = requests.get(url_login, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Login with wrong password
    resp_login_fail = requests.get(url_login, auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

# --- id=1243  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{generate_random_string()}"

    # Register user
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Add Address
    url_address = get_url("user", "/addresses")
    addr_payload = {
        "userID": username,
        "number": "123",
        "street": "Main St",
        "city": "Anytown",
        "postcode": "12345",
        "country": "USA"
    }
    resp_addr = requests.post(url_address, json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    # Verify Address
    url_get_addr = get_url("user", f"/addresses/{addr_id}")
    resp_get_addr = requests.get(url_get_addr, timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json()["city"] == "Anytown"

    # Add Card
    url_card = get_url("user", "/cards")
    card_payload = {
        "userID": username,
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123"
    }
    resp_card = requests.post(url_card, json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    # Verify Card
    url_get_card = get_url("user", f"/cards/{card_id}")
    resp_get_card = requests.get(url_get_card, timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert resp_get_card.json()["expires"] == "12/25"

# --- id=1244  name='Carts Add Increment And Item' ---
def test_carts_add_increment_and_delete_item():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    url_items = get_url("carts", f"/carts/{customer_id}/items")

    # Add item
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.50
    }
    resp_add = requests.post(url_items, json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verify item added
    url_item = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_get = requests.get(url_item, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 2

    # Increment item (operation more than once)
    resp_inc = requests.post(url_items, json=item_payload, timeout=10)
    assert resp_inc.status_code == 201, f"Expected 201, got {resp_inc.status_code}: {resp_inc.text}"

    # Verify cumulative state
    resp_get_inc = requests.get(url_item, timeout=10)
    assert resp_get_inc.status_code == 200, f"Expected 200, got {resp_get_inc.status_code}: {resp_get_inc.text}"
    assert resp_get_inc.json()["quantity"] == 4

    # Update item
    update_payload = {
        "itemId": item_id,
        "quantity": 10,
        "unitPrice": 10.50
    }
    resp_patch = requests.patch(url_items, json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify update
    resp_get_patch = requests.get(url_item, timeout=10)
    assert resp_get_patch.status_code == 200, f"Expected 200, got {resp_get_patch.status_code}: {resp_get_patch.text}"
    assert resp_get_patch.json()["quantity"] == 10

    # Delete item
    resp_del = requests.delete(url_item, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify deletion (Negative test for 404)
    resp_get_del = requests.get(url_item, timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=1245  name='Carts Merge Negative And Positive' ---
def test_carts_merge_negative_and_positive():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"

    url_merge = get_url("carts", f"/carts/{customer_id}/merge")

    # Negative: Merge non-existent session cart
    resp_merge_fail = requests.get(url_merge, params={"sessionId": session_id}, timeout=10)
    assert resp_merge_fail.status_code == 404, f"Expected 404, got {resp_merge_fail.status_code}: {resp_merge_fail.text}"

    # Create session cart by adding an item
    item_id = f"item_{generate_random_string()}"
    url_session_items = get_url("carts", f"/carts/{session_id}/items")
    resp_sess_add = requests.post(url_session_items, json={"itemId": item_id, "quantity": 1, "unitPrice": 5.0}, timeout=10)
    assert resp_sess_add.status_code == 201, f"Expected 201, got {resp_sess_add.status_code}: {resp_sess_add.text}"

    # Verify session item
    url_sess_item = get_url("carts", f"/carts/{session_id}/items/{item_id}")
    resp_sess_get = requests.get(url_sess_item, timeout=10)
    assert resp_sess_get.status_code == 200, f"Expected 200, got {resp_sess_get.status_code}: {resp_sess_get.text}"

    # Positive: Merge session cart
    resp_merge = requests.get(url_merge, params={"sessionId": session_id}, timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    # Verify item is in customer cart
    url_cust_item = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_cust_item = requests.get(url_cust_item, timeout=10)
    assert resp_cust_item.status_code == 200, f"Expected 200, got {resp_cust_item.status_code}: {resp_cust_item.text}"
    assert resp_cust_item.json()["itemId"] == item_id

# --- id=1246  name='Orders Place Order Success' ---
def test_orders_place_order_success():
    username = f"user_{generate_random_string()}"

    # 1. Register user
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # 2. Add Address
    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "userID": username, "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"
    }, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    # 3. Add Card
    resp_card = requests.post(get_url("user", "/cards"), json={
        "userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"
    }, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    # 4. Add item to cart (price <= 100 to ensure payment authorization)
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "sock1", "quantity": 1, "unitPrice": 50.00
    }, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items/sock1"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    # 5. Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    url_orders = get_url("orders", "/orders")
    resp_order = requests.post(url_orders, json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"

    order_id = resp_order.json()["id"]

    # Verify Order
    url_get_order = get_url("orders", f"/orders/{order_id}")
    resp_get_order = requests.get(url_get_order, timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id

# --- id=1247  name='Orders Place Order Payment Declined' ---
def test_orders_place_order_payment_declined():
    username = f"user_{generate_random_string()}"

    # 1. Register user
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # 2. Add Address
    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "userID": username, "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"
    }, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    # 3. Add Card
    resp_card = requests.post(get_url("user", "/cards"), json={
        "userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"
    }, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    # 4. Add item to cart with price > 100 to trigger payment decline
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "sock_expensive", "quantity": 1, "unitPrice": 150.00
    }, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items/sock_expensive"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    # 5. Place Order (Negative: Payment not authorized)
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    url_orders = get_url("orders", "/orders")
    resp_order = requests.post(url_orders, json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1248  name='Payment And Shipping Direct' ---
def test_payment_and_shipping_direct():
    order_id = f"order_{generate_random_string()}"

    # Payment
    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S"},
        "amount": 50.00,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    url_payments = get_url("payment-http", "/payments")
    resp_pay = requests.post(url_payments, json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json()["authorised"] is True

    # Verify Payment
    url_get_pay = get_url("payment-http", f"/payments/{order_id}")
    resp_get_pay = requests.get(url_get_pay, timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    assert len(resp_get_pay.json()) > 0

    # Shipping
    shipping_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "P", "street": "S"},
        "itemCount": 2,
        "orderId": order_id
    }
    url_shipping = get_url("shipping-http", "/shipping")
    resp_ship = requests.post(url_shipping, json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json()["orderId"] == order_id

    # Verify Shipping
    url_get_ship = get_url("shipping-http", f"/shipping/{order_id}")
    resp_get_ship = requests.get(url_get_ship, timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    assert resp_get_ship.json()["orderId"] == order_id
