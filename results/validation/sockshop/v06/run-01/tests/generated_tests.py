# Tests generated in iteration 01
# Captured: 2026-06-02T18:35:13
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex}"
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

    get_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

    login_resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

# --- id=2  name='User Address Management' ---
def test_user_address_management():
    username = f"user_{uuid.uuid4().hex}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    payload = {
        "city": "Springfield",
        "country": "USA",
        "number": "742",
        "postcode": "12345",
        "street": "Evergreen Terrace",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")

    get_resp = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

# --- id=3  name='User Card Management' ---
def test_user_card_management():
    username = f"user_{uuid.uuid4().hex}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    get_resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

# --- id=4  name='Catalogue Browsing' ---
def test_catalogue_browsing():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if items:
        item_id = items[0].get("id")
        item_resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert item_resp.status_code == 200, f"Expected 200, got {item_resp.status_code}: {item_resp.text}"

    tags_resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"

# --- id=5  name='Carts Add Update Item' ---
def test_carts_add_update_delete_item():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    username = f"user_{uuid.uuid4().hex}"
    reg_resp = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert reg_resp.status_code == 200, f"Expected 200, got {reg_resp.status_code}: {reg_resp.text}"

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    add_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": unit_price}
    update_resp = requests.patch(get_url("carts", f"/carts/{username}/items"), json=update_payload, timeout=10)
    assert update_resp.status_code == 202, f"Expected 202, got {update_resp.status_code}: {update_resp.text}"

    get_item_resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get_item_resp.status_code == 200, f"Expected 200, got {get_item_resp.status_code}: {get_item_resp.text}"

    del_resp = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_del_resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get_del_resp.status_code == 404, f"Expected 404, got {get_del_resp.status_code}: {get_del_resp.text}"

# --- id=6  name='Orders Placement E2e' ---
def test_orders_placement_e2e():
    username = f"user_{uuid.uuid4().hex}"
    user_payload = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    user_resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert user_resp.status_code == 200, f"Expected 200, got {user_resp.status_code}: {user_resp.text}"

    addr_payload = {"city": "C", "country": "US", "number": "1", "postcode": "12345", "street": "S", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json().get("id")

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json().get("id")

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    cart_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    cart_resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)
    assert cart_resp.status_code == 201, f"Expected 201, got {cart_resp.status_code}: {cart_resp.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_id = order_resp.json().get("id")

    get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order.status_code == 200, f"Expected 200, got {get_order.status_code}: {get_order.text}"

    get_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_payment.status_code == 200, f"Expected 200, got {get_payment.status_code}: {get_payment.text}"

    get_shipping = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_shipping.status_code == 200, f"Expected 200, got {get_shipping.status_code}: {get_shipping.text}"
