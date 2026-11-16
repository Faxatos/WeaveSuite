# Tests generated in iteration 01
# Captured: 2026-07-05T00:38:23
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=630  name='E2e Order Workflow' ---
def test_e2e_order_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Register
    resp = requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Registration
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["username"] == username
    assert resp.json()["firstName"] == "Test"

    # Login
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Address
    resp = requests.post(get_url("user", "/addresses"), json={
        "street": "123 Main St",
        "city": "Springfield",
        "country": "USA",
        "number": "123",
        "postcode": "12345",
        "userID": username
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Verify Address
    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["street"] == "123 Main St"

    # Add Card
    resp = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    # Verify Card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "1234567890123456" not in resp.json()["longNum"]

    # Get Catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    valid_items = [i for i in items if i.get("price", 0) <= 100 and i.get("price", 0) > 0]
    if not valid_items:
        pytest.skip("No valid items found for order")
    item = valid_items[0]
    item_id = item["id"]
    item_price = item["price"]

    # Add to Cart
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify Cart
    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id

    # Place Order
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]

    # Verify Order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == order_id

    # Verify Order Search by Customer
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert len(customer_orders) > 0
    assert any(o["id"] == order_id for o in customer_orders)

    # Verify Payment
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) > 0
    assert auths[-1]["orderId"] == order_id
    assert auths[-1]["authorised"] is True

    # Verify Shipping
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id

# --- id=631  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["username"] == username

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=632  name='Order Missing Cart Items 406' ---
def test_order_missing_cart_items_406():
    username = f"user_{uuid.uuid4().hex[:8]}"

    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@example.com"
    }, timeout=10)

    resp = requests.post(get_url("user", "/addresses"), json={
        "street": "S", "city": "C", "country": "C", "number": "1", "postcode": "123", "userID": username
    }, timeout=10)
    address_id = resp.json()["id"]

    resp = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    card_id = resp.json()["id"]

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=633  name='Order Invalid Uri Format 404' ---
def test_order_invalid_uri_format_404():
    username = f"user_{uuid.uuid4().hex[:8]}"

    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com"
    }, timeout=10)

    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "item1", "quantity": 1, "unitPrice": 10.0
    }, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format_no_colon",
        "card": f"/cards/invalid_format_no_colon",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=634  name='Order Payment Declined 406' ---
def test_order_payment_declined_406():
    username = f"user_{uuid.uuid4().hex[:8]}"

    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com"
    }, timeout=10)

    resp = requests.post(get_url("user", "/addresses"), json={
        "street": "S", "city": "C", "country": "C", "number": "1", "postcode": "123", "userID": username
    }, timeout=10)
    address_id = resp.json()["id"]

    resp = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    card_id = resp.json()["id"]

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    if not items:
        pytest.skip("No catalogue items")
    item = items[0]

    quantity = int(101 // item["price"]) + 1 if item.get("price", 0) > 0 else 101

    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"],
        "quantity": quantity,
        "unitPrice": item["price"]
    }, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=635  name='Carts Item Lifecycle' ---
def test_carts_item_lifecycle():
    username = f"user_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.5
    }, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 2

    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 15.5
    }, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=636  name='Payment Authorization Limits' ---
def test_payment_authorization_limits():
    order_id = f"order_{uuid.uuid4().hex[:8]}"

    resp = requests.post(get_url("payment-http", "/payments"), json={
        "orderId": order_id,
        "amount": 100.01,
        "customer": {"firstName": "A", "lastName": "B"},
        "address": {"street": "S", "city": "C", "country": "C", "number": "1", "postcode": "123"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is False

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is False

    resp = requests.post(get_url("payment-http", "/payments"), json={
        "orderId": order_id,
        "amount": 100.00,
        "customer": {"firstName": "A", "lastName": "B"},
        "address": {"street": "S", "city": "C", "country": "C", "number": "1", "postcode": "123"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is True

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 2
    assert auths[1]["authorised"] is True

    resp = requests.post(get_url("payment-http", "/payments"), json={
        "orderId": order_id,
        "amount": 0.0,
        "customer": {"firstName": "A", "lastName": "B"},
        "address": {"street": "S", "city": "C", "country": "C", "number": "1", "postcode": "123"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is False

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 3
    assert auths[2]["authorised"] is False

# --- id=637  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = f"order_{uuid.uuid4().hex[:8]}"

    resp = requests.post(get_url("shipping-http", "/shipping"), json={
        "orderId": order_id,
        "itemCount": 3,
        "address": {
            "street": "123 Shipping Ln",
            "city": "Port City",
            "country": "Oceania",
            "number": "42",
            "postcode": "54321"
        }
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_shipment = resp.json()
    assert fetched_shipment["orderId"] == order_id
    assert fetched_shipment["trackingNumber"] == shipment["trackingNumber"]

# --- id=638  name='Customer Deletion' ---
def test_customer_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"

    resp = requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "To",
        "lastName": "Delete"
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["firstName"] == "To"

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is True

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer["username"] == username
    assert "firstName" not in customer or not customer["firstName"]

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is False

# --- id=639  name='Address And Card Deletion' ---
def test_address_and_card_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"

    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@example.com"
    }, timeout=10)

    resp = requests.post(get_url("user", "/addresses"), json={
        "street": "S", "city": "C", "country": "C", "number": "1", "postcode": "123", "userID": username
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=640  name='Catalogue Filtering' ---
def test_catalogue_filtering():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    tags = tags_data.get("tags", [])
    if not tags:
        pytest.skip("No tags found")

    tag = tags[0]

    resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if items:
        assert tag in items[0].get("tag", [])

    resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    size_data = resp.json()
    assert size_data.get("size", 0) == len(items)

# --- id=641  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"user_{uuid.uuid4().hex[:8]}"
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json={
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": 10.0
    }, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 3

    bad_session = f"session_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={bad_session}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=642  name='Catalogue Images' ---
def test_catalogue_images():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if not items:
        pytest.skip("No items found")

    item = items[0]
    image_urls = item.get("imageUrl", [])
    if not image_urls:
        pytest.skip("No images found for item")

    image_name = image_urls[0].split("/")[-1]

    resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/catalogue/images/non_existent_image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=643  name='Order Not Found 404' ---
def test_order_not_found_404():
    bad_id = f"nonexistent_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("orders", f"/orders/{bad_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
