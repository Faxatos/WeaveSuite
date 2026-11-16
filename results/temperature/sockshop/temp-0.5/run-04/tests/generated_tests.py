# Tests generated in iteration 04
# Captured: 2026-07-04T13:43:05
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=429  name='User Registration And Conflict' ---
def test_user_registration_and_conflict():
    username = generate_username()
    payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    url = get_url("user", "/register")
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    get_url_cust = get_url("user", f"/customers/{username}")
    resp_get = requests.get(get_url_cust, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username

    resp_conflict = requests.post(url, json=payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=430  name='Carts Item Management' ---
def test_carts_item_management():
    username = register_user()
    item_id, price = get_catalogue_item()

    cart_url = get_url("carts", f"/carts/{username}/items")
    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": price}
    resp_add = requests.post(cart_url, json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(cart_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert any(i["itemId"] == item_id and i["quantity"] == 2 for i in items)

    item_payload_update = {"itemId": item_id, "quantity": 5, "unitPrice": price}
    resp_update = requests.patch(cart_url, json=item_payload_update, timeout=10)
    assert resp_update.status_code == 202, f"Expected 202, got {resp_update.status_code}: {resp_update.text}"

    item_url = get_url("carts", f"/carts/{username}/items/{item_id}")
    resp_get_item = requests.get(item_url, timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    assert resp_get_item.json()["quantity"] == 5

    resp_delete = requests.delete(item_url, timeout=10)
    assert resp_delete.status_code == 202, f"Expected 202, got {resp_delete.status_code}: {resp_delete.text}"

    resp_get_deleted = requests.get(item_url, timeout=10)
    assert resp_get_deleted.status_code == 404, f"Expected 404, got {resp_get_deleted.status_code}: {resp_get_deleted.text}"

# --- id=431  name='Orders Full Workflow' ---
def test_orders_full_workflow():
    username = register_user()
    address_id = add_address(username)
    card_id = add_card(username)
    item_id, price = get_catalogue_item()

    cart_url = get_url("carts", f"/carts/{username}/items")
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    requests.post(cart_url, json=item_payload, timeout=10)

    order_payload = {
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    order_url = get_url("orders", "/orders")
    resp_order = requests.post(order_url, json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"

    order_data = resp_order.json()
    order_id = order_data["id"]
    assert order_data["customer"]["username"] == username
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["itemId"] == item_id

    get_order_url = get_url("orders", f"/orders/{order_id}")
    resp_get_order = requests.get(get_order_url, timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id

    payment_url = get_url("payment-http", f"/payments/{order_id}")
    resp_payment = requests.get(payment_url, timeout=10)
    assert resp_payment.status_code == 200, f"Expected 200, got {resp_payment.status_code}: {resp_payment.text}"
    payments = resp_payment.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id

    shipping_url = get_url("shipping-http", f"/shipping/{order_id}")
    resp_shipping = requests.get(shipping_url, timeout=10)
    assert resp_shipping.status_code == 200, f"Expected 200, got {resp_shipping.status_code}: {resp_shipping.text}"
    assert resp_shipping.json()["orderId"] == order_id

    search_url = get_url("orders", f"/orders/search/customerId?custId={username}")
    resp_search = requests.get(search_url, timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders)

# --- id=432  name='Orders With Empty Cart' ---
def test_orders_with_empty_cart():
    username = register_user()
    address_id = add_address(username)
    card_id = add_card(username)

    order_payload = {
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    order_url = get_url("orders", "/orders")
    resp_order = requests.post(order_url, json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "message" in resp_order.json()

# --- id=433  name='Orders With Invalid Address Format' ---
def test_orders_with_invalid_address_format():
    username = register_user()
    card_id = add_card(username)
    item_id, price = get_catalogue_item()

    cart_url = get_url("carts", f"/carts/{username}/items")
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    requests.post(cart_url, json=item_payload, timeout=10)

    order_payload = {
        "address": "/addresses/invalid_format",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    order_url = get_url("orders", "/orders")
    resp_order = requests.post(order_url, json=order_payload, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=434  name='Catalogue Endpoints' ---
def test_catalogue_endpoints():
    tags_url = get_url("catalogue", "/tags")
    resp_tags = requests.get(tags_url, timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"

    cat_url = get_url("catalogue", "/catalogue")
    resp_cat = requests.get(cat_url, params={"size": 5}, timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0]["id"]
        item_url = get_url("catalogue", f"/catalogue/{item_id}")
        resp_item = requests.get(item_url, timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json()["id"] == item_id

        image_urls = items[0].get("imageUrl", [])
        if image_urls:
            img_name = image_urls[0].split("/")[-1]
            img_url = get_url("catalogue", f"/catalogue/images/{img_name}")
            resp_img = requests.get(img_url, timeout=10)
            assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

    bad_item_url = get_url("catalogue", "/catalogue/non_existent_item_123")
    resp_bad = requests.get(bad_item_url, timeout=10)
    assert resp_bad.status_code == 404, f"Expected 404, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=435  name='User Address And Card Deletion' ---
def test_user_address_and_card_deletion():
    username = register_user()
    address_id = add_address(username)
    card_id = add_card(username)

    cust_addr_url = get_url("user", f"/customers/{username}/addresses")
    resp_cust_addr = requests.get(cust_addr_url, timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    addresses = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert any(a["id"] == address_id for a in addresses)

    addr_url = get_url("user", f"/addresses/{address_id}")
    resp_del_addr = requests.delete(addr_url, timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_cust_addr_after = requests.get(cust_addr_url, timeout=10)
    addresses_after = resp_cust_addr_after.json().get("_embedded", {}).get("address", [])
    assert not any(a["id"] == address_id for a in addresses_after)

    card_url = get_url("user", f"/cards/{card_id}")
    resp_del_card = requests.delete(card_url, timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    cust_card_url = get_url("user", f"/customers/{username}/cards")
    resp_cust_card_after = requests.get(cust_card_url, timeout=10)
    cards_after = resp_cust_card_after.json().get("_embedded", {}).get("card", [])
    assert not any(c["id"] == card_id for c in cards_after)

# --- id=436  name='User Customer Deletion' ---
def test_user_customer_deletion():
    username = register_user()

    cust_url = get_url("user", f"/customers/{username}")
    resp_del = requests.delete(cust_url, timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_del_again = requests.delete(cust_url, timeout=10)
    assert resp_del_again.status_code == 200, f"Expected 200, got {resp_del_again.status_code}: {resp_del_again.text}"
    assert resp_del_again.json().get("status") is False

    resp_get = requests.get(cust_url, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cust_data = resp_get.json()
    assert cust_data.get("username") == username
    assert not cust_data.get("firstName")

# --- id=437  name='Carts Merge' ---
def test_carts_merge():
    username = register_user()
    session_id = str(uuid.uuid4())
    item_id, price = get_catalogue_item()

    anon_cart_url = get_url("carts", f"/carts/{session_id}/items")
    item_payload = {"itemId": item_id, "quantity": 3, "unitPrice": price}
    requests.post(anon_cart_url, json=item_payload, timeout=10)

    merge_url = get_url("carts", f"/carts/{username}/merge")
    resp_merge = requests.get(merge_url, params={"sessionId": session_id}, timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    user_cart_url = get_url("carts", f"/carts/{username}/items")
    resp_user_cart = requests.get(user_cart_url, timeout=10)
    assert resp_user_cart.status_code == 200, f"Expected 200, got {resp_user_cart.status_code}: {resp_user_cart.text}"
    items = resp_user_cart.json()
    assert any(i["itemId"] == item_id and i["quantity"] == 3 for i in items)

# --- id=438  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    username = register_user()
    session_id = str(uuid.uuid4())

    merge_url = get_url("carts", f"/carts/{username}/merge")
    resp_merge = requests.get(merge_url, params={"sessionId": session_id}, timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=439  name='Payment Http Authorization Repetition' ---
def test_payment_http_authorization_repetition():
    order_id = str(uuid.uuid4())
    payment_payload = {
        "address": {
            "city": "City",
            "country": "Country",
            "number": "12",
            "postcode": "12345",
            "street": "Street"
        },
        "amount": 50.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567812345678"
        },
        "customer": {
            "firstName": "John",
            "lastName": "Doe"
        },
        "orderId": order_id
    }

    pay_url = get_url("payment-http", "/payments")

    resp_pay1 = requests.post(pay_url, json=payment_payload, timeout=10)
    assert resp_pay1.status_code == 200, f"Expected 200, got {resp_pay1.status_code}: {resp_pay1.text}"
    assert resp_pay1.json()["authorised"] is True

    resp_pay2 = requests.post(pay_url, json=payment_payload, timeout=10)
    assert resp_pay2.status_code == 200, f"Expected 200, got {resp_pay2.status_code}: {resp_pay2.text}"
    assert resp_pay2.json()["authorised"] is True

    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    resp_get_pay = requests.get(get_pay_url, timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    auths = resp_get_pay.json()
    assert len(auths) == 2
    assert auths[0]["orderId"] == order_id
    assert auths[1]["orderId"] == order_id

# --- id=440  name='Payment Http Authorization Declined' ---
def test_payment_http_authorization_declined():
    order_id = str(uuid.uuid4())
    payment_payload = {
        "address": {
            "city": "City",
            "country": "Country",
            "number": "12",
            "postcode": "12345",
            "street": "Street"
        },
        "amount": 150.0,
        "card": {
            "ccv": "123",
            "expires": "12/25",
            "longNum": "1234567812345678"
        },
        "customer": {
            "firstName": "John",
            "lastName": "Doe"
        },
        "orderId": order_id
    }

    pay_url = get_url("payment-http", "/payments")
    resp_pay = requests.post(pay_url, json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json()["authorised"] is False

    get_pay_url = get_url("payment-http", f"/payments/{order_id}")
    resp_get_pay = requests.get(get_pay_url, timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    auths = resp_get_pay.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is False

# --- id=441  name='Shipping Http Workflow' ---
def test_shipping_http_workflow():
    order_id = str(uuid.uuid4())
    shipping_payload = {
        "address": {
            "city": "City",
            "country": "Country",
            "number": "12",
            "postcode": "12345",
            "street": "Street"
        },
        "itemCount": 2,
        "orderId": order_id
    }

    ship_url = get_url("shipping-http", "/shipping")
    resp_ship = requests.post(ship_url, json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment["orderId"] == order_id
    assert "trackingNumber" in shipment

    get_ship_url = get_url("shipping-http", f"/shipping/{order_id}")
    resp_get_ship = requests.get(get_ship_url, timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    assert resp_get_ship.json()["orderId"] == order_id
    assert resp_get_ship.json()["trackingNumber"] == shipment["trackingNumber"]

# --- id=442  name='Carts Deletion' ---
def test_carts_deletion():
    username = register_user()
    item_id, price = get_catalogue_item()

    cart_url = get_url("carts", f"/carts/{username}/items")
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    requests.post(cart_url, json=item_payload, timeout=10)

    del_cart_url = get_url("carts", f"/carts/{username}")
    resp_del = requests.delete(del_cart_url, timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_cart = requests.get(cart_url, timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"
    assert len(resp_get_cart.json()) == 0

# --- id=443  name='User Login' ---
def test_user_login():
    username = register_user()

    login_url = get_url("user", "/login")
    resp_login = requests.get(login_url, auth=(username, "password123"), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_bad_login = requests.get(login_url, auth=(username, "wrongpassword"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"
