# Quiz Platform Backend (Supabase)

A Flask-based quiz platform backend that uses Supabase as the database instead of SQLite.

## 🚀 Quick Start

### 1. Set up Supabase Database

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Copy and paste the contents of `supabase_schema.sql` into the editor
4. Run the SQL to create all tables and policies

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Setup Script

```bash
python setup_supabase.py
```

This will:
- Test the Supabase connection
- Check if all tables exist
- Create the default admin user

### 4. Start the Application

```bash
python main.py
```

The application will be available at `http://localhost:5000`

## 🔐 Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

## 📁 Project Structure

```
├── main.py              # Flask application entry point
├── models.py            # Data models (User, Quiz, Question, Result)
├── auth.py              # Authentication and business logic
├── database.py          # Supabase database operations
├── config.py            # Configuration settings
├── utils.py             # Utility functions
├── requirements.txt     # Python dependencies
├── supabase_schema.sql # Database schema for Supabase
├── setup_supabase.py   # Setup script
└── templates/          # HTML templates
```

## 🗄️ Database Schema

### Tables

1. **users** - User accounts (admin, teacher, student)
2. **quizzes** - Quiz information
3. **questions** - Quiz questions with options
4. **results** - Quiz results and answers

### Key Features

- **Row Level Security (RLS)** enabled on all tables
- **Foreign key constraints** for data integrity
- **Indexes** for better query performance
- **JSONB fields** for flexible data storage

## 🔧 Configuration

Edit `config.py` to modify:

- Supabase URL and API key
- Flask secret key
- Database table names

## 📡 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/signup` - User registration

### Student Routes
- `GET /api/student/available-quizzes` - Get available quizzes
- `GET /api/student/results` - Get student results
- `POST /api/student/quiz/<token>/start` - Start a quiz

### Teacher/Admin Routes
- `POST /api/quiz/create` - Create a new quiz
- `GET /api/quizzes` - Get teacher's quizzes
- `GET /api/quiz/<quiz_id>/results` - Get quiz results

### Admin Routes
- `POST /api/admin/create-teacher` - Create teacher account
- `GET /api/admin/users` - List all users
- `DELETE /api/admin/users/<user_id>` - Delete user
- `GET /api/admin/quizzes` - List all quizzes

## 🔄 Migration from SQLite

This project has been migrated from SQLite to Supabase. Key changes:

1. **Database Layer**: Replaced Peewee ORM with Supabase client
2. **Models**: Converted to simple Python classes
3. **Authentication**: Updated to work with Supabase
4. **Data Storage**: JSONB fields for flexible data storage

## 🛠️ Development

### Adding New Features

1. Update the database schema in `supabase_schema.sql`
2. Add new methods to `database.py`
3. Update models in `models.py`
4. Add business logic in `auth.py`
5. Create API endpoints in `main.py`

### Testing

```bash
# Test database connection
python setup_supabase.py

# Run the application
python main.py
```

## 🔒 Security Features

- **Password Hashing**: Using Werkzeug's security functions
- **Session Management**: Flask sessions with secure cookies
- **Role-based Access**: Admin, teacher, and student roles
- **Row Level Security**: Database-level access control

## 📊 Data Migration

If you have existing data in SQLite, you can migrate it by:

1. Export data from SQLite database
2. Transform data to match Supabase schema
3. Import data using Supabase client or SQL

## 🚨 Troubleshooting

### Common Issues

1. **Connection Error**: Check Supabase URL and API key in `config.py`
2. **Table Not Found**: Run the SQL schema in Supabase SQL Editor
3. **Permission Denied**: Check Row Level Security policies
4. **Import Error**: Install dependencies with `pip install -r requirements.txt`

### Debug Mode

Enable debug mode in `main.py`:

```python
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check Supabase logs in the dashboard
4. Create an issue in the repository
