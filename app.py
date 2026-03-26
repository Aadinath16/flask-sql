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
# Config (SAFE + PRODUCTION READY)
# =================================================

def get_env(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"Missing required env variable: {name}")
    return value


DB_HOST = get_env("DB_HOST", "127.0.0.1")
DB_USER = get_env("DB_USER", required=True)
DB_NAME = get_env("DB_NAME", required=True)
DB_PASS_FILE = get_env("DB_PASS_FILE", required=True)

# ✅ Read secret safely
try:
    with open(DB_PASS_FILE) as f:
        DB_PASS = f.read().strip()
except Exception as e:
    logger.error(f"Failed to read DB password file: {str(e)}")
    raise


VOLUME_PATH = get_env("VOLUME_PATH", "/app/data")
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
# Routes
# =================================================

@app.route("/")
def index():
    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()

        conn.close()

        logger.info("Users fetched")

        return render_template("index.html", users=users)

    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return "Error fetching users", 500


@app.route("/api/add-user", methods=["POST"])
def add_user():
    data = request.json

    try:
        name = data["name"]
        email = data["email"]
        city = data["city"]

        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users(name, email, city)
                VALUES(%s, %s, %s)
                """,
                (name, email, city)
            )

        conn.commit()
        conn.close()

        logger.info("User added")

        return {"status": "success"}, 200

    except Exception as e:
        logger.error(f"Error adding user: {str(e)}")
        return {"status": "error"}, 500


@app.route("/api/users")
def get_users():
    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()

        conn.close()

        return jsonify(users)

    except Exception as e:
        logger.error(f"Error fetching users API: {str(e)}")
        return {"error": str(e)}, 500


@app.route("/api/sql", methods=["POST"])
def run_sql():
    query = request.json.get("query")

    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        conn.close()

        logger.info("SQL executed")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"SQL error: {str(e)}")
        return {"error": str(e)}, 500


# =================================================
# Volume APIs
# =================================================

@app.route("/api/volume/write")
def write_volume():
    try:
        msg = ''.join(random.choices(string.ascii_letters + string.digits, k=40))

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

    except Exception as e:
        logger.error(f"Volume write error: {str(e)}")
        return {"error": str(e)}, 500


@app.route("/api/volume/read")
def read_volume():
    try:
        files = os.listdir(VOLUME_PATH)

        logger.info("Volume read")

        return {"files": files}

    except Exception as e:
        logger.error(f"Volume read error: {str(e)}")
        return {"error": str(e)}, 500


# =================================================
# Metrics
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

# import os
# import sys
# import json
# import logging
# import random
# import string
# from datetime import datetime

# import pymysql
# from flask import Flask, render_template, request, jsonify


# # =================================================
# # App Init
# # =================================================

# app = Flask(__name__)


# # =================================================
# # Structured Logging for GCP
# # =================================================

# class GCPJsonFormatter(logging.Formatter):

#     def format(self, record):

#         return json.dumps({
#             "severity": record.levelname,
#             "message": record.getMessage(),
#             "service": "flask-gke-poc",
#             "logger": record.name
#         })


# handler = logging.StreamHandler(sys.stdout)
# handler.setFormatter(GCPJsonFormatter())

# root_logger = logging.getLogger()
# root_logger.setLevel(logging.INFO)
# root_logger.handlers = []
# root_logger.addHandler(handler)

# logger = logging.getLogger(__name__)


# # =================================================
# # Config
# # =================================================

# DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
# DB_USER = os.getenv("DB_USER")
# DB_NAME = os.getenv("DB_NAME")

# with open(os.getenv("DB_PASS_FILE")) as f:
#     DB_PASS = f.read().strip()

# VOLUME_PATH = os.getenv("VOLUME_PATH", "/app/data")

# os.makedirs(VOLUME_PATH, exist_ok=True)


# # =================================================
# # DB Connection
# # =================================================

# def get_connection():

#     return pymysql.connect(
#         host=DB_HOST,
#         user=DB_USER,
#         password=DB_PASS,
#         database=DB_NAME,
#         cursorclass=pymysql.cursors.DictCursor
#     )


# # =================================================
# # Home Page
# # =================================================

# @app.route("/")
# def index():

#     conn = get_connection()

#     with conn.cursor() as cursor:
#         cursor.execute("SELECT * FROM users")
#         users = cursor.fetchall()

#     conn.close()

#     logger.info("Users fetched")

#     return render_template("index.html", users=users)


# # =================================================
# # Add User (API)
# # =================================================

# @app.route("/api/add-user", methods=["POST"])
# def add_user():

#     data = request.json

#     try:

#         name = data["name"]
#         email = data["email"]
#         city = data["city"]   # 👈 NEW

#         conn = get_connection()

#         with conn.cursor() as cursor:

#             cursor.execute(
#                 """
#                 INSERT INTO users(name, email, city)
#                 VALUES(%s, %s, %s)
#                 """,
#                 (name, email, city)   # 👈 NEW
#             )

#         conn.commit()
#         conn.close()

#         logger.info("User added with city")

#         return {"status": "success"}, 200


#     except Exception as e:

#         logger.error(str(e))

#         return {"status": "error"}, 500


# # =================================================
# # Fetch Users (API)
# # =================================================

# @app.route("/api/users")
# def get_users():

#     conn = get_connection()

#     with conn.cursor() as cursor:
#         cursor.execute("SELECT * FROM users")
#         users = cursor.fetchall()

#     conn.close()

#     return jsonify(users)


# # =================================================
# # SQL Executor
# # =================================================

# @app.route("/api/sql", methods=["POST"])
# def run_sql():

#     query = request.json["query"]

#     try:

#         conn = get_connection()

#         with conn.cursor() as cursor:
#             cursor.execute(query)
#             result = cursor.fetchall()

#         conn.close()

#         logger.info("SQL executed")

#         return jsonify(result), 200


#     except Exception as e:

#         logger.error(str(e))

#         return {"error": str(e)}, 500


# # =================================================
# # Volume: Create File
# # =================================================

# @app.route("/api/volume/write")
# def write_volume():

#     msg = ''.join(
#         random.choices(string.ascii_letters + string.digits, k=40)
#     )

#     filename = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

#     path = os.path.join(VOLUME_PATH, filename)

#     with open(path, "w") as f:
#         f.write(msg)

#     logger.info(f"File created: {path}")

#     return {
#         "file": filename,
#         "path": path,
#         "msg": msg
#     }


# @app.route("/api/volume/read")
# def read_volume():

#     files = os.listdir(VOLUME_PATH)

#     logger.info("Volume read")

#     return {"files": files}


# # =================================================
# # Metrics / Monitoring
# # =================================================

# @app.route("/api/metrics/<int:code>")
# def api_metrics(code):

#     if code == 200:

#         logger.info("200 OK test")

#         return {"msg": "200 OK"}, 200


#     elif code == 400:

#         logger.warning("400 Bad Request test")

#         return {"msg": "400 Bad Request"}, 400


#     elif code == 500:

#         logger.error("500 Internal Error test")

#         return {"msg": "500 Error"}, 500


#     else:

#         logger.warning("Invalid metrics")

#         return {"msg": "Invalid"}, 400


# # =================================================
# # Health
# # =================================================

# @app.route("/health")
# def health():

#     logger.info("Health OK")

#     return "OK", 200


# # =================================================
# # Run
# # =================================================

# if __name__ == "__main__":

#     app.run(
#         host="0.0.0.0",
#         port=8080,
#         debug=False
#     )