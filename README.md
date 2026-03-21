# EGE Informatics Trainer

Локальный тренажёр для подготовки к ЕГЭ по информатике на стеке **React 18 + FastAPI + Monaco + SQLite**.

Проект приведён к архитектуре, которая подходит для финального офлайн-продукта на одном изолированном Windows-ПК:
- **без MongoDB-сервиса**
- **с одним встроенным локальным хранилищем**
- **с сохранением текущих API-контрактов**
- **с возможностью раздавать собранный frontend прямо из backend**
- **с локальным profile/progress/mock/review persistence**
- **с основой под autosave через drafts API**

---

## Что теперь является текущим runtime

### Dev-режим
- backend: FastAPI на `http://127.0.0.1:8001`
- frontend: CRA dev server на `http://localhost:3000`
- storage: локальный SQLite-файл `backend/data/ege_trainer.sqlite3`

### Product-direction runtime
Если frontend собран (`frontend/build` существует), backend умеет раздавать его сам.
Это значит, что следующий шаг к desktop/exe уже не требует отдельного CRA-runtime в проде.

---

## Почему SQLite вместо MongoDB

Для одного офлайн-ПК SQLite лучше подходит, чем MongoDB, потому что:
- не нужен отдельный сервис и отдельный процесс БД
- нет дополнительной установки и администрирования
- база хранится в одном локальном файле
- проще упаковать в exe/setup
- надёжнее для single-user desktop сценария
- достаточно быстрый для профиля, прогресса, истории попыток, weekly review и mock exam

MongoDB была удобна как dev-сервис, но мешала реальному **one-click isolated-PC** сценарию.

---

## Что хранится локально

SQLite хранит:
- профиль ученика
- теорию
- практические задания
- прогресс по заданиям
- историю попыток
- weekly review
- mock exams
- drafts/autosave foundation
- metadata для seed/version контроля контента

База создаётся автоматически при первом старте backend.

---

## Переменные окружения

### `backend/.env`
```env
APP_DATA_DIR=./data
APP_DB_NAME=ege_trainer.sqlite3
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
SERVE_FRONTEND_BUILD=1
```

### `frontend/.env`
```env
REACT_APP_BACKEND_URL=http://127.0.0.1:8001
```

---

## Быстрый запуск под Windows

### 1. Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn server:app --host 127.0.0.1 --port 8001 --reload
```

### 2. Frontend (dev)
В новом окне PowerShell:
```powershell
cd frontend
npm install
npm start
```

---

## Проверка backend

```powershell
python backend_test.py
```

---

## Проверка product-direction режима

Собрать frontend и запустить только backend:

```powershell
cd frontend
npm install
npm run build

cd ..\backend
.\.venv\Scripts\Activate.ps1
uvicorn server:app --host 127.0.0.1 --port 8001
```

После этого приложение будет доступно через один backend-процесс на:
- `http://127.0.0.1:8001`

---

## Полезные endpoints

### Системные
- `GET /api/health`
- `POST /api/reseed`

### Профиль
- `GET /api/profile`
- `POST /api/profile`
- `PUT /api/profile`
- `POST /api/profile/reset`

### Теория и практика
- `GET /api/theory`
- `GET /api/theory/{task_number}`
- `GET /api/exercises/{task_number}`
- `GET /api/exercise/{exercise_id}`
- `POST /api/exercises/check`
- `POST /api/code/run`
- `POST /api/code/check`

### Прогресс и история
- `GET /api/progress`
- `GET /api/progress/{task_number}`
- `GET /api/attempts/{task_number}`

### Weekly review / mock exam
- `GET /api/weekly-review`
- `POST /api/weekly-review/start`
- `POST /api/weekly-review/complete`
- `GET /api/mock-exam`
- `POST /api/mock-exam/start`
- `PUT /api/mock-exam/{exam_id}/answer`
- `POST /api/mock-exam/{exam_id}/submit`
- `PUT /api/mock-exam/{exam_id}/flag`

### Drafts / autosave foundation
- `GET /api/drafts/{scope}`
- `PUT /api/drafts/{scope}`
- `DELETE /api/drafts/{scope}`

---

## Что уже учитывает архитектура

- один локальный профиль
- полностью офлайн-совместимое локальное хранилище
- отсутствие зависимости от внешней БД
- хранение истории попыток и прогресса в одном месте
- основа для autosave
- основа для будущей упаковки backend + frontend build в один локальный продукт
- UTF-8 как основная кодировка для текста и кода

---

## Что пока не является финальным packaging-этапом

В этой задаче **не делались**:
- финальный exe/setup
- финальная desktop-обёртка
- окончательный UI polish
- полный пересмотр всех 27 заданий

Но архитектура теперь подготовлена так, чтобы эти шаги делать уже без MongoDB и без лишних runtime-зависимостей.
