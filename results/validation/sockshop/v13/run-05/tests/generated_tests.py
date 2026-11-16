# Tests generated in iteration 05
# Captured: 2026-06-06T12:35:35
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=974  name='Carts Multiple Operations' ---
def test_carts_multiple_operations():
    # Setup: Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Get Catalogue Item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    # 1. Add item to cart (quantity 1)
    cart_item = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 1

    # 2. Add same item to cart again (quantity increments)
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify cumulative state
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 2

    # 3. PATCH item in cart (set quantity to 5)
    patch_item = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": item_price
    }
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=patch_item, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    # 4. DELETE item from cart
    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=975  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Try to register again
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=976  name='Orders Payment Not Authorized' ---
def test_orders_payment_not_authorized():
    # Setup: Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Add Card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    # Get Catalogue Item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    # Add item to cart with unitPrice > 100 to trigger payment decline
    cart_item = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 105.0
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Place Order
    order_req = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{address_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=977  name='Catalogue Image Not Found' ---
def test_catalogue_image_not_found():
    invalid_image = f"invalid_{uuid.uuid4().hex}.jpg"
    resp = requests.get(get_url("catalogue", f"/catalogue/images/{invalid_image}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=978  name='Catalogue Item Not Found' ---
def test_catalogue_item_not_found():
    invalid_id = f"invalid_{uuid.uuid4().hex}"
    resp = requests.get(get_url("catalogue", f"/catalogue/{invalid_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=979  name='Orders Search Not Found' ---
def test_orders_search_not_found():
    invalid_cust_id = f"invalid_{uuid.uuid4().hex}"
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={invalid_cust_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=980  name='Orders Not Found' ---
def test_orders_get_not_found():
    invalid_id = f"invalid_{uuid.uuid4().hex}"
    resp = requests.get(get_url("orders", f"/orders/{invalid_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=981  name='Carts Item Not Found' ---
def test_carts_item_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    invalid_id = f"invalid_{uuid.uuid4().hex}"
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{invalid_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=982  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    invalid_session = f"invalid_{uuid.uuid4().hex}"
    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={invalid_session}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=983  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = f"user_{uuid.uuid4().hex[:8]}"
    auth = (username, "wrongpassword")
    resp = requests.get(get_url("user", "/login"), auth=auth, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=973  name='E2e Order Workflow' ---
def test_e2e_order_workflow():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET for User
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Login
    auth = (username, "password")
    resp = requests.get(get_url("user", "/login"), auth=auth, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 3. Add Address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Follow-up GET for Address
    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_json = resp.json()
    assert get_json["city"] == address_data["city"]
    assert get_json["country"] == address_data["country"]
    assert get_json["number"] == address_data["number"]
    assert get_json["postcode"] == address_data["postcode"]
    assert get_json["street"] == address_data["street"]

    # 4. Add Card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    # Follow-up GET for Card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_json = resp.json()
    assert get_json["ccv"] == card_data["ccv"]
    assert get_json["expires"] == card_data["expires"]

    # 5. Get Catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]
    item_price = item["price"]

    # 6. Add to Cart
    cart_item = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()
    assert resp_json["itemId"] == cart_item["itemId"]
    assert resp_json["quantity"] == cart_item["quantity"]
    assert resp_json["unitPrice"] == cart_item["unitPrice"]

    # Follow-up GET for Cart Item
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_json = resp.json()
    assert get_json["itemId"] == cart_item["itemId"]
    assert get_json["quantity"] == cart_item["quantity"]
    assert get_json["unitPrice"] == cart_item["unitPrice"]

    # 7. Place Order
    order_req = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{address_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]
    assert order["payment"]["authorised"] is True

    # Follow-up GET for Order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    get_json = resp.json()
    assert get_json["id"] == order_id
    assert get_json["payment"]["authorised"] is True
