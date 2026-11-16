# Tests generated in iteration 09
# Captured: 2026-06-05T22:54:14
# Count:    6
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=735  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)

    # 1. Add Address
    address_payload = {
        "city": "Cityville",
        "country": "Countryland",
        "number": "123",
        "postcode": "12345",
        "street": "Main St",
        "userID": username
    }
    resp_addr = requests.post(get_url("user", "/addresses"), json=address_payload, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Verify Address via GET
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_data = resp_addr_get.json()
    assert addr_data.get("city") == address_payload["city"]
    assert addr_data.get("country") == address_payload["country"]
    assert addr_data.get("number") == address_payload["number"]
    assert addr_data.get("postcode") == address_payload["postcode"]
    assert addr_data.get("street") == address_payload["street"]

    # 2. Add Card
    card_payload = {
        "ccv": "123",
        "expires": "12/25",
        "longNum": "1234567890123456",
        "userID": username
    }
    resp_card = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Verify Card via GET
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_data = resp_card_get.json()
    assert card_data.get("ccv") == card_payload["ccv"]
    assert card_data.get("expires") == card_payload["expires"]
    assert "longNum" in card_data

    # 3. Verify Collections
    resp_cust_addr = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp_cust_addr.status_code == 200, f"Expected 200, got {resp_cust_addr.status_code}: {resp_cust_addr.text}"
    assert len(resp_cust_addr.json().get("_embedded", {}).get("address", [])) >= 1

    resp_cust_card = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp_cust_card.status_code == 200, f"Expected 200, got {resp_cust_card.status_code}: {resp_cust_card.text}"
    assert len(resp_cust_card.json().get("_embedded", {}).get("card", [])) >= 1

# --- id=736  name='Catalogue Listing And Retrieval' ---
def test_catalogue_listing_and_retrieval():
    # 1. List Catalogue
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    items = resp_list.json()
    assert len(items) > 0, "Catalogue is empty"

    item = items[0]
    item_id = item["id"]

    # 2. Get Specific Item
    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_item = resp_get.json()
    assert get_item["id"] == item_id
    assert get_item["name"] == item["name"]
    assert get_item["price"] == item["price"]

    # 3. Get Non-existent Item (Negative)
    resp_404 = requests.get(get_url("catalogue", "/catalogue/invalid-id-9999"), timeout=10)
    assert resp_404.status_code == 404, f"Expected 404, got {resp_404.status_code}: {resp_404.text}"

# --- id=737  name='Cart Item Lifecycle' ---
def test_cart_item_lifecycle():
    customer_id = f"cust_{generate_random_string()}"
    item_id = f"item_{generate_random_string()}"

    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": 15.50
    }

    # 1. Add to cart
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    add_data = resp_add.json()
    assert add_data["itemId"] == item_payload["itemId"]
    assert add_data["quantity"] == item_payload["quantity"]
    assert add_data["unitPrice"] == item_payload["unitPrice"]

    # Verify via GET
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    get_data = resp_get.json()
    assert get_data["itemId"] == item_payload["itemId"]
    assert get_data["quantity"] == item_payload["quantity"]
    assert get_data["unitPrice"] == item_payload["unitPrice"]

    # 2. Update item
    update_payload = {
        "itemId": item_id,
        "quantity": 5,
        "unitPrice": 15.50
    }
    resp_patch = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=update_payload, timeout=10)
    assert resp_patch.status_code == 202, f"Expected 202, got {resp_patch.status_code}: {resp_patch.text}"

    # Verify update via GET
    resp_get_updated = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_updated.status_code == 200, f"Expected 200, got {resp_get_updated.status_code}: {resp_get_updated.text}"
    assert resp_get_updated.json()["quantity"] == 5

    # 3. Delete item
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify delete (Negative)
    resp_get_deleted = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_deleted.status_code == 404, f"Expected 404, got {resp_get_deleted.status_code}: {resp_get_deleted.text}"

# --- id=734  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{generate_random_string()}"
    password = "password123"
    user_payload = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # 1. Register User (Positive)
    resp_reg = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Verify via GET
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    if resp_get.text:
        get_data = resp_get.json()
        assert get_data.get("username") == user_payload["username"]
        assert get_data.get("email") == user_payload["email"]
        assert get_data.get("firstName") == user_payload["firstName"]
        assert get_data.get("lastName") == user_payload["lastName"]
        assert "password" not in get_data or get_data.get("password") != password

    # 2. Login (Positive)
    resp_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

    # 3. Register Duplicate User (Negative)
    resp_conflict = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # 4. Login with Wrong Password (Negative)
    resp_bad_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, "wrongpass"), timeout=10)
    assert resp_bad_login.status_code == 401, f"Expected 401, got {resp_bad_login.status_code}: {resp_bad_login.text}"

# --- id=738  name='Orders E2e Successful Placement' ---
def test_orders_e2e_successful_placement():
    # 1. Setup User
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)

    # 2. Setup Address
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json().get("id")

    # 3. Setup Card
    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    # 4. Setup Cart (Amount <= 100 for successful payment)
    item_id = f"item_{generate_random_string()}"
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 50.00}, timeout=10)

    # 5. Place Order
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
    assert order_id is not None

    # 6. Verify Order via GET
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("payment", {}).get("authorised") is True

    # 7. Verify Payment via GET
    resp_payment = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp_payment.status_code == 200, f"Expected 200, got {resp_payment.status_code}: {resp_payment.text}"
    payments = resp_payment.json()
    assert len(payments) > 0
    assert payments[0].get("authorised") is True
    assert payments[0].get("orderId") == order_id

    # 8. Verify Shipping via GET
    resp_shipping = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp_shipping.status_code == 200, f"Expected 200, got {resp_shipping.status_code}: {resp_shipping.text}"
    assert resp_shipping.json().get("orderId") == order_id

# --- id=739  name='Orders E2e Payment Declined' ---
def test_orders_e2e_payment_declined():
    # 1. Setup User
    username = f"user_{generate_random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com", "firstName": "F", "lastName": "L"}, timeout=10)

    # 2. Setup Address
    addr_resp = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = addr_resp.json().get("id")

    # 3. Setup Card
    card_resp = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = card_resp.json().get("id")

    # 4. Setup Cart (Amount > 100 for declined payment)
    item_id = f"item_{generate_random_string()}"
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 2, "unitPrice": 60.00}, timeout=10)

    # 5. Place Order (Negative - Payment Declined)
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
