# Tests generated in iteration 10
# Captured: 2026-06-07T15:10:33
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1444  name='User Registration And Address Card Creation' ---
def test_user_registration_and_address_card_creation():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Register
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET for user
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_data = resp.json()
    assert "password" not in user_data or user_data.get("password") != password, "Password should not be returned in plain text"

    # Login
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Address
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")

    # Verify Address
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses), "Address not found in customer addresses"

    # Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    # Verify Card
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    card_obj = next((c for c in cards if c.get("id") == card_id), None)
    assert card_obj is not None, "Card not found in customer cards"
    assert "1234567890123456" not in card_obj.get("longNum", ""), "Card number should be masked"

# --- id=1445  name='User Registration Conflict Negative' ---
def test_user_registration_conflict_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "F",
        "lastName": "L"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Register again
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=1446  name='User Address And Card' ---
def test_user_delete_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Register
    resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Address
    resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S", "userID": username}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Delete Address
    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Address Deletion
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert not any(a.get("id") == addr_id for a in resp.json().get("_embedded", {}).get("address", []))

    # Add Card
    resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Delete Card
    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Card Deletion
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert not any(c.get("id") == card_id for c in resp.json().get("_embedded", {}).get("card", []))

# --- id=1447  name='Carts Add Item Cumulative Quantity' ---
def test_carts_add_item_cumulative_quantity():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get catalogue item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0, "No socks found in catalogue"
    sock = socks[0]
    item_id = sock["id"]

    # Add item to cart
    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": sock["price"]
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify quantity is 1
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 1

    # Add same item again
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify quantity is 2
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

    # Cleanup
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=1448  name='Carts Update And Remove Item' ---
def test_carts_update_and_remove_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get catalogue item
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    sock = resp.json()[0]
    item_id = sock["id"]

    # Add item to cart
    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": sock["price"]
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Update item quantity via PATCH
    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": sock["price"]
    }
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify update
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    # Remove item
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify removal
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1449  name='Carts Merge Sessions' ---
def test_carts_merge_sessions():
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Get item
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    sock = cat_resp.json()[0]

    # Add to anonymous cart
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{session_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Register user
    resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Merge
    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify item in user cart
    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == sock["id"]

# --- id=1450  name='Orders Successful Checkout' ---
def test_orders_successful_checkout():
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Register user
    resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add address
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S", "userID": username}, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")

    addr_check = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert addr_check.status_code == 200, f"Expected 200, got {addr_check.status_code}: {addr_check.text}"

    # Add card
    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")

    card_check = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert card_check.status_code == 200, f"Expected 200, got {card_check.status_code}: {card_check.text}"

    # Get item
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    sock = cat_resp.json()[0]

    # Add to cart
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    cart_check = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert cart_check.status_code == 200, f"Expected 200, got {cart_check.status_code}: {cart_check.text}"

    # Place order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None

    # Verify order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order.get("id") == order_id
    assert fetched_order.get("payment", {}).get("authorised") is True
    assert "shipment" in fetched_order

# --- id=1451  name='Orders Payment Declined Negative' ---
def test_orders_payment_declined_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Register user
    resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add address
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S", "userID": username}, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json().get("id")

    addr_check = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert addr_check.status_code == 200, f"Expected 200, got {addr_check.status_code}: {addr_check.text}"

    # Add card
    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")

    card_check = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert card_check.status_code == 200, f"Expected 200, got {card_check.status_code}: {card_check.text}"

    # Get item
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    sock = cat_resp.json()[0]

    # Calculate quantity to exceed 100.00
    price = sock.get("price", 1.0)
    if price <= 0:
        price = 1.0
    quantity = int(101 / price) + 1

    # Add to cart
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": quantity, "unitPrice": sock["price"]}, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    cart_check = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert cart_check.status_code == 200, f"Expected 200, got {cart_check.status_code}: {cart_check.text}"

    # Place order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=1452  name='Catalogue Item Not Found Negative' ---
def test_catalogue_item_not_found_negative():
    invalid_id = "non-existent-id-12345"
    resp = requests.get(get_url("catalogue", f"/catalogue/{invalid_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
