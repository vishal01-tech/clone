from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mysql.connector



# Connect to MySQL
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root", 
        password="root",
        database="UsersDatabase"
    )

app = FastAPI()

# html files
templates = Jinja2Templates(directory="templates")

# style css
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routes

# login page
@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# register page
@app.get("/register", response_class=HTMLResponse)
async def sign_up(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Show the add user page
@app.get("/add_user", response_class=HTMLResponse)
async def add_user_form(request: Request):
    return templates.TemplateResponse("add_user.html", {"request": request})

# update user page
@app.get("/update_user/{user_id}", response_class=HTMLResponse)
async def update_user_form(request: Request, user_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return templates.TemplateResponse("update_user.html", {"request": request, "user": user})

# delete user page
@app.get("/delete_user/{user_id}", response_class=HTMLResponse)
async def delete_user_form(request: Request, user_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return templates.TemplateResponse("delete_user.html", {"request": request, "user": user})

# register admin
@app.post("/register")
async def register_admin(
    request: Request,
    fullname: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    reconfirm_password: str = Form(...)
):
    if password != reconfirm_password:
        return {"error": "Passwords do not match"}

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

# login admin
@app.post("/",response_class=HTMLResponse)
async def login_admin(request: Request,username: str = Form(...), password: str = Form(...)):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        cursor.close()
        db.close()
        
        if admin:
        # ✅ Pass request to TemplateResponse
            return RedirectResponse(url="/home",status_code=303)
        else:
        # Show error message on login page again
            return {"Error":"Invalid username or password"}
    
        
# displaying users
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return templates.TemplateResponse("home.html", {"request": request, "users": users})


# adding user
@app.post("/add_user", response_class=HTMLResponse)
async def add_user(
    request: Request,
    name: str = Form(...),
    age: str = Form(...),
    gender: str = Form(...),
    address: str = Form(...),
    phone: str = Form(...)
):
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

# Update user
@app.post("/update_user/{user_id}", response_class=HTMLResponse)
async def update_user(
    request: Request,
    user_id: int,
    name: str = Form(),
    age: str = Form(),
    gender: str = Form(),
    address: str = Form(),
    phone: str = Form()
):
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

# delete user
@app.post("/delete_user/{user_id}", response_class=HTMLResponse)
async def delete_user(
    request: Request,
    user_id: int,
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    db.close()
    return RedirectResponse(url="/home", status_code=303)
