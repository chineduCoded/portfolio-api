from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from .routers import (
    auth, users, skills, basicinfo, publications, 
    awards, certifications, interests, references,
    educations, experiences, projects
)
from .config import settings, LoguruLogConfig
from .middleware import log_middleware

description = """
PortfolioApp API for managing personal portfolio information.
"""

# Loguru logger configuration
LoguruLogConfig().configure()

app = FastAPI(
    title="PortfolioApp",
    description=description,
    version="0.0.1",
    contact={
        "name": "PortfolioApp",
        "url": "https://chinedu-elijah.herokuapp.com",
        "email": "chinedujohn17@gmail.com",
        "phone": "+234 816 436 7316"
    }
)

# Middleware logs
app.add_middleware(
    BaseHTTPMiddleware,
    dispatch=log_middleware
)

origins = [
    settings.client_origin,
]
# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=origins
)

# Include the routers
app.include_router(auth.router, prefix="/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/v1/users", tags=["Users"])
app.include_router(basicinfo.router, prefix="/v1/basicinfo", tags=["Basic Information"])
app.include_router(skills.router, prefix="/v1/skills", tags=["Skills"])
app.include_router(publications.router, prefix="/v1/publications", tags=["Publications"])
app.include_router(awards.router, prefix="/v1/awards", tags=["Awards"])
app.include_router(certifications.router, prefix="/v1/certifications", tags=["Certifications"])
app.include_router(interests.router, prefix="/v1/interests", tags=["Interests"])
app.include_router(references.router, prefix="/v1/references", tags=["References"])
app.include_router(educations.router, prefix="/v1/educations", tags=["Educations"])
app.include_router(experiences.router, prefix="/v1/experiences", tags=["Experiences"])
app.include_router(projects.router, prefix="/v1/projects", tags=["Projects"])


@app.get("/", tags=["Root"], summary="Checks API status")
async def read_root():
    return JSONResponse(content={
        "status": "running!",
        "message": "Welcome to the Portfolio API."
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )