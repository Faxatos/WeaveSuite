# Tests generated in iteration 01
# Captured: 2026-06-07T01:55:23
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1195  name='User Register And Login Success' ---
def test_user_register_and_login_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=1196  name='User Register Conflict' ---
def test_user_register_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp1 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}: {resp1.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp2 = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=1197  name='User Login Unauthorized' ---
def test_user_login_unauthorized():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "wrongpassword"
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 401, f"Expected 401, got {resp_login.status_code}: {resp_login.text}"

# --- id=1198  name='User Customer Address Card' ---
def test_user_delete_customer_address_card():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    address_payload = {
        "street": "123 Main St",
        "number": "123",
        "country": "USA",
        "city": "Anytown",
        "postcode": "12345",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json().get("id")

    resp_get_addr = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_list_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_list_addr.status_code == 200, f"Expected 200, got {resp_list_addr.status_code}: {resp_list_addr.text}"
    addresses = resp_list_addr.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == address_id for a in addresses)

    resp_del_user = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del_user.status_code == 200, f"Expected 200, got {resp_del_user.status_code}: {resp_del_user.text}"

    resp_list_users = requests.get(get_url("user", "/customers"), timeout=10)
    assert resp_list_users.status_code == 200, f"Expected 200, got {resp_list_users.status_code}: {resp_list_users.text}"
    assert username not in resp_list_users.text

# --- id=1199  name='Catalogue Listing And Retrieval' ---
def test_catalogue_listing_and_retrieval():
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    items = resp_list.json()
    assert isinstance(items, list)
    assert len(items) > 0, "Expected at least one item in catalogue"

    item_id = items[0]["id"]

    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("id") == item_id

# --- id=1200  name='Catalogue Size And Tags' ---
def test_catalogue_size_and_tags():
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

# --- id=1201  name='Carts Add Item Cumulative State' ---
def test_carts_add_item_cumulative_state():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "No items found in catalogue"
    item = items[0]
    item_id = item["id"]

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item.get("price", 10.0)
    }

    resp1 = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp1.status_code == 201, f"Expected 201, got {resp1.status_code}: {resp1.text}"

    get_resp1 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get_resp1.status_code == 200, f"Expected 200, got {get_resp1.status_code}: {get_resp1.text}"
    assert get_resp1.json().get("quantity") == 1

    resp2 = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp2.status_code == 201, f"Expected 201, got {resp2.status_code}: {resp2.text}"

    get_resp2 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    assert get_resp2.json().get("quantity") == 2

# --- id=1202  name='Carts Update And Item' ---
def test_carts_update_and_delete_item():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "No items found in catalogue"
    item = items[0]
    item_id = item["id"]

    item_payload = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": item.get("price", 10.0)
    }

    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    get_resp1 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get_resp1.status_code == 200, f"Expected 200, got {get_resp1.status_code}: {get_resp1.text}"

    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": item.get("price", 10.0)
    }
    resp_update = requests.patch(get_url("carts", f"/carts/{username}/items"), json=update_payload, timeout=10)
    assert resp_update.status_code == 202, f"Expected 202, got {resp_update.status_code}: {resp_update.text}"

    get_resp2 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get_resp2.status_code == 200, f"Expected 200, got {get_resp2.status_code}: {get_resp2.text}"
    assert get_resp2.json().get("quantity") == 5

    resp_delete = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_delete.status_code == 202, f"Expected 202, got {resp_delete.status_code}: {resp_delete.text}"

    get_resp3 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert get_resp3.status_code == 404, f"Expected 404, got {get_resp3.status_code}: {get_resp3.text}"

# --- id=1203  name='Carts Merge Success' ---
def test_carts_merge_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) >= 2, "Not enough items in catalogue"
    item1 = items[0]
    item2 = items[1]

    item1_payload = {
        "itemId": item1["id"],
        "quantity": 1,
        "unitPrice": item1.get("price", 10.0)
    }
    resp_sess = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item1_payload, timeout=10)
    assert resp_sess.status_code == 201, f"Expected 201, got {resp_sess.status_code}: {resp_sess.text}"

    resp_sess_get = requests.get(get_url("carts", f"/carts/{session_id}/items/{item1['id']}"), timeout=10)
    assert resp_sess_get.status_code == 200, f"Expected 200, got {resp_sess_get.status_code}: {resp_sess_get.text}"

    item2_payload = {
        "itemId": item2["id"],
        "quantity": 1,
        "unitPrice": item2.get("price", 10.0)
    }
    resp_cust = requests.post(get_url("carts", f"/carts/{username}/items"), json=item2_payload, timeout=10)
    assert resp_cust.status_code == 201, f"Expected 201, got {resp_cust.status_code}: {resp_cust.text}"

    resp_cust_get = requests.get(get_url("carts", f"/carts/{username}/items/{item2['id']}"), timeout=10)
    assert resp_cust_get.status_code == 200, f"Expected 200, got {resp_cust_get.status_code}: {resp_cust_get.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    resp_items = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_items.status_code == 200, f"Expected 200, got {resp_items.status_code}: {resp_items.text}"
    cart_items = resp_items.json()
    item_ids = [item.get("itemId") for item in cart_items]
    assert item1["id"] in item_ids
    assert item2["id"] in item_ids

