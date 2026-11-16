# Tests generated in iteration 09
# Captured: 2026-06-06T15:06:12
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1020  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{generate_random_string()}"
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

    # Verify creation via GET
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username, f"Expected username {username}, got {resp_get.json()}"

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1021  name='User Register Duplicate' ---
def test_user_register_duplicate():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # First registration
    resp1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    # Duplicate registration
    resp2 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1022  name='User Login Invalid' ---
def test_user_login_invalid():
    resp = requests.get(get_url("user", "/login"), auth=("invalid_user", "invalid_pass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1023  name='Carts Add And Increment Item' ---
def test_carts_add_and_increment_item():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    item_payload_1 = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 10.5
    }

    # Add item
    resp1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_1, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    # Verify item added
    resp_get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    assert resp_get1.json().get("quantity") == 1, f"Expected quantity 1, got {resp_get1.json()}"
    assert resp_get1.json().get("unitPrice") == 10.5, f"Expected unitPrice 10.5, got {resp_get1.json()}"

    item_payload_2 = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }

    # Increment item
    resp2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_2, timeout=10)
    assert resp2.status_code == 201, f"Expected 201, got {resp2.status_code}: {resp2.text}"

    # Verify cumulative state
    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 3, f"Expected cumulative quantity 3, got {resp_get2.json()}"

# --- id=1024  name='Carts Item Not Found' ---
def test_carts_item_not_found():
    customer_id = f"cust_{generate_random_string()}"
    item_id = "nonexistent_item"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1025  name='Catalogue Items' ---
def test_catalogue_get_items():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if items:
        item = items[0]
        item_id = item.get("id")

        # Get specific item
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json().get("id") == item_id, "Item ID mismatch"

        image_urls = item.get("imageUrl", [])
        if image_urls:
            image_path = image_urls[0].split("/")[-1]
            resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_path}"), timeout=10)
            assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

# --- id=1026  name='Catalogue Item Not Found' ---
def test_catalogue_item_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_id_12345"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1027  name='Orders Place Order Success' ---
def test_orders_place_order_success():
    username = f"user_{generate_random_string()}"

    # Register user
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # Add Address
    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1",
        "street": "Baker St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json().get("id")

    # Verify Address
    resp_addr_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert resp_addr_get.json().get("city") == "London"

    # Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    # Verify Card
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    assert resp_card_get.json().get("ccv") == "123"

    # Add Item to Cart (amount <= 100 for successful payment)
    item_payload = {
        "itemId": "03fef6ac-1896-4ce8-bd69-b798f85c6e0b",
        "quantity": 1,
        "unitPrice": 50.0
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")

    # Verify Order
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id
    assert resp_order_get.json().get("payment", {}).get("authorised") is True

# --- id=1028  name='Orders Payment Not Authorized' ---
def test_orders_payment_not_authorized():
    username = f"user_{generate_random_string()}"

    # Register user
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # Add Address
    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1",
        "street": "Baker St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    address_id = resp_addr.json().get("id")

    # Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    # Add Item to Cart (amount > 100 for declined payment)
    item_payload = {
        "itemId": "03fef6ac-1896-4ce8-bd69-b798f85c6e0b",
        "quantity": 1,
        "unitPrice": 150.0
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1029  name='Payment Authorize And Retrieve' ---
def test_payment_authorize_and_retrieve():
    order_id = f"order_{generate_random_string()}"
    payment_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "W1",
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

    # Authorize payment
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True, "Expected payment to be authorised"

    # Retrieve payment
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert isinstance(auths, list) and len(auths) > 0, "Expected at least one authorization"
    assert auths[0].get("orderId") == order_id

# --- id=1030  name='Shipping Create And Retrieve' ---
def test_shipping_create_and_retrieve():
    order_id = f"order_{generate_random_string()}"
    shipping_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "W1",
            "street": "Baker St"
        },
        "itemCount": 2,
        "orderId": order_id
    }

    # Create shipping
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id

    # Retrieve shipping
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
