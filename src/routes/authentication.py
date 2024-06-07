import os
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
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.async_to_sync_wrapper import sync
from supertokens_python.recipe.emailpassword.interfaces import APIInterface, APIOptions, SignUpOkResult, SignInOkResult
from supertokens_python.recipe.emailpassword.asyncio import sign_in

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


@app.post("/auth/signup")
async def signup():
    pass  # Esta ruta se manejará automáticamente por Supertokens


@app.post("/auth/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    response = await sign_in("", form_data.username, form_data.password)
    if isinstance(response, SignInOkResult):
        s = await session.create_new_session(None, response.user.user_id, {}, {})
        return {
            "access_token": s.get_access_token(),
            "token_type": "bearer"
        }
    raise HTTPException(status_code=400, detail="Incorrect email or password")


@app.get("/protected-route")
async def protected_route(token: str = Depends(oauth2_scheme)):
    # Aquí puedes verificar el token si lo necesitas
    return {"message": "This is a protected route"}


@app.get("/users/me")
async def get_user_info(token: str = Depends(oauth2_scheme)):
    # Aquí puedes decodificar el token y obtener información del usuario
    return {"user": "user_info"}