# --- id=1204  name='Carts Merge Not Found' ---
def test_carts_merge_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "No items found in catalogue"
    item = items[0]

    item_payload = {
        "itemId": item["id"],
        "quantity": 1,
        "unitPrice": item.get("price", 10.0)
    }
    resp_sess = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_payload, timeout=10)
    assert resp_sess.status_code == 201, f"Expected 201, got {resp_sess.status_code}: {resp_sess.text}"

    resp_sess_get = requests.get(get_url("carts", f"/carts/{session_id}/items/{item['id']}"), timeout=10)
    assert resp_sess_get.status_code == 200, f"Expected 200, got {resp_sess_get.status_code}: {resp_sess_get.text}"

    resp_del = requests.delete(get_url("carts", f"/carts/{session_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_merge = requests.get(get_url("carts", f"/carts/{username}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 404, f"Expected 404, got {resp_merge.status_code}: {resp_merge.text}"

# --- id=1205  name='Orders Place Order Success' ---
def test_orders_place_order_success():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    address_payload = {
        "street": "123 Main St",
        "number": "123",
        "country": "USA",
        "city": "Anytown",
        "postcode": "12345",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json().get("id")

    resp_get_addr = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    card_payload = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "No items found in catalogue"
    cheap_item = next((item for item in items if item.get("price", 0) <= 100), items[0])

    item_payload = {
        "itemId": cheap_item["id"],
        "quantity": 1,
        "unitPrice": cheap_item.get("price", 10.0)
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{cheap_item['id']}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id

    resp_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_payment.status_code == 200, f"Expected 200, got {resp_payment.status_code}: {resp_payment.text}"
    auths = resp_payment.json()
    assert isinstance(auths, list)
    assert len(auths) > 0, "Expected at least one payment authorization"
    assert auths[0].get("authorised") is True

    resp_shipping = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_shipping.status_code == 200, f"Expected 200, got {resp_shipping.status_code}: {resp_shipping.text}"
    assert resp_shipping.json().get("orderId") == order_id

# --- id=1206  name='Orders Place Order Payment Declined' ---
def test_orders_place_order_payment_declined():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    address_payload = {
        "street": "123 Main St",
        "number": "123",
        "country": "USA",
        "city": "Anytown",
        "postcode": "12345",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json().get("id")

    resp_get_addr = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    card_payload = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "No items found in catalogue"
    item = items[0]

    item_payload = {
        "itemId": item["id"],
        "quantity": 1000,
        "unitPrice": item.get("price", 10.0)
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item['id']}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=1207  name='Orders Search By Customer' ---
def test_orders_search_by_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    address_payload = {
        "street": "123 Main St",
        "number": "123",
        "country": "USA",
        "city": "Anytown",
        "postcode": "12345",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json().get("id")

    resp_get_addr = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"

    card_payload = {
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    assert len(items) > 0, "No items found in catalogue"
    item = items[0]

    item_payload = {
        "itemId": item["id"],
        "quantity": 1,
        "unitPrice": 10.0
    }
    resp_cart = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp_cart.status_code == 201, f"Expected 201, got {resp_cart.status_code}: {resp_cart.text}"

    resp_cart_get = requests.get(get_url("carts", f"/carts/{username}/items/{item['id']}"), timeout=10)
    assert resp_cart_get.status_code == 200, f"Expected 200, got {resp_cart_get.status_code}: {resp_cart_get.text}"

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")

    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

# --- id=1208  name='Orders Search By Customer Not Found' ---
def test_orders_search_by_customer_not_found():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_payload = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 404, f"Expected 404, got {resp_search.status_code}: {resp_search.text}"
