# JWTAuth-RBAC

**Описание:**
Проект на Django с Django REST Framework для управления бизнес-элементами с поддержкой JWT-аутентификации и управления доступом на основе ролей (RBAC).

---

## Основные возможности

* Аутентификация пользователей через JWT.
* Разграничение прав доступа по ролям.
* CRUD операции с бизнес-элементами.
* Гибкая настройка правил доступа (`AccessRule`) для каждой роли.
* Пример работы с API для заказов (`Orders`) и продуктов (`Products`).

---

## Стек технологий

* Python 3.11+
* Django 4.x
* Django REST Framework
* PyJWT
* PostgreSQL

---

## Аутентификация

* Авторизация осуществляется через JWT.
* JWT необходимо передавать в заголовке `Authorization`:

```
Authorization: Bearer <your_jwt_token>
```
---

## Работа с ролями и доступом

* **Модель `User`** содержит поле `role`.
* **Модель `BusinessElement`** описывает сущности для доступа (`orders`, `products` и т.д.).
* **Модель `AccessRule`** задаёт права для каждой роли по элементам.
* **Пример действий**: `read`, `read_all`, `create`, `update`, `update_all`, `delete`, `delete_all`.
* **Permission `RoleBasedPermission`** проверяет права пользователя на доступ к view.

---

## Примеры запросов

**Получение списка продуктов (открытый доступ):**

```http
GET /api/products/
```

**Получение списка заказов (требуется роль с правом `read` на элемент `orders`):**

```http
GET /api/orders/
Authorization: Bearer <jwt_token>
```

**Пример ответа:**

```json
[
  {
    "id": 1,
    "owner": "1",
    "items": []
  }
]
```

---

