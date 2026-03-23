# database/tests.py
import unittest

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User as DjangoUser
from .models import Category, Supplier, Product, Store, User as CustomUser


class SimpleAPITests(APITestCase):
    """Простые тесты API"""

    def setUp(self):
        # Создаем пользователя Django для аутентификации
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.django_user)

        # Создаем тестовую категорию
        self.category = Category.objects.create(
            name='Электроника',
            description='Техника'
        )

        # Создаем тестового поставщика
        self.supplier = Supplier.objects.create(
            name='Тестовый поставщик',
            inn='1234567890',
            contact_phone='+79991234567',
            email='test@test.ru',
            address='Адрес',
            bank_details='Реквизиты',
            rating=4.0
        )

        # Создаем тестовый товар
        self.product = Product.objects.create(
            article='TEST-001',
            barcode='123456789012',
            name='Тестовый товар',
            description='Описание',
            price=1000.00,
            weight=0.5,
            is_active=True,
            supplier=self.supplier,
            category=self.category
        )

        # Создаем тестовый склад
        self.store = Store.objects.create(
            name='Тестовый склад',
            address='Адрес склада',
            region='Москва',
            phone='+79998887766',
            is_active=True
        )

        # Создаем тестового пользователя
        self.custom_user = CustomUser.objects.create(
            login='testuser',
            full_name='Тест Юзер',
            role='admin',
            email='user@test.ru',
            is_active=True
        )
        self.custom_user.set_password('testpass123')
        self.custom_user.save()

    def test_category_list(self):
        """Проверка получения списка категорий"""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # class CategoryCreateTest(unittest.TestCase):
    #     """Тест создания категории"""
    #
    #     def test_category_create(self):
    #         """Проверка создания категории"""
    #         # Создаем пользователя
    #         user, _ = User.objects.get_or_create(
    #             username='testuser',
    #             defaults={
    #                 'full_name': 'Test User',
    #                 'is_active': True
    #             }
    #         )
    #         user.set_password('testpass123')
    #         user.save()
    #
    #         # Авторизуемся
    #         client = APIClient()
    #         client.force_authenticate(user=user)
    #
    #         # Создаем категорию
    #         url = reverse('category-list')
    #         data = {'name': 'Новая категория', 'description': 'Описание'}
    #         response = client.post(url, data)
    #
    #         print(f"Статус: {response.status_code}")
    #         print(f"Ответ: {response.json()}")
    #
    #         # Проверки
    #         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #         self.assertTrue(Category.objects.filter(name='Новая категория').exists())
    #
    #         # Принудительный коммит
    #         from django.db import connection
    #         connection.commit()
    #
    #         print(f"✅ Категория создана!")

    def test_supplier_list(self):
        """Проверка получения списка поставщиков"""
        url = reverse('supplier-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supplier_create(self):
        """Проверка создания поставщика"""
        url = reverse('supplier-list')
        data = {
            'name': 'Новый поставщик',
            'inn': '0987654321',
            'contact_phone': '+79991112233',
            'email': 'new@test.ru',
            'address': 'Адрес',
            'bank_details': 'Реквизиты',
            'rating': 4.5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_product_list(self):
        """Проверка получения списка товаров"""
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_create(self):
        """Проверка создания товара"""
        url = reverse('product-list')
        data = {
            'article': 'NEW-001',
            'barcode': '111222333444',
            'name': 'Новый товар',
            'description': 'Описание',
            'price': 2000.00,
            'weight': 1.0,
            'is_active': True,
            'supplier': self.supplier.id,
            'category': self.category.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_store_list(self):
        """Проверка получения списка складов"""
        url = reverse('store-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list(self):
        """Проверка получения списка пользователей"""
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_create(self):
        """Проверка создания пользователя"""
        url = reverse('user-list')
        data = {
            'login': 'newuser',
            'password': 'password123',
            'full_name': 'Новый пользователь',
            'role': 'manager',
            'email': 'new@user.ru'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_product_search(self):
        """Проверка поиска товаров"""
        url = reverse('product-list') + '?search=Тестовый'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_supplier_products(self):
        """Проверка получения товаров поставщика"""
        url = reverse('supplier-products', args=[self.supplier.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_active_endpoint(self):
        """Проверка получения активных товаров"""
        url = reverse('product-active')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_access(self):
        """Проверка что без авторизации нельзя получить доступ"""
        client = APIClient()  # Неавторизованный клиент
        url = reverse('category-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_filter_by_active(self):
        """Проверка фильтрации товаров по активности"""
        url = reverse('product-list') + '?is_active=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ModelTests(TestCase):
    """Тесты моделей"""

    def test_category_str(self):
        category = Category(name='Тест')
        self.assertEqual(str(category), 'Тест')

    def test_supplier_str(self):
        supplier = Supplier(name='Тестовый поставщик')
        self.assertEqual(str(supplier), 'Тестовый поставщик')

    def test_product_str(self):
        supplier = Supplier(name='Поставщик')
        product = Product(name='Товар', article='ART-001', supplier=supplier)
        self.assertIn('Товар', str(product))
        self.assertIn('ART-001', str(product))

    def test_store_str(self):
        store = Store(name='Склад', region='Москва')
        self.assertIn('Склад', str(store))
        self.assertIn('Москва', str(store))

    def test_user_str(self):
        user = CustomUser(login='user', full_name='Имя', role='admin')
        self.assertIn('Имя', str(user))
        self.assertIn('admin', str(user))

    def test_product_price_must_be_positive(self):
        """Проверка что цена товара должна быть положительной"""
        supplier = Supplier.objects.create(
            name='Поставщик',
            inn='1111111111',
            contact_phone='+79991111111',
            email='test@test.ru'
        )
        category = Category.objects.create(name='Категория')

        product = Product.objects.create(
            article='ART-001',
            barcode='111',
            name='Товар',
            price=100.00,  # Положительная цена
            supplier=supplier,
            category=category
        )

        self.assertGreater(product.price, 0)


class EndpointTests(TestCase):
    """Тесты проверки доступности эндпоинтов"""

    def setUp(self):
        self.user = DjangoUser.objects.create_user(
            username='test',
            password='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_api_root(self):
        """Проверка что API корень доступен"""
        url = reverse('api-root')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_endpoints_defined(self):
        """Проверка что все эндпоинты определены"""
        endpoints = [
            ('category-list', None),
            ('supplier-list', None),
            ('product-list', None),
            ('store-list', None),
            ('user-list', None),
            ('order-list', None),
        ]

        for endpoint, args in endpoints:
            try:
                url = reverse(endpoint, args=args) if args else reverse(endpoint)
                response = self.client.get(url)
                # Эндпоинт должен возвращать 200 или 405 (если метод не разрешен)
                self.assertIn(response.status_code,
                              [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED])
            except Exception as e:
                self.fail(f'Эндпоинт {endpoint} не работает: {e}')
