# Tests generated in iteration 04
# Captured: 2026-06-04T18:24:09
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=301  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    # Register user
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify user exists
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    user_data = resp_get.json()
    if "username" in user_data:
        assert user_data["username"] == username
        assert user_data["email"] == email
        assert user_data["firstName"] == "Test"
        assert user_data["lastName"] == "User"

    # Login success
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Login failure
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

    # Register same user again
    resp_dup = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

# --- id=302  name='Catalogue Operations' ---
def test_catalogue_operations():
    # List socks
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)

    if socks:
        sock_id = socks[0]["id"]
        # Get specific sock
        resp_sock = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
        assert resp_sock.json()["id"] == sock_id

    # Get non-existent sock
    resp_not_found = requests.get(get_url("catalogue", "/catalogue/invalid-id-12345"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

    # Get tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=303  name='Carts Operations' ---
def test_carts_operations():
    customer_id = f"cust_{random_string()}"
    item_id = f"item_{random_string()}"

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.5
    }

    # Add item to cart
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    added_item = resp.json()
    assert added_item["itemId"] == item_payload["itemId"]
    assert added_item["quantity"] == item_payload["quantity"]
    assert added_item["unitPrice"] == item_payload["unitPrice"]

    # Verify item in cart
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["itemId"] == item_payload["itemId"]
    assert resp_get.json()["quantity"] == item_payload["quantity"]
    assert resp_get.json()["unitPrice"] == item_payload["unitPrice"]

    # Update item in cart
    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 15.5
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify updated item
    resp_get_updated = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_updated.status_code == 200, f"Expected 200, got {resp_get_updated.status_code}: {resp_get_updated.text}"
    assert resp_get_updated.json()["quantity"] == update_payload["quantity"]

    # Remove item from cart
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify item removed
    resp_get_deleted = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_deleted.status_code == 404, f"Expected 404, got {resp_get_deleted.status_code}: {resp_get_deleted.text}"

    # Delete cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    # Verify cart is empty
    resp_get_cart = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"
    assert len(resp_get_cart.json()) == 0

# --- id=304  name='User Address And Card' ---
def test_user_address_and_card():
    username = f"user_{random_string()}"

    # Register user
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Verify user
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

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
    address_id = resp_addr.json()["id"]

    # Verify address
    resp_get_addr = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addr_data = resp_get_addr.json()
    assert addr_data["city"] == address_payload["city"]
    assert addr_data["country"] == address_payload["country"]
    assert addr_data["number"] == address_payload["number"]
    assert addr_data["postcode"] == address_payload["postcode"]
    assert addr_data["street"] == address_payload["street"]

    # Add card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    # Verify card
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    card_data = resp_get_card.json()
    assert card_data["ccv"] == card_payload["ccv"]
    assert card_data["expires"] == card_payload["expires"]
    assert card_data["id"] == card_id

    # Delete address and card
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    # Verify deletion via listing endpoints
    resp_list_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_list_addr.status_code == 200, f"Expected 200, got {resp_list_addr.status_code}: {resp_list_addr.text}"
    if "_embedded" in resp_list_addr.json():
        addresses = resp_list_addr.json()["_embedded"].get("address", [])
        assert not any(a.get("id") == address_id for a in addresses)

    resp_list_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_list_card.status_code == 200, f"Expected 200, got {resp_list_card.status_code}: {resp_list_card.text}"
    if "_embedded" in resp_list_card.json():
        cards = resp_list_card.json()["_embedded"].get("card", [])
        assert not any(c.get("id") == card_id for c in cards)

# --- id=305  name='Orders End To End Success' ---
def test_orders_end_to_end_success():
    username = f"user_{random_string()}"

    # Register user
    resp_reg = requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Add address
    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json()["id"]

    resp_get_addr = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    # Add card
    resp_card = requests.post(get_url("user", "/cards"), json={
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    # Add item to cart (total <= 100 for successful payment)
    resp_item = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "sock1",
        "quantity": 2,
        "unitPrice": 20.0
    }, timeout=10)
    assert resp_item.status_code == 201, f"Expected 201, got {resp_item.status_code}: {resp_item.text}"

    resp_get_item = requests.get(get_url("carts", f"/carts/{username}/items/sock1"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"

    # Place order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data["id"]
    assert order_data["payment"]["authorised"] is True

    # Verify order
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id
    assert resp_get_order.json()["payment"]["authorised"] is True

    # Verify payment
    resp_get_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_payment.status_code == 200, f"Expected 200, got {resp_get_payment.status_code}: {resp_get_payment.text}"
    payments = resp_get_payment.json()
    assert isinstance(payments, list)
    assert len(payments) > 0
    assert payments[0]["authorised"] is True
    assert payments[0]["orderId"] == order_id

    # Verify shipment
    resp_get_shipment = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_shipment.status_code == 200, f"Expected 200, got {resp_get_shipment.status_code}: {resp_get_shipment.text}"
    assert resp_get_shipment.json()["orderId"] == order_id

# --- id=306  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    username = f"user_{random_string()}"

    # Register user
    resp_reg = requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    # Add address
    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json()["id"]

    resp_get_addr = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    # Add card
    resp_card = requests.post(get_url("user", "/cards"), json={
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    # Add item to cart (total > 100 for declined payment)
    resp_item = requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": "sock2",
        "quantity": 2,
        "unitPrice": 60.0
    }, timeout=10)
    assert resp_item.status_code == 201, f"Expected 201, got {resp_item.status_code}: {resp_item.text}"

    resp_get_item = requests.get(get_url("carts", f"/carts/{username}/items/sock2"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"

    # Place order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
