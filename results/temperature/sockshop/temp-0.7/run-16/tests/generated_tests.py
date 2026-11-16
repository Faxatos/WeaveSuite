# Tests generated in iteration 18
# Captured: 2026-06-30T19:40:05
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=711  name='User Customer Deletion' ---
def test_user_customer_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=712  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == item_id

    resp_404 = requests.get(get_url("catalogue", "/catalogue/invalid_id"), timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

# --- id=713  name='Catalogue Tags' ---
def test_catalogue_get_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    assert "tags" in tags_data
    tags = tags_data["tags"]
    if tags:
        tag = tags[0]
        resp_size = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        assert "size" in resp_size.json()

# --- id=714  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert items, "Catalogue is empty"
    item = items[0]

    item_data = {
        "itemId": item["id"],
        "quantity": 2,
        "unitPrice": item["price"]
    }

    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert any(i["itemId"] == item_data["itemId"] for i in cart_items)

    item_data["quantity"] = 5
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_data['itemId']}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()["quantity"] == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_data['itemId']}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_data['itemId']}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=715  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    assert len(items) >= 1
    item1 = items[0]

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item1["id"], "quantity": 1, "unitPrice": item1["price"]}, timeout=10)

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    merged_items = resp_get.json()
    item_ids = [i["itemId"] for i in merged_items]
    assert item1["id"] in item_ids

# --- id=716  name='Orders Create And' ---
def test_orders_create_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_data = {"street": "123 Main St", "number": "42", "country": "USA", "city": "Anytown", "postcode": "12345", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_data = {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order = order_resp.json()
    order_id = order["id"]

    get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order.status_code == 200, f"Expected 200, got {get_order.status_code}: {get_order.text}"
    assert get_order.json()["id"] == order_id
    assert get_order.json()["customer"]["username"] == username

    search_order = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_order.status_code == 200, f"Expected 200, got {search_order.status_code}: {search_order.text}"
    embedded = search_order.json().get("_embedded", {})
    assert any(o["id"] == order_id for o in embedded.get("customerOrders", []))

# --- id=717  name='Orders Create Empty Cart' ---
def test_orders_create_empty_cart():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)
    addr_resp = requests.post(get_url("user", "/addresses"), json={"street": "A", "number": "1", "country": "US", "city": "B", "postcode": "C", "userID": username}, timeout=10)
    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_resp.json()['id']}",
        "card": f"/cards/{card_resp.json()['id']}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"
    assert "message" in order_resp.json()

# --- id=718  name='Orders Create Invalid Composite Id' ---
def test_orders_create_invalid_composite_id():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_no_colon",
        "card": f"/cards/invalid_no_colon",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=708  name='User Register And Login' ---
def test_user_register_and_login():
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

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data["username"] == username
    assert get_data["email"] == user_data["email"]
    assert get_data["firstName"] == user_data["firstName"]
    assert get_data["lastName"] == user_data["lastName"]
    assert "password" not in get_data, "Password should not be returned"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=709  name='User Add Address And' ---
def test_user_add_address_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_data = {
        "street": "123 Main St",
        "number": "42",
        "country": "USA",
        "city": "Anytown",
        "postcode": "12345",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json()["id"]

    resp_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data["street"] == addr_data["street"]
    assert get_data["city"] == addr_data["city"]

    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    embedded = resp_cust_addr.json().get("_embedded", {})
    assert any(a.get("id") == addr_id for a in embedded.get("address", []))

    resp_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_cust_addr_post_del = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr_post_del.status_code == 200, f"Expected 200, got {resp_cust_addr_post_del.status_code}: {resp_cust_addr_post_del.text}"
    embedded_post_del = resp_cust_addr_post_del.json().get("_embedded", {})
    assert not any(a.get("id") == addr_id for a in embedded_post_del.get("address", []))

# --- id=710  name='User Add Card And' ---
def test_user_add_card_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    card_data = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data["longNum"].endswith("3456")
    assert get_data["expires"] == card_data["expires"]

    resp_cust_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_cards.status_code == 200, f"Expected 200, got {resp_cust_cards.status_code}: {resp_cust_cards.text}"
    embedded = resp_cust_cards.json().get("_embedded", {})
    assert any(c.get("id") == card_id for c in embedded.get("card", []))

    resp_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_cust_cards_post_del = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_cards_post_del.status_code == 200, f"Expected 200, got {resp_cust_cards_post_del.status_code}: {resp_cust_cards_post_del.text}"
    embedded_post_del = resp_cust_cards_post_del.json().get("_embedded", {})
    assert not any(c.get("id") == card_id for c in embedded_post_del.get("card", []))

# --- id=719  name='Payment Authorize' ---
def test_payment_authorize():
    order_id = str(uuid.uuid4())
    pay_req = {
        "orderId": order_id,
        "amount": 50.0,
        "address": {"street": "123 Main St", "number": "42", "country": "USA", "city": "Anytown", "postcode": "12345"},
        "card": {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123"},
        "customer": {"firstName": "John", "lastName": "Doe"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["orderId"] == order_id
    assert auth["authorised"] is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["orderId"] == order_id

    requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    resp_get2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert len(resp_get2.json()) == 2

# --- id=720  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = str(uuid.uuid4())
    pay_req = {
        "orderId": order_id,
        "amount": 150.0,
        "address": {"street": "123 Main St", "number": "42", "country": "USA", "city": "Anytown", "postcode": "12345"},
        "card": {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123"},
        "customer": {"firstName": "John", "lastName": "Doe"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["orderId"] == order_id
    assert auth["authorised"] is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is False

# --- id=721  name='Shipping Ship And' ---
def test_shipping_ship_and_get():
    order_id = str(uuid.uuid4())
    ship_req = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"street": "123 Main St", "number": "42", "country": "USA", "city": "Anytown", "postcode": "12345"}
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
