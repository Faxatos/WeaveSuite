# Tests generated in iteration 16
# Captured: 2026-07-04T20:53:05
# Count:    10
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=567  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
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
    customer = resp_get.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == "Test"
    assert customer.get("lastName") == "User"
    assert customer.get("email") == f"{username}@example.com"
    assert "password" not in customer

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_dup = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

    requests.delete(get_url("user", f"/customers/{username}"), timeout=10)

# --- id=568  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    addr_payload = {
        "street": "123 Main St",
        "number": "42",
        "city": "Springfield",
        "postcode": "12345",
        "country": "USA",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id_composite = resp_addr.json().get("id")

    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id_composite}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    addr_data = resp_get_addr.json()
    assert addr_data.get("street") == "123 Main St"
    assert addr_data.get("city") == "Springfield"
    assert addr_data.get("number") == "42"
    assert addr_data.get("postcode") == "12345"
    assert addr_data.get("country") == "USA"

    card_payload = {
        "longNum": "1234567812345678",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id_composite = resp_card.json().get("id")

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id_composite}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    card_data = resp_get_card.json()
    assert card_data.get("expires") == "12/25"
    assert card_data.get("longNum") == "************5678"

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id_composite}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_list_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_list_addr.status_code == 200, f"Expected 200, got {resp_list_addr.status_code}: {resp_list_addr.text}"
    addrs = resp_list_addr.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id_composite for a in addrs)

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id_composite}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    resp_list_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_list_card.status_code == 200, f"Expected 200, got {resp_list_card.status_code}: {resp_list_card.text}"
    cards = resp_list_card.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id_composite for c in cards)

    requests.delete(get_url("user", f"/customers/{username}"), timeout=10)

# --- id=569  name='Carts Add Update Items' ---
def test_carts_add_update_delete_items():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    sock = items[0]
    item_id = sock["id"]
    price = sock["price"]

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": price
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 2
    assert cart_items[0]["unitPrice"] == price

    item_payload["quantity"] = 5
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_item_404 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item_404.status_code == 404, f"Expected 404, got {resp_get_item_404.status_code}: {resp_get_item_404.text}"

    requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)

# --- id=570  name='Orders Create And Verify' ---
def test_orders_create_and_verify():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "John", "lastName": "Doe"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"street": "123 Main St", "number": "42", "city": "Springfield", "postcode": "12345", "country": "USA", "userID": username}, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    sock = resp_cat.json()[0]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": sock["id"], "quantity": 1, "unitPrice": sock["price"]}, timeout=10)

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

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    order_get = resp_get_order.json()
    assert order_get["id"] == order_id
    assert order_get["customer"]["username"] == username
    assert order_get["address"]["city"] == "Springfield"
    assert order_get["card"]["longNum"] == "************5678"
    assert len(order_get["items"]) == 1
    assert order_get["items"][0]["itemId"] == sock["id"]

    resp_cust_orders = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_cust_orders.status_code == 200, f"Expected 200, got {resp_cust_orders.status_code}: {resp_cust_orders.text}"
    cust_orders = resp_cust_orders.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in cust_orders)

    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    if resp_pay.status_code == 200:
        payments = resp_pay.json()
        if payments:
            assert payments[0]["orderId"] == order_id
            assert payments[0]["authorised"] is True

    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    if resp_ship.status_code == 200:
        shipment = resp_ship.json()
        if "orderId" in shipment:
            assert shipment["orderId"] == order_id

    requests.delete(get_url("user", f"/customers/{username}"), timeout=10)

# --- id=571  name='Orders Empty Cart Error' ---
def test_orders_empty_cart_error():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"street": "123 Main St", "number": "42", "city": "Springfield", "postcode": "12345", "country": "USA", "userID": username}, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "message" in resp_order.json()

    requests.delete(get_url("user", f"/customers/{username}"), timeout=10)

# --- id=572  name='Orders Invalid Uri Format' ---
def test_orders_invalid_uri_format():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com"}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

    requests.delete(get_url("user", f"/customers/{username}"), timeout=10)

# --- id=573  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    payment_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"street": "123 Main St", "number": "42", "city": "Springfield", "postcode": "12345", "country": "USA"},
        "card": {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123"}
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth = resp_pay.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    payments = resp_get.json()
    assert len(payments) == 1
    assert payments[0]["authorised"] is True
    assert payments[0]["orderId"] == order_id

    payment_payload["amount"] = 150.0
    resp_pay_declined = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay_declined.status_code == 200, f"Expected 200, got {resp_pay_declined.status_code}: {resp_pay_declined.text}"
    assert resp_pay_declined.json()["authorised"] is False

    resp_get_2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_2.status_code == 200, f"Expected 200, got {resp_get_2.status_code}: {resp_get_2.text}"
    payments_2 = resp_get_2.json()
    assert len(payments_2) == 2
    assert payments_2[1]["authorised"] is False

# --- id=574  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    shipping_payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"street": "123 Main St", "number": "42", "city": "Springfield", "postcode": "12345", "country": "USA"}
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment
    assert "carrier" in shipment

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    shipment_get = resp_get.json()
    assert shipment_get["orderId"] == order_id
    assert shipment_get["trackingNumber"] == shipment["trackingNumber"]
    assert shipment_get["carrier"] == shipment["carrier"]

# --- id=575  name='Catalogue Endpoints' ---
def test_catalogue_endpoints():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0
    sock = items[0]

    resp_item = requests.get(get_url("catalogue", f"/catalogue/{sock['id']}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == sock["id"]

    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

    resp_404 = requests.get(get_url("catalogue", f"/catalogue/{uuid.uuid4().hex}"), timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

# --- id=576  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    sock = resp_cat.json()[0]

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": sock["id"], "quantity": 2, "unitPrice": sock["price"]}, timeout=10)
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": sock["id"], "quantity": 3, "unitPrice": sock["price"]}, timeout=10)

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert len(cart_items) >= 1
    assert any(item["itemId"] == sock["id"] for item in cart_items)

    resp_merge_404 = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={uuid.uuid4().hex}"), timeout=10)
    assert resp_merge_404.status_code == 404, f"Expected 404, got {resp_merge_404.status_code}: {resp_merge_404.text}"

    requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    requests.delete(get_url("carts", f"/carts/{session_id}"), timeout=10)
