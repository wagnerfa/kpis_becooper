# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)


    app.config.from_object('app.config')


    # Inicializa o SQLAlchemy
    db.init_app(app)

    # Registra o blueprint
    from .routes import bp
    app.register_blueprint(bp)

    return app
