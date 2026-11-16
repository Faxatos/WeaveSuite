# Tests generated in iteration 10
# Captured: 2026-06-06T23:38:43
# Count:    21
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1174  name='E2e Order Placement' ---
def test_e2e_order_placement():
    username = create_user_and_verify()
    address_id = create_address_and_verify(username)
    card_id = create_card_and_verify(username)

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    item = resp.json()[0]

    add_item_to_cart_and_verify(username, item["id"], 1, item["price"])

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")
    assert order_id is not None

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == order_id

# --- id=1175  name='Carts Cumulative Quantity' ---
def test_carts_cumulative_quantity():
    username = create_user_and_verify()

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]

    add_item_to_cart_and_verify(username, item["id"], 2, item["price"])
    add_item_to_cart_and_verify(username, item["id"], 3, item["price"])

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item['id']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

# --- id=1176  name='Orders Payment Declined 406' ---
def test_orders_payment_declined_406():
    username = create_user_and_verify()
    address_id = create_address_and_verify(username)
    card_id = create_card_and_verify(username)

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]
    quantity = int(101 // item["price"]) + 1

    add_item_to_cart_and_verify(username, item["id"], quantity, item["price"])

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=1177  name='User Already Registered 409' ---
def test_user_already_registered_409():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {"username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "A", "lastName": "B"}

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=1178  name='Carts Merge' ---
def test_carts_merge():
    username = create_user_and_verify()
    session_id = f"session_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]

    add_item_to_cart_and_verify(session_id, item["id"], 1, item["price"])

    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert any(i["itemId"] == item["id"] for i in resp.json())

# --- id=1179  name='Carts Merge Not Found 404' ---
def test_carts_merge_not_found_404():
    username = create_user_and_verify()
    session_id = f"session_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]

    add_item_to_cart_and_verify(session_id, item["id"], 1, item["price"])

    resp = requests.delete(get_url("carts", f"/carts/{session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{session_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1180  name='Carts Item Not Found 404' ---
def test_carts_item_not_found_404():
    username = create_user_and_verify()

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]

    add_item_to_cart_and_verify(username, item["id"], 1, item["price"])

    resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item['id']}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert not any(i["itemId"] == item["id"] for i in resp.json())

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item['id']}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1181  name='Orders Search Not Found 404' ---
def test_orders_search_not_found_404():
    username = create_user_and_verify()

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1182  name='User Login Unauthorized 401' ---
def test_user_login_unauthorized_401():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    payload = {"username": username, "password": password, "email": f"{username}@example.com", "firstName": "A", "lastName": "B"}

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1183  name='User Login Success' ---
def test_user_login_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    payload = {"username": username, "password": password, "email": f"{username}@example.com", "firstName": "A", "lastName": "B"}

    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=1184  name='User Address' ---
def test_user_delete_address():
    username = create_user_and_verify()
    address_id = create_address_and_verify(username)

    resp = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses)

# --- id=1185  name='User Card' ---
def test_user_delete_card():
    username = create_user_and_verify()
    card_id = create_card_and_verify(username)

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

# --- id=1186  name='Carts Item' ---
def test_carts_patch_item():
    username = create_user_and_verify()

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]

    add_item_to_cart_and_verify(username, item["id"], 1, item["price"])

    patch_payload = {"itemId": item["id"], "quantity": 5}
    resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=patch_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item['id']}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

# --- id=1187  name='Carts Cart' ---
def test_carts_delete_cart():
    username = create_user_and_verify()

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp.json()[0]

    add_item_to_cart_and_verify(username, item["id"], 1, item["price"])

    resp = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=1188  name='Catalogue Size' ---
def test_catalogue_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

# --- id=1189  name='Catalogue Tags' ---
def test_catalogue_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=1190  name='User Customers' ---
def test_user_get_customers():
    create_user_and_verify()
    resp = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=1191  name='User All Addresses Empty' ---
def test_user_get_all_addresses_empty():
    resp = requests.get(get_url("user", "/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json().get("_embedded", {}).get("address", [])) == 0

# --- id=1192  name='User All Cards Empty' ---
def test_user_get_all_cards_empty():
    resp = requests.get(get_url("user", "/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json().get("_embedded", {}).get("card", [])) == 0

# --- id=1193  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is True

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) > 0
    assert auths[0]["orderId"] == order_id

# --- id=1194  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 2,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id
