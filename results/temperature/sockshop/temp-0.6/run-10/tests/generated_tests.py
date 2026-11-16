# Tests generated in iteration 01
# Captured: 2026-07-05T13:47:46
# Count:    9
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=901  name='User Registration And Login' ---
def test_user_registration_and_login():
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

    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer.get("username") == username
    assert customer.get("firstName") == "Test"
    assert customer.get("email") == f"{username}@example.com"

    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", "/login"), auth=(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

# --- id=902  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": "a@b.c", "firstName": "A", "lastName": "B"
    }, timeout=10)

    addr_payload = {
        "number": "123", "street": "Main St", "city": "City", 
        "postcode": "12345", "country": "Country", "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")

    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("city") == "City"

    card_payload = {
        "longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")

    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_data = resp.json()
    assert "5678" in card_data.get("longNum", "")
    assert "*" in card_data.get("longNum", "")

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses)

    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert not any(c.get("id") == card_id for c in cards)

# --- id=903  name='User Deletion' ---
def test_user_deletion():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": "a@b.c", "firstName": "A", "lastName": "B"
    }, timeout=10)

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

# --- id=904  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 5}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)

    if items:
        item_id = items[0]["id"]
        resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert resp.json().get("id") == item_id

        resp = requests.get(get_url("catalogue", "/catalogue/invalid_item_id_123"), timeout=10)
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

        if items[0].get("imageUrl"):
            image_url = items[0]["imageUrl"][0]
            image_name = image_url.split("/")[-1]
            resp = requests.get(get_url("catalogue", f"/catalogue/images/{image_name}"), timeout=10)
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/catalogue/images/non_existent_image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/catalogue/size"), params={"tags": "brown"}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

# --- id=905  name='Cart Management' ---
def test_cart_management():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    cat_items = resp.json()
    item_id = cat_items[0]["id"]
    unit_price = cat_items[0]["price"]

    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": unit_price}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

    patch_payload = {"itemId": item_id, "quantity": 5, "unitPrice": unit_price}
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=patch_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 5

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 0

# --- id=906  name='Cart Merge' ---
def test_cart_merge():
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 2}, timeout=10)
    items = resp.json()
    if len(items) < 2:
        pytest.skip("Not enough items in catalogue to test merge")
    item1_id = items[0]["id"]
    item2_id = items[1]["id"]

    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item1_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)
    requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": item2_id, "quantity": 1, "unitPrice": 20.0}, timeout=10)

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge"), params={"sessionId": session_id}, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    merged_items = resp.json()
    item_ids = [item["itemId"] for item in merged_items]
    assert item1_id in item_ids
    assert item2_id in item_ids

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge"), params={"sessionId": "invalid_session"}, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=907  name='E2e Order Placement' ---
def test_e2e_order_placement():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": "a@b.c", "firstName": "A", "lastName": "B"
    }, timeout=10)

    addr_payload = {"number": "123", "street": "Main", "city": "City", "postcode": "123", "country": "UK", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp.json().get("id")

    card_payload = {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    cat_items = resp.json()
    item_id = cat_items[0]["id"]
    unit_price = cat_items[0]["price"]

    item_payload = {"itemId": item_id, "quantity": 2, "unitPrice": unit_price}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    order_payload = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None

    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order.get("id") == order_id
    assert fetched_order.get("customer", {}).get("username") == username
    assert fetched_order.get("total") == unit_price * 2

    resp = requests.get(get_url("orders", "/orders/search/customerId"), params={"custId": username}, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in orders)

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) > 0
    assert payments[0].get("orderId") == order_id

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id

# --- id=908  name='Order Placement Negative Cases' ---
def test_order_placement_negative_cases():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": "a@b.c", "firstName": "A", "lastName": "B"
    }, timeout=10)

    addr_payload = {"number": "123", "street": "Main", "city": "City", "postcode": "123", "country": "UK", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp.json().get("id")

    card_payload = {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp.json().get("id")

    order_payload = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    item_id = resp.json()[0]["id"]
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_payload["address"] = "/addresses/invalidformat"
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("orders", "/orders/non_existent_order_id"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=909  name='Payment And Shipping Direct' ---
def test_payment_and_shipping_direct():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": "a@b.c", "firstName": "A", "lastName": "B"
    }, timeout=10)

    addr_payload = {"number": "123", "street": "Main", "city": "City", "postcode": "123", "country": "UK", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp.json().get("id")

    card_payload = {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp.json().get("id")

    resp = requests.get(get_url("catalogue", "/catalogue"), params={"size": 1}, timeout=10)
    item_id = resp.json()[0]["id"]
    unit_price = resp.json()[0]["price"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": unit_price}, timeout=10)

    order_payload = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    order_id = resp.json().get("id")

    payment_payload = {
        "address": {"number": "123", "street": "Main", "city": "City", "postcode": "123", "country": "UK"},
        "amount": 50.0,
        "card": {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123"},
        "customer": {"firstName": "A", "lastName": "B"},
        "orderId": order_id
    }

    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is True

    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) >= 2

    payment_payload["amount"] = 150.0
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("authorised") is False

    shipping_payload = {
        "address": {"number": "123", "street": "Main", "city": "City", "postcode": "123", "country": "UK"},
        "itemCount": 3,
        "orderId": order_id
    }

    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id
    assert "trackingNumber" in shipment

    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("trackingNumber") == shipment.get("trackingNumber")
