# Tests generated in iteration 10
# Captured: 2026-06-21T08:29:20
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1219  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    # Register
    reg_url = get_url("user", "/register")
    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(reg_url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    login_url = get_url("user", "/login")
    resp = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Customer State
    cust_url = get_url("user", f"/customers/{username}")
    resp = requests.get(cust_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("username") == username, "Username mismatch in customer record"
    assert resp.json().get("email") == email, "Email mismatch in customer record"

# --- id=1220  name='User Duplicate Registration Conflict' ---
def test_user_duplicate_registration_conflict():
    username = f"user_{generate_random_string()}"
    payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "F",
        "lastName": "L"
    }
    reg_url = get_url("user", "/register")

    # First registration
    resp1 = requests.post(reg_url, json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    # Duplicate registration
    resp2 = requests.post(reg_url, json=payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1221  name='Catalogue Browsing And Filtering' ---
def test_catalogue_browsing_and_filtering():
    tags_url = get_url("catalogue", "/tags")
    resp = requests.get(tags_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    assert "tags" in tags_data and len(tags_data["tags"]) > 0, "No tags found"
    tag = tags_data["tags"][0]

    cat_url = get_url("catalogue", f"/catalogue?tags={tag}")
    resp = requests.get(cat_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, f"No items found for tag {tag}"
    item_id = items[0]["id"]

    item_url = get_url("catalogue", f"/catalogue/{item_id}")
    resp = requests.get(item_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    item = resp.json()
    assert item["id"] == item_id, "Item ID mismatch"
    assert tag in item.get("tag", []), "Item does not contain the filtered tag"

# --- id=1222  name='Carts Add Increment And' ---
def test_carts_add_increment_and_delete():
    item_id, price = get_valid_catalogue_item()
    customer_id = f"cartuser_{generate_random_string()}"

    items_url = get_url("carts", f"/carts/{customer_id}/items")

    # Add item
    payload1 = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    resp = requests.post(items_url, json=payload1, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp = requests.get(item_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 1, "Quantity should be exactly 1"

    # Increment item
    payload2 = {"itemId": item_id, "quantity": 2, "unitPrice": price}
    resp = requests.post(items_url, json=payload2, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(item_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 3, "Quantity should be aggregated to 3"

    # Delete item
    resp = requests.delete(item_url, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(item_url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1223  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"user_{generate_random_string()}"
    merge_url = get_url("carts", f"/carts/{customer_id}/merge?sessionId=invalid_session_id")
    resp = requests.get(merge_url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1224  name='Orders End To End Placement' ---
def test_orders_end_to_end_placement():
    username = f"user_{generate_random_string()}"

    # 1. Register User
    reg_url = get_url("user", "/register")
    requests.post(reg_url, json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)

    # 2. Add Address
    addr_url = get_url("user", "/addresses")
    addr_payload = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    resp = requests.post(addr_url, json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")

    addr_get_url = get_url("user", f"/addresses/{address_id}")
    resp = requests.get(addr_get_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("city") == "City", "Address city mismatch"

    # 3. Add Card
    card_url = get_url("user", "/cards")
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(card_url, json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    card_get_url = get_url("user", f"/cards/{card_id}")
    resp = requests.get(card_get_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "3456" in resp.json().get("longNum", ""), "Card longNum should be masked but contain last 4 digits"

    # 4. Add Item to Cart
    item_id, price = get_valid_catalogue_item()
    cart_url = get_url("carts", f"/carts/{username}/items")
    requests.post(cart_url, json={"itemId": item_id, "quantity": 2, "unitPrice": price}, timeout=10)

    # 5. Place Order
    orders_url = get_url("orders", "/orders")
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(orders_url, json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_data = resp.json()
    order_id = order_data.get("id")
    assert order_id is not None, "Order ID missing"
    assert abs(order_data.get("total", 0) - (price * 2)) < 0.01, "Order total mismatch"

    # 6. Verify Order State
    order_get_url = get_url("orders", f"/orders/{order_id}")
    resp = requests.get(order_get_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == order_id, "Order ID mismatch on GET"

    # 7. Verify Payment Authorization
    payment_url = get_url("payment-http", f"/payments/{order_id}")
    resp = requests.get(payment_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) > 0, "No payment authorization found"
    assert payments[0].get("authorised") is True, "Payment not authorized"

    # 8. Verify Shipment
    shipping_url = get_url("shipping-http", f"/shipping/{order_id}")
    resp = requests.get(shipping_url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id, "Shipping orderId mismatch"

# --- id=1225  name='Orders Creation Missing Cart' ---
def test_orders_creation_missing_cart():
    username = f"user_{generate_random_string()}"

    # Setup user, address, card but NO cart items
    reg_url = get_url("user", "/register")
    requests.post(reg_url, json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_url = get_url("user", "/addresses")
    resp = requests.post(addr_url, json={"city": "C", "country": "C", "number": "1", "postcode": "123", "street": "S", "userID": username}, timeout=10)
    address_id = resp.json().get("id")

    card_url = get_url("user", "/cards")
    resp = requests.post(card_url, json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp.json().get("id")

    # Attempt to place order
    orders_url = get_url("orders", "/orders")
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(orders_url, json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
