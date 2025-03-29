# ER-диаграмма Post and Comment Service

```mermaid
erDiagram
    Post {
        int id "уникальный идентификатор"
        int user_id "автор поста"
        string title "заголовок"
        text content "содержимое"
        datetime created_at "дата создания"
    }

    Comment {
        int id "уникальный идентификатор"
        int post_id "ID поста"
        int user_id "автор комментария"
        text content "текст комментария"
        datetime created_at "дата создания"
    }

    Like {
        int id "уникальный идентификатор"
        int user_id "автор лайка"
        int entity_id "пост или комментарий"
        datetime created_at "дата создания"
    }

    Post ||--o{ Comment : "имеет"
    Post ||--o{ Like : "имеет"
    Comment ||--o{ Like : "имеет"