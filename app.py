from flask import Flask, request, redirect, session, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

def get_db_connection():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn

login_page = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">  
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Welcome / Login</title> 
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<style>
html, body { height: 100%; margin: 0; font-family: Arial, sans-serif; }
body { background: linear-gradient(to right, #6a11cb, #2575fc); display: flex; justify-content: center; align-items: center; }
.form-container { background-color: rgba(255,255,255,0.9); padding: 2rem 3rem; border-radius: 25px; width: 400px; text-align: center; box-shadow: 0 0 15px rgba(0,0,0,0.3);}
.form-container input { width: 100%; margin-bottom: 1rem; padding: 0.5rem; border-radius: 8px; border: 1px solid #ccc; }
.btn-block { width: 100%; }
</style>
</head>
<body>
<div class="form-container">
    <h3>Welcome!</h3>
    {% if login_error %}
        <div class="alert alert-danger">{{ login_error }}</div>
    {% endif %}
    <form action="/" method="POST">
        <input type="email" name="email" placeholder="Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit" class="btn btn-info btn-block">Login</button>
    </form>
    <hr>
    <button class="btn btn-success btn-block" data-bs-toggle="modal" data-bs-target="#registerModal">Register an Account</button>
</div>

<!-- Register Modal -->
<div class="modal fade" id="registerModal" tabindex="-1" aria-labelledby="registerModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form method="POST" action="/register">
        <div class="modal-header">
          <h5 class="modal-title" id="registerModalLabel">Register New Account</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
            {% if register_error %}
                <div class="alert alert-danger">{{ register_error }}</div>
            {% endif %}
            <input type="text" name="firstname" placeholder="First Name" required>
            <input type="text" name="lastname" placeholder="Last Name" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Password" required>
        </div>
        <div class="modal-footer">
          <button type="submit" class="btn btn-success btn-block">Register</button>
        </div>
      </form>
    </div>
  </div>
</div>

</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def login():
    login_error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM USERS WHERE email=? AND password=?", (email, password)).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["first_name"]
            return redirect("/dashboard")
        else:
            login_error = "Invalid email or password"
    return render_template_string(login_page, login_error=login_error, register_error=None)

@app.route("/register", methods=["POST"])
def register():
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM USERS WHERE email=?", (email,)).fetchone()
    if existing:
        error = "Email already exists!"
        conn.close()
        return render_template_string(login_page, login_error=None, register_error=error)
    else:
        conn.execute(
            "INSERT INTO USERS (first_name,last_name,email,password,is_admin) VALUES (?,?,?,?,0)",
            (firstname, lastname, email, password)
        )
        conn.commit()
        user = conn.execute("SELECT * FROM USERS WHERE email=?", (email,)).fetchone()
        session["user_id"] = user["id"]
        session["username"] = user["first_name"]
        conn.close()
        return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    return f"<h2>Welcome {session['username']}!</h2><p><a href='/logout'>Logout</a></p>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
