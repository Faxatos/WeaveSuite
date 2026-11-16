# Tests generated in iteration 03
# Captured: 2026-06-21T11:55:33
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1291  name='User Registration And Conflict' ---
def test_user_registration_and_conflict():
    user_data = generate_user()
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    username = user_data["username"]
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username

    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=1292  name='User Login' ---
def test_user_login():
    user_data = generate_user()
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    resp = requests.get(get_url("user", "/login"), auth=(user_data["username"], user_data["password"]), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_bad = requests.get(get_url("user", "/login"), auth=(user_data["username"], "wrongpass"), timeout=10)
    assert resp_bad.status_code == 401, f"Expected 401, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=1293  name='User Deletion And Non Existent' ---
def test_user_deletion_and_non_existent():
    fake_id = f"fake_{uuid.uuid4().hex[:8]}"
    resp_get_fake = requests.get(get_url("user", f"/customers/{fake_id}"), timeout=10)
    assert resp_get_fake.status_code == 200, f"Expected 200, got {resp_get_fake.status_code}: {resp_get_fake.text}"
    assert resp_get_fake.json().get("username") == fake_id

    resp_del_fake = requests.delete(get_url("user", f"/customers/{fake_id}"), timeout=10)
    assert resp_del_fake.status_code == 200, f"Expected 200, got {resp_del_fake.status_code}: {resp_del_fake.text}"
    assert resp_del_fake.json().get("status") is False

    user_data = generate_user()
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    username = user_data["username"]

    resp_del_real = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_real.status_code == 200, f"Expected 200, got {resp_del_real.status_code}: {resp_del_real.text}"
    assert resp_del_real.json().get("status") is True

# --- id=1294  name='Catalogue Listing Filtering And Not Found' ---
def test_catalogue_listing_filtering_and_not_found():
    tags_resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"
    tags = tags_resp.json().get("tags", [])

    if tags:
        tag = tags[0]
        filter_resp = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
        assert filter_resp.status_code == 200, f"Expected 200, got {filter_resp.status_code}: {filter_resp.text}"
        for item in filter_resp.json():
            assert tag in item.get("tag", [])

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    if items:
        item_id = items[0]["id"]
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json()["id"] == item_id

    resp_404 = requests.get(get_url("catalogue", "/catalogue/invalid-id-999"), timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

# --- id=1295  name='Carts Add Increment Update' ---
def test_carts_add_increment_update_delete():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No catalogue items available")
    item = items[0]
    item_id = item["id"]
    price = item["price"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert len(cart_items) == 1
    assert cart_items[0]["itemId"] == item_id
    assert cart_items[0]["quantity"] == 1

    payload_inc = {"itemId": item_id, "quantity": 2, "unitPrice": price}
    resp_inc = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload_inc, timeout=10)
    assert resp_inc.status_code == 201, f"Expected 201, got {resp_inc.status_code}: {resp_inc.text}"

    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json()[0]["quantity"] == 3

    payload_patch = {"itemId": item_id, "quantity": 5, "unitPrice": price}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=payload_patch, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get3 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get3.status_code == 200, f"Expected 200, got {resp_get3.status_code}: {resp_get3.text}"
    assert resp_get3.json()[0]["quantity"] == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get4 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get4.status_code == 200, f"Expected 200, got {resp_get4.status_code}: {resp_get4.text}"
    assert len(resp_get4.json()) == 0

# --- id=1296  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    user_data = generate_user()
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    username = user_data["username"]

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json()["city"] == "London"

    card_payload = {"longNum": "1234567812345678", "expires": "12/99", "ccv": "123", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    card_data = resp_get_card.json()
    assert card_data["expires"] == "12/99"
    assert card_data["longNum"].endswith("5678")
    assert "*" in card_data["longNum"]

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_cust_addrs = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addrs.status_code == 200, f"Expected 200, got {resp_cust_addrs.status_code}: {resp_cust_addrs.text}"
    embedded_addrs = resp_cust_addrs.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("addressId") == addr_id.split(":")[1] for a in embedded_addrs)

# --- id=1297  name='Orders End To End And Failure' ---
def test_orders_end_to_end_and_failure():
    user_data = generate_user()
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    username = user_data["username"]

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json()["id"]

    card_payload = {"longNum": "1234567812345678", "expires": "12/99", "ccv": "123", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json()["id"]

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order_fail = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order_fail.status_code == 406, f"Expected 406, got {resp_order_fail.status_code}: {resp_order_fail.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 2, "unitPrice": item["price"]}, timeout=10)

    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data["id"]
    assert order_data["customer"]["username"] == username
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["itemId"] == item["id"]

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json()["id"] == order_id

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in embedded_orders)

# --- id=1298  name='Payment And Shipping Direct' ---
def test_payment_and_shipping_direct():
    user_data = generate_user()
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    username = user_data["username"]

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    addr_id = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10).json()["id"]

    card_payload = {"longNum": "1234567812345678", "expires": "12/99", "ccv": "123", "userID": username}
    card_id = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10).json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json()["id"]

    payment_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St"},
        "card": {"longNum": "1234567812345678", "expires": "12/99", "ccv": "123"},
        "customer": {"firstName": "Test", "lastName": "User"}
    }
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json()["authorised"] is True

    resp_get_pay = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_pay.status_code == 200, f"Expected 200, got {resp_get_pay.status_code}: {resp_get_pay.text}"
    auths = resp_get_pay.json()
    assert len(auths) >= 1
    assert auths[-1]["orderId"] == order_id
    assert auths[-1]["authorised"] is True

    shipping_payload = {
        "orderId": order_id,
        "itemCount": 1,
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St"}
    }
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json()["orderId"] == order_id

    resp_get_ship = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_ship.status_code == 200, f"Expected 200, got {resp_get_ship.status_code}: {resp_get_ship.text}"
    assert resp_get_ship.json()["orderId"] == order_id
