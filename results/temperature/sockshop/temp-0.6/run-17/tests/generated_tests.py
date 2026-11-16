# Tests generated in iteration 17
# Captured: 2026-07-05T10:52:21
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=849  name='User Register And Conflict' ---
def test_user_register_and_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_req = {"username": username, "password": password, "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}

    resp = requests.post(get_url("user", "/register"), json=user_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_req, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=850  name='User Login Failure' ---
def test_user_login_failure():
    username, _ = create_user()
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=851  name='User Address Lifecycle' ---
def test_user_address_lifecycle():
    username, _ = create_user()
    addr_req = {"street": "123 Main St", "city": "Springfield", "country": "USA", "number": "12", "postcode": "12345", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["city"] == "Springfield"

    resp_del = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_col = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_col.status_code == 200, f"Expected 200, got {resp_col.status_code}: {resp_col.text}"
    addresses = resp_col.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses)

# --- id=852  name='User Card Lifecycle' ---
def test_user_card_lifecycle():
    username, _ = create_user()
    card_req = {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["expires"] == "12/25"

    resp_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_col = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_col.status_code == 200, f"Expected 200, got {resp_col.status_code}: {resp_col.text}"
    cards = resp_col.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

# --- id=853  name='Customer Deletion' ---
def test_customer_deletion():
    username, _ = create_user()
    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("firstName") is None

# --- id=854  name='Catalogue Listing And Retrieval' ---
def test_catalogue_listing_and_retrieval():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == item_id

# --- id=855  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid-id-12345"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=856  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    username, _ = create_user()
    item = get_catalogue_item()
    item_id = item["id"]

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": item["price"]}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 1

    cart_item_update = {"itemId": item_id, "quantity": 5, "unitPrice": item["price"]}
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=cart_item_update, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get2 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["quantity"] == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get3 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get3.status_code == 404, f"Expected 404, got {resp_get3.status_code}: {resp_get3.text}"

# --- id=857  name='Carts Merge' ---
def test_carts_merge():
    username, _ = create_user()
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    item = get_catalogue_item()

    cart_item = {"itemId": item["id"], "quantity": 2, "unitPrice": item["price"]}
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=cart_item, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{session_id}/items/{item['id']}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get_cust = requests.get(get_url("carts", f"/carts/{username}/items/{item['id']}"), timeout=10)
    assert resp_get_cust.status_code == 200, f"Expected 200, got {resp_get_cust.status_code}: {resp_get_cust.text}"
    assert resp_get_cust.json()["quantity"] == 2

# --- id=858  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    username, _ = create_user()
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    resp_merge = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=859  name='Orders Creation' ---
def test_orders_creation():
    username, _ = create_user()
    address_id = create_address(username)
    card_id = create_card(username)
    item = get_catalogue_item()

    cart_item = {"itemId": item["id"], "quantity": 2, "unitPrice": item["price"]}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order["id"]

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json()["id"] == order_id
    assert resp_order_get.json()["customer"]["username"] == username

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in orders)

# --- id=860  name='Orders Creation Empty Cart' ---
def test_orders_creation_empty_cart():
    username, _ = create_user()
    address_id = create_address(username)
    card_id = create_card(username)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=861  name='Orders Creation Invalid Uri' ---
def test_orders_creation_invalid_uri():
    username, _ = create_user()
    order_req = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_format",
        "card": "/cards/invalid_format",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=862  name='Payment Authorization' ---
def test_payment_authorization():
    username, _ = create_user()
    address_id = create_address(username)
    card_id = create_card(username)
    item = get_catalogue_item()

    cart_item = {"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json()["id"]

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    initial_count = len(resp_get.json())

    payment_req = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "Test", "lastName": "User"},
        "address": {"city": "Springfield", "country": "USA", "number": "12", "postcode": "12345", "street": "123 Main St"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"}
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert "authorised" in resp_pay.json()

    resp_get2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert len(resp_get2.json()) == initial_count + 1

# --- id=863  name='Shipping Request' ---
def test_shipping_request():
    username, _ = create_user()
    address_id = create_address(username)
    card_id = create_card(username)
    item = get_catalogue_item()

    cart_item = {"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json()["id"]

    shipping_req = {
        "orderId": order_id,
        "itemCount": 1,
        "address": {"city": "Springfield", "country": "USA", "number": "12", "postcode": "12345", "street": "123 Main St"}
    }
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json()["orderId"] == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
