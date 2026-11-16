# Tests generated in iteration 04
# Captured: 2026-07-05T02:18:32
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=659  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = f"user_{random_string()}"
    password = "password123"
    email = f"{username}@example.com"

    user_data = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "John",
        "lastName": "Doe"
    }

    # Register user
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify login with Basic Auth
    resp = requests.get(get_url("user", "/login"), auth=(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Conflict: Register same user again
    resp = requests.post(get_url("user", "/register"), json=user_data, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    # Unauthorized: Login with wrong password
    resp = requests.get(get_url("user", "/login"), auth=(username, "wrong_password"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

# --- id=660  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = f"user_{random_string()}"
    user_data = {"username": username, "password": "pwd", "email": f"{username}@test.com"}
    requests.post(get_url("user", "/register"), json=user_data, timeout=10)

    # Add Address
    addr_req = {
        "city": "London", "country": "UK", "number": "10", 
        "postcode": "NW1", "street": "Baker St", "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    assert addr_id is not None

    # Verify Address
    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_data = resp.json()
    assert addr_data["city"] == "London"
    assert addr_data["id"] == addr_id

    # Verify Address in Customer Collection
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert any(a["id"] == addr_id for a in addresses)

    # Add Card
    card_req = {
        "ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None

    # Verify Card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_data = resp.json()
    assert card_data["id"] == card_id
    assert card_data["longNum"].endswith("5678")
    assert "*" in card_data["longNum"]  # Verify masking

    # Verify Card in Customer Collection
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert any(c["id"] == card_id for c in cards)

    # Delete Address
    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify Address Deleted from Collection
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addresses = resp.json().get("_embedded", {}).get("address", [])
    assert not any(a["id"] == addr_id for a in addresses)

    # Delete Card
    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Delete Customer
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    # Verify Idempotent/Observable Deletion of Customer
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

# --- id=661  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()

    if items:
        sock = items[0]
        sock_id = sock["id"]

        resp = requests.get(get_url("catalogue", f"/catalogue/{sock_id}"), timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert resp.json()["id"] == sock_id

        if sock.get("imageUrl") and len(sock["imageUrl"]) > 0:
            img_url = sock["imageUrl"][0]
            img_name = img_url.split("/")[-1]
            resp = requests.get(get_url("catalogue", f"/catalogue/images/{img_name}"), timeout=10)
            assert resp.status_code in [200, 404], f"Expected 200 or 404, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

    # Negative: Not Found
    resp = requests.get(get_url("catalogue", "/catalogue/invalid-id-123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=662  name='Cart Operations' ---
def test_cart_operations():
    customer_id = f"cust_{random_string()}"
    item_id = f"item_{random_string()}"

    # Add Item
    item_req = {"itemId": item_id, "quantity": 2, "unitPrice": 15.5}
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Verify Item in Cart
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert len(items) == 1
    assert items[0]["itemId"] == item_id
    assert items[0]["quantity"] == 2

    # Increment Quantity
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": item_id, "quantity": 3}, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 5

    # Patch Quantity
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json={"itemId": item_id, "quantity": 10}, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["quantity"] == 10

    # Delete Item
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify Item Deleted
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Delete Cart
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Negative: Merge Not Found
    session_id = f"sess_{random_string()}"
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/merge?sessionId={session_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=663  name='End To End Order Workflow' ---
def test_end_to_end_order_workflow():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    addr_req = {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    card_id = card_resp.json()["id"]

    item_id = str(uuid.uuid4())
    cat_resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    if cat_resp.status_code == 200 and len(cat_resp.json()) > 0:
        item_id = cat_resp.json()[0]["id"]

    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": item_id, "quantity": 1, "unitPrice": 10.0}, timeout=10)

    order_req = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }

    # Create Order
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order["id"]

    assert order["customer"]["username"] == username
    assert len(order["items"]) == 1
    assert order["items"][0]["itemId"] == item_id
    assert order["total"] == 10.0

    # Verify Order Retrieval
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["id"] == order_id

    # Verify Order Search
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    orders_list = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o["id"] == order_id for o in orders_list)

    # Verify Payment Authorization
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert len(payments) > 0
    assert payments[0]["orderId"] == order_id
    assert payments[0]["authorised"] is True

    # Verify Shipment
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id

# --- id=664  name='Order Negative Scenarios' ---
def test_order_negative_scenarios():
    username = f"user_{random_string()}"
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd", "email": f"{username}@test.com"}, timeout=10)

    addr_req = {"city": "City", "country": "Country", "number": "1", "postcode": "123", "street": "Street", "userID": username}
    addr_resp = requests.post(get_url("user", "/addresses"), json=addr_req, timeout=10)
    addr_id = addr_resp.json()["id"]

    card_req = {"ccv": "123", "expires": "12/25", "longNum": "1234567812345678", "userID": username}
    card_resp = requests.post(get_url("user", "/cards"), json=card_req, timeout=10)
    card_id = card_resp.json()["id"]

    # 1. Empty Cart Order -> 406
    order_req = {
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "customer": f"/customers/{username}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    # 2. Bad Address URI -> 404
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "item1", "quantity": 1, "unitPrice": 10.0}, timeout=10)
    order_req["address"] = "/addresses/invalid_format"
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # 3. Payment Declined (Amount > 100) -> 406
    requests.post(get_url("carts", f"/carts/{username}/items"), json={"itemId": "expensive_item", "quantity": 1, "unitPrice": 150.0}, timeout=10)
    order_req["address"] = f"/addresses/{addr_id}"  # Restore valid address
    resp = requests.post(get_url("orders", "/orders"), json=order_req, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    # 4. Search Orders Not Found -> 404
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId=nonexistent_{random_string()}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # 5. Get Order Not Found -> 404
    resp = requests.get(get_url("orders", f"/orders/nonexistent_{random_string()}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=665  name='Payment And Shipping Direct' ---
def test_payment_and_shipping_direct():
    order_id = str(uuid.uuid4())

    payment_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "amount": 50.0,
        "card": {"ccv": "123", "expires": "12/25", "longNum": "1234"},
        "customer": {"firstName": "F", "lastName": "L"},
        "orderId": order_id
    }

    # Authorize Payment
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth["orderId"] == order_id
    assert auth["authorised"] is True

    # Verify Authorization Recorded
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 1

    # Duplicate Payment -> Appends, does not replace
    requests.post(get_url("payment-http", "/payments"), json=payment_req, timeout=10)
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 2

    # Boundary/Negative: Amount > 100 -> Declined (200 OK with authorised=false)
    payment_req_declined = payment_req.copy()
    payment_req_declined["amount"] = 150.0
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_req_declined, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["authorised"] is False

    # Verify Declined Authorization Appended
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert len(resp.json()) == 3
    assert resp.json()[-1]["authorised"] is False

    # Create Shipment
    ship_req = {
        "address": {"city": "C", "country": "C", "number": "1", "postcode": "1", "street": "S"},
        "itemCount": 2,
        "orderId": order_id
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=ship_req, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    ship = resp.json()
    assert ship["orderId"] == order_id

    # Verify Shipment Recorded
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["orderId"] == order_id
