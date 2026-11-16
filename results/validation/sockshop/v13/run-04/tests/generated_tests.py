# Tests generated in iteration 04
# Captured: 2026-06-06T11:47:51
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=959  name='Orders E2e Workflow' ---
def test_orders_e2e_workflow():
    username = f"user_{generate_random_string()}"
    password = "password123"

    create_user(username, password)

    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    address_id = create_address(username)
    card_id = create_card(username)

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Expected at least one item in catalogue"
    sock = items[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    add_item_to_cart(username, sock_id, sock_price, quantity=1)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None, "Expected order id in response"
    assert order.get("payment", {}).get("authorised") is True, "Expected payment to be authorised"

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    fetched_order = resp_get.json()
    assert fetched_order.get("id") == order_id
    assert fetched_order.get("payment", {}).get("authorised") is True

# --- id=960  name='Carts Operations Cumulative State' ---
def test_carts_operations_cumulative_state():
    username = f"user_{generate_random_string()}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Expected at least one item in catalogue"
    sock = items[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    add_item_to_cart(username, sock_id, sock_price, quantity=1)
    add_item_to_cart(username, sock_id, sock_price, quantity=2)

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 3, f"Expected quantity 3, got {resp_get.json().get('quantity')}"

    cart_item_payload = {
        "itemId": sock_id,
        "quantity": 5,
        "unitPrice": sock_price
    }
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=cart_item_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 5, f"Expected quantity 5, got {resp_get.json().get('quantity')}"

    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=961  name='User Registration Conflict Negative' ---
def test_user_registration_conflict_negative():
    username = f"user_{generate_random_string()}"
    password = "password123"

    user_payload = create_user(username, password)

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=962  name='Orders Payment Not Authorized Negative' ---
def test_orders_payment_not_authorized_negative():
    username = f"user_{generate_random_string()}"
    password = "password123"

    create_user(username, password)
    address_id = create_address(username)
    card_id = create_card(username)

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    sock = items[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    add_item_to_cart(username, sock_id, sock_price, quantity=100)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=963  name='Catalogue Item Not Found Negative' ---
def test_catalogue_item_not_found_negative():
    fake_id = str(uuid.uuid4())
    resp = requests.get(get_url("catalogue", f"/catalogue/{fake_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=964  name='Catalogue Image Not Found Negative' ---
def test_catalogue_image_not_found_negative():
    fake_image = str(uuid.uuid4()) + ".jpg"
    resp = requests.get(get_url("catalogue", f"/catalogue/images/{fake_image}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=965  name='Orders Not Found Negative' ---
def test_orders_not_found_negative():
    fake_id = str(uuid.uuid4())
    resp = requests.get(get_url("orders", f"/orders/{fake_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=966  name='Orders Search Not Found Negative' ---
def test_orders_search_not_found_negative():
    fake_cust_id = str(uuid.uuid4())
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={fake_cust_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=967  name='User Login Unauthorized Negative' ---
def test_user_login_unauthorized_negative():
    username = f"user_{generate_random_string()}"
    password = "wrongpassword"
    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=968  name='Carts Item Not Found Negative' ---
def test_carts_item_not_found_negative():
    username = f"user_{generate_random_string()}"
    fake_item_id = str(uuid.uuid4())
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{fake_item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=969  name='Carts Merge Not Found Negative' ---
def test_carts_merge_not_found_negative():
    username = f"user_{generate_random_string()}"
    fake_session_id = str(uuid.uuid4())
    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={fake_session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=970  name='Carts Cart' ---
def test_carts_delete_cart():
    username = f"user_{generate_random_string()}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    sock = items[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    add_item_to_cart(username, sock_id, sock_price, quantity=1)

    resp = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0, "Expected cart to be empty after deletion"

# --- id=971  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{generate_random_string()}"
    password = "password123"

    create_user(username, password)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert username not in resp_get.text, "Expected customer to be deleted"

# --- id=972  name='Orders Search By Customer' ---
def test_orders_search_by_customer():
    username = f"user_{generate_random_string()}"
    password = "password123"

    create_user(username, password)
    address_id = create_address(username)
    card_id = create_card(username)

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    sock = items[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    add_item_to_cart(username, sock_id, sock_price, quantity=1)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    assert order_id in resp_search.text, "Expected order ID in search results"
