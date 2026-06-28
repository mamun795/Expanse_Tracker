from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, abort
from database.db import init_db, seed_db, create_user, get_user_by_email, get_user_by_id
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-change-in-prod'  # TODO: move to env var before deploy

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        if not name or not email or not password or not confirm_password:
            return render_template("register.html", error="All fields are required.")
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")
        if get_user_by_email(email):
            return render_template("register.html", error="An account with that email already exists.")
        password_hash = generate_password_hash(password)
        new_id = create_user(name, email, password_hash)
        session["user_id"] = new_id
        return redirect(url_for("profile"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not email or not password:
            return render_template("login.html", error="All fields are required.")
        user = get_user_by_email(email)
        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid email or password.")
        session.clear()                   # prevent session fixation
        session["user_id"] = user["id"]
        return redirect(url_for("profile"))
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    db_user = get_user_by_id(session["user_id"])
    if db_user is None:
        session.clear()
        return redirect(url_for("login"))

    try:
        created = datetime.strptime(db_user["created_at"][:19], "%Y-%m-%d %H:%M:%S")
        member_since = created.strftime("%B %Y")
    except (TypeError, ValueError):
        member_since = "Recently"

    parts = db_user["name"].split()
    initials = parts[0][0].upper() + (parts[1][0].upper() if len(parts) > 1 else "")
    user = {
        "name": db_user["name"],
        "email": db_user["email"],
        "member_since": member_since,
        "initials": initials,
    }

    stats = [
        {"label": "Total Spent",  "value": "৳8,450", "sub": "all time",       "sub_class": ""},
        {"label": "Transactions", "value": "24",      "sub": "logged",         "sub_class": ""},
        {"label": "Top Category", "value": "Food",    "sub": "most frequent",  "sub_class": "mock-stat-sub--success"},
    ]

    transactions = [
        {"date": "June 22, 2026", "description": "Grocery run",            "category": "Food",          "amount": "৳850"},
        {"date": "June 18, 2026", "description": "Electricity bill",       "category": "Bills",         "amount": "৳1,200"},
        {"date": "June 15, 2026", "description": "Monthly bus pass",       "category": "Transport",     "amount": "৳450"},
        {"date": "June 10, 2026", "description": "Streaming subscription", "category": "Entertainment", "amount": "৳180"},
    ]

    categories = [
        {"name": "Food",      "amount": "৳2,900", "bar_class": "mock-cat-bar--orange", "width_class": "bar-w-65"},
        {"name": "Bills",     "amount": "৳1,850", "bar_class": "mock-cat-bar--blue",   "width_class": "bar-w-42"},
        {"name": "Transport", "amount": "৳1,200", "bar_class": "mock-cat-bar--purple", "width_class": "bar-w-28"},
        {"name": "Shopping",  "amount": "৳950",   "bar_class": "mock-cat-bar--green",  "width_class": "bar-w-22"},
    ]

    return render_template("profile.html", user=user, stats=stats,
                           transactions=transactions, categories=categories)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
