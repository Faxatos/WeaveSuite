# Tests generated in iteration 10
# Captured: 2026-06-29T21:55:58
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=376  name='User Registration And Retrieval' ---
def test_user_registration_and_retrieval():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == "Test"
    assert customer.get("lastName") == "User"

    # Negative test: duplicate registration
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    # Delete customer
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

# --- id=377  name='User Login Auth' ---
def test_user_login_auth():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Login success
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login failure
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpassword"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=378  name='User Address Card Management' ---
def test_user_address_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Add address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Follow-up GET address
    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address = resp.json()
    assert address.get("city") == "London"
    assert address.get("postcode") == "SW1A 1AA"

    # Follow-up GET customer addresses
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == address_id for a in addresses)

    # Add card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    # Follow-up GET card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card = resp.json()
    assert card.get("expires") == "12/25"
    assert card.get("longNum").endswith("3456")
    assert "*" in card.get("longNum")

    # Follow-up GET customer cards
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

    # Delete address
    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify deletion
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses)

    # Delete card
    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify deletion
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

# --- id=379  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get a valid item from catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    # Add item to cart
    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Follow-up GET item
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 2

    # Update item quantity
    item_data["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET item
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 5

    # Delete item
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET item (should be 404)
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Delete cart
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=380  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    # Get a valid item from catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    # Add item to session cart
    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Merge session cart into customer cart
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET customer cart items
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

# --- id=381  name='Orders End To End Placement' ---
def test_orders_end_to_end_placement():
    # Setup user
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Setup address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json()["id"]

    # Setup card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json()["id"]

    # Get catalogue item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp.json()
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    # Add to cart
    item_data = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": unit_price
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

    # Place order
    order_data = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]

    # Assertions on order response
    assert order["customer"]["username"] == username
    assert order["address"]["postcode"] == "SW1A 1AA"
    assert order["card"]["longNum"].endswith("3456")
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == item_id
    assert order["items"][0]["quantity"] == 3
    assert order["total"] == 3 * unit_price

    # Follow-up GET order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id
    assert fetched_order["status"] in ["CREATED", "PAID", "SHIPPED"]

    # Search orders by customerId
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert len(customer_orders) > 0
    assert any(o["id"] == order_id for o in customer_orders)

    # Check payment authorization
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id

    # Check shipping
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment

# --- id=382  name='Orders Creation Failures' ---
def test_orders_creation_failures():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json()["id"]

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json()["id"]

    # Empty cart order
    order_data = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_data, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    # Add item to cart
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp.json()
    item_id = socks[0]["id"]
    unit_price = socks[0]["price"]

    item_data = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

    # Invalid address URI format
    invalid_order_data = order_data.copy()
    invalid_order_data["address"] = "/addresses/invalid_format"
    resp = requests.post(get_url("orders", "/orders"), json=invalid_order_data, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=383  name='Payment Http Authorization' ---
def test_payment_http_authorization():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_request = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "SW1A 1AA",
            "street": "Downing Street"
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

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_request, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    # Follow-up GET
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is True

    # Repeat payment (should append)
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_request, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 2

# --- id=384  name='Shipping Http Creation' ---
def test_shipping_http_creation():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    shipping_request = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "SW1A 1AA",
            "street": "Downing Street"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_request, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment

    # Follow-up GET
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_shipment = resp.json()
    assert fetched_shipment["orderId"] == order_id
    assert fetched_shipment["carrier"] == shipment["carrier"]
    assert fetched_shipment["trackingNumber"] == shipment["trackingNumber"]

# --- id=385  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    # GET /catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0

    sock_id = socks[0]["id"]

    # GET /catalogue/{id}
    resp = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    sock = resp.json()
    assert sock["id"] == sock_id

    # GET /catalogue/size
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    size_info = resp.json()
    assert "size" in size_info

    # GET /tags
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_info = resp.json()
    assert "tags" in tags_info

    # GET /catalogue/images/{image}
    if "imageUrl" in sock and len(sock["imageUrl"]) > 0:
        image_url = sock["imageUrl"][0]
        image_name = image_url.split("/")[-1]
        resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
