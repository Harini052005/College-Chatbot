from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
password = "admin123"  
hashed_password = "$2b$12$mZfiAkcsaudyFtbqqFLNjO/Cdb/zwQ.hHgXuQ.OgmNfLMRB26FWt6"  # Password from MongoDB

if bcrypt.check_password_hash(hashed_password, password):
    print("Password is correct!")
else:
    print("Password is incorrect!")
