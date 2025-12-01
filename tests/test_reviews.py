"""
Тесты эндпоинтов отзывов
"""

import pytest
from fastapi import status


class TestReviews:
    
    def test_create_review(self, client, test_product, auth_headers):
        """Test creating a product review"""
        review_data = {
            "product_id": test_product.id,
            "rating": 5,
            "comment": "Excellent product!"
        }
        
        response = client.post("/reviews", json=review_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_id"] == test_product.id
        assert data["rating"] == review_data["rating"]
        assert data["comment"] == review_data["comment"]
        assert "user" in data
    
    def test_create_review_no_auth(self, client, test_product):
        """Test creating review without authentication"""
        review_data = {
            "product_id": test_product.id,
            "rating": 5,
            "comment": "Great!"
        }
        
        response = client.post("/reviews", json=review_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_review_nonexistent_product(self, client, auth_headers):
        """Test creating review for non-existent product"""
        review_data = {
            "product_id": 99999,
            "rating": 5,
            "comment": "Test"
        }
        
        response = client.post("/reviews", json=review_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_duplicate_review(self, client, test_product, auth_headers):
        """Test creating duplicate review for same product"""
        review_data = {
            "product_id": test_product.id,
            "rating": 5,
            "comment": "First review"
        }
        
        # Create first review
        response1 = client.post("/reviews", json=review_data, headers=auth_headers)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to create another review for same product
        review_data["comment"] = "Second review"
        response2 = client.post("/reviews", json=review_data, headers=auth_headers)
        
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already reviewed" in response2.json()["detail"].lower()
    
    def test_create_review_invalid_rating(self, client, test_product, auth_headers):
        """Test creating review with invalid rating"""
        review_data = {
            "product_id": test_product.id,
            "rating": 6,  # Invalid: should be 1-5
            "comment": "Test"
        }
        
        response = client.post("/reviews", json=review_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_review_without_comment(self, client, test_product, auth_headers):
        """Test creating review without comment"""
        review_data = {
            "product_id": test_product.id,
            "rating": 4
        }
        
        response = client.post("/reviews", json=review_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["rating"] == 4
        assert data["comment"] is None
    
    def test_get_product_reviews(self, client, test_product, auth_headers):
        """Test getting all reviews for a product"""
        # Create a review
        review_data = {
            "product_id": test_product.id,
            "rating": 5,
            "comment": "Great product!"
        }
        client.post("/reviews", json=review_data, headers=auth_headers)
        
        # Get reviews
        response = client.get(f"/reviews/product/{test_product.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1
        assert all(review["product_id"] == test_product.id for review in data["items"])
    
    def test_get_product_reviews_no_auth_required(self, client, test_product):
        """Test that getting product reviews doesn't require auth"""
        response = client.get(f"/reviews/product/{test_product.id}")
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_reviews_nonexistent_product(self, client):
        """Test getting reviews for non-existent product"""
        response = client.get("/reviews/product/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_my_reviews(self, client, test_product, auth_headers):
        """Test getting user's own reviews"""
        # Create reviews
        review_data = {
            "product_id": test_product.id,
            "rating": 5,
            "comment": "My review"
        }
        client.post("/reviews", json=review_data, headers=auth_headers)
        
        # Get my reviews
        response = client.get("/reviews/my", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1
    
    def test_get_my_reviews_no_auth(self, client):
        """Test getting my reviews without authentication"""
        response = client.get("/reviews/my")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_review(self, client, test_product, auth_headers):
        """Test updating a review"""
        # Create review
        review_data = {
            "product_id": test_product.id,
            "rating": 4,
            "comment": "Good product"
        }
        create_response = client.post("/reviews", json=review_data, headers=auth_headers)
        review_id = create_response.json()["id"]
        
        # Update review
        update_data = {
            "rating": 5,
            "comment": "Actually, it's excellent!"
        }
        response = client.put(f"/reviews/{review_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rating"] == update_data["rating"]
        assert data["comment"] == update_data["comment"]
    
    def test_update_review_partial(self, client, test_product, auth_headers):
        """Test partially updating a review"""
        # Create review
        review_data = {
            "product_id": test_product.id,
            "rating": 4,
            "comment": "Good product"
        }
        create_response = client.post("/reviews", json=review_data, headers=auth_headers)
        review_id = create_response.json()["id"]
        
        # Update only rating
        update_data = {"rating": 5}
        response = client.put(f"/reviews/{review_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == "Good product"  # Unchanged
    
    def test_update_nonexistent_review(self, client, auth_headers):
        """Test updating non-existent review"""
        update_data = {"rating": 5}
        response = client.put("/reviews/99999", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_review_no_auth(self, client):
        """Test updating review without authentication"""
        update_data = {"rating": 5}
        response = client.put("/reviews/1", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_review(self, client, test_product, auth_headers):
        """Test deleting a review"""
        # Create review
        review_data = {
            "product_id": test_product.id,
            "rating": 5,
            "comment": "Test review"
        }
        create_response = client.post("/reviews", json=review_data, headers=auth_headers)
        review_id = create_response.json()["id"]
        
        # Delete review
        response = client.delete(f"/reviews/{review_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        get_response = client.get("/reviews/my", headers=auth_headers)
        reviews_data = get_response.json()
        reviews = reviews_data["items"]  # Get items from paginated response
        assert not any(review["id"] == review_id for review in reviews)
    
    def test_delete_nonexistent_review(self, client, auth_headers):
        """Test deleting non-existent review"""
        response = client.delete("/reviews/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_review_no_auth(self, client):
        """Test deleting review without authentication"""
        response = client.delete("/reviews/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_review_isolation_between_users(self, client, test_product, test_user_data):
        """Test that users can only modify their own reviews"""
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
        
        # User 1 creates review
        review_data = {
            "product_id": test_product.id,
            "rating": 5,
            "comment": "User 1's review"
        }
        create_response = client.post("/reviews", json=review_data, headers=headers1)
        review_id = create_response.json()["id"]
        
        # User 2 should not be able to update User 1's review
        update_response = client.put(
            f"/reviews/{review_id}",
            json={"rating": 1, "comment": "Trying to modify"},
            headers=headers2
        )
        assert update_response.status_code == status.HTTP_404_NOT_FOUND
        
        # User 2 should not be able to delete User 1's review
        delete_response = client.delete(f"/reviews/{review_id}", headers=headers2)
        assert delete_response.status_code == status.HTTP_404_NOT_FOUND

