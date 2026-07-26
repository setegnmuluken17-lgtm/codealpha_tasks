# 📁 Project Structure - SocialHub

```
CodeAlpha_SocialMediaPlatform/
│
├── 📄 README.md                          # Main documentation
├── 📄 SETUP_GUIDE.md                     # Quick start guide
├── 📄 manage.py                          # Django management script
│
├── 📂 socialmedia/                       # Main Django project
│   ├── __init__.py
│   ├── settings.py                       # Django configuration
│   ├── urls.py                           # Main URL routing
│   ├── asgi.py                           # ASGI config
│   ├── wsgi.py                           # WSGI config
│   └── __pycache__/
│
├── 📂 accounts/                          # User authentication app
│   ├── 📂 migrations/                    # Database migrations
│   │   ├── 0001_initial.py              # UserProfile & Follow migrations
│   │   └── __init__.py
│   ├── 📂 templates/
│   │   └── 📂 accounts/
│   │       ├── register.html             # Registration page
│   │       ├── login.html                # Login page
│   │       ├── profile.html              # User profile page
│   │       ├── edit_profile.html         # Edit profile page
│   │       ├── followers_list.html       # View followers
│   │       └── following_list.html       # View following
│   ├── __init__.py
│   ├── admin.py                          # Admin configuration
│   ├── apps.py                           # App configuration
│   ├── forms.py                          # Registration, Login, Profile forms
│   ├── models.py                         # UserProfile & Follow models
│   ├── signals.py                        # Auto-create profile signal
│   ├── tests.py
│   ├── urls.py                           # Account URL routes
│   ├── views.py                          # Auth & profile views
│   └── __pycache__/
│
├── 📂 posts/                             # Posts & social features app
│   ├── 📂 migrations/                    # Database migrations
│   │   ├── 0001_initial.py              # Post, Like, Comment migrations
│   │   └── __init__.py
│   ├── 📂 templates/
│   │   └── 📂 posts/
│   │       ├── feed.html                 # News feed
│   │       ├── post_detail.html          # Full post with comments
│   │       ├── explore.html              # Public post explorer
│   │       ├── create_post.html          # Post creation page
│   │       ├── edit_post.html            # Edit post page
│   │       ├── delete_post.html          # Delete post confirmation
│   │       └── delete_comment.html       # Delete comment confirmation
│   ├── __init__.py
│   ├── admin.py                          # Post, Like, Comment admin config
│   ├── apps.py                           # App configuration
│   ├── forms.py                          # PostForm & CommentForm
│   ├── models.py                         # Post, Like, Comment models
│   ├── tests.py
│   ├── urls.py                           # Post URL routes
│   ├── views.py                          # Feed & post views
│   └── __pycache__/
│
├── 📂 templates/                         # Shared templates
│   └── base.html                         # Main layout template
│
├── 📂 media/                             # User uploads (auto-created)
│   ├── profile_pictures/                 # User profile photos
│   ├── cover_photos/                     # User cover photos
│   └── post_images/                      # Post images
│
├── 📂 static/                            # Static files (CSS, JS)
│   ├── css/
│   ├── js/
│   └── img/
│
└── 📂 __pycache__/                       # Python cache
```

---

## 🗂️ File Purpose Guide

### Root Level
| File | Purpose |
|------|---------|
| `manage.py` | Django CLI tool |
| `requirements.txt` | Python dependencies |
| `db.sqlite3` | Old SQLite database, no longer used by default |
| `README.md` | Full documentation |
| `SETUP_GUIDE.md` | Quick start guide |

### accounts/ App
| File | Purpose |
|------|---------|
| `models.py` | UserProfile & Follow models |
| `forms.py` | Registration, Login, Profile forms |
| `views.py` | Auth & profile views |
| `urls.py` | Account URL patterns |
| `admin.py` | Admin panel setup |
| `signals.py` | Auto-create profile on user creation |
| `templates/` | HTML templates for auth pages |
| `migrations/` | Database schema changes |

### posts/ App
| File | Purpose |
|------|---------|
| `models.py` | Post, Like, Comment models |
| `forms.py` | PostForm, CommentForm |
| `views.py` | Feed, post, like, comment views |
| `urls.py` | Post URL patterns |
| `admin.py` | Admin panel setup |
| `templates/` | HTML templates for posts |
| `migrations/` | Database schema changes |

