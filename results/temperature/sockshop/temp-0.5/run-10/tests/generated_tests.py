# Tests generated in iteration 10
# Captured: 2026-07-04T17:27:01
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=504  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=505  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    resp = requests.get(get_url("user", "/login"), auth=("nonexistent", "wrongpwd"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=506  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addresses = resp_addr_get.json().get("_embedded", {}).get("address", [])
    assert len(addresses) == 1
    assert addresses[0]["city"] == "City"
    assert addresses[0]["id"] == addr_id

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    cards = resp_card_get.json().get("_embedded", {}).get("card", [])
    assert len(cards) == 1
    assert cards[0]["id"] == card_id
    assert cards[0]["longNum"] == "************3456"

# --- id=507  name='Carts Catalogue And Items' ---
def test_carts_catalogue_and_items():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    socks = resp_cat.json()
    assert len(socks) > 0
    sock = socks[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    username = f"user_{uuid.uuid4().hex[:8]}"

    item_data = {"itemId": sock_id, "quantity": 2, "unitPrice": sock_price}
    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_cart = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart.status_code == 200, f"Expected 200, got {resp_cart.status_code}: {resp_cart.text}"
    items = resp_cart.json()
    assert len(items) == 1
    assert items[0]["itemId"] == sock_id
    assert items[0]["quantity"] == 2

    item_data_patch = {"itemId": sock_id, "quantity": 5, "unitPrice": sock_price}
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=item_data_patch, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_item = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["quantity"] == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_item_del = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp_item_del.status_code == 404, f"Expected 404, got {resp_item_del.status_code}: {resp_item_del.text}"

# --- id=508  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/nonexistent_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=509  name='Orders Place Order Success' ---
def test_orders_place_order_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = resp_addr.json()["id"]

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json()["id"]

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    sock = resp_cat.json()[0]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order["id"]
    assert order["customer"]["username"] == username
    assert order["status"] in ["CREATED", "PAID", "SHIPPED"]

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json()["id"] == order_id

    resp_orders_list = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_orders_list.status_code == 200, f"Expected 200, got {resp_orders_list.status_code}: {resp_orders_list.text}"
    customer_orders = resp_orders_list.json().get("_embedded", {}).get("customerOrders", [])
    assert len(customer_orders) > 0
    assert any(o["id"] == order_id for o in customer_orders)

    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    payments = resp_pay.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id

    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json()["orderId"] == order_id

# --- id=510  name='Orders Place Order Empty Cart 406' ---
def test_orders_place_order_empty_cart_406():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = resp_addr.json()["id"]

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json()["id"]

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=511  name='Orders Place Order Invalid Address Uri 404' ---
def test_orders_place_order_invalid_address_uri_404():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json()["id"]

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    sock = resp_cat.json()[0]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format_no_colon",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=512  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username
    assert "firstName" not in resp_get.json() or resp_get.json().get("firstName") is None

    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=513  name='Carts Merge' ---
def test_carts_merge():
    username = f"user_{uuid.uuid4().hex[:8]}"
    session_id = f"session_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    sock = resp_cat.json()[0]

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)

    resp_merge = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_cart = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart.status_code == 200, f"Expected 200, got {resp_cart.status_code}: {resp_cart.text}"
    assert len(resp_cart.json()) == 1
    assert resp_cart.json()[0]["itemId"] == sock["id"]

    bad_session = "nonexistent_session"
    resp_merge_bad = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={bad_session}"), timeout=10)
    assert resp_merge_bad.status_code == 404, f"Expected 404, got {resp_merge_bad.status_code}: {resp_merge_bad.text}"
