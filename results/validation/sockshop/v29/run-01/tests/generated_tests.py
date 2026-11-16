# Tests generated in iteration 01
# Captured: 2026-06-21T09:56:34
# Count:    31
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1232  name='Catalogue All And Filter' ---
def test_catalogue_get_all_and_filter():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if items:
        item = items[0]
        assert "id" in item
        assert "name" in item

        if "tag" in item and item["tag"]:
            tag = item["tag"][0]
            resp_filtered = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
            assert resp_filtered.status_code == 200, f"Expected 200, got {resp_filtered.status_code}: {resp_filtered.text}"
            filtered_items = resp_filtered.json()
            for f_item in filtered_items:
                assert tag in f_item.get("tag", [])

# --- id=1233  name='Catalogue Item' ---
def test_catalogue_get_item():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]

    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == item_id

# --- id=1234  name='Catalogue Item Not Found' ---
def test_catalogue_get_item_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/non-existent-id-12345"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1235  name='Catalogue Size' ---
def test_catalogue_get_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "size" in data
    assert isinstance(data["size"], int)

# --- id=1236  name='Catalogue Tags' ---
def test_catalogue_get_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "tags" in data
    assert isinstance(data["tags"], list)

# --- id=1237  name='Catalogue Images' ---
def test_catalogue_get_images():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")

    image_url = None
    for item in items:
        if item.get("imageUrl"):
            image_url = item["imageUrl"][0]
            break

    if not image_url:
        pytest.skip("No images found in catalogue items")

    image_name = image_url.split("/")[-1]
    resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=1238  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    auth = (username, password)
    resp_login = requests.get(get_url("user", "/login"), auth=auth, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_cust = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    cust_data = resp_cust.json()
    assert cust_data.get("username") == username
    assert cust_data.get("email") == payload["email"]
    assert cust_data.get("firstName") == payload["firstName"]
    assert cust_data.get("lastName") == payload["lastName"]
    assert "password" not in cust_data or cust_data["password"] != password

# --- id=1239  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com"
    }
    resp1 = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1240  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = f"user_{uuid.uuid4().hex[:8]}"
    auth = (username, "wrongpassword")
    resp = requests.get(get_url("user", "/login"), auth=auth, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1241  name='User Add Address And' ---
def test_user_add_address_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    payload = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing St",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    assert addr_id is not None

    resp_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    addr_data = resp_get.json()
    assert addr_data.get("city") == payload["city"]
    assert addr_data.get("street") == payload["street"]

    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    embedded = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in embedded)

# --- id=1242  name='User Address' ---
def test_user_delete_address():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    payload = {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=payload, timeout=10)
    addr_id = resp.json().get("id")

    resp_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    embedded = resp_cust_addr.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in embedded)

# --- id=1243  name='User Add Card And' ---
def test_user_add_card_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    card_data = resp_get.json()
    assert card_data.get("expires") == payload["expires"]
    assert card_data.get("longNum").endswith("3456")
    assert "1234567890" not in card_data.get("longNum")

    resp_cust_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_cards.status_code == 200, f"Expected 200, got {resp_cust_cards.status_code}: {resp_cust_cards.text}"
    embedded = resp_cust_cards.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in embedded)

# --- id=1244  name='User Card' ---
def test_user_delete_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=payload, timeout=10)
    card_id = resp.json().get("id")

    resp_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_cust_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_cards.status_code == 200, f"Expected 200, got {resp_cust_cards.status_code}: {resp_cust_cards.text}"
    embedded = resp_cust_cards.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in embedded)

# --- id=1245  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=1246  name='User Nonexistent Customer' ---
def test_user_delete_nonexistent_customer():
    invalid_id = f"nonexistent_{uuid.uuid4().hex[:8]}"
    resp = requests.delete(get_url("user", f"/customers/{invalid_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

# --- id=1247  name='User Customers' ---
def test_user_get_customers():
    resp = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=1248  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": item_price
    }
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert len(cart_items) >= 1
    assert any(i["itemId"] == item_id and i["quantity"] == 2 for i in cart_items)

    resp_item = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["itemId"] == item_id

# --- id=1249  name='Carts Update And Item' ---
def test_carts_update_and_delete_item():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": item_price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)

    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": item_price}
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=patch_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=1250  name='Carts Cart' ---
def test_carts_delete_cart():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": item_price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=payload, timeout=10)

    resp_del = requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0

# --- id=1251  name='Carts Merge' ---
def test_carts_merge():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    session_id = f"session_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": item_price}, timeout=10)

    resp_merge = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cart_items = resp_get.json()
    assert any(i["itemId"] == item_id and i["quantity"] == 1 for i in cart_items)

# --- id=1252  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    resp_merge = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=1253  name='Carts Item Not Found' ---
def test_carts_get_item_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1254  name='Orders Create And' ---
def test_orders_create_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "firstName": "John", "lastName": "Doe", "email": "j@d.com"}, timeout=10)

    addr_payload = {"city": "City", "country": "Country", "number": "1", "postcode": "12345", "street": "Street", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("No items in catalogue")
    item_id = items[0]["id"]
    item_price = items[0]["price"]

    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": item_price}
    requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)

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
    assert order_data["customer"]["username"] == username
    assert order_data["total"] == item_price * 2
    assert len(order_data["items"]) >= 1

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == order_id

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    embedded_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in embedded_orders)

# --- id=1255  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"
    assert "message" in resp.json()

# --- id=1256  name='Orders Create Invalid Uri Format' ---
def test_orders_create_invalid_uri_format():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalidformat",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1257  name='Orders Not Found' ---
def test_orders_get_not_found():
    invalid_id = str(uuid.uuid4())
    resp = requests.get(get_url("orders", f"/orders/{invalid_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1258  name='Orders Search Not Found' ---
def test_orders_search_not_found():
    invalid_cust = f"nonexistent_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={invalid_cust}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1259  name='Payment Authorize And' ---
def test_payment_authorize_and_get():
    order_id = create_order_for_test()
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data["authorised"] is True
    assert auth_data["orderId"] == order_id

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) >= 1
    assert auths[-1]["orderId"] == order_id
    assert auths[-1]["authorised"] is True

# --- id=1260  name='Payment Authorize Declined' ---
def test_payment_authorize_declined():
    order_id = create_order_for_test()
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 150.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth_data = resp.json()
    assert auth_data["authorised"] is False

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert auths[-1]["authorised"] is False

# --- id=1261  name='Payment Empty' ---
def test_payment_get_empty():
    invalid_id = str(uuid.uuid4())
    resp = requests.get(get_url("payment-http", f"/payments/{invalid_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json() == []

# --- id=1262  name='Shipping And' ---
def test_shipping_post_and_get():
    order_id = create_order_for_test()
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    ship_data = resp.json()
    assert ship_data["orderId"] == order_id
    assert "carrier" in ship_data
    assert "trackingNumber" in ship_data

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data["orderId"] == order_id
    assert get_data["carrier"] == ship_data["carrier"]
    assert get_data["trackingNumber"] == ship_data["trackingNumber"]
