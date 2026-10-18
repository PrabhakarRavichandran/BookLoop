# ============================================================
# BOOKLOOP - Flask Backend API + Static File Server
# app.py  -  Run with: python backend/app.py
# Serves BOTH the API and the frontend on port 5000
# ============================================================

from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import pooling
import os
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Flask serves static frontend from the bookloop root (one level up)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


app = Flask(__name__, static_folder=None)

# ─────────────────────────────────────────────
# EMAIL CONFIG  (update these for real email sending)
# Leave SMTP_USER empty to run in DEMO MODE — OTP is returned in API response
# ─────────────────────────────────────────────
SMTP_HOST   = "smtp.gmail.com"
SMTP_PORT   = 587
SMTP_USER   = ""          # e.g. youremail@gmail.com
SMTP_PASS   = ""          # Gmail App Password (not your real password)
EMAIL_FROM  = "BookLoop <noreply@bookloop.edu>"

# In-memory OTP store: { email -> {otp, expires_at, name, dept, year, phone, password} }
_otp_store = {}
app.secret_key = "bookloop_secret_2026_!@#"
app.config["SESSION_COOKIE_SAMESITE"]       = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"]       = True
app.config["SESSION_COOKIE_SECURE"]         = False   # HTTP on localhost
app.config["SESSION_COOKIE_PATH"]           = "/"
app.config["SESSION_PERMANENT"]             = False   # expire on browser close
app.config["SESSION_REFRESH_EACH_REQUEST"]  = True    # re-send cookie on every response

# CORS only needed if accessed from a different origin (kept for VS Code Live Server fallback)
CORS(app, supports_credentials=True, origins=[
    "null",
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
])

# ─────────────────────────────────────────────
# FRONTEND STATIC FILE ROUTES
# Serve HTML, CSS, JS, images from bookloop root
# ─────────────────────────────────────────────

@app.route("/")
def root():
    return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/<path:filename>")
def static_files(filename):
    # Block directory traversal - check using forward slashes (cross-platform safe)
    if ".." in filename:
        return "Forbidden", 403

    # Build the absolute path using os.path.join (handles both / and \ on Windows)
    target = os.path.join(FRONTEND_DIR, *filename.split("/"))

    if not os.path.isfile(target):
        return "Not found", 404

    # Determine correct directory and file name for send_from_directory
    file_dir  = os.path.dirname(target)
    file_name = os.path.basename(target)

    # Set MIME types explicitly for common assets
    import mimetypes
    mime, _ = mimetypes.guess_type(file_name)
    if mime:
        from flask import make_response
        resp = make_response(send_from_directory(file_dir, file_name))
        resp.headers["Content-Type"] = mime
        return resp

    return send_from_directory(file_dir, file_name)


# ─────────────────────────────────────────────
# DATABASE CONNECTION POOL
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "Prabhakar@2006",
    "database": "bookloop",
    "charset":  "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
}

pool = pooling.MySQLConnectionPool(pool_name="bl_pool", pool_size=5, **DB_CONFIG)


def get_conn():
    return pool.get_connection()


def query(sql, params=None, fetch=True, lastrowid=False):
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute(sql, params or ())
    if fetch:
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows
    conn.commit()
    rid = cur.lastrowid
    cur.close(); conn.close()
    return rid if lastrowid else None


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def ok(data=None, **kw):
    payload = {"success": True}
    if data is not None:
        payload["data"] = data
    payload.update(kw)
    return jsonify(payload)


def err(msg, code=400):
    return jsonify({"success": False, "message": msg}), code


def row_to_book(b):
    """Convert a DB row to the shape the frontend expects."""
    return {
        "id":          b["id"],
        "title":       b["title"],
        "author":      b["author"],
        "subject":     b["subject"],
        "semester":    b["semester"],
        "condition":   b["cond"],
        "description": b["description"] or "",
        "price":       b["price"],
        "type":        b["type"],
        "sellerId":    b["seller_id"],
        "seller":      b["seller_name"],
        "dept":        b["dept"],
        "status":      b["status"],
        "cover":       b["cover"] or "",
        "color":       b["color"] or "#6366F1",
        "offerCount":  b["offer_count"],
        "createdAt":   str(b["created_at"])[:10] if b["created_at"] else "",
    }


def row_to_user(u, include_password=False):
    d = {
        "id":     u["id"],
        "name":   u["name"],
        "dept":   u["dept"],
        "year":   u["year"],
        "email":  u["email"],
        "phone":  u["phone"] or "",
        "avatar": u["avatar"] or "",
    }
    if include_password:
        d["password"] = u["password"]
    return d


