# Tests generated in iteration 04
# Captured: 2026-06-21T12:27:21
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1299  name='Catalogue Browsing' ---
def test_catalogue_browsing():
    # GET /catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) > 0

    item = items[0]
    item_id = item["id"]

    # GET /catalogue/{id}
    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id

    # GET /tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=1300  name='User Registration And Authentication' ---
def test_user_registration_and_authentication():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "SecurePassword123!"
    email = f"{username}@example.com"
    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "John",
        "lastName": "Doe"
    }

    # POST /register
    resp_reg = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Verify via GET /customers/{id}
    resp_cust = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    cust_data = resp_cust.json()
    assert cust_data["username"] == username
    assert cust_data["email"] == email
    assert cust_data["firstName"] == "John"
    assert "password" not in cust_data or cust_data["password"] != password

    # GET /login (Success)
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # GET /login (Failure)
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "WrongPass!"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

    # POST /register (Conflict)
    resp_reg_conflict = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_reg_conflict.status_code == 409, f"Expected 409, got {resp_reg_conflict.status_code}: {resp_reg_conflict.text}"

# --- id=1301  name='Cart Management' ---
def test_cart_management():
    customer_id = f"cart_user_{uuid.uuid4().hex[:8]}"

    # Get a valid item ID from catalogue
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    catalogue_items = cat_resp.json()
    item_id = catalogue_items[0]["id"]
    unit_price = catalogue_items[0]["price"]

    # POST /carts/{customerId}/items
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"
    assert add_resp.json()["itemId"] == item_id

    # Verify via GET /carts/{customerId}/items
    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 1

    # Increment quantity
    add_resp2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add_resp2.status_code == 201, f"Expected 201, got {add_resp2.status_code}: {add_resp2.text}"

    # Verify increment
    get_resp2 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    items2 = get_resp2.json()
    assert items2[0]["quantity"] == 2

    # DELETE /carts/{customerId}/items/{itemId}
    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    # Verify deletion
    get_resp3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp3.status_code == 404, f"Expected 404, got {get_resp3.status_code}: {get_resp3.text}"

# --- id=1302  name='User Profile Management' ---
def test_user_profile_management():
    username = f"profile_user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    # Add Address
    addr_payload = {
        "city": "Testville",
        "country": "Testland",
        "number": "42",
        "postcode": "12345",
        "street": "Test St",
        "userID": username
    }
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    addr_id = addr_resp.json()["id"]

    # Verify Address
    get_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert get_addr.status_code == 200, f"Expected 200, got {get_addr.status_code}: {get_addr.text}"
    addresses = get_addr.json().get("_embedded", {}).get("address", [])
    assert len(addresses) >= 1
    assert any(a["id"] == addr_id for a in addresses)

    # Add Card
    card_payload = {
        "longNum": "1111222233334444",
        "expires": "12/26",
        "ccv": "123",
        "userID": username
    }
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    # Verify Card
    get_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert get_card.status_code == 200, f"Expected 200, got {get_card.status_code}: {get_card.text}"
    cards = get_card.json().get("_embedded", {}).get("card", [])
    assert len(cards) >= 1
    assert any(c["id"] == card_id for c in cards)

    # Verify masking
    added_card = next(c for c in cards if c["id"] == card_id)
    assert added_card["longNum"].endswith("4444")
    assert "*" in added_card["longNum"]

# --- id=1303  name='Order Placement E2e' ---
def test_order_placement_e2e():
    # 1. Setup User
    username = f"order_user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "O", "lastName": "U"}, timeout=10)

    # 2. Setup Address
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "US", "number": "1", "postcode": "123", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    # 3. Setup Card
    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "10/25", "ccv": "111", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    # 4. Setup Cart
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 2, "unitPrice": 15.0}, timeout=10)

    # 5. Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    assert "id" in order_data
    assert order_data["customer"]["username"] == username
    assert order_data["status"] in ["CREATED", "PAID", "SHIPPED"]

    # 6. Verify Order
    get_order = requests.get(get_url("orders", f"/orders/{order_data['id']}"), timeout=10)
    assert get_order.status_code == 200, f"Expected 200, got {get_order.status_code}: {get_order.text}"
    fetched_order = get_order.json()
    assert fetched_order["id"] == order_data["id"]
    assert fetched_order["customer"]["username"] == username
    assert len(fetched_order["items"]) >= 1
    assert fetched_order["items"][0]["itemId"] == item_id

# --- id=1304  name='Order Placement Failures' ---
def test_order_placement_failures():
    username = f"fail_user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    # Missing fields -> 406
    bad_payload = {
        "customer": f"/customers/{username}"
    }
    bad_resp = requests.post(get_url("orders", "/orders"), json=bad_payload, timeout=10)
    assert bad_resp.status_code == 406, f"Expected 406, got {bad_resp.status_code}: {bad_resp.text}"

    # Malformed composite ID -> 404
    malformed_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/invalid_format",
        "items": f"/carts/{username}/items"
    }
    malformed_resp = requests.post(get_url("orders", "/orders"), json=malformed_payload, timeout=10)
    assert malformed_resp.status_code == 404, f"Expected 404, got {malformed_resp.status_code}: {malformed_resp.text}"

# --- id=1305  name='Payment And Shipping Standalone' ---
def test_payment_and_shipping_standalone():
    # Create a real order first to get a valid orderId
    username = f"ps_user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "US", "number": "1", "postcode": "123", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]
    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "10/25", "ccv": "111", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_id = order_resp.json()["id"]

    # Payment
    pay_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"street": "S", "city": "C", "number": "1", "country": "US", "postcode": "123"},
        "card": {"longNum": "1234567812345678", "expires": "10/25", "ccv": "111"}
    }
    pay_resp = requests.post(get_url("payment-http", "/payments"), json=pay_payload, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    assert pay_resp.json()["orderId"] == order_id

    # Verify Payment
    get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_pay.status_code == 200, f"Expected 200, got {get_pay.status_code}: {get_pay.text}"
    payments = get_pay.json()
    assert len(payments) >= 1
    assert any(p["orderId"] == order_id for p in payments)

    # Shipping
    ship_payload = {
        "orderId": order_id,
        "itemCount": 1,
        "address": {"street": "S", "city": "C", "number": "1", "country": "US", "postcode": "123"}
    }
    ship_resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_payload, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    assert ship_resp.json()["orderId"] == order_id

    # Verify Shipping
    get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_ship.status_code == 200, f"Expected 200, got {get_ship.status_code}: {get_ship.text}"
    assert get_ship.json()["orderId"] == order_id
