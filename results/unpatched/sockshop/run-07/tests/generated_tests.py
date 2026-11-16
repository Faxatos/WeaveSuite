# Tests generated in iteration 07
# Captured: 2026-07-10T18:15:29
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=68  name='User Registration And Login' ---
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

    # 1. Register User
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Follow-up GET to verify user exists
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # 2. Login with valid credentials
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # 3. Negative: Login with invalid credentials
    resp_bad_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

    # 4. Negative: Duplicate Registration
    resp_dup = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

# --- id=69  name='Catalogue Browsing And Images' ---
def test_catalogue_browsing_and_images():
    # 1. Get all tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags_data = resp_tags.json()
    assert "tags" in tags_data

    # 2. Get catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert isinstance(items, list)

    if not items:
        pytest.skip("Catalogue is empty, cannot test specific item")

    item = items[0]
    item_id = item["id"]

    # 3. Get specific item
    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"

    # 4. Negative: Get non-existent item
    resp_bad_item = requests.get(get_url("catalogue", "/catalogue/invalid-id-9999"), timeout=10)
    assert resp_bad_item.status_code == 404, f"Expected 404, got {resp_bad_item.status_code}: {resp_bad_item.text}"

    # 5. Get image if available
    if item.get("imageUrl") and len(item["imageUrl"]) > 0:
        image_path = item["imageUrl"][0]
        image_name = image_path.split("/")[-1]
        resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

    # 6. Negative: Get non-existent image
    resp_bad_img = requests.get(get_url("catalogue", "/catalogue/images/nonexistent.jpg"), timeout=10)
    assert resp_bad_img.status_code == 404, f"Expected 404, got {resp_bad_img.status_code}: {resp_bad_img.text}"

# --- id=70  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = "3395a43e-2d88-40de-b95f-e00e1502085b" # Fallback ID
    price = 15.0

    # Try to get a real item from catalogue
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    if cat_resp.status_code == 200 and cat_resp.json():
        item_id = cat_resp.json()[0]["id"]
        price = cat_resp.json()[0].get("price", 15.0)

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": price}

    # 1. Add item to cart
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Follow-up GET items
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i.get("itemId") == item_id for i in items)

    # 2. Update item in cart
    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": price}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Follow-up GET specific item
    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json().get("quantity") == 5

    # 3. Delete item from cart
    resp_del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    # Follow-up GET specific item -> 404
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

    # 4. Delete cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    # 5. Negative: Delete cart again -> 404
    resp_del_cart_again = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart_again.status_code == 404, f"Expected 404, got {resp_del_cart_again.status_code}: {resp_del_cart_again.text}"

# --- id=71  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    # Add item to session cart
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": "sock1", "quantity": 2, "unitPrice": 10.0}, timeout=10)

    # Merge session cart into customer cart
    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    # Follow-up: customer cart should have the item
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert any(i.get("itemId") == "sock1" for i in resp_get.json())

    # Negative: merge non-existent session cart
    bad_session = f"bad_{uuid.uuid4().hex[:8]}"
    resp_bad_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={bad_session}"), timeout=10)
    assert resp_bad_merge.status_code == 404, f"Expected 404, got {resp_bad_merge.status_code}: {resp_bad_merge.text}"

# --- id=72  name='Payment And Shipping' ---
def test_payment_and_shipping():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    address = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Test Street"
    }
    customer = {
        "firstName": "John",
        "lastName": "Doe"
    }
    card = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456"
    }

    # 1. Authorize Payment
    payment_req = {
        "address": address,
        "amount": 99.99,
        "card": card,
        "customer": customer,
        "orderId": order_id
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth_res = resp_pay.json()
    assert auth_res.get("orderId") == order_id
    assert "authorised" in auth_res

    # Follow-up GET payment
    resp_pay_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay_get.status_code == 200, f"Expected 200, got {resp_pay_get.status_code}: {resp_pay_get.text}"

    # 2. Ship Order
    shipping_req = {
        "address": address,
        "itemCount": 2,
        "orderId": order_id
    }
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_res = resp_ship.json()
    assert ship_res.get("orderId") == order_id
    assert "trackingNumber" in ship_res

    # Follow-up GET shipping
    resp_ship_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship_get.status_code == 200, f"Expected 200, got {resp_ship_get.status_code}: {resp_ship_get.text}"
    assert resp_ship_get.json().get("orderId") == order_id

# --- id=73  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    # 1. Add Address
    addr_payload = {
        "city": "Paris",
        "country": "France",
        "number": "5",
        "postcode": "75001",
        "street": "Rue de Rivoli",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"

    # Follow-up GET addresses for customer
    resp_get_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    # 2. Add Card
    card_payload = {
        "ccv": "999",
        "expires": "01/28",
        "longNum": "1111222233334444",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"

    # Follow-up GET cards for customer
    resp_get_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

# --- id=74  name='Orders Search Not Found' ---
def test_orders_search_not_found():
    customer_id = f"nonexistent_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={customer_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
