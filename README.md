# ResuMatch

AI-powered job application tracker and resume matcher. Paste any job posting and instantly see how well your resume matches, which skills you're missing, and what keywords to add.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start with Docker](#quick-start-with-docker)
- [Manual Setup](#manual-setup)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [File Storage](#file-storage)

---

## ✨ Features

- ✅ **User Authentication** — Secure registration and login with JWT
- ✅ **Resume Upload** — PDF parsing and extraction to text
- ✅ **Job Tracking** — Save, apply, and manage job applications
- ✅ **AI-Powered Matching** — Match your resume against job postings
- ✅ **Match Scoring** — See 0-100% match score with detailed breakdown
- ✅ **Skill Analysis** — View matched skills, missing skills, and keyword gaps
- ✅ **Input Validation** — Email format and password strength validation
- ✅ **Rate Limiting** — Prevent AI extraction spam
- ✅ **Status Tracking** — Saved → Applied → Interview → Offer → Rejected
- ✅ **Responsive Design** — Works on desktop, tablet, and mobile

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with async support (asyncpg)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose + passlib/argon2)
- **AI**: Groq API (openai/gpt-oss-120b by default)
- **PDF Parsing**: pdfplumber
- **Web Scraping**: httpx + BeautifulSoup4
- **Validation**: Pydantic

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Routing**: React Router v6
- **HTTP Client**: Axios with JWT interceptor
- **State Management**: TanStack Query v5
- **Styling**: Tailwind CSS
- **Animations**: Custom CSS keyframes

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Version Control**: Git

---

## 🚀 Quick Start with Docker (Recommended)

### Prerequisites

Ensure you have installed:
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (includes Docker and Docker Compose)

Verify installation:
```bash
docker --version
docker compose --version
```

### Step-by-Step Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/kunj-web/resumatch.git
cd resumatch
```

#### 2. Create Backend Environment File

Create `backend/.env` in the backend directory:

```bash
# backend/.env
DATABASE_URL=postgresql://postgres:postgres@db:5432/resumatch
SECRET_KEY=your-secret-key-here-change-this-in-production
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=openai/gpt-oss-120b
UPLOAD_DIR=uploads
```

**How to get GROQ_API_KEY:**
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in with your account
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy the generated key
6. Paste it in the `GROQ_API_KEY` field above

**How to generate SECRET_KEY (optional but recommended for production):**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3. Create Frontend Environment File

Create `frontend/.env` in the frontend directory:

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000
```

#### 4. Create Uploads Directory

The backend needs an uploads directory for storing user resume PDFs:

```bash
mkdir -p backend/uploads/resumes
```

#### 5. Start the Application

From the project root directory, run:

```bash
docker compose up --build
```

**What this command does:**
- Builds the backend Docker image
- Builds the frontend Docker image
- Starts PostgreSQL database container
- Runs database migrations automatically
- Starts FastAPI backend server
- Starts React frontend development server

**Wait for all services to start** — you should see messages indicating:
```
backend  | Application startup complete
frontend | ✓ 200ms[v2] (x2)
```

#### 6. Access the Application

Once all services are running, open your browser:

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

#### 7. Test the Application

1. **Register** — Create a new account at `http://localhost:5173/register`
   - Email: `test@example.com`
   - Password: `Test@123` (must have uppercase, lowercase, number)
   - Full Name: `Test User`

2. **Login** — Sign in with your credentials

3. **Upload Resume** — Go to "Add Job" page and upload your resume PDF

4. **Add a Job** — Paste a job posting URL or description

5. **View Match** — Click on the job to see your match score and skill breakdown

### Stop the Application

To stop all running containers:

```bash
docker compose down
```

To stop and remove all data (including database):

```bash
docker compose down --volumes
```

---

## 🔧 Manual Setup (Development)

If you prefer to run services locally without Docker:

### Backend Setup

#### 1. Install Python and PostgreSQL

Ensure you have:
- Python 3.9 or higher
- PostgreSQL 14 or higher running on `localhost:5432`

#### 2. Navigate to Backend Directory

```bash
cd backend
```

#### 3. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 5. Create Environment File

Create `backend/.env`:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/resumatch
SECRET_KEY=your-super-secret-key-change-this
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=openai/gpt-oss-120b
UPLOAD_DIR=uploads
```

#### 6. Create Uploads Directory

```bash
mkdir -p uploads/resumes
```

#### 7. Run Database Migrations

```bash
alembic upgrade head
```

#### 8. Start Backend Server

```bash
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`

### Frontend Setup

#### 1. Navigate to Frontend Directory

```bash
cd frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Create Environment File

Create `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
```

#### 4. Start Development Server

