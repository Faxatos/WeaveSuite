# Tests generated in iteration 09
# Captured: 2026-06-29T06:13:22
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=144  name='User Registration And Login' ---
def test_user_registration_and_login():
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
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=145  name='User Profile Management' ---
def test_user_profile_management():
    username = random_string()
    password = random_string()

    user_payload = {"username": username, "password": password, "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    resp_get_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addresses = resp_get_addr.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    resp_get_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    cards = resp_get_card.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_get_addr2 = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    addresses2 = resp_get_addr2.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses2)

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    resp_get_card2 = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    cards2 = resp_get_card2.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards2)

    resp_del_cust = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_cust.status_code == 200, f"Expected 200, got {resp_del_cust.status_code}: {resp_del_cust.text}"
    assert resp_del_cust.json().get("status") is True

    resp_del_cust2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_cust2.status_code == 200, f"Expected 200, got {resp_del_cust2.status_code}: {resp_del_cust2.text}"
    assert resp_del_cust2.json().get("status") is False

# --- id=146  name='Catalogue Browsing' ---
def test_catalogue_browsing():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0]["id"]
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"

        resp_invalid = requests.get(get_url("catalogue", "/catalogue/invalid_item_id_123"), timeout=10)
        assert resp_invalid.status_code == 404, f"Expected 404, got {resp_invalid.status_code}: {resp_invalid.text}"

    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

# --- id=147  name='Carts Management' ---
def test_carts_management():
    customer_id = random_string()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp_cat.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert any(i.get("itemId") == item_id for i in cart_items)

    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": unit_price}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json().get("quantity") == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_item_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item_del.status_code == 404, f"Expected 404, got {resp_get_item_del.status_code}: {resp_get_item_del.text}"

    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=148  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
    username = random_string()

    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    addr_payload = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp_cat.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": unit_price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

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
    assert order_data.get("customer", {}).get("username") == username

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders)

    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auths = resp_pay.json()
    assert isinstance(auths, list)
    if auths:
        assert auths[0].get("orderId") == order_id

    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id

# --- id=149  name='Orders Empty Cart Rejection' ---
def test_orders_empty_cart_rejection():
    username = random_string()

    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    addr_payload = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "message" in resp_order.json()

# --- id=150  name='Orders Invalid Composite Id' ---
def test_orders_invalid_composite_id():
    username = random_string()

    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp_cat.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_non_composite_id",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=151  name='Orders Not Found' ---
def test_orders_not_found():
    resp = requests.get(get_url("orders", "/orders/non_existent_order_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=152  name='Payment Authorization Limits' ---
def test_payment_authorization_limits():
    order_id = random_string()

    pay_payload_valid = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp_pay_valid = requests.post(get_url("payment-http", "/payments"), json=pay_payload_valid, timeout=10)
    assert resp_pay_valid.status_code == 200, f"Expected 200, got {resp_pay_valid.status_code}: {resp_pay_valid.text}"
    assert resp_pay_valid.json().get("authorised") is True

    resp_get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    auths = resp_get_pay.json()
    assert len(auths) == 1
    assert auths[0].get("authorised") is True

    pay_payload_invalid = pay_payload_valid.copy()
    pay_payload_invalid["amount"] = 150.0
    resp_pay_invalid = requests.post(get_url("payment-http", "/payments"), json=pay_payload_invalid, timeout=10)
    assert resp_pay_invalid.status_code == 200, f"Expected 200, got {resp_pay_invalid.status_code}: {resp_pay_invalid.text}"
    assert resp_pay_invalid.json().get("authorised") is False

    resp_get_pay2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay2.status_code == 200, f"Expected 200, got {resp_get_pay2.status_code}: {resp_get_pay2.text}"
    auths2 = resp_get_pay2.json()
    assert len(auths2) == 2
    assert auths2[0].get("authorised") is True
    assert auths2[1].get("authorised") is False

# --- id=153  name='Shipping Standalone' ---
def test_shipping_standalone():
    order_id = random_string()

    ship_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=ship_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data.get("orderId") == order_id
    assert "trackingNumber" in ship_data

    resp_get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    assert resp_get_ship.json().get("orderId") == order_id
