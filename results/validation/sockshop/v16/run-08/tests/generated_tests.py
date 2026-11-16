# Tests generated in iteration 08
# Captured: 2026-06-07T14:07:31
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1427  name='User Registration And Login' ---
def test_user_registration_and_login():
    username, password = create_user()

    # Login with Basic Auth
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=1428  name='User Duplicate Registration Negative' ---
def test_user_duplicate_registration_negative():
    username, password = create_user()

    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    # Attempt to register the same user again
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=1429  name='Carts Cumulative Quantity Update' ---
def test_carts_cumulative_quantity_update():
    customer_id = f"cust_{generate_random_string()}"
    item = get_catalogue_item()
    item_id = item["id"]

    # Add item to cart (quantity 1)
    cart_item = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item.get("price", 10.0)
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify quantity is 1
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 1

    # Add same item again to increment quantity by 2
    cart_item["quantity"] = 2
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify cumulative quantity is 3
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 3

    # Patch item to replace quantity with 5
    cart_item["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify quantity is replaced to 5
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    # Delete item
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify item is deleted
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1430  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
    username, password = create_user()

    # Add address
    address_data = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Verify address creation
    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

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

    # Verify card creation
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add item to cart
    item = get_catalogue_item()
    item_id = item["id"]
    cart_item = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item.get("price", 10.0)
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify item in cart
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Place order
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

    # Verify order creation
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify payment authorization was created for the order
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify shipment was created for the order
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=1431  name='Carts Merge Not Found Negative' ---
def test_carts_merge_not_found_negative():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1432  name='Orders Not Found Negative' ---
def test_orders_not_found_negative():
    order_id = str(uuid.uuid4())
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1433  name='Catalogue Image Not Found Negative' ---
def test_catalogue_image_not_found_negative():
    image_id = "non_existent_image.jpg"
    resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
