# Tests generated in iteration 03
# Captured: 2026-06-07T03:24:03
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1226  name='User Register And Login' ---
def test_user_register_and_login():
    username, password = create_user()

    # Verify user exists
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Login
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=1227  name='User Register Duplicate' ---
def test_user_register_duplicate():
    username, password = create_user()

    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=1228  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    resp = requests.get(get_url("user", "/login"), auth=("invalid_user", "invalid_pass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1229  name='User Add Address And' ---
def test_user_add_address_and_get():
    username, _ = create_user()

    payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None, "Address ID not returned"

    # Verify address
    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("city") == "Test City"

# --- id=1230  name='User Add Card And' ---
def test_user_add_card_and_get():
    username, _ = create_user()

    payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None, "Card ID not returned"

    # Verify card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("expires") == "12/25"

# --- id=1231  name='Catalogue Items' ---
def test_catalogue_get_items():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Catalogue is empty"

    item_id = items[0]["id"]
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == item_id

# --- id=1232  name='Catalogue Item Not Found' ---
def test_catalogue_get_item_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid-item-id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1233  name='Carts Add Item Cumulative' ---
def test_carts_add_item_cumulative():
    customer_id = f"cust_{generate_random_string()}"
    item = get_catalogue_item()
    item_id = item["id"]

    payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item["price"]
    }

    # Add item first time
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify quantity is 1
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 1

    # Add item second time (cumulative)
    payload["quantity"] = 2
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify quantity is 3
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 3

# --- id=1234  name='Carts Item' ---
def test_carts_patch_item():
    customer_id = f"cust_{generate_random_string()}"
    item = get_catalogue_item()
    item_id = item["id"]

    payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item["price"]
    }

    # Add item
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Patch item
    payload["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify quantity is 5
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 5

# --- id=1235  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{generate_random_string()}"
    item = get_catalogue_item()
    item_id = item["id"]

    payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item["price"]
    }

    # Add item
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Delete item
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify item is gone
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1236  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{generate_random_string()}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=invalid_session"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1237  name='Orders Create Order' ---
def test_orders_create_order():
    username, _ = create_user()

    # Add address
    addr_payload = {
        "city": "Test City", "country": "Test Country", "number": "123",
        "postcode": "12345", "street": "Test Street", "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")

    # Add card
    card_payload = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    # Add item to cart
    item = get_catalogue_item()
    cart_payload = {
        "itemId": item["id"], "quantity": 1, "unitPrice": item["price"]
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Create order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")
    assert order_id is not None, "Order ID not returned"

    # Verify order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == order_id

# --- id=1238  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    username, _ = create_user()

    # Add address
    addr_payload = {
        "city": "Test City", "country": "Test Country", "number": "123",
        "postcode": "12345", "street": "Test Street", "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")

    # Add card
    card_payload = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    # Add item to cart with high quantity to exceed 100.00
    item = get_catalogue_item()
    quantity = int(101.0 / item["price"]) + 1
    cart_payload = {
        "itemId": item["id"], "quantity": quantity, "unitPrice": item["price"]
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Create order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=1239  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = str(uuid.uuid4())
    payload = {
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    # Verify payment
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) > 0
    assert auths[0].get("orderId") == order_id

# --- id=1240  name='Shipping Ship Order' ---
def test_shipping_ship_order():
    order_id = str(uuid.uuid4())
    payload = {
        "address": {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street"},
        "itemCount": 2,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id

    # Verify shipment
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id
