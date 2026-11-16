# Tests generated in iteration 07
# Captured: 2026-06-05T21:40:30
# Count:    19
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=719  name='Orders 406' ---
def test_orders_post_406():
    username, _ = create_user()
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Main St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json()["id"]

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json()["id"]

    cat_item = get_catalogue_item()
    cart_payload = {"itemId": cat_item["id"], "quantity": 1, "unitPrice": 150.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=720  name='Orders Search Customer 404' ---
def test_orders_search_customer_404():
    cat_item = get_catalogue_item()
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={cat_item['id']}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=721  name='Orders 404' ---
def test_orders_get_404():
    username, _ = create_user()
    resp = requests.get(get_url("orders", f"/orders/{username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=722  name='User Login 401' ---
def test_user_login_401():
    username, _ = create_user()
    resp = requests.get(get_url("user", "/login"), auth=(username, username), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=723  name='User Register 409' ---
def test_user_register_409():
    username, payload = create_user()
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=724  name='Carts Item 404' ---
def test_carts_get_item_404():
    username, _ = create_user()
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=725  name='Carts Merge 404' ---
def test_carts_merge_404():
    username, _ = create_user()
    resp = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=726  name='Carts Async Item 404' ---
def test_carts_async_get_item_404():
    username, _ = create_user()
    resp = requests.get(get_url("carts", f"/carts-async/{username}/items/{username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=727  name='Carts Async Merge 404' ---
def test_carts_async_merge_404():
    username, _ = create_user()
    resp = requests.get(get_url("carts", f"/carts-async/{username}/merge?sessionId={username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=709  name='User Register And Login Success' ---
def test_user_register_and_login_success():
    username, payload = create_user()

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    user_data = resp_get.json()
    assert user_data["username"] == payload["username"]
    assert user_data["email"] == payload["email"]
    assert user_data["firstName"] == payload["firstName"]
    assert user_data["lastName"] == payload["lastName"]
    assert "password" not in user_data or user_data["password"] != payload["password"]

    resp_login = requests.get(get_url("user", "/login"), auth=(username, "password123"), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=710  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username, _ = create_user()

    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Main St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_data = resp_addr_get.json()
    assert addr_data["city"] == addr_payload["city"]
    assert addr_data["country"] == addr_payload["country"]
    assert addr_data["number"] == addr_payload["number"]
    assert addr_data["postcode"] == addr_payload["postcode"]
    assert addr_data["street"] == addr_payload["street"]

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data["ccv"] == card_payload["ccv"]
    assert card_data["expires"] == card_payload["expires"]
    assert "longNum" in card_data
    assert card_data["longNum"] != card_payload["longNum"]
    assert card_data["longNum"].endswith("3456")

# --- id=711  name='Carts Lifecycle' ---
def test_carts_lifecycle():
    username, _ = create_user()
    cat_item = get_catalogue_item()
    item_id = cat_item["id"]

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 15.0}
    resp_post = requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)
    assert resp_post.status_code == 201, f"Expected 201, got {resp_post.status_code}: {resp_post.text}"
    post_data = resp_post.json()
    assert post_data["itemId"] == payload["itemId"]
    assert post_data["quantity"] == payload["quantity"]
    assert post_data["unitPrice"] == payload["unitPrice"]

    resp_get1 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    get_data1 = resp_get1.json()
    assert get_data1["itemId"] == payload["itemId"]
    assert get_data1["quantity"] == payload["quantity"]
    assert get_data1["unitPrice"] == payload["unitPrice"]

    payload_patch = {"itemId": item_id, "quantity": 5, "unitPrice": 15.0}
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=payload_patch, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get2 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    get_data2 = resp_get2.json()
    assert get_data2["quantity"] == payload_patch["quantity"]

    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get3 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get3.status_code == 404, f"Expected 404, got {resp_get3.status_code}: {resp_get3.text}"

    resp_del_cart = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    resp_get_cart = requests.get(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp_get_cart.status_code == 200, f"Expected 200, got {resp_get_cart.status_code}: {resp_get_cart.text}"
    assert resp_get_cart.json().get("customerId") == username

# --- id=712  name='Orders Lifecycle' ---
def test_orders_lifecycle():
    username, _ = create_user()
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Main St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp_addr.json()["id"]

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp_card.json()["id"]

    cat_item = get_catalogue_item()
    cart_payload = {"itemId": cat_item["id"], "quantity": 1, "unitPrice": 10.0}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=cart_payload, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data["id"]
    assert order_data["payment"]["authorised"] is True

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data["id"] == order_id
    assert get_data["payment"]["authorised"] is True

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    assert order_id in resp_search.text

# --- id=713  name='Payment Lifecycle' ---
def test_payment_lifecycle():
    order_id = create_full_order()

    payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Main St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }
    resp_post = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp_post.status_code == 200, f"Expected 200, got {resp_post.status_code}: {resp_post.text}"
    post_data = resp_post.json()
    assert post_data["authorised"] is True
    assert post_data["orderId"] == payload["orderId"]

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert isinstance(auths, list)
    assert any(a["orderId"] == order_id and a["authorised"] is True for a in auths)

# --- id=714  name='Shipping Lifecycle' ---
def test_shipping_lifecycle():
    order_id = create_full_order()

    payload = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "EC1", "street": "Main St"},
        "itemCount": 2,
        "orderId": order_id
    }
    resp_post = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp_post.status_code == 200, f"Expected 200, got {resp_post.status_code}: {resp_post.text}"
    post_data = resp_post.json()
    assert post_data["orderId"] == payload["orderId"]

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data["orderId"] == payload["orderId"]

# --- id=715  name='Catalogue Browsing' ---
def test_catalogue_browsing():
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    items = resp_list.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == item_id

    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=716  name='User Resources' ---
def test_user_delete_resources():
    username, _ = create_user()
    addr_payload = {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_get_addrs = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get_addrs.status_code == 200, f"Expected 200, got {resp_get_addrs.status_code}: {resp_get_addrs.text}"
    data = resp_get_addrs.json()
    if "_embedded" in data and "address" in data["_embedded"]:
        assert not any(a.get("id") == addr_id for a in data["_embedded"]["address"])

    resp_del_cust = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_cust.status_code == 200, f"Expected 200, got {resp_del_cust.status_code}: {resp_del_cust.text}"

    # --- Negative Tests ---

# --- id=717  name='Catalogue Image 404' ---
def test_catalogue_get_image_404():
    cat_item = get_catalogue_item()
    resp = requests.get(get_url("catalogue", f"/catalogue/images/{cat_item['id']}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=718  name='Catalogue Item 404' ---
def test_catalogue_get_item_404():
    username, _ = create_user()
    resp = requests.get(get_url("catalogue", f"/catalogue/{username}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
