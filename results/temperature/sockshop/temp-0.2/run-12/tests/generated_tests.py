# Tests generated in iteration 01
# Captured: 2026-06-29T08:00:35
# Count:    16
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=170  name='User Register And Conflict' ---
def test_user_register_and_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {"username": username, "password": "password", "email": f"{username}@test.com", "firstName": "Test", "lastName": "User"}
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username

    resp_conflict = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=171  name='User Login' ---
def test_user_login():
    username = _register_user()

    resp = requests.get(get_url("user", "/login"), auth=(username, "password"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_fail = requests.get(get_url("user", "/login"), auth=(username, "wrong"), timeout=10)
    assert resp_fail.status_code == 401, f"Expected 401, got {resp_fail.status_code}: {resp_fail.text}"

# --- id=172  name='User Add Address' ---
def test_user_add_address():
    username = _register_user()

    payload = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")

    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("city") == "City"

# --- id=173  name='User Add Card' ---
def test_user_add_card():
    username = _register_user()

    payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert "longNum" in resp_get.json()
    assert resp_get.json().get("ccv") == "123"

# --- id=174  name='User Customer' ---
def test_user_delete_customer():
    username = _register_user()

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert not resp_get.json().get("firstName")

# --- id=175  name='User Address' ---
def test_user_delete_address():
    username = _register_user()

    payload = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json().get("id")

    addr_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"

    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    addresses = resp_get.json().get("_embedded", {}).get("address", [])
    assert len(addresses) == 0

# --- id=176  name='User Card' ---
def test_user_delete_card():
    username = _register_user()

    payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")

    card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cards = resp_get.json().get("_embedded", {}).get("card", [])
    assert len(cards) == 0

# --- id=177  name='Catalogue And Not Found' ---
def test_catalogue_get_and_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if items:
        item_id = items[0]["id"]
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"

    resp_404 = requests.get(get_url("catalogue", "/catalogue/invalid_id_123"), timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

# --- id=178  name='Carts Add And Item' ---
def test_carts_add_and_delete_item():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id = items[0]["id"]

    username = _register_user()

    payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 2

    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=179  name='Carts Item' ---
def test_carts_patch_item():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    item_id = cat_resp.json()[0]["id"]

    username = _register_user()

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.5}
    post_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)
    assert post_resp.status_code == 201, f"Expected 201, got {post_resp.status_code}: {post_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 10.5}
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=patch_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 5

# --- id=180  name='Orders Create And Search' ---
def test_orders_create_and_search():
    username, order_id = _create_order()

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    assert len(resp_search.json().get("_embedded", {}).get("customerOrders", [])) > 0

# --- id=181  name='Orders Missing Fields 406' ---
def test_orders_missing_fields_406():
    username = _register_user()

    order_payload = {
        "customer": f"/customers/{username}"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=182  name='Orders Invalid Uri 404' ---
def test_orders_invalid_uri_404():
    username = _register_user()

    order_payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_format",
        "card": "/cards/invalid_format",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=183  name='Payment Authorize' ---
def test_payment_authorize():
    username, order_id = _create_order()
    payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 1
    assert auths[-1].get("orderId") == order_id
    assert auths[-1].get("authorised") is True

# --- id=184  name='Payment Declined' ---
def test_payment_declined():
    username, order_id = _create_order()
    payload = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert auths[-1].get("authorised") is False

# --- id=185  name='Shipping Ship Order' ---
def test_shipping_ship_order():
    username, order_id = _create_order()
    payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"}
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
