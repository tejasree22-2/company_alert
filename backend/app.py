from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import psycopg2
from datetime import date, datetime
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))
CORS(app, supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"

class User(UserMixin):
    def __init__(self, id, name, email, password, role):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, password, role FROM users WHERE id=%s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return User(row[0], row[1], row[2], row[3], row[4])
    return None

# ------------------ EMAIL CONFIG ------------------
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config["MAIL_USE_SSL"] = False

app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = ("Company Alert System", app.config["MAIL_USERNAME"])

mail = Mail(app)


# ------------------ DB CONFIG ------------------
DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/login-page")
def login_page():
    return render_template("login.html")


@app.route("/subscribe-page")
@login_required
def subscribe_page():
    return render_template("subscribe.html")


@app.route("/admin")
@login_required
def admin_page():
    if current_user.role != "admin":
        return jsonify({"message": "Access denied. Admin only."}), 403
    return render_template("admin.html")


@app.route("/register-page")
def register_page():
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_page"))


# ------------------ API ROUTES ------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not name or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    hashed_password = generate_password_hash(password)

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, 'user')
        """, (name, email, hashed_password))

        conn.commit()
        return jsonify({"message": "Registered successfully! Redirecting to login..."}), 201

    except Exception as e:
        conn.rollback()

        if "users_email_key" in str(e) or "duplicate key" in str(e):
            return jsonify({"message": "Email already exists. Please login."}), 400

        return jsonify({"message": f"Registration failed: {str(e)}"}), 500

    finally:
        cur.close()
        conn.close()


#  LOGIN
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
        
    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400
        
    conn = get_conn()
    cur = conn.cursor()
        
    cur.execute("SELECT id, name, email, password, role FROM users WHERE email=%s", (email,))
    user_row = cur.fetchone()
        
    cur.close()
    conn.close()
        
    if not user_row:
        return jsonify({"message": "User not found. Please register."}), 404
        
    if not check_password_hash(user_row[3], password):
        return jsonify({"message": "Invalid password"}), 401
    
    user = User(user_row[0], user_row[1], user_row[2], user_row[3], user_row[4])
    login_user(user)
        
    return jsonify({
        "message": "Login successful", 
        "email": email,
        "role": user_row[4],
        "name": user_row[1]
    }), 200


@app.route("/check-auth")
def check_auth():
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role
        }), 200
    return jsonify({"authenticated": False}), 401


# SUBSCRIBE
@app.route("/subscribe", methods=["POST"])
@login_required
def subscribe():
    data = request.json
    city = data.get("city", "").strip()
    category = data.get("category", "").strip()

    if not city or not category:
        return jsonify({"message": "City and category required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM subscriptions
        WHERE user_email=%s AND city=%s AND category=%s
    """, (current_user.email, city, category))

    exists = cur.fetchone()
    if exists:
        cur.close()
        conn.close()
        return jsonify({"message": "Already subscribed to this"}), 400

    cur.execute("""
        INSERT INTO subscriptions (user_email, city, category, is_paused)
        VALUES (%s, %s, %s, FALSE)
    """, (current_user.email, city, category))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": f"Subscribed to {category} in {city}"}), 201


# GET MY SUBSCRIPTIONS
@app.route("/get-subscriptions", methods=["GET"])
@login_required
def get_subscriptions():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, city, category, is_paused
        FROM subscriptions
        WHERE user_email=%s
        ORDER BY id DESC
    """, (current_user.email,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    subscriptions = []
    for r in rows:
        subscriptions.append({
            "id": r[0],
            "city": r[1],
            "category": r[2],
            "is_paused": r[3]
        })

    return jsonify({"subscriptions": subscriptions}), 200


# PAUSE / UNPAUSE
@app.route("/pause-subscription", methods=["POST"])
@login_required
def pause_subscription():
    data = request.json
    sub_id = data.get("subscription_id")
    pause_value = data.get("pause")

    if sub_id is None or pause_value is None:
        return jsonify({"message": "subscription_id, pause required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE subscriptions
        SET is_paused=%s
        WHERE id=%s AND user_email=%s
    """, (pause_value, sub_id, current_user.email))

    conn.commit()
    rows_affected = cur.rowcount
    cur.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({"message": "Subscription not found"}), 404

    return jsonify({"message": "Updated successfully"}), 200


