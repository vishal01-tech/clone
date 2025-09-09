from database import session
from models import User, Admin
from datetime import datetime , timedelta

class CRUD:
    User = User
    Admin = Admin

    def __init__(self):
        self.session = session

    # ------------------- User Methods -------------------

    def add_user(self, name: str, age: int, gender: str, address: str):
        new_user = self.User(name=name, age=age, gender=gender, address=address)
        self.session.add(new_user)
        self.session.commit()
        return new_user

    def get_users(self):
        return self.session.query(self.User).all()

    def get_user_by_id(self, id: int):
        return self.session.query(self.User).filter_by(id=id).first()

    def update_user(self, id: int, name: str, age: int, gender: str, address: str):
        update_data = self.session.query(self.User).filter_by(id=id).first()
        if update_data:
            update_data.name = name
            update_data.age = age
            update_data.gender = gender
            update_data.address = address
            self.session.commit()
            return update_data
        return None

    def delete_user(self, id: int):
        user = self.session.query(self.User).filter_by(id=id).first()
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def update_user_password(self, user_id: int, new_hashed_password: str):
        user = self.session.query(self.User).filter_by(id=user_id).first()
        if user:
            user.password = new_hashed_password
            self.session.commit()
            return user
        return None

    # ------------------- Admin Methods -------------------

    def register_admin(self, fullname: str, username: str, hashed_password: str, email: str, phone: str):
        new_admin = self.Admin(
            fullname=fullname,
            username=username,
            password=hashed_password,
            email=email,
            phone=phone
        )
        self.session.add(new_admin)
        self.session.commit()
        return new_admin

    def get_admin_by_username(self, username: str):
        return self.session.query(self.Admin).filter_by(username=username).first()

    def get_admin_by_email_or_phone(self, identifier: str):
        return self.session.query(self.Admin).filter(
            (self.Admin.email == identifier) | (self.Admin.phone == identifier)
        ).first()

    def update_admin_password(self, admin_id: int, new_hashed_password: str):
        admin = self.session.query(self.Admin).filter_by(id=admin_id).first()
        print(admin)
        if admin:
            admin.password = new_hashed_password
            self.session.commit()
            return admin
        return None

    # ------------------- Common Methods -------------------

    def get_account_by_email_or_phone(self, identifier: str):
        admin = self.get_admin_by_email_or_phone(identifier)
        if admin:
            return ("admin", admin)

        user = self.session.query(self.User).filter(
            (self.User.address == identifier) | (self.User.name == identifier)
        ).first()
        if user:
            return ("user", user)

        return (None, None)


    # Save OTP in Admin table
    def save_admin_otp(self, admin_id: int, otp: str):
        admin = self.session.query(self.Admin).filter_by(id=admin_id).first()
        if admin:
            admin.otp = otp
            admin.otp_expiry = datetime.utcnow() + timedelta(minutes=5)  # OTP valid 5 mins
            self.session.commit()
            return admin
        return None

    # Verify OTP
    def verify_admin_otp(self, admin_id: int, otp: str):
        admin = self.session.query(self.Admin).filter_by(id=admin_id).first()
        if admin and admin.otp == otp and admin.otp_expiry and admin.otp_expiry > datetime.utcnow():
            # OTP valid, clear it after use
            admin.otp = None
            admin.otp_expiry = None
            self.session.commit()
            return True
        return False