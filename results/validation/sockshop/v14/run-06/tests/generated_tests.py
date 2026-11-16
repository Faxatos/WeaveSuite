# Tests generated in iteration 06
# Captured: 2026-06-06T20:46:18
# Count:    23
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1110  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "John",
        "lastName": "Doe"
    }

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1111  name='User Registration Conflict Negative' ---
def test_user_registration_conflict_negative():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "A",
        "lastName": "B"
    }

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=1112  name='User Login Unauthorized Negative' ---
def test_user_login_unauthorized_negative():
    resp = requests.get(get_url("user", "/login"), auth=("invalid_user", "wrong_pass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1113  name='User Address And Card Lifecycle' ---
def test_user_address_and_card_lifecycle():
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
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_data = resp_addr_get.json()
    assert addr_data.get("city") == address_payload["city"], f"Expected {address_payload['city']}, got {addr_data.get('city')}"
    assert addr_data.get("country") == address_payload["country"], f"Expected {address_payload['country']}, got {addr_data.get('country')}"
    assert addr_data.get("number") == address_payload["number"], f"Expected {address_payload['number']}, got {addr_data.get('number')}"
    assert addr_data.get("postcode") == address_payload["postcode"], f"Expected {address_payload['postcode']}, got {addr_data.get('postcode')}"
    assert addr_data.get("street") == address_payload["street"], f"Expected {address_payload['street']}, got {addr_data.get('street')}"

    resp_addr_coll = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_coll.status_code == 200, f"Expected 200, got {resp_addr_coll.status_code}: {resp_addr_coll.text}"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data.get("ccv") == card_payload["ccv"], f"Expected {card_payload['ccv']}, got {card_data.get('ccv')}"
    assert card_data.get("expires") == card_payload["expires"], f"Expected {card_payload['expires']}, got {card_data.get('expires')}"

    resp_card_coll = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_coll.status_code == 200, f"Expected 200, got {resp_card_coll.status_code}: {resp_card_coll.text}"

    resp_addr_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_del.status_code == 200, f"Expected 200, got {resp_addr_del.status_code}: {resp_addr_del.text}"

    resp_card_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_del.status_code == 200, f"Expected 200, got {resp_card_del.status_code}: {resp_card_del.text}"

# --- id=1114  name='User Addresses Always Empty' ---
def test_user_addresses_always_empty():
    resp = requests.get(get_url("user", "/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert len(data.get("_embedded", {}).get("address", [])) == 0, "Expected empty address list"

# --- id=1115  name='User Cards Always Empty' ---
def test_user_cards_always_empty():
    resp = requests.get(get_url("user", "/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert len(data.get("_embedded", {}).get("card", [])) == 0, "Expected empty card list"

# --- id=1116  name='User Deletion' ---
def test_user_deletion():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "A",
        "lastName": "B"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_get_all = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_get_all.status_code == 200, f"Expected 200, got {resp_get_all.status_code}: {resp_get_all.text}"
    assert username not in resp_get_all.text, f"Expected user {username} to be deleted"

# --- id=1117  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    if len(socks) > 0:
        sock_id = socks[0]["id"]
        resp_get = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
        sock_data = resp_get.json()
        assert sock_data["id"] == sock_id, f"Expected {sock_id}, got {sock_data['id']}"

# --- id=1118  name='Catalogue Not Found Negative' ---
def test_catalogue_not_found_negative():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_sock_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1119  name='Catalogue Images' ---
def test_catalogue_images():
    resp = requests.get(get_url("catalogue", "/catalogue/images/invalid_image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1120  name='Catalogue Size' ---
def test_catalogue_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json(), f"Expected 'size' in response, got {resp.json()}"

# --- id=1121  name='Catalogue Tags' ---
def test_catalogue_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json(), f"Expected 'tags' in response, got {resp.json()}"

# --- id=1122  name='Carts Cumulative State And' ---
def test_carts_cumulative_state_and_patch():
    customer_id = f"cust_{generate_random_string()}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200
    socks = resp_cat.json()
    if not socks:
        pytest.skip("No items in catalogue to add to cart")
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    item_payload_1 = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }

    resp_add_1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_1, timeout=10)
    assert resp_add_1.status_code == 201, f"Expected 201, got {resp_add_1.status_code}: {resp_add_1.text}"
    added_item = resp_add_1.json()
    assert added_item["itemId"] == item_payload_1["itemId"], f"Expected {item_payload_1['itemId']}, got {added_item.get('itemId')}"
    assert added_item["quantity"] == item_payload_1["quantity"], f"Expected {item_payload_1['quantity']}, got {added_item.get('quantity')}"
    assert added_item["unitPrice"] == item_payload_1["unitPrice"], f"Expected {item_payload_1['unitPrice']}, got {added_item.get('unitPrice')}"

    resp_get_1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_1.status_code == 200, f"Expected 200, got {resp_get_1.status_code}: {resp_get_1.text}"
    assert resp_get_1.json()["quantity"] == 2, f"Expected 2, got {resp_get_1.json().get('quantity')}"

    item_payload_2 = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": unit_price
    }
    resp_add_2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_2, timeout=10)
    assert resp_add_2.status_code == 201, f"Expected 201, got {resp_add_2.status_code}: {resp_add_2.text}"

    resp_get_2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_2.status_code == 200, f"Expected 200, got {resp_get_2.status_code}: {resp_get_2.text}"
    assert resp_get_2.json()["quantity"] == 5, f"Expected 5, got {resp_get_2.json().get('quantity')}"

    item_payload_patch = {
        "itemId": item_id,
        "quantity": 10,
        "unitPrice": unit_price
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_patch, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_3.status_code == 200, f"Expected 200, got {resp_get_3.status_code}: {resp_get_3.text}"
    assert resp_get_3.json()["quantity"] == 10, f"Expected 10, got {resp_get_3.json().get('quantity')}"

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_4 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_4.status_code == 404, f"Expected 404, got {resp_get_4.status_code}: {resp_get_4.text}"

# --- id=1123  name='Carts Item Not Found Negative' ---
def test_carts_item_not_found_negative():
    customer_id = f"cust_{generate_random_string()}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/invalid_item"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1124  name='Carts Merge Not Found Negative' ---
def test_carts_merge_not_found_negative():
    customer_id = f"cust_{generate_random_string()}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=invalid_session"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1125  name='Carts Deletion' ---
def test_carts_deletion():
    customer_id = f"cust_{generate_random_string()}"

    item_payload = {
        "itemId": "sock_1",
        "quantity": 1,
        "unitPrice": 10.0
    }
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_items = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_items.status_code == 200, f"Expected 200, got {resp_items.status_code}: {resp_items.text}"
    assert len(resp_items.json()) == 0, "Expected cart to be empty after deletion"

# --- id=1126  name='Orders Creation Workflow' ---
def test_orders_creation_workflow():
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
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    addr_id = resp_addr.json().get("id")

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200
    socks = resp_cat.json()
    if not socks:
        pytest.skip("No items in catalogue")
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
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

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id, f"Expected {order_id}, got {resp_order_get.json().get('id')}"

    resp_order_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_order_search.status_code == 200, f"Expected 200, got {resp_order_search.status_code}: {resp_order_search.text}"

# --- id=1127  name='Orders Payment Declined Negative' ---
def test_orders_payment_declined_negative():
    username = f"user_{generate_random_string()}"
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    addr_id = resp_addr.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200
    socks = resp_cat.json()
    if not socks:
        pytest.skip("No items in catalogue")
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    item_payload = {
        "itemId": item_id,
        "quantity": 100,
        "unitPrice": unit_price
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1128  name='Orders Not Found Negative' ---
def test_orders_not_found_negative():
    resp = requests.get(get_url("orders", "/orders/invalid_order_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1129  name='Orders Search Not Found Negative' ---
def test_orders_search_not_found_negative():
    resp = requests.get(get_url("orders", "/orders/search/customerId?custId=invalid_cust_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1130  name='Payment Authorization' ---
def test_payment_authorization():
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
            "firstName": "John",
            "lastName": "Doe"
        },
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data.get("authorised") is True, f"Expected True, got {auth_data.get('authorised')}"
    assert auth_data.get("orderId") == order_id, f"Expected {order_id}, got {auth_data.get('orderId')}"

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auth_list = resp_get.json()
    assert len(auth_list) > 0, "Expected at least one authorization"
    assert auth_list[0].get("orderId") == order_id, f"Expected {order_id}, got {auth_list[0].get('orderId')}"

# --- id=1131  name='Payment Declined' ---
def test_payment_declined():
    order_id = f"order_{generate_random_string()}"
    payment_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "SW1A 1AA",
            "street": "Downing St"
        },
        "amount": 150.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "John",
            "lastName": "Doe"
        },
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data.get("authorised") is False, f"Expected False, got {auth_data.get('authorised')}"

# --- id=1132  name='Shipping Workflow' ---
def test_shipping_workflow():
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

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment_data = resp.json()
    assert shipment_data.get("orderId") == order_id, f"Expected {order_id}, got {shipment_data.get('orderId')}"

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    shipment_get_data = resp_get.json()
    assert shipment_get_data.get("orderId") == order_id, f"Expected {order_id}, got {shipment_get_data.get('orderId')}"
    assert shipment_get_data.get("carrier") == shipment_data.get("carrier"), f"Expected {shipment_data.get('carrier')}, got {shipment_get_data.get('carrier')}"
