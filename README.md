# Company Registry App

## Technologies
Backend: FastAPI, SQLAlchemy, Pydantic, PostgreSQL
Frontend: Vue.js, Axios

## Database Schema
![Database Schema](/database-diagram.png)

## Prerequisites
- Docker
- Docker Compose

## Installation
1. Clone the repository
2. Run the application:
```bash
docker-compose up -d
```

## Configuration
- Set `INITIALIZE_DB=true` in docker-compose.yml to generate sample data
- Configure database connection in docker-compose.yml:
  ```yaml
  environment:
    - POSTGRES_USER=postgres
    - POSTGRES_PASSWORD=postgres
    - POSTGRES_DB=company_db
  ```
  
## Access
- Web interface: http://localhost:8080
- API: http://localhost:5000
- API docs: http://localhost:5000/docs