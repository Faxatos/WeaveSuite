# Tests generated in iteration 09
# Captured: 2026-06-07T14:36:25
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1434  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    # Register
    register_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=register_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify user exists
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1435  name='User Register Conflict Negative' ---
def test_user_register_conflict_negative():
    username = f"user_{generate_random_string()}"
    register_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=register_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Register again
    resp_conflict = requests.post(get_url("user", "/register"), json=register_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=1436  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{generate_random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com"
    }, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Add Address
    address_payload = {
        "userID": username,
        "number": "123",
        "street": "Main St",
        "city": "Anytown",
        "postcode": "12345",
        "country": "USA"
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None, "Expected address ID in response"

    # Verify Address
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addresses = resp_addr_get.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses), "Created address not found in collection"

    # Add Card
    card_payload = {
        "userID": username,
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123"
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None, "Expected card ID in response"

    # Verify Card
    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    cards = resp_card_get.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards), "Created card not found in collection"

# --- id=1437  name='Carts Add Item Cumulative' ---
def test_carts_add_item_cumulative():
    # Get a valid item from catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]
    unit_price = item["price"]

    customer_id = f"cust_{generate_random_string()}"

    # Add item to cart (qty 1)
    cart_item = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": unit_price
    }
    resp_add1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp_add1.status_code == 201, f"Expected 201, got {resp_add1.status_code}: {resp_add1.text}"

    # Verify qty 1
    resp_get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    cart_items = resp_get1.json()
    assert len(cart_items) == 1
    assert cart_items[0]["quantity"] == 1

    # Add item again (qty 2)
    cart_item["quantity"] = 2
    resp_add2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp_add2.status_code == 201, f"Expected 201, got {resp_add2.status_code}: {resp_add2.text}"

    # Verify cumulative qty 3
    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    cart_items = resp_get2.json()
    assert len(cart_items) == 1
    assert cart_items[0]["quantity"] == 3

# --- id=1438  name='Carts Merge Not Found Negative' ---
def test_carts_merge_not_found_negative():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1439  name='Catalogue Item Not Found Negative' ---
def test_catalogue_item_not_found_negative():
    invalid_id = f"invalid_{generate_random_string()}"
    resp = requests.get(get_url("catalogue", f"/catalogue/{invalid_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1440  name='Orders Create Successful' ---
def test_orders_create_successful():
    username = f"user_{generate_random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com"
    }, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Add Address
    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "userID": username, "number": "123", "street": "Main St", "city": "Anytown", "postcode": "12345", "country": "USA"
    }, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"

    # Add Card
    resp_card = requests.post(get_url("user", "/cards"), json={
        "userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"
    }, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item = items[0]

    # Add to cart
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"], "quantity": 1, "unitPrice": 10.0
    }, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    # Create Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")
    assert order_id is not None, "Expected order ID in response"

    # Verify Order
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    order_data = resp_order_get.json()
    assert order_data.get("id") == order_id

# --- id=1441  name='Orders Create Payment Declined Negative' ---
def test_orders_create_payment_declined_negative():
    username = f"user_{generate_random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com"
    }, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Add Address
    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "userID": username, "number": "123", "street": "Main St", "city": "Anytown", "postcode": "12345", "country": "USA"
    }, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"

    # Add Card
    resp_card = requests.post(get_url("user", "/cards"), json={
        "userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"
    }, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item = items[0]

    # Add to cart (total > 100 to trigger payment decline)
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"], "quantity": 15, "unitPrice": 10.0
    }, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    # Create Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1442  name='Carts Item' ---
def test_carts_delete_item():
    # Get a valid item from catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item = items[0]
    item_id = item["id"]

    customer_id = f"cust_{generate_random_string()}"

    # Add item to cart
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={
        "itemId": item_id, "quantity": 1, "unitPrice": item["price"]
    }, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    resp_get_add = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_add.status_code == 200, f"Expected 200, got {resp_get_add.status_code}: {resp_get_add.text}"

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify item is removed
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=1443  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{generate_random_string()}"

    # Add item to cart to create it
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item = resp_cat.json()[0]

    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={
        "itemId": item["id"], "quantity": 1, "unitPrice": item["price"]
    }, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    resp_get_add = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_add.status_code == 200, f"Expected 200, got {resp_get_add.status_code}: {resp_get_add.text}"

    # Delete cart
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify cart items are empty
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0, "Expected cart to be empty after deletion"
