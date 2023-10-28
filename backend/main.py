import sys
sys.path.append('.')
from functools import lru_cache
from typing import Annotated, Union

import uvicorn
from fastapi import Body, FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.v1.router import router as v1_router
from core.config import Settings


# init app
app = FastAPI()

# apply cors
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# router
app.include_router(v1_router)


if __name__ == '__main__':
    uvicorn.run(app='main:app', host="0.0.0.0", port=5000, reload=True)