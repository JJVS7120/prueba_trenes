from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import User
from . import db
from .decorators import admin_required
from sqlalchemy import or_,func
from .models import (
    User,
    Articulo,
    MaestroArticulo
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():

    total_users = User.query.count()
    total_admins = User.query.filter_by(role="admin").count()
    total_normal = User.query.filter_by(role="user").count()

    return render_template(
        "dashboard.html",
        user=current_user,
        total_users=total_users,
        total_admins=total_admins,
        total_normal=total_normal
    )


# 👑 PANEL ADMIN
@main_bp.route("/admin")
@admin_required
def admin_panel():
    users = User.query.all()
    return render_template("admin.html", users=users)


@main_bp.route("/admin/delete/<int:user_id>")
@admin_required
def delete_user(user_id):

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
            flash("No puedes eliminar tu propio usuario")
            return redirect(url_for("main.admin_panel"))
    # 🔒 evitar borrar el último admin
    if user.role == "admin":
        admin_count = User.query.filter_by(role="admin").count()

        if admin_count <= 1:
            flash("No puedes eliminar el último administrador")
            return redirect(url_for("main.admin_panel"))

    db.session.delete(user)
    db.session.commit()

    flash("Usuario eliminado")
    return redirect(url_for("main.admin_panel"))

@main_bp.route("/admin/make-admin/<int:user_id>")
@admin_required
def make_admin(user_id):

    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        flash("El usuario ya es admin")
        return redirect(url_for("main.admin_panel"))

    user.role = "admin"
    db.session.commit()

    flash("Usuario actualizado a admin")
    return redirect(url_for("main.admin_panel"))

@main_bp.route("/admin/edit/<int:user_id>", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):

    user = User.query.get_or_404(user_id)

    if request.method == "POST":

        user.username = request.form.get("username")
        user.email = request.form.get("email")
        user.role = request.form.get("role")

        db.session.commit()

        return redirect(url_for("main.admin_panel"))

    return render_template(
        "edit_user.html",
        user=user
    )

@main_bp.route("/admin/create", methods=["GET", "POST"])
@admin_required
def create_user():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        # comprobar email duplicado
        if User.query.filter_by(email=email).first():
            flash("Ese email ya existe")
            return redirect(url_for("main.create_user"))

        user = User(
            username=username,
            email=email,
            role=role
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Usuario creado correctamente")

        return redirect(url_for("main.admin_panel"))

    return render_template("create_user.html")


@main_bp.route("/admin/articulos")
@admin_required
def admin_articulos():

    buscar = request.args.get(
        "buscar",
        ""
    ).strip()

    query = db.session.query(
        Articulo,
        User
    ).join(
        User,
        Articulo.user_id == User.id
    )

    if buscar:

        query = query.filter(

            or_(

                User.username.ilike(
                    f"%{buscar}%"
                ),

                Articulo.descripcion.ilike(
                    f"%{buscar}%"
                ),

                Articulo.referencia.ilike(
                    f"%{buscar}%"
                ),

                Articulo.numero.cast(db.String).ilike(
                    f"%{buscar}%"
                )

            )
        )

    resultados = query.order_by(
        User.username,
        Articulo.numero
    ).all()

    return render_template(
        "admin_articulos.html",
        resultados=resultados,
        buscar=buscar
    )

@main_bp.route("/admin/usuario/<int:user_id>")
@admin_required
def admin_usuario(user_id):

    usuario = User.query.get_or_404(user_id)

    articulos = Articulo.query.filter_by(
        user_id=user_id
    ).order_by(
        Articulo.numero
    ).all()

    return render_template(
        "admin_usuario.html",
        usuario=usuario,
        articulos=articulos
    )

@main_bp.route("/admin/estadisticas")
@admin_required
def admin_estadisticas():

    total_usuarios = User.query.count()

    total_articulos = Articulo.query.count()

    total_marcas = db.session.query(
        Articulo.marca
    ).distinct().count()

    total_ubicaciones = db.session.query(
        Articulo.ubicacion
    ).distinct().count()

    total_referencias = db.session.query(
        Articulo.referencia
    ).distinct().count()

    referencias_unicas = db.session.query(
        Articulo.referencia
    ).distinct().count()

    ranking_marcas = db.session.query(
        Articulo.marca,
        func.count(Articulo.id)
    ).group_by(
        Articulo.marca
    ).order_by(
        func.count(Articulo.id).desc()
    ).limit(20).all()

    ranking_tipos = db.session.query(
        Articulo.tipo,
        func.count(Articulo.id)
    ).group_by(
        Articulo.tipo
    ).order_by(
        func.count(Articulo.id).desc()
    ).limit(20).all()

    ranking_ubicaciones = db.session.query(
        Articulo.ubicacion,
        func.count(Articulo.id)
    ).group_by(
        Articulo.ubicacion
    ).order_by(
        func.count(Articulo.id).desc()
    ).limit(20).all()

    return render_template(
        "admin_estadisticas.html",
        total_usuarios=total_usuarios,
        total_articulos=total_articulos,
        total_marcas=total_marcas,
        total_ubicaciones=total_ubicaciones,
        total_referencias=total_referencias,
        ranking_marcas=ranking_marcas,
        ranking_tipos=ranking_tipos,
        ranking_ubicaciones=ranking_ubicaciones,
        referencias_unicas=referencias_unicas
    )


@main_bp.route("/admin/sin-inventario")
@admin_required
def usuarios_sin_inventario():

    usuarios = User.query.all()

    sin_inventario = []

    for usuario in usuarios:

        cantidad = Articulo.query.filter_by(
            user_id=usuario.id
        ).count()

        if cantidad == 0:

            sin_inventario.append(usuario)

    return render_template(
        "admin_sin_inventario.html",
        usuarios=sin_inventario
    )

@main_bp.route("/base-maestra")
@admin_required
def base_maestra():

    buscar = request.args.get("buscar", "").strip()
    marca = request.args.get("marca", "").strip()
    tipo = request.args.get("tipo", "").strip()
    epoca = request.args.get("epoca", "").strip()

    query = MaestroArticulo.query

    if buscar:

        query = query.filter(
            db.or_(
                MaestroArticulo.referencia.ilike(f"%{buscar}%"),
                MaestroArticulo.descripcion.ilike(f"%{buscar}%")
            )
        )

    if marca:
        query = query.filter(
            MaestroArticulo.marca == marca
        )

    if tipo:
        query = query.filter(
            MaestroArticulo.tipo == tipo
        )

    if epoca:
        query = query.filter(
            MaestroArticulo.epoca == epoca
        )

    fichas = query.order_by(
        MaestroArticulo.marca,
        MaestroArticulo.referencia
    ).all()

    marcas = db.session.query(
        MaestroArticulo.marca
    ).distinct().order_by(
        MaestroArticulo.marca
    ).all()

    tipos = db.session.query(
        MaestroArticulo.tipo
    ).distinct().order_by(
        MaestroArticulo.tipo
    ).all()

    epocas = db.session.query(
        MaestroArticulo.epoca
    ).distinct().order_by(
        MaestroArticulo.epoca
    ).all()
    ficha_articulos = {}

    for ficha in fichas:

        articulos = Articulo.query.filter(
            Articulo.referencia == ficha.referencia
        ).all()

        usuarios = []

        for articulo in articulos:

            if articulo.owner.username not in usuarios:
                usuarios.append(
                    articulo.owner.username
                )

        ficha_articulos[ficha.id] = usuarios
        
    return render_template(
        "admin_maestro.html",
        fichas=fichas,
        buscar=buscar,
        marca=marca,
        tipo=tipo,
        epoca=epoca,
        marcas=marcas,
        tipos=tipos,
        epocas=epocas,
        ficha_articulos=ficha_articulos
    )


@main_bp.route("/admin/generar-maestro")
@admin_required
def generar_maestro():

    referencias = db.session.query(
        Articulo.referencia
    ).distinct().all()

    creadas = 0
    actualizadas = 0

    campos = [
        "marca",
        "descripcion",
        "matricula",
        "matricula_ii",
        "epoca",
        "caja",
        "tipo",
        "ejes",
        "rodaje",
        "longitud",
        "administracion",
        "librea",
        "envejecido",
        "clasificacion",
        "mercancia",
        "estado",
        "necesidades",
        "rodaje_detalle",
        "imagen"
    ]

    for (referencia,) in referencias:

        if not referencia:
            continue

        maestro = MaestroArticulo.query.filter_by(
            referencia=referencia
        ).first()

        if not maestro:

            maestro = MaestroArticulo(
                referencia=referencia
            )

            db.session.add(maestro)

            creadas += 1

        else:

            actualizadas += 1

        articulos = Articulo.query.filter_by(
            referencia=referencia
        ).all()

        for campo in campos:

            valor_actual = getattr(
                maestro,
                campo
            )

            if valor_actual:
                continue

            for articulo in articulos:

                valor = getattr(
                    articulo,
                    campo
                )

                if valor and str(valor).strip():

                    setattr(
                        maestro,
                        campo,
                        valor
                    )

                    break

    db.session.commit()

    flash(
        f"Base maestra generada. "
        f"Creadas: {creadas} "
        f"Actualizadas: {actualizadas}"
    )

    return redirect(
        url_for("main.admin_maestro")
    )


@main_bp.route("/admin/maestro/<int:id>")
@admin_required
def maestro_detalle(id):

    ficha = MaestroArticulo.query.get_or_404(id)

    return render_template(
        "admin_maestro_detalles.html",
        ficha=ficha
    )


@main_bp.route(
    "/admin/maestro/<int:id>/editar",
    methods=["GET", "POST"]
)
@admin_required
def editar_maestro(id):

    ficha = MaestroArticulo.query.get_or_404(id)

    if request.method == "POST":

        ficha.marca = request.form.get("marca")
        ficha.descripcion = request.form.get("descripcion")
        ficha.matricula = request.form.get("matricula")
        ficha.matricula_ii = request.form.get("matricula_ii")
        ficha.epoca = request.form.get("epoca")
        ficha.caja = request.form.get("caja")
        ficha.tipo = request.form.get("tipo")
        ficha.ejes = request.form.get("ejes")
        ficha.rodaje = request.form.get("rodaje")
        ficha.longitud = request.form.get("longitud")
        ficha.administracion = request.form.get("administracion")
        ficha.librea = request.form.get("librea")
        ficha.envejecido = request.form.get("envejecido")
        ficha.clasificacion = request.form.get("clasificacion")
        ficha.mercancia = request.form.get("mercancia")
        ficha.estado = request.form.get("estado")
        ficha.necesidades = request.form.get("necesidades")
        ficha.rodaje_detalle = request.form.get("rodaje_detalle")
        ficha.imagen = request.form.get("imagen")

        db.session.commit()

        flash("Ficha actualizada")

        return redirect(
            url_for(
                "main.maestro_detalle",
                id=ficha.id
            )
        )

    return render_template(
        "admin_editar_maestro.html",
        ficha=ficha
    )



@main_bp.route(
    "/admin/maestro/<int:id>/validar"
)
@admin_required
def validar_maestro(id):

    ficha = MaestroArticulo.query.get_or_404(id)

    ficha.validada = True

    ficha.validada_por = current_user.username

    db.session.commit()

    flash("Ficha validada")

    return redirect(
        url_for(
            "main.maestro_detalle",
            id=id
        )
    )

@main_bp.route(
    "/admin/maestro/<int:id>/desvalidar"
)
@admin_required
def desvalidar_maestro(id):

    ficha = MaestroArticulo.query.get_or_404(id)

    ficha.validada = False

    ficha.validada_por = None

    db.session.commit()

    flash("Validación eliminada")

    return redirect(
        url_for(
            "main.maestro_detalle",
            id=id
        )
    )

@main_bp.route(
    "/cambiar-password",
    methods=["GET", "POST"]
)
@login_required
def cambiar_password():

    if request.method == "POST":

        actual = request.form["actual"]

        nueva = request.form["nueva"]

        repetir = request.form["repetir"]

        if not current_user.check_password(actual):

            flash("Contraseña actual incorrecta")

            return redirect(
                url_for("main.cambiar_password")
            )

        if nueva != repetir:

            flash("Las contraseñas no coinciden")

            return redirect(
                url_for("main.cambiar_password")
            )

        current_user.set_password(nueva)

        current_user.cambiar_password = False

        db.session.commit()

        flash("Contraseña actualizada")

        return redirect(
            url_for("main.home")
        )

    return render_template(
        "cambiar_password.html"
    )


@main_bp.route(
    "/admin/password/<int:id>",
    methods=["GET", "POST"]
)
@admin_required
def admin_password(id):

    usuario = User.query.get_or_404(id)

    if request.method == "POST":

        password = request.form["password"]

        usuario.set_password(password)

        usuario.cambiar_password = True

        db.session.commit()

        flash(
            "Contraseña actualizada"
        )

        return redirect(
            url_for("main.admin_panel")
        )

    return render_template(
        "admin_password.html",
        usuario=usuario
    )

@main_bp.route(
    "/admin/desactivar/<int:id>"
)
@admin_required
def desactivar_usuario(id):

    usuario = User.query.get_or_404(id)

    usuario.activo = False

    db.session.commit()

    return redirect(
        url_for("main.admin_panel")
    )

@main_bp.route(
    "/admin/activar/<int:id>"
)
@admin_required
def activar_usuario(id):

    usuario = User.query.get_or_404(id)

    usuario.activo = True

    db.session.commit()

    return redirect(
        url_for("main.admin_panel")
    )



