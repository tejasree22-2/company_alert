from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import psycopg2
from datetime import date, datetime

app = Flask(__name__)
CORS(app)

# ------------------ EMAIL CONFIG ------------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

app.config["MAIL_USERNAME"] = "ganditejasree@gmail.com"
app.config["MAIL_PASSWORD"] = "vdjolqazbqgdgjoi"   # Gmail App Password
app.config["MAIL_DEFAULT_SENDER"] = ("Company Alert System", app.config["MAIL_USERNAME"])

mail = Mail(app)


# ------------------ DB CONFIG ------------------
DB_CONFIG = {
    "host": "localhost",
    "database": "init_postgresql",
    "user": "tejasree",
    "password": "tejasree@22",
    "port": "5432"
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/login-page")
def login_page():
    return render_template("login.html")


@app.route("/subscribe-page")
def subscribe_page():
    return render_template("subscribe.html")


@app.route("/admin")
def admin_page():
    return render_template("admin.html")

@app.route("/register-page")
def register_page():
    return render_template("register.html")
    


# ------------------ API ROUTES ------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not name or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
        """, (name, email, password))

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
        
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
        
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
        
    cur.close()
    conn.close()
        
    #  if user not found → send 404
    if not user:
        return jsonify({"message": "User not found. Please register."}), 404
        
    # user = (id, name, email, password)
    if user[3] != password:
        return jsonify({"message": "Invalid password"}), 401
        
    return jsonify({"message": "Login successful", "email": email}), 200
        


# SUBSCRIBE
@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.json
    email = data.get("email")
    city = data.get("city", "").strip()
    category = data.get("category", "").strip()

    if not email or not city or not category:
        return jsonify({"message": "Email, city, category required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    # prevent duplicate subscriptions
    cur.execute("""
        SELECT id FROM subscriptions
        WHERE user_email=%s AND city=%s AND category=%s
    """, (email, city, category))

    exists = cur.fetchone()
    if exists:
        cur.close()
        conn.close()
        return jsonify({"message": "Already subscribed to this"}), 400

    cur.execute("""
        INSERT INTO subscriptions (user_email, city, category, is_paused)
        VALUES (%s, %s, %s, FALSE)
    """, (email, city, category))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": f"Subscribed to {category} in {city}"}), 201


# GET MY SUBSCRIPTIONS
@app.route("/get-subscriptions", methods=["POST"])
def get_subscriptions():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"message": "Email required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, city, category, is_paused
        FROM subscriptions
        WHERE user_email=%s
        ORDER BY id DESC
    """, (email,))

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
def pause_subscription():
    data = request.json
    email = data.get("email")
    sub_id = data.get("subscription_id")
    pause_value = data.get("pause")  # true/false

    if email is None or sub_id is None or pause_value is None:
        return jsonify({"message": "Email, subscription_id, pause required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE subscriptions
        SET is_paused=%s
        WHERE id=%s AND user_email=%s
    """, (pause_value, sub_id, email))

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Updated successfully"}), 200


# EDIT SUBSCRIPTION (change city/category)
@app.route("/edit-subscription", methods=["POST"])
def edit_subscription():
    data = request.json
    email = data.get("email")
    sub_id = data.get("subscription_id")
    new_city = data.get("city")
    new_category = data.get("category")

    if not email or not sub_id or not new_city or not new_category:
        return jsonify({"message": "Email, subscription_id, city, category required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE subscriptions
        SET city=%s, category=%s
        WHERE id=%s AND user_email=%s
    """, (new_city, new_category, sub_id, email))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Subscription updated"}), 200


# UNSUBSCRIBE
@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    data = request.json
    email = data.get("email")
    sub_id = data.get("subscription_id")

    if not email or not sub_id:
        return jsonify({"message": "Email and subscription_id required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM subscriptions
        WHERE id=%s AND user_email=%s
    """, (sub_id, email))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Unsubscribed successfully"}), 200


# ------------------ ADMIN: ADD COMPANY + EMAIL ------------------

@app.route("/add-company", methods=["POST"])
def add_company():
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

        # 1) Insert company
        cur.execute("""
            INSERT INTO companies (company_name, address, city, category, opening_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (company_name, address, city, category, opening_date))

        # 2) Get matching users (not paused)
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

        # 3) Send emails
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



if __name__ == "__main__":
    app.run(debug=True)
