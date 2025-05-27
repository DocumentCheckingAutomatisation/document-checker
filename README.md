# Система автоматического нормоконтроля

Система проверяет оформление студенческих работ (ВКР, курсовых, отчетов по практике) в соответствии с требованиями ГОСТ 7.32-2017 и требованиями Иркутского государственного университета.
LaTeX работы должны быть оформлены по шаблону для студенческих работ ИГУ: https://github.com/Alyona1619/LaTeXTemplate.


## 📌 Возможности:
 - Просмотр доступных для проверки типов работ и правил
- Проверка документов формата .docx\n
- Проверка документов формата LaTeX (.tex и .sty)
- Изменение правил (только для нормоконтролеров)
- Просмотр списка студентов, проверивших свои работы (только для нормоконтролеров)



#### ✅ В LaTeX работах проверяется:
- структура работы (главы и разделы)
- наличие ключевых слов во введении, выделенных жирным
- отсутствие жирности, курсива, подчеркиваний в тексте работы
- оформление списков (знаки препинания во вводном предложении и элементах, строчные/заглавные первые буквы элементов)\n"
- наличие пары объект-ссылка у рисунков, таблиц, приложения, списка использованных источников
- расстояние от ссылки до рисунка/таблицы
- использование правильных кавычек
- правильность .sty файла (размер шрифта, межстрочный интервал, отступы, формат подписей и другое)

#### ✅ В docx работах проверяется:
- структура работы (главы и разделы 'Выводы по главе')
- размер шрифта всего текста
- ключевые слова во введении выделенные жирным
- рисунки, таблицы, приложения, список использ. источн. (наличие пары объект-ссылка)

## 🚀 Развёртывание с Docker

### 1. Установка зависимостей

Убедитесь, что на машине установлены:
- Docker
- Git
- Docker Compose (v2+)

### 2. Клонирование репозитория

```bash
git clone https://github.com/your-username/document-checker.git
cd document-checker
```

### 3. Сборка и запуск контейнера
```bash
docker compose build
docker compose up -d
```

После запуска API будет доступен по адресу:
📍 http://localhost:8080
Swagger документация по адресу:
📍http://127.0.0.1:8080/docs

## 🚀 Развертывание вместе с Telegram-ботом

Для полноценной работы системы автоматического нормоконтроля необходимо запустить два компонента:

- document-checker — основной сервис для проверки документов

- tg-bot-doccheck — Telegram-бот для взаимодействия с пользователями

Оба компонента запускаются с помощью Docker и Docker Compose.

### 1. Клонирование репозиториев
Клонируйте оба репозитория на одну директорию виртуальной машины или сервера:

```bash
git clone https://github.com/your-username/document-checker.git
git clone https://github.com/your-username/tg-bot-doccheck.git
```
Предполагается, что структура каталогов выглядит так:

```bash
/project-root
├── document-checker/
└── tg-bot-doccheck/
```

### 2. Создание docker-compose.yml
Создайте в корне (/project-root) файл docker-compose.yml следующего содержания:
```yaml
version: "3.8"

services:
  document-checker:
    build: ./document-checker
    container_name: document-checker
    restart: always
    ports:
      - "8080:8080"
    volumes:
      - ./document-checker/application.log:/app/application.log
    networks:
      - doccheck-net

  tg-bot-doccheck:
    build: ./tg-bot-doccheck
    container_name: tg-bot-doccheck
    restart: always
    depends_on:
      - document-checker
    volumes:
      - ./tg-bot-doccheck/bot.log:/app/bot.log
      - ./tg-bot-doccheck/roles.db:/app/roles.db
    networks:
      - doccheck-net

networks:
  doccheck-net:
    driver: bridge
```    
    
### 3. Настройка переменных окружения
Убедитесь, что в Telegram-боте в файле .env указан правильный URL системы document-checker:

```python
API_URL = "http://document-checker:8080"
```

### 4. Сборка и запуск
Выполните из корневой директории:

```bash
docker compose build
docker compose up -d
```

## 📡 API документация

### 🔍 Получение типов документов

**GET** `/api/documents/options`

Возвращает список доступных типов документов, которые можно отправить на проверку (например: `diploma`, `course_work`, `practice_report`).

##### Пример ответа:
```json
[
  "diploma",
  "course_work",
  "practice_report"
]
```

### 📋 Получение правил для документа

**GET** `/api/rules/{doc_type}`

Параметры:

doc_type — тип документа (diploma, course_work, practice_report)

Возвращает список правил, по которым будет производиться проверка указанного типа документа.

##### Пример запроса:
```bash
GET /api/rules/diploma
```

##### Пример ответа:
```json
  {
  "common_rules": {
    "font": "Times New Roman",
    "font_size": 14.0,
    "line_spacing": 1.5
    }
  }
```

### ✏️ Изменение правила для одного типа документа

**POST** `/api/rules/update`

##### Параметры (в form-data или query строке):
- doc_type — тип документа (diploma, course_work, practice_report)
- rule_key — ключ правила (например: font_size)
-new_value — новое значение правила
- 
##### Пример запроса:
```bash
POST /api/rules/update
?doc_type=course_work&rule_key=common_rules.font_size&new_value=12.0
```

##### Пример ответа:
```json
{
  "message": "Правило font_size успешно обновлено"
}
```

### ✏️ Изменение одного правила для всех типов документов

**POST** `/api/rules/update/all`

##### Параметры:

- rule_key — ключ правила
- new_value — новое значение
- 
##### Пример запроса:
```bash
POST /api/rules/update/all
?doc_type=course_work&rule_key=common_rules.font_size&new_value=12.0
```

##### Пример ответа:
```json
{
  "message": "Правило font_size успешно обновлено для всех типов документов", 
  "updated": ["diploma", "course_work", "practice_report"]
}
```

### 📝 Проверка .tex и .sty файлов (LaTeX)

**POST** `/api/documents/validate/latex`

##### Параметры:
- tex_file — .tex файл (тип: file)
- sty_file — .sty файл (тип: file)
- doc_type — тип документа (строка: diploma, course_work, practice_report)

##### Пример запроса (multipart/form-data):
- tex_file: main.tex
- sty_file: settings.sty
- doc_type: diploma

##### Пример ответа:
```json
{
  "valid": true,
  "found": [...],
  "errors": []
}
```

### 📝 Проверка .docx файлов
**POST** `/api/documents/validate/single_file`

##### Параметры:
- file — документ Word (.docx) (тип: file)
- doc_type — тип документа (строка: diploma, course_work, practice_report)

##### Пример запроса (multipart/form-data):
- file: work.docx
- doc_type: practice_report

##### Пример ответа:
```json
{
  "valid": true,
  "found": [...],
  "errors": []
}
```

### ⛔ Возможные коды ошибок

| Код | Причина                                                                 |
|-----|-------------------------------------------------------------------------|
| 400 | Неверный тип документа, неподдерживаемый формат файла, ошибка валидации |
| 500 | Внутренняя ошибка сервера                                               |


## 📬 Обратная связь
Если у вас есть предложения или вы нашли ошибку, создайте issue или отправьте Pull Request 🙌