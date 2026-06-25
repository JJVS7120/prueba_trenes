from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint("auth", __name__)

# -------------------
# LOGIN
# -------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.activo:

                flash(
                    "Usuario desactivado"
                )

                return redirect(
                    url_for("auth.login")
                )
            login_user(user)
            if user.cambiar_password:

                return redirect(
                    url_for("main.cambiar_password")
                    )

            return redirect(
                url_for("main.home")
            )
            return redirect(url_for("main.dashboard"))

        flash("Email o contraseña incorrectos")

    return render_template("login.html")


# -------------------
# REGISTER
# -------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # evitar duplicados
        if User.query.filter_by(email=email).first():
            flash("Email ya registrado")
            return redirect(url_for("auth.register"))

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# -------------------
# LOGOUT
# -------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
