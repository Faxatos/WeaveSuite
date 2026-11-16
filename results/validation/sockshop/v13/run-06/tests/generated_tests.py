# Tests generated in iteration 06
# Captured: 2026-06-06T13:16:25
# Count:    18
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=984  name='Orders E2e Workflow' ---
def test_orders_e2e_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"
    user_data = resp_get_user.json()
    assert user_data.get("username") == user_payload["username"]
    assert user_data.get("email") == user_payload["email"]
    assert user_data.get("firstName") == user_payload["firstName"]
    assert user_data.get("lastName") == user_payload["lastName"]

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addr_data = resp_get_addr.json()
    assert addr_data["city"] == address_payload["city"]
    assert addr_data["country"] == address_payload["country"]
    assert addr_data["number"] == address_payload["number"]
    assert addr_data["postcode"] == address_payload["postcode"]
    assert addr_data["street"] == address_payload["street"]

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    card_data = resp_get_card.json()
    assert card_data["ccv"] == card_payload["ccv"]
    assert card_data["expires"] == card_payload["expires"]
    assert "longNum" in card_data

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]
    item_price = item["price"]

    cart_item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_cart_data = resp_cart.json()
    assert resp_cart_data["itemId"] == cart_item_payload["itemId"]
    assert resp_cart_data["quantity"] == cart_item_payload["quantity"]
    assert resp_cart_data["unitPrice"] == cart_item_payload["unitPrice"]

    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"
    cart_item_data = resp_get_cart.json()
    assert cart_item_data["itemId"] == cart_item_payload["itemId"]
    assert cart_item_data["quantity"] == cart_item_payload["quantity"]
    assert cart_item_data["unitPrice"] == cart_item_payload["unitPrice"]

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

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    get_order_data = resp_get_order.json()
    assert get_order_data["id"] == order_id
    assert get_order_data["payment"]["authorised"] is True

# --- id=985  name='Carts Cumulative State' ---
def test_carts_cumulative_state():
    username = f"user_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]
    item_price = item["price"]

    cart_item_payload_1 = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": item_price
    }
    resp_cart_1 = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload_1, timeout=10)
    assert resp_cart_1.status_code == 201, f"Expected 201, got {resp_cart_1.status_code}: {resp_cart_1.text}"

    resp_get_1 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_1.status_code == 200, f"Expected 200, got {resp_get_1.status_code}: {resp_get_1.text}"
    assert resp_get_1.json()["quantity"] == 2

    cart_item_payload_2 = {
        "itemId": item_id,
        "quantity": 3,
        "unitPrice": item_price
    }
    resp_cart_2 = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload_2, timeout=10)
    assert resp_cart_2.status_code == 201, f"Expected 201, got {resp_cart_2.status_code}: {resp_cart_2.text}"

    resp_get_2 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_2.status_code == 200, f"Expected 200, got {resp_get_2.status_code}: {resp_get_2.text}"
    assert resp_get_2.json()["quantity"] == 5

# --- id=986  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    resp_1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_1.status_code == 200, f"Expected 200, got {resp_1.status_code}: {resp_1.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_2 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_2.status_code == 409, f"Expected 409, got {resp_2.status_code}: {resp_2.text}"

