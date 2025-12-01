"""
Тесты эндпоинтов заказов
"""

import pytest
from fastapi import status
from decimal import Decimal


class TestOrders:
    
    def test_create_order_from_cart(self, client, test_product, auth_headers):
        """Test creating order from cart"""
        # Add item to cart
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 2},
            headers=auth_headers
        )
        
        # Create order
        order_data = {
            "shipping_address": "123 Test St, Test City, TC 12345",
            "payment_method": "credit_card",
            "notes": "Please handle with care"
        }
        
        response = client.post("/orders", json=order_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["shipping_address"] == order_data["shipping_address"]
        assert data["payment_method"] == order_data["payment_method"]
        assert data["status"] == "pending"
        assert "order_items" in data
        assert len(data["order_items"]) == 1
        assert float(data["total_amount"]) == float(test_product.price) * 2
    
    def test_create_order_no_auth(self, client):
        """Test creating order without authentication"""
        order_data = {
            "shipping_address": "123 Test St",
            "payment_method": "credit_card"
        }
        
        response = client.post("/orders", json=order_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_order_empty_cart(self, client, auth_headers):
        """Test creating order with empty cart"""
        order_data = {
            "shipping_address": "123 Test St",
            "payment_method": "credit_card"
        }
        
        response = client.post("/orders", json=order_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "empty" in response.json()["detail"].lower()
    
    def test_create_order_insufficient_stock(self, client, auth_headers, db):
        """Test creating order when stock is insufficient"""
        from app.models import Product
        from decimal import Decimal
        
        # Create product with limited stock
        product = Product(
            name="Limited Product",
            price=Decimal("99.99"),
            stock=1,
            is_active=1
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Try to add more than available
        client.post(
            "/cart/items",
            json={"product_id": product.id, "quantity": 1},
            headers=auth_headers
        )
        
        # Reduce stock to 0
        product.stock = 0
        db.commit()
        
        # Try to create order
        order_data = {
            "shipping_address": "123 Test St",
            "payment_method": "credit_card"
        }
        
        response = client.post("/orders", json=order_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "stock" in response.json()["detail"].lower()
    
    def test_order_clears_cart(self, client, test_product, auth_headers):
        """Test that creating order clears the cart"""
        # Add item to cart
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1},
            headers=auth_headers
        )
        
        # Create order
        order_data = {
            "shipping_address": "123 Test St",
            "payment_method": "credit_card"
        }
        client.post("/orders", json=order_data, headers=auth_headers)
        
        # Check cart is empty
        cart_response = client.get("/cart", headers=auth_headers)
        assert len(cart_response.json()["items"]) == 0
    
    def test_order_reduces_stock(self, client, test_product, auth_headers, db):
        """Test that creating order reduces product stock"""
        initial_stock = test_product.stock
        quantity = 2
        
        # Add item to cart
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": quantity},
            headers=auth_headers
        )
        
        # Create order
        order_data = {
            "shipping_address": "123 Test St",
            "payment_method": "credit_card"
        }
        client.post("/orders", json=order_data, headers=auth_headers)
        
        # Check stock is reduced
        db.refresh(test_product)
        assert test_product.stock == initial_stock - quantity
    
    def test_get_my_orders(self, client, test_product, auth_headers):
        """Test getting user's orders"""
        # Create an order first
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1},
            headers=auth_headers
        )
        client.post(
            "/orders",
            json={"shipping_address": "123 Test St", "payment_method": "credit_card"},
            headers=auth_headers
        )
        
        # Get orders
        response = client.get("/orders", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1
        # Verify basic order fields exist
        order = data["items"][0]
        assert "id" in order
        assert "status" in order
        assert "total_amount" in order
        # order_items should be present (may be empty list if no items)
        assert "order_items" in order
        assert isinstance(order["order_items"], list)
    
    def test_get_orders_no_auth(self, client):
        """Test getting orders without authentication"""
        response = client.get("/orders")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_specific_order(self, client, test_product, auth_headers):
        """Test getting specific order details"""
        # Create an order
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1},
            headers=auth_headers
        )
        order_response = client.post(
            "/orders",
            json={"shipping_address": "123 Test St", "payment_method": "credit_card"},
            headers=auth_headers
        )
        order_id = order_response.json()["id"]
        
        # Get specific order
        response = client.get(f"/orders/{order_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == order_id
        assert "order_items" in data
    
    def test_get_nonexistent_order(self, client, auth_headers):
        """Test getting non-existent order"""
        response = client.get("/orders/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_order_status(self, client, test_product, auth_headers):
        """Test updating order status"""
        # Create an order
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1},
            headers=auth_headers
        )
        order_response = client.post(
            "/orders",
            json={"shipping_address": "123 Test St", "payment_method": "credit_card"},
            headers=auth_headers
        )
        order_id = order_response.json()["id"]
        
        # Update status
        update_data = {"status": "confirmed"}
        response = client.put(f"/orders/{order_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "confirmed"
    
    def test_update_order_invalid_status(self, client, test_product, auth_headers):
        """Test updating order with invalid status"""
        # Create an order
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1},
            headers=auth_headers
        )
        order_response = client.post(
            "/orders",
            json={"shipping_address": "123 Test St", "payment_method": "credit_card"},
            headers=auth_headers
        )
        order_id = order_response.json()["id"]
        
        # Try invalid status
        update_data = {"status": "invalid_status"}
        response = client.put(f"/orders/{order_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_order_isolation_between_users(self, client, test_product, test_user_data):
        """Test that users can only see their own orders"""
        # Create two users
        user1_data = {**test_user_data, "email": "user1@example.com"}
        user2_data = {**test_user_data, "email": "user2@example.com"}
        
        client.post("/auth/register", json=user1_data)
        client.post("/auth/register", json=user2_data)
        
        # Get tokens
        token1_response = client.post("/auth/login", data={
            "username": user1_data["email"],
            "password": user1_data["password"]
        })
        headers1 = {"Authorization": f"Bearer {token1_response.json()['access_token']}"}
        
        token2_response = client.post("/auth/login", data={
            "username": user2_data["email"],
            "password": user2_data["password"]
        })
        headers2 = {"Authorization": f"Bearer {token2_response.json()['access_token']}"}
        
        # User 1 creates order
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1},
            headers=headers1
        )
        order_response = client.post(
            "/orders",
            json={"shipping_address": "123 Test St", "payment_method": "credit_card"},
            headers=headers1
        )
        order_id = order_response.json()["id"]
        
        # User 2 should not see User 1's order
        response = client.get(f"/orders/{order_id}", headers=headers2)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # User 2 should have no orders
        orders_response = client.get("/orders", headers=headers2)
        orders_data = orders_response.json()
        assert "items" in orders_data
        assert len(orders_data["items"]) == 0

