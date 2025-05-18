from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

# Ensure database folder exists
os.makedirs("database", exist_ok=True)

DB_PATH = os.path.join("database", "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            department TEXT,
            quantity INTEGER,
            condition TEXT,
            location TEXT
        )
    ''')
    
    # Create maintenance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            department TEXT,
            issue TEXT,
            status TEXT,
            date_reported TEXT
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def is_logged_in():
    return "username" in session

def is_admin():
    return session.get("role") == "admin"

@app.route("/")
def home():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# User registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        role = request.form.get("role", "user").strip()
        
        if not username or not password or role not in ("admin", "user"):
            flash("Invalid registration data.", "error")
            return redirect(url_for("register"))
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, hashed_password, role)
            )
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already taken.", "error")
            return redirect(url_for("register"))
        finally:
            conn.close()
    return render_template("register.html")

# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row and check_password_hash(row[0], password):
            session["username"] = username
            session["role"] = row[1]
            flash(f"Welcome {username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))
    
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

# Dashboard (landing page after login)
@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        flash("Please login first.", "error")
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"], role=session["role"])

# Inventory page - view and add (admins only can add)
@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if not is_logged_in():
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == "POST":
        if not is_admin():
            flash("Admin privileges required to add inventory.", "error")
            return redirect(url_for("inventory"))

        item_name = request.form["item_name"].strip()
        department = request.form["department"].strip()
        quantity = request.form.get("quantity", 0)
        condition = request.form["condition"].strip()
        location = request.form["location"].strip()

        try:
            quantity = int(quantity)
        except ValueError:
            quantity = 0

        cursor.execute('''
            INSERT INTO inventory (item_name, department, quantity, condition, location)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_name, department, quantity, condition, location))
        conn.commit()
        flash("Inventory item added.", "success")
        return redirect(url_for("inventory"))

    # SEARCH handling
    search_query = request.args.get("search")
    if search_query:
        cursor.execute("SELECT * FROM inventory WHERE department LIKE ?", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    conn.close()
    return render_template("inventory.html", inventory=items, is_admin=is_admin())

# Edit inventory item (admin only)
@app.route("/edit_inventory/<int:item_id>", methods=["GET", "POST"])
def edit_inventory(item_id):
    if not is_logged_in() or not is_admin():
        flash("Admin privileges required.", "error")
        return redirect(url_for("inventory"))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if request.method == "POST":
        item_name = request.form["item_name"].strip()
        department = request.form["department"].strip()
        quantity = request.form.get("quantity", 0)
        condition = request.form["condition"].strip()
        location = request.form["location"].strip()
        
        try:
            quantity = int(quantity)
        except ValueError:
            quantity = 0
        
        cursor.execute('''
            UPDATE inventory
            SET item_name = ?, department = ?, quantity = ?, condition = ?, location = ?
            WHERE id = ?
        ''', (item_name, department, quantity, condition, location, item_id))
        conn.commit()
        conn.close()
        flash("Inventory item updated.", "success")
        return redirect(url_for("inventory"))
    
    cursor.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    if not item:
        flash("Item not found.", "error")
        return redirect(url_for("inventory"))
    return render_template("edit_inventory.html", item=item)

# Delete inventory item (admin only)
@app.route("/delete_inventory/<int:item_id>", methods=["POST"])
def delete_inventory(item_id):
    if not is_logged_in() or not is_admin():
        flash("Admin privileges required.", "error")
        return redirect(url_for("inventory"))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Inventory item deleted.", "info")
    return redirect(url_for("inventory"))

# Maintenance page - view and add requests (admin only can add)
@app.route('/maintenance', methods=['GET', 'POST'])
def maintenance():
    if "username" not in session:
        flash("Please log in.", "error")
        return redirect("/login")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Handle POST request for adding new maintenance
    if request.method == 'POST':
        item_name = request.form['item_name']
        department = request.form['department']
        issue = request.form['issue']
        status = request.form['status']
        date_reported = request.form['date_reported']

        cursor.execute('''
            INSERT INTO maintenance (item_name, department, issue, status, date_reported)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_name, department, issue, status, date_reported))
        conn.commit()
        flash('Maintenance request submitted successfully.', 'success')

    # Handle GET request for search/filter
    department_filter = request.args.get('department', '').lower()
    issue_filter = request.args.get('issue', '').lower()
    status_filter = request.args.get('status', '').lower()

    cursor.execute("SELECT * FROM maintenance")
    all_requests = cursor.fetchall()
    conn.close()

    # Apply filters
    if department_filter or issue_filter or status_filter:
        filtered_requests = [
            req for req in all_requests
            if (department_filter in req[2].lower() if department_filter else True) and
               (issue_filter in req[3].lower() if issue_filter else True) and
               (status_filter in req[4].lower() if status_filter else True)
        ]
    else:
        filtered_requests = all_requests

    return render_template("maintenance.html", maintenance_requests=filtered_requests)

# Edit maintenance request (admin only)
@app.route("/edit_maintenance/<int:request_id>", methods=["GET", "POST"])
def edit_maintenance(request_id):
    if "username" not in session or not is_admin():
        flash("Admin privileges required.", "error")
        return redirect("/maintenance")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == "POST":
        item_name = request.form["item_name"]
        department = request.form["department"]
        issue = request.form["issue"]
        status = request.form["status"]
        date_reported = request.form["date_reported"]

        cursor.execute('''
            UPDATE maintenance
            SET item_name = ?, department = ?, issue = ?, status = ?, date_reported = ?
            WHERE id = ?
        ''', (item_name, department, issue, status, date_reported, request_id))

        conn.commit()
        conn.close()
        flash("Maintenance request updated.", "success")
        return redirect("/maintenance")

    cursor.execute("SELECT * FROM maintenance WHERE id = ?", (request_id,))
    request_data = cursor.fetchone()
    conn.close()

    return render_template("edit_maintenance.html", request_data=request_data)

# Delete maintenance request (admin only)
@app.route('/delete_maintenance/<int:req_id>', methods=['POST'])
def delete_maintenance(req_id):
    # your deletion code here
    if not is_logged_in() or not is_admin():
        flash("Admin privileges required.", "error")
        return redirect(url_for("maintenance"))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM maintenance WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()
    flash("Maintenance request deleted.", "info")
    return redirect(url_for("maintenance"))

# Update maintenance status (admin only)
@app.route("/update_status/<int:req_id>", methods=["POST"])
def update_status(req_id):
    if not is_logged_in() or not is_admin():
        flash("Admin privileges required.", "error")
        return redirect(url_for("maintenance"))
    
    new_status = request.form.get("status")
    if not new_status:
        flash("Status is required.", "error")
        return redirect(url_for("maintenance"))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE maintenance SET status = ? WHERE id = ?", (new_status, req_id))
    conn.commit()
    conn.close()
    flash("Status updated.", "success")
    return redirect(url_for("maintenance"))

# Add new maintenance request (admin only)
@app.route("/add_maintenance", methods=["GET", "POST"])
def add_maintenance():
    if request.method == "POST":
        if not is_admin():
            flash("Admin privileges required to add maintenace request.", "error")
            return redirect(url_for("maintenance"))
        item_name = request.form["item_name"]
        department = request.form["department"]
        issue = request.form["issue"]
        status = request.form["status"]
        date_reported = request.form["date_reported"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO maintenance (item_name, department, issue, status, date_reported)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_name, department, issue, status, date_reported))
        conn.commit()
        conn.close()

        flash("Maintenance request added.", "success")
        return redirect("/maintenance")

    return render_template("add_maintenance.html")

# Reports page (admin only)
@app.route("/reports")
def reports():
    if not is_logged_in() or not is_admin():
        flash("Admin privileges required.", "error")
        return redirect(url_for("dashboard"))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT department, COUNT(*) FROM inventory GROUP BY department")
    inventory_summary = cursor.fetchall()
    
    cursor.execute("SELECT status, COUNT(*) FROM maintenance GROUP BY status")
    maintenance_summary = cursor.fetchall()
    
    conn.close()
    return render_template("reports.html", inventory_summary=inventory_summary, maintenance_summary=maintenance_summary)

if __name__ == "__main__":
    app.run(debug=True)
