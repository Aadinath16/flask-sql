import os
import sys
import json
import logging
import random
import string
from datetime import datetime

import pymysql
from flask import Flask, render_template, request, jsonify


# =================================================
# App Init
# =================================================

app = Flask(__name__)


# =================================================
# Structured Logging for GCP
# =================================================

class GCPJsonFormatter(logging.Formatter):

    def format(self, record):

        return json.dumps({
            "severity": record.levelname,
            "message": record.getMessage(),
            "service": "flask-gke-poc",
            "logger": record.name
        })


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(GCPJsonFormatter())

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers = []
root_logger.addHandler(handler)

logger = logging.getLogger(__name__)


# =================================================
# Config
# =================================================

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

VOLUME_PATH = os.getenv("VOLUME_PATH", "/app/data")

os.makedirs(VOLUME_PATH, exist_ok=True)


# =================================================
# DB Connection
# =================================================

def get_connection():

    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )


# =================================================
# Home Page
# =================================================

@app.route("/")
def index():

    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

    conn.close()

    logger.info("Users fetched")

    return render_template("index.html", users=users)


# =================================================
# Add User (API)
# =================================================

@app.route("/api/add-user", methods=["POST"])
def add_user():

    data = request.json

    try:

        name = data["name"]
        email = data["email"]
        city = data["city"]   # 👈 NEW

        conn = get_connection()

        with conn.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO users(name, email, city)
                VALUES(%s, %s, %s)
                """,
                (name, email, city)   # 👈 NEW
            )

        conn.commit()
        conn.close()

        logger.info("User added with city")

        return {"status": "success"}, 200


    except Exception as e:

        logger.error(str(e))

        return {"status": "error"}, 500


# =================================================
# Fetch Users (API)
# =================================================

@app.route("/api/users")
def get_users():

    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

    conn.close()

    return jsonify(users)


# =================================================
# SQL Executor
# =================================================

@app.route("/api/sql", methods=["POST"])
def run_sql():

    query = request.json["query"]

    try:

        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()

        logger.info("SQL executed")

        return jsonify(result), 200


    except Exception as e:

        logger.error(str(e))

        return {"error": str(e)}, 500


# =================================================
# Volume: Create File
# =================================================

@app.route("/api/volume/write")
def write_volume():

    msg = ''.join(
        random.choices(string.ascii_letters + string.digits, k=40)
    )

    filename = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    path = os.path.join(VOLUME_PATH, filename)

    with open(path, "w") as f:
        f.write(msg)

    logger.info(f"File created: {path}")

    return {
        "file": filename,
        "path": path,
        "msg": msg
    }


@app.route("/api/volume/read")
def read_volume():

    files = os.listdir(VOLUME_PATH)

    logger.info("Volume read")

    return {"files": files}


# =================================================
# Metrics / Monitoring
# =================================================

@app.route("/api/metrics/<int:code>")
def api_metrics(code):

    if code == 200:

        logger.info("200 OK test")

        return {"msg": "200 OK"}, 200


    elif code == 400:

        logger.warning("400 Bad Request test")

        return {"msg": "400 Bad Request"}, 400


    elif code == 500:

        logger.error("500 Internal Error test")

        return {"msg": "500 Error"}, 500


    else:

        logger.warning("Invalid metrics")

        return {"msg": "Invalid"}, 400


# =================================================
# Health
# =================================================

@app.route("/health")
def health():

    logger.info("Health OK")

    return "OK", 200


# =================================================
# Run
# =================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )