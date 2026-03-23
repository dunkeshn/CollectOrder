from locust import HttpUser, task, between
import random

# --- Твои тестовые данные ---
# 1. Данные для входа (обязательно!!!)
# Создай пользователя в Django или используй существующего
TEST_USER = {
    "login": "testuser",  # <- ЗАМЕНИ НА РЕАЛЬНЫЙ ЛОГИН
    "password": "testpass123"  # <- ЗАМЕНИ НА РЕАЛЬНЫЙ ПАРОЛЬ
}

# 2. Данные для создания нового заказа (пример, подстрой под свою модель)
NEW_ORDER_DATA = {
    "order_number": "LOAD-TEST-001",
    "customer_name": "Load Test Customer",
    "customer_phone": "+70001234567",
    "status": "new"
}

# 3. Данные для создания нового товара (пример)
NEW_PRODUCT_DATA = {
    "article": "LOAD-001",
    "barcode": "200000000001",
    "name": "Load Test Product",
    "price": 999.99,
    "is_active": True
    # supplier и category нужно будет передать ID, если они обязательны
}
# --- Конец тестовых данных ---


class WarehouseUser(HttpUser):
    """
    Класс, имитирующий одного пользователя.
    Каждый такой "юзер" в тесте будет выполнять задачи (методы с @task)
    с паузой между ними от 1 до 3 секунд.
    """
    wait_time = between(1, 3)  # Пауза между задачами
    token = None  # Сюда сохраним JWT токен
    headers = {}  # Сюда сохраним заголовки с токеном

    def on_start(self):
        """
        Эта функция выполняется, когда каждый виртуальный пользователь СТАРТУЕТ.
        Идеально подходит для логина.
        """
        print(f"Пользователь {self} пытается залогиниться...")

        # 1. Пытаемся получить токен через JWT endpoint
        # Обычно это /api/token/ или /api/auth/token/
        # Убедись, что этот URL правильный для твоего проекта!
        login_response = self.client.post(
            "/api/token/",
            json={
                "username": TEST_USER["login"],
                "password": TEST_USER["password"]
            }
        )

        if login_response.status_code == 200:
            # Логин успешен, сохраняем токен
            self.token = login_response.json().get("access")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"Логин успешен для {self}. Токен получен.")
        else:
            print(f"ЛОГИН НЕ УДАЛСЯ для {self}!")
            # Если логин не удался, пользователь не сможет делать ничего дальше.
            # Обычно Locust все равно продолжит, но все запросы будут 401.
            # Это плохо для теста. Убедись, что данные правильные.

    # Задачи (task) - то, что будет делать пользователь.
    # Вес задачи (число в скобках) означает, насколько часто она будет выполняться.
    # Например, @task(5) будет выполняться в 5 раз чаще, чем @task(1).

    @task(5)
    def get_categories(self):
        """Прочитать список категорий (GET)"""
        if self.token:
            self.client.get("/api/categories/", headers=self.headers)
        else:
            self.client.get("/api/categories/")

    @task(5)
    def get_products(self):
        """Прочитать список товаров (GET)"""
        if self.token:
            self.client.get("/api/products/", headers=self.headers)
        else:
            self.client.get("/api/products/")

    @task(3)
    def get_suppliers(self):
        """Прочитать список поставщиков (GET)"""
        if self.token:
            self.client.get("/api/suppliers/", headers=self.headers)
        else:
            self.client.get("/api/suppliers/")

    # @task(2)
    # def create_order(self):
    #     """СОЗДАТЬ новый заказ (POST) - для объемного теста"""
    #     if not self.token:
    #         return  # Если не залогинились, не можем создавать
    #
    #     # randomize data to avoid unique constraint errors
    #     data = NEW_ORDER_DATA.copy()
    #     data["order_number"] = f"LOAD-{random.randint(10000, 99999)}"
    #
    #     self.client.post(
    #         "/api/orders/",
    #         json=data,
    #         headers=self.headers
    #     )

    # @task(2)
    # def create_product(self):
    #     """СОЗДАТЬ новый товар (POST) - для объемного теста"""
    #     if not self.token:
    #         return
    #
    #     data = NEW_PRODUCT_DATA.copy()
    #     data["article"] = f"LOAD-{random.randint(10000, 99999)}"
    #     data["barcode"] = str(random.randint(1000000000000, 9999999999999))
    #
    #     self.client.post(
    #         "/api/products/",
    #         json=data,
    #         headers=self.headers
    #     )

    @task(1)
    def get_specific_product(self):
        """Получить один конкретный товар (например, последний)"""
        # Сначала получим список, чтобы узнать ID (но это отдельный запрос)
        # В реальном тесте лучше иметь список заранее созданных ID.
        # Для простоты будем запрашивать товар с ID=1.
        if self.token:
            self.client.get("/api/products/1/", headers=self.headers)
        else:
            self.client.get("/api/products/1/")

    @task(1)
    def get_specific_order(self):
        """Получить один конкретный заказ"""
        if self.token:
            self.client.get("/api/orders/1/", headers=self.headers)
        else:
            self.client.get("/api/orders/1/")