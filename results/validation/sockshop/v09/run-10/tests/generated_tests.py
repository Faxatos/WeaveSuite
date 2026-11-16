# Tests generated in iteration 10
# Captured: 2026-06-04T21:26:01
# Count:    4
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=345  name='User Auth And Errors' ---
def test_user_auth_and_errors():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET customer
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Duplicate register
    resp_dup = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

    # Negative: Bad login
    resp_bad = requests.get(get_url("user", "/login"), auth=(username, "wrong"), timeout=10)
    assert resp_bad.status_code == 401, f"Expected 401, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=346  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get real item from catalogue
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add to cart
    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": unit_price}
    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    # Verify add
    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    cart_items = get_resp.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 2

    # Update cart
    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": unit_price}
    patch_resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    # Verify update
    get_item_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_item_resp.status_code == 200, f"Expected 200, got {get_item_resp.status_code}: {get_item_resp.text}"
    assert get_item_resp.json()["quantity"] == 5

    # Delete item
    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    # Verify delete
    get_item_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_item_del.status_code == 404, f"Expected 404, got {get_item_del.status_code}: {get_item_del.text}"

# --- id=347  name='Orders Successful Workflow' ---
def test_orders_successful_workflow():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    # 2. Add Address
    addr_payload = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert addr_resp.status_code == 200, f"Expected 200, got {addr_resp.status_code}: {addr_resp.text}"
    address_id = addr_resp.json()["id"]

    # Verify Address
    addr_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert addr_get.status_code == 200, f"Expected 200, got {addr_get.status_code}: {addr_get.text}"
    addresses = addr_get.json().get("_embedded", {}).get("address", [])
    assert any(a["id"] == address_id and a["city"] == "City" for a in addresses)

    # 3. Add Card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert card_resp.status_code == 200, f"Expected 200, got {card_resp.status_code}: {card_resp.text}"
    card_id = card_resp.json()["id"]

    # Verify Card
    card_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert card_get.status_code == 200, f"Expected 200, got {card_get.status_code}: {card_get.text}"
    cards = card_get.json().get("_embedded", {}).get("card", [])
    assert any(c["id"] == card_id and c["expires"] == "12/25" for c in cards)

    # 4. Add Item to Cart (ensure total <= 100 for successful payment)
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": 1.0}, timeout=10)

    # 5. Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_data = order_resp.json()
    order_id = order_data["id"]
    assert order_data["payment"]["authorised"] is True

    # 6. Verify Order
    order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert order_get.status_code == 200, f"Expected 200, got {order_get.status_code}: {order_get.text}"
    assert order_get.json()["id"] == order_id

    # 7. Verify Payment
    pay_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert pay_get.status_code == 200, f"Expected 200, got {pay_get.status_code}: {pay_get.text}"
    assert len(pay_get.json()) > 0
    assert pay_get.json()[0]["authorised"] is True

    # 8. Verify Shipping
    ship_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert ship_get.status_code == 200, f"Expected 200, got {ship_get.status_code}: {ship_get.text}"
    assert ship_get.json()["orderId"] == order_id

# --- id=348  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    # 2. Add Address & Card
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    address_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    # 3. Add Item to Cart (ensure total > 100 for declined payment)
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    # High quantity to exceed 100.00 limit
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 100, "unitPrice": 10.0}, timeout=10)

    # 4. Place Order - Expect 406 Not Acceptable
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"
