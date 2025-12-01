"""
Скрипт для заполнения базы данных тестовыми данными
Запуск: python seed_data.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine
from app.models import Base, User, Category, Product
from decimal import Decimal
from app.auth import get_password_hash

def seed_database():
    db = SessionLocal()
    
    try:
        print("Seeding database with sample data...")
        
        categories = [
            Category(name="Электроника", description="Электронные устройства и гаджеты"),
            Category(name="Одежда", description="Мода и одежда"),
            Category(name="Книги", description="Книги и публикации"),
            Category(name="Дом и Сад", description="Товары для дома и садоводства"),
            Category(name="Спорт", description="Спортивное оборудование и аксессуары"),
        ]
        
        for category in categories:
            db.add(category)
        db.commit()
        print(f"Created {len(categories)} categories")
        
        users = [
            User(
                name="Иван Иванов",
                email="ivan@example.com",
                hashed_password=get_password_hash("password123"),
                phone="+79001234567",
                address="ул. Ленина, д. 10, Москва, 101000",
                is_admin=1
            ),
            User(
                name="Мария Петрова",
                email="maria@example.com",
                hashed_password=get_password_hash("password123"),
                phone="+79001234568",
                address="пр. Невский, д. 25, Санкт-Петербург, 191186",
                is_admin=0
            ),
            User(
                name="Алексей Сидоров",
                email="alexey@example.com",
                hashed_password=get_password_hash("password123"),
                phone="+79001234569",
                address="ул. Красная, д. 5, Казань, 420000",
                is_admin=0
            ),
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        print(f"Created {len(users)} users")
        
        products = [
            Product(
                name="Ноутбук Pro 15\"",
                description="Высокопроизводительный ноутбук с 16 ГБ ОЗУ и 512 ГБ SSD",
                price=Decimal("1299.99"),
                stock=25,
                category_id=1,
                is_active=1,
                image_url="https://images.pexels.com/photos/18105/pexels-photo.jpg"
            ),
            Product(
                name="Беспроводная мышь",
                description="Эргономичная беспроводная мышь с точным отслеживанием",
                price=Decimal("29.99"),
                stock=100,
                category_id=1,
                is_active=1,
                image_url="https://images.pexels.com/photos/34396238/pexels-photo-34396238.jpeg"
            ),
            Product(
                name="USB-C концентратор",
                description="7-в-1 USB-C концентратор с HDMI, USB 3.0 и кардридером",
                price=Decimal("49.99"),
                stock=50,
                category_id=1,
                is_active=1
            ),
            Product(
                name="Bluetooth наушники",
                description="Наушники с шумоподавлением и батареей на 30 часов",
                price=Decimal("199.99"),
                stock=40,
                category_id=1,
                is_active=1
            ),
            Product(
                name="Хлопковая футболка",
                description="Удобная хлопковая футболка различных цветов",
                price=Decimal("19.99"),
                stock=200,
                category_id=2,
                is_active=1,
                image_url="https://images.pexels.com/photos/8532616/pexels-photo-8532616.jpeg"
            ),
            Product(
                name="Джинсы",
                description="Классические джинсы",
                price=Decimal("59.99"),
                stock=80,
                category_id=2,
                is_active=1
            ),
            Product(
                name="Беговые кроссовки",
                description="Легкие беговые кроссовки с амортизирующей подошвой",
                price=Decimal("89.99"),
                stock=60,
                category_id=2,
                is_active=1,
                image_url="https://images.pexels.com/photos/2529148/pexels-photo-2529148.jpeg"
            ),
            Product(
                name="Руководство по программированию на Python",
                description="Подробное руководство по программированию на Python",
                price=Decimal("39.99"),
                stock=150,
                category_id=3,
                is_active=1
            ),
            Product(
                name="Справочник по веб-разработке",
                description="Современные техники веб-разработки и лучшие практики",
                price=Decimal("44.99"),
                stock=120,
                category_id=3,
                is_active=1
            ),
            Product(
                name="LED настольная лампа",
                description="Регулируемая LED настольная лампа с сенсорным управлением",
                price=Decimal("34.99"),
                stock=75,
                category_id=4,
                is_active=1,
                image_url="https://images.pexels.com/photos/1112598/pexels-photo-1112598.jpeg"
            ),
            Product(
                name="Набор цветочных горшков",
                description="Набор из 3 керамических цветочных горшков с дренажем",
                price=Decimal("24.99"),
                stock=90,
                category_id=4,
                is_active=1
            ),
            Product(
                name="Коврик для йоги",
                description="Нескользящий коврик для йоги с ремнем для переноски",
                price=Decimal("29.99"),
                stock=100,
                category_id=5,
                is_active=1
            ),
            Product(
                name="Набор гантелей",
                description="Регулируемый набор гантелей (2-11 кг)",
                price=Decimal("149.99"),
                stock=30,
                category_id=5,
                is_active=1,
                image_url="https://images.pexels.com/photos/669582/pexels-photo-669582.jpeg"
            ),
        ]
        
        for product in products:
            db.add(product)
        db.commit()
        print(f"Created {len(products)} products")
        
        print("\nБаза данных успешно заполнена!")
        print("\nИтоги:")
        print(f"   - {len(categories)} категорий")
        print(f"   - {len(users)} пользователей (пароль: 'password123')")
        print(f"   - {len(products)} товаров")
        print("\nТестовые пользователи:")
        print("   - ivan@example.com / password123 (Администратор)")
        print("   - maria@example.com / password123")
        print("   - alexey@example.com / password123")
        print("\nТеперь вы можете протестировать API с этими данными!")
        print("   Посетите http://localhost:8000/docs для изучения API")
        print("   Используйте эндпоинт /auth/login для получения токена\n")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_database()

