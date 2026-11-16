# Tests generated in iteration 09
# Captured: 2026-06-20T06:42:48
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=768  name='User Registration And Authentication' ---
def test_user_registration_and_authentication():
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

    # Register again -> 409 Conflict
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    # Login success
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login failure
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrong"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Get customer
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust = resp.json()
    assert cust.get("username") == username
    assert cust.get("email") == user_data["email"]
    assert "password" not in cust or cust.get("password") != password

    # Delete customer
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    # Delete again -> status false
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

# --- id=769  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "A",
        "lastName": "B"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Address
    addr_req = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1",
        "street": "Baker St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    assert addr_id is not None

    # Get Address
    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr = resp.json()
    assert addr.get("city") == "London"

    # Add Card
    card_req = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    # Get Card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card = resp.json()
    assert card.get("expires") == "12/25"
    assert "3456" in card.get("longNum")
    assert "1234" not in card.get("longNum")

    # Get Customer Addresses
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addrs = resp.json().get("_embedded", {}).get("address", [])
    assert len(addrs) >= 1
    assert any(a.get("id") == addr_id for a in addrs)

    # Get Customer Cards
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert len(cards) >= 1
    assert any(c.get("id") == card_id for c in cards)

    # Delete Address
    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify deletion via customer addresses
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addrs = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addrs)

    # Delete Card
    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify deletion via customer cards
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

# --- id=770  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    # Get tags
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags = resp.json().get("tags", [])
    assert isinstance(tags, list)

    # Get catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if not items:
        pytest.skip("No catalogue items found")

    item_id = items[0].get("id")

    # Get specific item
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == item_id

    # Get invalid item
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Get size
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

# --- id=771  name='Carts Management' ---
def test_carts_management():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get catalogue item to add
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if not items:
        pytest.skip("No catalogue items")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add item to cart
    item_req = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Get cart items
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 2

    # Add same item again (increments)
    item_req["quantity"] = 3
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify increment
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    # Update item (PATCH)
    item_req["quantity"] = 10
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_req, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 10

    # Merge carts
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={
        "itemId": item_id, "quantity": 1, "unitPrice": unit_price
    }, timeout=10)

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify merge
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 11

    # Delete item
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify deletion
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Delete cart
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify cart deletion
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=772  name='Order Placement And Fulfillment' ---
def test_order_placement_and_fulfillment():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Address
    resp = requests.post(get_url("user", "/addresses"), json={
        "city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S", "userID": username
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")

    # Add Card
    resp = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    # Get catalogue item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if not items:
        pytest.skip("No catalogue items")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add to cart
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item_id, "quantity": 1, "unitPrice": unit_price
    }, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Place order
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("customer", {}).get("username") == username
    assert len(order.get("items", [])) == 1
    assert order.get("items")[0]["itemId"] == item_id

    # Verify order retrieval
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == order_id

    # Verify customer orders search
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in cust_orders)

    # Verify payment authorization
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert isinstance(auths, list)
    assert len(auths) >= 1
    assert auths[-1].get("orderId") == order_id

    # Verify shipment
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id

# --- id=773  name='Orders Negative Cases' ---
def test_orders_negative_cases():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Address
    resp = requests.post(get_url("user", "/addresses"), json={
        "city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S", "userID": username
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")

    # Add Card
    resp = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    # Empty cart order -> 406
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    # Add item to cart
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if items:
        item_id = items[0]["id"]
        resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={
            "itemId": item_id, "quantity": 1, "unitPrice": 10.0
        }, timeout=10)
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

        # Invalid address URI format -> 404
        order_req_invalid_uri = order_req.copy()
        order_req_invalid_uri["address"] = "/addresses/invalid_format"
        resp = requests.post(get_url("orders", "/orders"), json=order_req_invalid_uri, timeout=10)
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

        # Missing required field -> 406
        order_req_missing = order_req.copy()
        del order_req_missing["card"]
        resp = requests.post(get_url("orders", "/orders"), json=order_req_missing, timeout=10)
        assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=774  name='Payment And Shipping Direct' ---
def test_payment_and_shipping_direct():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    # Direct Payment Authorization
    payment_req = {
        "address": {
            "city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123", "expires": "12/25", "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "F", "lastName": "L"
        },
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    # Verify payment recorded
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0].get("authorised") is True

    # Payment amount > 100 -> declined
    payment_req_declined = payment_req.copy()
    payment_req_declined["amount"] = 150.0
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req_declined, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

    # Verify second payment recorded
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 2
    assert auths[1].get("authorised") is False

    # Direct Shipping
    shipping_req = {
        "address": payment_req["address"],
        "itemCount": 2,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id
    assert resp.json().get("carrier") is not None

    # Verify shipping recorded
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id
