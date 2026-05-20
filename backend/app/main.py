from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, resume, jobs


app = FastAPI(
    title="ResuMatch API",
    description="AI-powered job application tracker and resume matcher",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        # Add your Netlify URL here after deploy e.g.:
        # "https://resumatch.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(jobs.router)


@app.get("/health")
async def health():
    return {"status": "ok", "message": "ResuMatch API is running"}