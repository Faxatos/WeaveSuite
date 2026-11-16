# Tests generated in iteration 05
# Captured: 2026-07-05T02:48:09
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=666  name='User Registration Login Deletion' ---
def test_user_registration_login_deletion():
    user_data = generate_user()
    username = user_data["username"]

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify via GET
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer.get("username") == username
    assert customer.get("email") == user_data["email"]
    assert customer.get("firstName") == user_data["firstName"]
    assert customer.get("lastName") == user_data["lastName"]
    assert "password" not in customer

    # Duplicate register -> 409
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    # Login success
    resp = requests.get(get_url("user", "/login"), auth=(username, user_data["password"]), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login failure
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Delete user
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    # Delete again -> status: false
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

# --- id=667  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    user_data = generate_user()
    username = user_data["username"]
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Add address
    addr_req = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Main St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    assert addr_id is not None

    # Verify address
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert len(addresses) == 1
    assert addresses[0]["city"] == addr_req["city"]
    assert addresses[0]["id"] == addr_id

    # Add card
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

    # Verify card
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert len(cards) == 1
    assert cards[0]["id"] == card_id
    assert cards[0]["longNum"].endswith("3456")
    assert "*" in cards[0]["longNum"]

    # Delete address
    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify address deleted
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200
    assert len(resp.json().get("_embedded", {}).get("address", [])) == 0

    # Delete card
    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify card deleted
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200
    assert len(resp.json().get("_embedded", {}).get("card", [])) == 0

# --- id=668  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if not items:
        pytest.skip("No items in catalogue")

    item = items[0]
    item_id = item["id"]

    # Get specific item
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_item = resp.json()
    assert fetched_item["id"] == item_id
    assert fetched_item["name"] == item["name"]

    # Non-existent item
    invalid_id = "non_existent_" + str(uuid.uuid4())
    resp = requests.get(get_url("catalogue", f"/catalogue/{invalid_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=669  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    customer_id = f"cust_{uuid.uuid4()}"
    item_id = f"item_{uuid.uuid4()}"

    # Add item
    item_req = {"itemId": item_id, "quantity": 2, "unitPrice": 15.5}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify item in list
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

    # Increment quantity
    item_req_inc = {"itemId": item_id, "quantity": 3, "unitPrice": 15.5}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_req_inc, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify incremented quantity
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    # Patch item
    item_req_patch = {"itemId": item_id, "quantity": 1, "unitPrice": 15.5}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_req_patch, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify patched quantity
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 1

    # Delete item
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify item deleted
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Delete cart
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=670  name='Orders Workflow' ---
def test_orders_workflow():
    # Setup User, Address, Card
    user_data = generate_user()
    username = user_data["username"]
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_req = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Main St", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    card_id = card_resp.json()["id"]

    # Add item to cart
    item_id = str(uuid.uuid4())
    item_req = {"itemId": item_id, "quantity": 2, "unitPrice": 12.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_req, timeout=10)

    # Place order
    order_req = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{addr_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }

    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order["customer"]["username"] == username
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == item_id
    assert order["total"] == 24.0

    # Verify order via GET
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id

    # Verify via search
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

# --- id=671  name='Orders Negative Conditions' ---
def test_orders_negative_conditions():
    user_data = generate_user()
    username = user_data["username"]
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_req = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Main St", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10).json()["id"]

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_req, timeout=10).json()["id"]

    # Empty cart
    requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)

    order_req = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{addr_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }

    # 1. Empty cart -> 406
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    # Add item to cart
    item_req = {"itemId": "item1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_req, timeout=10)

    # 2. Missing required field -> 406
    bad_order_req = order_req.copy()
    del bad_order_req["address"]
    resp = requests.post(get_url("orders", "/orders"), json=bad_order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    # 3. Malformed address URI -> 404
    bad_order_req2 = order_req.copy()
    bad_order_req2["address"] = get_url("user", f"/addresses/invalid_format_without_colon")
    resp = requests.post(get_url("orders", "/orders"), json=bad_order_req2, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=672  name='Payment Http Authorization' ---
def test_payment_http_authorization():
    order_id = f"order_{uuid.uuid4()}"
    payment_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Main St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    # Authorize payment
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    # Verify via GET
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is True

    # Duplicate payment (amount > 0 and <= 100 is authorized)
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify via GET -> should have 2 entries
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 2

    # Declined payment (amount > 100)
    declined_req = payment_req.copy()
    declined_req["amount"] = 150.0
    resp = requests.post(get_url("payment-http", "/payments"), json=declined_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is False

    # Verify via GET -> should have 3 entries
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 3
    assert auths[-1]["authorised"] is False

# --- id=673  name='Shipping Http Workflow' ---
def test_shipping_http_workflow():
    order_id = f"order_{uuid.uuid4()}"
    ship_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Main St"},
        "itemCount": 3,
        "orderId": order_id
    }

    # Create shipment
    resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment
    assert "carrier" in shipment

    # Verify via GET
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched = resp.json()
    assert fetched["orderId"] == order_id
    assert fetched["trackingNumber"] == shipment["trackingNumber"]
    assert fetched["carrier"] == shipment["carrier"]
