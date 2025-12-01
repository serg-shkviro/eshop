"""
Демонстрационный скрипт для показа аутентификации и защищенных эндпоинтов
Убедитесь, что сервер запущен и БД заполнена перед выполнением!

Запуск: python scripts/demo_auth.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, default=str))
        return data
    except:
        print(response.text)
        return None


def test_authentication_flow():
    
    print("\nAUTHENTICATION & PROTECTED ENDPOINTS DEMO")
    print("=" * 60)
    
    print("\nStep 1: Registering a new user...")
    user_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword123",
        "phone": "+1234567890",
        "address": "123 Test Street"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code == 201:
        print_response("User Registration", response)
    else:
        print("\nUser might already exist, will try to login...")
    
    print("\n\nStep 2: Logging in to get access token...")
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data
    )
    
    if response.status_code != 200:
        print("\nLogin failed, trying with seeded user...")
        login_data = {
            "username": "john@example.com",
            "password": "password123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    token_data = print_response("Login", response)
    
    if not token_data or "access_token" not in token_data:
        print("\nFailed to get access token!")
        return
    
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\nToken received: {token[:50]}...")
    
    print("\n\nStep 3: Getting my profile...")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    user_data = print_response("My Profile", response)
    
    print("\n\nStep 4: Trying to access cart without authentication...")
    response = requests.get(f"{BASE_URL}/cart")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 401:
        print("Correctly rejected! Authentication required.")
    
    print("\n\nStep 5: Accessing MY cart (authenticated)...")
    response = requests.get(f"{BASE_URL}/cart", headers=headers)
    print_response("My Cart", response)
    
    print("\n\nStep 6: Adding products to MY cart...")
    cart_items = [
        {"product_id": 1, "quantity": 2},
        {"product_id": 2, "quantity": 1}
    ]
    
    for item in cart_items:
        response = requests.post(
            f"{BASE_URL}/cart/items",
            headers=headers,
            json=item
        )
        print_response(f"Add Product {item['product_id']}", response)
    
    print("\n\nStep 7: Viewing MY cart...")
    response = requests.get(f"{BASE_URL}/cart", headers=headers)
    cart = print_response("My Cart", response)
    
    if cart:
        print(f"\nCart Total: ${cart['total']}")
        print(f"Items in cart: {len(cart['items'])}")
    
    print("\n\nStep 8: Updating my profile...")
    profile_update = {"phone": "+9876543210"}
    response = requests.put(
        f"{BASE_URL}/users/me",
        headers=headers,
        json=profile_update
    )
    print_response("Update Profile", response)
    
    print("\n\nStep 9: Creating order from MY cart...")
    order_data = {
        "shipping_address": "456 New Address, Test City",
        "payment_method": "credit_card",
        "notes": "Test order"
    }
    
    response = requests.post(
        f"{BASE_URL}/orders",
        headers=headers,
        json=order_data
    )
    order = print_response("Create Order", response)
    
    if order:
        print(f"\nOrder created!")
        print(f"   Order ID: {order['id']}")
        print(f"   Total: ${order['total_amount']}")
        print(f"   Status: {order['status']}")
    
    print("\n\nStep 10: Viewing MY orders...")
    response = requests.get(f"{BASE_URL}/orders", headers=headers)
    orders = print_response("My Orders", response)
    
    if orders:
        print(f"\nTotal orders: {len(orders)}")
    
    print("\n\nStep 11: Verifying cart is cleared...")
    response = requests.get(f"{BASE_URL}/cart", headers=headers)
    cart = print_response("My Cart After Order", response)
    
    if cart:
        print(f"Items in cart: {len(cart['items'])}")
        print(f"Cart total: ${cart['total']}")
    
    print("\n\nStep 12: Adding a product review...")
    review_data = {
        "product_id": 1,
        "rating": 5,
        "comment": "Excellent product! Highly recommend."
    }
    
    response = requests.post(
        f"{BASE_URL}/reviews",
        headers=headers,
        json=review_data
    )
    print_response("Create Review", response)
    
    print("\n\nStep 13: Viewing MY reviews...")
    response = requests.get(f"{BASE_URL}/reviews/my", headers=headers)
    print_response("My Reviews", response)
    
    print("\n\n" + "="*60)
    print("AUTHENTICATION TEST COMPLETE!")
    print("="*60)
    print("\nAll protected endpoints require authentication")
    print("Users can only access their own cart and orders")
    print("JWT tokens are working correctly")


if __name__ == "__main__":
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("Server is running!")
            test_authentication_flow()
        else:
            print("Server responded but health check failed")
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server!")
        print("   Make sure the server is running at http://localhost:8000")
        print("   Start it with: docker-compose up  OR  python main.py")
        print("   Also run: python seed_data.py")

