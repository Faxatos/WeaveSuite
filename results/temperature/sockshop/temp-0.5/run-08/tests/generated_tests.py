# Tests generated in iteration 08
# Captured: 2026-07-04T16:18:41
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=483  name='Catalogue Workflow' ---
def test_catalogue_workflow():
    catalogue_url = get_url("catalogue", "/catalogue")
    resp = requests.get(catalogue_url, params={"size": 5}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    assert isinstance(socks, list)

    if socks:
        sock_id = socks[0]["id"]
        sock_url = get_url("catalogue", f"/catalogue/{sock_id}")
        resp_sock = requests.get(sock_url, timeout=10)
        assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
        assert resp_sock.json()["id"] == sock_id

        # Negative test: invalid sock id
        resp_bad_sock = requests.get(get_url("catalogue", "/catalogue/invalid_id"), timeout=10)
        assert resp_bad_sock.status_code == 404, f"Expected 404, got {resp_bad_sock.status_code}: {resp_bad_sock.text}"

        if "imageUrl" in socks[0] and socks[0]["imageUrl"]:
            image_path = socks[0]["imageUrl"][0]
            image_name = image_path.split("/")[-1]
            image_url = get_url("catalogue", f"/catalogue/images/{image_name}")
            resp_img = requests.get(image_url, timeout=10)
            assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

            # Negative test: invalid image
            resp_bad_img = requests.get(get_url("catalogue", "/catalogue/images/invalid_image.jpg"), timeout=10)
            assert resp_bad_img.status_code == 404, f"Expected 404, got {resp_bad_img.status_code}: {resp_bad_img.text}"

    tags_url = get_url("catalogue", "/tags")
    resp_tags = requests.get(tags_url, timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()
    tags = resp_tags.json()["tags"]

    if tags:
        tag = tags[0]
        size_url = get_url("catalogue", "/catalogue/size")
        resp_size = requests.get(size_url, params={"tags": tag}, timeout=10)
        assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
        assert "size" in resp_size.json()

# --- id=484  name='User Workflow' ---
def test_user_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    # Register
    register_url = get_url("user", "/register")
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(register_url, json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Registration by Login
    login_url = get_url("user", "/login")
    resp_login = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Register conflict
    resp_conflict = requests.post(register_url, json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Add Address
    address_url = get_url("user", "/addresses")
    address_data = {
        "street": "123 Main St",
        "number": "42",
        "city": "Testville",
        "postcode": "12345",
        "country": "Testland",
        "userID": username
    }
    resp_addr = requests.post(address_url, json=address_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    # Verify Address
    addr_get_url = get_url("user", f"/addresses/{addr_id}")
    resp_get_addr = requests.get(addr_get_url, timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json()["id"] == addr_id

    # Add Card
    card_url = get_url("user", "/cards")
    card_data = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(card_url, json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    # Verify Card
    card_get_url = get_url("user", f"/cards/{card_id}")
    resp_get_card = requests.get(card_get_url, timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert resp_get_card.json()["id"] == card_id

    # Delete Address
    resp_del_addr = requests.delete(addr_get_url, timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Verify Address Deletion
    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    addresses = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses)

    # Delete Card
    resp_del_card = requests.delete(card_get_url, timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    # Verify Card Deletion
    resp_cust_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_card.status_code == 200, f"Expected 200, got {resp_cust_card.status_code}: {resp_cust_card.text}"
    cards = resp_cust_card.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

    # Delete Customer
    del_cust_url = get_url("user", f"/customers/{username}")
    resp_del = requests.delete(del_cust_url, timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    # Verify deletion by login failure
    resp_login_after = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp_login_after.status_code == 401, f"Expected 401, got {resp_login_after.status_code}: {resp_login_after.text}"

# --- id=485  name='Carts Workflow' ---
def test_carts_workflow():
    customer_id = f"cartuser_{uuid.uuid4().hex[:8]}"

    catalogue_url = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(catalogue_url, params={"size": 1}, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    socks = resp_cat.json()
    if not socks:
        pytest.skip("Catalogue is empty, cannot proceed with carts test")
    item_id = socks[0]["id"]

    items_url = get_url("carts", f"/carts/{customer_id}/items")
    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 10.5
    }

    # Add item
    resp_add = requests.post(items_url, json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verify add
    resp_get = requests.get(items_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i["itemId"] == item_id and i["quantity"] == 2 for i in items)

    # Update item (PATCH)
    item_data_update = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 10.5
    }
    resp_patch = requests.patch(items_url, json=item_data_update, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify update
    resp_get_update = requests.get(items_url, timeout=10)
    assert resp_get_update.status_code == 200, f"Expected 200, got {resp_get_update.status_code}: {resp_get_update.text}"
    items_update = resp_get_update.json()
    assert any(i["itemId"] == item_id and i["quantity"] == 5 for i in items_update)

    # Merge cart
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    resp_add_session = requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.5}, timeout=10)
    assert resp_add_session.status_code == 201, f"Expected 201, got {resp_add_session.status_code}: {resp_add_session.text}"

    merge_url = get_url("carts", f"/carts/{customer_id}/merge")
    resp_merge = requests.get(merge_url, params={"sessionId": session_id}, timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get_merged = requests.get(items_url, timeout=10)
    assert resp_get_merged.status_code == 200, f"Expected 200, got {resp_get_merged.status_code}: {resp_get_merged.text}"
    items_merged = resp_get_merged.json()
    assert any(i["itemId"] == item_id for i in items_merged)

    # Negative merge
    resp_merge_fail = requests.get(merge_url, params={"sessionId": "nonexistent"}, timeout=10)
    assert resp_merge_fail.status_code == 404, f"Expected 404, got {resp_merge_fail.status_code}: {resp_merge_fail.text}"

    # Delete item
    del_item_url = get_url("carts", f"/carts/{customer_id}/items/{item_id}")
    resp_del = requests.delete(del_item_url, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify item deleted
    resp_get_after = requests.get(items_url, timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    items_after = resp_get_after.json()
    assert not any(i["itemId"] == item_id for i in items_after)

    # Delete cart
    cart_url = get_url("carts", f"/carts/{customer_id}")
    resp_del_cart = requests.delete(cart_url, timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    # Verify cart deletion
    resp_get_cart_items = requests.get(items_url, timeout=10)
    assert resp_get_cart_items.status_code == 200, f"Expected 200, got {resp_get_cart_items.status_code}: {resp_get_cart_items.text}"
    assert len(resp_get_cart_items.json()) == 0

# --- id=486  name='Orders Workflow' ---
def test_orders_workflow():
    order_id, username, addr_id, card_id = setup_order()

    # Search Order by Customer
    resp_search = requests.get(get_url("orders", "/orders/search/customerId"), params={"custId": username}, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

    # Negative Test: Create order with missing items
    orders_url = get_url("orders", "/orders")
    bad_order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}"
    }
    resp_bad = requests.post(orders_url, json=bad_order_req, timeout=10)
    assert resp_bad.status_code == 406, f"Expected 406, got {resp_bad.status_code}: {resp_bad.text}"

    # Negative Test: Create order with invalid address format
    invalid_addr_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_inv = requests.post(orders_url, json=invalid_addr_req, timeout=10)
    assert resp_inv.status_code == 404, f"Expected 404, got {resp_inv.status_code}: {resp_inv.text}"

# --- id=487  name='Payments Workflow' ---
def test_payments_workflow():
    order_id, _, _, _ = setup_order()
    payment_url = get_url("payment-http", "/payments")

    payment_req = {
        "address": {
            "city": "Test",
            "country": "Test",
            "number": "1",
            "postcode": "123",
            "street": "Test"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567890123456"
        },
        "customer": {
            "firstName": "John",
            "lastName": "Doe"
        },
        "orderId": order_id
    }

    resp_pay = requests.post(payment_url, json=payment_req, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth = resp_pay.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    # Verify payment
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 1
    assert any(a["orderId"] == order_id for a in auths)

    # Negative Test: Amount > 100 should be declined
    payment_req_declined = payment_req.copy()
    payment_req_declined["amount"] = 150.0
    resp_declined = requests.post(payment_url, json=payment_req_declined, timeout=10)
    assert resp_declined.status_code == 200, f"Expected 200, got {resp_declined.status_code}: {resp_declined.text}"
    assert resp_declined.json()["authorised"] is False

    # Verify declined payment is recorded
    resp_get_after = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    auths_after = resp_get_after.json()
    assert any(a["orderId"] == order_id and a["authorised"] is False for a in auths_after)

# --- id=488  name='Shipping Workflow' ---
def test_shipping_workflow():
    order_id, _, _, _ = setup_order()
    shipping_url = get_url("shipping-http", "/shipping")

    shipping_req = {
        "address": {
            "city": "Test",
            "country": "Test",
            "number": "1",
            "postcode": "123",
            "street": "Test"
        },
        "itemCount": 2,
        "orderId": order_id
    }

    resp_ship = requests.post(shipping_url, json=shipping_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment

    # Verify shipment
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