def row_to_offer(o):
    return {
        "id":               o["id"],
        "bookId":           o["book_id"],
        "bookTitle":        o["book_title"],
        "buyerId":          o["buyer_id"],
        "buyerName":        o["buyer_name"],
        "buyerDept":        o["buyer_dept"],
        "offerPrice":       o["offer_price"],
        "message":          o["message"] or "",
        "status":           o["status"],
        "createdAt":        str(o["created_at"])[:10] if o["created_at"] else "",
        "handoverCode":     o.get("handover_code") or "",
        "txStage":          o.get("tx_stage") or "",
        "sellerConfirmed":  bool(o.get("seller_confirmed", 0)),
        "buyerConfirmed":   bool(o.get("buyer_confirmed", 0)),
    }



# ─────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def login():
    d = request.get_json(force=True)
    email = (d.get("email") or "").strip().lower()
    pwd   = (d.get("password") or "")
    if not email or not pwd:
        return err("Email and password are required.")
    rows = query("SELECT * FROM users WHERE email = %s", (email,))
    if not rows or rows[0]["password"] != pwd:
        return err("Incorrect email or password.")
    user = rows[0]
    session["user_id"] = user["id"]
    session.modified = True
    return ok(row_to_user(user))


# ─────────────────────────────────────────────────────────────────────────────
# OTP HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _generate_otp():
    """Return a random 6-digit numeric OTP string."""
    return str(random.randint(100000, 999999))


def _send_otp_email(to_email, otp_code, name):
    """
    Attempt to send OTP via Gmail SMTP.
    Returns True on success, False if SMTP is not configured or fails.
    """
    if not SMTP_USER or not SMTP_PASS:
        return False   # DEMO MODE — caller will include OTP in API response
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Your BookLoop verification code is {otp_code}"
        msg["From"]    = EMAIL_FROM
        msg["To"]      = to_email

        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto;">
          <h2 style="color:#E4572E;">BookLoop</h2>
          <p>Hi {name},</p>
          <p>Your one-time verification code is:</p>
          <div style="font-size:2.5rem;font-weight:800;letter-spacing:8px;
                      text-align:center;padding:24px;background:#FAF7F2;
                      border-radius:8px;margin:24px 0;">{otp_code}</div>
          <p style="color:#8A8378;font-size:.85rem;">This code expires in 10 minutes.
          If you did not request this, ignore this email.</p>
        </div>
        """
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRATION — Step 1: send OTP
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/auth/send-otp", methods=["POST"])
def send_otp():
    """
    Validate registration fields, generate OTP, store pending registration,
    attempt to email OTP. Returns the OTP in the response body when email
    is not configured (DEMO MODE) so the UI can display it.
    """
    d     = request.get_json(force=True)
    name  = (d.get("name") or "").strip()
    dept  = (d.get("dept") or "").strip()
    year  = (d.get("year") or "").strip()
    email = (d.get("email") or "").strip().lower()
    pwd   = (d.get("password") or "")
    phone = (d.get("phone") or "").strip()

    if not all([name, dept, year, email, pwd]):
        return err("All required fields must be filled.")
    if len(pwd) < 6:
        return err("Password must be at least 6 characters.")
    if query("SELECT id FROM users WHERE email = %s", (email,)):
        return err("An account with this email already exists.")

    otp         = _generate_otp()
    expires_at  = time.time() + 600   # 10 minutes

    # Store pending registration (overwrite any previous attempt for same email)
    _otp_store[email] = {
        "otp":        otp,
        "expires_at": expires_at,
        "name":       name,
        "dept":       dept,
        "year":       year,
        "phone":      phone,
        "password":   pwd,
    }

    email_sent = _send_otp_email(email, otp, name)

    payload = {
        "email_sent": email_sent,
        "demo_mode":  not email_sent,
    }
    if not email_sent:
        # DEMO MODE — return OTP so the UI can show it
        payload["otp"] = otp

    return ok(payload)


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRATION — Step 2: verify OTP and create account
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/auth/verify-otp", methods=["POST"])
def verify_otp():
    """
    Verify the OTP entered by the user. On success, create the user account
    and remove the pending entry from the OTP store.
    """
    d     = request.get_json(force=True)
    email = (d.get("email") or "").strip().lower()
    otp   = (d.get("otp") or "").strip()

    if not email or not otp:
        return err("Email and OTP are required.")

    pending = _otp_store.get(email)
    if not pending:
        return err("No pending registration for this email. Please request a new OTP.")

    if time.time() > pending["expires_at"]:
        del _otp_store[email]
        return err("OTP has expired. Please register again.")

    if pending["otp"] != otp:
        return err("Incorrect OTP. Please check and try again.")

    # OTP is valid — create the account
    name    = pending["name"]
    initials = "".join(w[0] for w in name.split() if w)[:2].upper()
    try:
        query(
            "INSERT INTO users (name, dept, year, email, password, phone, avatar) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (name, pending["dept"], pending["year"], email,
             pending["password"], pending["phone"], initials),
            fetch=False,
        )
    except Exception as e:
        return err("Account creation failed: " + str(e))

    # Clean up OTP store
    del _otp_store[email]

    return ok({"message": "Account created successfully. You can now log in."}), 201


# Legacy endpoint kept for compatibility — now just redirects callers to use send-otp flow
@app.route("/api/auth/register", methods=["POST"])
def register():
    return err("Direct registration is disabled. Use the OTP verification flow.", 405)


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return ok()


@app.route("/api/auth/me", methods=["GET"])
def me():
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT * FROM users WHERE id = %s", (uid,))
    if not rows:
        return err("User not found.", 404)
    return ok(row_to_user(rows[0]))


# ─────────────────────────────────────────────
# BOOKS ROUTES
# ─────────────────────────────────────────────

@app.route("/api/books", methods=["GET"])
def get_books():
    rows = query("SELECT * FROM books ORDER BY id DESC")
    return ok([row_to_book(b) for b in rows])


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    rows = query("SELECT * FROM books WHERE id = %s", (book_id,))
    if not rows:
        return err("Book not found.", 404)
    return ok(row_to_book(rows[0]))


@app.route("/api/books", methods=["POST"])
def add_book():
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    user = query("SELECT * FROM users WHERE id = %s", (uid,))[0]
    d = request.get_json(force=True)
    title  = (d.get("title") or "").strip()
    author = (d.get("author") or "").strip()
    subj   = (d.get("subject") or "").strip()
    sem    = (d.get("semester") or "").strip()
    cond   = (d.get("condition") or "").strip()
    desc   = (d.get("description") or "No description.").strip()
    price  = int(d.get("price") or 0)
    btype  = d.get("type", "Sell")
    cover  = (d.get("cover") or title[:4].upper()).strip()
    color  = (d.get("color") or "#6366F1").strip()
    if not all([title, author, subj, sem, cond]):
        return err("Required fields missing.")
    if btype == "Sell" and price <= 0:
        return err("Enter a price for a Sell listing.")
    bid = query(
        """INSERT INTO books (title, author, subject, semester, cond, description,
           price, type, seller_id, seller_name, dept, cover, color)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (title, author, subj, sem, cond, desc, price, btype,
         uid, user["name"], user["dept"], cover, color),
        fetch=False, lastrowid=True,
    )
    book = query("SELECT * FROM books WHERE id = %s", (bid,))[0]
    return ok(row_to_book(book)), 201


