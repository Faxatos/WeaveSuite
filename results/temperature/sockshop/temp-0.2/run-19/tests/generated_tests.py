# Tests generated in iteration 08
# Captured: 2026-06-29T12:15:31
# Count:    18
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=251  name='User Register And Conflict' ---
def test_user_register_and_conflict():
    username = f"user_{generate_random_string()}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username, "Username mismatch"

    resp_conflict = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=252  name='User Login' ---
def test_user_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_fail.status_code == 401, f"Expected 401, got {resp_fail.status_code}: {resp_fail.text}"

# --- id=253  name='User Add And Address' ---
def test_user_add_and_delete_address():
    username = f"user_{generate_random_string()}"
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None, "Expected address id in response"

    resp_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    addresses = resp_get.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == address_id for a in addresses), "Address not found in customer addresses"

    resp_del = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_get_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    addresses_after = resp_get_after.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses_after), "Address still found after deletion"

# --- id=254  name='User Add And Card' ---
def test_user_add_and_delete_card():
    username = f"user_{generate_random_string()}"
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None, "Expected card id in response"

    resp_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cards = resp_get.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards), "Card not found in customer cards"

    resp_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_get_after = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    cards_after = resp_get_after.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards_after), "Card still found after deletion"

# --- id=255  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{generate_random_string()}"
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True, "Expected status true for deleted customer"

    resp_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_again.status_code == 200, f"Expected 200, got {resp_again.status_code}: {resp_again.text}"
    assert resp_again.json().get("status") is False, "Expected status false for non-existent customer"

# --- id=256  name='Catalogue Items' ---
def test_catalogue_get_items():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list), "Expected catalogue to be a list"

    if items:
        item_id = items[0].get("id")
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json().get("id") == item_id, "Item ID mismatch"

# --- id=257  name='Catalogue Size' ---
def test_catalogue_get_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json(), "Expected size in response"

# --- id=258  name='Catalogue Tags' ---
def test_catalogue_get_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json(), "Expected tags in response"

# --- id=259  name='Carts Add And Update Item' ---
def test_carts_add_and_update_item():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }

    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i.get("itemId") == item_id and i.get("quantity") == 2 for i in items), "Item not found or quantity mismatch"

    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 10.5
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_after = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    items_after = resp_get_after.json()
    assert any(i.get("itemId") == item_id and i.get("quantity") == 5 for i in items_after), "Item quantity not updated"

# --- id=260  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 10.0
    }
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=261  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{generate_random_string()}"
    item_payload = {
        "itemId": "item1",
        "quantity": 1,
        "unitPrice": 10.0
    }
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0, "Expected empty cart after deletion"

# --- id=262  name='Carts Merge' ---
def test_carts_merge():
    session_id = f"sess_{generate_random_string()}"
    customer_id = f"cust_{generate_random_string()}"

    item_payload = {
        "itemId": "item_merge",
        "quantity": 3,
        "unitPrice": 15.0
    }
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i.get("itemId") == "item_merge" for i in items), "Merged item not found in customer cart"

# --- id=263  name='Orders Create And' ---
def test_orders_create_and_get():
    username = f"user_{generate_random_string()}"

    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    address_id = resp_addr.json().get("id")

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    item_payload = {
        "itemId": "item1",
        "quantity": 2,
        "unitPrice": 10.0
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"

    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id is not None, "Expected order ID in response"

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json().get("id") == order_id, "Order ID mismatch"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders), "Order not found in customer search"

# --- id=264  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    address_id = resp_addr.json().get("id")

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=265  name='Orders Create Invalid Composite Id' ---
def test_orders_create_invalid_composite_id():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    item_payload = {
        "itemId": "item1",
        "quantity": 2,
        "unitPrice": 10.0
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_id_format",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=266  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = f"order_{generate_random_string()}"
    payment_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "EC1A 1BB",
            "street": "Baker St"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "Test",
            "lastName": "User"
        },
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data.get("authorised") is True, "Expected payment to be authorised"

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert isinstance(auths, list) and len(auths) > 0, "Expected list of authorizations"
    assert auths[-1].get("orderId") == order_id, "Order ID mismatch in authorization"

# --- id=267  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = f"order_{generate_random_string()}"
    payment_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "EC1A 1BB",
            "street": "Baker St"
        },
        "amount": 150.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "Test",
            "lastName": "User"
        },
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data.get("authorised") is False, "Expected payment to be declined for amount > 100"

# --- id=268  name='Shipping Ship And' ---
def test_shipping_ship_and_get():
    order_id = f"order_{generate_random_string()}"
    shipping_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "EC1A 1BB",
            "street": "Baker St"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment_data = resp.json()
    assert shipment_data.get("orderId") == order_id, "Order ID mismatch in shipment"

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id, "Order ID mismatch in fetched shipment"
