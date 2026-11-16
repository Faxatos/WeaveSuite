# Tests generated in iteration 07
# Captured: 2026-07-04T15:45:20
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=474  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{random_string()}"
    password = "password123"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register
    resp = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Login
    auth = HTTPBasicAuth(username, password)
    resp_login = requests.get(get_url("user", "/login"), auth=auth, timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Duplicate register
    resp_dup = requests.post(get_url("user", "/register"), json=payload, timeout=10)
    assert resp_dup.status_code == 409, f"Expected 409, got {resp_dup.status_code}: {resp_dup.text}"

    # Negative: Bad login
    bad_auth = HTTPBasicAuth(username, "wrongpass")
    resp_bad_login = requests.get(get_url("user", "/login"), auth=bad_auth, timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=475  name='User Address Card Lifecycle' ---
def test_user_address_card_lifecycle():
    username = f"user_{random_string()}"
    payload = {"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=payload, timeout=10)

    # Add Address
    addr_payload = {"city": "City", "country": "Country", "number": "12", "postcode": "12345", "street": "Street", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    # Get Address
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json().get("city") == "City"

    # Customer Addresses
    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    assert len(resp_cust_addr.json().get("_embedded", {}).get("address", [])) > 0

    # Add Card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    # Get Card
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert "3456" in resp_get_card.json().get("longNum")

    # Customer Cards
    resp_cust_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_card.status_code == 200, f"Expected 200, got {resp_cust_card.status_code}: {resp_cust_card.text}"
    assert len(resp_cust_card.json().get("_embedded", {}).get("card", [])) > 0

    # Delete Address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Delete Card
    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

# --- id=476  name='Catalogue List And' ---
def test_catalogue_list_and_get():
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    items = resp_list.json()
    assert len(items) > 0

    item_id = items[0]["id"]
    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["id"] == item_id

    resp_not_found = requests.get(get_url("catalogue", "/catalogue/invalid-id-999"), timeout=10)
    assert resp_not_found.status_code == 404, f"Expected 404, got {resp_not_found.status_code}: {resp_not_found.text}"

    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"
    assert "tags" in resp_tags.json()

# --- id=477  name='Carts Add Update Items' ---
def test_carts_add_update_delete_items():
    customer_id = f"cust_{random_string()}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200
    item = cat_resp.json()[0]
    item_id = item["id"]
    price = item["price"]

    payload = {"itemId": item_id, "quantity": 1, "unitPrice": price}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    resp_items = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_items.status_code == 200, f"Expected 200, got {resp_items.status_code}: {resp_items.text}"
    assert any(i["itemId"] == item_id for i in resp_items.json())

    update_payload = {"itemId": item_id, "quantity": 5, "unitPrice": price}
    resp_update = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_update.status_code == 202, f"Expected 202, got {resp_update.status_code}: {resp_update.text}"

    resp_item = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json()["quantity"] == 5

    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    resp_item_after = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_item_after.status_code == 404, f"Expected 404, got {resp_item_after.status_code}: {resp_item_after.text}"

    resp_del_cart = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp_del_cart.status_code == 202, f"Expected 202, got {resp_del_cart.status_code}: {resp_del_cart.text}"

# --- id=478  name='Orders E2e Workflow' ---
def test_orders_e2e_workflow():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 2, "unitPrice": item["price"]}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order = order_resp.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order["customer"]["username"] == username

    get_order_resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert get_order_resp.status_code == 200, f"Expected 200, got {get_order_resp.status_code}: {get_order_resp.text}"
    assert get_order_resp.json()["id"] == order_id

    search_resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    cust_orders = search_resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in cust_orders)

    pay_resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert pay_resp.status_code == 200, f"Expected 200, got {pay_resp.status_code}: {pay_resp.text}"
    auths = pay_resp.json()
    assert len(auths) > 0
    assert auths[0]["orderId"] == order_id
    assert auths[0]["authorised"] is True

    ship_resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert ship_resp.status_code == 200, f"Expected 200, got {ship_resp.status_code}: {ship_resp.text}"
    assert ship_resp.json()["orderId"] == order_id

# --- id=479  name='Orders Missing Fields' ---
def test_orders_missing_fields():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]
    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 406, f"Expected 406, got {order_resp.status_code}: {order_resp.text}"
    assert "message" in order_resp.json()

# --- id=480  name='Orders Invalid Composite Id' ---
def test_orders_invalid_composite_id():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item["id"], "quantity": 1, "unitPrice": item["price"]}, timeout=10)

    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_id_format",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert order_resp.status_code == 404, f"Expected 404, got {order_resp.status_code}: {order_resp.text}"

# --- id=481  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = str(uuid.uuid4())
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["authorised"] is True
    assert auth["orderId"] == order_id

    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) == 1
    assert auths[0]["orderId"] == order_id

    payload["amount"] = 150.0
    resp_declined = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp_declined.status_code == 200, f"Expected 200, got {resp_declined.status_code}: {resp_declined.text}"
    assert resp_declined.json()["authorised"] is False

# --- id=482  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = str(uuid.uuid4())
    payload = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 3,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id
    assert "carrier" in shipment

    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json()["orderId"] == order_id
