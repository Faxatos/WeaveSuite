# Tests generated in iteration 08
# Captured: 2026-06-02T22:08:29
# Count:    13
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=51  name='User Register And' ---
def test_user_register_and_get():
    helper_create_user()

# --- id=52  name='User Login' ---
def test_user_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    reg_resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_user.status_code == 200, f"Expected 200, got {get_user.status_code}: {get_user.text}"

    login_resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

# --- id=53  name='User Add Address' ---
def test_user_add_address():
    username = helper_create_user()
    helper_create_address(username)

# --- id=54  name='User Add Card' ---
def test_user_add_card():
    username = helper_create_user()
    helper_create_card(username)

# --- id=55  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    item_id = helper_get_catalogue_item()
    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=56  name='Catalogue Size' ---
def test_catalogue_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=57  name='Catalogue Tags' ---
def test_catalogue_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=58  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    username = helper_create_user()
    item_id = helper_get_catalogue_item()
    helper_add_cart_item(username, item_id)

# --- id=59  name='Carts Item' ---
def test_carts_delete_item():
    username = helper_create_user()
    item_id = helper_get_catalogue_item()
    helper_add_cart_item(username, item_id)

    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=60  name='Orders Create And' ---
def test_orders_create_and_get():
    helper_create_order()

# --- id=61  name='Orders Search By Customer' ---
def test_orders_search_by_customer():
    username = helper_create_user()
    address_id = helper_create_address(username)
    card_id = helper_create_card(username)
    item_id = helper_get_catalogue_item()
    helper_add_cart_item(username, item_id)

    payload = {
        "customer": get_url("user", f"/customers/{username}"),
        "address": get_url("user", f"/addresses/{address_id}"),
        "card": get_url("user", f"/cards/{card_id}"),
        "items": get_url("carts", f"/carts/{username}/items")
    }
    resp = requests.post(get_url("orders", "/orders"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    search_resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"

# --- id=62  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = helper_create_order()

    payload = {
        "address": {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

# --- id=63  name='Shipping Ship' ---
def test_shipping_ship():
    order_id = helper_create_order()

    payload = {
        "address": {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"},
        "itemCount": 1,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
