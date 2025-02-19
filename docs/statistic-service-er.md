# ER-диаграмма Statistic Service

```mermaid
erDiagram
    UserActivity {
        int id "уникальный идентификатор"
        int user_id "ID пользователя"
        string action_type "тип действия (лайк, комментарий, просмотр)"
        int target_id "ID поста/комментария"
        datetime timestamp "время события"
    }

    PostStatistic {
        int id "уникальный идентификатор"
        int post_id "ID поста"
        int views_count "количество просмотров"
        int likes_count "количество лайков"
        int comments_count "количество комментариев"
    }

    UserStatistic {
        int id "уникальный идентификатор"
        int user_id "ID пользователя"
        int posts_created "создано постов"
        int comments_written "написано комментариев"
        int likes_given "отправлено лайков"
    }
