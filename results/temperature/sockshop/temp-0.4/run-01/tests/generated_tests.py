# Tests generated in iteration 01
# Captured: 2026-06-29T16:30:43
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=277  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register user
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Verify via GET
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["username"] == username
    assert resp_get.json()["firstName"] == "Test"
    assert "password" not in resp_get.json()

    # Conflict: Register same user
    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Login success
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Login failure
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

# --- id=278  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    # Add address
    addr_payload = {"street": "123 Main St", "city": "Anytown", "country": "USA", "number": "123", "postcode": "12345", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    # GET address
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json()["street"] == "123 Main St"
    assert resp_get_addr.json()["id"] == addr_id

    # Add card
    card_payload = {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    # GET card
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    card_data = resp_get_card.json()
    assert card_data["id"] == card_id
    assert card_data["longNum"].endswith("5678")
    assert "*" in card_data["longNum"]

    # Verify collections
    resp_addr_col = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_col.status_code == 200, f"Expected 200, got {resp_addr_col.status_code}: {resp_addr_col.text}"
    addresses = resp_addr_col.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

    # Delete address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Verify deletion
    resp_addr_col_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_col_after.status_code == 200, f"Expected 200, got {resp_addr_col_after.status_code}: {resp_addr_col_after.text}"
    addresses_after = resp_addr_col_after.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses_after)

# --- id=279  name='Carts Item Lifecycle' ---
def test_carts_item_lifecycle():
    # Get real item from catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Add item to cart
    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": unit_price}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    assert resp_add.json()["itemId"] == item_id

    # GET cart items
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 2

    # PATCH item quantity
    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": unit_price}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # GET specific item
    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5

    # DELETE item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # GET specific item -> 404
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=280  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"street": "S", "city": "C", "country": "CO", "number": "1", "postcode": "P", "userID": username}, timeout=10)
    addr_id = resp_addr.json()["id"]

    resp_card = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = resp_card.json()["id"]

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp_cat.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data["id"]
    assert order_data["customer"]["username"] == username
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["itemId"] == item["id"]
    assert order_data["total"] == item["price"]

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id
    assert resp_get_order.json()["status"] in ["CREATED", "PAID", "SHIPPED"]

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    orders_list = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in orders_list)

# --- id=281  name='Orders Missing Fields Not Acceptable' ---
def test_orders_missing_fields_not_acceptable():
    order_payload = {
        "customer": "/customers/nonexistent"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "message" in resp_order.json()

# --- id=282  name='Orders Invalid Uri Format Not Found' ---
def test_orders_invalid_uri_format_not_found():
    order_payload = {
        "customer": "/customers/someuser",
        "address": "/addresses/invalid_format_no_colon",
        "card": "/cards/someuser:1234",
        "items": "/carts/someuser/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=283  name='Payment Authorization And History' ---
def test_payment_authorization_and_history():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payment_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"street": "123", "city": "C", "country": "US", "number": "1", "postcode": "123"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json()["authorised"] is True
    assert resp_pay.json()["orderId"] == order_id

    resp_hist = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_hist.status_code == 200, f"Expected 200, got {resp_hist.status_code}: {resp_hist.text}"
    history = resp_hist.json()
    assert len(history) == 1
    assert history[0]["orderId"] == order_id

    resp_pay2 = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay2.status_code == 200, f"Expected 200, got {resp_pay2.status_code}: {resp_pay2.text}"

    resp_hist2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_hist2.status_code == 200, f"Expected 200, got {resp_hist2.status_code}: {resp_hist2.text}"
    assert len(resp_hist2.json()) == 2

# --- id=284  name='Payment Amount Boundary Declined' ---
def test_payment_amount_boundary_declined():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payment_payload = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"street": "123", "city": "C", "country": "US", "number": "1", "postcode": "123"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json()["authorised"] is False

    resp_hist = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_hist.status_code == 200, f"Expected 200, got {resp_hist.status_code}: {resp_hist.text}"
    assert resp_hist.json()[0]["authorised"] is False

# --- id=285  name='Shipping Creation And Retrieval' ---
def test_shipping_creation_and_retrieval():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    shipping_payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"street": "123", "city": "C", "country": "US", "number": "1", "postcode": "123"}
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json()["orderId"] == order_id
    assert "carrier" in resp_ship.json()
    assert "trackingNumber" in resp_ship.json()

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
    assert resp_get.json()["trackingNumber"] == resp_ship.json()["trackingNumber"]
