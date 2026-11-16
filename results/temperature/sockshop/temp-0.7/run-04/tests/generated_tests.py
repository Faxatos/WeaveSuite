# Tests generated in iteration 04
# Captured: 2026-06-30T11:29:14
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=556  name='User Registration And Conflict' ---
def test_user_registration_and_conflict():
    username = random_string()
    email = f"{username}@example.com"
    payload = {
        "username": username,
        "password": "password123",
        "email": email,
        "firstName": "John",
        "lastName": "Doe"
    }

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    user_data = resp_get.json()
    assert user_data.get("username") == username
    assert user_data.get("email") == email
    assert "password" not in user_data

    resp_conflict = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=557  name='User Login' ---
def test_user_login():
    username = random_string()
    password = "password123"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": password, "email": f"{username}@test.com", "firstName": "A", "lastName": "B"
    }, timeout=10)

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_fail.status_code == 401, f"Expected 401, got {resp_fail.status_code}: {resp_fail.text}"

# --- id=558  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = random_string()
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"
    }, timeout=10)

    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Downing St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id

    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_data = resp_addr_get.json()
    assert addr_data.get("city") == "London"
    assert addr_data.get("postcode") == "EC1A 1BB"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id

    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data.get("ccv") == "123"
    assert card_data.get("expires") == "12/25"
    assert "*" in card_data.get("longNum")

# --- id=559  name='Catalogue Browsing' ---
def test_catalogue_browsing():
    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 5}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if not items:
        pytest.skip("No items in catalogue")

    first_item = items[0]
    item_id = first_item.get("id")

    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json().get("id") == item_id

    resp_invalid = requests.get(get_url("catalogue", "/catalogue/invalid-id-xyz"), timeout=10)
    assert resp_invalid.status_code == 404, f"Expected 404, got {resp_invalid.status_code}: {resp_invalid.text}"

# --- id=560  name='Cart Management' ---
def test_cart_management():
    customer_id = random_string()

    item_payload = {
        "itemId": "item-123",
        "quantity": 2,
        "unitPrice": 15.5
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/item-123"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 2

    update_payload = {
        "itemId": "item-123",
        "quantity": 5,
        "unitPrice": 15.5
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/item-123"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_empty = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_empty.status_code == 200, f"Expected 200, got {resp_empty.status_code}: {resp_empty.text}"
    assert resp_empty.json() == []

# --- id=561  name='Order Placement And Workflow' ---
def test_order_placement_and_workflow():
    username = random_string()
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"
    }, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "city": "London", "country": "UK", "number": "10", "postcode": "EC1A", "street": "Street", "userID": username
    }, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    card_id = resp_card.json().get("id")

    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "sock-1", "quantity": 2, "unitPrice": 10.0
    }, timeout=10)

    order_payload = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id
    assert order_data.get("total") == 20.0

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id

    resp_search = requests.get(get_url("orders", "/orders/search/customerId"), params={"custId": username}, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded = resp_search.json().get("_embedded", {})
    customer_orders = embedded.get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders)

# --- id=562  name='Order Placement Empty Cart 406' ---
def test_order_placement_empty_cart_406():
    username = random_string()
    order_payload = {
        "address": f"/addresses/{username}:123",
        "card": f"/cards/{username}:1234",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=563  name='Order Placement Invalid Composite Id 404' ---
def test_order_placement_invalid_composite_id_404():
    username = random_string()
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "sock-1", "quantity": 2, "unitPrice": 10.0
    }, timeout=10)

    order_payload = {
        "address": "/addresses/invalidformat",
        "card": "/cards/invalidformat",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=564  name='Payment Authorization Limits' ---
def test_payment_authorization_limits():
    order_id = random_string()

    pay_payload_declined = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "111", "expires": "11/11", "longNum": "1111"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp_declined = requests.post(get_url("payment-http", "/payments"), json=pay_payload_declined, timeout=10)
    assert resp_declined.status_code == 200, f"Expected 200, got {resp_declined.status_code}: {resp_declined.text}"
    assert resp_declined.json().get("authorised") is False

    pay_payload_auth = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "111", "expires": "11/11", "longNum": "1111"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp_auth = requests.post(get_url("payment-http", "/payments"), json=pay_payload_auth, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    assert resp_auth.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 2
    assert auths[0].get("authorised") is False
    assert auths[1].get("authorised") is True

# --- id=565  name='Shipping Creation And Retrieval' ---
def test_shipping_creation_and_retrieval():
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
    assert ship_data.get("trackingNumber")

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("trackingNumber") == ship_data.get("trackingNumber")
