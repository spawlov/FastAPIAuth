# FastAPI аутентификация
## Возможный вариант реализации аутентификации на JWT без дополнительных библиотек
***Проект на данный момент ещё находится в работе...***
### Как установить:

- Должен быть установлен [Python](https://www.python.org/) версии 3,11 или выше
- Должен быть установлен [Poetry](https://python-poetry.org/) лучше всего, если он будет установлен при помощи [PIPX](https://pipx.pypa.io/stable/)

Клонируйте репозиторий:

```shell
git clone https://github.com/spawlov/FastAPIAuth.git
```

Установите и активируйте виртуальное окружение:

```shell
poetry install
poetry shell
```

Перейдите в папку `src` и создайте файл `.env` (допустимые имена для различных конфигураций: ".env.dev", ".env.prod", ".env.test")

Содержимое файла:

```text
APP__DB__URL=sqlite+aiosqlite:///./db.sqlite3

# Далее могут быть другие настройки для файла `src.core.settings.py`
```

Сделайте миграции:

```shell
alembic upgrade head
```

Перейдите в папку `certs` создайте приватный и публичный ключи:

```shell
openssl genrsa -out jwt-private.pem 2048
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```

Вернитесь в папку `src` и запустите файл `main.py`:

```shell
python main.py
```

Документация будет доступна по ссылке: [http://0.0.0.0:8000/docs/](http://0.0.0.0:8000/docs/)

<hr>
