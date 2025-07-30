# AssemCloud

**AssemCloud** is a web application for managing industrial machine and module assemblies, storing blueprints and STEP models, automatically generating assembly trees, assigning tasks, and organizing work via Email and Telegram.

---   
![screen_demo](https://github.com/user-attachments/assets/dc1aefeb-e39e-4a59-9e97-1f3ab23cbe3e)

## Description

AssemCloud enables you to:

- Store and organize PDF blueprints and 3D STEP models of modules, assemblies, and parts.
- Automatically generate an **assembly tree** for products based on uploaded STEP files.
- Manage **Machines**, **Modules**, **Module Sets**, and **Parts** through a user-friendly admin interface.
- Create and assign **Tasks** to users, track their status and progress.
- Control access and permissions through configurable **Roles** (e.g., Admin, Engineer, Collaborator).  
- Send **Notifications** via Email and Telegram bot when tasks are created or updated.  
- Import data files via web forms to quickly onboard new machines or components.

The project is built on **Django** and organized into two main components:

1. **assembler/** — Django project scaffolding, settings for different environments, static assets, templates, and routing.  
2. **assembler/core/** — Core application containing models (Machine, Module, Part, etc.), forms, views, services, and the Telegram bot integration.

---

## Project Structure

```

.
├── assembler/               # Django project
│   ├── assembler/           # Settings, static files, templates
│   ├── core/                # Business logic: models, views, forms, services
│   ├── manage.py            # Django CLI entry point
│   ├── pyproject.toml       # Metadata & dependencies if using Poetry
│   └── requirements.txt     # Python dependencies for pip
└── db/
└── createbasetable.sql  # Initial database setup script

````

---

## Technologies & Dependencies

- **Python 3.8+**  
- **Django 4.2.20**  
- **MySQL** (via `mysqlclient`) if you prefer MySQL  
- **psycopg2‑binary**, **mysqlclient** — database drivers  
- **django-extensions**, **django-mptt**, **django-select2**, **django-widget-tweaks**  
- **channels 4.2.2** for WebSocket support  
- **python-telegram-bot** (via `TELEGRAM_TOKEN`) for Telegram integration  
- **Celery** + **Redis** (optional) for background tasks  
- **black**, **flake8**, **ruff** for code formatting and linting  
- **pandas**, **numpy**, **openpyxl** for data processing  
- **Sphinx**, **sphinx-rtd-theme** for documentation  
- **python-decouple** for environment variable management  

> See the full list in `requirements.txt`.
---

## Installation & Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/alex-1-tech/AssemCloud.git
   cd AssemCloud
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**

   * With `pip`:

     ```bash
     pip install -r requirements.txt
     ```
   * Or with `Poetry`:

     ```bash
     poetry install
     ```

4. **Configure environment variables**
   Create a `.env` file in the project root (or export variables):

   ```dotenv
   SECRET_KEY=your_secret_key
   DEBUG=True
   PASSWORD=your_password_for_mysql
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   CSRF_TRUSTED_ORIGINS=your_address
   EMAIL_HOST=smtp.example.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=you@example.com
   DEFAULT_FROM_EMAIL=you@example.com
   EMAIL_HOST_PASSWORD=your_email_password
   TELEGRAM_TOKEN=your_telegram_bot_token
   ```

5. **Run database migrations and initialize**

   ```bash
   python manage.py migrate
   # Optionally load initial SQL data
   psql -d assemcloud -f db/createbasetable.sql
   ```

6. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**

   ```bash
   python manage.py runserver
   ```

   Open [http://localhost:8000](http://localhost:8000) in your browser to access the app.

---

## Usage Examples

1. **Importing a Module**

   * Go to **Modules → Import** in the web interface.
   * Upload STEP and PDF files.
   * After upload, the system generates and displays the assembly tree automatically.

2. **Creating a Task**

   * Navigate to **Tasks → Create**.
   * Fill in the “Assignee”, “Description”, and attach any relevant files.
   * The assigned user receives notifications via Email and Telegram.

3. **Viewing the Assembly Tree**

   * Open a Module’s detail page.
   * The **Assembly Tree** component visualizes the hierarchical structure.

---

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository.
2. **Create** a new branch:

   ```bash
   git checkout -b feature/awesome-feature
   ```
3. **Commit** your changes:

   ```bash
   git commit -m "Add awesome feature"
   ```
4. **Push** to your fork:

   ```bash
   git push origin feature/awesome-feature
   ```
5. **Open** a Pull Request and describe your changes.

Please adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/) and write tests for new features.

---

## License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.
=======
