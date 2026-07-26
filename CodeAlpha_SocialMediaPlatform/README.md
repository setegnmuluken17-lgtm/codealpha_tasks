# SocialHub - Social Media Platform

A full-featured Django-based social media platform with user authentication, profiles, posts, likes, comments, and follower system.

## Project Brief

SocialHub is a Django social media web application built for sharing updates, connecting with friends, and communicating in private message threads. Users can create profiles, follow each other, publish text/image/video posts, react with likes and comments, and browse a personalized feed or public explore page.

The platform also includes 24-hour stories with story views and likes, direct messaging between mutual friends, voice message uploads/recording, profile details such as bio and birthday, dark/light mode, media upload support, and PostgreSQL database configuration. It is designed as a complete educational full-stack project that demonstrates authentication, CRUD operations, relationships between users, media handling, and user-to-user interaction workflows.

### Core Capabilities
- User registration, login, logout, and profile editing
- Follow/unfollow system with mutual-friend messaging
- Text, image, and video posts
- Likes, comments, post editing, and post deletion
- 24-hour stories with viewers and story likes
- Private text and voice messages between friends
- Profile bio, birthday, profile photo, and cover photo
- Personalized feed and public all-posts/explore page
- Dark/light theme toggle
- PostgreSQL-backed Django database

## ✅ Features Implemented

### 1. User Registration & Login
- User registration with email validation
- Login with username or email
- Remember me functionality
- Password validation and security
- Automatic UserProfile creation on signup

### 2. User Profiles
- Extended user profiles with bio, location, website
- Profile picture and cover photo upload
- Birth date tracking
- Profile stats (posts, followers, following)
- Edit profile functionality

### 3. Follow System
- Follow/unfollow users
- View followers and following lists
- Follow recommendations on profiles
- Follow status tracking

### 4. Create Posts
- Rich text post creation
- Optional image uploads
- Character limit validation (5000 chars)
- Post editing and deletion
- Timestamps and metadata

### 5. Like System
- Like/unlike posts
- Like counters
- Like tracking to prevent duplicates
- Visual like indicators

### 6. Comment System
- Add comments to posts
- Comment deletion (author only)
- Character limit validation (1000 chars)
- Comments preview on feed
- Full comments section on post detail

### 7. News Feed
- Personalized feed showing posts from followed users
- Infinite scroll potential
- Post statistics display
- Quick access to user actions

### 8. Explore
- Browse all public posts
- Discover content without following
- Like/comment on posts while exploring

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- PostgreSQL server

### Installation

1. **Clone or navigate to the project:**
```bash
cd CodeAlpha_SocialMediaPlatform
```

2. **Create virtual environment (optional but recommended):**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure PostgreSQL connection:**
```bash
# Windows PowerShell
$env:POSTGRES_DB="socialmedia_db"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="your_password"
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5432"
```

Create the PostgreSQL database if it does not already exist:
```sql
CREATE DATABASE socialmedia_db;
```

5. **Run migrations:**
```bash
python manage.py migrate
```

6. **Create superuser (admin account):**
```bash
python manage.py createsuperuser
```

7. **Collect static files (optional for development):**
```bash
python manage.py collectstatic --noinput
```

8. **Start the development server:**
```bash
python manage.py runserver
```

The server will run at `http://localhost:8000`

## 📍 URL Routes

### Authentication
- `/accounts/register/` - Register new account
- `/accounts/login/` - Login to account
- `/accounts/logout/` - Logout

### Profiles
- `/accounts/profile/<username>/` - View user profile
- `/accounts/edit-profile/` - Edit your profile
- `/accounts/<username>/followers/` - View user's followers
- `/accounts/<username>/following/` - View user's following

### Follow
- `/accounts/follow/<username>/` - Follow user
- `/accounts/unfollow/<username>/` - Unfollow user

### Posts & Feed
- `/` - Home (redirects to feed if logged in, explore if not)
- `/posts/` - News feed (authenticated)
- `/posts/create/` - Create new post
- `/posts/<id>/` - View post detail with comments
- `/posts/<id>/like/` - Like/unlike post
- `/posts/<id>/edit/` - Edit post (author only)
- `/posts/<id>/delete/` - Delete post (author only)
- `/posts/comment/<id>/delete/` - Delete comment (author only)
- `/posts/explore/` - Explore all posts

### Admin
- `/admin/` - Django admin panel

