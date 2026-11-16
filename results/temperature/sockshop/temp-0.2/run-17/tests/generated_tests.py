# Tests generated in iteration 06
# Captured: 2026-06-29T11:07:31
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=232  name='Catalogue Workflow' ---
def test_catalogue_workflow():
    # Get all tags
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags = resp.json().get("tags", [])
    assert len(tags) > 0

    # Get catalogue with a tag
    tag = tags[0]
    resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0

    # Get catalogue size
    resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    size = resp.json().get("size")
    assert size == len(items)

    # Get specific item
    item_id = items[0]["id"]
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == item_id

# --- id=233  name='Carts Workflow' ---
def test_carts_workflow():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get catalogue to get a real item ID
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add item to cart
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify item in cart
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 1

    # Update item in cart
    payload["quantity"] = 3
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify item updated
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 3

    # Delete item from cart
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify item deleted
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Delete cart
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify cart deleted (items list should be empty)
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=234  name='Carts Merge Workflow' ---
def test_carts_merge_workflow():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    # Get catalogue item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    item = resp.json()[0]

    # Add item to session cart
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={
        "itemId": item["id"], "quantity": 2, "unitPrice": item["price"]
    }, timeout=10)

    # Merge session cart to customer cart
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify customer cart has the item
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item["id"]
    assert items[0]["quantity"] == 2

    # Merge non-existent session cart -> 404
    bad_session = "nonexistent"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={bad_session}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=235  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Register again -> 409
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    # Login success
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login failure
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Get customer
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust = resp.json()
    assert cust["username"] == username
    assert cust["email"] == payload["email"]
    assert "password" not in cust or cust["password"] != password

    # Delete customer
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    # Delete again -> status: false
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

# --- id=236  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    # Add Address
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1",
        "street": "Baker St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Verify address in collection
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert len(addresses) == 1
    assert addresses[0]["id"] == address_id
    assert addresses[0]["city"] == "London"

    # Get specific address
    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == address_id

    # Add Card
    card_payload = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    # Verify card in collection
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert len(cards) == 1
    assert cards[0]["id"] == card_id
    assert cards[0]["longNum"] == "************3456"

    # Get specific card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == card_id

    # Delete Address
    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Address deleted
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert len(addresses) == 0

    # Delete Card
    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Card deleted
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert len(cards) == 0

# --- id=237  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"
    }, timeout=10)

    # 2. Add Address
    resp = requests.post(get_url("user", "/addresses"), json={
        "city": "C", "country": "D", "number": "1", "postcode": "123", "street": "S", "userID": username
    }, timeout=10)
    address_id = resp.json()["id"]

    # 3. Add Card
    resp = requests.post(get_url("user", "/cards"), json={
        "longNum": "1111222233334444", "expires": "12/26", "ccv": "111", "userID": username
    }, timeout=10)
    card_id = resp.json()["id"]

    # 4. Get Catalogue Item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]

    # 5. Add to Cart
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"], "quantity": 2, "unitPrice": item["price"]
    }, timeout=10)

    # 6. Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]

    assert order["customer"]["username"] == username
    assert order["address"]["city"] == "C"
    assert order["card"]["longNum"].endswith("4444")
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == item["id"]
    assert order["total"] == 2 * item["price"]
    assert order["payment"]["authorised"] is True
    assert order["status"] in ["CREATED", "PAID", "SHIPPED"]

    # 7. Verify Order via GET /orders/{id}
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == order_id

    # 8. Verify Order via GET /orders/search/customerId
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

    # 9. Verify Payment Authorization
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) >= 1
    assert auths[-1]["orderId"] == order_id
    assert auths[-1]["authorised"] is True

    # 10. Verify Shipment
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment

# --- id=238  name='Orders Missing Cart Items Negative' ---
def test_orders_missing_cart_items_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"
    }, timeout=10)

    resp = requests.post(get_url("user", "/addresses"), json={
        "city": "C", "country": "D", "number": "1", "postcode": "123", "street": "S", "userID": username
    }, timeout=10)
    address_id = resp.json()["id"]

    resp = requests.post(get_url("user", "/cards"), json={
        "longNum": "1111222233334444", "expires": "12/26", "ccv": "111", "userID": username
    }, timeout=10)
    card_id = resp.json()["id"]

    # Cart is empty, attempt to place order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=239  name='Orders Invalid Address Uri Negative' ---
def test_orders_invalid_address_uri_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"
    }, timeout=10)

    resp = requests.post(get_url("user", "/cards"), json={
        "longNum": "1111222233334444", "expires": "12/26", "ccv": "111", "userID": username
    }, timeout=10)
    card_id = resp.json()["id"]

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"], "quantity": 1, "unitPrice": item["price"]
    }, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=240  name='Payment Authorization Workflow' ---
def test_payment_authorization_workflow():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payload = {
        "address": {"city": "C", "country": "D", "number": "1", "postcode": "123", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }

    # Authorized payment
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    # Verify payment recorded
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0]["orderId"] == order_id

    # Declined payment (amount > 100)
    payload["amount"] = 150.0
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is False

    # Verify both payments recorded
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 2
    assert auths[0]["authorised"] is True
    assert auths[1]["authorised"] is False

# --- id=241  name='Shipping Workflow' ---
def test_shipping_workflow():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payload = {
        "address": {"city": "C", "country": "D", "number": "1", "postcode": "123", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    # Create shipment
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment

    # Verify shipment
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id
    assert resp.json()["trackingNumber"] == shipment["trackingNumber"]
