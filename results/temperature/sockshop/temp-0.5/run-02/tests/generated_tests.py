# Tests generated in iteration 02
# Captured: 2026-07-04T12:08:00
# Count:    26
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=386  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    url = get_url("catalogue", "/catalogue")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Expected at least one item in catalogue"

    item_id = items[0]["id"]

    url_id = get_url("catalogue", f"/catalogue/{item_id}")
    resp_id = requests.get(url_id, timeout=10)
    assert resp_id.status_code == 200, f"Expected 200, got {resp_id.status_code}: {resp_id.text}"
    item = resp_id.json()
    assert item["id"] == item_id
    assert item["name"] == items[0]["name"]

# --- id=387  name='Catalogue Size' ---
def test_catalogue_size():
    url = get_url("catalogue", "/catalogue/size")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()
    assert isinstance(resp.json()["size"], int)

# --- id=388  name='Catalogue Tags' ---
def test_catalogue_tags():
    url = get_url("catalogue", "/tags")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()
    assert isinstance(resp.json()["tags"], list)

# --- id=389  name='Catalogue Image' ---
def test_catalogue_image():
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    if not items:
        pytest.skip("No catalogue items found")

    item = items[0]
    image_urls = item.get("imageUrl", [])
    if not image_urls:
        pytest.skip("No images found for catalogue item")

    image_name = image_urls[0].split("/")[-1]
    url = get_url("catalogue", f"/catalogue/images/{image_name}")
    resp_img = requests.get(url, timeout=10)
    assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

# --- id=390  name='Catalogue Image Not Found' ---
def test_catalogue_image_not_found():
    url = get_url("catalogue", "/catalogue/images/nonexistent_image.jpeg")
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=391  name='Nonexistent Catalogue Item' ---
def test_get_nonexistent_catalogue_item():
    item_id = "nonexistent_item_" + "".join(random.choices(string.ascii_lowercase, k=8))
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=392  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp_reg = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_cust = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_cust.status_code == 200, f"Expected 200, got {resp_cust.status_code}: {resp_cust.text}"
    cust = resp_cust.json()
    assert cust["username"] == username
    assert cust["firstName"] == "Test"
    assert cust["lastName"] == "User"
    assert cust["email"] == f"{username}@example.com"
    assert "password" not in cust or cust["password"] != password

    auth = (username, password)
    resp_login = requests.get(get_url("user", "/login"), auth=auth, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=393  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=394  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    auth = (username, "wrongpassword")
    resp = requests.get(get_url("user", "/login"), auth=auth, timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=395  name='User Add Address And Card' ---
def test_user_add_address_and_card():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "John", "lastName": "Doe"
    }, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "number": "123", "street": "Main St", "city": "Anytown", "postcode": "12345", "country": "USA", "userID": username
    }, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json()["id"]

    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert resp_addr_get.json()["id"] == addr_id
    assert resp_addr_get.json()["number"] == "123"
    assert resp_addr_get.json()["street"] == "Main St"

    resp_card = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    assert resp_card_get.json()["id"] == card_id
    assert resp_card_get.json()["expires"] == "12/25"
    assert resp_card_get.json()["longNum"] == "************3456"

# --- id=396  name='User Address' ---
def test_user_delete_address():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@example.com", "firstName": "John", "lastName": "Doe"
    }, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "number": "123", "street": "Main St", "city": "Anytown", "postcode": "12345", "country": "USA", "userID": username
    }, timeout=10)
    addr_id = resp_addr.json()["id"]

    resp_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_addrs = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addrs.status_code == 200, f"Expected 200, got {resp_addrs.status_code}: {resp_addrs.text}"
    addrs = resp_addrs.json().get("_embedded", {}).get("address", [])
    assert not any(a["id"] == addr_id for a in addrs), "Address should be deleted"

# --- id=397  name='Customer Deletion' ---
def test_customer_deletion():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"
    }, timeout=10)

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"
    assert resp_del.json().get("status") is True

    resp_del2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del2.status_code == 200, f"Expected 200, got {resp_del2.status_code}: {resp_del2.text}"
    assert resp_del2.json().get("status") is False

# --- id=398  name='Cart Add And Item' ---
def test_cart_add_and_delete_item():
    customer_id = "cust_" + "".join(random.choices(string.ascii_lowercase, k=8))

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp_cat.json()[0]["id"]
    unit_price = resp_cat.json()[0]["price"]

    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2
    assert items[0]["unitPrice"] == unit_price

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get_after = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_after.status_code == 200, f"Expected 200, got {resp_get_after.status_code}: {resp_get_after.text}"
    assert len(resp_get_after.json()) == 0

