# serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import (
    Category, Supplier, Product, Store,
    StoreInventory, User, Order, OrderItem
)
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer
from drf_spectacular.types import OpenApiTypes


@extend_schema_serializer(
    examples=[
        {
            'name': 'Электроника',
            'description': 'Техника и гаджеты',
        }
    ]
)
class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий товаров"""

    products_count = serializers.SerializerMethodField(
        help_text="Количество товаров в категории"
    )

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'products_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    @extend_schema_field(OpenApiTypes.INT)
    def get_products_count(self, obj):
        return obj.products.count()


@extend_schema_serializer(
    examples=[
        {
            'name': 'ООО "Электроникс"',
            'inn': '1234567890',
            'contact_phone': '+79991234567',
            'email': 'info@electronix.ru',
            'address': 'Москва, ул. Ленина, 1',
            'bank_details': 'р/с 40702810123456789012',
            'rating': 4.5
        }
    ]
)
class SupplierSerializer(serializers.ModelSerializer):
    """Сериализатор для поставщиков"""

    products_count = serializers.SerializerMethodField(
        help_text="Количество товаров у поставщика"
    )

    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'inn', 'contact_phone', 'email',
            'address', 'bank_details', 'rating', 'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    @extend_schema_field(OpenApiTypes.INT)
    def get_products_count(self, obj):
        return obj.products.count()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_products_count(self, obj):
        return obj.products.count()


class SupplierSerializer(serializers.ModelSerializer):
    """Сериализатор для поставщиков"""
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'inn', 'contact_phone', 'email',
            'address', 'bank_details', 'rating', 'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_products_count(self, obj):
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для товаров"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    stores_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'article', 'barcode', 'name', 'description',
            'price', 'weight', 'is_active', 'supplier', 'supplier_name',
            'category', 'category_name', 'stores_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_stores_count(self, obj):
        return obj.stores.count()


class StoreSerializer(serializers.ModelSerializer):
    """Сериализатор для складов/магазинов"""
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    products_count = serializers.SerializerMethodField()
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = [
            'id', 'name', 'address', 'region', 'phone',
            'manager', 'manager_name', 'is_active',
            'products_count', 'employees_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_products_count(self, obj):
        return obj.products.count()

    def get_employees_count(self, obj):
        return obj.employees.count()


class StoreInventorySerializer(serializers.ModelSerializer):
    """Сериализатор для остатков на складе"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    product_article = serializers.CharField(source='product.article', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = StoreInventory
        fields = [
            'id', 'store', 'store_name', 'product', 'product_name',
            'product_article', 'product_price', 'quantity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей"""
    store_name = serializers.CharField(source='store.name', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    permissions_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'login', 'password', 'password_hash', 'full_name',
            'role', 'store', 'store_name', 'phone', 'email',
            'is_active', 'last_login', 'permissions', 'permissions_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'password_hash', 'last_login', 'created_at', 'updated_at']

    def get_permissions_display(self, obj):
        # Преобразуем список прав в читаемый формат
        permission_map = {
            'view': 'Просмотр',
            'edit': 'Редактирование',
            'create': 'Создание',
            'delete': 'Удаление',
            'admin': 'Администрирование'
        }
        return [permission_map.get(p, p) for p in obj.permissions]

    def create(self, validated_data):
        # Обработка пароля при создании
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        # Обработка пароля при обновлении
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для позиций заказа"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_article = serializers.CharField(source='product.article', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_article',
            'quantity', 'price', 'total_price', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_total_price(self, obj):
        return obj.total_price


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для заказов"""
    store_name = serializers.CharField(source='store.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'store', 'store_name',
            'customer_name', 'customer_phone', 'customer_email',
            'status', 'status_display', 'total_sum',
            'created_by', 'created_by_name', 'notes',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_sum', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания заказа с позициями"""
    items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'store', 'customer_name',
            'customer_phone', 'customer_email', 'status',
            'created_by', 'notes', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        # Пересчет общей суммы
        order.calculate_total()

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Обновление полей заказа
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновление позиций заказа, если предоставлены
        if items_data is not None:
            # Удаляем старые позиции
            instance.items.all().delete()

            # Создаем новые позиции
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

            # Пересчет общей суммы
            instance.calculate_total()

        return instance


class StoreInventoryUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления остатков на складе"""

    class Meta:
        model = StoreInventory
        fields = ['quantity']