# Tests generated in iteration 03
# Captured: 2026-06-07T11:27:32
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1390  name='User Register And Login' ---
def test_user_register_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"

    # Register
    register_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=register_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify creation
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Login
    resp_login = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Negative: Register same user
    resp_conflict = requests.post(get_url("user", "/register"), json=register_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=1391  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={
        "username": username, "password": "pwd", "email": f"{username}@ex.com", "firstName": "F", "lastName": "L"
    }, timeout=10)

    # Add Address
    address_payload = {
        "userID": username,
        "number": "123",
        "street": "Main St",
        "city": "Cityville",
        "postcode": "12345",
        "country": "Countryland"
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None, "Expected address ID in response"

    # Verify Address
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json().get("city") == "Cityville"

    # Add Card
    card_payload = {
        "userID": username,
        "longNum": "1234567890123456",
        "expires": "12/25",
        "ccv": "123"
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None, "Expected card ID in response"

    # Verify Card
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"

    # Delete Address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Verify Deletion (Check collection)
    resp_coll = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_coll.status_code == 200, f"Expected 200, got {resp_coll.status_code}: {resp_coll.text}"
    addresses = resp_coll.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses), "Address should be deleted"

# --- id=1392  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    # Get all
    resp_all = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_all.status_code == 200, f"Expected 200, got {resp_all.status_code}: {resp_all.text}"
    items = resp_all.json()
    assert len(items) > 0, "Expected at least one item in catalogue"

    item_id = items[0]["id"]

    # Get specific
    resp_one = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_one.status_code == 200, f"Expected 200, got {resp_one.status_code}: {resp_one.text}"
    assert resp_one.json().get("id") == item_id

    # Negative: Not found
    resp_404 = requests.get(get_url("catalogue", "/catalogue/invalid-id-999"), timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

# --- id=1393  name='Carts Cumulative State And' ---
def test_carts_cumulative_state_and_patch():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    # Add item (quantity 1)
    payload = {"itemId": item_id, "quantity": 1, "unitPrice": 10.5}
    resp_add1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp_add1.status_code == 201, f"Expected 201, got {resp_add1.status_code}: {resp_add1.text}"

    # Verify state
    resp_get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    items = resp_get1.json()
    assert len(items) == 1
    assert items[0]["quantity"] == 1

    # Add same item again (quantity 2) -> Cumulative state
    payload["quantity"] = 2
    resp_add2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp_add2.status_code == 201, f"Expected 201, got {resp_add2.status_code}: {resp_add2.text}"

    # Verify cumulative state (1 + 2 = 3)
    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    items = resp_get2.json()
    assert items[0]["quantity"] == 3

    # Patch item (set quantity to 5)
    payload["quantity"] = 5
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify patched state
    resp_get3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get3.status_code == 200, f"Expected 200, got {resp_get3.status_code}: {resp_get3.text}"
    assert resp_get3.json()["quantity"] == 5

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify deletion
    resp_get4 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get4.status_code == 404, f"Expected 404, got {resp_get4.status_code}: {resp_get4.text}"

# --- id=1394  name='Carts Merge' ---
def test_carts_merge():
    session_id = f"sess_{generate_random_string()}"
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    # Add to session cart
    requests.post(get_url("carts", f"/carts/{session_id}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 5.0}, timeout=10)

    # Merge
    resp_merge = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp_merge.status_code == 202, f"Expected 202, got {resp_merge.status_code}: {resp_merge.text}"

    # Verify merge
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    items = resp_get.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id

    # Negative: Merge non-existent session
    resp_merge_fail = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId=invalid_session"), timeout=10)
    assert resp_merge_fail.status_code == 404, f"Expected 404, got {resp_merge_fail.status_code}: {resp_merge_fail.text}"

# --- id=1395  name='Orders Creation And Payment Decline' ---
def test_orders_creation_and_payment_decline():
    username = f"user_{generate_random_string()}"

    # Setup User
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@ex.com", "firstName": "F", "lastName": "L"}, timeout=10)

    # Setup Address
    addr_resp = requests.post(get_url("user", "/addresses"), json={"userID": username, "number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"}, timeout=10)
    addr_id = addr_resp.json()["id"]

    # Setup Card
    card_resp = requests.post(get_url("user", "/cards"), json={"userID": username, "longNum": "1234567890123456", "expires": "12/25", "ccv": "123"}, timeout=10)
    card_id = card_resp.json()["id"]

    # Setup Cart (Amount <= 100 for success)
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "sock1", "quantity": 1, "unitPrice": 50.0}, timeout=10)

    # Create Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")
    assert order_id is not None

    # Verify Order
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"

    # Negative: Payment declined (Amount > 100)
    # Clear cart and add expensive item
    requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "sock2", "quantity": 1, "unitPrice": 150.0}, timeout=10)

    resp_order_fail = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order_fail.status_code == 406, f"Expected 406, got {resp_order_fail.status_code}: {resp_order_fail.text}"

# --- id=1396  name='Payment Authorization' ---
def test_payment_authorization():
    order_id = f"order_{generate_random_string()}"

    payload = {
        "orderId": order_id,
        "amount": 50.0,
        "customer": {"firstName": "John", "lastName": "Doe"},
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"},
        "card": {"longNum": "1234", "expires": "12/25", "ccv": "123"}
    }

    # Authorize payment
    resp_pay = requests.post(get_url("payment-http", "/payments"), json=payload, timeout=10)
    assert resp_pay.status_code == 200, f"Expected 200, got {resp_pay.status_code}: {resp_pay.text}"
    assert resp_pay.json().get("authorised") is True

    # Verify payment
    resp_get = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    auths = resp_get.json()
    assert len(auths) > 0
    assert auths[0]["orderId"] == order_id

# --- id=1397  name='Shipping Creation' ---
def test_shipping_creation():
    order_id = f"order_{generate_random_string()}"

    payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"number": "1", "street": "S", "city": "C", "postcode": "P", "country": "C"}
    }

    # Create shipment
    resp_ship = requests.post(get_url("shipping-http", "/shipping"), json=payload, timeout=10)
    assert resp_ship.status_code == 200, f"Expected 200, got {resp_ship.status_code}: {resp_ship.text}"
    assert resp_ship.json().get("orderId") == order_id

    # Verify shipment
    resp_get = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("orderId") == order_id