```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

---

## 📁 Project Structure

```
resumatch/
│
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py       # Settings from .env
│   │   │   ├── database.py     # SQLAlchemy engine and session
│   │   │   ├── security.py     # JWT and password hashing
│   │   │   └── deps.py         # Dependency injection
│   │   ├── models/
│   │   │   ├── base.py         # SQLAlchemy declarative base
│   │   │   ├── user.py         # User model
│   │   │   ├── resume.py       # Resume model
│   │   │   ├── job.py          # Job model
│   │   │   ├── enums.py        # Enums (JobStatus, LocationType, etc)
│   │   │   └── __init__.py     # Export all models
│   │   ├── schemas/
│   │   │   ├── user.py         # User request/response schemas
│   │   │   ├── resume.py       # Resume schemas
│   │   │   ├── job.py          # Job schemas
│   │   │   ├── token.py        # Auth token schema
│   │   │   └── __init__.py
│   │   ├── routers/
│   │   │   ├── auth.py         # /auth endpoints (register, login)
│   │   │   ├── resume.py       # /resume endpoints (upload, get, delete)
│   │   │   ├── jobs.py         # /jobs endpoints (CRUD + status updates)
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── parser.py       # PDF text extraction
│   │   │   ├── groq.py         # Groq AI job extraction
│   │   │   ├── matcher.py      # Resume matching logic
│   │   │   └── improver.py     # Resume improvement (future)
│   │   └── main.py             # FastAPI app initialization
│   │
│   ├── alembic/                # Database migrations
│   │   ├── versions/           # Migration files
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── alembic.ini
│   │
│   ├── uploads/                # User uploaded files
│   │   └── resumes/            # PDF resumes (created automatically)
│   │
│   ├── .env                    # Environment variables (create this)
│   ├── .gitignore              # Git ignore rules
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Backend container config
│   └── pyproject.toml          # Project metadata
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx       # Login page
│   │   │   ├── Register.jsx    # Registration page
│   │   │   ├── Dashboard.jsx   # Job list and stats
│   │   │   ├── AddJob.jsx      # Add job page
│   │   │   ├── JobDetail.jsx   # Job details and skills
│   │   │   └── 404.jsx         # Not found page
│   │   ├── components/
│   │   │   └── Layout.jsx      # Sidebar and navbar
│   │   ├── api/
│   │   │   ├── axios.js        # Axios instance with JWT interceptor
│   │   │   ├── auth.js         # Auth API calls
│   │   │   ├── resume.js       # Resume API calls
│   │   │   └── jobs.js         # Jobs API calls
│   │   ├── utils/
│   │   │   └── validation.js   # Email and password validation
│   │   ├── App.jsx             # Main app component
│   │   ├── main.jsx            # React entry point
│   │   └── index.css           # Global styles
│   │
│   ├── .env                    # Environment variables (create this)
│   ├── .gitignore              # Git ignore rules
│   ├── package.json            # NPM dependencies
│   ├── vite.config.js          # Vite configuration
│   ├── tailwind.config.js      # Tailwind CSS config
│   ├── Dockerfile              # Frontend container config
│   └── index.html              # HTML entry point
│
├── docker-compose.yml          # Docker services orchestration
├── .gitignore                  # Root-level git ignore
├── README.md                   # This file
└── CONTRIBUTING.md             # Contribution guidelines
```

---

## 🔐 Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@db:5432/resumatch` |
| `SECRET_KEY` | JWT signing key (change in production) | `your-super-secret-key` |
| `GROQ_API_KEY` | Groq API key for AI extraction | `gsk_xxxxxxxx...` |
| `GROQ_MODEL` | Groq model used for extraction, matching, and tailoring | `openai/gpt-oss-120b` |
| `UPLOAD_DIR` | Directory for uploaded files | `uploads` |

### Frontend (`frontend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

---

## 📊 Database Models

### Users
```
- id (UUID, primary key)
- email (String, unique)
- hashed_password (String)
- full_name (String)
- created_at (DateTime)
- updated_at (DateTime)
```

### Resumes
```
- id (UUID, primary key)
- user_id (FK → users)
- file_name (String)
- file_path (String)
- raw_text (Text) — extracted PDF text
- is_active (Boolean)
- processing_status (Enum: UPLOADED, PARSED, MATCHED, FAILED)
- uploaded_at (DateTime)
- updated_at (DateTime)
```

### Jobs
```
- id (UUID, primary key)
- user_id (FK → users)
- source_url (String, nullable)
- raw_description (Text)
- title, company, location (String)
- location_type (Enum: REMOTE, ONSITE, HYBRID)
- job_type (Enum: FULL_TIME, PART_TIME, CONTRACT, INTERNSHIP)
- salary_min/max, experience_min/max (Integer)
- required_skills, preferred_skills (JSONB array)
- extraction_status (Enum: PENDING, SUCCESS, FAILED)
- match_score (Integer: 0-100)
- matched_skills, missing_skills, keyword_gaps (JSONB)
- status (Enum: SAVED, APPLIED, INTERVIEW, OFFER, REJECTED)
- notes (Text)
- created_at, updated_at (DateTime)
- applied_at (DateTime, nullable)
- deleted_at (DateTime, nullable) — soft delete
```

