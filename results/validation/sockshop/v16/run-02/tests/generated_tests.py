# Tests generated in iteration 02
# Captured: 2026-06-07T10:49:49
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1389  name='Payment And Shipping Direct' ---
def test_payment_and_shipping_direct():
    username = generate_random_string()
    addr_id, card_id = setup_user_with_address_and_card(username)

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    sock = resp_cat.json()[0]

    item_payload = {
        "itemId": sock["id"],
        "quantity": 1,
        "unitPrice": 10.0
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{sock['id']}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

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
        "address": {
            "city": "Springfield",
            "country": "USA",
            "number": "42",
            "postcode": "12345",
            "street": "Main St"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "Test",
            "lastName": "User"
        },
        "orderId": order_id
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"

    resp_pay_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay_get.status_code == 200, f"Expected 200, got {resp_pay_get.status_code}: {resp_pay_get.text}"

    shipping_payload = {
        "address": {
            "city": "Springfield",
            "country": "USA",
            "number": "42",
            "postcode": "12345",
            "street": "Main St"
        },
        "itemCount": 2,
        "orderId": order_id
    }
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"

    resp_ship_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship_get.status_code == 200, f"Expected 200, got {resp_ship_get.status_code}: {resp_ship_get.text}"

# --- id=1381  name='User Register And Login Negative' ---
def test_user_register_and_login_negative():
    username = generate_random_string()
    password = generate_random_string()
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

    resp_reg_fail = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg_fail.status_code == 409, f"Expected 409, got {resp_reg_fail.status_code}: {resp_reg_fail.text}"

# --- id=1382  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = generate_random_string()
    addr_id, card_id = setup_user_with_address_and_card(username)

    resp_addr_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_del.status_code == 200, f"Expected 200, got {resp_addr_del.status_code}: {resp_addr_del.text}"

    resp_addr_get_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_get_after.status_code == 200, f"Expected 200, got {resp_addr_get_after.status_code}: {resp_addr_get_after.text}"
    addresses_after = resp_addr_get_after.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses_after), "Address was not deleted"

    resp_card_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_del.status_code == 200, f"Expected 200, got {resp_card_del.status_code}: {resp_card_del.text}"

    resp_card_get_after = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_get_after.status_code == 200, f"Expected 200, got {resp_card_get_after.status_code}: {resp_card_get_after.text}"
    cards_after = resp_card_get_after.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards_after), "Card was not deleted"

# --- id=1383  name='Carts Cumulative State' ---
def test_carts_cumulative_state():
    customer_id = generate_random_string()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    socks = resp_cat.json()
    assert len(socks) > 0, "No socks found in catalogue"
    sock = socks[0]
    item_id = sock["id"]

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": sock["price"]
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 1, "Quantity should be 1"

    item_payload["quantity"] = 2
    resp_add_again = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add_again.status_code == 201, f"Expected 201, got {resp_add_again.status_code}: {resp_add_again.text}"

    resp_get_again = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_again.status_code == 200, f"Expected 200, got {resp_get_again.status_code}: {resp_get_again.text}"
    assert resp_get_again.json()["quantity"] == 3, "Quantity should be 3"

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_empty = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_empty.status_code == 200, f"Expected 200, got {resp_get_empty.status_code}: {resp_get_empty.text}"
    assert len(resp_get_empty.json()) == 0, "Cart should be empty"

# --- id=1384  name='Carts Item' ---
def test_carts_patch_item():
    customer_id = generate_random_string()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    sock = resp_cat.json()[0]
    item_id = sock["id"]

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": sock["price"]
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    patch_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": sock["price"]
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_patched = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_patched.status_code == 200, f"Expected 200, got {resp_get_patched.status_code}: {resp_get_patched.text}"
    assert resp_get_patched.json()["quantity"] == 5, "Quantity should be updated to 5"

# --- id=1385  name='Carts Merge Negative' ---
def test_carts_merge_negative():
    customer_id = generate_random_string()
    session_id = generate_random_string()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    sock = resp_cat.json()[0]

    item_payload = {
        "itemId": sock["id"],
        "quantity": 1,
        "unitPrice": sock["price"]
    }
    resp_add = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_session_get = requests.get(get_url("carts", f"/carts/{session_id}/items/{sock['id']}"), timeout=10)
    assert resp_session_get.status_code == 200, f"Expected 200, got {resp_session_get.status_code}: {resp_session_get.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{sock['id']}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_merge_fail = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=nonexistent_{generate_random_string()}"), timeout=10)
    assert resp_merge_fail.status_code == 404, f"Expected 404, got {resp_merge_fail.status_code}: {resp_merge_fail.text}"

# --- id=1386  name='Orders End To End' ---
def test_orders_end_to_end():
    username = generate_random_string()
    addr_id, card_id = setup_user_with_address_and_card(username)

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    sock = resp_cat.json()[0]

    item_payload = {
        "itemId": sock["id"],
        "quantity": 1,
        "unitPrice": 10.0
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{sock['id']}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

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
    assert resp_order_get.json().get("id") == order_id, "Order ID mismatch"

# --- id=1387  name='Orders Payment Failure Negative' ---
def test_orders_payment_failure_negative():
    username = generate_random_string()
    addr_id, card_id = setup_user_with_address_and_card(username)

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    sock = resp_cat.json()[0]

    item_payload = {
        "itemId": sock["id"],
        "quantity": 1,
        "unitPrice": 150.0
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{sock['id']}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1388  name='Catalogue Images And Size' ---
def test_catalogue_images_and_size():
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags = resp_tags.json().get("tags", [])

    if tags:
        tag = tags[0]
        resp_size = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        assert "size" in resp_size.json(), "Size field missing"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    socks = resp_cat.json()

    if socks and socks[0].get("imageUrl"):
        image_url = socks[0]["imageUrl"][0]
        image_name = image_url.split("/")[-1]
        resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

        resp_img_fail = requests.get(get_url("catalogue", "/catalogue/images/nonexistent_image.jpg"), timeout=10)
        assert resp_img_fail.status_code == 404, f"Expected 404, got {resp_img_fail.status_code}: {resp_img_fail.text}"
