"""
Вспомогательные функции для приложения
"""

from typing import List, TypeVar
from sqlalchemy.orm import Query
from app.schemas import PaginationParams, PaginationMeta

T = TypeVar('T')


def paginate(
    query: Query,
    pagination: PaginationParams
) -> tuple[List, PaginationMeta]:
    """
    Пагинирует SQLAlchemy запрос
    
    Аргументы:
        query: Объект SQLAlchemy запроса
        pagination: Параметры пагинации
        
    Возвращает:
        Кортеж (элементы, метаданные_пагинации)
    """
    total = query.count()
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    items = query.offset(pagination.skip).limit(pagination.limit).all()
    
    meta = PaginationMeta(
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_previous=pagination.page > 1
    )
    
    return items, meta


def create_paginated_response(
    items: List[T],
    pagination_meta: PaginationMeta
) -> dict:
    """
    Создает словарь пагинированного ответа
    
    Аргументы:
        items: Список элементов
        pagination_meta: Метаданные пагинации
        
    Возвращает:
        Словарь с элементами и метаданными пагинации
    """
    return {
        "items": items,
        "pagination": pagination_meta
    }

