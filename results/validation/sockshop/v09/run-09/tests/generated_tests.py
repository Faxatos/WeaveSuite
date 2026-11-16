# Tests generated in iteration 09
# Captured: 2026-06-04T20:54:26
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=336  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Register same user
    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Negative: Login wrong password
    resp_bad_login = requests.get(get_url("user", "/login"), auth=(username, "wrong"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=337  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Jane",
        "lastName": "Doe"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Add Address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1 1AA",
        "street": "Baker St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Follow-up GET Address
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addr_body = resp_get_addr.json()
    assert addr_body.get("city") == address_data["city"]
    assert addr_body.get("country") == address_data["country"]
    assert addr_body.get("number") == address_data["number"]
    assert addr_body.get("postcode") == address_data["postcode"]
    assert addr_body.get("street") == address_data["street"]

    # Add Card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Follow-up GET Card
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    card_body = resp_get_card.json()
    assert card_body.get("ccv") == card_data["ccv"]
    assert card_body.get("expires") == card_data["expires"]

# --- id=338  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    socks = resp_list.json()
    assert isinstance(socks, list)
    if len(socks) > 0:
        sock_id = socks[0]["id"]
        resp_get = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
        assert resp_get.json().get("id") == sock_id

    # Negative
    resp_not_found = requests.get(get_url("catalogue", "/catalogue/invalid-id-9999"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=339  name='Catalogue Tags' ---
def test_catalogue_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "tags" in data
    assert isinstance(data["tags"], list)

# --- id=340  name='Carts Add Item' ---
def test_carts_add_get_delete_item():
    # Setup User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_req, timeout=10)

    # Setup Item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp_cat.json()
    assert len(socks) > 0
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }

    # Add item
    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    add_body = resp_add.json()
    assert add_body.get("itemId") == item_data["itemId"]
    assert add_body.get("quantity") == item_data["quantity"]
    assert add_body.get("unitPrice") == item_data["unitPrice"]

    # Follow-up GET item
    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data.get("itemId") == item_id
    assert get_data.get("quantity") == 2
    assert get_data.get("unitPrice") == unit_price

    # Update item (PATCH)
    item_data_update = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": unit_price
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=item_data_update, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Follow-up GET item
    resp_get_patch = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_patch.status_code == 200, f"Expected 200, got {resp_get_patch.status_code}: {resp_get_patch.text}"
    assert resp_get_patch.json().get("quantity") == 5

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Follow-up GET item -> 404
    resp_get_after = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_after.status_code == 404, f"Expected 404, got {resp_get_after.status_code}: {resp_get_after.text}"

# --- id=341  name='Carts Cart' ---
def test_carts_delete_cart():
    # Setup User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_req, timeout=10)

    # Setup Item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp_cat.json()
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    # Add item to cart
    cart_req = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_req, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    # Delete cart
    resp_del = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Follow-up GET cart items -> should be empty list
    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json() == []

# --- id=342  name='Carts Merge' ---
def test_carts_merge():
    # Setup User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_req, timeout=10)

    # Setup Session Cart
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp_cat.json()
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    cart_req = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=cart_req, timeout=10)

    # Merge
    resp_merge = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    # Verify item is in user cart
    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 1

    # Negative: Merge non-existent session cart
    resp_merge_fail = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId=invalid_session"), timeout=10)
    assert resp_merge_fail.status_code == 404, f"Expected 404, got {resp_merge_fail.status_code}: {resp_merge_fail.text}"

# --- id=343  name='Orders Create And Retrieve' ---
def test_orders_create_and_retrieve():
    # Setup User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    resp_user = requests.post(get_url("user", "/register"), json=user_req, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Setup Address
    addr_req = {"city": "C", "country": "D", "number": "1", "postcode": "123", "street": "S", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    # Setup Card
    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    # Setup Item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp_cat.json()
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    # Setup Cart
    cart_req = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_req, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    # Create Order
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")

    # Follow-up GET Order
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json().get("id") == order_id

    # Search Orders
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

    # Follow-up GET Payment
    resp_get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    pay_list = resp_get_pay.json()
    assert isinstance(pay_list, list)
    if len(pay_list) > 0:
        assert pay_list[0].get("orderId") == order_id
        assert pay_list[0].get("authorised") is True

    # Follow-up GET Shipping
    resp_get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    ship_data = resp_get_ship.json()
    if ship_data and "orderId" in ship_data:
        assert ship_data.get("orderId") == order_id

    # Negative: GET non-existent order
    resp_not_found = requests.get(get_url("orders", "/orders/invalid-order-id-999"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=344  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    # Setup User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    resp_user = requests.post(get_url("user", "/register"), json=user_req, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Setup Address
    addr_req = {"city": "C", "country": "D", "number": "1", "postcode": "123", "street": "S", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    # Setup Card
    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    # Setup Item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp_cat.json()
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    # Setup Cart with high quantity to trigger decline (amount > 100)
    cart_req = {"itemId": item_id, "quantity": 1000, "unitPrice": unit_price}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_req, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    # Create Order
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