---

## 📁 File Storage

### Uploads Directory Structure

```
backend/
└── uploads/
    └── resumes/
        ├── a1b2c3d4-e5f6-7890-abcd-ef1234567890.pdf
        ├── b2c3d4e5-f6a7-8901-bcde-f1234567890a.pdf
        └── ...
```

### Important Notes

- **Location**: `backend/uploads/resumes/`
- **Naming**: Files are named with UUIDs (not original filenames)
- **Creation**: Directory is created automatically when users upload resumes
- **Git**: The `uploads/` directory is in `.gitignore` — never commit user files
- **Backup**: In production, backup this directory or use cloud storage (AWS S3, Google Cloud Storage, Azure Blob Storage)

### For Production

Do NOT use local file storage in production. Use:

- **AWS S3** — Most popular
- **Google Cloud Storage** — Easy integration
- **Azure Blob Storage** — Microsoft ecosystem
- **Supabase Storage** — Easiest for startups (PostgreSQL-based)

---

## 🐛 Troubleshooting

### Port Already in Use

If you get an error like `Address already in use` for port 5173 or 8000:

**Option 1 — Kill the process**
```bash
# On macOS/Linux
lsof -i :5173
kill -9 <PID>

# On Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**Option 2 — Change the port in `docker-compose.yml`**
```yaml
services:
  frontend:
    ports:
      - "3000:5173"  # Changed from 5173 to 3000
  
  backend:
    ports:
      - "8001:8000"  # Changed from 8000 to 8001
```

Then access frontend at `http://localhost:3000` and update `VITE_API_URL` accordingly.

### Database Connection Error

Ensure PostgreSQL is running and containers are healthy:

```bash
docker compose ps
```

Should show all containers as `healthy` or `running`.

**Restart the database:**
```bash
docker compose restart db
```

**View database logs:**
```bash
docker compose logs db
```

### Backend Errors

View backend logs:
```bash
docker compose logs backend
```

Common issues:
- Missing `.env` file — Create `backend/.env` with required variables
- Database migrations failed — Run `alembic upgrade head` manually
- Groq API key invalid — Verify your API key at [console.groq.com](https://console.groq.com)

### Frontend Not Loading

View frontend logs:
```bash
docker compose logs frontend
```

Issues:
- `VITE_API_URL` not set — Verify `frontend/.env` exists and has `VITE_API_URL=http://localhost:8000`
- Port 5173 in use — Change port in `docker-compose.yml`

### Upload Directory Permission Denied

If you get permission errors when uploading resumes:

```bash
# Create with proper permissions
mkdir -p backend/uploads/resumes
chmod 755 backend/uploads
chmod 755 backend/uploads/resumes
```

### GROQ API Rate Limited

If you get "Too many requests" errors:
- You've hit the rate limit (10 extractions/hour for free tier)
- Wait 1 hour before making more requests
- Upgrade your Groq plan for higher limits

---

## 📝 API Endpoints

### Authentication
- `POST /auth/register` — Create new account
- `POST /auth/login` — Login and get JWT token
- `GET /auth/me` — Get current user info

### Resume
- `POST /resume/upload` — Upload PDF resume
- `GET /resume/me` — Get user's active resume
- `DELETE /resume/me` — Delete active resume

### Jobs
- `GET /jobs/` — List all user's jobs
- `GET /jobs/{job_id}` — Get job details
- `POST /jobs/` — Create new job (extract from URL or text)
- `PATCH /jobs/{job_id}/status` — Update job status
- `PATCH /jobs/{job_id}/notes` — Update job notes
- `DELETE /jobs/{job_id}` — Delete job (soft delete)

Full documentation available at `http://localhost:8000/docs` (Swagger UI)

---

## 🚢 Deployment

### Production Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` in `backend/.env`
- [ ] Set up cloud storage for uploads (S3, GCS, Azure Blob)
- [ ] Configure production database (not Docker container)
- [ ] Set up environment variables securely (use services like AWS Secrets Manager)
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting per IP
- [ ] Set up backups for database and uploaded files
- [ ] Run security audit

### Recommended Platforms

- **Backend**: Railway, Render, AWS EC2, Google Cloud Run
- **Frontend**: Vercel, Netlify, AWS S3 + CloudFront
- **Database**: AWS RDS, Google Cloud SQL, Supabase

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for more details.

---

## 📞 Support

For issues, questions, or suggestions:

- Open an issue on [GitHub Issues](https://github.com/kunj-web/resumatch/issues)
- Check existing issues for similar problems
- Provide detailed information about your environment and error messages

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — Modern web framework
- [React](https://react.dev/) — UI library
- [Groq](https://groq.com/) — Fast AI inference
- [PostgreSQL](https://www.postgresql.org/) — Reliable database
- [Tailwind CSS](https://tailwindcss.com/) — Utility-first CSS

---

## Copyright (c) 2026 Kunj Bihari
