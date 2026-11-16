# Tests generated in iteration 09
# Captured: 2026-06-29T21:23:18
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=368  name='User Registration And Profile' ---
def test_user_registration_and_profile():
    username = f"user_{generate_random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    # Register user
    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Duplicate registration
    resp_dup = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Add address
    address_payload = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None, "Expected address id in response"

    # Verify address in customer profile
    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    addresses = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses), "Added address not found in customer addresses"

    # Add card
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

    # Verify card in customer profile
    resp_cust_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_card.status_code == 200, f"Expected 200, got {resp_cust_card.status_code}: {resp_cust_card.text}"
    cards = resp_cust_card.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards), "Added card not found in customer cards"

    # Verify masking
    added_card = next(c for c in cards if c.get("id") == card_id)
    assert added_card.get("longNum", "").endswith("3456"), "Card number should be masked"
    assert "*" in added_card.get("longNum", ""), "Card number should be masked with *"

# --- id=369  name='Carts And Catalogue Workflow' ---
def test_carts_and_catalogue_workflow():
    customer_id = f"cust_{generate_random_string()}"

    # Get catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Expected at least one item in catalogue"
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add to cart
    cart_item = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verify cart
    resp_cart = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_cart.status_code == 200, f"Expected 200, got {resp_cart.status_code}: {resp_cart.text}"
    cart_items = resp_cart.json()
    assert len(cart_items) == 1, "Expected 1 item in cart"
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 2

    # Update cart item
    cart_item_update = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": unit_price
    }
    resp_update = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item_update, timeout=10)
    assert resp_update.status_code == 202, f"Expected 202, got {resp_update.status_code}: {resp_update.text}"

    # Verify update
    resp_cart_updated = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_cart_updated.status_code == 200, f"Expected 200, got {resp_cart_updated.status_code}: {resp_cart_updated.text}"
    assert resp_cart_updated.json()["quantity"] == 5

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify deletion
    resp_cart_deleted = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_cart_deleted.status_code == 404, f"Expected 404, got {resp_cart_deleted.status_code}: {resp_cart_deleted.text}"

# --- id=370  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
    username = f"user_{generate_random_string()}"

    # Register user
    requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "F",
        "lastName": "L"
    }, timeout=10)

    # Add address
    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username
    }, timeout=10)
    addr_id = resp_addr.json()["id"]

    # Add card
    resp_card = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    card_id = resp_card.json()["id"]

    # Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp_cat.json()[0]

    # Add to cart
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"],
        "quantity": 1,
        "unitPrice": item["price"]
    }, timeout=10)

    # Place order
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
    assert order_id is not None, "Expected order ID in response"
    assert order_data.get("status") in ["CREATED", "PAID", "SHIPPED"], "Unexpected order status"

    # Verify order retrieval
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id

    # Verify customer orders search
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    cust_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in cust_orders), "Order not found in customer orders"

    # Verify payment authorization
    resp_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_payment.status_code == 200, f"Expected 200, got {resp_payment.status_code}: {resp_payment.text}"
    payments = resp_payment.json()
    assert len(payments) > 0, "Expected at least one payment authorization"
    assert payments[0]["orderId"] == order_id

    # Verify shipment
    resp_shipment = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_shipment.status_code == 200, f"Expected 200, got {resp_shipment.status_code}: {resp_shipment.text}"
    assert resp_shipment.json()["orderId"] == order_id

# --- id=371  name='Orders Missing Fields Negative' ---
def test_orders_missing_fields_negative():
    username = f"user_{generate_random_string()}"

    # Place order with missing fields
    order_payload = {
        "customer": f"/customers/{username}"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "message" in resp_order.json(), "Expected message in 406 response"

# --- id=372  name='Orders Invalid Uri Format Negative' ---
def test_orders_invalid_uri_format_negative():
    username = f"user_{generate_random_string()}"

    # Place order with syntactically invalid composite ID
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format_no_colon",
        "card": f"/cards/invalid_format_no_colon",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=373  name='Payment Http Authorization And Retrieval' ---
def test_payment_http_authorization_and_retrieval():
    order_id = str(uuid.uuid4())

    payment_payload = {
        "address": {
            "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123", "expires": "12/25", "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "F", "lastName": "L"
        },
        "orderId": order_id
    }

    # Authorize payment
    resp_auth = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_auth.status_code == 200, f"Expected 200, got {resp_auth.status_code}: {resp_auth.text}"
    auth_data = resp_auth.json()
    assert auth_data["orderId"] == order_id
    assert auth_data["authorised"] is True

    # Retrieve authorizations
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["orderId"] == order_id

    # Re-authorize to check append behavior
    resp_auth2 = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_auth2.status_code == 200, f"Expected 200, got {resp_auth2.status_code}: {resp_auth2.text}"

    resp_get2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    auths2 = resp_get2.json()
    assert len(auths2) == 2

# --- id=374  name='Shipping Http Creation And Retrieval' ---
def test_shipping_http_creation_and_retrieval():
    order_id = str(uuid.uuid4())

    shipping_payload = {
        "address": {
            "city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    # Create shipment
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data["orderId"] == order_id
    assert "trackingNumber" in ship_data

    # Retrieve shipment
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
    assert resp_get.json()["trackingNumber"] == ship_data["trackingNumber"]

# --- id=375  name='User Customer Deletion' ---
def test_user_customer_deletion():
    username = f"user_{generate_random_string()}"

    # Register user
    requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "F",
        "lastName": "L"
    }, timeout=10)

    # Delete customer
    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    # Delete again (should be false)
    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False
