# EGE Informatics Trainer

Desktop-приложение для подготовки к ЕГЭ по информатике.  
Проект работает локально: теория, практика, прогресс, weekly review и пробные экзамены в одном приложении.

## Что внутри

- 27 заданий ЕГЭ с теорией и практикой
- отдельные режимы: `Theory`, `Practice`, `Weekly Review`, `Mock Exam`, `Progress`
- кодовые задачи на Python с проверкой и тестами
- локальное хранение прогресса в SQLite
- desktop-режим (Electron) и dev-режим с автоперезапуском

## Стек

- Frontend: React 18, Monaco Editor
- Backend: FastAPI, Uvicorn
- Storage: SQLite
- Desktop shell: Electron

## Структура проекта

- `frontend/` — интерфейс и страницы приложения
- `backend/` — API, проверка заданий, работа с хранилищем
- `content/` — учебный контент:
  - `content/theory/taskNN.json`
  - `content/tasks/taskNN/lesson_01.json`
- `desktop/` — вход для desktop-окна Electron

## Быстрый запуск (рекомендуется)

1. Подготовить backend-окружение (один раз):
   - создать `backend/.venv`
   - установить зависимости из `backend/requirements.txt`
2. Установить Node-зависимости:
   - в корне проекта: `npm install`
   - во frontend: `npm --prefix frontend install`
3. Запустить desktop dev-режим:
   - `start-desktop-dev.cmd`

Что это делает:
- автоматически поднимает backend
- автоматически поднимает frontend dev server
- открывает приложение в отдельном desktop-окне
- при изменениях в `frontend/**`, `backend/**`, `content/**` изменения подхватываются без ручной пересборки

## Полезные команды

- `npm run desktop:dev` — полный dev-режим (backend + frontend + Electron)
- `npm run desktop:build` — сборка frontend
- `npm run desktop:run` — запуск desktop с backend без frontend dev server (через собранный frontend)

## Данные и локальное хранение

- База хранится в `backend/data/ege_trainer.sqlite3`
- Все пользовательские данные остаются на локальной машине

## Для контента

Если редактируете задания, правьте рабочие файлы в `content/`:
- теория: `content/theory/taskNN.json`
- практика: `content/tasks/taskNN/lesson_01.json`

Это именно те источники, которые используются текущим runtime.