### Templates Hierarchy
```
base.html (main layout)
├── accounts/register.html
├── accounts/login.html
├── accounts/profile.html
├── accounts/edit_profile.html
├── accounts/followers_list.html
├── accounts/following_list.html
├── posts/feed.html
├── posts/post_detail.html
├── posts/explore.html
├── posts/create_post.html
├── posts/edit_post.html
├── posts/delete_post.html
└── posts/delete_comment.html
```

---

## 🔄 File Relationships

### Models → Views → Templates → URLs

**User Registration Flow:**
```
models.py (User)
    ↓
forms.py (RegistrationForm)
    ↓
views.py (register view)
    ↓
register.html template
    ↓
urls.py (/accounts/register/)
```

**Feed Display Flow:**
```
models.py (Post, Like, Comment, Follow)
    ↓
views.py (feed view)
    ↓
feed.html template
    ↓
urls.py (/posts/)
```

**Profile View Flow:**
```
models.py (UserProfile, Post)
    ↓
views.py (profile view)
    ↓
profile.html template
    ↓
urls.py (/accounts/profile/<username>/)
```

---

## 📊 Database Files

### Migrations
Located in `*/migrations/` directories:
- `0001_initial.py` - First schema creation
- `0002_*.py` - Schema updates (if any)

### Database
- PostgreSQL is used by default. Connection settings are read from `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, and `POSTGRES_PORT`.

---

## 📦 Key Dependencies

### In requirements.txt
```
Django==6.0.3
Pillow==10.1.0
psycopg[binary]==3.2.3
```

- **Django** - Web framework
- **Pillow** - Image processing
- **psycopg** - PostgreSQL database driver

---

## 🎯 How Files Work Together

### User Registration Example

1. User visits `/accounts/register/`
2. `urls.py` routes to `register()` view
3. `register()` loads `RegistrationForm` from `forms.py`
4. Form renders `register.html` template
5. User submits form
6. `RegistrationForm` validates data using `models.py` rules
7. User created via `models.User`
8. Signal in `signals.py` auto-creates `UserProfile`
9. User redirected to login
10. Admin can manage in Django admin (`admin.py`)

### Post Creation Example

1. Authenticated user goes to `/posts/create/`
2. `urls.py` routes to `create_post()` view
3. View loads `PostForm` from `forms.py`
4. Form renders `create_post.html`
5. User submits form with content & image
6. Form validates using `Post` model rules
7. Post saved to database
8. User redirected to `/posts/`
9. Feed view queries posts from `models.Post`
10. `feed.html` template displays posts

---

## 🔐 Important Security Files

- `settings.py` - Security settings (CSRF, password validators)
- `signals.py` - Ensures profile creation for all users
- Forms with `clean()` methods - Input validation

---

## 📱 Template Files Overview

### Base Template (base.html)
- Navigation bar
- Message display
- Footer
- Static CSS/JS links
- Block structure for child templates

### Page Templates
- All inherit from base.html
- Each has specific content blocks
- Bootstrap grid layout
- Responsive design

---

## 🚀 Deployment Files

Ready for production:
- `wsgi.py` - WSGI application
- `asgi.py` - ASGI application
- `settings.py` - Configuration
- `requirements.txt` - Dependencies

---

## 📝 Documentation Files

- `README.md` - Full project documentation
- `SETUP_GUIDE.md` - Quick start guide
- `IMPLEMENTATION_SUMMARY.md` - Feature details
- This file - Project structure guide

---

## 🔧 How to Add New Features

### Adding a New Model

1. Edit `app/models.py` - Define model
2. Create migration: `python manage.py makemigrations`
3. Apply: `python manage.py migrate`
4. Edit `app/admin.py` - Register in admin
5. Edit `app/forms.py` - Create model form
6. Edit `app/views.py` - Create view
7. Create template in `app/templates/app/`
8. Edit `app/urls.py` - Add URL route

### Adding a New View

1. Add function to `app/views.py`
2. Create template in `app/templates/app/`
3. Add URL pattern to `app/urls.py`
4. Add link in template or navigation

---

## 📂 Automatic Directories

These are created automatically:
- `__pycache__/` - Python bytecode cache
- `media/` - User uploads
- `migrations/` - Django migrations
- `.git/` - Version control (if using Git)

---

## 🎯 File Size Overview

| Type | Size | Count |
|------|------|-------|
| Python files | ~1500 lines | 15+ |
| Templates | ~2000 lines | 13 |
| CSS (Bootstrap) | External CDN | - |
| Database | ~100KB | 1 |

---

## ✅ All Files Present

The project includes all necessary files for a complete social media platform.

**To run:** `python manage.py runserver`

---

*Project Structure: Complete and Organized*
