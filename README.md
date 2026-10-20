## Требования
- Python 3.10+
- Node.js 18+ и npm

## Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/grilaw/bot-site
cd repo
```

### 2. Создать и активировать виртуальное окружение

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установить Python-зависимости
```bash
pip install -r requirements.txt
```

### 4. Собрать React-шаблоны
```bash
cd school-pgs
npm install
npm run build
cd ..
```

### 5. Применить миграции и запустить сервер
```bash
cd schooldj
python manage.py migrate
python manage.py runserver
```

Сервер будет доступен на http://127.0.0.1:8000/
