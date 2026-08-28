# 📝 DVS Blog

> A simple, lightweight **blog system** built with Flask — write Markdown articles, manage them in an admin panel, and upload files.

**DVS Blog** is a self-hosted blog platform. It renders **Markdown** articles (with code highlighting, tables, and TOC), provides an admin dashboard with login, article creation/deletion, and file upload — all with a clean, themeable UI.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Markdown Articles** | Write articles in Markdown (extra, codehilite, tables, TOC) |
| 🏠 **Blog Homepage** | Lists all articles newest-first |
| 🔐 **Admin Login** | SHA-256 password protected admin access |
| 📝 **Create/Delete Articles** | Manage articles from the admin dashboard |
| 📎 **File Upload** | Upload images/videos/audio/documents (100MB max) |
| 🎨 **Themeable UI** | Light/dark theme toggle |

---

## 🔌 Routes

| Route | Description |
|-------|-------------|
| `/` | Blog homepage (article list) |
| `/docs/<filename>` | Render an article (Markdown → HTML) |
| `/admin` | Admin login |
| `/admin/dashboard` | Admin dashboard |
| `/admin/create_article` | Create article (POST) |
| `/admin/upload_file` | Upload file (POST) |
| `/admin/delete_article` | Delete article (POST) |
| `/admin/logout` | Log out |
| `/uploads/<filename>` | Serve uploaded files |
| `/css.css` | Serve stylesheet |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- `flask`, `markdown`

### Install & Run

```bash
# Install dependencies
pip install flask markdown

# Run the blog
python app.py
```

Then open `http://localhost:50` in your browser.

### Admin
- Visit `/admin`, enter the admin password (SHA-256 configured in `app.py`)
- The admin password hash is set via `ADMIN_PASSWORD_HASH` in `app.py`

---

## 📁 Project Structure

```
blog/
├── app.py              # Main Flask application
├── templates/          # HTML templates
│   ├── index.html      # Blog homepage
│   ├── article.html    # Article view
│   ├── admin.html      # Admin dashboard
│   ├── admin_login.html# Admin login
│   ├── base.html       # Layout
│   └── css.css         # Stylesheet (62KB)
├── docs/               # Markdown articles (created at runtime)
├── uploads/            # Uploaded files (created at runtime)
└── README.md           # This document
```

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## ⚠️ Security Note

> The admin password is stored as an SHA-256 hash — override `ADMIN_PASSWORD_HASH` with your own value before production use. For higher security, consider using a salted hash (e.g., werkzeug or argon2).
