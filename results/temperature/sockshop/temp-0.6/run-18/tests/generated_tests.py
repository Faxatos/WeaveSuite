# Tests generated in iteration 18
# Captured: 2026-07-05T11:33:36
# Count:    12
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=864  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {"username": username, "password": password, "email": f"{username}@example.com", "firstName": "Test", "lastName": "User"}

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("username") == username
    assert resp.json().get("firstName") == "Test"

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=865  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    addr_req = {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")

    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_data = resp.json()
    assert addr_data.get("city") == "City"
    assert addr_data.get("country") == "Country"
    assert addr_data.get("number") == "123"
    assert addr_data.get("postcode") == "12345"

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_data = resp.json()
    assert card_data.get("expires") == "12/25"
    assert card_data.get("longNum", "").endswith("5678")
    assert "*" in card_data.get("longNum", "")

    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    embedded_addrs = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("addressId") in addr_id for a in embedded_addrs)

# --- id=866  name='Catalogue And Cart Management' ---
def test_catalogue_and_cart_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    sock = resp.json()[0]
    sock_id = sock.get("id")

    item_req = {"itemId": sock_id, "quantity": 2, "unitPrice": sock.get("price", 10.0)}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 1

    patch_req = {"itemId": sock_id, "quantity": 5, "unitPrice": sock.get("price", 10.0)}
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=patch_req, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 5

    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{sock_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=867  name='Cart Merge' ---
def test_cart_merge():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    sock = resp.json()[0]
    sock_id = sock.get("id")

    item_req = {"itemId": sock_id, "quantity": 1, "unitPrice": sock.get("price", 10.0)}
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_req, timeout=10)

    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert any(i.get("itemId") == sock_id for i in items)

    bad_session = f"sess_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={bad_session}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=868  name='Order Placement And Fulfillment' ---
def test_order_placement_and_fulfillment():
    username = f"user_{uuid.uuid4().hex[:8]}"
    addr_id, card_id = _setup_user_address_card_cart(username, quantity=1)

    order_req = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    order_data = resp.json()
    assert order_data.get("id") == order_id
    assert order_data.get("customer", {}).get("username") == username
    assert order_data.get("address", {}).get("city") == "City"
    assert "5678" in order_data.get("card", {}).get("longNum", "")
    assert len(order_data.get("items", [])) == 1

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders)

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) > 0
    assert auths[0].get("orderId") == order_id

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id

# --- id=869  name='Order Placement Negative Cases' ---
def test_order_placement_negative_cases():
    username = f"user_{uuid.uuid4().hex[:8]}"
    addr_id, card_id = _setup_user_address_card_cart(username, quantity=0)

    order_req = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    order_req_invalid_uri = {
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req_invalid_uri, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=870  name='Order Placement Payment Declined' ---
def test_order_placement_payment_declined():
    username = f"user_{uuid.uuid4().hex[:8]}"
    addr_id, card_id = _setup_user_address_card_cart(username, quantity=1000)

    order_req = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=871  name='Payment Authorization Repetition' ---
def test_payment_authorization_repetition():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {"city": "City", "country": "Country", "number": "12", "postcode": "123", "street": "St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 2
    assert auths[0].get("orderId") == order_id
    assert auths[1].get("orderId") == order_id

# --- id=872  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    shipping_req = {
        "address": {"city": "City", "country": "Country", "number": "12", "postcode": "123", "street": "St"},
        "itemCount": 2,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id

# --- id=873  name='Customer Deletion' ---
def test_customer_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

# --- id=874  name='Catalogue Tags And Size' ---
def test_catalogue_tags_and_size():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags = resp.json().get("tags", [])

    if tags:
        tag = tags[0]
        resp = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert "size" in resp.json()

# --- id=875  name='Catalogue Images' ---
def test_catalogue_images():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    if socks and socks[0].get("imageUrl"):
        image_url = socks[0]["imageUrl"][0]
        image_name = image_url.split("/")[-1]
        resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/catalogue/images/nonexistent_image_12345.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
