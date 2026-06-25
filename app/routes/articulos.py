from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from sqlalchemy import or_

import pandas as pd

from .. import db
from ..models import Articulo


articulos_bp = Blueprint(
    "articulos",
    __name__,
    url_prefix="/articulos"
)


@articulos_bp.route("/")
@login_required
def lista():

    buscar = request.args.get("buscar", "").strip()

    marca = request.args.get("marca", "").strip()

    tipo = request.args.get("tipo", "").strip()

    epoca = request.args.get("epoca", "").strip()

    ubicacion = request.args.get("ubicacion", "").strip()

    estado = request.args.get("estado", "").strip()

    orden = request.args.get(
        "orden",
        "numero"
    )

    query = Articulo.query.filter_by(
        user_id=current_user.id
    )

    if buscar:

        query = query.filter(
            or_(
                Articulo.descripcion.ilike(f"%{buscar}%"),
                Articulo.referencia.ilike(f"%{buscar}%"),
                Articulo.marca.ilike(f"%{buscar}%"),
                Articulo.matricula.ilike(f"%{buscar}%"),
                Articulo.numero.cast(db.String).ilike(f"%{buscar}%")
            )
        )

    if marca:
        query = query.filter(
            Articulo.marca == marca
        )

    if tipo:
        query = query.filter(
            Articulo.tipo == tipo
        )

    if epoca:
        query = query.filter(
            Articulo.epoca == epoca
        )

    if ubicacion:
        query = query.filter(
            Articulo.ubicacion == ubicacion
        )

    if estado:
        query = query.filter(
            Articulo.estado == estado
        )

    if orden == "marca":

        query = query.order_by(
            Articulo.marca
        )

    elif orden == "referencia":

        query = query.order_by(
            Articulo.referencia
        )

    elif orden == "ubicacion":

        query = query.order_by(
            Articulo.ubicacion
        )

    elif orden == "tipo":

        query = query.order_by(
            Articulo.tipo
        )

    elif orden == "epoca":

        query = query.order_by(
            Articulo.epoca
        )

    else:

        query = query.order_by(
            Articulo.numero
        )

    articulos = query.all()

    todos = Articulo.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Articulo.numero
    ).all()

    marcas = []
    tipos = []
    epocas = []
    ubicaciones = []
    estados = []

    filtros_query = Articulo.query.filter_by(
        user_id=current_user.id
    )

    if buscar:
        filtros_query = filtros_query.filter(
            or_(
                Articulo.descripcion.ilike(f"%{buscar}%"),
                Articulo.referencia.ilike(f"%{buscar}%"),
                Articulo.marca.ilike(f"%{buscar}%"),
                Articulo.matricula.ilike(f"%{buscar}%"),
                Articulo.numero.cast(db.String).ilike(f"%{buscar}%")
            )
        )

    if marca:
        filtros_query = filtros_query.filter(
            Articulo.marca == marca
        )

    if tipo:
        filtros_query = filtros_query.filter(
            Articulo.tipo == tipo
        )

    if epoca:
        filtros_query = filtros_query.filter(
            Articulo.epoca == epoca
        )

    if ubicacion:
        filtros_query = filtros_query.filter(
            Articulo.ubicacion == ubicacion
        )

    if estado:
        filtros_query = filtros_query.filter(
            Articulo.estado == estado
        )

    marcas = filtros_query.with_entities(
        Articulo.marca,
        func.count(Articulo.id)
    ).filter(
        Articulo.marca.isnot(None)
    ).group_by(
        Articulo.marca
    ).order_by(
        Articulo.marca
    ).all()

    tipos = filtros_query.with_entities(
        Articulo.tipo,
        func.count(Articulo.id)
    ).filter(
        Articulo.tipo.isnot(None)
    ).group_by(
        Articulo.tipo
    ).order_by(
        Articulo.tipo
    ).all()

    epocas = filtros_query.with_entities(
        Articulo.epoca,
        func.count(Articulo.id)
    ).filter(
        Articulo.epoca.isnot(None)
    ).group_by(
        Articulo.epoca
    ).order_by(
        Articulo.epoca
    ).all()

    ubicaciones = filtros_query.with_entities(
        Articulo.ubicacion,
        func.count(Articulo.id)
    ).filter(
        Articulo.ubicacion.isnot(None)
    ).group_by(
        Articulo.ubicacion
    ).order_by(
        Articulo.ubicacion
    ).all()

    estados = filtros_query.with_entities(
        Articulo.estado,
        func.count(Articulo.id)
    ).filter(
        Articulo.estado.isnot(None)
    ).group_by(
        Articulo.estado
    ).order_by(
        Articulo.estado
    ).all()

    return render_template(
        "articulos/lista.html",
        articulos=articulos,
        buscar=buscar,
        marca=marca,
        tipo=tipo,
        epoca=epoca,
        ubicacion=ubicacion,
        estado=estado,
        marcas=marcas,
        tipos=tipos,
        epocas=epocas,
        ubicaciones=ubicaciones,
        estados=estados,
        orden=orden
    )

