# Tests generated in iteration 04
# Captured: 2026-06-06T19:36:43
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1095  name='Order Payment Failure' ---
def test_order_payment_failure():
    username = random_string()

    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"
    }, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username
    }, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp_cat.json()
    if not items:
        pytest.skip("No items")
    real_item_id = items[0]["id"]
    real_price = items[0].get("price", 50.0)

    quantity = int(101 / real_price) + 1

    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": real_item_id, "quantity": quantity, "unitPrice": real_price
    }, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1096  name='Payment' ---
def test_payment_service():
    order_id = _setup_order()
    if not order_id:
        pytest.skip("Failed to setup order")

    payment_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    pay_data = resp_pay.json()
    assert pay_data.get("authorised") is True
    assert pay_data.get("orderId") == order_id

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert isinstance(auths, list)
    assert any(a.get("orderId") == order_id for a in auths)

    payment_payload["amount"] = 150.0
    resp_pay_fail = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay_fail.status_code == 200, f"Expected 200, got {resp_pay_fail.status_code}: {resp_pay_fail.text}"
    assert resp_pay_fail.json().get("authorised") is False

# --- id=1097  name='Shipping' ---
def test_shipping_service():
    order_id = _setup_order()
    if not order_id:
        pytest.skip("Failed to setup order")

    shipping_payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    ship_data = resp_ship.json()
    assert ship_data.get("orderId") == order_id
    assert "trackingNumber" in ship_data

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id

# --- id=1089  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = random_string()
    password = random_string()
    email = f"{username}@example.com"

    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }

    # POST /register
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET /customers/{username}
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Negative: Register same user -> 409
    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # GET /login (Basic Auth)
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Login wrong password -> 401
    resp_login_fail = requests.get(get_url("user", "/login"), auth=(username, "wrong"), timeout=10)
    assert resp_login_fail.status_code == 401, f"Expected 401, got {resp_login_fail.status_code}: {resp_login_fail.text}"

    # DELETE /customers/{username}
    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    # Follow-up GET /customers
    resp_all = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_all.status_code == 200, f"Expected 200, got {resp_all.status_code}: {resp_all.text}"
    data = resp_all.json()
    if isinstance(data, dict) and "_embedded" in data:
        customers = data["_embedded"].get("customer", [])
        assert not any(c.get("username") == username for c in customers)
    elif isinstance(data, list):
        assert not any(c.get("username") == username for c in data)

# --- id=1090  name='User Addresses And Cards' ---
def test_user_addresses_and_cards():
    username = random_string()
    user_payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@test.com",
        "firstName": "F",
        "lastName": "L"
    }
    requests.post(get_url("user", "/register"), json=user_payload, timeout=10)

    # POST /addresses
    addr_payload = {
        "city": "City",
        "country": "Country",
        "number": "123",
        "postcode": "12345",
        "street": "Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Follow-up GET /addresses/{id}
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_data = resp_addr_get.json()
    assert addr_data.get("city") == addr_payload["city"]
    assert addr_data.get("country") == addr_payload["country"]
    assert addr_data.get("number") == addr_payload["number"]
    assert addr_data.get("postcode") == addr_payload["postcode"]
    assert addr_data.get("street") == addr_payload["street"]

    # Follow-up GET /customers/{username}/addresses
    resp_addr_list = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_list.status_code == 200, f"Expected 200, got {resp_addr_list.status_code}: {resp_addr_list.text}"
    addresses = resp_addr_list.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

    # POST /cards
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Follow-up GET /cards/{id}
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data.get("ccv") == card_payload["ccv"]
    assert card_data.get("expires") == card_payload["expires"]
    assert "longNum" in card_data

    # Follow-up GET /customers/{username}/cards
    resp_card_list = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_list.status_code == 200, f"Expected 200, got {resp_card_list.status_code}: {resp_card_list.text}"
    cards = resp_card_list.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

    # DELETE /addresses/{id}
    resp_addr_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_del.status_code == 200, f"Expected 200, got {resp_addr_del.status_code}: {resp_addr_del.text}"

    # Follow-up GET /customers/{username}/addresses
    resp_addr_list2 = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_list2.status_code == 200
    addresses2 = resp_addr_list2.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses2)

    # DELETE /cards/{id}
    resp_card_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_del.status_code == 200, f"Expected 200, got {resp_card_del.status_code}: {resp_card_del.text}"

    # Follow-up GET /customers/{username}/cards
    resp_card_list2 = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_list2.status_code == 200
    cards2 = resp_card_list2.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards2)

