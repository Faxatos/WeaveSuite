# Tests generated in iteration 04
# Captured: 2026-07-10T16:34:31
# Count:    18
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=34  name='User Register And Login' ---
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

    login_resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"

# --- id=35  name='User Register Conflict' ---
def test_user_register_conflict():
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

    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=36  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    login_resp = requests.get(get_url("user", "/login"), auth=("nonexistent", "wrongpass"), timeout=10)
    assert login_resp.status_code == 401, f"Expected 401, got {login_resp.status_code}: {login_resp.text}"

# --- id=37  name='Carts Add Update Remove Item' ---
def test_carts_add_update_remove_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "Catalogue is empty"
    item = items[0]
    item_id = item["id"]
    unit_price = item["price"]

    cart_item = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    add_resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item, timeout=10)
    assert add_resp.status_code == 201, f"Expected 201, got {add_resp.status_code}: {add_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    fetched_item = get_resp.json()
    assert fetched_item["itemId"] == item_id
    assert fetched_item["quantity"] == 2

    cart_item_update = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": unit_price
    }
    patch_resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=cart_item_update, timeout=10)
    assert patch_resp.status_code == 202, f"Expected 202, got {patch_resp.status_code}: {patch_resp.text}"

    get_resp2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    fetched_item2 = get_resp2.json()
    assert fetched_item2["quantity"] == 5

    del_resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert del_resp.status_code == 202, f"Expected 202, got {del_resp.status_code}: {del_resp.text}"

    get_resp3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp3.status_code == 404, f"Expected 404, got {get_resp3.status_code}: {get_resp3.text}"

# --- id=38  name='Carts Nonexistent Item' ---
def test_carts_get_nonexistent_item():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    item_id = f"item_{uuid.uuid4().hex[:8]}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert get_resp.status_code == 404, f"Expected 404, got {get_resp.status_code}: {get_resp.text}"

# --- id=39  name='Carts Merge' ---
def test_carts_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("Catalogue is empty")
    item = items[0]

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={
        "itemId": item["id"],
        "quantity": 1,
        "unitPrice": item["price"]
    }, timeout=10)

    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 202, f"Expected 202, got {merge_resp.status_code}: {merge_resp.text}"

    get_resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    cart_items = get_resp.json()
    assert len(cart_items) > 0
    assert any(ci["itemId"] == item["id"] for ci in cart_items)

# --- id=40  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    merge_resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert merge_resp.status_code == 404, f"Expected 404, got {merge_resp.status_code}: {merge_resp.text}"

# --- id=41  name='Catalogue Nonexistent Item' ---
def test_catalogue_get_nonexistent_item():
    item_id = f"nonexistent_{uuid.uuid4().hex[:8]}"
    get_resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert get_resp.status_code == 404, f"Expected 404, got {get_resp.status_code}: {get_resp.text}"

# --- id=42  name='Catalogue Size And Tags' ---
def test_catalogue_size_and_tags():
    size_resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert size_resp.status_code == 200, f"Expected 200, got {size_resp.status_code}: {size_resp.text}"
    assert "size" in size_resp.json()

    tags_resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert tags_resp.status_code == 200, f"Expected 200, got {tags_resp.status_code}: {tags_resp.text}"
    assert "tags" in tags_resp.json()

# --- id=43  name='Catalogue Images' ---
def test_catalogue_images():
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    if len(items) > 0 and "imageUrl" in items[0] and len(items[0]["imageUrl"]) > 0:
        image_path = items[0]["imageUrl"][0]
        image_name = image_path.split("/")[-1]
        img_resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
        assert img_resp.status_code == 200, f"Expected 200, got {img_resp.status_code}: {img_resp.text}"

# --- id=44  name='Catalogue Images Not Found' ---
def test_catalogue_images_not_found():
    img_resp = requests.get(get_url("catalogue", "/catalogue/images/nonexistent_image.jpg"), timeout=10)
    assert img_resp.status_code == 404, f"Expected 404, got {img_resp.status_code}: {img_resp.text}"

