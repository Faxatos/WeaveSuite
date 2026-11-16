# Tests generated in iteration 03
# Captured: 2026-06-05T19:26:45
# Count:    11
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=672  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register User
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Follow-up GET (Login)
    resp_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Follow-up GET (Customer Details)
    resp_cust = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    if resp_cust.text:
        cust_data = resp_cust.json()
        assert cust_data.get("username") == user_payload["username"]
        assert cust_data.get("email") == user_payload["email"]
        assert cust_data.get("firstName") == user_payload["firstName"]
        assert cust_data.get("lastName") == user_payload["lastName"]

# --- id=673  name='User Register Existing User 409' ---
def test_user_register_existing_user_409():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # First registration
    resp1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    # Second registration (Negative)
    resp2 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=674  name='User Login Unauthorized 401' ---
def test_user_login_unauthorized_401():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "correctpassword",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # Login with wrong password (Negative)
    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, "wrongpassword"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=675  name='Carts Add Update Item' ---
def test_carts_add_update_delete_item():
    # Get real item from catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    cat_items = resp_cat.json()
    assert len(cat_items) > 0
    item_id = cat_items[0]["id"]

    # Register user to get a valid customer ID
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    customer_id = username

    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 15.5}

    # Add item
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    add_data = resp_add.json()
    assert add_data.get("itemId") == item_payload["itemId"]
    assert add_data.get("quantity") == item_payload["quantity"]
    assert add_data.get("unitPrice") == item_payload["unitPrice"]

    # Follow-up GET
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data.get("itemId") == item_payload["itemId"]
    assert get_data.get("quantity") == item_payload["quantity"]
    assert get_data.get("unitPrice") == item_payload["unitPrice"]

    # Update item
    item_payload["quantity"] = 5
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Follow-up GET
    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 5

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Follow-up GET (Negative - 404)
    resp_get3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get3.status_code == 404, f"Expected 404, got {resp_get3.status_code}: {resp_get3.text}"

# --- id=676  name='Orders Place Order Success' ---
def test_orders_place_order_success():
    # 1. Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    cat_items = resp_cat.json()
    assert len(cat_items) > 0
    sock_id = cat_items[0]["id"]

    # 2. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # 3. Add Address
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    # Follow-up GET Address
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_data = resp_addr_get.json()
    assert addr_data.get("city") == addr_payload["city"]
    assert addr_data.get("country") == addr_payload["country"]
    assert addr_data.get("number") == addr_payload["number"]
    assert addr_data.get("postcode") == addr_payload["postcode"]
    assert addr_data.get("street") == addr_payload["street"]

    # 4. Add Card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    # Follow-up GET Card
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data.get("ccv") == card_payload["ccv"]
    assert card_data.get("expires") == card_payload["expires"]
    assert card_data.get("longNum", "").endswith("3456")

    # 5. Add to Cart
    cart_payload = {"itemId": sock_id, "quantity": 1, "unitPrice": 50.0}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    # 6. Place Order
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
    assert order_data.get("payment", {}).get("authorised") is True

    # Follow-up GET Order
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json()["id"] == order_id

    # 7. Verify Payment
    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    pay_data = resp_pay.json()
    assert len(pay_data) > 0
    assert pay_data[0].get("orderId") == order_id
    assert pay_data[0].get("authorised") is True

    # 8. Verify Shipping
    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data.get("orderId") == order_id

# --- id=677  name='Orders Payment Declined 406' ---
def test_orders_payment_declined_406():
    # 1. Get catalogue item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    sock_id = resp_cat.json()[0]["id"]

    # 2. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # 3. Add Address
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "NW1", "street": "Baker St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json()["id"]

    # 4. Add Card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json()["id"]

    # 5. Add to Cart with price > 100 to trigger decline
    cart_payload = {"itemId": sock_id, "quantity": 1, "unitPrice": 150.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)

    # 6. Place Order (Negative - 406)
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=678  name='Carts Merge Success' ---
def test_carts_merge_success():
    # Get real item from catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    item_id = resp_cat.json()[0]["id"]

    # Register user
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    customer_id = username
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    # Add item to session cart
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    resp_add = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Merge session cart into customer cart
    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    # Follow-up GET customer cart
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) >= 1
    assert any(item.get("itemId") == item_id for item in items)

# --- id=679  name='Carts Merge Not Found 404' ---
def test_carts_merge_not_found_404():
    # Get real item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp_cat.json()[0]["id"]

    # Register user
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)
    customer_id = username
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    # Create session cart
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    # Delete session cart
    requests.delete(get_url("carts", f"/carts/{session_id}"), timeout=10)

    # Attempt to merge deleted session cart (Negative - 404)
    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=680  name='Orders Search Customer 404' ---
def test_orders_search_customer_404():
    # Register user
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # Search orders for user with no orders (Negative - 404)
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=681  name='Catalogue And Tags' ---
def test_catalogue_and_tags_get():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"

    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=682  name='User Collections' ---
def test_user_collections_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    resp_custs = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_custs.status_code == 200, f"Expected 200, got {resp_custs.status_code}: {resp_custs.text}"

    resp_addrs = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addrs.status_code == 200, f"Expected 200, got {resp_addrs.status_code}: {resp_addrs.text}"

    resp_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cards.status_code == 200, f"Expected 200, got {resp_cards.status_code}: {resp_cards.text}"
