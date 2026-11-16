# Tests generated in iteration 08
# Captured: 2026-06-06T14:30:55
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1008  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{random_string()}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify creation
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1009  name='User Register Duplicate' ---
def test_user_register_duplicate():
    username = f"user_{random_string()}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1010  name='User Login Invalid' ---
def test_user_login_invalid():
    resp = requests.get(get_url("user", "/login"), auth=("invalid_user", "wrong_pass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1011  name='Carts Add Increment' ---
def test_carts_add_increment_delete():
    customer_id = f"cust_{random_string()}"
    item_id = f"item_{random_string()}"

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }

    # Add item
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verify addition
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 2, f"Expected quantity 2, got {resp_get.json().get('quantity')}"
    assert resp_get.json()["unitPrice"] == 10.5, f"Expected unitPrice 10.5, got {resp_get.json().get('unitPrice')}"

    # Increment item (Cumulative state)
    item_payload_inc = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": 10.5
    }
    resp_inc = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_inc, timeout=10)
    assert resp_inc.status_code == 201, f"Expected 201, got {resp_inc.status_code}: {resp_inc.text}"

    # Verify cumulative state
    resp_get_inc = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_inc.status_code == 200, f"Expected 200, got {resp_get_inc.status_code}: {resp_get_inc.text}"
    assert resp_get_inc.json()["quantity"] == 5, f"Expected quantity 5, got {resp_get_inc.json().get('quantity')}"

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify deletion
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=1012  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{random_string()}"
    session_id = f"sess_{random_string()}"
    item_id = f"item_{random_string()}"

    # Add item to session cart
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    resp_add = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Merge session cart into customer cart
    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    # Verify item is in customer cart
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["itemId"] == item_id, f"Expected itemId {item_id}, got {resp_get.json().get('itemId')}"

# --- id=1013  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{random_string()}"
    session_id = f"sess_{random_string()}"

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=1014  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"

    items = resp_list.json()
    if items:
        item_id = items[0]["id"]
        resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
        assert resp_get.json()["id"] == item_id, f"Expected id {item_id}, got {resp_get.json().get('id')}"

# --- id=1015  name='Catalogue Not Found' ---
def test_catalogue_get_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_nonexistent_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1016  name='Orders Create And Retrieve' ---
def test_orders_create_and_retrieve():
    username = f"user_{random_string()}"

    # Register user
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # Add address
    addr_payload = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json()["id"]

    # Verify address
    resp_addr_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"

    # Add card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    # Verify card
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"

    # Add item to cart (amount <= 100 for authorized payment)
    item_payload = {"itemId": "item1", "quantity": 1, "unitPrice": 50.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    # Create order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data["id"]

    # Verify order retrieval
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json()["id"] == order_id, f"Expected order id {order_id}, got {resp_order_get.json().get('id')}"

    # Verify order search
    resp_order_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_order_search.status_code == 200, f"Expected 200, got {resp_order_search.status_code}: {resp_order_search.text}"

# --- id=1017  name='Orders Payment Not Authorized' ---
def test_orders_payment_not_authorized():
    username = f"user_{random_string()}"

    # Register user
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # Add address
    addr_payload = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    address_id = resp_addr.json()["id"]

    # Add card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json()["id"]

    # Add item to cart (amount > 100 for unauthorized payment)
    item_payload = {"itemId": "item1", "quantity": 1, "unitPrice": 150.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    # Create order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1018  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = f"order_{random_string()}"
    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json()["authorised"] is True, f"Expected authorised True, got {resp_pay.json().get('authorised')}"

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert isinstance(auths, list) and len(auths) > 0, "Expected non-empty list of authorizations"
    assert auths[0]["orderId"] == order_id, f"Expected orderId {order_id}, got {auths[0].get('orderId')}"

# --- id=1019  name='Shipping Ship' ---
def test_shipping_ship():
    order_id = f"order_{random_string()}"
    shipping_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 2,
        "orderId": order_id
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json()["orderId"] == order_id, f"Expected orderId {order_id}, got {resp_ship.json().get('orderId')}"

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id, f"Expected orderId {order_id}, got {resp_get.json().get('orderId')}"
