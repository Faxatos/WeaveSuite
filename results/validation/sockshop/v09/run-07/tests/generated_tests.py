# Tests generated in iteration 07
# Captured: 2026-06-04T19:50:11
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=318  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
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

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_resp = resp.json()
    assert addr_resp["city"] == address_data["city"]
    assert addr_resp["country"] == address_data["country"]
    assert addr_resp["number"] == address_data["number"]
    assert addr_resp["postcode"] == address_data["postcode"]
    assert addr_resp["street"] == address_data["street"]

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    c_resp = resp.json()
    assert c_resp["ccv"] == card_data["ccv"]
    assert c_resp["expires"] == card_data["expires"]

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    cheap_socks = [s for s in socks if s.get("price", 0) <= 100]
    assert len(cheap_socks) > 0, "No cheap socks found"
    sock = cheap_socks[0]
    sock_id = sock["id"]
    sock_price = sock["price"]

    item_data = {
        "itemId": sock_id,
        "quantity": 1,
        "unitPrice": sock_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    item_resp = resp.json()
    assert item_resp["itemId"] == item_data["itemId"]
    assert item_resp["quantity"] == item_data["quantity"]
    assert item_resp["unitPrice"] == item_data["unitPrice"]

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    item_get = resp.json()
    assert item_get["itemId"] == item_data["itemId"]
    assert item_get["quantity"] == item_data["quantity"]
    assert item_get["unitPrice"] == item_data["unitPrice"]

    order_data = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]
    assert order["payment"]["authorised"] is True

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    order_get = resp.json()
    assert order_get["id"] == order_id
    assert order_get["payment"]["authorised"] is True

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=319  name='Orders Payment Declined' ---
def test_orders_payment_declined():
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

    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0
    sock_id = socks[0]["id"]

    item_data = {
        "itemId": sock_id,
        "quantity": 1,
        "unitPrice": 150.0
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    order_data = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_data, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=320  name='Catalogue Operations' ---
def test_catalogue_operations():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags = resp.json().get("tags", [])

    if tags:
        tag = tags[0]
        resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert "size" in resp.json()

        resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        socks = resp.json()
        if socks:
            sock_id = socks[0]["id"]
            resp = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
            assert resp.json()["id"] == sock_id

            if socks[0].get("imageUrl"):
                image_url = socks[0]["imageUrl"][0]
                image_name = image_url.split("/")[-1]
                resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
                assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=321  name='Carts Operations' ---
def test_carts_operations():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0
    sock_id = socks[0]["id"]

    item_data = {
        "itemId": sock_id,
        "quantity": 2,
        "unitPrice": 10.5
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    item_resp = resp.json()
    assert item_resp["itemId"] == item_data["itemId"]
    assert item_resp["quantity"] == item_data["quantity"]
    assert item_resp["unitPrice"] == item_data["unitPrice"]

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    item_get = resp.json()
    assert item_get["itemId"] == item_data["itemId"]
    assert item_get["quantity"] == item_data["quantity"]
    assert item_get["unitPrice"] == item_data["unitPrice"]

    item_data["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    item_get = resp.json()
    assert item_get["quantity"] == 5

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=322  name='Carts Merge' ---
def test_carts_merge():
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert len(socks) > 0
    sock_id = socks[0]["id"]

    item_data = {
        "itemId": sock_id,
        "quantity": 1,
        "unitPrice": 5.0
    }
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{session_id}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    item_get = resp.json()
    assert item_get["itemId"] == sock_id
    assert item_get["quantity"] == 1

# --- id=323  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "A",
        "lastName": "B"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=324  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    resp = requests.get(get_url("user", "/login"), auth=("nonexistent", "wrong"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=325  name='User Address Card Deletion' ---
def test_user_address_card_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "A",
        "lastName": "B"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "EC1A 1BB",
        "street": "Baker Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses)

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

# --- id=326  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "EC1A 1BB",
            "street": "Baker Street"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "Test",
            "lastName": "User"
        },
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) > 0
    assert auths[0]["authorised"] is True
    assert auths[0]["orderId"] == order_id

# --- id=327  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    shipping_req = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "EC1A 1BB",
            "street": "Baker Street"
        },
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment_get = resp.json()
    assert shipment_get["orderId"] == order_id
    assert shipment_get["carrier"] == shipment["carrier"]
