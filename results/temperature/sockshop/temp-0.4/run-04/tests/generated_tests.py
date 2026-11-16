# Tests generated in iteration 04
# Captured: 2026-06-29T18:20:58
# Count:    18
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=308  name='User Register And Login' ---
def test_user_register_and_login():
    username = random_string()
    password = random_string()
    email = f"{username}@example.com"

    payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("username") == username
    assert data.get("email") == email
    assert data.get("firstName") == "Test"
    assert data.get("lastName") == "User"
    assert "password" not in data or data.get("password") != password

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=309  name='User Register Conflict' ---
def test_user_register_conflict():
    username = random_string()
    payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=310  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    resp = requests.get(get_url("user", "/login"), auth=("invalid", "invalid"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=311  name='User Add And Address' ---
def test_user_add_and_get_address():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    payload = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None

    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("city") == "City"
    assert data.get("country") == "Country"
    assert data.get("number") == "123"
    assert data.get("postcode") == "12345"
    assert data.get("street") == "Street"
    assert data.get("id") == address_id

# --- id=312  name='User Add And Card' ---
def test_user_add_and_get_card():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567812345678",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("ccv") == "123"
    assert data.get("expires") == "12/25"
    assert data.get("id") == card_id
    assert data.get("longNum") != "1234567812345678"
    assert data.get("longNum").endswith("5678")
    assert "*" in data.get("longNum")

# --- id=313  name='User Customer' ---
def test_user_delete_customer():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

# --- id=314  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)
    if len(socks) > 0:
        sock_id = socks[0].get("id")
        resp = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert resp.json().get("id") == sock_id

# --- id=315  name='Catalogue Sock Not Found' ---
def test_catalogue_get_sock_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid-id-12345"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=316  name='Carts Add And Item' ---
def test_carts_add_and_get_item():
    customer_id = random_string()
    item_id = random_string()
    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("itemId") == item_id
    assert data.get("quantity") == 2
    assert data.get("unitPrice") == 10.5

# --- id=317  name='Carts Update Item' ---
def test_carts_update_item():
    customer_id = random_string()
    item_id = random_string()
    payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)

    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 10.5}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 5

# --- id=318  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = random_string()
    item_id = random_string()
    payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=319  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = random_string()
    item_id = random_string()
    payload = {"itemId": item_id, "quantity": 2, "unitPrice": 10.5}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json() == []

# --- id=320  name='Orders Create Order' ---
def test_orders_create_order():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "CO", "number": "1", "postcode": "123", "street": "S", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    item_id = random_string()
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 2, "unitPrice": 10.5}, timeout=10)

    payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")
    assert order_id is not None

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("id") == order_id
    assert data.get("customer").get("username") == username
    assert data.get("total") == 21.0
    assert len(data.get("items")) == 1
    assert data.get("items")[0].get("itemId") == item_id

# --- id=321  name='Orders Create Order Missing Fields' ---
def test_orders_create_order_missing_fields():
    resp = requests.post(get_url("orders", "/orders"), json={}, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=322  name='Orders Create Order Bad Composite Id' ---
def test_orders_create_order_bad_composite_id():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item1", "quantity": 2, "unitPrice": 10.5}, timeout=10)

    payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid-id",
        "card": "/cards/invalid-id",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=323  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = str(uuid.uuid4())
    payload = {
        "orderId": order_id,
        "amount": 50.0,
        "address": {"city": "C", "country": "CO", "number": "1", "postcode": "123", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "F", "lastName": "L"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0].get("orderId") == order_id
    assert data[0].get("authorised") is True

# --- id=324  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = str(uuid.uuid4())
    payload = {
        "orderId": order_id,
        "amount": 150.0,
        "address": {"city": "C", "country": "CO", "number": "1", "postcode": "123", "street": "S"},
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "F", "lastName": "L"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0].get("orderId") == order_id
    assert data[0].get("authorised") is False

# --- id=325  name='Shipping Ship Order' ---
def test_shipping_ship_order():
    order_id = str(uuid.uuid4())
    payload = {
        "orderId": order_id,
        "itemCount": 2,
        "address": {"city": "C", "country": "CO", "number": "1", "postcode": "123", "street": "S"}
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("orderId") == order_id
    assert "carrier" in data
    assert "trackingNumber" in data

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("orderId") == order_id
    assert "carrier" in data
    assert "trackingNumber" in data
