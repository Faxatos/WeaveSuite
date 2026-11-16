# Tests generated in iteration 06
# Captured: 2026-06-30T12:37:18
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=583  name='Orders Checkout Empty Cart Not Acceptable' ---
def test_orders_checkout_empty_cart_not_acceptable():
    username = generate_random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    # Ensure empty cart
    requests.delete(get_url("carts", f"/carts/{username}"), timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    # Attempt to create order with empty cart (Negative Test)
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"

# --- id=577  name='User Register And Conflict' ---
def test_user_register_and_conflict():
    username = generate_random_string()
    user_data = {
        "username": username,
        "password": "password123",
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register user
    url = get_url("user", "/register")
    resp = requests.post(url, json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify state via GET
    get_url_cust = get_url("user", f"/customers/{username}")
    resp_get = requests.get(get_url_cust, timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("username") == username, f"Expected username {username}"

    # Conflict on repeating registration
    resp_conflict = requests.post(url, json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

# --- id=578  name='User Login Success And Failure' ---
def test_user_login_success_and_failure():
    username = generate_random_string()
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Login success
    login_url = get_url("user", "/login")
    resp_login = requests.get(login_url, auth=(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # Login failure
    resp_bad = requests.get(login_url, auth=(username, "wrongpass"), timeout=10)
    assert resp_bad.status_code == 401, f"Expected 401, got {resp_bad.status_code}: {resp_bad.text}"

# --- id=579  name='User Address And Card Lifecycle' ---
def test_user_address_and_card_lifecycle():
    username = generate_random_string()
    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Add Address
    addr_data = {"city": "Paris", "country": "France", "number": "10", "postcode": "75001", "street": "Rue", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Verify Address GET
    resp_get_addr = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_get_addr.status_code == 200, f"Expected 200, got {resp_get_addr.status_code}: {resp_get_addr.text}"
    assert resp_get_addr.json().get("city") == "Paris"

    # Add Card
    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Verify Card GET
    resp_get_card = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_get_card.status_code == 200, f"Expected 200, got {resp_get_card.status_code}: {resp_get_card.text}"
    assert resp_get_card.json().get("expires") == "12/25"
    assert "*" in resp_get_card.json().get("longNum")

    # Delete Address
    resp_del_addr = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_del_addr.status_code == 200, f"Expected 200, got {resp_del_addr.status_code}: {resp_del_addr.text}"

    # Delete Card
    resp_del_card = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_del_card.status_code == 200, f"Expected 200, got {resp_del_card.status_code}: {resp_del_card.text}"

# --- id=580  name='Catalogue Retrieval And Not Found' ---
def test_catalogue_retrieval_and_not_found():
    # Get tags
    resp_tags = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp_tags.status_code == 200, f"Expected 200, got {resp_tags.status_code}: {resp_tags.text}"

    # Get catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_cat.status_code == 200, f"Expected 200, got {resp_cat.status_code}: {resp_cat.text}"
    items = resp_cat.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    # Get specific item
    resp_item = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_item.status_code == 200, f"Expected 200, got {resp_item.status_code}: {resp_item.text}"
    assert resp_item.json().get("id") == item_id

    # Get invalid item (Negative Test)
    resp_invalid = requests.get(get_url("catalogue", "/catalogue/invalid-id-xyz"), timeout=10)
    assert resp_invalid.status_code == 404, f"Expected 404, got {resp_invalid.status_code}: {resp_invalid.text}"

# --- id=581  name='Carts Item Lifecycle' ---
def test_carts_item_lifecycle():
    username = generate_random_string()

    # Get real item from catalogue
    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item_id = resp_cat.json()[0]["id"]

    # Add to cart
    item_data = {"itemId": item_id, "quantity": 1, "unitPrice": 10.5}
    resp_add = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"

    # Verify add
    resp_get = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 1

    # Update cart
    item_data["quantity"] = 5
    resp_patch = requests.patch(get_url("carts", f"/carts/{username}/items"), json=item_data, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify update
    resp_get2 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get2.status_code == 200, f"Expected 200, got {resp_get2.status_code}: {resp_get2.text}"
    assert resp_get2.json().get("quantity") == 5

    # Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify delete (Negative Test)
    resp_get3 = requests.get(get_url("carts", f"/carts/{username}/items/{item_id}"), timeout=10)
    assert resp_get3.status_code == 404, f"Expected 404, got {resp_get3.status_code}: {resp_get3.text}"

# --- id=582  name='Orders Checkout E2e Workflow' ---
def test_orders_checkout_e2e_workflow():
    username = generate_random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "F", "lastName": "L"}, timeout=10)

    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = resp_addr.json().get("id")

    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json().get("id")

    resp_cat = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = resp_cat.json()[0]
    item_id = item["id"]
    price = item["price"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 2, "unitPrice": price}, timeout=10)

    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }

    # Create Order
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"

    order = resp_order.json()
    order_id = order.get("id")
    assert order_id is not None
    assert float(order.get("total")) == float(2 * price)
    assert order.get("status") in ["CREATED", "PAID", "SHIPPED", "PAYMENT_FAILED", "SHIPMENT_FAILED"]

    # Follow up on order
    resp_get_order = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_get_order.status_code == 200, f"Expected 200, got {resp_get_order.status_code}: {resp_get_order.text}"
    assert resp_get_order.json().get("id") == order_id

    # Follow up on payment authorization
    resp_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_payment.status_code == 200, f"Expected 200, got {resp_payment.status_code}: {resp_payment.text}"
    payments = resp_payment.json()
    assert isinstance(payments, list) and len(payments) > 0
    assert payments[0].get("orderId") == order_id

    # Follow up on shipping
    resp_shipping = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_shipping.status_code == 200, f"Expected 200, got {resp_shipping.status_code}: {resp_shipping.text}"
    assert resp_shipping.json().get("orderId") == order_id
