# Tests generated in iteration 07
# Captured: 2026-06-30T13:06:25
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=584  name='User Register Login Conflict' ---
def test_user_register_login_conflict():
    username = f"user-{uuid.uuid4()}"
    user_payload = {
        "username": username,
        "password": "secret123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register user
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Conflict: Register same user
    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Login successfully
    resp_login = requests.get(get_url("user", "/login"), auth=(username, "secret123"), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Login failure (Negative test)
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

# --- id=585  name='User Profile Management' ---
def test_user_profile_management():
    username = f"u-{uuid.uuid4()}"
    user_payload = {
        "username": username,
        "password": "pass",
        "email": f"{username}@test.com",
        "firstName": "A",
        "lastName": "B"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # Add Address
    addr_payload = {
        "city": "Springfield",
        "country": "US",
        "number": "742",
        "postcode": "12345",
        "street": "Evergreen Terrace",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Verify Address via GET
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addr_data = resp_get_addr.json()
    assert addr_data["city"] == "Springfield"
    assert addr_data["street"] == "Evergreen Terrace"

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
    assert card_id is not None

    # Verify Card via GET
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    card_data = resp_get_card.json()
    assert card_data["expires"] == "12/25"
    assert card_data["longNum"] == "************3456"  # Masked as per spec

    # Verify Customer Collections
    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    assert any(a.get("id") == addr_id for a in resp_cust_addr.json().get("_embedded", {}).get("address", []))

    # Delete Address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Delete Customer
    resp_del_cust = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_cust.status_code == 200, f"Expected 200, got {resp_del_cust.status_code}: {resp_del_cust.text}"
    assert resp_del_cust.json().get("status") is True

    # Delete Customer Again (Observable state change check)
    resp_del_cust_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_cust_again.status_code == 200, f"Expected 200, got {resp_del_cust_again.status_code}: {resp_del_cust_again.text}"
    assert resp_del_cust_again.json().get("status") is False

# --- id=586  name='Catalogue Listing' ---
def test_catalogue_listing():
    # Get all catalogue items
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)
    assert len(socks) > 0

    sock_id = socks[0]["id"]

    # Get specific item
    resp_item = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == sock_id

    # Negative test: Non-existent item
    resp_not_found = requests.get(get_url("catalogue", "/catalogue/invalid-sock-id-123"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

    # Get tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=587  name='Carts Management' ---
def test_carts_management():
    cust_id = str(uuid.uuid4())
    item_id = f"item-{uuid.uuid4()}"

    # Add item to cart
    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 15.5}
    resp_add = requests.post(get_url("carts", f"/carts/{cust_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verify via GET items
    resp_get = requests.get(get_url("carts", f"/carts/{cust_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

    # Update item quantity
    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 15.5}
    resp_patch = requests.patch(get_url("carts", f"/carts/{cust_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify update via GET specific item
    resp_get_item = requests.get(get_url("carts", f"/carts/{cust_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5

    # Delete item
    resp_del_item = requests.delete(get_url("carts", f"/carts/{cust_id}/items/{item_id}"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    # Verify deletion
    resp_get_deleted = requests.get(get_url("carts", f"/carts/{cust_id}/items/{item_id}"), timeout=10)
    assert resp_get_deleted.status_code == 404, f"Expected 404, got {resp_get_deleted.status_code}: {resp_get_deleted.text}"

    # Delete cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{cust_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=588  name='Orders E2e Workflow' ---
def test_orders_e2e_workflow():
    username = f"u-{uuid.uuid4()}"
    # 1. Register User
    requests.post(get_url("user", "/register"), json={"username": username, "password": "p", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    # 2. Add Address & Card
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city":"C","country":"C","number":"1","postcode":"1","street":"S","userID":username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv":"123","expires":"12/25","longNum":"1234567890123456","userID":username}, timeout=10)
    card_id = card_resp.json()["id"]

    # 3. Get Catalogue Item and Add to Cart
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    sock_id = cat_resp.json()[0]["id"]
    sock_price = cat_resp.json()[0]["price"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock_id, "quantity": 2, "unitPrice": sock_price}, timeout=10)

    # 4. Create Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order["id"]
    assert order["total"] == sock_price * 2
    assert order["customer"]["username"] == username

    # 5. Verify Order via GET
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id

    # 6. Verify Order in Customer Search
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

# --- id=589  name='Orders Negative Workflows' ---
def test_orders_negative_workflows():
    username = f"u-{uuid.uuid4()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "p"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city":"C","country":"C","number":"1","postcode":"1","street":"S","userID":username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv":"123","expires":"12/25","longNum":"1234567890123456","userID":username}, timeout=10)
    card_id = card_resp.json()["id"]

    # 1. 406 Not Acceptable (Empty Cart)
    # We intentionally do NOT add items to the cart for this user
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_empty_cart = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_empty_cart.status_code == 406, f"Expected 406, got {resp_empty_cart.status_code}: {resp_empty_cart.text}"

    # 2. 404 Not Found (Invalid composite ID format)
    # We add an item so the cart is not empty, isolating the 404 failure
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "test-item", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_payload["address"] = "/addresses/invalid-id-without-colon"
    resp_invalid_id = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_invalid_id.status_code == 404, f"Expected 404, got {resp_invalid_id.status_code}: {resp_invalid_id.text}"

# --- id=590  name='Payment Standalone' ---
def test_payment_standalone():
    order_id = str(uuid.uuid4())
    pay_payload = {
        "address": {"city":"C","country":"C","number":"1","postcode":"1","street":"S"},
        "amount": 50.0,
        "card": {"ccv":"123","expires":"12/25","longNum":"1234567890123456"},
        "customer": {"firstName":"F","lastName":"L"},
        "orderId": order_id
    }

    # Authorize payment
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=pay_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json()["authorised"] is True

    # Verify authorization recorded
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["orderId"] == order_id
    assert auths[0]["authorised"] is True

# --- id=591  name='Shipping Standalone' ---
def test_shipping_standalone():
    order_id = str(uuid.uuid4())
    ship_payload = {
        "address": {"city":"C","country":"C","number":"1","postcode":"1","street":"S"},
        "itemCount": 3,
        "orderId": order_id
    }

    # Create shipment
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=ship_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json()["orderId"] == order_id

    # Verify shipment details
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
