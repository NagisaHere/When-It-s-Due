from flask import Flask

def create_app() -> Flask:
    from app.http.users import bp as user_bp
    blueprints = [user_bp]

    app = Flask(__name__)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app
