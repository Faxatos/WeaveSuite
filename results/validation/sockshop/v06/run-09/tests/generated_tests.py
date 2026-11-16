# Tests generated in iteration 09
# Captured: 2026-06-02T22:47:48
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=64  name='Carts Add And Item' ---
def test_carts_add_and_get_item():
    customer_id = random_string()
    item_id = str(uuid.uuid4())

    add_url = get_url("carts", f"/carts/{customer_id}/items")
    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 9.99}
    resp = requests.post(add_url, json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    get_url_item = get_url("carts", f"/carts/{customer_id}/items")
    resp_get = requests.get(get_url_item, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i.get("itemId") == item_id for i in items), "Item not found in cart"

# --- id=65  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = random_string()
    item_id = str(uuid.uuid4())

    add_url = get_url("carts", f"/carts/{customer_id}/items")
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    resp = requests.post(add_url, json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    get_url_item = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_get_item = requests.get(get_url_item, timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"

    del_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_del = requests.delete(del_url, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(del_url, timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=66  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = random_string()

    add_url = get_url("carts", f"/carts/{customer_id}/items")
    item_payload = {"itemId": str(uuid.uuid4()), "quantity": 1, "unitPrice": 5.0}
    resp = requests.post(add_url, json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    get_url_items = get_url("carts", f"/carts/{customer_id}/items")
    resp_get_items = requests.get(get_url_items, timeout=10)
    assert resp_get_items.status_code == 200, f"Expected 200, got {resp_get_items.status_code}: {resp_get_items.text}"

    del_url = get_url("carts", f"/carts/{customer_id}")
    resp_del = requests.delete(del_url, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_items_after = requests.get(get_url_items, timeout=10)
    assert resp_get_items_after.status_code == 200, f"Expected 200, got {resp_get_items_after.status_code}: {resp_get_items_after.text}"
    assert len(resp_get_items_after.json()) == 0, "Cart not empty after deletion"

# --- id=67  name='Catalogue List And Item' ---
def test_catalogue_list_and_get_item():
    list_url = get_url("catalogue", "/catalogue")
    resp_list = requests.get(list_url, timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    items = resp_list.json()
    if not items:
        pytest.skip("No items in catalogue to test")

    item_id = items[0]["id"]

    get_url_item = get_url("catalogue", f"/catalogue/{item_id}")
    resp_get = requests.get(get_url_item, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=68  name='Catalogue Tags' ---
def test_catalogue_get_tags():
    tags_url = get_url("catalogue", "/tags")
    resp = requests.get(tags_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=69  name='User Register And Customer' ---
def test_user_register_and_get_customer():
    username = random_string()

    reg_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(reg_url, json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    get_url_cust = get_url("user", f"/customers/{username}")
    resp_get = requests.get(get_url_cust, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=70  name='User Add And Address' ---
def test_user_add_and_get_address():
    username = random_string()

    reg_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(reg_url, json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    get_user_url = get_url("user", f"/customers/{username}")
    resp_get_user = requests.get(get_user_url, timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    add_url = get_url("user", "/addresses")
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Test Street",
        "userID": username
    }
    resp_add = requests.post(add_url, json=addr_payload, timeout=10)
    assert resp_add.status_code == 200, f"Expected 200, got {resp_add.status_code}: {resp_add.text}"
    addr_id = resp_add.json().get("id")

    get_url_addr = get_url("user", f"/addresses/{addr_id}")
    resp_get = requests.get(get_url_addr, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=71  name='User Add And Card' ---
def test_user_add_and_get_card():
    username = random_string()

    reg_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(reg_url, json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    get_user_url = get_url("user", f"/customers/{username}")
    resp_get_user = requests.get(get_user_url, timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    add_url = get_url("user", "/cards")
    card_payload = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_add = requests.post(add_url, json=card_payload, timeout=10)
    assert resp_add.status_code == 200, f"Expected 200, got {resp_add.status_code}: {resp_add.text}"
    card_id = resp_add.json().get("id")

    get_url_card = get_url("user", f"/cards/{card_id}")
    resp_get = requests.get(get_url_card, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=72  name='User Customer' ---
def test_user_delete_customer():
    username = random_string()

    reg_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(reg_url, json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    get_user_url = get_url("user", f"/customers/{username}")
    resp_get_user = requests.get(get_user_url, timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    del_url = get_url("user", f"/customers/{username}")
    resp_del = requests.delete(del_url, timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customers = resp_get.json().get("_embedded", {}).get("customer", [])
    assert not any(c.get("username") == username for c in customers), "Customer was not deleted"

# --- id=73  name='Orders Create And Order' ---
def test_orders_create_and_get_order():
    username = random_string()

    reg_url = get_url("user", "/register")
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(reg_url, json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    get_user_url = get_url("user", f"/customers/{username}")
    resp_get_user = requests.get(get_user_url, timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    add_url = get_url("user", "/addresses")
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Test Street",
        "userID": username
    }
    resp_addr = requests.post(add_url, json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    get_addr_url = get_url("user", f"/addresses/{addr_id}")
    resp_get_addr = requests.get(get_addr_url, timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

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

    get_card_url = get_url("user", f"/cards/{card_id}")
    resp_get_card = requests.get(get_card_url, timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    cart_url = get_url("carts", f"/carts/{username}/items")
    item_payload = {"itemId": str(uuid.uuid4()), "quantity": 1, "unitPrice": 10.0}
    resp_cart = requests.post(cart_url, json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    get_cart_url = get_url("carts", f"/carts/{username}/items")
    resp_get_cart = requests.get(get_cart_url, timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

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

    get_order_url = get_url("orders", f"/orders/{order_id}")
    resp_get_order = requests.get(get_order_url, timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"

# --- id=74  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = random_string()

    pay_url = get_url("payment-http", "/payments")
    pay_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "Test", "lastName": "User"},
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A", "street": "Street"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"}
    }
    resp_pay = requests.post(pay_url, json=pay_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"

    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    resp_get = requests.get(get_pay_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) > 0, "Payment authorization not found"

# --- id=75  name='Shipping Create And' ---
def test_shipping_create_and_get():
    order_id = random_string()

    ship_url = get_url("shipping-http", "/shipping")
    ship_payload = {
        "orderId": order_id,
        "itemCount": 2,
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A", "street": "Street"}
    }
    resp_ship = requests.post(ship_url, json=ship_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"

    get_ship_url = get_url("shipping-http", f"/shipping/{order_id}")
    resp_get = requests.get(get_ship_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
