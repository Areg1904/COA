# ER-диаграмма User Service

```mermaid
erDiagram
    User {
        int id "уникальный идентификатор"
        string username "уникальное имя пользователя"
        string email "уникальная почта"
        string password_hash "хеш пароля"
        datetime created_at "дата регистрации"
    }

    Profile {
        int id "уникальный идентификатор"
        int user_id "ссылка на пользователя"
        string first_name "имя"
        string last_name "фамилия"
        string bio "биография"
        string avatar_url "ссылка на аватар"
    }

    Role {
        int id "уникальный идентификатор"
        int user_id "ссылка на пользователя"
        string role_name "название роли"
        string permissions "разрешения, доступные роли"
        datetime assigned_at "время назначения роли"
    }

    User ||--o{ Profile : "имеет"
    User ||--o{ Role : "имеет роль"
