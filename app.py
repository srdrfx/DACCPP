from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "secret123"

# KẾT NỐI MONGODB
client = MongoClient("mongodb://localhost:27017/")
db = client["complaint_db"]
complaints_col = db["complaints"]
admins_col = db["admins"]

# TẠO ADMIN MẶC ĐỊNH (chạy 1 lần)
if admins_col.count_documents({}) == 0:
    admins_col.insert_one({
        "username": "admin",
        "password": "123456"
    })

# TRANG CHỦ
@app.route("/")
def index():
    return render_template("index.html")

# GỬI KHIẾU NẠI
@app.route("/add", methods=["GET", "POST"])
def add_complaint():
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "email": request.form["email"],
            "complaint": request.form["complaint"],
            "status": "Chưa xử lý"
        }
        complaints_col.insert_one(data)
        return redirect("/")
    return render_template("add_complaint.html")

# LOGIN ADMIN
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = admins_col.find_one({
            "username": request.form["username"],
            "password": request.form["password"]
        })
        if user:
            session["admin"] = user["username"]
            return redirect("/admin")
        else:
            error = "Sai tài khoản hoặc mật khẩu"
    return render_template("login.html", error=error)

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

# ADMIN DASHBOARD
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/login")
    complaints = complaints_col.find()
    return render_template("admin_dashboard.html", complaints=complaints)

# CẬP NHẬT TRẠNG THÁI
@app.route("/update/<id>/<status>")
def update_status(id, status):
    if "admin" not in session:
        return redirect("/login")
    complaints_col.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": status}}
    )
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)







 