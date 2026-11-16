# Tests generated in iteration 09
# Captured: 2026-06-30T14:12:05
# Count:    21
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=601  name='User Registration And Resources' ---
def test_user_registration_and_resources():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_req = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify customer
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == "John"
    assert customer.get("lastName") == "Doe"

    # Login
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Add Address
    addr_req = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "NW1 6XE",
        "street": "Baker Street",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    assert addr_id is not None

    # Verify Address
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addrs = resp.json().get("_embedded", {}).get("address", [])
    assert len(addrs) > 0
    found_addr = next((a for a in addrs if a.get("id") == addr_id), None)
    assert found_addr is not None
    assert found_addr.get("city") == "London"

    # Add Card
    card_req = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    # Verify Card
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert len(cards) > 0
    found_card = next((c for c in cards if c.get("id") == card_id), None)
    assert found_card is not None
    assert found_card.get("expires") == "12/25"
    assert "3456" in found_card.get("longNum")

# --- id=602  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "A",
        "lastName": "B"
    }
    resp = requests.post(get_url("user", "/register"), json=user_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp2 = requests.post(get_url("user", "/register"), json=user_req, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=603  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    resp = requests.get(get_url("user", "/login"), auth=("nonexistent", "badpassword"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=604  name='User Deletion' ---
def test_user_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"
    }
    requests.post(get_url("user", "/register"), json=user_req, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("username") == username

# --- id=605  name='User Address Card Deletion' ---
def test_user_address_card_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"
    }
    requests.post(get_url("user", "/register"), json=user_req, timeout=10)

    addr_req = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10).json()["id"]

    card_req = {"ccv": "123", "expires": "12/26", "longNum": "1111222233334444", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_req, timeout=10).json()["id"]

    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json().get("_embedded", {}).get("address", [])) == 0

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json().get("_embedded", {}).get("card", [])) == 0

# --- id=606  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if items:
        item = items[0]
        item_id = item["id"]

        resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        fetched_item = resp.json()
        assert fetched_item["id"] == item_id
        assert fetched_item["name"] == item["name"]

    resp = requests.get(get_url("catalogue", "/catalogue/invalid-id-xyz"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=607  name='Catalogue Size And Tags' ---
def test_catalogue_size_and_tags():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=608  name='Catalogue Images' ---
def test_catalogue_images():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if items and items[0].get("imageUrl"):
        img_url = items[0]["imageUrl"][0]
        img_name = img_url.split("/")[-1]

        resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{img_name}"), timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

        resp_img_404 = requests.get(get_url("catalogue", "/catalogue/images/nonexistent_image.jpg"), timeout=10)
        assert resp_img_404.status_code == 404, f"Expected 404, got {resp_img_404.status_code}: {resp_img_404.text}"

# --- id=609  name='Carts Management' ---
def test_carts_management():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = "test-item-123"

    item_req = {"itemId": item_id, "quantity": 2, "unitPrice": 15.50}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

    item_req2 = {"itemId": item_id, "quantity": 3, "unitPrice": 15.50}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_req2, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=610  name='Carts Item' ---
def test_carts_patch_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = "item-patch"

    item_req = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_req, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 1

    item_req_replace = {"itemId": item_id, "quantity": 10, "unitPrice": 5.0}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_req_replace, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 10

# --- id=611  name='Carts Merge' ---
def test_carts_merge():
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    item_req = {"itemId": "item-1", "quantity": 2, "unitPrice": 10.0}
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == "item-1"
    assert items[0]["quantity"] == 2

# --- id=612  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=613  name='Carts Deletion' ---
def test_carts_deletion():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_req = {"itemId": "item-1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_req, timeout=10)

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=614  name='Orders E2e Workflow' ---
def test_orders_e2e_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"
    }
    requests.post(get_url("user", "/register"), json=user_req, timeout=10)

    addr_req = {"city": "Paris", "country": "France", "number": "1", "postcode": "75001", "street": "Rue", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    addr_id = resp.json()["id"]

    card_req = {"ccv": "123", "expires": "12/26", "longNum": "1111222233334444", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    card_id = resp.json()["id"]

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cat_items = resp.json()
    assert len(cat_items) > 0
    cat_item = cat_items[0]

    cart_item_req = {"itemId": cat_item["id"], "quantity": 2, "unitPrice": cat_item["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_req, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]

    assert order["customer"]["username"] == username
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == cat_item["id"]
    assert order["items"][0]["quantity"] == 2
    assert abs(order["total"] - (2 * cat_item["price"])) < 0.01

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cust_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in cust_orders)

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) > 0
    assert payments[-1]["orderId"] == order_id
    assert payments[-1]["authorised"] is True

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

# --- id=615  name='Orders Empty Cart Not Acceptable' ---
def test_orders_empty_cart_not_acceptable():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_req, timeout=10)

    addr_req = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10).json()["id"]

    card_req = {"ccv": "123", "expires": "12/26", "longNum": "1111222233334444", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_req, timeout=10).json()["id"]

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=616  name='Orders Missing Field Not Acceptable' ---
def test_orders_missing_field_not_acceptable():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_req, timeout=10)

    addr_req = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10).json()["id"]

    cart_item_req = {"itemId": "item-1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_req, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=617  name='Orders Bad Uri Format Not Found' ---
def test_orders_bad_uri_format_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_req, timeout=10)

    cart_item_req = {"itemId": "item-1", "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item_req, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format_no_colon",
        "card": f"/cards/invalid_format_no_colon",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=618  name='Orders Search Not Found' ---
def test_orders_search_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_req = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_req, timeout=10)

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=619  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    pay_req = {
        "address": {"city": "A", "country": "B", "number": "1", "postcode": "2", "street": "C"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/26", "longNum": "1234"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0]["orderId"] == order_id

    resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 2

# --- id=620  name='Payment Declined Large Amount' ---
def test_payment_declined_large_amount():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    pay_req = {
        "address": {"city": "A", "country": "B", "number": "1", "postcode": "2", "street": "C"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/26", "longNum": "1234"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is False
    assert auth["orderId"] == order_id

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is False

# --- id=621  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    ship_req = {
        "address": {"city": "A", "country": "B", "number": "1", "postcode": "2", "street": "C"},
        "itemCount": 2,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_shipment = resp.json()
    assert fetched_shipment["orderId"] == order_id
    assert fetched_shipment.get("carrier") == shipment.get("carrier")