# --- id=987  name='Orders Payment Not Authorized' ---
def test_orders_payment_not_authorized():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp_user = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item = next((i for i in items if i.get("price", 0) > 0), None)
    assert item is not None, "No item with price > 0 found"
    item_id = item["id"]
    item_price = item["price"]

    quantity = int(101.0 / item_price) + 1

    cart_item_payload = {
        "itemId": item_id,
        "quantity": quantity,
        "unitPrice": item_price
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=988  name='Carts Item' ---
def test_carts_delete_item():
    username = f"user_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    cart_item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=989  name='Carts Item' ---
def test_carts_patch_item():
    username = f"user_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    cart_item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    patch_payload = {
        "itemId": item_id,
        "quantity": 10,
        "unitPrice": item_price
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_patch = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_patch.status_code == 200, f"Expected 200, got {resp_get_patch.status_code}: {resp_get_patch.text}"
    assert resp_get_patch.json()["quantity"] == 10

# --- id=990  name='Carts Cart' ---
def test_carts_delete_cart():
    username = f"user_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    cart_item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) > 0

    resp_del = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get_del.status_code == 200, f"Expected 200, got {resp_get_del.status_code}: {resp_get_del.text}"
    assert len(resp_get_del.json()) == 0

# --- id=991  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp_user = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpassword"), timeout=10)
    assert resp_login.status_code == 401, f"Expected 401, got {resp_login.status_code}: {resp_login.text}"

# --- id=992  name='Orders Search Not Found' ---
def test_orders_search_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp_user = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 404, f"Expected 404, got {resp_search.status_code}: {resp_search.text}"

# --- id=993  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp_user = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    session_id = f"session_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    cart_item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=cart_item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_get_cart = requests.get(get_url("carts", f"/carts/{session_id}/items"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    resp_del = requests.delete(get_url("carts", f"/carts/{session_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{session_id}/items"), timeout=10)
    assert resp_get_del.status_code == 200, f"Expected 200, got {resp_get_del.status_code}: {resp_get_del.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=994  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp_user = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp_cat = requests.get(get_url("catalogue", f"/catalogue/{username}"), timeout=10)
    assert resp_cat.status_code == 404, f"Expected 404, got {resp_cat.status_code}: {resp_cat.text}"

# --- id=995  name='Catalogue Image Not Found' ---
def test_catalogue_image_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp_user = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{username}"), timeout=10)
    assert resp_img.status_code == 404, f"Expected 404, got {resp_img.status_code}: {resp_img.text}"

# --- id=996  name='Orders Not Found' ---
def test_orders_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp_user = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp_order = requests.get(get_url("orders", f"/orders/{username}"), timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=997  name='Carts Async Item' ---
def test_carts_delete_async_item():
    username = f"user_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    cart_item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }
    resp_cart = requests.post(get_url("carts", f"/carts-async/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_get = requests.get(get_url("carts", f"/carts-async/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_del = requests.delete(get_url("carts", f"/carts-async/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts-async/{username}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=998  name='Carts Async Merge Not Found' ---
def test_carts_async_merge_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp_user = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    session_id = f"session_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    cart_item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item_price
    }
    resp_cart = requests.post(get_url("carts", f"/carts-async/{session_id}/items"), json=cart_item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_get_cart = requests.get(get_url("carts", f"/carts-async/{session_id}/items"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    resp_del = requests.delete(get_url("carts", f"/carts-async/{session_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts-async/{session_id}/items"), timeout=10)
    assert resp_get_del.status_code == 200, f"Expected 200, got {resp_get_del.status_code}: {resp_get_del.text}"

    resp_merge = requests.get(get_url("carts", f"/carts-async/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=999  name='Catalogue Tags And Size' ---
def test_catalogue_tags_and_size():
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags_data = resp_tags.json()
    assert "tags" in tags_data

    if len(tags_data["tags"]) > 0:
        tag = tags_data["tags"][0]
        resp_size = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        size_data = resp_size.json()
        assert "size" in size_data

# --- id=1000  name='User Operations' ---
def test_user_delete_operations():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }
    resp_user = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_user.status_code == 200, f"Expected 200, got {resp_user.status_code}: {resp_user.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    address_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_get_addrs = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get_addrs.status_code == 200, f"Expected 200, got {resp_get_addrs.status_code}: {resp_get_addrs.text}"
    addrs_data = resp_get_addrs.json()
    if "_embedded" in addrs_data and "address" in addrs_data["_embedded"]:
        for addr in addrs_data["_embedded"]["address"]:
            assert addr.get("id") != addr_id

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    resp_get_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get_cards.status_code == 200, f"Expected 200, got {resp_get_cards.status_code}: {resp_get_cards.text}"
    cards_data = resp_get_cards.json()
    if "_embedded" in cards_data and "card" in cards_data["_embedded"]:
        for card in cards_data["_embedded"]["card"]:
            assert card.get("id") != card_id

    resp_del_cust = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_cust.status_code == 200, f"Expected 200, got {resp_del_cust.status_code}: {resp_del_cust.text}"

    resp_get_custs = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_get_custs.status_code == 200, f"Expected 200, got {resp_get_custs.status_code}: {resp_get_custs.text}"
    custs_data = resp_get_custs.json()
    if "_embedded" in custs_data and "customer" in custs_data["_embedded"]:
        for cust in custs_data["_embedded"]["customer"]:
            assert cust.get("username") != username

# --- id=1001  name='Payment Shipping Direct' ---
def test_payment_shipping_direct():
    order_id = f"order_{uuid.uuid4().hex[:8]}"

    payment_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "SW1A 1AA",
            "street": "Downing Street"
        },
        "amount": 50.00,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "John",
            "lastName": "Doe"
        },
        "orderId": order_id
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    pay_data = resp_pay.json()
    assert pay_data["authorised"] is True
    assert pay_data["orderId"] == order_id

    resp_get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    get_pay_data = resp_get_pay.json()
    assert len(get_pay_data) > 0
    assert get_pay_data[0]["orderId"] == order_id
    assert get_pay_data[0]["authorised"] is True

    shipping_payload = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "SW1A 1AA",
            "street": "Downing Street"
        },
        "itemCount": 2,
        "orderId": order_id
    }
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data["orderId"] == order_id
    assert "carrier" in ship_data
    assert "trackingNumber" in ship_data

    resp_get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    get_ship_data = resp_get_ship.json()
    assert get_ship_data["orderId"] == order_id
    assert get_ship_data["carrier"] == ship_data["carrier"]
    assert get_ship_data["trackingNumber"] == ship_data["trackingNumber"]
