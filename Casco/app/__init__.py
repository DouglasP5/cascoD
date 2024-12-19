from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SECRET_KEY'] = 'sua-chave-secreta'

    db.init_app(app)

    from .routes.auth_routes import auth
    from .routes.dashboard_routes import dashboard
    from .routes.equipe_routes import equipe
    from .routes.tartaruga_routes import tartaruga
    
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(equipe)
    app.register_blueprint(tartaruga)

    with app.app_context():
        db.create_all()

    return app
