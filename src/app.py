import os
import datetime
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, User
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

app.config['DEBUG'] = True # Permite ver los errores
app.config['ENV'] = 'development' # Activa el servidor en modo desarrollo
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASEURI') # Leemos la url de conexion a la base de datos

# Configuracion de JWT
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)
Migrate(app, db) # db init, db migrate, db upgrade, db downgrade
jwt = JWTManager(app)

@app.route('/')
def main():
    return jsonify({ "status": "Server Up"}), 200

@app.route('/login', methods=['POST'])
def login():

    username = request.json.get("username")
    password = request.json.get("password")

    if not username:
        return jsonify({ "msg": "username es obligatorio!"}), 400

    if not password:
        return jsonify({ "msg": "password es obligatorio!"}), 400

    userFound = User.query.filter_by(username=username).first() # [<User 1>] => <User 1>

    if not userFound:
        return jsonify({ "msg": "username/password son incorrectos!"}), 401

    if not check_password_hash(userFound.password, password):
        return jsonify({ "msg": "username/password son incorrectos!"}), 401

    # crear fecha de vencimiento del token
    expires = datetime.timedelta(days=3)
    # crear el token (jwt)
    access_token =  create_access_token(identity=userFound.id, expires_delta=expires)

    # creamos un diccionario para devolver el token y la informacion del usuario
    data = {
        "access_token": access_token,
        "user": userFound.serialize()
    }

    return jsonify(data), 200

@app.route('/register', methods=['POST'])
def register():

    username = request.json.get("username")
    password = request.json.get("password")

    if not username:
        return jsonify({ "msg": "username es obligatorio!"}), 400

    if not password:
        return jsonify({ "msg": "password es obligatorio!"}), 400

    userFound = User.query.filter_by(username=username).first()

    if userFound:
        return jsonify({ "msg": "el username ya esta siendo usado!"}), 400

    user = User()
    user.username = username
    user.password = generate_password_hash(password) # se encripta el password

    db.session.add(user)
    db.session.commit()

    return jsonify({ "success": "Registro con exito, por favor iniciar sesion!"}), 200

@app.route('/private', methods=['GET'])
@jwt_required() # convierte el endpoint en una ruta privada
def private():

    # Saber quien es el usuario podemos hacerlo de la siguiente manera
    id = get_jwt_identity() # devuelve el valor unico del usuario
    user = User.query.get(id)

    return jsonify({ "success": { "user": user.serialize() }}), 200

if __name__ == '__main__':
    app.run()
