# Tests generated in iteration 20
# Captured: 2026-06-30T20:52:27
# Count:    14
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=732  name='End To End Order Workflow' ---
def test_end_to_end_order_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "John", "lastName": "Doe"}
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, "password123"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    address_data = {"street": "123 Main St", "number": "12", "city": "Anytown", "postcode": "12345", "country": "USA", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    address_id = resp.json()["id"]

    card_data = {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json()["id"]

    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) > 0, "Catalogue is empty"
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    item_data = {"itemId": item_id, "quantity": 2, "unitPrice": unit_price}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    order_req = {"customer": f"/customers/{username}", "address": f"/addresses/{address_id}", "card": f"/cards/{card_id}", "items": f"/carts/{username}/items"}
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order["id"] == order_id
    assert fetched_order["customer"]["username"] == username
    assert len(fetched_order["items"]) == 1
    assert fetched_order["items"][0]["itemId"] == item_id
    assert fetched_order["items"][0]["quantity"] == 2

# --- id=733  name='User Registration Conflict' ---
def test_user_registration_conflict():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp2 = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp2.status_code == 409, f"Expected 409, got {resp2.status_code}: {resp2.text}"

# --- id=734  name='Catalogue Search And Retrieval' ---
def test_catalogue_search_and_retrieval():
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    tags_data = resp.json()
    assert "tags" in tags_data

    if tags_data["tags"]:
        tag = tags_data["tags"][0]
        resp2 = requests.get(get_url("catalogue", f"/catalogue?tags={tag}"), timeout=10)
        assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
        items = resp2.json()

        if items:
            item_id = items[0]["id"]
            resp3 = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
            assert resp3.status_code == 200, f"Expected 200, got {resp3.status_code}: {resp3.text}"
            assert resp3.json()["id"] == item_id

            resp4 = requests.get(get_url("catalogue", f"/catalogue/size?tags={tag}"), timeout=10)
            assert resp4.status_code == 200, f"Expected 200, got {resp4.status_code}: {resp4.text}"
            assert resp4.json()["size"] >= 1

# --- id=735  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = create_test_order()
    payment_req = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"street": "1", "number": "1", "city": "C", "postcode": "1", "country": "US"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["orderId"] == order_id
    assert auth["authorised"] is True

    resp2 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    auths = resp2.json()
    assert len(auths) >= 1
    assert any(a["orderId"] == order_id for a in auths)

    resp3 = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp3.status_code == 200, f"Expected 200, got {resp3.status_code}: {resp3.text}"

    resp4 = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp4.status_code == 200, f"Expected 200, got {resp4.status_code}: {resp4.text}"
    assert len(resp4.json()) > len(auths)

# --- id=736  name='Payment Authorization Invalid Amount' ---
def test_payment_authorization_invalid_amount():
    order_id = create_test_order()
    payment_req = {
        "orderId": order_id,
        "amount": 150.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"street": "1", "number": "1", "city": "C", "postcode": "1", "country": "US"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is False

# --- id=737  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = create_test_order()
    shipping_req = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"street": "1", "number": "1", "city": "C", "postcode": "1", "country": "US"}
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment["orderId"] == order_id

    resp2 = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    assert resp2.json()["orderId"] == order_id

# --- id=738  name='Cart Operations' ---
def test_cart_operations():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200, f"Expected 200, got {cat_resp.status_code}: {cat_resp.text}"
    items = cat_resp.json()
    item_id = items[0]["id"]

    item_data = {"itemId": item_id, "quantity": 1, "unitPrice": 9.99}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp2 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    assert len(resp2.json()) == 1

    patch_data = {"itemId": item_id, "quantity": 5, "unitPrice": 9.99}
    resp3 = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_data, timeout=10)
    assert resp3.status_code == 202, f"Expected 202, got {resp3.status_code}: {resp3.text}"

    resp4 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp4.status_code == 200, f"Expected 200, got {resp4.status_code}: {resp4.text}"
    assert resp4.json()["quantity"] == 5

    resp5 = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp5.status_code == 202, f"Expected 202, got {resp5.status_code}: {resp5.text}"

    resp6 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp6.status_code == 404, f"Expected 404, got {resp6.status_code}: {resp6.text}"

    resp7 = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp7.status_code == 202, f"Expected 202, got {resp7.status_code}: {resp7.text}"

# --- id=739  name='Cart Merge' ---
def test_cart_merge():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    item_data = {"itemId": item_id, "quantity": 1, "unitPrice": 9.99}
    resp = requests.post(get_url("carts", f"/carts/{session_id}/items"), json=item_data, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 1
    assert resp.json()[0]["itemId"] == item_id

# --- id=740  name='Order Missing Fields' ---
def test_order_missing_fields():
    username = f"user_{uuid.uuid4().hex[:8]}"
    order_req = {
        "customer": f"/customers/{username}"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=741  name='Order Invalid Uri Format' ---
def test_order_invalid_uri_format():
    username = f"user_{uuid.uuid4().hex[:8]}"
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/invalid_format",
        "card": f"/cards/{username}:1234",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=742  name='Order Empty Cart' ---
def test_order_empty_cart():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@example.com", "firstName": "John", "lastName": "Doe"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    address_data = {"street": "123", "number": "1", "city": "A", "postcode": "1", "country": "US", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=address_data, timeout=10)
    address_id = addr_resp.json()["id"]

    card_data = {"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    card_id = card_resp.json()["id"]

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{address_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

# --- id=743  name='User Customer Deletion' ---
def test_user_customer_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "password", "email": f"{username}@test.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] is True

    resp2 = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    assert resp2.json()["status"] is False

# --- id=744  name='Nonexistent Customer' ---
def test_get_nonexistent_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["username"] == username
    assert "firstName" not in resp.json() or not resp.json()["firstName"]

# --- id=745  name='Order Search By Customer' ---
def test_order_search_by_customer():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    addr_resp = requests.post(get_url("user", "/addresses"), json={"street": "1", "number": "1", "city": "A", "postcode": "1", "country": "US", "userID": username}, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_resp = requests.post(get_url("user", "/cards"), json={"longNum": "1234567890123456", "expires": "12/25", "ccv": "123", "userID": username}, timeout=10)
    card_id = card_resp.json()["id"]

    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = cat_resp.json()[0]["id"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    order_resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert order_resp.status_code == 201, f"Expected 201, got {order_resp.status_code}: {order_resp.text}"
    order_id = order_resp.json()["id"]

    search_resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}: {search_resp.text}"
    orders = search_resp.json()["_embedded"]["customerOrders"]
    assert len(orders) >= 1
    assert any(o["id"] == order_id for o in orders)
