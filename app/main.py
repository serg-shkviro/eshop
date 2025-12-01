from fastapi import FastAPI, Depends, HTTPException, Query, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from decimal import Decimal
from datetime import timedelta
import uvicorn
from pathlib import Path
from contextlib import asynccontextmanager

from app.database import get_db, engine
from app.models import Base, User, Category, Product, CartItem, Order, OrderItem, Review, OrderStatus
from app.schemas import (
    PaginationParams, UserRegister, Token,
    UserUpdate, UserResponse, PasswordChange,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse,
    OrderCreate, OrderUpdate, OrderResponse,
    ReviewCreate, ReviewUpdate, ReviewResponse,
    AdminUserUpdate
)
from app.utils import paginate, create_paginated_response
from app.auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_user, get_current_active_user, get_current_admin_user
)
from app.config import settings

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создает первого администратора из переменных окружения при запуске"""
    db = next(get_db())
    try:
        admin_exists = db.query(User).filter(User.is_admin == 1).first()
        
        if not admin_exists and settings.FIRST_ADMIN_EMAIL and settings.FIRST_ADMIN_PASSWORD:
            existing_user = db.query(User).filter(User.email == settings.FIRST_ADMIN_EMAIL).first()
            
            if not existing_user:
                admin_name = settings.FIRST_ADMIN_NAME or "Administrator"
                new_admin = User(
                    email=settings.FIRST_ADMIN_EMAIL,
                    name=admin_name,
                    hashed_password=get_password_hash(settings.FIRST_ADMIN_PASSWORD),
                    is_admin=1,
                )
                db.add(new_admin)
                db.commit()
                print(f"Создан первый администратор: {settings.FIRST_ADMIN_EMAIL}")
            else:
                existing_user.is_admin = 1
                db.commit()
                print(f"Существующий пользователь повышен до администратора: {settings.FIRST_ADMIN_EMAIL}")
        elif admin_exists:
            print("ℹАдминистраторы уже существуют, пропускаем создание первого администратора")
        elif not settings.FIRST_ADMIN_EMAIL:
            print("ℹFIRST_ADMIN_EMAIL не установлен, пропускаем создание первого администратора")
    except Exception as e:
        print(f"Ошибка при создании первого администратора: {e}")
    finally:
        db.close()
    
    yield


app = FastAPI(
    lifespan=lifespan,
    title="E-Commerce API",
    description="A secure e-commerce API with authentication, product management, cart, orders, and reviews",
    version="3.0.0"
)

cors_origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Корневой эндпоинт"""
    return {
        "message": "Welcome to the E-Commerce API",
        "status": "running",
        "version": "3.0.0",
        "docs": "/docs",
        "authentication": "enabled"
    }


@app.get("/health")
def health_check():
    """Эндпоинт проверки состояния"""
    return {"status": "healthy"}


