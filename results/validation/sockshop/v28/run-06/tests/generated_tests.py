# Tests generated in iteration 06
# Captured: 2026-06-21T05:24:35
# Count:    23
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1143  name='User Register And Login' ---
def test_user_register_and_login():
    username = create_user_verified()

    resp_login = requests.get(get_url("user", "/login"), auth=(username, "pwd"), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1144  name='User Register Conflict' ---
def test_user_register_conflict():
    username = create_user_verified()

    payload = {"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "F", "lastName": "L"}
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=1145  name='User Add Address And' ---
def test_user_add_address_and_get():
    username = create_user_verified()
    create_address_verified(username)

# --- id=1146  name='User Add Card And' ---
def test_user_add_card_and_get():
    username = create_user_verified()
    create_card_verified(username)

# --- id=1147  name='User Customer' ---
def test_user_delete_customer():
    username = create_user_verified()

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cust_data = resp_get.json()
    assert cust_data.get("username") == username
    assert "email" not in cust_data or not cust_data.get("email")

    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=1148  name='User Addresses Always Empty' ---
def test_user_addresses_always_empty():
    username = create_user_verified()
    create_address_verified(username)

    resp = requests.get(get_url("user", "/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addrs = resp.json().get("_embedded", {}).get("address", [])
    assert len(addrs) == 0

# --- id=1149  name='User Cards Always Empty' ---
def test_user_cards_always_empty():
    username = create_user_verified()
    create_card_verified(username)

    resp = requests.get(get_url("user", "/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert len(cards) == 0

# --- id=1150  name='User Customer Collections' ---
def test_user_customer_collections():
    username = create_user_verified()
    addr_id = create_address_verified(username)
    card_id = create_card_verified(username)

    resp_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addrs = resp_addr.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addrs)

    resp_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    cards = resp_card.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

# --- id=1151  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)

# --- id=1152  name='Catalogue Sock By Id' ---
def test_catalogue_get_sock_by_id():
    item_id = get_real_item_id()

    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("id") == item_id

# --- id=1153  name='Catalogue Sock Not Found' ---
def test_catalogue_get_sock_not_found():
    fake_id = "nonexistent_sock_id"
    resp = requests.get(get_url("catalogue", f"/catalogue/{fake_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1154  name='Catalogue Tags And Size' ---
def test_catalogue_tags_and_size():
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags_data = resp_tags.json()
    tags = tags_data.get("tags", [])

    if tags:
        tag = tags[0]
        resp_size = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        size_data = resp_size.json()
        assert "size" in size_data

# --- id=1155  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    username = create_user_verified()
    item_id = get_real_item_id()
    add_item_to_cart_verified(username, item_id, quantity=2)

# --- id=1156  name='Carts Add Item Increment' ---
def test_carts_add_item_increment():
    username = create_user_verified()
    item_id = get_real_item_id()
    add_item_to_cart_verified(username, item_id, quantity=2)

    payload = {"itemId": item_id, "quantity": 2, "unitPrice": 15.0}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 4

# --- id=1157  name='Carts Item' ---
def test_carts_patch_item():
    username = create_user_verified()
    item_id = get_real_item_id()
    add_item_to_cart_verified(username, item_id, quantity=2)

    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 15.0}
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=patch_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 5

# --- id=1158  name='Carts Item' ---
def test_carts_delete_item():
    username = create_user_verified()
    item_id = get_real_item_id()
    add_item_to_cart_verified(username, item_id, quantity=2)

    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=1159  name='Carts Merge' ---
def test_carts_merge():
    username = create_user_verified()
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    item_id = get_real_item_id()

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 5.0}
    resp_sess = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=payload, timeout=10)
    assert resp_sess.status_code == 201, f"Expected 201, got {resp_sess.status_code}: {resp_sess.text}"

    resp_sess_get = requests.get(get_url("carts", f"/carts/{session_id}/items/{item_id}"), timeout=10)
    assert resp_sess_get.status_code == 200, f"Expected 200, got {resp_sess_get.status_code}: {resp_sess_get.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(item["itemId"] == item_id for item in items)

# --- id=1160  name='Orders Create And' ---
def test_orders_create_and_get():
    order_id, username = create_order_verified()

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    search_data = resp_search.json()
    orders_list = search_data.get("_embedded", {}).get("customerOrders", [])
    assert len(orders_list) >= 1
    assert any(o["id"] == order_id for o in orders_list)

# --- id=1161  name='Orders Create Missing Cart' ---
def test_orders_create_missing_cart():
    username = create_user_verified()
    addr_id = create_address_verified(username)
    card_id = create_card_verified(username)

    resp_del = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"
    assert len(resp_cart_get.json()) == 0

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=1162  name='Orders Create Invalid Uri Format' ---
def test_orders_create_invalid_uri_format():
    username = create_user_verified()
    item_id = get_real_item_id()
    add_item_to_cart_verified(username, item_id)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format_no_colon",
        "card": f"/cards/invalid_format_no_colon",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1163  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id, _ = create_order_verified()
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 2
    assert any(a["authorised"] is True for a in auths)

# --- id=1164  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id, _ = create_order_verified()
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 2
    assert any(a["authorised"] is False for a in auths)

# --- id=1165  name='Shipping And' ---
def test_shipping_post_and_get():
    order_id, _ = create_order_verified()
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    shipment_get = resp_get.json()
    assert shipment_get["orderId"] == order_id
    assert shipment_get["carrier"] == shipment["carrier"]
