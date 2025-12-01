"""
Тесты эндпоинтов корзины
"""

import pytest
from fastapi import status


class TestCart:
    
    def test_add_item_to_cart(self, client, test_product, auth_headers):
        """Test adding item to cart"""
        cart_item_data = {
            "product_id": test_product.id,
            "quantity": 2
        }
        
        response = client.post("/cart/items", json=cart_item_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_id"] == test_product.id
        assert data["quantity"] == cart_item_data["quantity"]
        assert "product" in data
    
    def test_add_item_to_cart_no_auth(self, client, test_product):
        """Test adding item to cart without authentication"""
        cart_item_data = {
            "product_id": test_product.id,
            "quantity": 1
        }
        
        response = client.post("/cart/items", json=cart_item_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_add_nonexistent_product_to_cart(self, client, auth_headers):
        """Test adding non-existent product to cart"""
        cart_item_data = {
            "product_id": 99999,
            "quantity": 1
        }
        
        response = client.post("/cart/items", json=cart_item_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_add_item_exceeds_stock(self, client, test_product, auth_headers):
        """Test adding more items than available stock"""
        cart_item_data = {
            "product_id": test_product.id,
            "quantity": test_product.stock + 10  # More than available
        }
        
        response = client.post("/cart/items", json=cart_item_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "stock" in response.json()["detail"].lower()
    
    def test_add_duplicate_item_increases_quantity(self, client, test_product, auth_headers):
        """Test adding same product twice increases quantity"""
        cart_item_data = {
            "product_id": test_product.id,
            "quantity": 2
        }
        
        # Add first time
        response1 = client.post("/cart/items", json=cart_item_data, headers=auth_headers)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Add same product again
        response2 = client.post("/cart/items", json=cart_item_data, headers=auth_headers)
        assert response2.status_code == status.HTTP_201_CREATED
        
        data = response2.json()
        assert data["quantity"] == 4  # 2 + 2
    
    def test_get_cart(self, client, test_product, auth_headers):
        """Test getting cart contents"""
        # Add item to cart first
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 2},
            headers=auth_headers
        )
        
        response = client.get("/cart", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 1
        assert float(data["total"]) == float(test_product.price) * 2
    
    def test_get_empty_cart(self, client, auth_headers):
        """Test getting empty cart"""
        response = client.get("/cart", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["items"] == []
        assert float(data["total"]) == 0.0
    
    def test_get_cart_no_auth(self, client):
        """Test getting cart without authentication"""
        response = client.get("/cart")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_cart_item_quantity(self, client, test_product, auth_headers):
        """Test updating cart item quantity"""
        # Add item to cart
        add_response = client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 2},
            headers=auth_headers
        )
        item_id = add_response.json()["id"]
        
        # Update quantity
        update_data = {"quantity": 5}
        response = client.put(f"/cart/items/{item_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quantity"] == 5
    
    def test_update_cart_item_exceeds_stock(self, client, test_product, auth_headers):
        """Test updating cart item to exceed stock"""
        # Add item to cart
        add_response = client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1},
            headers=auth_headers
        )
        item_id = add_response.json()["id"]
        
        # Try to update to exceed stock
        update_data = {"quantity": test_product.stock + 10}
        response = client.put(f"/cart/items/{item_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_remove_item_from_cart(self, client, test_product, auth_headers):
        """Test removing item from cart"""
        # Add item to cart
        add_response = client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 2},
            headers=auth_headers
        )
        item_id = add_response.json()["id"]
        
        # Remove item
        response = client.delete(f"/cart/items/{item_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify cart is empty
        cart_response = client.get("/cart", headers=auth_headers)
        assert len(cart_response.json()["items"]) == 0
    
    def test_remove_nonexistent_cart_item(self, client, auth_headers):
        """Test removing non-existent cart item"""
        response = client.delete("/cart/items/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_clear_cart(self, client, test_products, auth_headers):
        """Test clearing entire cart"""
        # Add multiple items to cart
        for product in test_products[:2]:
            client.post(
                "/cart/items",
                json={"product_id": product.id, "quantity": 1},
                headers=auth_headers
            )
        
        # Clear cart
        response = client.delete("/cart", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify cart is empty
        cart_response = client.get("/cart", headers=auth_headers)
        assert len(cart_response.json()["items"]) == 0
    
    def test_cart_isolation_between_users(self, client, test_product, db, test_user_data):
        """Test that users can only see their own cart"""
        # Create two users and get their tokens
        user1_data = {**test_user_data, "email": "user1@example.com"}
        user2_data = {**test_user_data, "email": "user2@example.com"}
        
        client.post("/auth/register", json=user1_data)
        client.post("/auth/register", json=user2_data)
        
        # Get tokens
        token1_response = client.post("/auth/login", data={
            "username": user1_data["email"],
            "password": user1_data["password"]
        })
        token1 = token1_response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        token2_response = client.post("/auth/login", data={
            "username": user2_data["email"],
            "password": user2_data["password"]
        })
        token2 = token2_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # User 1 adds item to cart
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 2},
            headers=headers1
        )
        
        # User 2 should have empty cart
        cart_response = client.get("/cart", headers=headers2)
        assert len(cart_response.json()["items"]) == 0

