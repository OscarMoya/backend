import os
import re
from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.exceptions import ExceptionMiddleware
from starlette.middleware.cors import CORSMiddleware

from supertokens_python import (
    InputAppInfo,
    SupertokensConfig,
    get_all_cors_headers,
    init,
)
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe import (
    dashboard,
    emailverification,
    session,
    usermetadata,
    thirdparty,
    emailpassword,
)

from supertokens_python.recipe.emailpassword.asyncio import sign_in, sign_up
from supertokens_python.recipe.emailpassword.interfaces import SignInOkResult, SignInWrongCredentialsError
from supertokens_python.recipe.session.framework.fastapi import verify_session

import constants

app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(get_middleware())


init(
    app_info=InputAppInfo(
        app_name="FastAPI App",
        api_domain="http://localhost:8000",
        website_domain="http://localhost:3000",
        api_base_path="/auth",
        website_base_path="/auth"
    ),
    supertokens_config=SupertokensConfig(
        connection_uri="http://supertokens:3567"
    ),
    framework="fastapi",
    recipe_list=[
        session.init(),
        emailpassword.init()
    ]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class UserCredentials(BaseModel):
    tenant_id: str
    email: str
    password: str

@app.post("/backend/register")
async def register_user(credentials: UserCredentials):
    try:
        user = await sign_up(credentials.tenant_id, credentials.email, credentials.password)
        return {"user": user}
    except Exception as e:
        return {"error": str(e)}

@app.post("/backend/login")
async def login_user(credentials: UserCredentials):
    try:
        response = await sign_in(credentials.tenant_id ,credentials.email, credentials.password)
        if isinstance(response, SignInOkResult):
            return {"user": response.user}
        elif isinstance(response, SignInWrongCredentialsError):
            return {"error": response}
    except Exception as e:
        return {"error": str(e)}


@app.get("/protected-route")
async def protected_route(token: str = Depends(verify_session())):
    return {"message": "This is a protected route"}


@app.get("/users/me")
async def get_user_info(token: str = Depends(verify_session())):
    return {"user": "user_info"}

