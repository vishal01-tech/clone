# from fastapi import FastAPI, Request, Form, Depends
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from jose import JWTError, jwt
# from crud import CRUD
# from datetime import datetime, timedelta
# from typing import Optional
# from passlib.context import CryptContext


# # jwt config
# SECRET_KEY = "your_secret_key" 
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # Password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # defining hash password
# def hash_password(password: str):
#     return pwd_context.hash(password)

# # verifying hash password
# def verify_password(plain_password: str, hashed_password: str):
#     return pwd_context.verify(plain_password, hashed_password)

# # initializing the fastapi
# app = FastAPI()

# # jinja templates
# templates = Jinja2Templates(directory="templates")

# # static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # database
# crud = CRUD()

# # jwt helpers
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# # verify jwt token
# def verify_access_token(token: str) -> Optional[dict]:
#     try:
#         return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     except JWTError:
#         return None


# # Dependency to get current user from JWT cookie
# def get_current_user(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         return None
#     return verify_access_token(token)


# # Login page
# @app.get("/", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


# # Register page
# @app.get("/register", response_class=HTMLResponse)
# async def register_page(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})


# @app.get("/forgot",response_class=HTMLResponse)
# async def forgot_password(request : Request):
#     return templates.TemplateResponse("forgot_pass.html",{"request": request})

# # Register (admin)
# @app.post("/register")
# async def register_admin(
#     request: Request,
#     fullname: str = Form(...),
#     username: str = Form(...),
#     password: str = Form(...),
#     reconfirm_password: str = Form(...)
# ):
#     # password match check
#     if password != reconfirm_password:
#         return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords do not match"})
    
#     existing = crud.get_admin_by_username(username)

#     # if user already exist
#     if existing:
#         return templates.TemplateResponse("register.html",{"request":request,"error":"Username already exists"})
    
#     hashed = hash_password(password)
#     crud.register_admin(fullname,username,hashed)



#     return RedirectResponse(url="/", status_code=303)


# # Login page post
# @app.post("/", response_class=HTMLResponse)
# async def login_admin(request: Request, username: str = Form(...), password: str = Form(...)):
#     admin = crud.get_admin_by_username(username)

#     if not admin or not verify_password(password, admin.password):
#         return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid username or password"})

#     token_data = {"sub": admin.username, "fullname": admin.fullname}
#     access_token = create_access_token(token_data)

#     response = RedirectResponse(url="/home", status_code=303)
#     response.set_cookie(
#         key="access_token",
#         value=access_token,
#     #     httponly=True,       
#     #     secure=False,        # set True with HTTPS in production
#     #     samesite="lax",
#     #     max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
#     )
#     return response


# # Logout 
# @app.get("/logout")
# async def logout():
#     response = RedirectResponse(url="/", status_code=303)
#     response.delete_cookie("access_token")
#     return response


# # Home page user list
# @app.get("/home", response_class=HTMLResponse)
# async def home(request: Request, current_user: dict = Depends(get_current_user)):
#     if not current_user:
#         return RedirectResponse(url="/", status_code=303)

#     users = crud.get_users()
#     return templates.TemplateResponse("home.html", {"request": request, "users": users, "user": current_user})





# # Add user get
# @app.get("/add_user", response_class=HTMLResponse)
# async def add_user_form(request: Request, current_user: dict = Depends(get_current_user)):
#     if not current_user:
#         return RedirectResponse(url="/", status_code=303)
#     return templates.TemplateResponse("add_user.html", {"request": request})



# # Add user (POST)
# @app.post("/add_user", response_class=HTMLResponse)
# async def add_user(
#     request: Request,
#     name: str = Form(...),
#     age: str = Form(...),
#     gender: str = Form(...),
#     address: str = Form(...),
#     phone: str = Form(...),
#     current_user: dict = Depends(get_current_user)
# ):
#     if not current_user:
#         return RedirectResponse(url="/", status_code=303)

#     crud.add_user(name,age,gender,address,phone)
#     return RedirectResponse(url="/home", status_code=303)



# # Update user (GET)
# @app.get("/update_user/{user_id}", response_class=HTMLResponse)
# async def update_user_form(request: Request, user_id: int, current_user: dict = Depends(get_current_user)):
#     if not current_user:
#         return RedirectResponse(url="/", status_code=303)

    
#     user = crud.get_user_by_id(user_id)
    
#     if not user:
#         return RedirectResponse(url="/home", status_code=303)

#     return templates.TemplateResponse("update_user.html", {"request": request, "user": user})


# # Update user (POST)
# @app.post("/update_user/{user_id}", response_class=HTMLResponse)
# async def update_user(
#     request: Request,
#     user_id: int,
#     name: str = Form(...),
#     age: str = Form(...),
#     gender: str = Form(...),
#     address: str = Form(...),
#     phone: str = Form(...),
#     current_user: dict = Depends(get_current_user)
# ):
#     if not current_user:
#         return RedirectResponse(url="/", status_code=303)

#     crud.update_user(user_id,name,age,gender,address,phone)

#     return RedirectResponse(url="/home", status_code=303)


# # Delete user post
# @app.post("/delete_user/{user_id}", response_class=HTMLResponse)
# async def delete_user_post(request: Request, user_id: int, current_user: dict = Depends(get_current_user)):
#     if not current_user:
#         return RedirectResponse(url="/", status_code=303)