# --- id=399  name='Cart Item Update' ---
def test_cart_item_update():
    customer_id = "cust_" + "".join(random.choices(string.ascii_lowercase, k=8))

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp_cat.json()[0]["id"]

    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={
        "itemId": item_id, "quantity": 1, "unitPrice": 10.0
    }, timeout=10)

    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json={
        "itemId": item_id, "quantity": 5, "unitPrice": 10.0
    }, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 5

# --- id=400  name='Cart Merge' ---
def test_cart_merge():
    session_id = "sess_" + "".join(random.choices(string.ascii_lowercase, k=8))
    customer_id = "cust_" + "".join(random.choices(string.ascii_lowercase, k=8))

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp_cat.json()[0]["id"]

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={
        "itemId": item_id, "quantity": 2, "unitPrice": 10.0
    }, timeout=10)

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["quantity"] == 2

# --- id=401  name='Cart Merge Not Found' ---
def test_cart_merge_not_found():
    customer_id = "cust_" + "".join(random.choices(string.ascii_lowercase, k=8))
    session_id = "sess_" + "".join(random.choices(string.ascii_lowercase, k=8))

    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=402  name='Cart Deletion' ---
def test_cart_deletion():
    customer_id = "cust_" + "".join(random.choices(string.ascii_lowercase, k=8))

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp_cat.json()[0]["id"]

    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={
        "itemId": item_id, "quantity": 1, "unitPrice": 10.0
    }, timeout=10)

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0

# --- id=403  name='Nonexistent Cart Item' ---
def test_get_nonexistent_cart_item():
    customer_id = "cust_" + "".join(random.choices(string.ascii_lowercase, k=8))
    item_id = "nonexistent_item"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=404  name='Order Creation Success' ---
def test_order_creation_success():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"
    }, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "US", "userID": username
    }, timeout=10)
    addr_id = resp_addr.json()["id"]

    resp_card = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    card_id = resp_card.json()["id"]

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    cat_item = resp_cat.json()[0]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": cat_item["id"], "quantity": 2, "unitPrice": cat_item["price"]
    }, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order = resp_order.json()
    order_id = order["id"]

    assert order["customer"]["username"] == username
    assert order["address"]["number"] == "1"
    assert order["card"]["longNum"] == "************3456"
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == cat_item["id"]
    assert order["items"][0]["quantity"] == 2
    assert order["items"][0]["unitPrice"] == cat_item["price"]
    assert order["total"] == 2 * cat_item["price"]

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    fetched_order = resp_get_order.json()
    assert fetched_order["id"] == order_id
    assert fetched_order["total"] == 2 * cat_item["price"]

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"
    customer_orders = resp_search.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in customer_orders), "Order not found in customer search"

# --- id=405  name='Order Creation Empty Cart Failure' ---
def test_order_creation_empty_cart_failure():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"
    }, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={
        "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "US", "userID": username
    }, timeout=10)
    addr_id = resp_addr.json()["id"]

    resp_card = requests.post(get_url("user", "/cards"), json={
        "longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username
    }, timeout=10)
    card_id = resp_card.json()["id"]

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
    assert "message" in resp_order.json()

# --- id=406  name='Order Creation Invalid Uri Format' ---
def test_order_creation_invalid_uri_format():
    username = "user_" + "".join(random.choices(string.ascii_lowercase, k=8))
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"
    }, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalid_format_without_colon",
        "card": "/cards/invalid_format_without_colon",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 404, f"Expected 404, got {resp_order.status_code}: {resp_order.text}"

# --- id=407  name='Nonexistent Order' ---
def test_get_nonexistent_order():
    order_id = str(uuid.uuid4())
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=408  name='Orders Search Not Found' ---
def test_orders_search_not_found():
    customer_id = "cust_" + "".join(random.choices(string.ascii_lowercase, k=8))
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={customer_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=409  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = str(uuid.uuid4())
    pay_req = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"},
        "card": {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth = resp_pay.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id
    assert "message" in auth
    assert "time" in auth

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["orderId"] == order_id
    assert auths[0]["authorised"] is True

# --- id=410  name='Payment Authorization Declined' ---
def test_payment_authorization_declined():
    order_id = str(uuid.uuid4())
    pay_req = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"},
        "card": {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}
    }

    resp_pay = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    auth = resp_pay.json()
    assert auth["authorised"] is False
    assert auth["orderId"] == order_id

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["authorised"] is False

# --- id=411  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = str(uuid.uuid4())
    ship_req = {
        "orderId": order_id,
        "itemCount": 2,
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"}
    }

    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    shipment = resp_ship.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment
    assert "deliveryDate" in shipment

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    fetched = resp_get.json()
    assert fetched["orderId"] == order_id
    assert fetched["carrier"] == shipment["carrier"]
    assert fetched["trackingNumber"] == shipment["trackingNumber"]
