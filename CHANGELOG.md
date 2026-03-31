# Changelog API

Документация изменений и текущего функционала API на основе OpenAPI-спецификации.

## 🔐 Аутентификация и пользователи (Auth & Users)

- **Регистрация пользователя**  
  `POST /api/v1/auth/register`

- **Вход в систему**  
  `POST /api/v1/auth/login`

- **Выход из системы**  
  `POST /api/v1/auth/logout`

- **Профиль текущего пользователя**  
  `GET /api/v1/users/profile`

- **Загрузка аватара**  
  `POST /api/v1/users/upload-avatar`

- **Смена пароля**  
  `POST /api/v1/users/change-password`

---

## 📅 Мероприятия (Events)

- **Создание мероприятия**  
  `POST /api/v1/events/`

- **Список мероприятий с фильтрацией**  
  `GET /api/v1/events/`  
  *Параметры: пагинация (`page`, `limit`), фильтр по категории, статусу, поиску, диапазону дат (`start_from`, `start_to`)*

- **Детали мероприятия**  
  `GET /api/v1/events/{event_id}`

- **Обновление мероприятия** (только организатор)  
  `PUT /api/v1/events/{event_id}`

- **Удаление мероприятия** (только организатор)  
  `DELETE /api/v1/events/{event_id}`

- **Отметка «Проверено»** (модерация)  
  `POST /api/v1/events/{event_id}/reviewed`

- **Отметка «Требуется доработка»** с указанием причины  
  `POST /api/v1/events/{event_id}/needs-edit`

---

## 🎤 Сессии мероприятий (Sessions)

- **Создание сессии**  
  `POST /api/v1/sessions/`

- **Информация о сессии**  
  `GET /api/v1/sessions/{session_id}`

- **Список сессий по мероприятию**  
  `GET /api/v1/sessions/event/{event_id}`

---

## 📚 Справочники и перечисления (Enums)

- **Статусы мероприятий**  
  `GET /api/v1/enums/event-statuses`  
  *Возможные значения: `draft`, `pending`, `reviewed`, `published`, `needs_edit`, `completed`*

- **Статусы сессий**  
  `GET /api/v1/enums/session-statuses`  
  *Возможные значения: `draft`, `pending`, `reviewed`, `published`, `completed`*

- **Категории мероприятий**  
  `GET /api/v1/enums/categories`

---

## 🛠️ Административная панель (Admin UI)

*HTML-страницы для ручного управления*

- **Вход в админку**  
  `GET /admin/login`

- **Регистрация администратора**  
  `GET /admin/register`

- **Дашборд**  
  `GET /admin/dashboard`

- **Создание мероприятия (форма)**  
  `GET /admin/events/create`

- **Детали мероприятия (админка)**  
  `GET /admin/events/{event_id}`

- **Создание сессии (форма)**  
  `GET /admin/events/{event_id}/sessions/create`

- **Профиль администратора**  
  `GET /admin/profile`

---

## 🏠 Общее

- **Корневой эндпоинт (проверка доступности)**  
  `GET /`