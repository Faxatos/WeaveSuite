# Tests generated in iteration 05
# Captured: 2026-06-20T04:10:41
# Count:    23
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=713  name='User Registration And Customer Retrieval' ---
def test_user_registration_and_customer_retrieval():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("username") == username

# --- id=714  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=715  name='User Login' ---
def test_user_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {"username": username, "password": password, "email": "a@b.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=716  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == address_id for a in addresses)

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

# --- id=717  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("username") == username
    assert not data.get("firstName")

# --- id=718  name='User Address And Card' ---
def test_user_delete_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")

    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses)

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

# --- id=719  name='Catalogue Item' ---
def test_catalogue_get_item():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0
    sock = socks[0]
    item_id = sock["id"]

    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_sock = resp.json()
    assert fetched_sock["id"] == item_id
    assert fetched_sock["name"] == sock["name"]

# --- id=720  name='Catalogue Item Not Found' ---
def test_catalogue_get_item_not_found():
    item_id = f"invalid_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=721  name='Catalogue Size' ---
def test_catalogue_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "size" in data
    assert isinstance(data["size"], int)

# --- id=722  name='Catalogue Tags' ---
def test_catalogue_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "tags" in data
    assert isinstance(data["tags"], list)

# --- id=723  name='Carts Add And' ---
def test_carts_add_and_delete():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp.json()
    sock = socks[0]
    item_id = sock["id"]

    item_data = {"itemId": item_id, "quantity": 3, "unitPrice": sock["price"]}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    added_item = resp.json()
    assert added_item["itemId"] == item_id
    assert added_item["quantity"] == 3

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 3

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=724  name='Carts Item' ---
def test_carts_patch_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp.json()
    sock = socks[0]
    item_id = sock["id"]

    item_data = {"itemId": item_id, "quantity": 1, "unitPrice": sock["price"]}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)

    patch_data = {"itemId": item_id, "quantity": 5, "unitPrice": sock["price"]}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

# --- id=725  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp.json()
    sock = socks[0]
    item_id = sock["id"]

    item_data = {"itemId": item_id, "quantity": 1, "unitPrice": sock["price"]}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=726  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp.json()
    sock = socks[0]
    item_id = sock["id"]

    item_data = {"itemId": item_id, "quantity": 2, "unitPrice": sock["price"]}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_data, timeout=10)

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) >= 1
    assert any(i["itemId"] == item_id and i["quantity"] >= 2 for i in items)

# --- id=727  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=728  name='Carts Async Add And' ---
def test_carts_async_add_and_delete():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    socks = resp.json()
    sock = socks[0]
    item_id = sock["id"]

    item_data = {"itemId": item_id, "quantity": 2, "unitPrice": sock["price"]}
    resp = requests.post(get_url("carts", f"/carts-async/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts-async/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id

    resp = requests.delete(get_url("carts", f"/carts-async/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=729  name='Orders Place Order E2e' ---
def test_orders_place_order_e2e():
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

    address_data = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1A 1BB", "street": "Test Street", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0, "Catalogue is empty"
    sock = socks[0]

    item_data = {"itemId": sock["id"], "quantity": 2, "unitPrice": sock["price"]}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None, "Order ID is missing"
    assert order["customer"]["username"] == username
    assert order["total"] == sock["price"] * 2

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id
    assert fetched_order["status"] in ["CREATED", "PAID", "SHIPPED"]

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

# --- id=730  name='Orders Missing Items' ---
def test_orders_missing_items():
    username = f"user_{uuid.uuid4().hex[:8]}"

    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    address_id = addr_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=731  name='Orders Invalid Composite Id' ---
def test_orders_invalid_composite_id():
    username = f"user_{uuid.uuid4().hex[:8]}"

    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    sock = resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=732  name='Orders Not Found' ---
def test_orders_not_found():
    order_id = f"invalid_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=733  name='Payment Authorization Direct' ---
def test_payment_authorization_direct():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is True
    assert auth.get("orderId") == order_id

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) >= 1
    assert auths[-1]["orderId"] == order_id
    assert auths[-1]["authorised"] is True

# --- id=734  name='Payment Authorization Declined' ---
def test_payment_authorization_declined():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is False

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) >= 1
    assert auths[-1]["authorised"] is False

# --- id=735  name='Shipping Direct' ---
def test_shipping_direct():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    shipping_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_shipment = resp.json()
    assert fetched_shipment.get("orderId") == order_id
    assert fetched_shipment.get("trackingNumber") == shipment.get("trackingNumber")
