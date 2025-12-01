"""
Конфигурация тестов и фикстуры
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "phone": "+1234567890",
        "address": "123 Test Street"
    }


@pytest.fixture
def test_user(db, test_user_data):
    from app.models import User
    
    user = User(
        name=test_user_data["name"],
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        phone=test_user_data["phone"],
        address=test_user_data["address"],
        is_active=1
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_token(client, test_user, test_user_data):
    response = client.post(
        "/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.status_code} - {response.json()}")
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def admin_user(db):
    from app.models import User
    
    user = User(
        name="Admin User",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        phone="+1234567890",
        address="Admin Street",
        is_active=1,
        is_admin=1
    )
    db.add(user)
    db.flush()  # Ensure user is available in the same transaction
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(client, admin_user):
    # Ensure admin_user is committed and visible
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "adminpassword123"
        }
    )
    if response.status_code != 200:
        error_detail = response.json() if response.content else "No response content"
        raise Exception(f"Admin login failed: {response.status_code} - {error_detail}")
    token_data = response.json()
    if "access_token" not in token_data:
        raise Exception(f"Token not in response: {token_data}")
    return token_data["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def test_category(db):
    from app.models import Category
    
    category = Category(
        name="Electronics",
        description="Electronic devices and gadgets"
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def test_product(db, test_category):
    from app.models import Product
    from decimal import Decimal
    
    product = Product(
        name="Test Laptop",
        description="A test laptop",
        price=Decimal("999.99"),
        stock=10,
        category_id=test_category.id,
        is_active=1
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def test_products(db, test_category):
    from app.models import Product
    from decimal import Decimal
    
    products = [
        Product(
            name="Laptop Pro",
            description="High-end laptop",
            price=Decimal("1299.99"),
            stock=5,
            category_id=test_category.id,
            is_active=1
        ),
        Product(
            name="Wireless Mouse",
            description="Ergonomic mouse",
            price=Decimal("29.99"),
            stock=50,
            category_id=test_category.id,
            is_active=1
        ),
        Product(
            name="USB-C Hub",
            description="7-in-1 hub",
            price=Decimal("49.99"),
            stock=0,  # Out of stock
            category_id=test_category.id,
            is_active=1
        ),
    ]
    
    for product in products:
        db.add(product)
    db.commit()
    
    for product in products:
        db.refresh(product)
    
    return products

