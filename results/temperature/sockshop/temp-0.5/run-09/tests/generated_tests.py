# Tests generated in iteration 09
# Captured: 2026-07-04T16:47:53
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=489  name='E2e Order Workflow' ---
def test_e2e_order_workflow():
    username = random_string()
    password = random_string()
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("username") == username, "Customer username mismatch"

    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    address_payload = {
        "city": "Testville",
        "country": "Testland",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None, "Expected address id in response"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == address_id for a in addresses), "Address not found in customer addresses"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None, "Expected card id in response"

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards), "Card not found in customer cards"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Expected at least one item in catalogue"
    item = items[0]
    item_id = item["id"]
    item_price = item["price"]

    cart_item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": item_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) > 0, "Expected item in cart"
    assert cart_items[0]["itemId"] == item_id, "Cart item ID mismatch"
    assert cart_items[0]["quantity"] == 2, "Cart item quantity mismatch"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None, "Expected order ID in response"
    assert order.get("customer", {}).get("username") == username, "Order customer mismatch"

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order.get("id") == order_id, "Fetched order ID mismatch"

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert isinstance(payments, list), "Expected list of payments"
    assert len(payments) > 0, "Expected payment authorization"
    assert payments[0].get("orderId") == order_id, "Payment order ID mismatch"

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id, "Shipment order ID mismatch"

# --- id=490  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = random_string()
    password = random_string()
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=491  name='Order Missing Fields Not Acceptable' ---
def test_order_missing_fields_not_acceptable():
    username = random_string()
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "F",
        "lastName": "L"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json(), "Expected message in 406 response"

# --- id=492  name='Order Invalid Uri Not Found' ---
def test_order_invalid_uri_not_found():
    username = random_string()
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "F",
        "lastName": "L"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    cart_item_payload = {
        "itemId": "test_item",
        "quantity": 1,
        "unitPrice": 9.99
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_id_format",
        "card": "/cards/invalid_id_format",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=493  name='Catalogue Item Not Found' ---
def test_catalogue_item_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/nonexistent_item_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=494  name='Cart Item Not Found' ---
def test_cart_item_not_found():
    username = random_string()
    cart_item_payload = {
        "itemId": "test_item",
        "quantity": 1,
        "unitPrice": 9.99
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/nonexistent_item_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=495  name='Cart' ---
def test_delete_cart():
    username = random_string()

    cart_item_payload = {
        "itemId": "test_item",
        "quantity": 1,
        "unitPrice": 9.99
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0, "Expected cart to be empty after deletion"

# --- id=496  name='Customer' ---
def test_delete_customer():
    username = random_string()

    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "F",
        "lastName": "L"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True, "Expected status true for deleted customer"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("firstName") is None, "Expected empty customer after deletion"

# --- id=497  name='Cart Item' ---
def test_delete_cart_item():
    username = random_string()
    item_id = "test_item"

    cart_item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 9.99
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=498  name='Cart Item' ---
def test_patch_cart_item():
    username = random_string()
    item_id = "test_item"

    cart_item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 9.99
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    patch_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 9.99
    }
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=patch_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 5, "Expected quantity to be updated"

# --- id=499  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = str(uuid.uuid4())
    payment_payload = {
        "address": {
            "city": "City",
            "country": "Country",
            "number": "12",
            "postcode": "12345",
            "street": "Street"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "First",
            "lastName": "Last"
        },
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is True, "Expected payment to be authorised"
    assert auth.get("orderId") == order_id, "Order ID mismatch"

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1, "Expected exactly one authorization"
    assert auths[0].get("authorised") is True, "Expected authorization to be true"

# --- id=500  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = str(uuid.uuid4())
    shipping_payload = {
        "address": {
            "city": "City",
            "country": "Country",
            "number": "12",
            "postcode": "12345",
            "street": "Street"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id, "Order ID mismatch"
    assert shipment.get("carrier") is not None, "Expected carrier to be assigned"

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_shipment = resp.json()
    assert fetched_shipment.get("orderId") == order_id, "Order ID mismatch in follow-up"

# --- id=501  name='Orders Search By Customer' ---
def test_orders_search_by_customer():
    username = random_string()
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "F",
        "lastName": "L"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {
        "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    address_id = resp.json().get("id")

    card_payload = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp.json().get("id")

    cart_item_payload = {
        "itemId": "test_item", "quantity": 1, "unitPrice": 9.99
    }
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert len(orders) > 0, "Expected at least one order"
    assert any(o.get("id") == order_id for o in orders), "Created order not found in search results"

# --- id=502  name='Catalogue Tags And Size' ---
def test_catalogue_tags_and_size():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags = resp.json().get("tags", [])
    assert isinstance(tags, list), "Expected tags to be a list"

    if tags:
        tag = tags[0]
        resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        size = resp.json().get("size")
        assert isinstance(size, int), "Expected size to be an integer"

# --- id=503  name='Address And Card' ---
def test_delete_address_and_card():
    username = random_string()
    user_payload = {
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    address_payload = {
        "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    address_id = resp.json().get("id")

    card_payload = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses), "Expected address to be deleted"

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards), "Expected card to be deleted"