@app.post("/auth/register", response_model=UserResponse, status_code=201, tags=["Authentication"])
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_dict = user_data.model_dump()
    user_dict['hashed_password'] = get_password_hash(user_dict.pop('password'))
    
    new_user = User(**user_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/login", response_model=Token, tags=["Authentication"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Вход и получение токена доступа"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@app.get("/users/me", response_model=UserResponse, tags=["Users"])
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Получить мой профиль"""
    return current_user


@app.put("/users/me", response_model=UserResponse, tags=["Users"])
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновить мой профиль"""
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@app.post("/users/me/change-password", tags=["Users"])
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Изменить пароль пользователя (требуется аутентификация)"""
    from app.auth import verify_password, get_password_hash
    
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@app.get("/users", tags=["Users"])
def get_users(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Элементов на странице"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить всех пользователей с пагинацией (только администраторы)"""
    pagination = PaginationParams(page=page, page_size=page_size)
    query = db.query(User).order_by(User.created_at.desc())
    
    items, meta = paginate(query, pagination)
    
    return create_paginated_response(items, meta)


@app.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Обновить пользователя (только администраторы)"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    if current_user.id == user_id and 'is_admin' in update_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot change your own admin status"
        )
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@app.post("/categories/", response_model=CategoryResponse, status_code=201, tags=["Categories"])
def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Создать новую категорию товаров (только администраторы)"""
    db_category = db.query(Category).filter(Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    new_category = Category(**category.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@app.get("/categories/", tags=["Categories"])
def get_categories(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Элементов на странице"),
    db: Session = Depends(get_db)
):
    """Получить все категории с пагинацией (публичный)"""
    pagination = PaginationParams(page=page, page_size=page_size)
    query = db.query(Category)
    
    items, meta = paginate(query, pagination)
    
    return create_paginated_response(items, meta)


@app.get("/categories/{category_id}", response_model=CategoryResponse, tags=["Categories"])
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Получить конкретную категорию по ID (публичный)"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.put("/categories/{category_id}", response_model=CategoryResponse, tags=["Categories"])
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Обновить категорию (только администраторы)"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category


@app.delete("/categories/{category_id}", tags=["Categories"])
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Удалить категорию (только администраторы)"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}


@app.post("/products/", response_model=ProductResponse, status_code=201, tags=["Products"])
def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Создать новый товар (только администраторы)"""
    if product.category_id:
        category = db.query(Category).filter(Category.id == product.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


async def get_optional_admin_user(
    token: Optional[HTTPAuthorizationCredentials] = Security(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Получает администратора если токен предоставлен и валиден, иначе None"""
    if not token:
        return None
    try:
        from app.auth import get_user_by_email
        from jose import jwt
        from app.config import settings
        
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email:
            user = get_user_by_email(db, email=email)
            if user and user.is_admin == 1 and user.is_active == 1:
                return user
    except:
        pass
    return None

@app.get("/products/", tags=["Products"])
async def get_products(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Элементов на странице"),
    category_id: Optional[int] = Query(None, description="Фильтр по ID категории"),
    search: Optional[str] = Query(None, description="Поиск в названиях товаров"),
    min_price: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    in_stock: Optional[bool] = Query(None, description="Фильтр по наличию на складе"),
    include_inactive: Optional[bool] = Query(None, description="Включить неактивные товары (только для администраторов)"),
    admin_user: Optional[User] = Depends(get_optional_admin_user),
    db: Session = Depends(get_db)
):
    """Получить все товары с пагинацией и фильтрами"""
    pagination = PaginationParams(page=page, page_size=page_size)
    query = db.query(Product).options(joinedload(Product.category))
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
    
    if in_stock:
        query = query.filter(Product.stock > 0)
    
    if include_inactive and admin_user:
        pass
    else:
        query = query.filter(Product.is_active == 1)
    
    query = query.order_by(Product.id.desc())
    
    items, meta = paginate(query, pagination)
    
    return create_paginated_response(items, meta)


@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Получить конкретный товар по ID (публичный)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Обновить товар (только администраторы)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.model_dump(exclude_unset=True)
    
    if 'category_id' in update_data and update_data['category_id']:
        category = db.query(Category).filter(Category.id == update_data['category_id']).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}", tags=["Products"])
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Удалить товар (только администраторы)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    order_items_count = db.query(OrderItem).filter(OrderItem.product_id == product_id).count()
    if order_items_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete product: it is used in {order_items_count} order(s). Deactivate it instead."
        )
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


@app.post("/cart/items", response_model=CartItemResponse, status_code=201, tags=["Shopping Cart"])
async def add_to_cart(
    item: CartItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Добавить товар в мою корзину (требуется аутентификация)"""
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item.product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += item.quantity
        if product.stock < cart_item.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
    else:
        cart_item = CartItem(user_id=current_user.id, **item.model_dump())
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart_item)
    return cart_item


@app.get("/cart", response_model=CartResponse, tags=["Shopping Cart"])
async def get_my_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить мою корзину (требуется аутентификация)"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    total = Decimal('0.00')
    for item in cart_items:
        total += item.product.price * item.quantity
    
    return {"items": cart_items, "total": total}


@app.put("/cart/items/{item_id}", response_model=CartItemResponse, tags=["Shopping Cart"])
async def update_cart_item(
    item_id: int,
    item_update: CartItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновить количество товара в корзине (требуется аутентификация)"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if cart_item.product.stock < item_update.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    cart_item.quantity = item_update.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


@app.delete("/cart/items/{item_id}", tags=["Shopping Cart"])
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удалить товар из моей корзины (требуется аутентификация)"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}


@app.delete("/cart", tags=["Shopping Cart"])
async def clear_my_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Очистить все товары из моей корзины (требуется аутентификация)"""
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}


@app.post("/orders", response_model=OrderResponse, status_code=201, tags=["Orders"])
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создать заказ из моей корзины (требуется аутентификация)"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total_amount = Decimal('0.00')
    for cart_item in cart_items:
        product = cart_item.product
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product: {product.name}"
            )
        total_amount += product.price * cart_item.quantity
    
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        **order_data.model_dump()
    )
    db.add(new_order)
    db.flush()
    
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.add(order_item)
        
        cart_item.product.stock -= cart_item.quantity
    
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    
    db.commit()
    db.refresh(new_order)
    return new_order


@app.get("/orders", tags=["Orders"])
async def get_my_orders(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Элементов на странице"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить все мои заказы с пагинацией (требуется аутентификация)"""
    pagination = PaginationParams(page=page, page_size=page_size)
    query = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc())
    query = query.options(joinedload(Order.order_items).joinedload(OrderItem.product))
    
    items, meta = paginate(query, pagination)
    
    return create_paginated_response(items, meta)


@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
async def get_my_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить детали конкретного заказа (требуется аутентификация)"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).options(joinedload(Order.order_items).joinedload(OrderItem.product)).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order


@app.put("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
async def update_my_order_status(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновить статус заказа (требуется аутентификация)"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = OrderStatus[order_update.status.upper()]
    db.commit()
    db.refresh(order)
    return order


@app.post("/reviews", response_model=ReviewResponse, status_code=201, tags=["Reviews"])
async def create_review(
    review: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создать отзыв на товар (требуется аутентификация)"""
    product = db.query(Product).filter(Product.id == review.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing_review = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.product_id == review.product_id
    ).first()
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You already reviewed this product")
    
    new_review = Review(user_id=current_user.id, **review.model_dump())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


@app.get("/reviews/product/{product_id}", tags=["Reviews"])
def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Элементов на странице"),
    db: Session = Depends(get_db)
):
    """Получить все отзывы на товар с пагинацией (публичный)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    pagination = PaginationParams(page=page, page_size=page_size)
    query = db.query(Review).filter(Review.product_id == product_id).order_by(Review.created_at.desc())
    query = query.options(joinedload(Review.user))
    
    items, meta = paginate(query, pagination)
    
    return create_paginated_response(items, meta)


@app.get("/reviews/my", tags=["Reviews"])
async def get_my_reviews(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Элементов на странице"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить все мои отзывы с пагинацией (требуется аутентификация)"""
    pagination = PaginationParams(page=page, page_size=page_size)
    query = db.query(Review).filter(Review.user_id == current_user.id).order_by(Review.created_at.desc())
    
    items, meta = paginate(query, pagination)
    
    return create_paginated_response(items, meta)


@app.put("/reviews/{review_id}", response_model=ReviewResponse, tags=["Reviews"])
async def update_my_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновить мой отзыв (требуется аутентификация)"""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    update_data = review_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    db.commit()
    db.refresh(review)
    return review


@app.delete("/reviews/{review_id}", tags=["Reviews"])
async def delete_my_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удалить мой отзыв (требуется аутентификация)"""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}


frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    static_dir = frontend_dist / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Обслуживание SPA фронтенда - перехват всех маршрутов, не соответствующих API"""
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "health")):
            raise HTTPException(status_code=404, detail="Not found")
        
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            from fastapi.responses import FileResponse
            return FileResponse(str(index_file))
        return {"message": "Frontend not found"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

