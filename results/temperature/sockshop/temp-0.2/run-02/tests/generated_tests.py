# Tests generated in iteration 02
# Captured: 2026-06-29T01:12:45
# Count:    19
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=25  name='User Register And' ---
def test_user_register_and_get():
    username = random_string()
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data.get("username") == username
    assert data.get("email") == payload["email"]
    assert data.get("firstName") == payload["firstName"]
    assert data.get("lastName") == payload["lastName"]
    assert "password" not in data or data["password"] != "password123"

# --- id=26  name='User Register Conflict' ---
def test_user_register_conflict():
    username = random_string()
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=27  name='User Add Address' ---
def test_user_add_address():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "W1",
        "street": "Baker St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None

    resp_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    addresses = resp_get.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == address_id for a in addresses)

# --- id=28  name='User Add Card' ---
def test_user_add_card():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    resp_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cards = resp_get.json().get("_embedded", {}).get("card", [])
    found = next((c for c in cards if c.get("id") == card_id), None)
    assert found is not None
    assert found.get("longNum", "").endswith("3456")
    assert found.get("longNum", "").startswith("*")

# --- id=29  name='User Customer' ---
def test_user_delete_customer():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username
    assert not resp_get.json().get("email")

# --- id=30  name='User Login' ---
def test_user_login():
    username = random_string()
    password = "password123"
    requests.post(get_url("user", "/register"), json={"username": username, "password": password, "email": "a@b.com"}, timeout=10)

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=31  name='User Login Fail' ---
def test_user_login_fail():
    resp = requests.get(get_url("user", "/login"), auth=("invalid", "invalid"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # --- Catalogue Service Tests ---

# --- id=32  name='Catalogue All And Item' ---
def test_catalogue_get_all_and_item():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if items:
        item_id = items[0]["id"]
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"

# --- id=33  name='Catalogue Item Not Found' ---
def test_catalogue_get_item_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # --- Carts Service Tests ---

# --- id=34  name='Carts Add And Items' ---
def test_carts_add_and_get_items():
    customer_id = random_string()
    item_id = random_string()
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.5}

    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i.get("itemId") == item_id and i.get("quantity") == 1 for i in items)

# --- id=35  name='Carts Update Item' ---
def test_carts_update_item():
    customer_id = random_string()
    item_id = random_string()
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.5}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)

    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 10.5}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 5

# --- id=36  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = random_string()
    item_id = random_string()
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.5}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=37  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = random_string()
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": "1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0

    # --- Orders Service Tests ---

# --- id=38  name='Orders Create And' ---
def test_orders_create_and_get():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item1", "quantity": 2, "unitPrice": 15.0}, timeout=10)

    payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp = requests.post(get_url("orders", "/orders"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_data = resp.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("customer", {}).get("username") == username
    assert order_data.get("total") == 30.0

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("id") == order_id

# --- id=39  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    payload = {
        "customer": "/customers/someone"
    }
    resp = requests.post(get_url("orders", "/orders"), json=payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=40  name='Orders Create Invalid Uri' ---
def test_orders_create_invalid_uri():
    payload = {
        "customer": "/customers/someone",
        "address": "/addresses/invalid_format",
        "card": "/cards/invalid_format",
        "items": "/carts/someone/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # --- Payment Service Tests ---

# --- id=41  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = str(uuid.uuid4())
    payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "A", "lastName": "B"},
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 1
    assert auths[-1].get("authorised") is True

# --- id=42  name='Payment Authorize Decline' ---
def test_payment_authorize_decline():
    order_id = str(uuid.uuid4())
    payload = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "A", "lastName": "B"},
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 1
    assert auths[-1].get("authorised") is False

    # --- Shipping Service Tests ---

# --- id=43  name='Shipping And' ---
def test_shipping_post_and_get():
    order_id = str(uuid.uuid4())
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
