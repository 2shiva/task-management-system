# Task Management System - Architecture

```mermaid
flowchart TD
    Client[Client / Postman] --> API[FastAPI Application]

    API --> Auth[Authentication & RBAC]
    API --> Users[Users API]
    API --> Tasks[Tasks API]
    API --> Comments[Comments API]
    API --> Attachments[Attachments API]
    API --> Notifications[Notifications API]
    API --> Dashboard[Dashboard API]
    API --> Audit[Audit Logs API]

    Auth --> Services[Service Layer]
    Users --> Services
    Tasks --> Services
    Comments --> Services
    Attachments --> Services
    Notifications --> Services
    Dashboard --> Services
    Audit --> Services

    Services --> Repositories[Repository Layer]
    Repositories --> DB[(PostgreSQL Database)]

    Attachments --> Storage[File Storage]
    Notifications --> Background[Background Tasks]