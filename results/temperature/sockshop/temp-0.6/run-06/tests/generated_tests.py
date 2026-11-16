# Tests generated in iteration 06
# Captured: 2026-07-05T03:19:27
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=674  name='User Register And Login Success' ---
def test_user_register_and_login_success():
    username = generate_string()
    password = generate_string()
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username

    resp_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=675  name='User Register Conflict' ---
def test_user_register_conflict():
    username = generate_string()
    password = generate_string()
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com"
    }

    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=676  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    resp_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth("invalid", "invalid"), timeout=10)
    assert resp_login.status_code == 401, f"Expected 401, got {resp_login.status_code}: {resp_login.text}"

# --- id=677  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = generate_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "NW1",
        "street": "Baker St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert resp_addr_get.json().get("city") == "London"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567812345678",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    assert resp_card_get.json().get("ccv") == "123"

# --- id=678  name='Carts Add Item And Retrieve' ---
def test_carts_add_item_and_retrieve():
    cust_id = generate_string()
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp_add = requests.post(get_url("carts", f"/carts/{cust_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{cust_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 2

# --- id=679  name='Carts Item' ---
def test_carts_delete_item():
    cust_id = generate_string()
    item_id = "item_" + generate_string()

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 5.0
    }
    requests.post(get_url("carts", f"/carts/{cust_id}/items"), json=item_payload, timeout=10)

    resp_del = requests.delete(get_url("carts", f"/carts/{cust_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{cust_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=680  name='Orders Create Success' ---
def test_orders_create_success():
    username = generate_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

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

# --- id=681  name='Orders Create Missing Cart 406' ---
def test_orders_create_missing_cart_406():
    username = generate_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
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

# --- id=682  name='Orders Create Invalid Address Uri 404' ---
def test_orders_create_invalid_address_uri_404():
    username = generate_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    item_payload = {"itemId": "item_1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_format",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=683  name='Payment Authorize And Retrieve' ---
def test_payment_authorize_and_retrieve():
    order_id = generate_string()
    payment_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 1

    requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    resp_get_2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_2.status_code == 200, f"Expected 200, got {resp_get_2.status_code}: {resp_get_2.text}"
    assert len(resp_get_2.json()) == 2

# --- id=684  name='Payment Authorize Declined Amount Exceeded' ---
def test_payment_authorize_declined_amount_exceeded():
    order_id = generate_string()
    payment_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is False

# --- id=685  name='Shipping Create And Retrieve' ---
def test_shipping_create_and_retrieve():
    order_id = generate_string()
    shipping_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id

# --- id=686  name='Catalogue Items' ---
def test_catalogue_get_items():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert isinstance(items, list)
    if len(items) > 0:
        item_id = items[0]["id"]
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json().get("id") == item_id

# --- id=687  name='Catalogue Invalid Image 404' ---
def test_catalogue_invalid_image_404():
    resp = requests.get(get_url("catalogue", "/catalogue/images/invalid_image_name.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
