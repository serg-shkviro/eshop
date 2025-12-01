from pydantic import BaseModel, EmailStr, Field, condecimal, ConfigDict
from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from decimal import Decimal

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Параметры пагинации"""
    page: int = Field(1, ge=1, description="Номер страницы (начинается с 1)")
    page_size: int = Field(20, ge=1, le=100, description="Элементов на странице (макс 100)")
    
    @property
    def skip(self) -> int:
        """Вычисляет значение пропуска для запроса к БД"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Получает значение лимита для запроса к БД"""
        return self.page_size


class PaginationMeta(BaseModel):
    """Метаданные пагинации"""
    total: int = Field(..., description="Общее количество элементов")
    page: int = Field(..., description="Текущий номер страницы")
    page_size: int = Field(..., description="Элементов на странице")
    total_pages: int = Field(..., description="Общее количество страниц")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_previous: bool = Field(..., description="Есть ли предыдущая страница")


class PaginatedResponse(BaseModel, Generic[T]):
    """Обобщенный пагинированный ответ"""
    items: List[T]
    pagination: PaginationMeta


class UserRegister(BaseModel):
    """Схема для регистрации пользователя"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Схема ответа с токеном"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Схема данных токена"""
    email: Optional[str] = None


class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class PasswordChange(BaseModel):
    """Схема для изменения пароля"""
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)


class AdminUserUpdate(BaseModel):
    """Схема для обновления пользователя администратором"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    is_active: Optional[int] = None
    is_admin: Optional[int] = None


class UserResponse(BaseModel):
    """Схема ответа с пользователем"""
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: int
    is_admin: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    """Схема для создания категории"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    """Схема для обновления категории"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    """Схема ответа с категорией"""
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """Схема для создания товара"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: condecimal(max_digits=10, decimal_places=2, gt=0)
    stock: int = Field(..., ge=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[int] = Field(1, ge=0, le=1)


class ProductUpdate(BaseModel):
    """Схема для обновления товара"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[condecimal(max_digits=10, decimal_places=2, gt=0)] = None
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[int] = Field(None, ge=0, le=1)


class ProductResponse(BaseModel):
    """Схема ответа с товаром"""
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None
    image_url: Optional[str] = None
    is_active: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class CartItemCreate(BaseModel):
    """Схема для добавления товара в корзину"""
    product_id: int
    quantity: int = Field(..., ge=1)


class CartItemUpdate(BaseModel):
    """Схема для обновления количества товара в корзине"""
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    """Схема ответа с элементом корзины"""
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: ProductResponse
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    """Схема полного ответа с корзиной"""
    items: List[CartItemResponse]
    total: Decimal


class OrderItemCreate(BaseModel):
    """Схема для элемента заказа"""
    product_id: int
    quantity: int = Field(..., ge=1)


class OrderItemResponse(BaseModel):
    """Схема ответа с элементом заказа"""
    id: int
    product_id: int
    quantity: int
    price: Decimal
    product: ProductResponse
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    """Схема для создания заказа"""
    shipping_address: str
    payment_method: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class OrderUpdate(BaseModel):
    """Схема для обновления статуса заказа"""
    status: str = Field(..., pattern="^(pending|confirmed|shipped|delivered|cancelled)$")


class OrderResponse(BaseModel):
    """Схема ответа с заказом"""
    id: int
    user_id: int
    total_amount: Decimal
    status: str
    shipping_address: str
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    order_items: List[OrderItemResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    """Схема для создания отзыва"""
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewUpdate(BaseModel):
    """Схема для обновления отзыва"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    """Схема ответа с отзывом"""
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: Optional[str] = None
    user: UserResponse
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