# --- id=45  name='Orders Workflow' ---
def test_orders_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }, timeout=10)

    requests.post(get_url("user", "/addresses"), json={
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "NW1",
        "street": "Baker St",
        "userID": username
    }, timeout=10)

    requests.post(get_url("user", "/cards"), json={
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }, timeout=10)

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = cat_resp.json()
    if not items:
        pytest.skip("Catalogue is empty")
    item = items[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={
        "itemId": item["id"],
        "quantity": 1,
        "unitPrice": item["price"]
    }, timeout=10)

    addr_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    addr_uri = ""
    if addr_resp.status_code == 200:
        data = addr_resp.json()
        if isinstance(data, dict) and "_embedded" in data:
            addr_list = data["_embedded"].get("address", [])
            if addr_list:
                addr_uri = addr_list[0].get("_links", {}).get("self", {}).get("href", "")
        elif isinstance(data, list) and len(data) > 0:
            addr_uri = data[0].get("_links", {}).get("self", {}).get("href", "")
            if not addr_uri:
                addr_id = data[0].get("addressId") or data[0].get("id")
                if isinstance(addr_id, dict):
                    addr_id = addr_id.get("addressId")
                if addr_id:
                    addr_uri = get_url("user", f"/addresses/{addr_id}")

    card_resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    card_uri = ""
    if card_resp.status_code == 200:
        data = card_resp.json()
        if isinstance(data, dict) and "_embedded" in data:
            card_list = data["_embedded"].get("card", [])
            if card_list:
                card_uri = card_list[0].get("_links", {}).get("self", {}).get("href", "")
        elif isinstance(data, list) and len(data) > 0:
            card_uri = data[0].get("_links", {}).get("self", {}).get("href", "")
            if not card_uri:
                card_id = data[0].get("cardId") or data[0].get("id")
                if isinstance(card_id, dict):
                    card_id = card_id.get("cardId")
                if card_id:
                    card_uri = get_url("user", f"/cards/{card_id}")

    if not addr_uri or not card_uri:
        pytest.skip("Could not retrieve address or card URIs from user service")

    customer_uri = get_url("user", f"/customers/{username}")
    items_uri = get_url("carts", f"/carts/{username}/items")

    order_req = {
        "address": addr_uri,
        "card": card_uri,
        "customer": customer_uri,
        "items": items_uri
    }

    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"

    search_resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"

# --- id=46  name='Orders Not Found' ---
def test_orders_get_not_found():
    order_id = f"nonexistent_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=47  name='Orders Search Not Found' ---
def test_orders_search_not_found():
    cust_id = f"nonexistent_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={cust_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=48  name='User Customer' ---
def test_user_delete_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }, timeout=10)

    del_resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

    login_resp = requests.get(get_url("user", "/login"), auth=(username, "password"), timeout=10)
    assert login_resp.status_code == 401, f"Expected 401, got {login_resp.status_code}: {login_resp.text}"

# --- id=49  name='User Address' ---
def test_user_delete_address():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }, timeout=10)

    requests.post(get_url("user", "/addresses"), json={
        "city": "London",
        "country": "UK",
        "number": "10",
        "postcode": "NW1",
        "street": "Baker St",
        "userID": username
    }, timeout=10)

    addr_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    addr_id = None
    if addr_resp.status_code == 200:
        data = addr_resp.json()
        if isinstance(data, dict) and "_embedded" in data:
            addr_list = data["_embedded"].get("address", [])
            if addr_list:
                addr_id = addr_list[0].get("addressId") or addr_list[0].get("id")
        elif isinstance(data, list) and len(data) > 0:
            addr_id = data[0].get("addressId") or data[0].get("id")

    if isinstance(addr_id, dict):
        addr_id = addr_id.get("addressId")

    if addr_id:
        del_resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
        assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

        get_all_resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
        assert get_all_resp.status_code == 200, f"Expected 200, got {get_all_resp.status_code}: {get_all_resp.text}"
        data_after = get_all_resp.json()
        if isinstance(data_after, dict) and "_embedded" in data_after:
            assert len(data_after["_embedded"].get("address", [])) == 0
        elif isinstance(data_after, list):
            assert len(data_after) == 0

# --- id=50  name='Payment Http Authorize' ---
def test_payment_http_authorize():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    payment_req = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "NW1",
            "street": "Baker St"
        },
        "amount": 99.99,
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

    pay_resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    auth = pay_resp.json()
    assert auth["orderId"] == order_id
    assert "authorised" in auth

    get_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"

# --- id=51  name='Shipping Http Ship' ---
def test_shipping_http_ship():
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    shipping_req = {
        "address": {
            "city": "London",
            "country": "UK",
            "number": "10",
            "postcode": "NW1",
            "street": "Baker St"
        },
        "itemCount": 3,
        "orderId": order_id
    }

    ship_resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    shipment = ship_resp.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment
    assert "trackingNumber" in shipment

    get_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    fetched_shipment = get_resp.json()
    assert fetched_shipment["orderId"] == order_id
    assert fetched_shipment["trackingNumber"] == shipment["trackingNumber"]
