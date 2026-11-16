# Tests generated in iteration 06
# Captured: 2026-06-04T19:22:02
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=313  name='User Authentication And Registration' ---
def test_user_authentication_and_registration():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify user creation
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Register again -> 409
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    # Login success
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login failure
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpassword"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=314  name='Catalogue Functionality' ---
def test_catalogue_functionality():
    # Get all items
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0
    sock_id = socks[0]["id"]

    # Get specific item
    resp = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == sock_id

    # Get non-existent item -> 404
    resp = requests.get(get_url("catalogue", "/catalogue/non_existent_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Get tags
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=315  name='Carts Management' ---
def test_carts_management():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get real item from catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0
    real_item_id = socks[0]["id"]
    real_price = socks[0]["price"]

    # Add item
    item_data = {
        "itemId": real_item_id,
        "quantity": 2,
        "unitPrice": real_price
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    resp_item = resp.json()
    assert resp_item["itemId"] == item_data["itemId"]
    assert resp_item["quantity"] == item_data["quantity"]
    assert resp_item["unitPrice"] == item_data["unitPrice"]

    # Verify item
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{real_item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_item = resp.json()
    assert fetched_item["itemId"] == item_data["itemId"]
    assert fetched_item["quantity"] == item_data["quantity"]
    assert fetched_item["unitPrice"] == item_data["unitPrice"]

    # Update item
    item_data["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{real_item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_item = resp.json()
    assert fetched_item["quantity"] == 5

    # Delete item
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{real_item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify delete
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{real_item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Delete cart
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=316  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify user creation
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Add Address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Test Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Verify address
    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_address = resp.json()
    assert fetched_address["city"] == address_data["city"]
    assert fetched_address["country"] == address_data["country"]
    assert fetched_address["number"] == address_data["number"]
    assert fetched_address["postcode"] == address_data["postcode"]
    assert fetched_address["street"] == address_data["street"]

    # 3. Add Card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    # Verify card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_card = resp.json()
    assert fetched_card["ccv"] == card_data["ccv"]
    assert fetched_card["expires"] == card_data["expires"]
    assert fetched_card["longNum"].endswith(card_data["longNum"][-4:])

    # 4. Get Catalogue Item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0
    sock = socks[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    # 5. Add to Cart
    item_data = {
        "itemId": sock_id,
        "quantity": 1,
        "unitPrice": sock_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    resp_item = resp.json()
    assert resp_item["itemId"] == item_data["itemId"]
    assert resp_item["quantity"] == item_data["quantity"]
    assert resp_item["unitPrice"] == item_data["unitPrice"]

    # Verify cart item
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_item = resp.json()
    assert fetched_item["itemId"] == item_data["itemId"]
    assert fetched_item["quantity"] == item_data["quantity"]
    assert fetched_item["unitPrice"] == item_data["unitPrice"]

    # 6. Place Order
    order_req = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{address_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    assert "id" in order
    order_id = order["id"]
    assert order["payment"]["authorised"] is True

    # Verify Order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id
    assert fetched_order["payment"]["authorised"] is True

    # Verify Payment
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert isinstance(payments, list)
    if len(payments) > 0:
        assert payments[0]["orderId"] == order_id
        assert payments[0]["authorised"] is True

    # Verify Shipment
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

# --- id=317  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"
    }, timeout=10)

    # 2. Add Address
    resp = requests.post(get_url("user", "/addresses"), json={
        "city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S", "userID": username
    }, timeout=10)
    address_id = resp.json()["id"]

    # 3. Add Card
    resp = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    card_id = resp.json()["id"]

    # 4. Add expensive item to cart
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0
    sock = socks[0]

    item_data = {
        "itemId": sock["id"],
        "quantity": 1000, # Ensure total > 100
        "unitPrice": sock["price"]
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # 5. Place Order
    order_req = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{address_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
