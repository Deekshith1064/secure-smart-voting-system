from flask import Flask, render_template, request, redirect, session
import sqlite3
from config import Config
from flask import jsonify
import os

if not os.path.exists(Config.DATABASE):
    open(Config.DATABASE, "w").close()

app = Flask(__name__)
app.config.from_object(Config)


def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        voter_id = request.form["voter_id"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password, voter_id) VALUES (?, ?, ?)",
                (username, password, voter_id),
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except:
            conn.close()
            return "User already exists!"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password),
        ).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["username"] = user["username"]

            if user["role"] == "admin":
                return redirect("/admin")

            return redirect("/dashboard")

        else:
            return "Invalid credentials!"

    return render_template("login.html")


@app.route("/live-stats")
def live_stats():
    conn = get_db_connection()

    total_votes = conn.execute(
        "SELECT COUNT(*) FROM votes"
    ).fetchone()[0]

    total_candidates = conn.execute(
        "SELECT COUNT(*) FROM candidates"
    ).fetchone()[0]

    conn.close()

    return {
        "total_votes": total_votes,
        "total_candidates": total_candidates
    }


@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    user = conn.execute(
        "SELECT has_voted FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template("dashboard.html", voted=user["has_voted"])

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")


@app.route("/vote", methods=["GET", "POST"])
def vote():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    election = conn.execute(
        "SELECT status FROM election_status WHERE id = 1"
    ).fetchone()

    election_status = election["status"]

    user = conn.execute(
        "SELECT has_voted FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    has_voted = user["has_voted"]


    if request.method == "POST":

        if election_status == 1 and has_voted == 0:

            candidate_id = request.form["candidate_id"]

            conn.execute(
                "INSERT INTO votes (user_id, candidate_id) VALUES (?, ?)",
                (session["user_id"], candidate_id)
            )

            conn.execute(
                "UPDATE candidates SET vote_count = vote_count + 1 WHERE id = ?",
                (candidate_id,)
            )

            conn.execute(
                "UPDATE users SET has_voted = 1 WHERE id = ?",
                (session["user_id"],)
            )

            conn.commit()

            conn.close()

            return redirect("/results")


    candidates = conn.execute(
        "SELECT * FROM candidates"
    ).fetchall()

    conn.close()


    return render_template(
        "vote.html",
        candidates=candidates,
        election_status=election_status,
        has_voted=has_voted
    )


@app.route("/live_results")
def live_results():

    conn = get_db_connection()

    candidates = conn.execute(
        "SELECT candidate_name, vote_count FROM candidates"
    ).fetchall()

    conn.close()

    data = []

    for candidate in candidates:

        data.append({
            "name": candidate["candidate_name"],
            "votes": candidate["vote_count"]
        })

    return jsonify(data)

@app.route("/results")
def results():

    conn = get_db_connection()

    candidates = conn.execute(
        "SELECT * FROM candidates"
    ).fetchall()

    conn.close()

    total_votes = sum(candidate["vote_count"] for candidate in candidates)

    winner = None

    if total_votes > 0:
        winner = max(candidates, key=lambda x: x["vote_count"])

    return render_template(
        "results.html",
        candidates=candidates,
        total_votes=total_votes,
        winner=winner
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    conn = get_db_connection()

    if request.method == "POST":

        if "candidate_name" in request.form:

            candidate_name = request.form["candidate_name"]

            conn.execute(
                "INSERT INTO candidates (candidate_name) VALUES (?)",
                (candidate_name,)
            )

        if "start" in request.form:

            conn.execute(
                "UPDATE election_status SET status = 1 WHERE id = 1"
            )

        if "stop" in request.form:

            conn.execute(
                "UPDATE election_status SET status = 0 WHERE id = 1"
            )

        conn.commit()


    candidates = conn.execute(
        "SELECT * FROM candidates"
    ).fetchall()


    election = conn.execute(
        "SELECT status FROM election_status WHERE id = 1"
    ).fetchone()


    # ✅ Correct total vote calculation
    total_votes = sum(candidate["vote_count"] for candidate in candidates)


    conn.close()


    return render_template(
        "admin.html",
        candidates=candidates,
        election_status=election["status"],
        total_votes=total_votes
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)