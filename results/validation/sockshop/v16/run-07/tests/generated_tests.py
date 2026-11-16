# Tests generated in iteration 07
# Captured: 2026-06-07T13:40:39
# Count:    5
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=1422  name='User Registration And Login' ---
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

    # Register user
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Verify user creation via GET
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"

    # Login positive
    resp_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Login negative (invalid credentials)
    resp_login_bad = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, "wrongpass"), timeout=10)
    assert resp_login_bad.status_code == 401, f"Expected 401, got {resp_login_bad.status_code}: {resp_login_bad.text}"

    # Register negative (conflict)
    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=1423  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    # Add Address
    addr_payload = {"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")

    # Verify Address creation
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    assert resp_addr_get.json().get("city") == "London"

    # Add Card
    card_payload = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")

    # Verify Card creation
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    assert resp_card_get.json().get("expires") == "12/25"

    # Verify Collections
    resp_addr_coll = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_addr_coll.status_code == 200, f"Expected 200, got {resp_addr_coll.status_code}: {resp_addr_coll.text}"
    addresses = resp_addr_coll.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addresses)

    # Delete Address
    resp_addr_del = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_del.status_code == 200, f"Expected 200, got {resp_addr_del.status_code}: {resp_addr_del.text}"

    # Verify Address deletion via collection
    resp_addr_coll_after = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    addresses_after = resp_addr_coll_after.json().get("_embedded", {}).get("address", [])
    assert not any(a.get("id") == addr_id for a in addresses_after)

# --- id=1424  name='Carts Cumulative Operations' ---
def test_carts_cumulative_operations():
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Get an item from catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add item (qty 1)
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp_add1 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add1.status_code == 201, f"Expected 201, got {resp_add1.status_code}: {resp_add1.text}"

    # Verify qty 1
    resp_get1 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get1.status_code == 200, f"Expected 200, got {resp_get1.status_code}: {resp_get1.text}"
    assert resp_get1.json().get("quantity") == 1

    # Add item again (qty 2)
    item_payload["quantity"] = 2
    resp_add2 = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add2.status_code == 201, f"Expected 201, got {resp_add2.status_code}: {resp_add2.text}"

    # Verify cumulative qty 3
    resp_get2 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 3

    # Patch item (replace qty to 5)
    item_payload["quantity"] = 5
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify patched qty 5
    resp_get3 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get3.status_code == 200, f"Expected 200, got {resp_get3.status_code}: {resp_get3.text}"
    assert resp_get3.json().get("quantity") == 5

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify deletion (404)
    resp_get4 = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get4.status_code == 404, f"Expected 404, got {resp_get4.status_code}: {resp_get4.text}"

# --- id=1425  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    # Add Address
    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}, timeout=10)
    addr_id = resp_addr.json().get("id")

    # Add Card
    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    # Get Catalogue Item
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp_cat.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add to Cart (ensure total <= 100 for successful payment)
    qty = 1
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": qty, "unitPrice": unit_price}, timeout=10)

    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_data = resp_order.json()
    order_id = order_data.get("id")

    # Verify Order creation
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"

    # Verify Payment Authorization
    resp_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_payment.status_code == 200, f"Expected 200, got {resp_payment.status_code}: {resp_payment.text}"
    payments = resp_payment.json()
    assert len(payments) > 0
    assert payments[0].get("authorised") is True

    # Verify Shipping
    resp_shipping = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_shipping.status_code == 200, f"Expected 200, got {resp_shipping.status_code}: {resp_shipping.text}"
    assert resp_shipping.json().get("orderId") == order_id

# --- id=1426  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "London", "country": "UK", "number": "10", "postcode": "W1", "street": "Baker St", "userID": username}, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp_cat.json()
    item_id = items[0]["id"]
    unit_price = items[0]["price"]

    # Add to Cart (ensure total > 100 for declined payment)
    qty = int(105.0 / unit_price) + 1
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": qty, "unitPrice": unit_price}, timeout=10)

    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