@articulos_bp.route("/importar", methods=["GET", "POST"])
@login_required
def importar():

    if request.method == "POST":

        archivo = request.files.get("archivo")

        if not archivo:
            flash("Seleccione un fichero")
            return redirect(url_for("articulos.importar"))

        df = pd.read_excel(archivo)

        creados = 0
        actualizados = 0

        for _, fila in df.iterrows():

            numero = fila.get("Número")

            articulo = Articulo.query.filter_by(
                user_id=current_user.id,
                numero=numero
            ).first()

            if articulo:

                actualizados += 1

            else:

                articulo = Articulo(
                    user_id=current_user.id,
                    numero=numero
                )

                db.session.add(articulo)

                creados += 1

            articulo.lista_orden = str(fila.get("LISTA ORDEN", ""))

            articulo.ubicacion = str(fila.get("Ubicación", ""))

            articulo.marca = str(fila.get("Marca", ""))

            articulo.referencia = str(fila.get("Referencia", ""))

            articulo.set_modelo = str(fila.get("Set", ""))

            articulo.descripcion = str(fila.get("Descripción", ""))

            articulo.matricula = str(fila.get("Matrícula", ""))

            articulo.matricula_ii = str(fila.get("Matrícula II", ""))

            articulo.epoca = str(fila.get("Epoca", ""))

            articulo.caja = str(fila.get("Caja", ""))

            articulo.unidades = fila.get("Unidades")

            articulo.tipo = str(fila.get("Tipo", ""))

            articulo.ejes = str(fila.get("Ejes", ""))

            articulo.rodaje = str(fila.get("Rodaje", ""))

            articulo.longitud = str(fila.get("Longitud", ""))

            articulo.administracion = str(fila.get("Administración", ""))

            articulo.librea = str(fila.get("Librea", ""))

            articulo.envejecido = str(fila.get("Envejecido", ""))

            articulo.clasificacion = str(fila.get("Clasificación", ""))

            articulo.mercancia = str(fila.get("Mercancía", ""))

            articulo.estado = str(fila.get("Estado", ""))

            articulo.necesidades = str(fila.get("Necesidades", ""))

            articulo.rodaje_detalle = str(fila.get("Rodaje.1", ""))

            imagen = fila.get("Imagen")

            if pd.isna(imagen):
                articulo.imagen = ""
            else:
                articulo.imagen = str(imagen).strip()

        db.session.commit()

        flash(
            f"Importación finalizada. "
            f"Creados: {creados} | "
            f"Actualizados: {actualizados}"
        )

        return redirect(url_for("articulos.lista"))

    return render_template(
        "articulos/importar.html"
    )


@articulos_bp.route("/<int:numero>")
@login_required
def detalle(numero):

    articulo = Articulo.query.filter_by(
        numero=numero,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "articulos/detalle.html",
        articulo=articulo
    )

@articulos_bp.route("/coleccion")
@login_required
def coleccion():

    articulos = Articulo.query.filter_by(
        user_id=current_user.id
    )

    total_articulos = articulos.count()

    total_marcas = db.session.query(
        Articulo.marca
    ).filter_by(
        user_id=current_user.id
    ).distinct().count()

    total_ubicaciones = db.session.query(
        Articulo.ubicacion
    ).filter_by(
        user_id=current_user.id
    ).distinct().count()

    ranking_marcas = db.session.query(
        Articulo.marca,
        func.count(Articulo.id)
    ).filter(
        Articulo.user_id == current_user.id
    ).group_by(
        Articulo.marca
    ).order_by(
        func.count(Articulo.id).desc()
    ).all()

    ranking_tipos = db.session.query(
        Articulo.tipo,
        func.count(Articulo.id)
    ).filter(
        Articulo.user_id == current_user.id
    ).group_by(
        Articulo.tipo
    ).order_by(
        func.count(Articulo.id).desc()
    ).all()

    ranking_ubicaciones = db.session.query(
        Articulo.ubicacion,
        func.count(Articulo.id)
    ).filter(
        Articulo.user_id == current_user.id
    ).group_by(
        Articulo.ubicacion
    ).order_by(
        func.count(Articulo.id).desc()
    ).all()

    locomotoras = Articulo.query.filter(
        Articulo.user_id == current_user.id,
        Articulo.tipo.ilike("%locomotora%")
    ).count()

    vagones = Articulo.query.filter(
        Articulo.user_id == current_user.id,
        Articulo.tipo.ilike("%vag%")
    ).count()

    coches = Articulo.query.filter(
        Articulo.user_id == current_user.id,
        Articulo.tipo.ilike("%coche%")
    ).count()

    ultimos = Articulo.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Articulo.numero.desc()
    ).limit(20).all()

    return render_template(
        "articulos/coleccion.html",
        total_articulos=total_articulos,
        total_marcas=total_marcas,
        total_ubicaciones=total_ubicaciones,
        locomotoras=locomotoras,
        vagones=vagones,
        coches=coches,
        ranking_marcas=ranking_marcas,
        ranking_tipos=ranking_tipos,
        ranking_ubicaciones=ranking_ubicaciones,
        ultimos=ultimos
    )