# --- id=1091  name='Catalogue Operations' ---
def test_catalogue_operations():
    # GET /catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert isinstance(items, list)
    if len(items) > 0:
        item_id = items[0]["id"]

        # GET /catalogue/{id}
        resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
        assert resp_item.json()["id"] == item_id

        if items[0].get("imageUrl"):
            image_url = items[0]["imageUrl"][0]
            image_name = image_url.split("/")[-1]
            resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
            assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

    # Negative: GET /catalogue/invalid_id -> 404
    resp_invalid = requests.get(get_url("catalogue", "/catalogue/invalid_id_12345"), timeout=10)
    assert resp_invalid.status_code == 404, f"Expected 404, got {resp_invalid.status_code}: {resp_invalid.text}"

    # GET /catalogue/size
    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

    # GET /tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=1092  name='Carts Cumulative State And' ---
def test_carts_cumulative_state_and_patch():
    customer_id = random_string()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200
    items = resp_cat.json()
    if not items:
        pytest.skip("No items in catalogue")
    item = items[0]
    item_id = item["id"]
    price = item.get("price", 10.0)

    # POST /carts/{customerId}/items (Quantity 1)
    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": price
    }
    resp_add1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add1.status_code == 201, f"Expected 201, got {resp_add1.status_code}: {resp_add1.text}"
    add1_data = resp_add1.json()
    assert add1_data.get("itemId") == item_payload["itemId"]
    assert add1_data.get("quantity") == item_payload["quantity"]
    assert add1_data.get("unitPrice") == item_payload["unitPrice"]

    # Follow-up GET
    resp_get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    assert resp_get1.json().get("quantity") == 1

    # POST /carts/{customerId}/items (Quantity 2) -> Cumulative state
    item_payload["quantity"] = 2
    resp_add2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add2.status_code == 201, f"Expected 201, got {resp_add2.status_code}: {resp_add2.text}"

    # Follow-up GET to check cumulative state (1 + 2 = 3)
    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 3

    # PATCH /carts/{customerId}/items (Set quantity to 5)
    patch_payload = {
        "itemId": item_id,
        "quantity": 5
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Follow-up GET to check patched state
    resp_get3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get3.status_code == 200, f"Expected 200, got {resp_get3.status_code}: {resp_get3.text}"
    assert resp_get3.json().get("quantity") == 5

    # Negative: GET invalid item -> 404
    resp_invalid_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/invalid_item_id"), timeout=10)
    assert resp_invalid_item.status_code == 404, f"Expected 404, got {resp_invalid_item.status_code}: {resp_invalid_item.text}"

    # DELETE item
    resp_del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    # Follow-up GET -> 404
    resp_get4 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get4.status_code == 404, f"Expected 404, got {resp_get4.status_code}: {resp_get4.text}"

    # DELETE cart
    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    # Follow-up GET items -> empty list
    resp_get_empty = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_empty.status_code == 200
    assert resp_get_empty.json() == []

# --- id=1093  name='Carts Merge' ---
def test_carts_merge():
    customer_id = random_string()
    session_id = random_string()

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp_cat.json()
    if not items:
        pytest.skip("No items")
    real_item_id = items[0]["id"]

    item_payload = {
        "itemId": real_item_id,
        "quantity": 1,
        "unitPrice": 10.0
    }
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_items = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_items.status_code == 200, f"Expected 200, got {resp_items.status_code}: {resp_items.text}"
    items_in_cart = resp_items.json()
    assert len(items_in_cart) > 0
    assert items_in_cart[0].get("itemId") == real_item_id

    resp_merge_fail = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=non_existent_session"), timeout=10)
    assert resp_merge_fail.status_code == 404, f"Expected 404, got {resp_merge_fail.status_code}: {resp_merge_fail.text}"

# --- id=1094  name='End To End Order Workflow' ---
def test_end_to_end_order_workflow():
    username = random_string()

    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"
    }, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street", "userID": username
    }, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={
        "ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username
    }, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp_cat.json()
    if not items:
        pytest.skip("No items")
    real_item_id = items[0]["id"]
    real_price = items[0].get("price", 50.0)

    if real_price > 100:
        pytest.skip("Item price > 100, cannot test successful order")

    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": real_item_id, "quantity": 1, "unitPrice": real_price
    }, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")
    assert order_id is not None

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

    resp_invalid_order = requests.get(get_url("orders", "/orders/invalid_order_id"), timeout=10)
    assert resp_invalid_order.status_code == 404, f"Expected 404, got {resp_invalid_order.status_code}: {resp_invalid_order.text}"
