# Tests generated in iteration 02
# Captured: 2026-06-05T18:50:16
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=666  name='Carts Add And Items' ---
def test_carts_add_and_get_items():
    username = f"user_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    item_id = item["id"]
    unit_price = item["price"]

    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }

    # POST /carts/{customerId}/items
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    resp_data = resp.json()
    assert resp_data["itemId"] == payload["itemId"]
    assert resp_data["quantity"] == payload["quantity"]
    assert resp_data["unitPrice"] == payload["unitPrice"]

    # Follow-up GET /carts/{customerId}/items/{itemId}
    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data["itemId"] == payload["itemId"]
    assert get_data["quantity"] == payload["quantity"]
    assert get_data["unitPrice"] == payload["unitPrice"]

# --- id=667  name='Carts Item And Not Found' ---
def test_carts_delete_item_and_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)

    # DELETE /carts/{customerId}/items/{itemId}
    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # GET /carts/{customerId}/items/{itemId} (Negative)
    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=660  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    # POST /register
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET /customers/{id}
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Login GET /login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=661  name='User Register Duplicate' ---
def test_user_register_duplicate():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    # First register
    resp1 = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    # Second register (Negative)
    resp2 = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=662  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    # Login with wrong password (Negative)
    resp_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpassword"), timeout=10)
    assert resp_login.status_code == 401, f"Expected 401, got {resp_login.status_code}: {resp_login.text}"

# --- id=663  name='User Add Address' ---
def test_user_add_address():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1",
        "street": "Baker St",
        "userID": username
    }

    # POST /addresses
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    # Follow-up GET /addresses/{id}
    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data["city"] == payload["city"]
    assert data["country"] == payload["country"]
    assert data["number"] == payload["number"]
    assert data["postcode"] == payload["postcode"]
    assert data["street"] == payload["street"]

# --- id=664  name='User Add Card' ---
def test_user_add_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }

    # POST /cards
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    # Follow-up GET /cards/{id}
    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    data = resp_get.json()
    assert data["ccv"] == payload["ccv"]
    assert data["expires"] == payload["expires"]
    assert "longNum" in data
    assert data["longNum"] != payload["longNum"]
    assert "3456" in data["longNum"]

# --- id=665  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    # GET /catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    # GET /catalogue/{id}
    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == item_id

# --- id=668  name='Orders Create And' ---
def test_orders_create_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Baker St", "userID": username}, timeout=10)
    address_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 50.0}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    # POST /orders
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_data = resp.json()
    assert "id" in order_data
    order_id = order_data["id"]

    # Follow-up GET /orders/{id}
    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == order_id

# --- id=669  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Baker St", "userID": username}, timeout=10)
    address_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    # Price > 100 to trigger payment decline
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 150.0}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    # POST /orders (Negative)
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=670  name='Payment Authorize' ---
def test_payment_authorize():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Baker St", "userID": username}, timeout=10)
    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 50.0}, timeout=10)

    order_resp = requests.post(get_url("orders", "/orders"), json={
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_resp.json()['id']}",
        "card": f"/cards/{card_resp.json()['id']}",
        "items": f"/carts/{username}/items"
    }, timeout=10)
    order_id = order_resp.json()["id"]

    payment_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Baker St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    # POST /payments
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data["authorised"] is True
    assert auth_data["orderId"] == order_id

    # Follow-up GET /payments/{orderId}
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auth_list = resp_get.json()
    assert len(auth_list) > 0
    assert auth_list[0]["orderId"] == order_id

# --- id=671  name='Shipping Create' ---
def test_shipping_create():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "e@e.com", "firstName": "F", "lastName": "L"}, timeout=10)
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Baker St", "userID": username}, timeout=10)
    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 50.0}, timeout=10)

    order_resp = requests.post(get_url("orders", "/orders"), json={
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_resp.json()['id']}",
        "card": f"/cards/{card_resp.json()['id']}",
        "items": f"/carts/{username}/items"
    }, timeout=10)
    order_id = order_resp.json()["id"]

    shipping_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Baker St"},
        "itemCount": 1,
        "orderId": order_id
    }

    # POST /shipping
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    ship_data = resp.json()
    assert ship_data["orderId"] == order_id
    assert "carrier" in ship_data
    assert "trackingNumber" in ship_data

    # Follow-up GET /shipping/{orderId}
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
