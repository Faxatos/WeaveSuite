# Tests generated in iteration 03
# Captured: 2026-06-06T10:59:15
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=945  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register User
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET to verify user creation
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login with correct credentials
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Negative: Login with incorrect credentials
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrong"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Negative: Register existing user
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=946  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Add address
    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None

    # Follow-up GET to verify address
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    added_address = next((a for a in addresses if a["id"] == address_id), None)
    assert added_address is not None
    assert added_address["city"] == address_data["city"]
    assert added_address["country"] == address_data["country"]
    assert added_address["number"] == address_data["number"]
    assert added_address["postcode"] == address_data["postcode"]
    assert added_address["street"] == address_data["street"]

    # Add card
    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    # Follow-up GET to verify card
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    added_card = next((c for c in cards if c["id"] == card_id), None)
    assert added_card is not None
    assert added_card["expires"] == card_data["expires"]
    assert "longNum" in added_card

# --- id=947  name='User Address And Card' ---
def test_user_delete_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "Delete"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json()["id"]

    # Delete address
    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify address deleted
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a["id"] == address_id for a in addresses)

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json()["id"]

    # Delete card
    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify card deleted
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert not any(c["id"] == card_id for c in cards)

# --- id=948  name='Catalogue Operations' ---
def test_catalogue_operations():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0

    item_id = items[0]["id"]

    # Get specific item
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == item_id

    # Negative: Non-existent item
    fake_id = "non-existent-id-12345"
    resp = requests.get(get_url("catalogue", f"/catalogue/{fake_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=949  name='Catalogue Size And Tags' ---
def test_catalogue_size_and_tags():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=950  name='Catalogue Images' ---
def test_catalogue_images():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200
    items = resp.json()
    image_url = items[0]["imageUrl"][0]
    image_name = image_url.split("/")[-1]

    resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Negative: Non-existent image
    resp = requests.get(get_url("catalogue", "/catalogue/images/non-existent-image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=951  name='Carts Cumulative State' ---
def test_carts_cumulative_state():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200
    items = resp.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    item_data = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }

    # Add item to cart
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    resp_item = resp.json()
    assert resp_item["itemId"] == item_data["itemId"]
    assert resp_item["quantity"] == item_data["quantity"]
    assert resp_item["unitPrice"] == item_data["unitPrice"]

    # Follow-up GET
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_item = resp.json()
    assert fetched_item["itemId"] == item_data["itemId"]
    assert fetched_item["quantity"] == item_data["quantity"]
    assert fetched_item["unitPrice"] == item_data["unitPrice"]

    # Add same item again to test cumulative state
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Follow-up GET to verify quantity is 2
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_item = resp.json()
    assert fetched_item["itemId"] == item_data["itemId"]
    assert fetched_item["quantity"] == 2
    assert fetched_item["unitPrice"] == item_data["unitPrice"]

    # Delete item
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Negative: Verify item is deleted
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=952  name='Carts Item' ---
def test_carts_patch_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200
    item = resp.json()[0]

    item_data = {"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201

    # Patch item
    patch_data = {"itemId": item["id"], "quantity": 5, "unitPrice": item["price"]}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item['id']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_item = resp.json()
    assert fetched_item["quantity"] == 5

# --- id=953  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200
    item = resp.json()[0]

    item_data = {"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)

    # Delete cart
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET items should be empty
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=954  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200
    item = resp.json()[0]

    item_data = {"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201

    # Merge session cart into customer cart
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify customer cart has the item
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item["id"]

    # Negative: merge non-existent session cart
    fake_session = f"fake_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={fake_session}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=955  name='Orders End To End' ---
def test_orders_end_to_end():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "Order"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 2. Add Address
    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # 3. Add Card
    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    # 4. Get Catalogue Item (ensure price <= 100 for successful payment)
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    cheap_item = next(item for item in items if item["price"] <= 100.0)

    # 5. Add to Cart
    item_data = {"itemId": cheap_item["id"], "quantity": 1, "unitPrice": cheap_item["price"]}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # 6. Place Order
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
    assert order["payment"]["authorised"] is True

    # 7. Verify Order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id
    assert fetched_order["payment"]["authorised"] is True

    # 8. Verify Payment Authorization
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id
    assert payments[0]["authorised"] is True

    # 9. Verify Shipment
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

# --- id=956  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "Test", "lastName": "Decline"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json()["id"]

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json()["id"]

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    item = items[0]

    # Add to Cart with high quantity to exceed 100.00
    quantity = int(101.0 / item["price"]) + 1
    item_data = {"itemId": item["id"], "quantity": quantity, "unitPrice": item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

    # Place Order -> Should be 406 Not Acceptable
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=957  name='Orders Search Customer' ---
def test_orders_search_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "Test", "lastName": "Search"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Baker St", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = resp.json()["id"]

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = resp.json()["id"]

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    cheap_item = next(item for item in items if item["price"] <= 100.0)

    item_data = {"itemId": cheap_item["id"], "quantity": 1, "unitPrice": cheap_item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201

    # Search Orders
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Negative: Search non-existent customer
    fake_user = f"fake_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={fake_user}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=958  name='Orders Not Found' ---
def test_orders_get_not_found():
    fake_order_id = str(uuid.uuid4())
    resp = requests.get(get_url("orders", f"/orders/{fake_order_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
