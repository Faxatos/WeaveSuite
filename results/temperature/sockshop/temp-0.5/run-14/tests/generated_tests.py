# Tests generated in iteration 14
# Captured: 2026-07-04T19:49:56
# Count:    7
#
# NOTE: this file contains only the test functions, not the
# template (imports, MICROSERVICES dict, get_url helper).
# Prepend the template from WeaveSuite if you want it runnable.

# --- id=550  name='User Registration And Login' ---
def test_user_registration_and_login():
    username = random_string()
    password = random_string()
    email = f"{username}@example.com"

    # 1. Register
    user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "firstName": "Test",
        "lastName": "User"
    }
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Follow-up GET
    resp = requests.get(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer = resp.json()
    assert customer.get("username") == username
    assert customer.get("email") == email
    assert "password" not in customer

    # 2. Login (Basic Auth)
    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, password), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 3. Login Negative (Wrong Password)
    resp = requests.get(get_url("user", "/login"), auth=HTTPBasicAuth(username, "wrongpass"), timeout=10)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # 4. Register Negative (Duplicate)
    resp = requests.post(get_url("user", "/register"), json=user_payload, timeout=10)
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"

    # 5. Delete Customer
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is True

    # Delete again (Idempotency / State Check)
    resp = requests.delete(get_url("user", f"/customers/{username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("status") is False

# --- id=551  name='User Address And Card Management' ---
def test_user_address_and_card_management():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    # Add Address
    addr_payload = {
        "street": "123 Main St",
        "number": "42",
        "city": "Anytown",
        "postcode": "12345",
        "country": "USA",
        "userID": username
    }
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr_id = resp.json().get("id")
    assert addr_id is not None
    assert addr_id.startswith(f"{username}:")

    # GET Address
    resp = requests.get(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addr = resp.json()
    assert addr.get("street") == "123 Main St"

    # GET Customer Addresses
    resp = requests.get(get_url("user", f"/customers/{username}/addresses"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    addrs = resp.json().get("_embedded", {}).get("address", [])
    assert any(a.get("id") == addr_id for a in addrs)

    # Add Card
    card_payload = {
        "longNum": "1234567812345678",
        "expires": "12/25",
        "ccv": "123",
        "userID": username
    }
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card_id = resp.json().get("id")
    assert card_id is not None
    assert card_id.startswith(f"{username}:")

    # GET Card
    resp = requests.get(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    card = resp.json()
    assert card.get("expires") == "12/25"
    assert "12345678" not in card.get("longNum", "")
    assert card.get("longNum", "").endswith("5678")

    # GET Customer Cards
    resp = requests.get(get_url("user", f"/customers/{username}/cards"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cards = resp.json().get("_embedded", {}).get("card", [])
    assert any(c.get("id") == card_id for c in cards)

    # Delete Address
    resp = requests.delete(get_url("user", f"/addresses/{addr_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Delete Card
    resp = requests.delete(get_url("user", f"/cards/{card_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

# --- id=552  name='Catalogue Retrieval' ---
def test_catalogue_retrieval():
    # Get Catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    items = resp.json()
    assert isinstance(items, list)
    if not items:
        pytest.skip("No catalogue items found")

    item_id = items[0]["id"]

    # Get specific item
    resp = requests.get(get_url("catalogue", f"/catalogue/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("id") == item_id

    # Get invalid item
    resp = requests.get(get_url("catalogue", "/catalogue/invalid_id_123"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Get Size
    resp = requests.get(get_url("catalogue", "/catalogue/size"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "size" in resp.json()

    # Get Tags
    resp = requests.get(get_url("catalogue", "/tags"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert "tags" in resp.json()

    # Get non-existent image
    resp = requests.get(get_url("catalogue", "/catalogue/images/non_existent_image.jpg"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=553  name='Carts Management' ---
def test_carts_management():
    customer_id = random_string()

    # Get a real item from catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    assert resp.status_code == 200
    items = resp.json()
    if not items:
        pytest.skip("No catalogue items found")
    item_id = items[0]["id"]
    unit_price = items[0].get("price", 10.0)

    # Add to cart
    item_payload = {
        "itemId": item_id,
        "quantity": 2,
        "unitPrice": unit_price
    }
    resp = requests.post(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # GET cart items
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    cart_items = resp.json()
    assert len(cart_items) >= 1
    assert any(i.get("itemId") == item_id and i.get("quantity") == 2 for i in cart_items)

    # Update item quantity
    item_payload["quantity"] = 5
    resp = requests.patch(get_url("carts", f"/carts/{customer_id}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # GET specific item
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json().get("quantity") == 5

    # Delete item
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

    # Verify deletion
    resp = requests.get(get_url("carts", f"/carts/{customer_id}/items/{item_id}"), timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

    # Delete cart
    resp = requests.delete(get_url("carts", f"/carts/{customer_id}"), timeout=10)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"

# --- id=554  name='Orders End To End Workflow' ---
def test_orders_end_to_end_workflow():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    # Address
    addr_payload = {"street": "123 Main St", "number": "42", "city": "Anytown", "postcode": "12345", "country": "USA", "userID": username}
    resp = requests.post(get_url("user", "/addresses"), json=addr_payload, timeout=10)
    addr_id = resp.json().get("id")

    # Card
    card_payload = {"longNum": "1234567812345678", "expires": "12/25", "ccv": "123", "userID": username}
    resp = requests.post(get_url("user", "/cards"), json=card_payload, timeout=10)
    card_id = resp.json().get("id")

    # Catalogue
    resp = requests.get(get_url("catalogue", "/catalogue"), timeout=10)
    items = resp.json()
    if not items:
        pytest.skip("No catalogue items found")
    item_id = items[0]["id"]
    unit_price = items[0].get("price", 10.0)

    # Cart
    item_payload = {"itemId": item_id, "quantity": 1, "unitPrice": unit_price}
    resp = requests.post(get_url("carts", f"/carts/{username}/items"), json=item_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    # Place Order
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{addr_id}",
        "card": f"/cards/{card_id}",
        "items": f"/carts/{username}/items"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    order = resp.json()
    order_id = order.get("id")
    assert order_id is not None
    assert order.get("customer", {}).get("username") == username

    # GET Order
    resp = requests.get(get_url("orders", f"/orders/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_order = resp.json()
    assert fetched_order.get("id") == order_id

    # GET Payments
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payments = resp.json()
    assert isinstance(payments, list)
    assert len(payments) >= 1
    assert payments[0].get("orderId") == order_id

    # GET Shipping
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id

    # Search Orders
    resp = requests.get(get_url("orders", f"/orders/search/customerId?custId={username}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    customer_orders = resp.json().get("_embedded", {}).get("customerOrders", [])
    assert any(o.get("id") == order_id for o in customer_orders)

# --- id=555  name='Orders Negative Paths' ---
def test_orders_negative_paths():
    username = random_string()
    requests.post(get_url("user", "/register"), json={"username": username, "password": "pwd"}, timeout=10)

    # Missing items (406)
    order_payload = {
        "customer": f"/customers/{username}",
        "address": f"/addresses/{username}:1",
        "card": f"/cards/{username}:5678"
    }
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 406, f"Expected 406, got {resp.status_code}: {resp.text}"

    # Invalid address URI format (404)
    order_payload["items"] = f"/carts/{username}/items"
    order_payload["address"] = "/addresses/invalid_format_no_colon"
    resp = requests.post(get_url("orders", "/orders"), json=order_payload, timeout=10)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"

# --- id=556  name='Payment And Shipping Direct' ---
def test_payment_and_shipping_direct():
    order_id = str(uuid.uuid4())

    # Payment
    payment_payload = {
        "orderId": order_id,
        "amount": 50.0,
        "address": {"street": "123", "number": "1", "city": "C", "postcode": "123", "country": "US"},
        "card": {"longNum": "1234123412341234", "expires": "12/25", "ccv": "123"},
        "customer": {"firstName": "John", "lastName": "Doe"}
    }
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is True

    # Verify Payment
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) >= 1
    assert auths[-1].get("orderId") == order_id

    # Payment Negative (Amount > 100)
    payment_payload["amount"] = 150.0
    resp = requests.post(get_url("payment-http", "/payments"), json=payment_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auth = resp.json()
    assert auth.get("authorised") is False

    # Verify Payment appended
    resp = requests.get(get_url("payment-http", f"/payments/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    auths = resp.json()
    assert len(auths) >= 2
    assert auths[-1].get("authorised") is False

    # Shipping
    shipping_payload = {
        "orderId": order_id,
        "itemCount": 3,
        "address": {"street": "123", "number": "1", "city": "C", "postcode": "123", "country": "US"}
    }
    resp = requests.post(get_url("shipping-http", "/shipping"), json=shipping_payload, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    shipment = resp.json()
    assert shipment.get("orderId") == order_id

    # Verify Shipping
    resp = requests.get(get_url("shipping-http", f"/shipping/{order_id}"), timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    fetched_shipment = resp.json()
    assert fetched_shipment.get("orderId") == order_id
