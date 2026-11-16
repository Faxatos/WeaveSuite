# Tests generated in iteration 16
# Captured: 2026-06-30T18:22:11
# Count:    21
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=680  name='User Register And Login Success' ---
def test_user_register_and_login_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
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

    login_resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

    cust_resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert cust_resp.status_code == 200, f"Expected 200, got {cust_resp.status_code}: {cust_resp.text}"
    assert cust_resp.json().get("username") == username

# --- id=681  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "pwd"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=682  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    resp = requests.get(get_url("user", "/login"), auth=("nonexistent", "wrongpwd"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=683  name='User Add Address And' ---
def test_user_add_address_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_data = {
        "number": "123",
        "street": "Main St",
        "city": "Anytown",
        "postcode": "12345",
        "country": "USA",
        "userID": username
    }
    post_resp = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    assert post_resp.status_code == 200, f"Expected 200, got {post_resp.status_code}: {post_resp.text}"
    addr_id = post_resp.json().get("id")

    get_resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("city") == "Anytown"

    list_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    addresses = list_resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

# --- id=684  name='User Add Card And' ---
def test_user_add_card_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    card_data = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    post_resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert post_resp.status_code == 200, f"Expected 200, got {post_resp.status_code}: {post_resp.text}"
    card_id = post_resp.json().get("id")

    get_resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    card_info = get_resp.json()
    assert card_info.get("expires") == "12/25"
    assert "*" in card_info.get("longNum")

# --- id=685  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    del_resp1 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_resp1.status_code == 200, f"Expected 200, got {del_resp1.status_code}: {del_resp1.text}"
    assert del_resp1.json().get("status") is True

    del_resp2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_resp2.status_code == 200, f"Expected 200, got {del_resp2.status_code}: {del_resp2.text}"
    assert del_resp2.json().get("status") is False

# --- id=686  name='Carts Add Item And' ---
def test_carts_add_item_and_get():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_data = {"itemId": "item1", "quantity": 2, "unitPrice": 10.5}

    post_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert post_resp.status_code == 201, f"Expected 201, got {post_resp.status_code}: {post_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    items = get_resp.json()
    assert len(items) >= 1
    assert any(i.get("itemId") == "item1" and i.get("quantity") == 2 for i in items)

    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    get_resp2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/item1"), timeout=10)
    assert get_resp2.status_code == 200
    assert get_resp2.json().get("quantity") == 4

# --- id=687  name='Carts Update Item' ---
def test_carts_update_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": "item2", "quantity": 1, "unitPrice": 5.0}, timeout=10)

    patch_resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": "item2", "quantity": 5, "unitPrice": 5.0}, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/item2"), timeout=10)
    assert get_resp.status_code == 200
    assert get_resp.json().get("quantity") == 5

# --- id=688  name='Carts Item' ---
def test_carts_delete_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": "item3", "quantity": 1, "unitPrice": 1.0}, timeout=10)

    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/item3"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/item3"), timeout=10)
    assert get_resp.status_code == 404, f"Expected 404, got {get_resp.status_code}: {get_resp.text}"

# --- id=689  name='Carts Cart' ---
def test_carts_delete_cart():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": "item4", "quantity": 1, "unitPrice": 1.0}, timeout=10)

    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200
    assert len(get_resp.json()) == 0

# --- id=690  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": "item_merge", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200
    items = get_resp.json()
    assert any(i.get("itemId") == "item_merge" for i in items)

# --- id=691  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    list_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}: {list_resp.text}"
    items = list_resp.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0].get("id")
        get_resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
        assert get_resp.json().get("id") == item_id

# --- id=692  name='Catalogue Not Found' ---
def test_catalogue_get_not_found():
    resp = requests.get(get_url("catalogue", "/catalogue/nonexistent_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=693  name='Catalogue Tags' ---
def test_catalogue_tags():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

# --- id=694  name='Orders Create And' ---
def test_orders_create_and_get():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    addr_post = requests.post(get_url("user", "/addresses"), json={"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C", "userID": username}, timeout=10)
    addr_id = addr_post.json().get("id")

    card_post = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_post.json().get("id")

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    post_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert post_resp.status_code == 201, f"Expected 201, got {post_resp.status_code}: {post_resp.text}"
    order_data = post_resp.json()
    order_id = order_data.get("id")
    assert order_id is not None
    assert order_data.get("customer", {}).get("username") == username

    get_resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("id") == order_id

    search_resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    cust_orders = search_resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in cust_orders)

# --- id=695  name='Orders Create Missing Fields' ---
def test_orders_create_missing_fields():
    order_req = {
        "customer": "/customers/someuser"
    }
    post_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert post_resp.status_code == 406, f"Expected 406, got {post_resp.status_code}: {post_resp.text}"

# --- id=696  name='Orders Create Invalid Uri' ---
def test_orders_create_invalid_uri():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": "/addresses/invalidformat",
        "card": "/cards/invalidformat",
        "items": f"/carts/{username}/items"
    }
    post_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert post_resp.status_code == 404, f"Expected 404, got {post_resp.status_code}: {post_resp.text}"

# --- id=697  name='Payment Authorize Success' ---
def test_payment_authorize_success():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    pay_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    post_resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert post_resp.status_code == 200, f"Expected 200, got {post_resp.status_code}: {post_resp.text}"
    assert post_resp.json().get("authorised") is True

    get_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    auths = get_resp.json()
    assert len(auths) == 1
    assert auths[0].get("orderId") == order_id
    assert auths[0].get("authorised") is True

# --- id=698  name='Payment Authorize Decline Boundary' ---
def test_payment_authorize_decline_boundary():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    pay_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 105.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    post_resp = requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    assert post_resp.status_code == 200, f"Expected 200, got {post_resp.status_code}: {post_resp.text}"
    assert post_resp.json().get("authorised") is False

    get_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_resp.status_code == 200
    auths = get_resp.json()
    assert len(auths) == 1
    assert auths[0].get("authorised") is False

# --- id=699  name='Payment Authorize Multiple' ---
def test_payment_authorize_multiple():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    pay_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 10.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)
    requests.post(get_url("payment-http", "/payments"), json=pay_req, timeout=10)

    get_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_resp.status_code == 200
    assert len(get_resp.json()) == 2

# --- id=700  name='Shipping And' ---
def test_shipping_post_and_get():
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    ship_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }

    post_resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert post_resp.status_code == 200, f"Expected 200, got {post_resp.status_code}: {post_resp.text}"
    assert post_resp.json().get("orderId") == order_id

    get_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    assert get_resp.json().get("orderId") == order_id