# EDIT SUBSCRIPTION (change city/category)
@app.route("/edit-subscription", methods=["POST"])
@login_required
def edit_subscription():
    data = request.json
    sub_id = data.get("subscription_id")
    new_city = data.get("city")
    new_category = data.get("category")

    if not sub_id or not new_city or not new_category:
        return jsonify({"message": "subscription_id, city, category required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE subscriptions
        SET city=%s, category=%s
        WHERE id=%s AND user_email=%s
    """, (new_city, new_category, sub_id, current_user.email))

    conn.commit()
    rows_affected = cur.rowcount
    cur.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({"message": "Subscription not found"}), 404

    return jsonify({"message": "Subscription updated"}), 200


# UNSUBSCRIBE
@app.route("/unsubscribe", methods=["POST"])
@login_required
def unsubscribe():
    data = request.json
    sub_id = data.get("subscription_id")

    if not sub_id:
        return jsonify({"message": "subscription_id required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM subscriptions
        WHERE id=%s AND user_email=%s
    """, (sub_id, current_user.email))

    conn.commit()
    rows_affected = cur.rowcount
    cur.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({"message": "Subscription not found"}), 404

    return jsonify({"message": "Unsubscribed successfully"}), 200


# ------------------ ADMIN: ADD COMPANY + EMAIL ------------------

@app.route("/add-company", methods=["POST"])
@login_required
def add_company():
    if current_user.role != "admin":
        return jsonify({"message": "Access denied. Admin only."}), 403
    
    try:
        data = request.json
        company_name = data.get("company_name")
        address = data.get("address")
        city = data.get("city")
        category = data.get("category")
        opening_date = data.get("opening_date")

        if not company_name or not address or not city or not category:
            return jsonify({"message": "All fields required"}), 400

        if opening_date:
            opening_date = datetime.strptime(opening_date, "%Y-%m-%d").date()
        else:
            opening_date = date.today()

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO companies (company_name, address, city, category, opening_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (company_name, address, city, category, opening_date))

        cur.execute("""
            SELECT user_email
            FROM subscriptions
            WHERE TRIM(LOWER(city)) = TRIM(LOWER(%s))
              AND TRIM(LOWER(category)) = TRIM(LOWER(%s))
              AND is_paused = FALSE
        """, (city, category))
        

        users = cur.fetchall()
        conn.commit()

        cur.close()
        conn.close()

        print("Matching emails found:", users, flush=True)

        sent_count = 0

        for u in users:
            email_to = u[0]

            msg = Message(
                subject=f"New {category} company opened in {city}!",
                recipients=[email_to]
            )

            msg.body = f"""
Hello 

A new company has opened in your subscribed area!

Company: {company_name}
City: {city}
Category: {category}
Address: {address}
Opening Date: {opening_date}

Thanks,
Company Alert System
            """

            try:
                mail.send(msg)
                print(f"Email sent to {email_to}", flush=True)
                sent_count += 1
            except Exception as mail_error:
                print(f"Email failed to {email_to}: {mail_error}", flush=True)

        return jsonify({
            "message": f"Company added successfully. Emails sent to {sent_count} users."
        }), 201

    except Exception as e:
        print("Error in add_company:", str(e), flush=True)
        return jsonify({"message": "Failed to add company", "error": str(e)}), 400

@app.route("/mcp/subscriptions", methods=["GET"])
def mcp_get_subscriptions():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, city, category, is_paused
        FROM subscriptions
        ORDER BY id DESC
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({
        "subscriptions": [
            {
                "id": r[0],
                "city": r[1],
                "category": r[2],
                "is_paused": r[3]
            } for r in rows
        ]
    })

@app.route("/mcp/add-company", methods=["POST"])
def mcp_add_company():
    data = request.json

    company_name = data.get("company_name")
    city = data.get("city")
    category = data.get("category")
    address = data.get("address", "Auto generated")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO companies (company_name, address, city, category)
        VALUES (%s, %s, %s, %s)
    """, (company_name, address, city, category))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Company added successfully"})    

if __name__ == "__main__":
    app.run(debug=True)
