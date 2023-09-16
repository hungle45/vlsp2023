from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from api.v1.endpoints.users import users_router
from api.v1.endpoints.tts import tts_router


router = APIRouter()
templates = Jinja2Templates(directory="core/views")

@router.get('/', include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse('/tts/home.html', {'request': request})

router.include_router(users_router)
router.include_router(tts_router)