# views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.utils import timezone

from .models import (
    Category, Supplier, Product, Store,
    StoreInventory, User, Order, OrderItem
)
from .serializers import (
    CategorySerializer, SupplierSerializer, ProductSerializer,
    StoreSerializer, StoreInventorySerializer, UserSerializer,
    OrderSerializer, OrderCreateSerializer, OrderItemSerializer,
    StoreInventoryUpdateSerializer
)
# database/views.py
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import status as http_status


# Декораторы для CategoryViewSet
@extend_schema_view(
    list=extend_schema(
        summary="Получить список категорий",
        description="Возвращает список всех категорий товаров с пагинацией. "
                    "Доступны фильтрация, поиск и сортировка.",
        tags=['Категории'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Поиск по названию или описанию категории'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Сортировка (name, -name, created_at, -created_at)'
            ),
        ],
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                value=[
                    {
                        "id": 1,
                        "name": "Электроника",
                        "description": "Техника и гаджеты",
                        "products_count": 15,
                        "created_at": "2024-01-29T10:00:00Z",
                        "updated_at": "2024-01-29T10:00:00Z"
                    }
                ]
            )
        ]
    ),
    create=extend_schema(
        summary="Создать новую категорию",
        description="Создает новую категорию товаров. "
                    "Все поля, кроме description, обязательны.",
        tags=['Категории'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Одежда'},
                    'description': {'type': 'string', 'example': 'Одежда и обувь'}
                },
                'required': ['name']
            }
        },
        responses={
            201: OpenApiResponse(
                response=CategorySerializer,
                description='Категория успешно создана'
            ),
            400: OpenApiResponse(
                response={'type': 'object'},
                description='Некорректные данные'
            )
        }
    ),
    retrieve=extend_schema(
        summary="Получить информацию о категории",
        description="Возвращает детальную информацию о категории, "
                    "включая количество товаров в ней.",
        tags=['Категории']
    ),
    update=extend_schema(
        summary="Обновить категорию",
        description="Полностью обновляет информацию о категории.",
        tags=['Категории']
    ),
    partial_update=extend_schema(
        summary="Частично обновить категорию",
        description="Частично обновляет информацию о категории.",
        tags=['Категории']
    ),
    destroy=extend_schema(
        summary="Удалить категорию",
        description="Удаляет категорию. "
                    "Категорию нельзя удалить, если в ней есть товары.",
        tags=['Категории'],
        responses={
            204: OpenApiResponse(description='Категория удалена'),
            400: OpenApiResponse(
                description='Невозможно удалить категорию с товарами'
            )
        }
    )
)
class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @extend_schema(
        summary="Товары в категории",
        description="Получить все товары, принадлежащие конкретной категории.",
        tags=['Категории'],
        responses={200: ProductSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Получить товары в категории"""
        category = self.get_object()
        products = category.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


# Декораторы для SupplierViewSet
@extend_schema_view(
    list=extend_schema(
        summary="Получить список поставщиков",
        description="Возвращает список всех поставщиков с возможностью фильтрации по рейтингу.",
        tags=['Поставщики'],
        parameters=[
            OpenApiParameter(
                name='rating',
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                description='Фильтр по минимальному рейтингу (например: 4.0)'
            ),
        ]
    ),
    create=extend_schema(
        summary="Создать нового поставщика",
        description="Создает нового поставщика. ИНН должен быть уникальным.",
        tags=['Поставщики']
    ),
    retrieve=extend_schema(
        summary="Получить информацию о поставщике",
        description="Возвращает детальную информацию о поставщике.",
        tags=['Поставщики']
    )
)
class SupplierViewSet(viewsets.ModelViewSet):
    """CRUD для поставщиков"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating']
    search_fields = ['name', 'inn', 'email', 'contact_phone']
    ordering_fields = ['name', 'rating', 'created_at']
    ordering = ['name']

    @extend_schema(
        summary="Товары поставщика",
        description="Получить все товары конкретного поставщика.",
        tags=['Поставщики'],
        responses={200: ProductSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Получить товары поставщика"""
        supplier = self.get_object()
        products = supplier.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Топ поставщиков",
        description="Получить список поставщиков с рейтингом 4.0 и выше.",
        tags=['Поставщики'],
        responses={200: SupplierSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Топ поставщиков по рейтингу"""
        suppliers = Supplier.objects.filter(rating__gte=4.0).order_by('-rating')
        serializer = self.get_serializer(suppliers, many=True)
        return Response(serializer.data)


# Добавь аналогичные декораторы для других ViewSet
# (ProductViewSet, StoreViewSet, UserViewSet, OrderViewSet, StoreInventoryViewSet)

class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Получить товары в категории"""
        category = self.get_object()
        products = category.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class SupplierViewSet(viewsets.ModelViewSet):
    """CRUD для поставщиков"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating']
    search_fields = ['name', 'inn', 'email', 'contact_phone']
    ordering_fields = ['name', 'rating', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Получить товары поставщика"""
        supplier = self.get_object()
        products = supplier.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Топ поставщиков по рейтингу"""
        suppliers = Supplier.objects.filter(rating__gte=4.0).order_by('-rating')
        serializer = self.get_serializer(suppliers, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD для товаров"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'supplier', 'category']
    search_fields = ['name', 'article', 'barcode', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Фильтрация товаров"""
        queryset = super().get_queryset()

        # Фильтр по минимальной цене
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        # Фильтр по максимальной цене
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Фильтр по весу
        max_weight = self.request.query_params.get('max_weight')
        if max_weight:
            queryset = queryset.filter(weight__lte=max_weight)

        return queryset

    @action(detail=True, methods=['get'])
    def stores(self, request, pk=None):
        """Получить склады, где есть товар"""
        product = self.get_object()
        stores = product.stores.all()
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Только активные товары"""
        products = Product.objects.filter(is_active=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Переключить активность товара"""
        product = self.get_object()
        product.is_active = not product.is_active
        product.save()
        serializer = self.get_serializer(product)
        return Response(serializer.data)


class StoreViewSet(viewsets.ModelViewSet):
    """CRUD для складов/магазинов"""
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'region']
    search_fields = ['name', 'address', 'phone', 'region']
    ordering_fields = ['name', 'region', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """Получить инвентарь склада"""
        store = self.get_object()
        inventory = StoreInventory.objects.filter(store=store).select_related('product')
        serializer = StoreInventorySerializer(inventory, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Получить сотрудников склада"""
        store = self.get_object()
        employees = store.employees.all()
        serializer = UserSerializer(employees, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Получить заказы склада"""
        store = self.get_object()
        orders = store.orders.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Переключить активность склада"""
        store = self.get_object()
        store.is_active = not store.is_active
        store.save()
        serializer = self.get_serializer(store)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика по складам"""
        stats = Store.objects.annotate(
            products_count=Count('products', distinct=True),
            employees_count=Count('employees', distinct=True),
            orders_count=Count('orders', distinct=True),
            total_inventory=Sum('storeinventory__quantity')
        )
        data = []
        for store in stats:
            data.append({
                'id': store.id,
                'name': store.name,
                'products_count': store.products_count,
                'employees_count': store.employees_count,
                'orders_count': store.orders_count,
                'total_inventory': store.total_inventory or 0
            })
        return Response(data)


class StoreInventoryViewSet(viewsets.ModelViewSet):
    """CRUD для остатков на складе"""
    queryset = StoreInventory.objects.all()
    serializer_class = StoreInventorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['store', 'product']
    search_fields = ['product__name', 'product__article', 'store__name']
    ordering_fields = ['quantity', 'created_at']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        """Использовать разные сериализаторы для разных операций"""
        if self.action in ['update', 'partial_update']:
            return StoreInventoryUpdateSerializer
        return StoreInventorySerializer

    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        """Добавить количество на склад"""
        inventory = self.get_object()
        quantity = request.data.get('quantity', 0)

        if not quantity or quantity <= 0:
            return Response(
                {'error': 'Укажите корректное количество'},
                status=status.HTTP_400_BAD_REQUEST
            )

        inventory.quantity += int(quantity)
        inventory.save()
        serializer = self.get_serializer(inventory)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_stock(self, request, pk=None):
        """Убрать количество со склада"""
        inventory = self.get_object()
        quantity = request.data.get('quantity', 0)

        if not quantity or quantity <= 0:
            return Response(
                {'error': 'Укажите корректное количество'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if inventory.quantity < quantity:
            return Response(
                {'error': f'Недостаточно товара. Доступно: {inventory.quantity}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        inventory.quantity -= int(quantity)
        inventory.save()
        serializer = self.get_serializer(inventory)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD для пользователей"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'store']
    search_fields = ['login', 'full_name', 'email', 'phone']
    ordering_fields = ['full_name', 'created_at', 'last_login']
    ordering = ['full_name']

    def perform_create(self, serializer):
        """Хеширование пароля при создании"""
        user = serializer.save()
        if 'password' in self.request.data:
            user.set_password(self.request.data['password'])
            user.save()

    def perform_update(self, serializer):
        """Хеширование пароля при обновлении"""
        user = serializer.save()
        if 'password' in self.request.data:
            user.set_password(self.request.data['password'])
            user.save()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить текущего пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Изменить пароль пользователя"""
        user = self.get_object()
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response(
                {'error': 'Укажите старый и новый пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(old_password):
            return Response(
                {'error': 'Неверный старый пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Пароль успешно изменен'})

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Переключить активность пользователя"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD для заказов"""
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'store', 'created_by']
    search_fields = ['order_number', 'customer_name', 'customer_phone', 'customer_email']
    ordering_fields = ['created_at', 'total_sum', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Использовать разные сериализаторы для разных операций"""
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """Фильтрация заказов"""
        queryset = super().get_queryset()

        # Фильтр по дате начала
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        # Фильтр по дате окончания
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        # Фильтр по минимальной сумме
        min_sum = self.request.query_params.get('min_sum')
        if min_sum:
            queryset = queryset.filter(total_sum__gte=min_sum)

        # Фильтр по максимальной сумме
        max_sum = self.request.query_params.get('max_sum')
        if max_sum:
            queryset = queryset.filter(total_sum__lte=max_sum)

        return queryset

    def perform_create(self, serializer):
        """Установка создателя заказа"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Изменить статус заказа"""
        order = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {'error': 'Укажите новый статус'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка допустимых статусов
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Недопустимый статус. Допустимые: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Добавить товар в заказ"""
        order = self.get_object()

        # Проверка, что заказ еще можно изменять
        if order.status in ['cancelled', 'completed', 'delivered']:
            return Response(
                {'error': 'Нельзя изменить завершенный или отмененный заказ'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response(
                {'error': 'Укажите товар'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Создаем или обновляем позицию заказа
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )

        if not created:
            order_item.quantity += int(quantity)
            order_item.save()

        # Пересчет общей суммы
        order.calculate_total()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        """Удалить товар из заказа"""
        order = self.get_object()

        # Проверка, что заказ еще можно изменять
        if order.status in ['cancelled', 'completed', 'delivered']:
            return Response(
                {'error': 'Нельзя изменить завершенный или отмененный заказ'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_id = request.data.get('product')

        if not product_id:
            return Response(
                {'error': 'Укажите товар'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order_item = OrderItem.objects.get(order=order, product_id=product_id)
        except OrderItem.DoesNotExist:
            return Response(
                {'error': 'Товар не найден в заказе'},
                status=status.HTTP_404_NOT_FOUND
            )

        order_item.delete()

        # Пересчет общей суммы
        order.calculate_total()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика по заказам"""
        # Общая статистика
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('total_sum'))['total'] or 0
        average_order_value = Order.objects.aggregate(avg=Sum('total_sum') / Count('id'))['avg'] or 0

        # Статистика по статусам
        status_stats = Order.objects.values('status').annotate(
            count=Count('id'),
            total=Sum('total_sum')
        )

        # Статистика по дням (последние 30 дней)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        daily_stats = Order.objects.filter(
            created_at__gte=thirty_days_ago
        ).extra(
            {'date': "date(created_at)"}
        ).values('date').annotate(
            count=Count('id'),
            total=Sum('total_sum')
        ).order_by('date')

        return Response({
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'average_order_value': float(average_order_value),
            'status_stats': list(status_stats),
            'daily_stats': list(daily_stats)
        })


class OrderItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Только чтение для позиций заказа"""
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order', 'product']
    ordering_fields = ['created_at']
    ordering = ['-created_at']