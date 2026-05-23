# Job Tracker API

Job Tracker API is a professional backend Job Application Tracking System developed using FastAPI, SQLite, SQLAlchemy ORM, and JWT Authentication. The project was designed to help users manage their complete job application process through secure REST APIs.

The system allows users to:
- Register and login securely
- Manage companies they are applying to
- Track job applications
- Schedule and manage interviews
- Store job preferences
- Get real-time job recommendations using external APIs
- Save recommended jobs directly into the tracker
- View dashboard analytics and application statistics
- Maintain audit logs for important actions

This project demonstrates backend development concepts such as authentication, database relationships, CRUD operations, modular architecture, validation,  external API integration, and API documentation.

---

# Project Development Process

The project was initially developed in a single `main.py` file to quickly build the core functionality and test API endpoints. After implementing the main features, the application was refactored into a modular FastAPI architecture for better scalability, maintainability, and clean code organization.

The backend was developed using:
- FastAPI for building REST APIs
- SQLAlchemy ORM for database operations
- SQLite as the relational database
- Pydantic for request validation
- JWT Authentication for secure login
- Swagger UI for API testing and documentation
- External Job API Integration using Arbeitnow API

The application was tested using FastAPI Swagger documentation available at:

```text
http://127.0.0.1:8000/docs