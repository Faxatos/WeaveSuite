# Tests generated in iteration 02
# Captured: 2026-06-06T10:18:16
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=943  name='Payment Authorize Success' ---
def test_payment_authorize_success():
    order_id = str(uuid.uuid4())
    payment_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A", "street": "Main"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }

    pay_resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json().get("authorised") is True, "Expected payment to be authorised"

    get_pay_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay_resp.status_code == 200, f"Expected 200, got {get_pay_resp.status_code}: {get_pay_resp.text}"
    auths = get_pay_resp.json()
    assert len(auths) > 0, "Expected at least one authorization"
    assert auths[0].get("orderId") == order_id, "Order ID mismatch"

# --- id=944  name='Shipping Ship Request Success' ---
def test_shipping_ship_request_success():
    order_id = str(uuid.uuid4())
    shipping_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A", "street": "Main"},
        "itemCount": 2,
        "orderId": order_id
    }

    ship_resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    assert ship_resp.json().get("orderId") == order_id, "Order ID mismatch"

    get_ship_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_ship_resp.status_code == 200, f"Expected 200, got {get_ship_resp.status_code}: {get_ship_resp.text}"
    assert get_ship_resp.json().get("orderId") == order_id, "Order ID mismatch"

# --- id=935  name='User Register And Login' ---
def test_user_register_and_login():
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

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify via GET
    get_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    get_data = get_resp.json()
    assert get_data.get("username") == username, f"Expected username {username}, got {get_data.get('username')}"
    assert get_data.get("firstName") == "John", f"Expected firstName John, got {get_data.get('firstName')}"

    # Login
    login_resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

# --- id=936  name='User Register Existing User 409' ---
def test_user_register_existing_user_409():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    # Register first time
    resp1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    # Register second time
    resp2 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=937  name='User Login Unauthorized 401' ---
def test_user_login_unauthorized_401():
    username = f"user_{generate_random_string()}"
    login_resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpassword"), timeout=10)
    assert login_resp.status_code == 401, f"Expected 401, got {login_resp.status_code}: {login_resp.text}"

# --- id=938  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # Add Address
    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Main St",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")
    assert addr_id is not None, "Expected address id in response"

    # Verify Address
    get_addr_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert get_addr_resp.status_code == 200, f"Expected 200, got {get_addr_resp.status_code}: {get_addr_resp.text}"
    addresses = get_addr_resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses), "Added address not found in customer addresses"

    # Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    assert card_id is not None, "Expected card id in response"

    # Verify Card
    get_card_resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert get_card_resp.status_code == 200, f"Expected 200, got {get_card_resp.status_code}: {get_card_resp.text}"
    cards = get_card_resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards), "Added card not found in customer cards"

# --- id=939  name='Catalogue Item And Not Found 404' ---
def test_catalogue_get_item_and_not_found_404():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "Expected at least one item in catalogue"

    item_id = items[0]["id"]

    # Get specific item
    item_resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"
    assert item_resp.json().get("id") == item_id, "Item ID mismatch"

    # Get invalid item
    invalid_resp = requests.get(get_url("catalogue", "/catalogue/invalid-id-12345"), timeout=10)
    assert invalid_resp.status_code == 404, f"Expected 404, got {invalid_resp.status_code}: {invalid_resp.text}"

# --- id=940  name='Carts Add Item Multiple Times Cumulative State' ---
def test_carts_add_item_multiple_times_cumulative_state():
    customer_id = f"cust_{generate_random_string()}"

    # Get an item from catalogue
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item = cat_resp.json()[0]
    item_id = item["id"]
    unit_price = item["price"]

    # Add item to cart (quantity 1)
    item_payload_1 = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
    add_resp_1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_1, timeout=10)
    assert add_resp_1.status_code == 201, f"Expected 201, got {add_resp_1.status_code}: {add_resp_1.text}"

    # Verify quantity is 1
    get_resp_1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp_1.status_code == 200, f"Expected 200, got {get_resp_1.status_code}: {get_resp_1.text}"
    assert get_resp_1.json().get("quantity") == 1, "Expected quantity 1"

    # Add item to cart again (quantity 2)
    item_payload_2 = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    add_resp_2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload_2, timeout=10)
    assert add_resp_2.status_code == 201, f"Expected 201, got {add_resp_2.status_code}: {add_resp_2.text}"

    # Verify cumulative quantity is 3
    get_resp_2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp_2.status_code == 200, f"Expected 200, got {get_resp_2.status_code}: {get_resp_2.text}"
    assert get_resp_2.json().get("quantity") == 3, f"Expected cumulative quantity 3, got {get_resp_2.json().get('quantity')}"

    # Delete item
    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    # Verify deletion
    get_resp_3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp_3.status_code == 404, f"Expected 404, got {get_resp_3.status_code}: {get_resp_3.text}"

# --- id=941  name='Orders Place Order Success' ---
def test_orders_place_order_success():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # Add Address
    addr_resp = requests.post(get_url("user", "/addresses"), json={
        "city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Main St", "userID": username
    }, timeout=10)
    address_id = addr_resp.json().get("id")

    # Add Card
    card_resp = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    card_id = card_resp.json().get("id")

    # Get catalogue item with price <= 100
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    cheap_item = next((i for i in items if i["price"] <= 100.0), items[0])

    # Add to cart
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": cheap_item["id"], "quantity": 1, "unitPrice": cheap_item["price"]
    }, timeout=10)

    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data.get("id")
    assert order_id is not None, "Expected order ID in response"
    assert order_data.get("payment", {}).get("authorised") is True, "Expected payment to be authorised"

    # Verify Order
    get_order_resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    assert get_order_resp.json().get("id") == order_id, "Order ID mismatch"

# --- id=942  name='Orders Payment Declined 406' ---
def test_orders_payment_declined_406():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "J", "lastName": "D"
    }, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={
        "city": "L", "country": "U", "number": "1", "postcode": "1", "street": "S", "userID": username
    }, timeout=10)
    address_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    card_id = card_resp.json().get("id")

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]

    # Add to cart with quantity to make total > 100
    quantity = int(101 / item["price"]) + 1
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"], "quantity": quantity, "unitPrice": item["price"]
    }, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"
