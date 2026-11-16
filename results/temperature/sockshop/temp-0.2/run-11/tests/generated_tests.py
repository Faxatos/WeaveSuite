# Tests generated in iteration 11
# Captured: 2026-06-29T07:19:58
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=162  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
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

    # Verify by getting customer
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username

    # Register again -> 409
    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Login success
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Login failure
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

    # Delete customer
    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

# --- id=163  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # Add address
    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "NW1 6XE",
        "street": "Baker Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Verify address in customer addresses
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addresses = resp_addr_get.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

    # Add card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Verify card in customer cards
    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    cards = resp_card_get.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

    # Delete address
    resp_addr_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_del.status_code == 200, f"Expected 200, got {resp_addr_del.status_code}: {resp_addr_del.text}"

    # Verify address deleted
    resp_addr_get2 = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    addresses2 = resp_addr_get2.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses2)

    # Delete card
    resp_card_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_del.status_code == 200, f"Expected 200, got {resp_card_del.status_code}: {resp_card_del.text}"

    # Verify card deleted
    resp_card_get2 = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    cards2 = resp_card_get2.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards2)

# --- id=164  name='Catalogue Browsing' ---
def test_catalogue_browsing():
    # Get catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)
    assert len(socks) > 0

    sock_id = socks[0]["id"]

    # Get specific sock
    resp_sock = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
    assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
    assert resp_sock.json().get("id") == sock_id

    # Get non-existent sock
    resp_404 = requests.get(get_url("catalogue", "/catalogue/invalid-sock-id-123"), timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

    # Get tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=165  name='Carts Management' ---
def test_carts_management():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp_cat.json()
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }

    # Add item
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verify item in cart
    resp_items = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_items.status_code == 200, f"Expected 200, got {resp_items.status_code}: {resp_items.text}"
    items = resp_items.json()
    assert any(i.get("itemId") == item_id and i.get("quantity") == 2 for i in items)

    # Update item
    item_payload["quantity"] = 5
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify updated item
    resp_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json().get("quantity") == 5

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify item deleted
    resp_item_404 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_item_404.status_code == 404, f"Expected 404, got {resp_item_404.status_code}: {resp_item_404.text}"

    # Delete cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=166  name='Orders Creation Workflow' ---
def test_orders_creation_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@example.com",
        "firstName": "Order", "lastName": "Tester"
    }, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker", "userID": username
    }, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp_cat.json()
    item_id = socks[0]["id"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item_id, "quantity": 1, "unitPrice": socks[0]["price"]
    }, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("customer", {}).get("username") == username

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders)

# --- id=167  name='Orders Creation Empty Cart' ---
def test_orders_creation_empty_cart():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@example.com",
        "firstName": "Empty", "lastName": "Cart"
    }, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker", "userID": username
    }, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
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

# --- id=168  name='Payment Http Authorization' ---
def test_payment_http_authorization():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_payload = {
        "address": {
            "city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123", "expires": "12/25", "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "John", "lastName": "Doe"
        },
        "orderId": order_id
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth_res = resp_pay.json()
    assert auth_res.get("authorised") is True

    resp_get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    auths = resp_get_pay.json()
    assert isinstance(auths, list)
    assert len(auths) > 0
    assert auths[-1].get("orderId") == order_id

    payment_payload["amount"] = 150.0
    resp_pay_declined = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay_declined.status_code == 200, f"Expected 200, got {resp_pay_declined.status_code}: {resp_pay_declined.text}"
    assert resp_pay_declined.json().get("authorised") is False

# --- id=169  name='Shipping Http Shipment' ---
def test_shipping_http_shipment():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    shipping_payload = {
        "address": {
            "city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment.get("orderId") == order_id
    assert "trackingNumber" in shipment

    resp_get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    assert resp_get_ship.json().get("orderId") == order_id
