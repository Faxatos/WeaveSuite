# Tests generated in iteration 03
# Captured: 2026-06-29T01:57:41
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=52  name='Shipping Request' ---
def test_shipping_request():
    order_id = f"order_{uuid.uuid4().hex[:8]}"

    shipping_url = get_url("shipping-http", "/shipping")
    shipping_req = {
        "address": {
            "city": "S City",
            "country": "S Country",
            "number": "3",
            "postcode": "33333",
            "street": "S Street"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(shipping_url, json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id, f"Expected orderId {order_id}, got {resp.text}"
    assert "trackingNumber" in shipment, f"Expected trackingNumber, got {resp.text}"

    get_shipping_url = get_url("shipping-http", f"/shipping/{order_id}")
    resp = requests.get(get_shipping_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id, f"Expected orderId {order_id}, got {resp.text}"

# --- id=44  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    register_url = get_url("user", "/register")
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(register_url, json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    login_url = get_url("user", "/login")
    resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(register_url, json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    customer_url = get_url("user", f"/customers/{username}")
    resp = requests.get(customer_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("username") == username, f"Expected username {username}, got {resp.text}"

    resp = requests.delete(customer_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True, f"Expected status true, got {resp.text}"

# --- id=45  name='User Profile Address And Card' ---
def test_user_profile_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"

    address_url = get_url("user", "/addresses")
    address_data = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp = requests.post(address_url, json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id, f"Expected address id, got {resp.text}"

    cust_addresses_url = get_url("user", f"/customers/{username}/addresses")
    resp = requests.get(cust_addresses_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert len(addresses) > 0, f"Expected at least one address, got {resp.text}"
    assert any(a.get("id") == address_id for a in addresses), f"Expected address {address_id} in {resp.text}"

    card_url = get_url("user", "/cards")
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(card_url, json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id, f"Expected card id, got {resp.text}"

    cust_cards_url = get_url("user", f"/customers/{username}/cards")
    resp = requests.get(cust_cards_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert len(cards) > 0, f"Expected at least one card, got {resp.text}"
    assert any(c.get("id") == card_id for c in cards), f"Expected card {card_id} in {resp.text}"

    del_address_url = get_url("user", f"/addresses/{address_id}")
    resp = requests.delete(del_address_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    del_card_url = get_url("user", f"/cards/{card_id}")
    resp = requests.delete(del_card_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=46  name='Catalogue Listing And Retrieval' ---
def test_catalogue_listing_and_retrieval():
    catalogue_url = get_url("catalogue", "/catalogue")
    resp = requests.get(catalogue_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list), f"Expected list, got {type(items)}"
    assert len(items) > 0, "Expected at least one item in catalogue"

    item_id = items[0].get("id")
    assert item_id, "Expected item to have an id"

    item_url = get_url("catalogue", f"/catalogue/{item_id}")
    resp = requests.get(item_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == item_id, f"Expected id {item_id}, got {resp.text}"

    tags_url = get_url("catalogue", "/tags")
    resp = requests.get(tags_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags = resp.json().get("tags", [])
    assert isinstance(tags, list), f"Expected tags list, got {type(tags)}"

# --- id=47  name='Carts Add Update' ---
def test_carts_add_update_delete():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    catalogue_url = get_url("catalogue", "/catalogue")
    resp = requests.get(catalogue_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if not items:
        pytest.skip("No catalogue items available")
    item_id = items[0]["id"]

    cart_items_url = get_url("carts", f"/carts/{customer_id}/items")
    item_data = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    resp = requests.post(cart_items_url, json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(cart_items_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) > 0, f"Expected items in cart, got {resp.text}"
    assert any(i.get("itemId") == item_id for i in cart_items), f"Expected {item_id} in cart"

    update_data = {"itemId": item_id, "quantity": 5, "unitPrice": 10.0}
    resp = requests.patch(cart_items_url, json=update_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp = requests.get(item_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 5, f"Expected quantity 5, got {resp.text}"

    resp = requests.delete(item_url, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(item_url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=48  name='Carts Merge' ---
def test_carts_merge():
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    catalogue_url = get_url("catalogue", "/catalogue")
    resp = requests.get(catalogue_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if not items:
        pytest.skip("No catalogue items available")
    item_id = items[0]["id"]

    session_cart_url = get_url("carts", f"/carts/{session_id}/items")
    item_data = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    resp = requests.post(session_cart_url, json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    merge_url = get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}")
    resp = requests.get(merge_url, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    customer_cart_url = get_url("carts", f"/carts/{customer_id}/items")
    resp = requests.get(customer_cart_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert any(i.get("itemId") == item_id for i in cart_items), f"Expected {item_id} in customer cart"

# --- id=49  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"

    register_url = get_url("user", "/register")
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Order",
        "lastName": "Tester"
    }
    resp = requests.post(register_url, json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    address_url = get_url("user", "/addresses")
    address_data = {
        "city": "O City",
        "country": "O Country",
        "number": "1",
        "postcode": "11111",
        "street": "O Street",
        "userID": username
    }
    resp = requests.post(address_url, json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")

    card_url = get_url("user", "/cards")
    card_data = {
        "ccv": "111",
        "expires": "11/26",
        "longNum": "1111222233334444",
        "userID": username
    }
    resp = requests.post(card_url, json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    catalogue_url = get_url("catalogue", "/catalogue")
    resp = requests.get(catalogue_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if not items:
        pytest.skip("No catalogue items available")
    item = items[0]
    item_id = item["id"]
    item_price = item.get("price", 10.0)

    cart_items_url = get_url("carts", f"/carts/{username}/items")
    cart_item_data = {"itemId": item_id, "quantity": 2, "unitPrice": item_price}
    resp = requests.post(cart_items_url, json=cart_item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    orders_url = get_url("orders", "/orders")
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(orders_url, json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id, f"Expected order id, got {resp.text}"
    assert order.get("customer", {}).get("username") == username, f"Expected username {username}, got {resp.text}"
    assert order.get("total") == 2 * item_price, f"Expected total {2 * item_price}, got {resp.text}"

    order_get_url = get_url("orders", f"/orders/{order_id}")
    resp = requests.get(order_get_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == order_id, f"Expected order id {order_id}, got {resp.text}"

    payment_url = get_url("payment-http", f"/payments/{order_id}")
    resp = requests.get(payment_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert isinstance(payments, list) and len(payments) > 0, f"Expected payments, got {resp.text}"
    assert payments[0].get("orderId") == order_id, f"Expected payment for order {order_id}, got {resp.text}"

    shipping_url = get_url("shipping-http", f"/shipping/{order_id}")
    resp = requests.get(shipping_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id, f"Expected shipment for order {order_id}, got {resp.text}"

# --- id=50  name='Orders Missing Cart' ---
def test_orders_missing_cart():
    username = f"user_{uuid.uuid4().hex[:8]}"

    register_url = get_url("user", "/register")
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Order",
        "lastName": "Tester"
    }
    requests.post(register_url, json=user_data, timeout=10)

    address_url = get_url("user", "/addresses")
    address_data = {
        "city": "O City",
        "country": "O Country",
        "number": "1",
        "postcode": "11111",
        "street": "O Street",
        "userID": username
    }
    resp = requests.post(address_url, json=address_data, timeout=10)
    address_id = resp.json().get("id")

    card_url = get_url("user", "/cards")
    card_data = {
        "ccv": "111",
        "expires": "11/26",
        "longNum": "1111222233334444",
        "userID": username
    }
    resp = requests.post(card_url, json=card_data, timeout=10)
    card_id = resp.json().get("id")

    orders_url = get_url("orders", "/orders")
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(orders_url, json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=51  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"order_{uuid.uuid4().hex[:8]}"

    payment_url = get_url("payment-http", "/payments")
    payment_req = {
        "address": {
            "city": "P City",
            "country": "P Country",
            "number": "2",
            "postcode": "22222",
            "street": "P Street"
        },
        "amount": 50.0,
        "card": {
            "ccv": "222",
            "expires": "12/26",
            "longNum": "5555666677778888"
        },
        "customer": {
            "firstName": "Pay",
            "lastName": "Ment"
        },
        "orderId": order_id
    }

    resp = requests.post(payment_url, json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is True, f"Expected authorised true, got {resp.text}"
    assert auth.get("orderId") == order_id, f"Expected orderId {order_id}, got {resp.text}"

    get_payment_url = get_url("payment-http", f"/payments/{order_id}")
    resp = requests.get(get_payment_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1, f"Expected 1 authorization, got {resp.text}"
    assert auths[0].get("orderId") == order_id, f"Expected orderId {order_id}, got {resp.text}"