@app.route("/api/books/<int:book_id>/status", methods=["PATCH"])
def update_book_status(book_id):
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT * FROM books WHERE id = %s", (book_id,))
    if not rows:
        return err("Book not found.", 404)
    book = rows[0]
    if book["seller_id"] != uid:
        return err("Not authorised.", 403)
    new_status = (request.get_json(force=True).get("status") or "").upper()
    if new_status not in ("AVAILABLE", "RESERVED", "SOLD"):
        return err("Invalid status.")
    query("UPDATE books SET status = %s WHERE id = %s", (new_status, book_id), fetch=False)
    book = query("SELECT * FROM books WHERE id = %s", (book_id,))[0]
    return ok(row_to_book(book))


# ─────────────────────────────────────────────
# OFFERS ROUTES
# ─────────────────────────────────────────────

@app.route("/api/offers", methods=["GET"])
def get_offers():
    rows = query("SELECT * FROM offers ORDER BY id DESC")
    return ok([row_to_offer(o) for o in rows])


@app.route("/api/offers", methods=["POST"])
def make_offer():
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    user = query("SELECT * FROM users WHERE id = %s", (uid,))[0]
    d = request.get_json(force=True)
    book_id     = int(d.get("bookId") or 0)
    offer_price = int(d.get("offerPrice") or 0)
    message     = (d.get("message") or "").strip()
    book_rows   = query("SELECT * FROM books WHERE id = %s", (book_id,))
    if not book_rows:
        return err("Book not found.", 404)
    book = book_rows[0]
    if book["status"] != "AVAILABLE":
        return err("This book is no longer available.")
    if book["seller_id"] == uid:
        return err("You cannot make an offer on your own book.")
    oid = query(
        """INSERT INTO offers (book_id, book_title, buyer_id, buyer_name, buyer_dept,
           offer_price, message) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (book_id, book["title"], uid, user["name"], user["dept"], offer_price, message),
        fetch=False, lastrowid=True,
    )
    query("UPDATE books SET offer_count = offer_count + 1 WHERE id = %s", (book_id,), fetch=False)
    offer = query("SELECT * FROM offers WHERE id = %s", (oid,))[0]
    return ok(row_to_offer(offer)), 201


@app.route("/api/offers/<int:offer_id>/accept", methods=["PATCH"])
def accept_offer(offer_id):
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT * FROM offers WHERE id = %s", (offer_id,))
    if not rows:
        return err("Offer not found.", 404)
    offer = rows[0]
    book_rows = query("SELECT * FROM books WHERE id = %s", (offer["book_id"],))
    if not book_rows or book_rows[0]["seller_id"] != uid:
        return err("Not authorised.", 403)
    # Generate a unique 8-char alphanumeric handover code
    import string
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    conn = get_conn(); cur = conn.cursor()
    cur.execute(
        "UPDATE offers SET status = CASE WHEN id = %s THEN 'ACCEPTED' ELSE 'REJECTED' END WHERE book_id = %s",
        (offer_id, offer["book_id"]),
    )
    cur.execute(
        "UPDATE offers SET handover_code = %s, tx_stage = 'ACCEPTED', seller_confirmed = 0, buyer_confirmed = 0 WHERE id = %s",
        (code, offer_id),
    )
    cur.execute("UPDATE books SET status = 'RESERVED' WHERE id = %s", (offer["book_id"],))
    conn.commit(); cur.close(); conn.close()
    return ok({"handoverCode": code})



@app.route("/api/offers/<int:offer_id>/reject", methods=["PATCH"])
def reject_offer(offer_id):
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT * FROM offers WHERE id = %s", (offer_id,))
    if not rows:
        return err("Offer not found.", 404)
    offer = rows[0]
    book_rows = query("SELECT * FROM books WHERE id = %s", (offer["book_id"],))
    if not book_rows or book_rows[0]["seller_id"] != uid:
        return err("Not authorised.", 403)
    query("UPDATE offers SET status = 'REJECTED' WHERE id = %s", (offer_id,), fetch=False)
    return ok()


# ─────────────────────────────────────────────
# WISHLIST ROUTES
# ─────────────────────────────────────────────

@app.route("/api/wishlist", methods=["GET"])
def get_wishlist():
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT book_id FROM wishlists WHERE user_id = %s", (uid,))
    return ok([r["book_id"] for r in rows])


@app.route("/api/wishlist/<int:book_id>", methods=["POST"])
def add_wishlist(book_id):
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    try:
        query(
            "INSERT IGNORE INTO wishlists (user_id, book_id) VALUES (%s, %s)",
            (uid, book_id), fetch=False,
        )
    except Exception:
        pass
    return ok()


@app.route("/api/wishlist/<int:book_id>", methods=["DELETE"])
def remove_wishlist(book_id):
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    query("DELETE FROM wishlists WHERE user_id = %s AND book_id = %s", (uid, book_id), fetch=False)
    return ok()


# ─────────────────────────────────────────────
# ADMIN - RESET (demo use)
# ─────────────────────────────────────────────
@app.route("/api/admin/reset", methods=["POST"])
def reset():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    for t in ("wishlists", "offers", "books", "users"):
        cur.execute(f"TRUNCATE TABLE {t}")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit(); cur.close(); conn.close()
    # Re-seed via schema execution
    import subprocess, sys
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    subprocess.run([
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
        "-u", "root", "-pPrabhakar@2006", "bookloop"
    ], stdin=open(schema_path), capture_output=True)
    session.clear()
    return ok()


# ─────────────────────────────────────────────
# DASHBOARD STATS  (real counts from DB)
# ─────────────────────────────────────────────

@app.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():
    """Return campus-wide aggregate statistics for the dashboard."""
    try:
        total_books    = query("SELECT COUNT(*) AS c FROM books")[0]["c"]
        available      = query("SELECT COUNT(*) AS c FROM books WHERE status='AVAILABLE'")[0]["c"]
        reserved       = query("SELECT COUNT(*) AS c FROM books WHERE status='RESERVED'")[0]["c"]
        sold           = query("SELECT COUNT(*) AS c FROM books WHERE status='SOLD'")[0]["c"]
        total_users    = query("SELECT COUNT(*) AS c FROM users")[0]["c"]
        pending_offers = query("SELECT COUNT(*) AS c FROM offers WHERE status='PENDING'")[0]["c"]
        total_offers   = query("SELECT COUNT(*) AS c FROM offers")[0]["c"]
        accepted       = query("SELECT COUNT(*) AS c FROM offers WHERE status='ACCEPTED'")[0]["c"]
        # wishlist count
        wishlisted     = query("SELECT COUNT(*) AS c FROM wishlists")[0]["c"]
        # trending: books with most offers
        trending = query(
            "SELECT id, title, author, cover, color, offer_count, type, price, status "
            "FROM books WHERE status='AVAILABLE' ORDER BY offer_count DESC, id DESC LIMIT 4"
        )
        # recent listings (newest 5)
        recent = query(
            "SELECT id, title, author, cover, color, type, price, status, seller_name, dept, created_at "
            "FROM books ORDER BY created_at DESC, id DESC LIMIT 5"
        )
        # most wishlisted
        top_wish = query(
            "SELECT b.id, b.title, b.author, b.cover, b.color, b.type, b.price, b.status, "
            "COUNT(w.id) AS wc FROM books b "
            "JOIN wishlists w ON w.book_id = b.id "
            "GROUP BY b.id ORDER BY wc DESC LIMIT 4"
        )
        # recent activity feed (offers + books, last 6 events)
        recent_offers = query(
            "SELECT 'offer' AS kind, o.id, o.book_title AS title, o.buyer_name AS actor, "
            "o.offer_price AS price, o.status, o.created_at "
            "FROM offers o ORDER BY o.created_at DESC, o.id DESC LIMIT 6"
        )
        recent_books = query(
            "SELECT 'listing' AS kind, b.id, b.title, b.seller_name AS actor, "
            "b.price, b.status, b.created_at "
            "FROM books b ORDER BY b.created_at DESC, b.id DESC LIMIT 6"
        )

        def dt_key(r):
            v = r.get("created_at")
            if v is None:
                return ""
            return str(v)

        activity = sorted(
            [
                {
                    "kind":      r["kind"],
                    "id":        r["id"],
                    "title":     r["title"],
                    "actor":     r["actor"],
                    "price":     r["price"],
                    "status":    r["status"],
                    "createdAt": str(r["created_at"])[:16] if r["created_at"] else "",
                }
                for r in (list(recent_offers) + list(recent_books))
            ],
            key=dt_key,
            reverse=True,
        )[:8]

        def book_mini(b):
            return {
                "id":     b["id"],
                "title":  b["title"],
                "author": b.get("author", ""),
                "cover":  b.get("cover", ""),
                "color":  b.get("color", "#6366F1"),
                "type":   b.get("type", "Sell"),
                "price":  b.get("price", 0),
                "status": b.get("status", "AVAILABLE"),
                "offerCount": b.get("offer_count", 0),
                "seller": b.get("seller_name", ""),
                "dept":   b.get("dept", ""),
                "createdAt": str(b["created_at"])[:10] if b.get("created_at") else "",
            }

        return ok({
            "totalBooks":    total_books,
            "available":     available,
            "reserved":      reserved,
            "sold":          sold,
            "totalUsers":    total_users,
            "pendingOffers": pending_offers,
            "totalOffers":   total_offers,
            "accepted":      accepted,
            "wishlisted":    wishlisted,
            "trending":      [book_mini(b) for b in trending],
            "recent":        [book_mini(b) for b in recent],
            "topWishlisted": [
                {**book_mini(b), "wishCount": b["wc"]}
                for b in top_wish
            ],
            "activity":      activity,
        })
    except Exception as e:
        return err("Stats failed: " + str(e), 500)


# ─────────────────────────────────────────────
# LIVE CAMPUS SIMULATION
# /api/demo/simulation  — runs 7 sequential steps
# /api/demo/reset       — restores demo to initial state
#
# Demo users are created with fixed emails tagged [DEMO].
# Foreign-key integrity is always guaranteed.
# ─────────────────────────────────────────────

DEMO_TAG          = "[DEMO]"
DEMO_BOOK_TITLE   = "Operating Systems"
DEMO_OFFER_PRICE  = 250
DEMO_MATCH_PCT    = 96

# Fixed demo user emails — used to find/create them safely
DEMO_SELLER_EMAIL = "demo.rahul@bookloop.demo"
DEMO_BUYER_EMAIL  = "demo.divya@bookloop.demo"


def _ensure_demo_user(email, name, dept, year, avatar):
    """Return the demo user row, creating it if it doesn't exist."""
    rows = query("SELECT * FROM users WHERE email = %s", (email,))
    if rows:
        return rows[0]
    uid = query(
        "INSERT INTO users (name, dept, year, email, password, phone, avatar) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (name, dept, year, email, "demo_pass_not_for_login", "", avatar),
        fetch=False, lastrowid=True,
    )
    return query("SELECT * FROM users WHERE id = %s", (uid,))[0]


def _get_or_create_demo_book(seller_id, seller_name, seller_dept):
    """Return the demo book row (create if missing). Idempotent."""
    rows = query(
        "SELECT * FROM books WHERE seller_id = %s AND description LIKE %s LIMIT 1",
        (seller_id, DEMO_TAG + "%"),
    )
    if rows:
        return rows[0]
    bid = query(
        """INSERT INTO books
           (title, author, subject, semester, cond, description,
            price, type, seller_id, seller_name, dept, cover, color, status)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'AVAILABLE')""",
        (
            DEMO_BOOK_TITLE, "Abraham Silberschatz", "Operating Systems",
            "4", "Good",
            DEMO_TAG + " Demo book for campus simulation. Covers processes, threads, memory.",
            300, "Sell",
            seller_id, seller_name, seller_dept,
            "OS", "#6366F1",
        ),
        fetch=False, lastrowid=True,
    )
    return query("SELECT * FROM books WHERE id = %s", (bid,))[0]


@app.route("/api/demo/simulation", methods=["POST"])
def run_simulation():
    """
    Execute the full 7-step campus simulation.
    Always ensures demo users exist first (FK safety).
    Idempotent — safe to call multiple times.
    """
    try:
        # ── Ensure demo users exist (FK safety first) ─────────────
        seller = _ensure_demo_user(
            DEMO_SELLER_EMAIL, "Rahul Kumar", "ECE", "2nd Year", "RK"
        )
        buyer = _ensure_demo_user(
            DEMO_BUYER_EMAIL, "Divya Nair", "IT", "2nd Year", "DN"
        )
        seller_id = seller["id"]
        buyer_id  = buyer["id"]

        # ── Ensure demo book exists and is AVAILABLE ──────────────
        book    = _get_or_create_demo_book(seller_id, seller["name"], seller["dept"])
        book_id = book["id"]
        query("UPDATE books SET status = 'AVAILABLE', offer_count = 0 WHERE id = %s",
              (book_id,), fetch=False)

        # ── Delete stale offer then create fresh PENDING offer ────
        query(
            "DELETE FROM offers WHERE book_id = %s AND buyer_id = %s",
            (book_id, buyer_id), fetch=False,
        )
        oid = query(
            """INSERT INTO offers
               (book_id, book_title, buyer_id, buyer_name, buyer_dept,
                offer_price, message, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,'PENDING')""",
            (book_id, DEMO_BOOK_TITLE, buyer_id,
             buyer["name"], buyer["dept"], DEMO_OFFER_PRICE,
             "Hi! I need this for my 4th semester. Can we meet near the library?"),
            fetch=False, lastrowid=True,
        )
        query("UPDATE books SET offer_count = 1 WHERE id = %s", (book_id,), fetch=False)

        # ── Accept the offer (sets book → RESERVED) ───────────────
        conn = get_conn(); cur = conn.cursor()
        cur.execute("UPDATE offers SET status = 'ACCEPTED' WHERE id = %s", (oid,))
        cur.execute("UPDATE books  SET status = 'RESERVED' WHERE id = %s", (book_id,))
        conn.commit(); cur.close(); conn.close()

        # ── Build timeline steps ───────────────────────────────────
        steps = [
            {
                "id": 1, "icon": "📋",
                "title": seller["name"] + ' listed "' + DEMO_BOOK_TITLE + '"',
                "sub":   seller["dept"] + " · Semester 4 · ₹300 · For Sale",
                "color": "#6366F1",
                "phase": "LISTING",
            },
            {
                "id": 2, "icon": "🔍",
                "title": buyer["name"] + ' searched for "' + DEMO_BOOK_TITLE + '"',
                "sub":   buyer["dept"] + " · Looking for Semester 4 OS textbook",
                "color": "#F59E0B",
                "phase": "REQUEST",
            },
            {
                "id": 3, "icon": "⚡",
                "title": "BookLoop found a " + str(DEMO_MATCH_PCT) + "% match",
                "sub":   "Subject · Semester · Condition — near-perfect compatibility",
                "color": "#E4572E",
                "phase": "MATCH",
            },
            {
                "id": 4, "icon": "💬",
                "title": buyer["name"] + " sent an offer of ₹" + str(DEMO_OFFER_PRICE),
                "sub":   '"Can we meet near the library?" · Offer #' + str(oid),
                "color": "#10B981",
                "phase": "OFFER",
            },
            {
                "id": 5, "icon": "✅",
                "title": seller["name"] + " accepted the offer",
                "sub":   "All other pending offers automatically declined",
                "color": "#3B82F6",
                "phase": "ACCEPTED",
            },
            {
                "id": 6, "icon": "🔒",
                "title": "Book status → RESERVED",
                "sub":   '"' + DEMO_BOOK_TITLE + '" is now reserved for ' + buyer["name"],
                "color": "#8B5CF6",
                "phase": "RESERVED",
            },
            {
                "id": 7, "icon": "🎉",
                "title": "Transaction Completed",
                "sub":   "Campus book exchange successfully facilitated by BookLoop",
                "color": "#E4572E",
                "phase": "COMPLETED",
            },
        ]

        summary = {
            "matchPct":   DEMO_MATCH_PCT,
            "offerPrice": DEMO_OFFER_PRICE,
            "status":     "Completed",
            "students":   2,
            "book":       DEMO_BOOK_TITLE,
            "bookId":     book_id,
            "offerId":    oid,
            "seller":     seller["name"],
            "buyer":      buyer["name"],
        }

        return ok({"steps": steps, "summary": summary})

    except Exception as e:
        return err("Simulation failed: " + str(e), 500)


@app.route("/api/demo/reset", methods=["POST"])
def reset_simulation():
    """
    Restore only demo-tagged data to initial state.
    Never touches real user data.
    """
    try:
        # Find demo users
        seller_rows = query("SELECT id FROM users WHERE email = %s", (DEMO_SELLER_EMAIL,))
        buyer_rows  = query("SELECT id FROM users WHERE email = %s", (DEMO_BUYER_EMAIL,))

        if seller_rows:
            seller_id = seller_rows[0]["id"]
            book_rows = query(
                "SELECT id FROM books WHERE seller_id = %s AND description LIKE %s LIMIT 1",
                (seller_id, DEMO_TAG + "%"),
            )
            if book_rows:
                book_id = book_rows[0]["id"]
                if buyer_rows:
                    query(
                        "DELETE FROM offers WHERE book_id = %s AND buyer_id = %s",
                        (book_id, buyer_rows[0]["id"]), fetch=False,
                    )
                query(
                    "UPDATE books SET status = 'AVAILABLE', offer_count = 0 WHERE id = %s",
                    (book_id,), fetch=False,
                )
        return ok({"message": "Demo reset. Ready to run again."})
    except Exception as e:
        return err("Reset failed: " + str(e), 500)



# ─────────────────────────────────────────────
# SAFE HANDOVER ROUTES
# ─────────────────────────────────────────────

@app.route("/api/offers/<int:offer_id>/handover", methods=["GET"])
def get_handover(offer_id):
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT * FROM offers WHERE id = %s", (offer_id,))
    if not rows:
        return err("Offer not found.", 404)
    offer = rows[0]
    book_rows = query("SELECT * FROM books WHERE id = %s", (offer["book_id"],))
    if not book_rows:
        return err("Book not found.", 404)
    book = book_rows[0]
    # Only seller or buyer may view
    if uid not in (offer["buyer_id"], book["seller_id"]):
        return err("Not authorised.", 403)
    return ok(row_to_offer(offer))


@app.route("/api/offers/<int:offer_id>/seller-confirm", methods=["POST"])
def seller_confirm(offer_id):
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT * FROM offers WHERE id = %s", (offer_id,))
    if not rows:
        return err("Offer not found.", 404)
    offer = rows[0]
    book_rows = query("SELECT * FROM books WHERE id = %s", (offer["book_id"],))
    if not book_rows or book_rows[0]["seller_id"] != uid:
        return err("Not authorised.", 403)
    if offer["status"] != "ACCEPTED":
        return err("Offer is not in ACCEPTED state.")
    # Advance tx_stage
    query(
        "UPDATE offers SET seller_confirmed = 1, tx_stage = 'SELLER_CONFIRMED' WHERE id = %s",
        (offer_id,), fetch=False,
    )
    # If buyer also confirmed, complete
    updated = query("SELECT * FROM offers WHERE id = %s", (offer_id,))[0]
    if updated["buyer_confirmed"]:
        _complete_transaction(offer_id, offer["book_id"])
    return ok(row_to_offer(query("SELECT * FROM offers WHERE id = %s", (offer_id,))[0]))


@app.route("/api/offers/<int:offer_id>/buyer-confirm", methods=["POST"])
def buyer_confirm(offer_id):
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT * FROM offers WHERE id = %s", (offer_id,))
    if not rows:
        return err("Offer not found.", 404)
    offer = rows[0]
    if offer["buyer_id"] != uid:
        return err("Not authorised.", 403)
    if offer["status"] != "ACCEPTED":
        return err("Offer is not in ACCEPTED state.")
    d = request.get_json(force=True)
    code = (d.get("code") or "").strip().upper()
    if not offer["handover_code"] or code != offer["handover_code"].upper():
        return err("Incorrect handover code.")
    query(
        "UPDATE offers SET buyer_confirmed = 1 WHERE id = %s",
        (offer_id,), fetch=False,
    )
    # If seller also confirmed, complete
    updated = query("SELECT * FROM offers WHERE id = %s", (offer_id,))[0]
    if updated["seller_confirmed"]:
        _complete_transaction(offer_id, offer["book_id"])
    else:
        query("UPDATE offers SET tx_stage = 'HANDOVER_PENDING' WHERE id = %s",
              (offer_id,), fetch=False)
    return ok(row_to_offer(query("SELECT * FROM offers WHERE id = %s", (offer_id,))[0]))


def _complete_transaction(offer_id, book_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE offers SET tx_stage = 'COMPLETED' WHERE id = %s", (offer_id,))
    cur.execute("UPDATE books  SET status = 'SOLD'       WHERE id = %s", (book_id,))
    conn.commit(); cur.close(); conn.close()


# ─────────────────────────────────────────────
# WANTED BOOKS ROUTES
# ─────────────────────────────────────────────

def row_to_wanted(w):
    return {
        "id":        w["id"],
        "userId":    w["user_id"],
        "userName":  w["user_name"],
        "userDept":  w["user_dept"],
        "title":     w["title"],
        "subject":   w["subject"],
        "semester":  w["semester"],
        "maxBudget": w["max_budget"],
        "message":   w["message"] or "",
        "status":    w["status"],
        "createdAt": str(w["created_at"])[:10] if w["created_at"] else "",
    }


@app.route("/api/wanted", methods=["GET"])
def get_wanted():
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT * FROM wanted_books WHERE status = 'OPEN' ORDER BY created_at DESC")
    return ok([row_to_wanted(w) for w in rows])


@app.route("/api/wanted/mine", methods=["GET"])
def get_my_wanted():
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT * FROM wanted_books WHERE user_id = %s ORDER BY created_at DESC", (uid,))
    return ok([row_to_wanted(w) for w in rows])


@app.route("/api/wanted", methods=["POST"])
def post_wanted():
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    user = query("SELECT * FROM users WHERE id = %s", (uid,))[0]
    d = request.get_json(force=True)
    title     = (d.get("title") or "").strip()
    subject   = (d.get("subject") or "").strip()
    semester  = (d.get("semester") or "").strip()
    budget    = int(d.get("maxBudget") or 0)
    message   = (d.get("message") or "").strip()
    if not title:
        return err("Book title is required.")
    wid = query(
        "INSERT INTO wanted_books (user_id, user_name, user_dept, title, subject, semester, max_budget, message) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (uid, user["name"], user["dept"], title, subject, semester, budget, message),
        fetch=False, lastrowid=True,
    )
    row = query("SELECT * FROM wanted_books WHERE id = %s", (wid,))[0]
    return ok(row_to_wanted(row)), 201


@app.route("/api/wanted/<int:wanted_id>", methods=["DELETE"])
def delete_wanted(wanted_id):
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT * FROM wanted_books WHERE id = %s", (wanted_id,))
    if not rows:
        return err("Request not found.", 404)
    if rows[0]["user_id"] != uid:
        return err("Not authorised.", 403)
    query("DELETE FROM wanted_books WHERE id = %s", (wanted_id,), fetch=False)
    return ok()


@app.route("/api/wanted/<int:wanted_id>/fulfill", methods=["POST"])
def fulfill_wanted(wanted_id):
    """Mark a wanted request as fulfilled (by the poster or a seller who responded)."""
    uid = session.get("user_id")
    if not uid:
        return err("Not authenticated.", 401)
    rows = query("SELECT * FROM wanted_books WHERE id = %s", (wanted_id,))
    if not rows:
        return err("Request not found.", 404)
    if rows[0]["user_id"] != uid:
        return err("Not authorised.", 403)
    query("UPDATE wanted_books SET status = 'FULFILLED' WHERE id = %s", (wanted_id,), fetch=False)
    return ok()


# ─────────────────────────────────────────────
# CAMPUS IMPACT STATS
# ─────────────────────────────────────────────

@app.route("/api/dashboard/impact", methods=["GET"])
def campus_impact():
    """Compute real campus impact metrics from the database."""
    try:
        books_reused = query("SELECT COUNT(*) AS c FROM books WHERE status = 'SOLD'")[0]["c"]
        exchanges    = query("SELECT COUNT(*) AS c FROM books WHERE type = 'Exchange' AND status = 'SOLD'")[0]["c"]
        donations    = query("SELECT COUNT(*) AS c FROM books WHERE type = 'Donate'")[0]["c"]
        # Estimate savings: avg price of sold books × number sold
        savings_row  = query(
            "SELECT COALESCE(SUM(price), 0) AS total FROM books WHERE status = 'SOLD' AND type = 'Sell'"
        )[0]
        savings = int(savings_row["total"])
        # Active sellers
        active_sellers = query("SELECT COUNT(DISTINCT seller_id) AS c FROM books")[0]["c"]
        # Completed transactions (offers that reached COMPLETED stage)
        completed_tx = query(
            "SELECT COUNT(*) AS c FROM offers WHERE tx_stage = 'COMPLETED'"
        )[0]["c"]
        # Total books posted
        total_listed = query("SELECT COUNT(*) AS c FROM books")[0]["c"]
        # Wanted board open requests
        wanted_open  = query("SELECT COUNT(*) AS c FROM wanted_books WHERE status = 'OPEN'")[0]["c"]

        return ok({
            "booksReused":      books_reused,
            "exchanges":        exchanges,
            "donations":        donations,
            "estimatedSavings": savings,
            "activeSellers":    active_sellers,
            "completedTx":      completed_tx,
            "totalListed":      total_listed,
            "wantedOpen":       wanted_open,
        })
    except Exception as e:
        return err("Impact stats failed: " + str(e), 500)


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys as _sys
    _no_reload = "--no-reload" in _sys.argv
    print("=" * 55)
    print("  BookLoop API  ->  http://localhost:5000")
    print("=" * 55)
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=not _no_reload,
        use_reloader=not _no_reload,
    )
