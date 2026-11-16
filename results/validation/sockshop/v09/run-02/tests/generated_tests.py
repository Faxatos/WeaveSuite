# Tests generated in iteration 02
# Captured: 2026-06-04T17:13:58
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=278  name='User Registration And Authentication' ---
def test_user_registration_and_authentication():
    username = f"user_{generate_random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    user_data = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    resp_bad_login = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

    resp_dup = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

    resp_del = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_del.status_code == 200, f"Expected 200, got {resp_del.status_code}: {resp_del.text}"

# --- id=279  name='Catalogue Queries' ---
def test_catalogue_queries():
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    tags_data = resp_tags.json()
    assert "tags" in tags_data

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    cat_data = resp_cat.json()
    assert len(cat_data) > 0

    item_id = cat_data[0]["id"]

    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["id"] == item_id

    resp_size = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp_size.status_code == 200, f"Expected 200, got {resp_size.status_code}: {resp_size.text}"
    assert "size" in resp_size.json()

    resp_not_found = requests.get(get_url("catalogue", f"/catalogue/nonexistent-{uuid.uuid4()}"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

# --- id=280  name='Carts Management' ---
def test_carts_management():
    customer_id = f"cart_user_{generate_random_string()}"

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200
    item_id = resp_cat.json()[0]["id"]

    item_data = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.0
    }
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    add_resp_data = resp_add.json()
    assert add_resp_data["itemId"] == item_data["itemId"]
    assert add_resp_data["quantity"] == item_data["quantity"]
    assert add_resp_data["unitPrice"] == item_data["unitPrice"]

    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    item_found = next((i for i in items if i["itemId"] == item_data["itemId"]), None)
    assert item_found is not None
    assert item_found["quantity"] == item_data["quantity"]
    assert item_found["unitPrice"] == item_data["unitPrice"]

    update_data = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 15.0
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_data, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    resp_get_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_item.status_code == 200, f"Expected 200, got {resp_get_item.status_code}: {resp_get_item.text}"
    get_item_data = resp_get_item.json()
    assert get_item_data["itemId"] == update_data["itemId"]
    assert get_item_data["quantity"] == update_data["quantity"]
    assert get_item_data["unitPrice"] == update_data["unitPrice"]

    resp_del_item = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del_item.status_code == 202, f"Expected 202, got {resp_del_item.status_code}: {resp_del_item.text}"

    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

    resp_get_cart_items = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get_cart_items.status_code == 200, f"Expected 200, got {resp_get_cart_items.status_code}: {resp_get_cart_items.text}"
    assert len(resp_get_cart_items.json()) == 0

# --- id=281  name='Order Workflow Success' ---
def test_order_workflow_success():
    username = f"order_user_{generate_random_string()}"

    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Order",
        "lastName": "Tester"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    address_data = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json()["id"]

    resp_get_addr = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    get_addr_data = resp_get_addr.json()
    assert get_addr_data["city"] == address_data["city"]
    assert get_addr_data["country"] == address_data["country"]
    assert get_addr_data["number"] == address_data["number"]
    assert get_addr_data["postcode"] == address_data["postcode"]
    assert get_addr_data["street"] == address_data["street"]

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    get_card_data = resp_get_card.json()
    assert get_card_data["ccv"] == card_data["ccv"]
    assert get_card_data["expires"] == card_data["expires"]

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp_cat.json()[0]["id"]

    item_data = {
        "itemId": item_id,
        "quantity": 1,
        "unitPrice": 15.0
    }
    resp_add_item = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp_add_item.status_code == 201, f"Expected 201, got {resp_add_item.status_code}: {resp_add_item.text}"

    resp_get_items = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get_items.status_code == 200, f"Expected 200, got {resp_get_items.status_code}: {resp_get_items.text}"
    assert len(resp_get_items.json()) > 0

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    assert "id" in order_data
    assert order_data["payment"]["authorised"] is True

    order_id = order_data["id"]

    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    get_order_data = resp_get_order.json()
    assert get_order_data["id"] == order_id
    assert get_order_data["payment"]["authorised"] is True

    resp_search = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}: {resp_search.text}"

    resp_get_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get_payment.status_code == 200, f"Expected 200, got {resp_get_payment.status_code}: {resp_get_payment.text}"
    payments = resp_get_payment.json()
    assert len(payments) > 0
    assert payments[0]["authorised"] is True
    assert payments[0]["orderId"] == order_id

    resp_get_shipment = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get_shipment.status_code == 200, f"Expected 200, got {resp_get_shipment.status_code}: {resp_get_shipment.text}"
    assert resp_get_shipment.json()["orderId"] == order_id

    resp_del_addr = requests.delete(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    resp_cust_addrs = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addrs.status_code == 200, f"Expected 200, got {resp_cust_addrs.status_code}: {resp_cust_addrs.text}"
    cust_addrs_data = resp_cust_addrs.json()
    assert len(cust_addrs_data.get("_embedded", {}).get("address", [])) == 0

    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

    resp_cust_cards = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_cards.status_code == 200, f"Expected 200, got {resp_cust_cards.status_code}: {resp_cust_cards.text}"
    cust_cards_data = resp_cust_cards.json()
    assert len(cust_cards_data.get("_embedded", {}).get("card", [])) == 0

# --- id=282  name='Order Workflow Payment Declined' ---
def test_order_workflow_payment_declined():
    username = f"fail_user_{generate_random_string()}"

    user_data = {
        "username": username,
        "password": "password",
        "email": f"{username}@example.com",
        "firstName": "Fail",
        "lastName": "Tester"
    }
    resp_reg = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    resp_get_user = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get_user.status_code == 200, f"Expected 200, got {resp_get_user.status_code}: {resp_get_user.text}"

    address_data = {
        "city": "Test City",
        "country": "Test Country",
        "number": "123",
        "postcode": "12345",
        "street": "Test Street",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    address_id = resp_addr.json()["id"]

    resp_get_addr = requests.get(get_url("user", f"/addresses/{address_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json()["city"] == address_data["city"]

    card_data = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json()["id"]

    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert resp_get_card.json()["ccv"] == card_data["ccv"]

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp_cat.json()[0]["id"]

    item_data = {
        "itemId": item_id,
        "quantity": 100,
        "unitPrice": 20.0
    }
    resp_add_item = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp_add_item.status_code == 201, f"Expected 201, got {resp_add_item.status_code}: {resp_add_item.text}"

    resp_get_items = requests.get(get_url("carts", f"/carts/{username}/items"), timeout=10)
    assert resp_get_items.status_code == 200, f"Expected 200, got {resp_get_items.status_code}: {resp_get_items.text}"
    assert len(resp_get_items.json()) > 0

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
