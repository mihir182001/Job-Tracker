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

## Recent Enhancements

Based on production-readiness improvements, the following features have been added:

### Structured Logging

* Implemented centralized application logging using Python logging.
* Logs user authentication, company creation, job creation, interview scheduling, and job preference activities.
* Improves monitoring and debugging capabilities.

### Custom Exception Handling

* Added global exception handlers for HTTP and application-level errors.
* Returns clean and consistent JSON error responses.
* Improves API reliability and maintainability.

### Docker Support

* Added Dockerfile for containerized deployment.
* Added docker-compose.yml for simplified application setup.
* Enables easier deployment across environments.

### Automated API Testing

Implemented automated API testing using Pytest and FastAPI TestClient.

Current test coverage includes:

* Home Endpoint
* User Registration
* User Login
* Create Company
* Get Companies
* Create Job
* Get Jobs



### Current Test Status:

```text
7 passed
```

### Cloud Deployment

The application has been deployed on the Render cloud platform using Docker containerization.

### Live API Documentation
```text
https://job-tracker-hrfz.onrender.com/docs
```

The deployed API provides publicly accessible Swagger documentation for testing and exploring all endpoints.

### CI/CD Pipeline
A continuous integration pipeline has been implemented using GitHub Actions.

### Workflow Features
* Automatically triggers on every push to the main branch
* Automatically triggers on pull requests
* Installs project dependencies in a clean environment
* Executes automated test suites using Pytest
* Verifies application stability before deployment

## Performance Monitoring

Implemented request-time monitoring middleware to track API performance.

Sample local response times:

| Endpoint | Response Time |
|-----------|-------------|
| POST /login | 2.53 sec |
| POST /companies | 0.53 sec |
| GET /companies | 0.08 sec |


The application was tested using FastAPI Swagger documentation available at:

```text
http://127.0.0.1:8000/docs