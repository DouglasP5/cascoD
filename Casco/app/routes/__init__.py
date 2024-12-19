from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/casco'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    
    db.init_app(app)
    Session(app)

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
