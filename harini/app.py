from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import re
from bson.objectid import ObjectId

# Initialize Flask app 
app = Flask(__name__)
app.secret_key = "enter_secret_key"

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"

# Connect to MongoDB
client = MongoClient("update_mongodb_connection")  # Update with your MongoDB connection string
chatbot_db = client["chatbot_db"]  # Database name
responses_collection = chatbot_db["chatbot_responses"]  # Collection for chatbot responses
admin_collection = chatbot_db["admin_users"]  # Collection for admin credentials
bcrypt = Bcrypt(app)

# User class for Flask-Login
class AdminUser(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return AdminUser(user_id) if admin_collection.find_one({"username": user_id}) else None


def preprocess_input(user_input):
    """Normalize user input to improve matching."""
    return re.sub(r"[^\w\s]", "", user_input).strip().lower()  # Remove special characters & lowercase

def get_chatbot_response(user_input):
    user_input = preprocess_input(user_input)  # Clean input

    # Escape regex special characters in input for better matching
    escaped_input = re.escape(user_input)

    query = {"pattern": {"$regex": f".*{escaped_input}.*", "$options": "i"}}  # More flexible matching
    result = responses_collection.find_one(query)

    if result and "response" in result:
        return result["response"][0] if isinstance(result["response"], list) else result["response"]
    else:
        return "Sorry, I didn't understand that."



@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    try:
        user_input = request.form["user_input"]
        response = get_chatbot_response(user_input)
        return jsonify({"response": response})
    except Exception as e:
        print("Error in get_response:", str(e))
        return jsonify({"response": "Internal Server Error"}), 500


# Admin Login Route
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(f"Debug: Username entered - {username}")  # Debugging log
        
        admin = admin_collection.find_one({"username": username})
        print(f"Debug: Admin data from DB - {admin}")  

        if admin and bcrypt.check_password_hash(admin["password"], password):
            user = AdminUser(username)
            login_user(user)
            print("Debug: Admin successfully logged in!")  
            return redirect(url_for("admin_dashboard"))
        else:
            print("Debug: Login failed - Invalid credentials")  

    return render_template("admin_login.html")


# Admin Dashboard Route
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    responses = responses_collection.find()  # Fetch chatbot responses
    return render_template("admin_dashboard.html", responses=responses)

@app.route("/add_response", methods=["POST"])
@login_required
def add_response():
    pattern = request.form.get("pattern").strip()
    response = request.form.get("response").strip()

    if pattern and response:
        correct_pattern = f".*{pattern}.*"  # Automatically add `.*`
        responses_collection.insert_one({"pattern": correct_pattern, "response": [response]})
        print("Debug: Response added successfully!")  # Debugging log
    else:
        print("Debug: Missing pattern or response!")  # Debugging log

    return redirect(url_for("admin_dashboard"))

@app.route("/edit_response/<response_id>", methods=["POST"])
@login_required
def edit_response(response_id):
    pattern = request.form.get("pattern").strip()
    response = request.form.get("response").strip()

    if pattern and response:
        responses_collection.update_one(
            {"_id": ObjectId(response_id)},  # Convert ID to ObjectId
            {"$set": {"pattern": pattern, "response": [response]}}
        )
        print(f"Debug: Updated response {response_id}")  # Debug log
    else:
        print("Debug: Missing pattern or response!")

    return redirect(url_for("admin_dashboard"))

@app.route("/delete_response/<response_id>", methods=["POST"])
@login_required
def delete_response(response_id):
    responses_collection.delete_one({"_id": ObjectId(response_id)})  # Convert ID
    print(f"Debug: Deleted response {response_id}")  # Debug log
    return redirect(url_for("admin_dashboard"))

# Admin Logout Route
@app.route("/admin_logout")
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(debug=True)

