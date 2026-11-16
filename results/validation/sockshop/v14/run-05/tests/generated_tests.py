# Tests generated in iteration 05
# Captured: 2026-06-06T20:09:20
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1109  name='Shipping Ship' ---
def test_shipping_ship():
    order_id = f"order_{generate_random_string()}"
    shipping_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "SW1A 1AA",
            "street": "Downing St"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    ship_resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    assert ship_resp.json().get("orderId") == order_id, "Order ID mismatch in shipment response"

    get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_ship.status_code == 200, f"Expected 200, got {get_ship.status_code}: {get_ship.text}"
    assert get_ship.json().get("orderId") == order_id, "Order ID mismatch in shipment verification"

# --- id=1098  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
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

    login_resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

# --- id=1099  name='User Register Conflict Negative' ---
def test_user_register_conflict_negative():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "A",
        "lastName": "B"
    }
    resp1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1100  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "A",
        "lastName": "B"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing St",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    assert addr_id is not None, "Expected address ID in response"

    addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"
    addr_data = addr_get.json()
    assert addr_data.get("city") == address_payload["city"], f"Expected {address_payload['city']}, got {addr_data.get('city')}"
    assert addr_data.get("country") == address_payload["country"], f"Expected {address_payload['country']}, got {addr_data.get('country')}"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    assert card_id is not None, "Expected card ID in response"

    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"
    card_data = card_get.json()
    assert card_data.get("expires") == card_payload["expires"], f"Expected {card_payload['expires']}, got {card_data.get('expires')}"

# --- id=1101  name='Catalogue Items' ---
def test_catalogue_get_items():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if items:
        item_id = items[0].get("id")
        item_resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"
        assert item_resp.json().get("id") == item_id, "Item ID mismatch"

# --- id=1102  name='Catalogue Not Found Negative' ---
def test_catalogue_not_found_negative():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid-id-12345"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1103  name='Carts Cumulative State And' ---
def test_carts_cumulative_state_and_patch():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"
    add_data = add_resp.json()
    assert add_data.get("itemId") == item_payload["itemId"]
    assert add_data.get("quantity") == item_payload["quantity"]
    assert add_data.get("unitPrice") == item_payload["unitPrice"]

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("quantity") == 2, f"Expected quantity 2, got {get_resp.json().get('quantity')}"

    item_payload_2 = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": 10.5
    }
    add_resp_2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_2, timeout=10)
    assert add_resp_2.status_code == 201, f"Expected 201, got {add_resp_2.status_code}: {add_resp_2.text}"

    get_resp_2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp_2.status_code == 200, f"Expected 200, got {get_resp_2.status_code}: {get_resp_2.text}"
    assert get_resp_2.json().get("quantity") == 5, f"Expected quantity 5, got {get_resp_2.json().get('quantity')}"

    patch_payload = {
        "itemId": item_id,
        "quantity": 10,
        "unitPrice": 10.5
    }
    patch_resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_resp_3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp_3.status_code == 200, f"Expected 200, got {get_resp_3.status_code}: {get_resp_3.text}"
    assert get_resp_3.json().get("quantity") == 10, f"Expected quantity 10, got {get_resp_3.json().get('quantity')}"

    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp_4 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp_4.status_code == 404, f"Expected 404, got {get_resp_4.status_code}: {get_resp_4.text}"

# --- id=1104  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 5.0
    }
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)

    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("itemId") == item_id, "Item ID mismatch after merge"

# --- id=1105  name='Carts Merge Not Found Negative' ---
def test_carts_merge_not_found_negative():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"

    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 404, f"Expected 404, got {merge_resp.status_code}: {merge_resp.text}"

# --- id=1106  name='Orders Place Order' ---
def test_orders_place_order():
    username = f"user_{generate_random_string()}"

    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "A",
        "lastName": "B"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing St",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = card_resp.json().get("id")

    item_id = f"item_{generate_random_string()}"
    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 50.0
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

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
    assert order_id is not None, "Order ID should not be None"

    get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order.status_code == 200, f"Expected 200, got {get_order.status_code}: {get_order.text}"
    assert get_order.json().get("id") == order_id, "Order ID mismatch"

# --- id=1107  name='Orders Payment Not Authorized Negative' ---
def test_orders_payment_not_authorized_negative():
    username = f"user_{generate_random_string()}"

    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "A",
        "lastName": "B"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing St",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    addr_id = addr_resp.json().get("id")

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = card_resp.json().get("id")

    item_id = f"item_{generate_random_string()}"
    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 150.0
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"

# --- id=1108  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = f"order_{generate_random_string()}"
    payment_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "SW1A 1AA",
            "street": "Downing St"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "A",
            "lastName": "B"
        },
        "orderId": order_id
    }

    pay_resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json().get("authorised") is True, "Payment should be authorised"
    assert pay_resp.json().get("orderId") == order_id, "Order ID mismatch in response"

    get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay.status_code == 200, f"Expected 200, got {get_pay.status_code}: {get_pay.text}"
    auths = get_pay.json()
    assert isinstance(auths, list) and len(auths) > 0, "Expected at least one authorisation"
    assert auths[0].get("orderId") == order_id, "Order ID mismatch in payment"
