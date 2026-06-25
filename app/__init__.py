from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev-key"
    app.config["UPLOAD_FOLDER"] = "app/uploads"

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    from .models import User
    from .models import Articulo
    from .models import MaestroArticulo

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth_bp
    from .main_routes import main_bp
    from .routes.articulos import articulos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(articulos_bp)

    with app.app_context():

        db.create_all()

        admin = User.query.filter_by(
            username="admin"
        ).first()

        if not admin:

            admin = User(
                username="admin",
                email="admin@admin.com",
                role="admin"
            )

            admin.set_password("admin123")

            db.session.add(admin)
            db.session.commit()

    return app
