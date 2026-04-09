from fastapi import FastAPI
from src.api_routes.incoming_call_routes import incoming_call_router

# Creating the main application instance(object) for Doctomed AI system
doctomed_application=FastAPI()

# Including incoming call routes into main application
doctomed_application.include_router(incoming_call_router)

# Root endpoint to verify that backend is running
@doctomed_application.get("/")
async def check_application_status():
    return {
        "application_status": "Doctomed AI backend is running successfully"
    }
