# Tests generated in iteration 07
# Captured: 2026-06-20T05:38:46
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=751  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    # Register
    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify customer exists
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username, f"Expected username {username}, got {resp_get.json().get('username')}"

    # Register again (Conflict)
    resp_conflict = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Login success
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Login failure
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

# --- id=752  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{generate_random_string()}"

    # Register
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    # Add Address
    addr_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None, "Expected address id in response"

    # Get Address
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json().get("city") == "Test City"

    # Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None, "Expected card id in response"

    # Get Card
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert resp_get_card.json().get("expires") == "12/25"

    # Delete Address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Delete Card
    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

# --- id=753  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    # Get catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0].get("id")
        # Get specific item
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json().get("id") == item_id

    # Get non-existent item
    resp_not_found = requests.get(get_url("catalogue", "/catalogue/invalid-id-12345"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=754  name='Carts Management' ---
def test_carts_management():
    customer_id = f"cust_{generate_random_string()}"
    item_id = "item_1"

    # Add item to cart
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Get cart items
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) > 0
    assert any(i.get("itemId") == item_id for i in items)

    # Update item in cart
    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 10.5
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify update
    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json().get("quantity") == 5

    # Delete item from cart
    resp_del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    # Verify deletion
    resp_get_item_after = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item_after.status_code == 404, f"Expected 404, got {resp_get_item_after.status_code}: {resp_get_item_after.text}"

    # Delete cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=755  name='Orders Creation And Retrieval' ---
def test_orders_creation_and_retrieval():
    username = f"user_{generate_random_string()}"

    # 1. Register User
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    # 2. Add Address
    addr_payload = {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json().get("id")

    # 3. Add Card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json().get("id")

    # 4. Add Item to Cart
    item_payload = {"itemId": "item_1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    # 5. Create Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("customer", {}).get("username") == username

    # 6. Get Order
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json().get("id") == order_id

    # 7. Search Orders by Customer
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded = resp_search.json().get("_embedded", {})
    customer_orders = embedded.get("customerOrders", [])
    assert len(customer_orders) > 0
    assert any(o.get("id") == order_id for o in customer_orders)

# --- id=756  name='Orders Negative Cases' ---
def test_orders_negative_cases():
    username = f"user_{generate_random_string()}"

    # Missing fields (406)
    order_payload_missing = {
        "customer": f"/customers/{username}"
    }
    resp_order_missing = requests.post(get_url("orders", "/orders"), json=order_payload_missing, timeout=10)
    assert resp_order_missing.status_code == 406, f"Expected 406, got {resp_order_missing.status_code}: {resp_order_missing.text}"

    # Invalid composite ID (404)
    order_payload_invalid_id = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_id_format",
        "card": "/cards/invalid_id_format",
        "items": f"/carts/{username}/items"
    }
    resp_order_invalid = requests.post(get_url("orders", "/orders"), json=order_payload_invalid_id, timeout=10)
    assert resp_order_invalid.status_code == 404, f"Expected 404, got {resp_order_invalid.status_code}: {resp_order_invalid.text}"

# --- id=757  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = str(uuid.uuid4())

    payment_payload = {
        "address": {
            "city": "City",
            "country": "Country",
            "number": "1",
            "postcode": "123",
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

    # Authorize payment
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True

    # Get payment authorizations
    resp_get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    auths = resp_get_pay.json()
    assert isinstance(auths, list)
    assert len(auths) > 0
    assert auths[-1].get("orderId") == order_id

    # Negative: Amount > 100 should be declined (authorised=false) but still return 200
    payment_payload["amount"] = 150.0
    resp_pay_declined = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay_declined.status_code == 200, f"Expected 200, got {resp_pay_declined.status_code}: {resp_pay_declined.text}"
    assert resp_pay_declined.json().get("authorised") is False

# --- id=758  name='Shipping Management' ---
def test_shipping_management():
    order_id = str(uuid.uuid4())

    shipping_payload = {
        "address": {
            "city": "City",
            "country": "Country",
            "number": "1",
            "postcode": "123",
            "street": "Street"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    # Ship order
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id

    # Get shipment
    resp_get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    assert resp_get_ship.json().get("orderId") == order_id
