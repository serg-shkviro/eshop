"""
Демонстрационный скрипт для показа функциональности корзины
Убедитесь, что сервер запущен перед выполнением!

Запуск: python scripts/demo_cart.py
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
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_cart_workflow():
    
    print("\nSHOPPING CART DEMO")
    print("=" * 60)
    
    print("\nStep 1: Creating a test user...")
    user_data = {
        "name": "Test Shopper",
        "email": "shopper@test.com",
        "phone": "+1234567890",
        "address": "123 Test St, Test City"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print_response("Create User", response)
    
    if response.status_code == 201:
        user_id = response.json()["id"]
        print(f"\nUser created with ID: {user_id}")
    else:
        print("\nFailed to create user. User might already exist.")
        response = requests.get(f"{BASE_URL}/users/")
        users = response.json()
        if users:
            user_id = users[0]["id"]
            print(f"Using existing user ID: {user_id}")
        else:
            print("No users found. Please check the server.")
            return
    
    print("\n\nStep 2: Fetching available products...")
    response = requests.get(f"{BASE_URL}/products/?limit=5")
    print_response("Get Products", response)
    
    products = response.json()
    if not products:
        print("\nNo products found. Run 'python seed_data.py' first!")
        return
    
    print("\n\nStep 3: Adding product to cart...")
    product_1 = products[0]
    cart_item_1 = {
        "product_id": product_1["id"],
        "quantity": 2
    }
    
    response = requests.post(f"{BASE_URL}/cart/{user_id}/items/", json=cart_item_1)
    print_response(f"Add '{product_1['name']}' (x2) to cart", response)
    
    if len(products) > 1:
        print("\n\nStep 4: Adding another product to cart...")
        product_2 = products[1]
        cart_item_2 = {
            "product_id": product_2["id"],
            "quantity": 1
        }
        
        response = requests.post(f"{BASE_URL}/cart/{user_id}/items/", json=cart_item_2)
        print_response(f"Add '{product_2['name']}' (x1) to cart", response)
    
    print("\n\nStep 5: Viewing cart contents...")
    response = requests.get(f"{BASE_URL}/cart/{user_id}")
    print_response("View Cart", response)
    
    cart_data = response.json()
    print(f"\nCart Total: ${cart_data['total']}")
    print(f"Items in cart: {len(cart_data['items'])}")
    
    if cart_data['items']:
        print("\n\nStep 6: Updating item quantity...")
        first_item = cart_data['items'][0]
        update_data = {"quantity": 3}
        
        response = requests.put(
            f"{BASE_URL}/cart/{user_id}/items/{first_item['id']}",
            json=update_data
        )
        print_response("Update Quantity to 3", response)
        
        response = requests.get(f"{BASE_URL}/cart/{user_id}")
        cart_data = response.json()
        print(f"\nUpdated Cart Total: ${cart_data['total']}")
    
    if len(cart_data['items']) > 1:
        print("\n\nStep 7: Removing an item from cart...")
        item_to_remove = cart_data['items'][1]
        
        response = requests.delete(
            f"{BASE_URL}/cart/{user_id}/items/{item_to_remove['id']}"
        )
        print_response("Remove Item", response)
    
    print("\n\nStep 8: Viewing final cart...")
    response = requests.get(f"{BASE_URL}/cart/{user_id}")
    print_response("Final Cart", response)
    
    cart_data = response.json()
    print(f"\nFinal Cart Total: ${cart_data['total']}")
    print(f"Items remaining: {len(cart_data['items'])}")
    
    print("\n\nStep 9: Creating order from cart...")
    order_data = {
        "shipping_address": "123 Test St, Test City, TC 12345",
        "payment_method": "credit_card",
        "notes": "Please handle with care"
    }
    
    response = requests.post(f"{BASE_URL}/orders/{user_id}", json=order_data)
    print_response("Create Order", response)
    
    if response.status_code == 201:
        order = response.json()
        print(f"\nOrder created successfully!")
        print(f"   Order ID: {order['id']}")
        print(f"   Status: {order['status']}")
        print(f"   Total: ${order['total_amount']}")
        print(f"   Items: {len(order['order_items'])}")
    
    print("\n\nStep 10: Verifying cart is cleared after order...")
    response = requests.get(f"{BASE_URL}/cart/{user_id}")
    cart_data = response.json()
    print(f"Items in cart: {len(cart_data['items'])}")
    print(f"Cart total: ${cart_data['total']}")
    
    print("\n\n" + "="*60)
    print("CART WORKFLOW TEST COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("Server is running!")
            test_cart_workflow()
        else:
            print("Server responded but health check failed")
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server!")
        print("   Make sure the server is running at http://localhost:8000")
        print("   Start it with: docker-compose up  OR  python main.py")

