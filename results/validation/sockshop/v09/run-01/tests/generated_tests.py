# Tests generated in iteration 01
# Captured: 2026-06-04T16:38:29
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=266  name='User Register And Login' ---
def test_user_register_and_login():
    username = random_string()
    password = random_string()
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=267  name='User Register Existing User Conflict' ---
def test_user_register_existing_user_conflict():
    username = random_string()
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=268  name='User Add Address' ---
def test_user_add_address():
    username = random_string()
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {
        "city": "Cityville",
        "country": "Countryland",
        "number": "123",
        "postcode": "12345",
        "street": "Main St",
        "userID": username
    }

    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None, "Expected 'id' in response"

    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data.get("city") == address_data["city"]
    assert get_data.get("country") == address_data["country"]
    assert get_data.get("number") == address_data["number"]
    assert get_data.get("postcode") == address_data["postcode"]
    assert get_data.get("street") == address_data["street"]

# --- id=269  name='User Add Card' ---
def test_user_add_card():
    username = random_string()
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }

    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None, "Expected 'id' in response"

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data.get("ccv") == card_data["ccv"]
    assert get_data.get("expires") == card_data["expires"]
    assert get_data.get("longNum", "").endswith("3456")

# --- id=270  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    if socks:
        sock_id = socks[0]["id"]
        resp_get = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
        assert resp_get.json().get("id") == sock_id

# --- id=271  name='Catalogue Nonexistent' ---
def test_catalogue_get_nonexistent():
    resp = requests.get(get_url("catalogue", "/catalogue/nonexistent-id-123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=272  name='Carts Add And Item' ---
def test_carts_add_and_get_item():
    customer_id = random_string()
    item_id = random_string()
    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.50
    }

    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()
    assert resp_json.get("itemId") == item_data["itemId"]
    assert resp_json.get("quantity") == item_data["quantity"]
    assert resp_json.get("unitPrice") == item_data["unitPrice"]

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data.get("itemId") == item_data["itemId"]
    assert get_data.get("quantity") == item_data["quantity"]
    assert get_data.get("unitPrice") == item_data["unitPrice"]

# --- id=273  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = random_string()
    item_id = random_string()
    item_data = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 10.00
    }

    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=274  name='Orders Create Order' ---
def test_orders_create_order():
    username = random_string()
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {
        "city": "Cityville",
        "country": "Countryland",
        "number": "123",
        "postcode": "12345",
        "street": "Main St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp_addr.json().get("id")

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp_card.json().get("id")

    item_data = {
        "itemId": "03fef6ac-1896-4ce8-bd69-b798f85c6e0b",
        "quantity": 1,
        "unitPrice": 50.00
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

    order_data = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp_order = requests.post(get_url("orders", "/orders"), json=order_data, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")
    assert order_id is not None

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("id") == order_id

# --- id=275  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    username = random_string()
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {
        "city": "Cityville",
        "country": "Countryland",
        "number": "123",
        "postcode": "12345",
        "street": "Main St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp_addr.json().get("id")

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp_card.json().get("id")

    item_data = {
        "itemId": "03fef6ac-1896-4ce8-bd69-b798f85c6e0b",
        "quantity": 1,
        "unitPrice": 150.00
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

    order_data = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp_order = requests.post(get_url("orders", "/orders"), json=order_data, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=276  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = str(uuid.uuid4())
    payment_data = {
        "address": {
            "city": "Cityville",
            "country": "Countryland",
            "number": "123",
            "postcode": "12345",
            "street": "Main St"
        },
        "amount": 50.00,
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

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) > 0
    assert auths[0].get("authorised") is True
    assert auths[0].get("orderId") == order_id

# --- id=277  name='Shipping Create Shipment' ---
def test_shipping_create_shipment():
    order_id = str(uuid.uuid4())
    shipping_data = {
        "address": {
            "city": "Cityville",
            "country": "Countryland",
            "number": "123",
            "postcode": "12345",
            "street": "Main St"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()
    assert resp_json.get("orderId") == order_id
    assert "carrier" in resp_json
    assert "trackingNumber" in resp_json

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data.get("orderId") == order_id
    assert get_data.get("carrier") == resp_json.get("carrier")
    assert get_data.get("trackingNumber") == resp_json.get("trackingNumber")
