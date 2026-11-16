# Tests generated in iteration 08
# Captured: 2026-06-06T22:17:58
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1147  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1148  name='User Login Unauthorized Negative' ---
def test_user_login_unauthorized_negative():
    username = f"user_{generate_random_string()}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, "wrong_password"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1149  name='Catalogue Item' ---
def test_catalogue_get_item():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if not items:
        pytest.skip("No items in catalogue")

    item_id = items[0]["id"]
    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id

# --- id=1150  name='Carts Cumulative State And' ---
def test_carts_cumulative_state_and_patch():
    username, _, _, _, _ = setup_user_and_cart()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    if not items:
        pytest.skip("No items in catalogue")
    cat_item = items[0]
    item_id = cat_item["id"]

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": cat_item["price"]
    }

    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    added_item = resp_add.json()
    for k, v in item_payload.items():
        if k in added_item:
            assert added_item[k] == v

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert len(cart_items) == 1
    assert cart_items[0]["quantity"] == 2

    resp_add_again = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_add_again.status_code == 201, f"Expected 201, got {resp_add_again.status_code}: {resp_add_again.text}"

    resp_get_cumulative = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get_cumulative.status_code == 200, f"Expected 200, got {resp_get_cumulative.status_code}: {resp_get_cumulative.text}"
    items_cumulative = resp_get_cumulative.json()
    assert items_cumulative[0]["quantity"] == 4

    patch_payload = {
        "itemId": item_id,
        "quantity": 10
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_patched = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_patched.status_code == 200, f"Expected 200, got {resp_get_patched.status_code}: {resp_get_patched.text}"
    assert resp_get_patched.json()["quantity"] == 10
    assert resp_get_patched.json()["unitPrice"] == cat_item["price"]

# --- id=1151  name='Carts Item' ---
def test_carts_delete_item():
    username, _, _, _, _ = setup_user_and_cart()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    if not items:
        pytest.skip("No items in catalogue")
    cat_item = items[0]
    item_id = cat_item["id"]

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": cat_item["price"]
    }

    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_after = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_after.status_code == 404, f"Expected 404, got {resp_get_after.status_code}: {resp_get_after.text}"

# --- id=1152  name='Orders End To End' ---
def test_orders_end_to_end():
    username, addr_id, card_id, _, _ = setup_user_and_cart()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    if not items:
        pytest.skip("No items in catalogue")
    cat_item = items[0]

    item_payload = {
        "itemId": cat_item["id"],
        "quantity": 1,
        "unitPrice": cat_item["price"]
    }
    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id

    resp_search = requests.get(get_url("orders", "/orders/search/customerId"), params={"custId": username}, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

# --- id=1153  name='Orders Payment Declined Negative' ---
def test_orders_payment_declined_negative():
    username, addr_id, card_id, _, _ = setup_user_and_cart()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    if not items:
        pytest.skip("No items in catalogue")
    cat_item = items[0]

    quantity = int(101 / cat_item["price"]) + 1
    item_payload = {
        "itemId": cat_item["id"],
        "quantity": quantity,
        "unitPrice": cat_item["price"]
    }
    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1154  name='Payment And Shipping Direct' ---
def test_payment_and_shipping_direct():
    username, addr_id, card_id, address_payload, card_payload = setup_user_and_cart()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    if not items:
        pytest.skip("No items in catalogue")
    cat_item = items[0]

    item_payload = {
        "itemId": cat_item["id"],
        "quantity": 1,
        "unitPrice": cat_item["price"]
    }
    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"

    payment_payload = {
        "address": address_payload,
        "amount": cat_item["price"],
        "card": card_payload,
        "customer": {
            "firstName": "Direct",
            "lastName": "Tester"
        },
        "orderId": order_id
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth_result = resp_pay.json()
    assert auth_result.get("authorised") is True
    assert auth_result.get("orderId") == order_id

    resp_pay_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay_get.status_code == 200, f"Expected 200, got {resp_pay_get.status_code}: {resp_pay_get.text}"
    auths = resp_pay_get.json()
    assert len(auths) > 0
    assert auths[-1].get("orderId") == order_id

    shipping_payload = {
        "address": address_payload,
        "itemCount": 1,
        "orderId": order_id
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment.get("orderId") == order_id

    resp_ship_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship_get.status_code == 200, f"Expected 200, got {resp_ship_get.status_code}: {resp_ship_get.text}"
    assert resp_ship_get.json().get("orderId") == order_id
