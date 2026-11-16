# Tests generated in iteration 11
# Captured: 2026-07-04T18:00:30
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=514  name='User Register And Retrieve' ---
def test_user_register_and_retrieve():
    username = random_string()
    password = random_string()
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    user_data = resp_get.json()
    assert user_data.get("username") == username
    assert user_data.get("email") == user_payload["email"]
    assert user_data.get("firstName") == user_payload["firstName"]
    assert user_data.get("lastName") == user_payload["lastName"]
    assert "password" not in user_data or user_data["password"] != password

    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=515  name='User Login' ---
def test_user_login():
    username = random_string()
    password = random_string()
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpwd"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

# --- id=516  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = random_string()
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "F",
        "lastName": "L"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {
        "number": "123",
        "street": "Main St",
        "city": "Anytown",
        "postcode": "12345",
        "country": "USA",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_data = resp_addr_get.json()
    assert addr_data.get("number") == address_payload["number"]
    assert addr_data.get("street") == address_payload["street"]
    assert addr_data.get("city") == address_payload["city"]
    assert addr_data.get("postcode") == address_payload["postcode"]
    assert addr_data.get("country") == address_payload["country"]

    card_payload = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data.get("expires") == card_payload["expires"]
    assert card_data.get("longNum") != card_payload["longNum"]
    assert card_data.get("longNum").endswith("3456")
    assert "ccv" not in card_data or card_data["ccv"] != card_payload["ccv"]

    resp_addr_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_del.status_code == 200, f"Expected 200, got {resp_addr_del.status_code}: {resp_addr_del.text}"

    resp_card_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_del.status_code == 200, f"Expected 200, got {resp_card_del.status_code}: {resp_card_del.text}"

# --- id=517  name='User Customer' ---
def test_user_delete_customer():
    username = random_string()
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    user_data = resp_get.json()
    assert user_data.get("username") == username
    assert user_data.get("email") is None or user_data.get("email") == ""

    resp_del_2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_2.status_code == 200, f"Expected 200, got {resp_del_2.status_code}: {resp_del_2.text}"
    assert resp_del_2.json().get("status") is False

# --- id=518  name='Carts Add And Retrieve Items' ---
def test_carts_add_and_retrieve_items():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    customer_id = random_string()

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_add_2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add_2.status_code == 201, f"Expected 201, got {resp_add_2.status_code}: {resp_add_2.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 4
    assert cart_items[0]["unitPrice"] == unit_price

    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": unit_price
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_item_404 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item_404.status_code == 404, f"Expected 404, got {resp_get_item_404.status_code}: {resp_get_item_404.text}"

# --- id=519  name='Carts Cart' ---
def test_carts_delete_cart():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp_cat.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    customer_id = random_string()

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0

# --- id=520  name='Orders Create And Retrieve' ---
def test_orders_create_and_retrieve():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "US", "userID": username}, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={"longNum": "1111222233334444", "expires": "12/26", "ccv": "111", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp_cat.json()
    item_id = items[0]["id"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": items[0]["price"]}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data["customer"]["username"] == username
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["itemId"] == item_id

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    retrieved_order = resp_order_get.json()
    assert retrieved_order["id"] == order_id
    assert retrieved_order["customer"]["username"] == username
    assert retrieved_order["address"]["city"] == "C"
    assert retrieved_order["card"]["longNum"].endswith("4444")
    assert len(retrieved_order["items"]) == 1
    assert retrieved_order["items"][0]["itemId"] == item_id
    assert retrieved_order["total"] == items[0]["price"]

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    search_data = resp_search.json()
    customer_orders = search_data.get("_embedded", {}).get("customerOrders", [])
    assert len(customer_orders) > 0
    assert any(o["id"] == order_id for o in customer_orders)

# --- id=521  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "US", "userID": username}, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={"longNum": "1111222233334444", "expires": "12/26", "ccv": "111", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "message" in resp_order.json()

# --- id=522  name='Orders Create Invalid Uri' ---
def test_orders_create_invalid_uri():
    username = random_string()

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid-id-format",
        "card": f"/cards/invalid-id-format",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=523  name='Payments Authorize Boundaries' ---
def test_payments_authorize_boundaries():
    order_id = random_string(10)
    base_payload = {
        "address": {"city": "C", "country": "US", "number": "1", "postcode": "P", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    payload_100 = dict(base_payload)
    payload_100["amount"] = 100.0
    resp_100 = requests.post(get_url("payment-http", "/payments"), json=payload_100, timeout=10)
    assert resp_100.status_code == 200, f"Expected 200, got {resp_100.status_code}: {resp_100.text}"
    assert resp_100.json().get("authorised") is True

    payload_over = dict(base_payload)
    payload_over["amount"] = 100.01
    resp_over = requests.post(get_url("payment-http", "/payments"), json=payload_over, timeout=10)
    assert resp_over.status_code == 200, f"Expected 200, got {resp_over.status_code}: {resp_over.text}"
    assert resp_over.json().get("authorised") is False

    payload_zero = dict(base_payload)
    payload_zero["amount"] = 0.0
    resp_zero = requests.post(get_url("payment-http", "/payments"), json=payload_zero, timeout=10)
    assert resp_zero.status_code == 200, f"Expected 200, got {resp_zero.status_code}: {resp_zero.text}"
    assert resp_zero.json().get("authorised") is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auth_list = resp_get.json()
    assert len(auth_list) == 3
    assert auth_list[0]["authorised"] is True
    assert auth_list[1]["authorised"] is False
    assert auth_list[2]["authorised"] is False

# --- id=524  name='Shipping Create And Retrieve' ---
def test_shipping_create_and_retrieve():
    order_id = random_string(10)
    shipping_payload = {
        "address": {
            "city": "C",
            "country": "US",
            "number": "1",
            "postcode": "P",
            "street": "S"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data.get("orderId") == order_id
    assert ship_data.get("carrier") is not None
    assert ship_data.get("trackingNumber") is not None

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    ship_get_data = resp_get.json()
    assert ship_get_data.get("orderId") == order_id
    assert ship_get_data.get("carrier") == ship_data.get("carrier")
    assert ship_get_data.get("trackingNumber") == ship_data.get("trackingNumber")

# --- id=525  name='Catalogue Size' ---
def test_catalogue_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size?tags=brown"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    size_data = resp.json()
    assert "size" in size_data
    assert isinstance(size_data["size"], int)