## 🛠️ Database Models

### User Profile
```
UserProfile
├── user (OneToOneField to User)
├── bio (TextField)
├── profile_picture (ImageField)
├── cover_photo (ImageField)
├── location (CharField)
├── website (URLField)
├── birth_date (DateField)
├── joined_date (DateTimeField)
└── updated_date (DateTimeField)
```

### Follow
```
Follow
├── follower (ForeignKey to User)
├── following (ForeignKey to User)
└── created_at (DateTimeField)
```

### Post
```
Post
├── author (ForeignKey to User)
├── content (TextField)
├── image (ImageField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

### Like
```
Like
├── post (ForeignKey to Post)
├── user (ForeignKey to User)
└── created_at (DateTimeField)
```

### Comment
```
Comment
├── post (ForeignKey to Post)
├── author (ForeignKey to User)
├── content (TextField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

## 📁 Project Structure

```
CodeAlpha_SocialMediaPlatform/
├── accounts/
│   ├── migrations/
│   ├── templates/accounts/
│   │   ├── register.html
│   │   ├── login.html
│   │   ├── profile.html
│   │   ├── edit_profile.html
│   │   ├── followers_list.html
│   │   └── following_list.html
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── posts/
│   ├── migrations/
│   ├── templates/posts/
│   │   ├── feed.html
│   │   ├── post_detail.html
│   │   ├── explore.html
│   │   ├── create_post.html
│   │   ├── edit_post.html
│   │   ├── delete_post.html
│   │   └── delete_comment.html
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── socialmedia/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── templates/
│   └── base.html
├── media/ (uploaded files)
├── static/ (static files)
├── db.sqlite3 (SQLite database)
├── manage.py
└── requirements.txt
```

## 🎨 Technology Stack

- **Backend:** Django 6.0.3
- **Database:** PostgreSQL
- **Frontend:** Bootstrap 5.1.3
- **Image Handling:** Pillow 10.1.0
- **Authentication:** Django built-in auth system

## 📝 Usage Examples

### Register New User
1. Go to `/accounts/register/`
2. Fill in username, email, password
3. Click "Sign Up"
4. Automatically logged in after registration

### Create a Post
1. Navigate to `/posts/` (Feed)
2. Fill in post content in the text box
3. Optionally add an image
4. Click "Post"

### Like a Post
- Click the heart icon on any post
- Like count will increment

### Add a Comment
1. Click "Comment" button on a post
2. Go to post detail page
3. Fill in comment text
4. Click "Comment"

### Follow a User
1. Visit user's profile
2. Click "Follow" button
3. User added to your following list

## 🔒 Security Features

- CSRF protection on all forms
- Password hashing with Django's built-in password validators
- SQL injection protection via ORM
- Authentication required for write operations
- User authorization checks (users can only edit/delete their own content)
- Email validation on registration

## 🐛 Troubleshooting

### Database Issues
If you encounter database errors:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Missing Media Files
Ensure the `media/` directory exists:
```bash
mkdir media
```

### Static Files Issues
```bash
python manage.py collectstatic --noinput
```

### Port Already in Use
Run on different port:
```bash
python manage.py runserver 8001
```

## 📚 Admin Panel

Access the admin panel at `/admin/`:
- View and manage users
- Edit user profiles
- View all posts, likes, and comments
- Manage followers/following relationships
- Delete inappropriate content

## 🔄 File Upload Limits

- Default max file size: 5MB (configurable in settings)
- Supported image formats: JPG, PNG, GIF, WebP

## 📈 Future Enhancements

- Search functionality
- Hashtags and trending topics
- Direct messaging
- Notifications system
- Post scheduling
- Analytics and insights
- Mobile app
- Real-time updates with WebSockets
- Email notifications
- Two-factor authentication

## 📄 License

This project is open source and available for educational purposes.

## 👨‍💻 Development

### Creating New Models
1. Define model in `models.py`
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Register in `admin.py`

### Adding New Views
1. Create view function in `views.py`
2. Create template in `templates/`
3. Add URL pattern in `urls.py`

### Running Tests
```bash
python manage.py test
```

## 💡 Tips

- Use Django admin for quick data entry
- Check logs for debugging issues
- Use `print()` statements for debugging views
- Django shell is useful for testing: `python manage.py shell`

---

**Enjoy using SocialHub! 🎉**
