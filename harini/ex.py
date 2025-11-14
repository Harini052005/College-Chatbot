from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
password = "enter_password"  
hashed_password = "paste_hashed_code_here"  # Password from MongoDB

if bcrypt.check_password_hash(hashed_password, password):
    print("Password is correct!")
else:
    print("Password is incorrect!")

