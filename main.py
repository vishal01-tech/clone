from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mysql.connector
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext

# jwt config
SECRET_KEY = "your_secret_key" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# defining hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# verifying hash password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# database
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="UsersDatabase"
    )

# initializing the fastapi
app = FastAPI()

# jinja templates
templates = Jinja2Templates(directory="templates")

# static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# jwt helpers
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# verify jwt token
def verify_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# Dependency to get current user from JWT cookie
def get_current_user(request: Request) -> Optional[dict]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    return verify_access_token(token)


# Login page
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Register page
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Register (admin)
@app.post("/register")
async def register_admin(
    request: Request,
    fullname: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    reconfirm_password: str = Form(...)
):
    # password match check
    if password != reconfirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords do not match"})

    db = get_db()
    try:
        # check if username exists
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id FROM admin WHERE username = %s", (username,))
        existing = cursor.fetchone()
        cursor.close()
        if existing:
            return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})

        hashed_pwd = hash_password(password)
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO admin (fullname, username, password) VALUES (%s, %s, %s)",
            (fullname, username, hashed_pwd)
        )
        db.commit()
        cursor.close()
    finally:
        db.close()

    return RedirectResponse(url="/", status_code=303)


# Login page post
@app.post("/", response_class=HTMLResponse)
async def login_admin(request: Request, username: str = Form(...), password: str = Form(...)):
    db = get_db()
    admin = None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        admin = cursor.fetchone()
        cursor.close()
    finally:
        db.close()

    if not admin or not verify_password(password, admin["password"]):
        return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid username or password"})

    token_data = {"sub": admin["username"], "fullname": admin.get("fullname")}
    access_token = create_access_token(token_data)

    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
    #     httponly=True,       
    #     secure=False,        # set True with HTTPS in production
    #     samesite="lax",
    #     max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response



# Logout 
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


# Home page user list
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    db = get_db()
    users = []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users ORDER BY id DESC")
        users = cursor.fetchall()
        cursor.close()
    finally:
        db.close()

    return templates.TemplateResponse("home.html", {"request": request, "users": users, "user": current_user})


# Add user get
@app.get("/add_user", response_class=HTMLResponse)
async def add_user_form(request: Request, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("add_user.html", {"request": request})



# Add user (POST)
@app.post("/add_user", response_class=HTMLResponse)
async def add_user(
    request: Request,
    name: str = Form(...),
    age: str = Form(...),
    gender: str = Form(...),
    address: str = Form(...),
    phone: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (name, age, gender, address, phone) VALUES (%s, %s, %s, %s, %s)",
            (name, age, gender, address, phone)
        )
        db.commit()
        cursor.close()
    finally:
        db.close()

    return RedirectResponse(url="/home", status_code=303)




# Update user (GET)
@app.get("/update_user/{user_id}", response_class=HTMLResponse)
async def update_user_form(request: Request, user_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    db = get_db()
    user = None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
    finally:
        db.close()

    if not user:
        return RedirectResponse(url="/home", status_code=303)

    return templates.TemplateResponse("update_user.html", {"request": request, "user": user})


# Update user (POST)
@app.post("/update_user/{user_id}", response_class=HTMLResponse)
async def update_user(
    request: Request,
    user_id: int,
    name: str = Form(...),
    age: str = Form(...),
    gender: str = Form(...),
    address: str = Form(...),
    phone: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE users
            SET name = %s, age = %s, gender = %s, address = %s, phone = %s
            WHERE id = %s
            """,
            (name, age, gender, address, phone, user_id)
        )
        db.commit()
        cursor.close()
    finally:
        db.close()

    return RedirectResponse(url="/home", status_code=303)



# Delete user get
@app.get("/delete_user/{user_id}", response_class=HTMLResponse)
async def delete_user_get(request: Request, user_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        cursor.close()
    finally:
        db.close()

    return RedirectResponse(url="/home", status_code=303)



# Delete user post
@app.post("/delete_user/{user_id}", response_class=HTMLResponse)
async def delete_user_post(request: Request, user_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        cursor.close()
    finally:
        db.close()

    return RedirectResponse(url="/home", status_code=303)
