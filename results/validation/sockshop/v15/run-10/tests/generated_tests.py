# Tests generated in iteration 10
# Captured: 2026-06-07T08:24:05
# Count:    33
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1340  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1341  name='User Register Duplicate' ---
def test_user_register_duplicate():
    username = f"user_{generate_random_string()}"
    user_data = {
        "username": username,
        "password": "pwd",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    resp1 = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp2 = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1342  name='User Login Fail' ---
def test_user_login_fail():
    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth("invalid", "invalid"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=1343  name='User Add Address' ---
def test_user_add_address():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    address_data = {
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "SW1A 1AA",
        "street": "Downing St",
        "userID": username
    }

    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json().get("id")
    assert address_id is not None

    resp_get = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("city") == "London"

# --- id=1344  name='User Add Card' ---
def test_user_add_card():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    card_data = {
        "longNum": "1234567812345678",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }

    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    resp_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("expires") == "12/25"

# --- id=1345  name='User Address' ---
def test_user_delete_address():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    address_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St", "userID": username}, timeout=10)
    address_id = address_resp.json().get("id")

    resp_del = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    addresses = resp_get.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses)

# --- id=1346  name='User Card' ---
def test_user_delete_card():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    resp_del = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    cards = resp_get.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

# --- id=1347  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert username not in resp_get.text

# --- id=1348  name='User Addresses Empty' ---
def test_user_get_addresses_empty():
    resp = requests.get(get_url("user", "/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json().get("_embedded", {}).get("address", [])) == 0

# --- id=1349  name='User Cards Empty' ---
def test_user_get_cards_empty():
    resp = requests.get(get_url("user", "/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json().get("_embedded", {}).get("card", [])) == 0

# --- id=1350  name='Carts Add Item Cumulative' ---
def test_carts_add_item_cumulative():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    item_data_1 = {"itemId": item_id, "quantity": 2, "unitPrice": 15.5}
    resp1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data_1, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    resp_get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    assert resp_get1.json().get("quantity") == 2

    item_data_2 = {"itemId": item_id, "quantity": 3, "unitPrice": 15.5}
    resp2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data_2, timeout=10)
    assert resp2.status_code == 201, f"Expected 201, got {resp2.status_code}: {resp2.text}"

    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 5

# --- id=1351  name='Carts Item' ---
def test_carts_patch_item():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": item_id, "quantity": 10, "unitPrice": 10.0}, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 10

# --- id=1352  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=1353  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{generate_random_string()}"
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": "sock1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert len(resp_get.json()) == 0

# --- id=1354  name='Carts Cart' ---
def test_carts_get_cart():
    customer_id = f"cust_{generate_random_string()}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("customerId") == customer_id

# --- id=1355  name='Carts Item Not Found' ---
def test_carts_get_item_not_found():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1356  name='Carts Merge Success' ---
def test_carts_merge_success():
    session_id = f"sess_{generate_random_string()}"
    customer_id = f"cust_{generate_random_string()}"

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": "sock1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) > 0
    assert items[0].get("itemId") == "sock1"

# --- id=1357  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1358  name='Carts Async Item Not Found' ---
def test_carts_async_get_item_not_found():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"
    resp = requests.get(get_url("carts", f"/carts-async/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1359  name='Carts Async Merge Not Found' ---
def test_carts_async_merge_not_found():
    customer_id = f"cust_{generate_random_string()}"
    session_id = f"sess_{generate_random_string()}"
    resp = requests.get(get_url("carts", f"/carts-async/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1360  name='Catalogue Socks' ---
def test_catalogue_get_socks():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    if socks:
        sock_id = socks[0].get("id")
        resp_sock = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp_sock.status_code == 200, f"Expected 200, got {resp_sock.status_code}: {resp_sock.text}"
        assert resp_sock.json().get("id") == sock_id

# --- id=1361  name='Catalogue Sock Not Found' ---
def test_catalogue_get_sock_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/invalid-sock-id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1362  name='Catalogue Image Success' ---
def test_catalogue_get_image_success():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    socks = resp.json()
    if socks and socks[0].get("imageUrl"):
        image_url = socks[0]["imageUrl"][0]
        image_name = image_url.split("/")[-1]
        resp_img = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert resp_img.status_code == 200, f"Expected 200, got {resp_img.status_code}: {resp_img.text}"

# --- id=1363  name='Catalogue Image Not Found' ---
def test_catalogue_get_image_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/images/invalid-image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1364  name='Catalogue Tags' ---
def test_catalogue_get_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=1365  name='Catalogue Size' ---
def test_catalogue_get_size():
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

# --- id=1366  name='Orders Create Success' ---
def test_orders_create_success():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    address_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St", "userID": username}, timeout=10)
    address_id = address_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "sock1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order_id = resp.json().get("id")
    assert order_id is not None

    resp_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("id") == order_id

# --- id=1367  name='Orders Create Payment Declined' ---
def test_orders_create_payment_declined():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    address_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St", "userID": username}, timeout=10)
    address_id = address_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "sock1", "quantity": 10, "unitPrice": 15.0}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=1368  name='Orders Not Found' ---
def test_orders_get_not_found():
    resp = requests.get(get_url("orders", "/orders/invalid-order-id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1369  name='Orders Search Success' ---
def test_orders_search_success():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    address_resp = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St", "userID": username}, timeout=10)
    address_id = address_resp.json().get("id")

    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "sock1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

# --- id=1370  name='Orders Search Not Found' ---
def test_orders_search_not_found():
    resp = requests.get(get_url("orders", "/orders/search/customerId?custId=invalid-cust-id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=1371  name='Payment Authorize Success' ---
def test_payment_authorize_success():
    order_id = f"order_{generate_random_string()}"
    payment_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678"},
        "customer": {"firstName": "Test", "lastName": "User"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) > 0
    assert auths[0].get("orderId") == order_id

# --- id=1372  name='Shipping And' ---
def test_shipping_post_and_get():
    order_id = f"order_{generate_random_string()}"
    shipping_req = {
        "address": {"city": "London", "country": "UK", "number": "10", "postcode": "SW1A 1AA", "street": "Downing St"},
        "itemCount": 2,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("orderId") == order_id

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
