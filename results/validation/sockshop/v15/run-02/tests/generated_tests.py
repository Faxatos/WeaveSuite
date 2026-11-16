# Tests generated in iteration 02
# Captured: 2026-06-07T02:42:07
# Count:    17
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1209  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{random_string()}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1210  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{random_string()}"
    payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp1 = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp2 = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

    resp_get2 = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"

# --- id=1211  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, "wrong_pass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1212  name='User Add Address' ---
def test_user_add_address():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    payload = {
        "userID": username,
        "number": "123",
        "street": "Main St",
        "city": "Anytown",
        "postcode": "12345",
        "country": "USA"
    }
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None, "Expected address ID in response"

    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("city") == "Anytown"

# --- id=1213  name='User Add Card' ---
def test_user_add_card():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    payload = {
        "userID": username,
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123"
    }
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None, "Expected card ID in response"

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("expires") == "12/25"

# --- id=1214  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if items:
        item_id = items[0]["id"]
        resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
        assert resp_get.json().get("id") == item_id

# --- id=1215  name='Catalogue Not Found' ---
def test_catalogue_get_not_found():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp = requests.get(get_url("catalogue", f"/catalogue/{username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1216  name='Catalogue Images Not Found' ---
def test_catalogue_images_not_found():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp = requests.get(get_url("catalogue", f"/catalogue/images/{username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1217  name='Carts Add Item Cumulative' ---
def test_carts_add_item_cumulative():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item_id = cat_resp.json()[0]["id"]
    item_price = cat_resp.json()[0]["price"]

    payload1 = {"itemId": item_id, "quantity": 2, "unitPrice": item_price}
    resp1 = requests.post(get_url("carts", f"/carts/{username}/items"), json=payload1, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"
    resp_get1 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    assert resp_get1.json().get("quantity") == 2

    payload2 = {"itemId": item_id, "quantity": 3, "unitPrice": item_price}
    resp2 = requests.post(get_url("carts", f"/carts/{username}/items"), json=payload2, timeout=10)
    assert resp2.status_code == 201, f"Expected 201, got {resp2.status_code}: {resp2.text}"
    resp_get2 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 5

# --- id=1218  name='Carts Item Not Found' ---
def test_carts_get_item_not_found():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item_id = cat_resp.json()[0]["id"]

    cart_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    resp_get_item = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"

    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_404 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_404.status_code == 404, f"Expected 404, got {resp_get_404.status_code}: {resp_get_404.text}"

# --- id=1219  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    session_id = f"session_{random_string()}"
    resp_reg2 = requests.post(get_url("user", "/register"), json={"username": session_id, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg2.status_code == 200, f"Expected 200, got {resp_reg2.status_code}: {resp_reg2.text}"
    resp_get_user2 = requests.get(get_url("user", f"/customers/{session_id}"), timeout=10)
    assert resp_get_user2.status_code == 200, f"Expected 200, got {resp_get_user2.status_code}: {resp_get_user2.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1220  name='Orders Create Success' ---
def test_orders_create_success():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    addr_payload = {"userID": username, "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json().get("id")
    addr_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"

    card_payload = {"userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item_id = cat_resp.json()[0]["id"]

    cart_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"
    cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert cart_get.status_code == 200, f"Expected 200, got {cart_get.status_code}: {cart_get.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")
    assert order_id is not None

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("id") == order_id

# --- id=1221  name='Orders Create Payment Declined' ---
def test_orders_create_payment_declined():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    addr_resp = requests.post(get_url("user", "/addresses"), json={"userID": username, "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"}, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json().get("id")
    addr_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"

    card_resp = requests.post(get_url("user", "/cards"), json={"userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")
    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item_id = cat_resp.json()[0]["id"]

    cart_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 150.0}
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"
    cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert cart_get.status_code == 200, f"Expected 200, got {cart_get.status_code}: {cart_get.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 404, f"Expected 404, got {resp_search.status_code}: {resp_search.text}"

# --- id=1222  name='Orders Not Found' ---
def test_orders_get_not_found():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp = requests.get(get_url("orders", f"/orders/{username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1223  name='Payment Authorize Success' ---
def test_payment_authorize_success():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    order_id = username
    payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "Test", "lastName": "User"},
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) > 0
    assert auths[0].get("authorised") is True

# --- id=1224  name='Payment Authorize Decline' ---
def test_payment_authorize_decline():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    order_id = username
    payload = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "Test", "lastName": "User"},
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) > 0
    assert auths[0].get("authorised") is False

# --- id=1225  name='Shipping Create And' ---
def test_shipping_create_and_get():
    username = f"user_{random_string()}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"
    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    order_id = username
    payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"}
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
