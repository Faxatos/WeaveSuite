# Tests generated in iteration 08
# Captured: 2026-06-05T22:25:47
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=728  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    user_resp_data = resp_get.json()
    if "firstName" in user_resp_data:
        assert user_resp_data["firstName"] == user_data["firstName"]
        assert user_resp_data["lastName"] == user_data["lastName"]
        assert user_resp_data["email"] == user_data["email"]
        assert user_resp_data["username"] == user_data["username"]
        assert "password" not in user_resp_data

    resp_login = requests.get(get_url("user", "/login"), auth=(username, "password123"), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=729  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = f"user_{uuid.uuid4().hex}"
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "John",
        "lastName": "Doe"
    }

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=730  name='Catalogue Browsing And Not Found' ---
def test_catalogue_browsing_and_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Catalogue is empty"

    item_id = items[0]["id"]

    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id

    resp_not_found = requests.get(get_url("catalogue", "/catalogue/invalid_nonexistent_id_999"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=731  name='Carts Management' ---
def test_carts_management():
    username = f"user_{uuid.uuid4().hex}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]
    item_price = cat_resp.json()[0]["price"]

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": item_price}
    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    add_data = resp_add.json()
    assert add_data["itemId"] == cart_item["itemId"]
    assert add_data["quantity"] == cart_item["quantity"]
    assert add_data["unitPrice"] == cart_item["unitPrice"]

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 1

    cart_item_update = {"itemId": item_id, "quantity": 3, "unitPrice": item_price}
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=cart_item_update, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_updated = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get_updated.status_code == 200, f"Expected 200, got {resp_get_updated.status_code}: {resp_get_updated.text}"
    updated_items = resp_get_updated.json()
    updated_item = next((i for i in updated_items if i["itemId"] == item_id), None)
    assert updated_item is not None
    assert updated_item["quantity"] == cart_item_update["quantity"]
    assert updated_item["unitPrice"] == cart_item_update["unitPrice"]

    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_deleted = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_deleted.status_code == 404, f"Expected 404, got {resp_get_deleted.status_code}: {resp_get_deleted.text}"

# --- id=732  name='Orders E2e Placement' ---
def test_orders_e2e_placement():
    username = f"user_{uuid.uuid4().hex}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    addr_data = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json()["id"]

    resp_addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addresses = resp_addr_get.json().get("_embedded", {}).get("address", [])
    created_addr = next((a for a in addresses if a.get("id") == address_id), None)
    assert created_addr is not None, "Address not found in customer addresses"
    assert created_addr["city"] == addr_data["city"]
    assert created_addr["country"] == addr_data["country"]
    assert created_addr["number"] == addr_data["number"]
    assert created_addr["postcode"] == addr_data["postcode"]
    assert created_addr["street"] == addr_data["street"]

    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    cards = resp_card_get.json().get("_embedded", {}).get("card", [])
    created_card = next((c for c in cards if c.get("id") == card_id), None)
    assert created_card is not None, "Card not found in customer cards"
    assert created_card["ccv"] == card_data["ccv"]
    assert created_card["expires"] == card_data["expires"]
    assert "longNum" in created_card

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    valid_items = [item for item in cat_resp.json() if item["price"] <= 100.0]
    assert len(valid_items) > 0, "No items with price <= 100 found in catalogue"
    item = valid_items[0]

    cart_item = {"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json()["id"]

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    order_data = resp_order_get.json()
    assert order_data["id"] == order_id
    assert order_data.get("payment", {}).get("authorised") is True, "Payment should be authorised"

    resp_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    pay_data = resp_pay.json()
    assert len(pay_data) > 0
    assert pay_data[0]["authorised"] is True

    resp_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data["orderId"] == order_id

# --- id=733  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    username = f"user_{uuid.uuid4().hex}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}, timeout=10)
    address_id = resp_addr.json()["id"]

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    cart_item = {"itemId": item_id, "quantity": 1, "unitPrice": 150.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_item, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
