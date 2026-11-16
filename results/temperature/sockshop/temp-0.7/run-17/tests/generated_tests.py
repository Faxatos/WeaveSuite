# Tests generated in iteration 19
# Captured: 2026-06-30T20:18:29
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=722  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "passWord123!"

    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    reg_url = get_url("user", "/register")
    resp = requests.post(reg_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify customer exists
    cust_url = get_url("user", f"/customers/{username}")
    cust_resp = requests.get(cust_url, timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json().get("username") == username, f"Expected username {username}, got {cust_resp.json()}"

    # Login
    login_url = get_url("user", "/login")
    login_resp = requests.get(login_url, auth=HTTPBasicAuth(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    # Conflict: Register again
    resp_conflict = requests.post(reg_url, json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=723  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "123", "email": "a@b.c"}, timeout=10)

    # Add address
    addr_payload = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    assert addr_id, f"Expected address id in response: {addr_resp.text}"

    # Verify address in collection
    cust_addr_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert cust_addr_resp.status_code == 200, f"Expected 200, got {cust_addr_resp.status_code}: {cust_addr_resp.text}"
    addresses = cust_addr_resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses), f"Address {addr_id} not found in {addresses}"

    # Add card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    assert card_id, f"Expected card id in response: {card_resp.text}"

    # Verify card in collection
    cust_card_resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert cust_card_resp.status_code == 200, f"Expected 200, got {cust_card_resp.status_code}: {cust_card_resp.text}"
    cards = cust_card_resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards), f"Card {card_id} not found in {cards}"

    # Delete address
    del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert del_addr.status_code == 200, f"Expected 200, got {del_addr.status_code}: {del_addr.text}"

    # Delete card
    del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert del_card.status_code == 200, f"Expected 200, got {del_card.status_code}: {del_card.text}"

# --- id=724  name='Catalogue Retrieval And Not Found' ---
def test_catalogue_retrieval_and_not_found():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert isinstance(items, list), "Expected catalogue to be a list"

    if items:
        item_id = items[0]["id"]
        item_resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"
        assert item_resp.json().get("id") == item_id, f"Expected id {item_id}, got {item_resp.json()}"

    fake_id = "non_existent_id_12345"
    fake_resp = requests.get(get_url("catalogue", f"/catalogue/{fake_id}"), timeout=10)
    assert fake_resp.status_code == 404, f"Expected 404, got {fake_resp.status_code}: {fake_resp.text}"

# --- id=725  name='Carts Add Update Items' ---
def test_carts_add_update_delete_items():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    # Add item
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.5}
    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    # Verify item in cart
    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert any(i.get("itemId") == item_id and i.get("quantity") == 1 for i in items), f"Item {item_id} not found or wrong quantity in {items}"

    # Update item
    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 10.5}
    upd_resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert upd_resp.status_code == 202, f"Expected 202, got {upd_resp.status_code}: {upd_resp.text}"

    # Verify update
    get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_item.status_code == 200, f"Expected 200, got {get_item.status_code}: {get_item.text}"
    assert get_item.json().get("quantity") == 5, f"Expected quantity 5, got {get_item.json()}"

    # Delete item
    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    # Verify deletion
    get_item_after = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_item_after.status_code == 404, f"Expected 404, got {get_item_after.status_code}: {get_item_after.text}"

    # Delete cart
    del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert del_cart.status_code == 202, f"Expected 202, got {del_cart.status_code}: {del_cart.text}"

# --- id=726  name='Orders Creation And Search' ---
def test_orders_creation_and_search():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "123", "email": "a@b.c", "firstName": "A", "lastName": "B"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    item_id = "3395a43e-2d88-40de-b95f-e00e1502085b"
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 2, "unitPrice": 15.0}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"

    order_data = order_resp.json()
    order_id = order_data.get("id")
    assert order_id, f"Expected order id, got {order_data}"
    assert order_data["customer"]["username"] == username, f"Expected customer {username}, got {order_data['customer']}"
    assert len(order_data["items"]) > 0, "Expected items in order"

    # Verify order retrieval
    get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order.status_code == 200, f"Expected 200, got {get_order.status_code}: {get_order.text}"
    assert get_order.json().get("id") == order_id, f"Expected id {order_id}, got {get_order.json()}"

    # Verify customer orders search
    search_resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    customer_orders = search_resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders), f"Order {order_id} not found in {customer_orders}"

# --- id=727  name='Orders Negative Invalid Uri' ---
def test_orders_negative_invalid_uri():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "123", "email": "a@b.c"}, timeout=10)
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    # Invalid card URI (not composite)
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:1234",
        "card": "/cards/invalid_format", 
        "items": f"/carts/{username}/items"
    }

    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404 for syntactically invalid card URI, got {resp.status_code}: {resp.text}"

# --- id=728  name='Orders Negative Missing Field' ---
def test_orders_negative_missing_field():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "123", "email": "a@b.c"}, timeout=10)
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    # Missing 'card' field
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:1234",
        "items": f"/carts/{username}/items"
    }

    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406 for missing required field, got {resp.status_code}: {resp.text}"

# --- id=729  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_payload = {
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    pay_resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    auth_data = pay_resp.json()
    assert auth_data.get("authorised") is True, f"Expected authorized payment, got {auth_data}"
    assert auth_data.get("orderId") == order_id, f"Expected orderId {order_id}, got {auth_data}"

    # Verify payment retrieval
    get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay.status_code == 200, f"Expected 200, got {get_pay.status_code}: {get_pay.text}"
    payments = get_pay.json()
    assert isinstance(payments, list) and len(payments) == 1, f"Expected 1 payment, got {payments}"
    assert payments[0].get("orderId") == order_id, f"Expected orderId {order_id}, got {payments[0]}"

    # Duplicate payment to check repetition constraint
    pay_resp_2 = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert pay_resp_2.status_code == 200, f"Expected 200, got {pay_resp_2.status_code}: {pay_resp_2.text}"

    get_pay_2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay_2.status_code == 200, f"Expected 200, got {get_pay_2.status_code}: {get_pay_2.text}"
    assert len(get_pay_2.json()) == 2, f"Expected 2 payments appended, got {len(get_pay_2.json())}"

# --- id=730  name='Payment Negative Amount Limit' ---
def test_payment_negative_amount_limit():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_payload = {
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "St"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    pay_resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    auth_data = pay_resp.json()
    assert auth_data.get("authorised") is False, f"Expected declined payment for amount > 100, got {auth_data}"

# --- id=731  name='Shipping Creation And Retrieval' ---
def test_shipping_creation_and_retrieval():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    shipping_payload = {
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "St"},
        "itemCount": 3,
        "orderId": order_id
    }

    ship_resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    ship_data = ship_resp.json()
    assert ship_data.get("orderId") == order_id, f"Expected orderId {order_id}, got {ship_data}"
    assert "carrier" in ship_data, f"Expected carrier in response, got {ship_data}"

    # Verify shipment retrieval
    get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_ship.status_code == 200, f"Expected 200, got {get_ship.status_code}: {get_ship.text}"
    get_ship_data = get_ship.json()
    assert get_ship_data.get("orderId") == order_id, f"Expected orderId {order_id}, got {get_ship_data}"
    assert get_ship_data.get("trackingNumber") == ship_data.get("trackingNumber"), f"Expected tracking number {ship_data.get('trackingNumber')}, got {get_ship_data}"
