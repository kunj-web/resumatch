# ResuMatch

AI-powered job application tracker and resume matcher.

---

## Quick Start with Docker (Recommended)

The easiest way to run the entire application (frontend, backend, and database) is with Docker Compose.

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop)

### Starting the Application

Navigate to the project root directory and run:

```bash
docker compose up --build
```

This command will:
1. Build the backend Docker image
2. Build the frontend Docker image
3. Start the PostgreSQL database
4. Run database migrations automatically
5. Start the backend API server
6. Start the frontend development server

### Access the Application

Once all services are running, open your browser and navigate to:

- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

### Stopping the Application

To stop all services:

```bash
docker compose down
```

To stop and remove all data (including database):

```bash
docker compose down --volumes
```

---

## Manual Setup (Development)

If you prefer to run services locally without Docker:

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the `backend` directory with required variables:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/resumatch
   SECRET_KEY=your-super-secret-key-change-this
   GROQ_API_KEY=your-groq-api-key
   UPLOAD_DIR=uploads/resumes
   ```

5. Start PostgreSQL (ensure it's running on `localhost:5432`)

6. Run database migrations:
   ```bash
   alembic upgrade head
   ```

7. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

---

## Project Structure

```
resumatch/
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── main.py       # FastAPI app initialization
│   │   ├── routers/      # API route handlers
│   │   ├── models/       # SQLAlchemy database models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Business logic
│   │   └── core/         # Configuration, database, security
│   ├── alembic/          # Database migrations
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile        # Backend Docker configuration
│
├── frontend/             # React + Vite frontend application
│   ├── src/
│   │   ├── pages/        # React page components
│   │   ├── components/   # Reusable React components
│   │   ├── api/          # API client functions
│   │   └── App.jsx       # Main app component
│   ├── package.json      # Node.js dependencies
│   └── Dockerfile        # Frontend Docker configuration
│
├── docker-compose.yml    # Docker Compose orchestration
└── README.md             # This file
```

---

## Features

- ✅ User authentication (registration & login)
- ✅ Resume upload and parsing
- ✅ Job application tracking
- ✅ AI-powered resume matching using Groq API
- ✅ PostgreSQL database with async support

---

## Tech Stack

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Async**: asyncpg
- **Authentication**: JWT (JSON Web Tokens)
- **API AI**: Groq API

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Routing**: React Router
- **HTTP Client**: Axios
- **State Management**: React Query
- **Styling**: Tailwind CSS

---

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for our code of conduct and the process for submitting pull requests.

---

## License

This project is licensed under the MIT License.

---

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
