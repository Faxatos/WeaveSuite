# Tests generated in iteration 06
# Captured: 2026-06-05T21:07:16
# Count:    8
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=701  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register User
    resp_reg = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Verify User Creation via GET
    resp_get = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    user_resp = resp_get.json()
    assert user_resp.get("username") == username
    assert user_resp.get("email") == user_data["email"]
    assert user_resp.get("firstName") == user_data["firstName"]
    assert user_resp.get("lastName") == user_data["lastName"]
    assert "password" not in user_resp or user_resp["password"] != password

    # Login User
    resp_login = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}: {resp_login.text}"

# --- id=702  name='User Registration Conflict And Unauthorized' ---
def test_user_registration_conflict_and_unauthorized():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Register User
    resp_reg = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_reg.status_code == 200, f"Expected 200, got {resp_reg.status_code}: {resp_reg.text}"

    # Negative: Register same user again
    resp_conflict = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp_conflict.status_code == 409, f"Expected 409, got {resp_conflict.status_code}: {resp_conflict.text}"

    # Negative: Login with wrong password
    resp_unauth = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, "wrongpassword"), timeout=10)
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}: {resp_unauth.text}"

# --- id=703  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{uuid.uuid4().hex[:8]}"
    user_data = {"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Add Address
    addr_data = {"city": "Cityville", "country": "Countryland", "number": "42", "postcode": "12345", "street": "Main St", "userID": username}
    resp_addr = requests.post(get_url("user", "/addresses"), json=addr_data, timeout=10)
    assert resp_addr.status_code == 200, f"Expected 200, got {resp_addr.status_code}: {resp_addr.text}"
    addr_id = resp_addr.json().get("id")
    assert addr_id is not None

    # Verify Address via GET
    resp_addr_get = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp_addr_get.status_code == 200, f"Expected 200, got {resp_addr_get.status_code}: {resp_addr_get.text}"
    addr_resp = resp_addr_get.json()
    assert addr_resp.get("city") == addr_data["city"]
    assert addr_resp.get("country") == addr_data["country"]
    assert addr_resp.get("number") == addr_data["number"]
    assert addr_resp.get("postcode") == addr_data["postcode"]
    assert addr_resp.get("street") == addr_data["street"]

    # Add Card
    card_data = {"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}
    resp_card = requests.post(get_url("user", "/cards"), json=card_data, timeout=10)
    assert resp_card.status_code == 200, f"Expected 200, got {resp_card.status_code}: {resp_card.text}"
    card_id = resp_card.json().get("id")
    assert card_id is not None

    # Verify Card via GET
    resp_card_get = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp_card_get.status_code == 200, f"Expected 200, got {resp_card_get.status_code}: {resp_card_get.text}"
    card_resp = resp_card_get.json()
    assert card_resp.get("expires") == card_data["expires"]
    assert card_resp.get("ccv") == card_data["ccv"]
    assert card_resp.get("longNum") != card_data["longNum"]  # Should be masked

# --- id=704  name='Catalogue Listing And Retrieval' ---
def test_catalogue_listing_and_retrieval():
    # List Catalogue
    resp_list = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp_list.status_code == 200, f"Expected 200, got {resp_list.status_code}: {resp_list.text}"
    items = resp_list.json()
    assert len(items) > 0
    item_id = items[0]["id"]

    # Get Specific Item
    resp_get = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("id") == item_id

# --- id=705  name='Catalogue Not Found' ---
def test_catalogue_not_found():
    # Negative: Get non-existent item
    resp_get = requests.get(get_url("catalogue", "/catalogue/invalid-id-999999"), timeout=10)
    assert resp_get.status_code == 404, f"Expected 404, got {resp_get.status_code}: {resp_get.text}"

# --- id=706  name='Carts Management' ---
def test_carts_management():
    # Get a valid catalogue item
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert cat_resp.status_code == 200
    item = cat_resp.json()[0]
    item_id = item["id"]
    price = item["price"]

    customer_id = f"cust_{uuid.uuid4().hex[:8]}"

    # Add Item to Cart
    item_data = {"itemId": item_id, "quantity": 2, "unitPrice": price}
    resp_add = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_data, timeout=10)
    assert resp_add.status_code == 201, f"Expected 201, got {resp_add.status_code}: {resp_add.text}"
    assert resp_add.json().get("itemId") == item_id
    assert resp_add.json().get("quantity") == 2

    # Verify Item in Cart via GET
    resp_get = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get.status_code == 200, f"Expected 200, got {resp_get.status_code}: {resp_get.text}"
    assert resp_get.json().get("quantity") == 2
    assert resp_get.json().get("unitPrice") == price

    # Delete Item from Cart
    resp_del = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_del.status_code == 202, f"Expected 202, got {resp_del.status_code}: {resp_del.text}"

    # Verify Deletion via GET
    resp_get_del = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp_get_del.status_code == 404, f"Expected 404, got {resp_get_del.status_code}: {resp_get_del.text}"

# --- id=707  name='Orders Successful Placement' ---
def test_orders_successful_placement():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    # 2. Add Address
    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = resp_addr.json()["id"]

    # 3. Add Card
    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json()["id"]

    # 4. Get Catalogue Item (ensure price is low enough for payment <= 100)
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = next((i for i in cat_resp.json() if i["price"] <= 50), cat_resp.json()[0])
    item_id = item["id"]
    price = item["price"]

    # 5. Add to Cart
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": price}, timeout=10)

    # 6. Place Order
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 201, f"Expected 201, got {resp_order.status_code}: {resp_order.text}"
    order_id = resp_order.json().get("id")
    assert order_id is not None
    assert resp_order.json().get("payment", {}).get("authorised") is True

    # 7. Verify Order via GET
    resp_order_get = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp_order_get.status_code == 200, f"Expected 200, got {resp_order_get.status_code}: {resp_order_get.text}"
    assert resp_order_get.json().get("id") == order_id
    assert resp_order_get.json().get("payment", {}).get("authorised") is True

# --- id=708  name='Orders Payment Declined' ---
def test_orders_payment_declined():
    # 1. Register User
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": "a@b.com", "firstName": "A", "lastName": "B"}, timeout=10)

    # 2. Add Address & Card
    resp_addr = requests.post(get_url("user", "/addresses"), json={"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S", "userID": username}, timeout=10)
    addr_id = resp_addr.json()["id"]
    resp_card = requests.post(get_url("user", "/cards"), json={"ccv": "123", "expires": "12/25", "longNum": "1234567890123456", "userID": username}, timeout=10)
    card_id = resp_card.json()["id"]

    # 3. Get Catalogue Item
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    item = cat_resp.json()[0]
    item_id = item["id"]
    price = item["price"]

    # 4. Add to Cart with high quantity to exceed 100.00
    qty = int(150 / price) + 1
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": qty, "unitPrice": price}, timeout=10)

    # 5. Place Order -> Expect 406 Not Acceptable due to payment > 100.00
    order_req = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp_order = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp_order.status_code == 406, f"Expected 406, got {resp_order.status_code}: {resp_order.text}"
