"""
Тесты функциональности пагинации
"""

import pytest
from fastapi import status


class TestPagination:
    
    def test_products_pagination_default(self, client, test_products):
        """Test products pagination with default parameters"""
        response = client.get("/products/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check response structure
        assert "items" in data
        assert "pagination" in data
        
        # Check pagination metadata
        pagination = data["pagination"]
        assert "total" in pagination
        assert "page" in pagination
        assert "page_size" in pagination
        assert "total_pages" in pagination
        assert "has_next" in pagination
        assert "has_previous" in pagination
        
        # Check default values
        assert pagination["page"] == 1
        assert pagination["page_size"] == 20
        assert pagination["has_previous"] is False
    
    def test_products_pagination_custom_page_size(self, client, test_products):
        """Test products pagination with custom page size"""
        response = client.get("/products/?page=1&page_size=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["items"]) <= 2
        assert data["pagination"]["page_size"] == 2
    
    def test_products_pagination_second_page(self, client, test_products):
        """Test products pagination second page"""
        # Get first page
        response1 = client.get("/products/?page=1&page_size=2")
        data1 = response1.json()
        
        # Get second page
        response2 = client.get("/products/?page=2&page_size=2")
        data2 = response2.json()
        
        assert response2.status_code == status.HTTP_200_OK
        assert data2["pagination"]["page"] == 2
        assert data2["pagination"]["has_previous"] is True
        
        # Items should be different
        if len(data1["items"]) > 0 and len(data2["items"]) > 0:
            assert data1["items"][0]["id"] != data2["items"][0]["id"]
    
    def test_products_pagination_out_of_range(self, client, test_products):
        """Test products pagination with page out of range"""
        response = client.get("/products/?page=999&page_size=20")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should return empty items
        assert len(data["items"]) == 0
        assert data["pagination"]["has_next"] is False
    
    def test_categories_pagination(self, client, test_category):
        """Test categories pagination"""
        response = client.get("/categories/?page=1&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
    
    def test_orders_pagination(self, client, test_product, auth_headers):
        """Test orders pagination"""
        # Create some orders first
        for i in range(3):
            client.post(
                "/cart/items",
                json={"product_id": test_product.id, "quantity": 1},
                headers=auth_headers
            )
            client.post(
                "/orders",
                json={"shipping_address": f"Address {i}", "payment_method": "credit_card"},
                headers=auth_headers
            )
        
        response = client.get("/orders?page=1&page_size=2", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "pagination" in data
        assert len(data["items"]) <= 2
        assert data["pagination"]["total"] >= 3
    
    def test_reviews_pagination(self, client, test_products, auth_headers):
        """Test reviews pagination"""
        # Create reviews for first product
        product = test_products[0]
        client.post(
            "/reviews",
            json={"product_id": product.id, "rating": 5, "comment": "Great!"},
            headers=auth_headers
        )
        
        response = client.get(f"/reviews/product/{product.id}?page=1&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "pagination" in data
    
    def test_my_reviews_pagination(self, client, test_product, auth_headers):
        """Test my reviews pagination"""
        client.post(
            "/reviews",
            json={"product_id": test_product.id, "rating": 5, "comment": "Test"},
            headers=auth_headers
        )
        
        response = client.get("/reviews/my?page=1&page_size=10", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "pagination" in data
    
    def test_pagination_invalid_page(self, client):
        """Test pagination with invalid page number"""
        response = client.get("/products/?page=0")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_pagination_invalid_page_size(self, client):
        """Test pagination with invalid page size"""
        # Page size too large
        response = client.get("/products/?page_size=101")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_pagination_total_pages_calculation(self, client, db):
        """Test total pages calculation"""
        from app.models import Category
        
        # Create exactly 25 categories
        for i in range(25):
            category = Category(name=f"Category {i}", description=f"Description {i}")
            db.add(category)
        db.commit()
        
        # With page_size=10, should have 3 pages
        response = client.get("/categories/?page=1&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["pagination"]["total"] == 25
        assert data["pagination"]["total_pages"] == 3
        assert data["pagination"]["has_next"] is True
        
        # Last page should have has_next=False
        response = client.get("/categories/?page=3&page_size=10")
        data = response.json()
        
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_previous"] is True
        assert len(data["items"]) == 5  # Remaining items
    
    def test_pagination_with_filters(self, client, test_products):
        """Test pagination works with filters"""
        response = client.get("/products/?page=1&page_size=5&in_stock=true")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "pagination" in data
        # All items should have stock > 0
        for item in data["items"]:
            assert item["stock"] > 0

