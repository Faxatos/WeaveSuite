# Tests generated in iteration 07
# Captured: 2026-06-21T14:03:46
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1323  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify customer exists
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    customer = resp_get.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == "Test"
    assert customer.get("lastName") == "User"
    assert "password" not in customer

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Register again
    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Negative: Login with wrong password
    resp_bad_login = requests.get(get_url("user", "/login"), auth=(username, "wrong"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

    # Delete customer
    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    # Verify deletion
    resp_del_again = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_again.status_code == 200, f"Expected 200, got {resp_del_again.status_code}: {resp_del_again.text}"
    assert resp_del_again.json().get("status") is False

# --- id=1324  name='User Address And Card' ---
def test_user_address_and_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    # Add Address
    addr_payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Verify Address
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addr_data = resp_get_addr.json()
    assert addr_data.get("city") == "London"
    assert addr_data.get("id") == addr_id

    # Verify Address in collection
    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    embedded_addr = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in embedded_addr)

    # Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Verify Card
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    card_data = resp_get_card.json()
    assert card_data.get("id") == card_id
    assert card_data.get("longNum") == "************3456"

    # Verify Card in collection
    resp_cust_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_card.status_code == 200, f"Expected 200, got {resp_cust_card.status_code}: {resp_cust_card.text}"
    embedded_card = resp_cust_card.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in embedded_card)

    # Delete Address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Delete Card
    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

# --- id=1325  name='Catalogue Operations' ---
def test_catalogue_operations():
    # Get catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)
    if not socks:
        pytest.skip("No socks in catalogue")

    sock = socks[0]
    sock_id = sock["id"]

    # Get specific sock
    resp_sock = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
    assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
    assert resp_sock.json()["id"] == sock_id

    # Get tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags_data = resp_tags.json()
    assert "tags" in tags_data

    if tags_data["tags"]:
        tag = tags_data["tags"][0]
        resp_size = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        assert "size" in resp_size.json()

    # Negative: Invalid sock
    resp_invalid = requests.get(get_url("catalogue", "/catalogue/invalid_sock_id_123"), timeout=10)
    assert resp_invalid.status_code == 404, f"Expected 404, got {resp_invalid.status_code}: {resp_invalid.text}"

# --- id=1326  name='Carts Operations' ---
def test_carts_operations():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Add item
    item_payload = {
        "itemId": "03fef6ac-1896-4ce8-bd69-b798f85c6e0b",
        "quantity": 2,
        "unitPrice": 10.5
    }

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    if cat_resp.status_code == 200 and cat_resp.json():
        item_payload["itemId"] = cat_resp.json()[0]["id"]
        item_payload["unitPrice"] = cat_resp.json()[0]["price"]

    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Get items
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) >= 1
    assert any(i["itemId"] == item_payload["itemId"] for i in items)

    # Update item
    item_payload["quantity"] = 5
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Get specific item
    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_payload['itemId']}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_payload['itemId']}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify deletion
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_payload['itemId']}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

    # Delete cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=1327  name='Orders End To End' ---
def test_orders_end_to_end():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json()["id"]

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    if not cat_resp.json():
        pytest.skip("No catalogue items")
    sock = cat_resp.json()[0]

    item_payload = {"itemId": sock["id"], "quantity": 2, "unitPrice": sock["price"]}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order["id"]
    assert order["customer"]["username"] == username
    assert order["address"]["city"] == "London"
    assert order["card"]["longNum"] == "************3456"
    assert len(order["items"]) >= 1

    # Verify order
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id

    # Search orders
    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

# --- id=1328  name='Orders Negative' ---
def test_orders_negative():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    # Missing fields
    order_payload = {
        "customer": f"/customers/{username}"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

    # Invalid composite ID format
    order_payload_invalid = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/invalid_format",
        "items": f"/carts/{username}/items"
    }
    resp_invalid = requests.post(get_url("orders", "/orders"), json=order_payload_invalid, timeout=10)
    assert resp_invalid.status_code == 404, f"Expected 404, got {resp_invalid.status_code}: {resp_invalid.text}"

# --- id=1329  name='Payment Operations' ---
def test_payment_operations():
    order_id = f"order_{uuid.uuid4().hex[:8]}"

    payment_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    # Authorize payment
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth = resp_pay.json()
    assert auth["orderId"] == order_id
    assert auth["authorised"] is True

    # Get authorizations
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["orderId"] == order_id

    # Repeat payment
    resp_pay2 = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay2.status_code == 200, f"Expected 200, got {resp_pay2.status_code}: {resp_pay2.text}"

    # Get authorizations again
    resp_get2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    auths2 = resp_get2.json()
    assert len(auths2) == 2

# --- id=1330  name='Shipping Operations' ---
def test_shipping_operations():
    order_id = f"order_{uuid.uuid4().hex[:8]}"

    shipping_payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St"},
        "itemCount": 3,
        "orderId": order_id
    }

    # Ship request
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment

    # Get shipment
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    shipment_get = resp_get.json()
    assert shipment_get["orderId"] == order_id
    assert shipment_get["trackingNumber"] == shipment["trackingNumber"]
