# GenCD Backend

## Overview

The **GenCD Backend** is a monolithic Django-based service powering all core functionalities of the GenCD platform. It provides end-to-end support for:

- Authentication
- User management (RBAC)
- Project and repository handling
- Automated documentation generation
- System-wide logging

This backend integrates multiple Django apps, each handling a specific domain:

| App Name        | Purpose                                           |
|-----------------|--------------------------------------------------|
| `auth_app`      | Authentication and session handling             |
| `users_app`     | Role-based access control, permissions, invites |
| `projects_app`  | Project lifecycle management                     |
| `repositories_app` | GitHub repository integration and configuration |
| `docs_app`      | Automatic documentation generation and logging  |
| `extras_app`    | Cross-service request and response logging      |

---

## Key Features

### 1. Authentication & Authorization (`auth_app`)

- Secure JWT-based authentication (login, logout, register)
- Password reset and account verification
- Management command for super admin bootstrap
- Custom user model with extended fields

### 2. User & Role Management (`users_app`)

- Role-Based Access Control (RBAC)
- CRUD for roles and permissions
- Invite and manage users via email
- JSON-based permission schema with categories and HTTP method mapping
- First-time Super Admin creation using `create_super_admin` command

### 3. Project Management (`projects_app`)

- Create, update, delete, and retrieve projects
- Maintain a count of repositories linked to each project
- Serializer and API views for project CRUD

### 4. Repository Management (`repositories_app`)

- Link public or private GitHub repositories
- Store configurations such as branch names, access URLs, and metadata
- SSH key integration for private repositories
- CRUD operations for repositories with filtering by project or privacy level
- Repository detail page provides triggers for documentation generation

### 5. Documentation Generator (`docs_app`)

- Core logic for automatic documentation generation ("Gen Docs Now" process)
- Links each repository with generated documentation records
- Stores logs for generation steps (e.g., cloning, parsing, generating)
- Utility functions for file-level and function-level doc creation
- Estimated generation time and progress tracking

### 6. Cross Request-Response Logging (`extras_app`)

- Centralized logging system for API requests and responses
- Tracks user actions, endpoints, and status codes
- Useful for debugging, auditing, and analytics

### 7. SSH Key Management

- Public and private SSH keys are generated **once per environment**
- Keys stored securely inside `keys/` directory:

```

keys/private_key.pem
keys/public_key.pem

````
- Public key can be shared with users to connect private GitHub repositories
- No keys are stored in the database for security reasons

### 8. Analytics Dashboard

- Aggregated data for total projects, repositories, and generated documentation
- Export options: PDF, HTML
- System statistics powered by internal APIs

---

## Project Structure

```text
gencd_api/
├── auth_app/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── management/commands/create_super_admin.py
├── users_app/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── permissions.py
├── projects_app/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── repos_app/
│   ├── models.py
│   ├── views.py
│   ├── utils/ssh_handler.py
│   ├── serializers.py
│   └── urls.py
├── docs_app/
│   ├── models.py
│   ├── views.py
│   ├── utils/doc_generator.py
│   └── urls.py
├── extras_app/
│   ├── models.py
│   ├── middleware.py
│   └── utils/logger.py
├── keys/
│   ├── private_key.pem
│   └── public_key.pem
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
├── manage.py
├── Dockerfile
├── .gitignore
└── .env
````

---

## Setup Guide

### 1. Clone Repository

```bash
git clone git@github.com:gencdgit/gencd-api.git
cd gencd-api
```

### 2. Environment Setup

```bash
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Bootstrap Super Admin

```bash
python manage.py create_super_admin
```

### 6. Run Development Server

```bash
python manage.py runserver
```

---

## API Overview

| App              | Purpose                  |
| ---------------- | ------------------------ |
| auth_app         | Authentication           |
| users_app        | RBAC & Invitations       |
| projects_app     | Manage Projects          |
| repositories_app | Manage Repositories      |
| docs_app         | Documentation Generation |
| extras_app       | Logs & Audits            |

---

## Security & Privacy

* SSH keys never stored in the database
* JWT-based authentication and role-level permission checks
* All sensitive configurations managed via `.env`
* Supports deployment via Docker for isolation

---

## Future Enhancements

* Support for multiple programming languages (Java, JS, C++)
* Integration with GitHub/GitLab CI pipelines
* Real-time progress tracking via WebSockets
* Knowledge Graph support for cross-repo insights

---

## Conclusion

The **GenCD Backend** offers a robust, extensible, and secure architecture that automates documentation generation and centralizes all user, repository, and log management tasks within a unified Django service.
