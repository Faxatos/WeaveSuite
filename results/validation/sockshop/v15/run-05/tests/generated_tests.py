# Tests generated in iteration 05
# Captured: 2026-06-07T04:38:17
# Count:    15
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1257  name='Catalogue 404' ---
def test_catalogue_get_404():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200
    resp_reg_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_reg_get.status_code == 200

    resp = requests.get(get_url("catalogue", f"/catalogue/{username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1258  name='Catalogue Image 404' ---
def test_catalogue_image_404():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200
    resp_reg_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_reg_get.status_code == 200

    resp = requests.get(get_url("catalogue", f"/catalogue/images/{username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1259  name='Orders 404' ---
def test_orders_get_404():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200
    resp_reg_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_reg_get.status_code == 200

    resp = requests.get(get_url("orders", f"/orders/{username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1260  name='Orders Search 404' ---
def test_orders_search_404():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp_reg = requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)
    assert resp_reg.status_code == 200
    resp_reg_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_reg_get.status_code == 200

    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1261  name='User Register 409' ---
def test_user_register_409():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}

    resp1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp1.status_code == 200
    resp1_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp1_get.status_code == 200

    resp2 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1262  name='User Login 401' ---
def test_user_login_401():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}

    resp1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp1.status_code == 200
    resp1_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp1_get.status_code == 200

    resp_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpwd"), timeout=10)
    assert resp_login.status_code == 401, f"Expected 401, got {resp_login.status_code}: {resp_login.text}"

# --- id=1263  name='Carts Merge 404' ---
def test_carts_merge_404():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    item_id = get_catalogue_item()

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    resp_add = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201
    resp_add_get = requests.get(get_url("carts", f"/carts/{session_id}/items/{item_id}"), timeout=10)
    assert resp_add_get.status_code == 200

    resp_del = requests.delete(get_url("carts", f"/carts/{session_id}"), timeout=10)
    assert resp_del.status_code == 202

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=1249  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
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

# --- id=1250  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username, addr_id, card_id = setup_user_with_address_and_card()

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_addr_list = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_list.status_code == 200, f"Expected 200, got {resp_addr_list.status_code}: {resp_addr_list.text}"
    addresses = resp_addr_list.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses)

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    resp_card_list = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_card_list.status_code == 200, f"Expected 200, got {resp_card_list.status_code}: {resp_card_list.text}"
    cards = resp_card_list.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

# --- id=1251  name='User' ---
def test_user_delete():
    username, _, _ = setup_user_with_address_and_card()

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_list = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    data = resp_list.json()
    customers = data.get("_embedded", {}).get("customer", []) if isinstance(data, dict) and "_embedded" in data else data
    if isinstance(customers, list):
        assert not any(c.get("username") == username for c in customers)

# --- id=1252  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    items = resp_list.json()
    if not items:
        pytest.skip("No items in catalogue")

    item_id = items[0].get("id")
    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("id") == item_id

    image_urls = items[0].get("imageUrl", [])
    if image_urls:
        image_name = image_urls[0].split("/")[-1]
        resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"

    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"

# --- id=1253  name='Carts Add Increment And' ---
def test_carts_add_increment_and_delete():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = get_catalogue_item()

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.0}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 1

    resp_inc = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_inc.status_code == 201, f"Expected 201, got {resp_inc.status_code}: {resp_inc.text}"

    resp_get_inc = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_inc.status_code == 200, f"Expected 200, got {resp_get_inc.status_code}: {resp_get_inc.text}"
    assert resp_get_inc.json().get("quantity") == 2

    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": 10.0}
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_patch = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_patch.status_code == 200, f"Expected 200, got {resp_get_patch.status_code}: {resp_get_patch.text}"
    assert resp_get_patch.json().get("quantity") == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    resp_cart_items = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_cart_items.status_code == 200, f"Expected 200, got {resp_cart_items.status_code}: {resp_cart_items.text}"
    assert len(resp_cart_items.json()) == 0

# --- id=1254  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    item_id = get_catalogue_item()

    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": 15.0}
    resp_sess_add = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)
    assert resp_sess_add.status_code == 201, f"Expected 201, got {resp_sess_add.status_code}: {resp_sess_add.text}"

    resp_sess_get = requests.get(get_url("carts", f"/carts/{session_id}/items/{item_id}"), timeout=10)
    assert resp_sess_get.status_code == 200, f"Expected 200, got {resp_sess_get.status_code}: {resp_sess_get.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 2

# --- id=1255  name='Orders Create And Verify Downstream' ---
def test_orders_create_and_verify_downstream():
    username, addr_id, card_id = setup_user_with_address_and_card()
    item_id = get_catalogue_item()

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 50.0}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
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

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"

    payment_payload = {
        "address": {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"},
        "amount": 10.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }
    resp_pay_post = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp_pay_post.status_code == 200, f"Expected 200, got {resp_pay_post.status_code}: {resp_pay_post.text}"

    resp_pay_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_pay_get.status_code == 200, f"Expected 200, got {resp_pay_get.status_code}: {resp_pay_get.text}"

    shipping_payload = {
        "address": {"city": "City", "country": "Country", "number": "123", "postcode": "12345", "street": "Street"},
        "itemCount": 2,
        "orderId": order_id
    }
    resp_ship_post = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp_ship_post.status_code == 200, f"Expected 200, got {resp_ship_post.status_code}: {resp_ship_post.text}"

    resp_ship_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_ship_get.status_code == 200, f"Expected 200, got {resp_ship_get.status_code}: {resp_ship_get.text}"

# --- id=1256  name='Orders Payment Declined 406' ---
def test_orders_payment_declined_406():
    username, addr_id, card_id = setup_user_with_address_and_card()
    item_id = get_catalogue_item()

    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": 150.0}
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"
    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
