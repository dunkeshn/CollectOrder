from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название категории'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание категории'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего изменения'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Наименование поставщика'
    )
    inn = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='ИНН'
    )
    contact_phone = models.CharField(
        max_length=20,
        verbose_name='Контактный телефон'
    )
    email = models.EmailField(
        verbose_name='Email'
    )
    address = models.TextField(
        verbose_name='Адрес'
    )
    bank_details = models.TextField(
        verbose_name='Банковские реквизиты'
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name='Рейтинг поставщика'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего изменения'
    )

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    article = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Артикул'
    )
    barcode = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Штрихкод'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название товара'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание товара'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        verbose_name='Вес (кг)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        verbose_name='Поставщик'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Категория'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего изменения'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']
        indexes = [
            models.Index(fields=['article']),
            models.Index(fields=['barcode']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.article})"


class Store(models.Model):
    """Модель складов/магазинов"""
    name = models.CharField(
        max_length=255,
        verbose_name='Наименование'
    )
    address = models.TextField(
        verbose_name='Адрес'
    )
    region = models.CharField(
        max_length=100,
        verbose_name='Регион/Город'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон'
    )
    # Добавляем поле manager - связь с пользователем
    manager = models.ForeignKey(
        'User',  # Ссылка на модель User
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_stores',  # Меняем related_name, чтобы не было конфликта
        verbose_name='Менеджер'
    )
    products = models.ManyToManyField(
        Product,
        through='StoreInventory',
        related_name='stores',
        verbose_name='Товары на складе'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего изменения'
    )

    class Meta:
        verbose_name = 'Склад/Магазин'
        verbose_name_plural = 'Склады/Магазины'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.region}"


class StoreInventory(models.Model):
    """Промежуточная модель для хранения информации о количестве товаров на складе"""
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name='Склад'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Остаток на складе'
        verbose_name_plural = 'Остатки на складах'
        unique_together = ['store', 'product']

    def __str__(self):
        return f"{self.product.name} - {self.store.name}: {self.quantity}"


class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('cashier', 'Кассир'),
        ('warehouse', 'Кладовщик'),
        ('supplier', 'Поставщик'),
    ]

    PERMISSION_CHOICES = [
        ('view', 'Просмотр'),
        ('edit', 'Редактирование'),
        ('create', 'Создание'),
        ('delete', 'Удаление'),
        ('admin', 'Администрирование'),
    ]

    login = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Логин'
    )
    password_hash = models.CharField(
        max_length=255,
        verbose_name='Хеш пароля'
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name='Полное имя'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='cashier',
        verbose_name='Роль'
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',  # Этот related_name уже используется
        verbose_name='Магазин/Склад'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    last_login = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Последний вход'
    )
    permissions = models.JSONField(
        default=list,
        verbose_name='Права доступа'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего изменения'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    def set_password(self, raw_password):
        """Установка пароля"""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        """Проверка пароля"""
        return check_password(raw_password, self.password_hash)

    def update_last_login(self):
        """Обновление времени последнего входа"""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('confirmed', 'Подтвержден'),
        ('packing', 'Комплектуется'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
        ('completed', 'Выполнен'),
    ]

    order_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Номер заказа'
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Магазин/Склад'
    )
    customer_name = models.CharField(
        max_length=255,
        verbose_name='Имя клиента'
    )
    customer_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон клиента'
    )
    customer_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email клиента'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    total_sum = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name='Общая сумма'
    )
    products = models.ManyToManyField(
        Product,
        through='OrderItem',
        related_name='orders',
        verbose_name='Товары в заказе'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_orders',
        verbose_name='Создал'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Примечания'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Заказ #{self.order_number} - {self.customer_name}"

    def calculate_total(self):
        """Пересчет общей суммы заказа"""
        total = sum(item.total_price for item in self.items.all())
        self.total_sum = total
        self.save(update_fields=['total_sum'])
        return total


class OrderItem(models.Model):
    """Промежуточная модель для товаров в заказе"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за единицу'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def total_price(self):
        """Общая стоимость позиции"""
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        """Сохранение с автоматическим заполнением цены"""
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
        # Обновляем общую сумму заказа
        self.order.calculate_total()