#     crud.delete_user(user_id)
#     return RedirectResponse(url="/home", status_code=303)



# # forgot password
# # Forgot password page (GET)
# @app.get("/forgot", response_class=HTMLResponse)
# async def forgot_password_page(request: Request):
#     return templates.TemplateResponse("forgot_pass.html", {"request": request})


# # Forgot password (POST)
# @app.post("/forgot", response_class=HTMLResponse)
# async def forgot_password(request: Request, identifier: str = Form(...)):
#     user = crud.get_user_by_email_or_phone(identifier)

#     if not user:
#         return templates.TemplateResponse("forgot_pass.html", {
#             "request": request,
#             "error": "No account found with this email or phone"
#         })

#     # go to next page with username + reset form
#     return templates.TemplateResponse("show_username.html", {
#         "request": request,
#         "username": user.username,
#         "identifier": identifier
#     })


# # Update password (POST)
# @app.post("/update_password", response_class=HTMLResponse)
# async def update_password(
#     request: Request,
#     identifier: str = Form(...),
#     new_password: str = Form(...),
#     confirm_password: str = Form(...)
# ):
#     if new_password != confirm_password:
#         return templates.TemplateResponse("new_password.html", {
#             "request": request,
#             "error": "Passwords do not match",
#             "identifier": identifier
#         })

#     user = crud.get_user_by_email_or_phone(identifier)
#     if not user:
#         return RedirectResponse(url="/forgot", status_code=303)

#     hashed = hash_password(new_password)
#     crud.update_admin_password(user.id, hashed)

#     return RedirectResponse(url="/", status_code=303)


# # show username 
# @app.post("/show", response_class=HTMLResponse)
# async def show_username(request: Request):
#     return templates.TemplateResponse("show_username.html", {"request": request})







from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from crud import CRUD
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext

# jwt config
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# initializing the fastapi
app = FastAPI()

# jinja templates
templates = Jinja2Templates(directory="templates")

# static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# database
crud = CRUD()

# jwt helpers
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    return verify_access_token(token)

# ------------------- Auth Routes -------------------

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_admin(
    request: Request,
    fullname: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    reconfirm_password: str = Form(...),
    email : str = Form(...),
    phone : str = Form(...)
):
    if password != reconfirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords do not match"})
    
    existing = crud.get_admin_by_username(username)
    
    if existing:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})
    
    hashed = hash_password(password)
    crud.register_admin(fullname, username, hashed,email,phone)
    return RedirectResponse(url="/", status_code=303)



@app.post("/", response_class=HTMLResponse)
async def login_admin(request: Request, username: str = Form(...), password: str = Form(...)):
    admin = crud.get_admin_by_username(username)
    if not admin or not verify_password(password, admin.password):
        return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid username or password"})

    token_data = {"sub": admin.username, "fullname": admin.fullname}
    access_token = create_access_token(token_data)

    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(key="access_token", value=access_token)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

# ------------------- Forgot Password Flow -------------------

@app.get("/forgot", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_pass.html", {"request": request})

@app.post("/forgot", response_class=HTMLResponse)
async def forgot_password(request: Request, identifier: str = Form(...)):
    role, account = crud.get_account_by_email_or_phone(identifier)

    if not account:
        return templates.TemplateResponse("forgot_pass.html", {
            "request": request,
            "error": "No account found with this email or phone"
        })

    return templates.TemplateResponse("show_username.html", {
        "request": request,
        "username": account.username,
        "identifier": identifier,
        "role": role
    })

@app.post("/update_password", response_class=HTMLResponse)
async def update_password(
    request: Request,
    identifier: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form(...)
):
    if new_password != confirm_password:
        return templates.TemplateResponse("new_pass.html", {
            "request": request,
            "error": "Passwords do not match",
            "identifier": identifier,
            "role": role
        })

    role, account = crud.get_account_by_email_or_phone(identifier)
    if not account:
        return RedirectResponse(url="/forgot", status_code=303)

    hashed = hash_password(new_password)

    if role == "admin":
        crud.update_admin_password(account.id, hashed)
    else:
        crud.update_user_password(account.id, hashed)

    return RedirectResponse(url="/", status_code=303)



@app.get("/new")
def show_reset_page(request: Request, token: str):
    return templates.TemplateResponse(
        "new_pass.html",
        {"request": request, "token": token, "error": None}
    )


@app.post("/update_password", response_class=HTMLResponse)
async def update_password(
    request: Request,
    identifier: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "new_pass.html", 
            {"request": request, "error": "Passwords do not match", "identifier": identifier}
        )

    # check user by email/phone
    user = crud.get_user_by_email_or_phone(identifier)
    if not user:
        return templates.TemplateResponse(
            "new_pass.html", 
            {"request": request, "error": "No user found with this email or phone", "identifier": identifier}
        )

    hashed = hash_password(new_password)
    crud.update_user_password(user.id, hashed)

    return RedirectResponse(url="/", status_code=303)


@app.post("/show",response_class=HTMLResponse)
async def show_username(request : Request):
    return templates.TemplateResponse("show_username.html",{"request":request})