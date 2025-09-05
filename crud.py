# from database import session
# from models import User, Admin

# # users operation
# class CRUD():
#     User = User
#     Admin = Admin
#     def __init__(self):
#         self.session = session

#     # for adding the user
#     def add_user(self,name,age,gender,address,phone):
#             new_user = self.User(name=name,age=age,gender=gender,address=address,phone=phone)
#             self.session.add(new_user)
#             self.session.commit()
            
#     # get all users
#     def get_users(self):
#         get_data = self.session.query(self.User).all()
#         return get_data
    
    
#     # get users by id
#     def get_user_by_id(self,id:int):
#         get_by_id = self.session.query(User).get(id)
#         return get_by_id
    

#     # Update users
#     def update_user(self,id,name,age,gender,address,phone):
#         update_data = session.query(self.User).filter(self.User.id == id).first()
#         if update_data:
#             update_data.name = name
#             update_data.age = age
#             update_data.gender = gender
#             update_data.address = address
#             update_data.phone = phone
#             self.session.commit()


#     # to delete the user
#     def delete_user(self, id: int):
#         user = self.session.query(self.User).filter(self.User.id == id).first()
#         if user:
#             self.session.delete(user)
#             self.session.commit()



#      # Register admin
#     def register_admin(self, fullname: str, username: str, hashed_password: str):
#         new_admin = self.Admin(fullname=fullname, username=username, password=hashed_password)
#         self.session.add(new_admin)
#         self.session.commit()
#         return new_admin

#     # Get admin by username
#     def get_admin_by_username(self, username: str):
#         return self.session.query(self.Admin).filter(self.Admin.username == username).first()

#     # Verify admin login
#     def login_admin(self, username: str, hashed_password: str, verify_password_func):
#         admin = self.Admin(username)
#         if admin and verify_password_func(hashed_password, admin.password):
#             return admin
#         return None



#     # Get admin by email or phone (for forgot password)
#     def get_user_by_email_or_phone(self, identifier: str):
#         return self.session.query(self.User).filter(
#             (self.User.email == identifier) | (self.User.phone == identifier)
#         ).first()


#     # Update admin password
#     def update_admin_password(self, admin_id: int, new_hashed_password: str):
#         admin = self.session.query(self.Admin).filter_by(id=admin_id).first()
#         if admin:
#             admin.password = new_hashed_password
#             self.session.commit()
#             return admin
#         return None

#     # Verify admin login (used in login route)
#     def verify_admin_login(self, username: str, verify_password_func, plain_password: str):
#         admin = self.get_admin_by_username(username)
#         if admin and verify_password_func(plain_password, admin.password):
#             return admin
#         return None


from database import session
from models import User, Admin

class CRUD:
    User = User
    Admin = Admin

    def __init__(self):
        self.session = session

    # ------------------- User Methods -------------------

    def add_user(self, name, age, gender, address, email,phone):
        new_user = self.User(name=name, age=age, gender=gender, address=address,email=email, phone=phone)
        self.session.add(new_user)
        self.session.commit()
        return new_user

    def get_users(self):
        return self.session.query(self.User).all()

    def get_user_by_id(self, id: int):
        return self.session.query(self.User).get(id)

    def update_user(self, id, name, age, gender, address, phone):
        update_data = self.session.query(self.User).filter(self.User.id == id).first()
        if update_data:
            update_data.name = name
            update_data.age = age
            update_data.gender = gender
            update_data.address = address
            update_data.phone = phone
            self.session.commit()
            return update_data

    def delete_user(self, id: int):
        user = self.session.query(self.User).filter(self.User.id == id).first()
        if user:
            self.session.delete(user)
            self.session.commit()
            return True


    def update_user_password(self, user_id: int, new_hashed_password: str):
        user = self.session.query(self.User).filter_by(id=user_id).first()
        if user:
            user.password = new_hashed_password
            self.session.commit()
            return user



    # Admin Methods 
    def register_admin(self, fullname: str, username: str, hashed_password: str, email : str, phone :str):
        new_admin = self.Admin(fullname=fullname, username=username, password=hashed_password, email=email, phone=phone)
        self.session.add(new_admin)
        self.session.commit()
        return new_admin

    def get_admin_by_username(self, username: str):
        return self.session.query(self.Admin).filter(self.Admin.username == username).first()

    def get_admin_by_email_or_phone(self, identifier: str):
        return self.session.query(self.Admin).filter(
            (self.Admin.email == identifier) | (self.Admin.phone == identifier)
        ).first()

    def verify_admin_login(self, username: str, verify_password_func, plain_password: str):
        admin = self.get_admin_by_username(username)
        if admin and verify_password_func(plain_password, admin.password):
            return admin
        return None

    def update_admin_password(self, admin_id: int, new_hashed_password: str):
        admin = self.session.query(self.Admin).filter_by(id=admin_id).first()
        if admin:
            admin.password = new_hashed_password
            self.session.commit()
            return admin
        return None

    # ------------------- Common Methods -------------------

    def get_account_by_email_or_phone(self, identifier: str):
        # Check in User
        admin = self.get_user_by_email_or_phone(identifier)
        if admin:
            return ("user", admin)

        # Check in Admin
        admin = self.get_admin_by_email_or_phone(identifier)
        if admin:
            return ("admin", admin)


    def update_user_password(self, user_id: int, new_hashed_password: str):
        user = self.session.query(self.User).filter_by(id=user_id).first()
        if user:
            user.password = new_hashed_password
            self.session.commit()
            return user
        return None
