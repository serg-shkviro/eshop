"""
Тесты эндпоинтов товаров и категорий
"""

import pytest
from fastapi import status
from decimal import Decimal


class TestCategories:
    
    def test_create_category(self, client, admin_headers):
        """Test creating a category"""
        category_data = {
            "name": "Books",
            "description": "Books and publications"
        }
        
        response = client.post("/categories/", json=category_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["description"] == category_data["description"]
        assert "id" in data
    
    def test_create_duplicate_category(self, client, test_category, admin_headers):
        """Test creating category with duplicate name"""
        category_data = {
            "name": test_category.name,
            "description": "Different description"
        }
        
        response = client.post("/categories/", json=category_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_all_categories(self, client, test_category):
        """Test getting all categories"""
        response = client.get("/categories/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert len(data["items"]) >= 1
        assert any(cat["id"] == test_category.id for cat in data["items"])
    
    def test_get_category_by_id(self, client, test_category):
        """Test getting specific category"""
        response = client.get(f"/categories/{test_category.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_category.id
        assert data["name"] == test_category.name
    
    def test_get_nonexistent_category(self, client):
        """Test getting non-existent category"""
        response = client.get("/categories/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_category(self, client, test_category, admin_headers):
        """Test updating a category"""
        update_data = {
            "name": "Updated Electronics",
            "description": "Updated description"
        }
        
        response = client.put(f"/categories/{test_category.id}", json=update_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
    
    def test_delete_category(self, client, test_category, admin_headers):
        """Test deleting a category"""
        response = client.delete(f"/categories/{test_category.id}", headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        get_response = client.get(f"/categories/{test_category.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestProducts:
    
    def test_create_product(self, client, test_category, admin_headers):
        """Test creating a product"""
        product_data = {
            "name": "New Laptop",
            "description": "Brand new laptop",
            "price": 1299.99,
            "stock": 15,
            "category_id": test_category.id,
            "image_url": "https://example.com/laptop.jpg",
            "is_active": 1
        }
        
        response = client.post("/products/", json=product_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == product_data["name"]
        assert float(data["price"]) == product_data["price"]
        assert data["stock"] == product_data["stock"]
        assert data["category_id"] == test_category.id
    
    def test_create_product_invalid_category(self, client, admin_headers):
        """Test creating product with non-existent category"""
        product_data = {
            "name": "Test Product",
            "price": 99.99,
            "stock": 10,
            "category_id": 99999  # Non-existent
        }
        
        response = client.post("/products/", json=product_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_all_products(self, client, test_product):
        """Test getting all products"""
        response = client.get("/products/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert len(data["items"]) >= 1
        assert any(prod["id"] == test_product.id for prod in data["items"])
    
    def test_get_products_with_filters(self, client, test_products):
        """Test getting products with filters"""
        # Test search filter
        response = client.get("/products/?search=laptop")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 1
        assert all("laptop" in prod["name"].lower() for prod in data["items"])
        
        # Test price range filter
        response = client.get("/products/?min_price=50&max_price=100")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for prod in data["items"]:
            price = float(prod["price"])
            assert 50 <= price <= 100
        
        # Test in_stock filter
        response = client.get("/products/?in_stock=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(prod["stock"] > 0 for prod in data["items"])
    
    def test_get_product_by_id(self, client, test_product):
        """Test getting specific product"""
        response = client.get(f"/products/{test_product.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == test_product.name
    
    def test_update_product(self, client, test_product, admin_headers):
        """Test updating a product"""
        update_data = {
            "name": "Updated Laptop",
            "price": 899.99,
            "stock": 20
        }
        
        response = client.put(f"/products/{test_product.id}", json=update_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert float(data["price"]) == update_data["price"]
        assert data["stock"] == update_data["stock"]
    
    def test_delete_product(self, client, test_product, admin_headers):
        """Test deleting a product"""
        response = client.delete(f"/products/{test_product.id}", headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        get_response = client.get(f"/products/{test_product.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_product_in_order(self, client, test_product, test_user, auth_headers, admin_headers):
        """Test that product in order cannot be deleted"""
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1},
            headers=auth_headers
        )

        order_data = {
            "shipping_address": "123 Test St, Test City, TC 12345",
            "payment_method": "credit_card"
        }
        order_response = client.post("/orders", json=order_data, headers=auth_headers)
        assert order_response.status_code == status.HTTP_201_CREATED

        response = client.delete(f"/products/{test_product.id}", headers=admin_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "order" in response.json()["detail"].lower()
        assert "cannot delete" in response.json()["detail"].lower()

