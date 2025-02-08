import uvicorn
from fastapi import FastAPI
from user.interface.controllers.user_controller import router as user_routers
from project.interface.controllers.project_controller import router as project_routers
from flow.interface.controllers.flow_controller import router as flow_routers
from dataset.interface.controllers.dataset_controller import router as dataset_routers
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from containers import Container
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.container = Container()
app.include_router(user_routers)
app.include_router(project_routers)
app.include_router(flow_routers)
app.include_router(dataset_routers)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    requese: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content=exc.errors(),
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", reload=True)