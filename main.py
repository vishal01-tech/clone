from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from crud import CRUD
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import random




# jwt config
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# generate 6 digit number
def generate_otp():
    return str(random.randint(100000, 999999))


# initializing the fastapi
app = FastAPI()

# jinja templates
templates = Jinja2Templates(directory="templates")

# static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# database
crud = CRUD()

# jwt helpers
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=5))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# verify token
def verify_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# current user
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
    email: str = Form(...),
    phone: str = Form(...)
):
    existing = crud.get_admin_by_username(username)
    if existing:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})
    
    hashed = hash_password(password)
    crud.register_admin(fullname, username, hashed, email, phone)
    return RedirectResponse(url="/", status_code=303)




# ------------------- Login -------------------
@app.post("/", response_class=HTMLResponse)
async def login_admin(request: Request, username: str = Form(...), password: str = Form(...)):
    admin = crud.get_admin_by_username(username)
    if not admin or not verify_password(password, admin.password):
        return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid username or password"})

    token_data = {"sub": admin.username, "fullname": admin.fullname}
    access_token = create_access_token(token_data)

    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        path="/",          
        secure=False      
    )
    return response


# ------------------- Logout -------------------
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token") 
    return response

# ------------------- Forgot Password -------------------

# get
@app.get("/forgot", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_pass.html", {"request": request})


# post
@app.post("/show", response_class=HTMLResponse)
async def forgot_password(request: Request, identifier: str = Form(...)):
    identifier = identifier.strip()
    role, account = crud.get_account_by_email_or_phone(identifier)

    if not account:
        return templates.TemplateResponse("forgot_pass.html", {
            "request": request,
            "error": "No account found with this email or phone"
        })

    reset_token = create_access_token({"sub": account.username}, expires_delta=timedelta(minutes=1))
    return templates.TemplateResponse("show_username.html", {
        "request": request,
        "username": account.username,
        "identifier": identifier,
        "role": role,
        "admin": True,
        "token": reset_token
    })


# Reset Password
@app.get("/new", response_class=HTMLResponse)
def show_reset_get(request: Request, token: str):
    decoded = verify_access_token(token)
    if not decoded:
        return templates.TemplateResponse(
            "new_pass.html",
            {"request": request, "error": "Invalid or expired token", "token": token}
        )
    
    username = decoded["sub"]
    admin = crud.get_admin_by_username(username)
    return templates.TemplateResponse(
        "new_pass.html",
        {"request": request, "token": token, "error": None, "admin": admin, "username": username}
    )


# -----------Password update-------------
@app.get("/update_password",response_class=HTMLResponse)
async def update_get(request : Request):
    return templates.TemplateResponse("new_pass.html",{"request": request})


@app.post("/update_password", response_class=HTMLResponse)
async def update_password(
    request: Request,
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    if new_password != confirm_password:
        return templates.TemplateResponse("new_pass.html",{"request": request, "error": "Passwords do not match", "token": token})

    decoded = verify_access_token(token)
    if not decoded:
        return templates.TemplateResponse("new_pass.html",{"request": request, "error": "Invalid or expired token", "token": token})

    username = decoded["sub"]

    admin = crud.get_admin_by_username(username)

    if not admin:
        return templates.TemplateResponse("new_pass.html",{"request": request, "error": "No user found", "token": token})
    
    hashed = hash_password(new_password)
    crud.update_user_password(admin.id, hashed)

    return RedirectResponse(url="/", status_code=303)


# ------------------- Show Username -------------------

@app.get("/show", response_class=HTMLResponse)
async def show_username(request: Request):
    return templates.TemplateResponse("show_username.html", {"request": request})



@app.post("/show", response_class=HTMLResponse)
async def show_username_post(request: Request):
    current_user = get_current_user(request)
    if current_user:
        return templates.TemplateResponse("show_username.html", {
            "request": request,
            "admin": True,
            "username": current_user["sub"],
            "identifier": "from_cookie"
        })
    return RedirectResponse(url="/", status_code=303)





# ------------------- Home & User CRUD -------------------

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    users = crud.get_users()
    return templates.TemplateResponse("home.html", {"request": request, "users": users, "user": current_user})



@app.get("/update_user/{user_id}", response_class=HTMLResponse)
async def update_user_form(request: Request, user_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    user = crud.get_user_by_id(user_id)
    if not user:
        return RedirectResponse(url="/home", status_code=303)

    return templates.TemplateResponse("update_user.html", {"request": request, "user": user})




@app.post("/update_user/{user_id}", response_class=HTMLResponse)
async def update_user(
    request: Request,
    user_id: int,
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    address: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    crud.update_user(user_id, name, age, gender, address)
    return RedirectResponse(url="/home", status_code=303)




@app.post("/delete_user/{user_id}", response_class=HTMLResponse)
async def delete_user_post(request: Request, user_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    crud.delete_user(user_id)
    return RedirectResponse(url="/home", status_code=303)



@app.get("/add_user", response_class=HTMLResponse)
async def add_user_form(request: Request, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("add_user.html", {"request": request})



@app.post("/add_user", response_class=HTMLResponse)
async def add_user(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    address: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    crud.add_user(name, age, gender, address)
    return RedirectResponse(url="/home", status_code=303)
