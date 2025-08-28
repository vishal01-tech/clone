from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import mysql.connector
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# JWT CONFIG 
SECRET_KEY = "your_secret_key_here_change_this_to_a_random_value"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# DATABASE
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="UsersDatabase"
    )

# APi
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# JWt helper
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Dependency to get current user from cookie
def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    user = verify_access_token(token)
    return user


# Login page
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Register page
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Process registration (admin)
@app.post("/register")
async def register_admin(
    request: Request,
    fullname: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    reconfirm_password: str = Form(...)
):
    if password != reconfirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords do not match"})

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO admin (fullname, username, password, reconfirm_password) VALUES (%s, %s, %s, %s)",
        (fullname, username, password, reconfirm_password)
    )
    db.commit()
    cursor.close()
    db.close()

    return RedirectResponse(url="/", status_code=303)

# Process login and set JWT cookie
@app.post("/", response_class=HTMLResponse)
async def login_admin(request: Request, username: str = Form(...), password: str = Form(...)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
    admin = cursor.fetchone()
    cursor.close()
    db.close()

    if not admin:
        # re-render login with error
        return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid username or password"})

    # create token
    token_data = {"sub": admin["username"], "fullname": admin.get("fullname")}
    access_token = create_access_token(token_data)

    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,     # not readable by JS
        secure=False,      # set to True in production (HTTPS)
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response


# logout
@app.get("/logout")
async def logout(request: Request):
    if "user" in request.session:
        request.session.clear()
    
    return RedirectResponse(url="/login", status_code=303)

# home page
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    db.close()

    return templates.TemplateResponse("home.html", {"request": request, "users": users, "user": current_user})

# Add user (form page)
@app.get("/add_user", response_class=HTMLResponse)
async def add_user_form(request: Request, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("add_user.html", {"request": request})

# Add user (post)
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
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (name, age, gender, address, phone) VALUES (%s, %s, %s, %s, %s)",
        (name, age, gender, address, phone)
    )
    db.commit()
    cursor.close()
    db.close()
    return RedirectResponse(url="/home", status_code=303)

# Update user (form)
@app.get("/update_user/{user_id}", response_class=HTMLResponse)
async def update_user_form(request: Request, user_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    if not user:
        return RedirectResponse(url="/home", status_code=303)

    return templates.TemplateResponse("update_user.html", {"request": request, "user": user})

# Update user (post)
@app.post("/update_user/{user_id}", response_class=HTMLResponse)
async def update_user(
    request: Request,
    user_id: int,
    name: str = Form(),
    age: str = Form(),
    gender: str = Form(),
    address: str = Form(),
    phone: str = Form(),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """UPDATE users
        SET name = %s, age = %s, gender = %s, address = %s, phone = %s
        WHERE id = %s""",
        (name, age, gender, address, phone, user_id)
    )
    db.commit()
    cursor.close()
    db.close()
    return RedirectResponse(url="/home", status_code=303)

# Delete user (confirmation page)
@app.get("/delete_user/{user_id}", response_class=HTMLResponse)
async def delete_user_form(request: Request, user_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    if not user:
        return RedirectResponse(url="/home", status_code=303)

    return templates.TemplateResponse("delete_user.html", {"request": request, "user": user})

# Delete user (post)
@app.post("/delete_user/{user_id}", response_class=HTMLResponse)
async def delete_user(request: Request, user_id: int, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    db.close()
    return RedirectResponse(url="/home", status_code=303)
