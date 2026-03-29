from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from construction_api.routes.v1 import projects
from construction_api.error_handlers import register_exception_handlers

app = FastAPI(
    title="Construction Projects API",
    description="API for listing construction projects filtered by area",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register RFC 9457 exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(projects.router, prefix="", tags=["projects"])


@app.get("/")
async def root():
    return {"message": "Construction Projects API"}
