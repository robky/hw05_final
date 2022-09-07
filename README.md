# Учебный проект. YaTube

**YaTube** - социальная сеть для дневников. После регистрации на сайте, любой пользователь может вести свои записи, читать записи других пользователей и оставлять комментарии.

Разработан по классической MVT архитектуре. Используется кэширование и пагинация. Регистрация реализована с верификацией данных, сменой и восстановлением пароля через почту. Модерация записей, работа с пользователями, создание групп осуществляется через панель администратора. Написаны тесты проверяющие работу сервиса.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/robky/hw05_final.git
```

Перейти в созданную директорию:

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
source venv/Scripts/activate
```

Обновить pip и установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
