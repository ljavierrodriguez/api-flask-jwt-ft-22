# Proyecto con FLASK y PostgreSQL

1. Crear carpeta y abrirla con vscode

2. Crear archivo Pipfile

3. Crear y activar entorno virtual para trabajar, desde el terminal ejecutar

```shell
pipenv shell
```
4. Instalar los siguientes modulos:

```shell
pipenv install flask flask-migrate flask-sqlalchemy flask-cors python-dotenv psycopg2-binary
```

5. Crear el archivo ***.env*** en la carpeta principal y agregar los siguiente

```env
DATABASEURI="postgresql+psycopg2://postgres:postgres@localhost:5432/nombre-de-tu-base-de-datos"
```

6. Crear la carpeta ***src/*** y dentro crear dos archivos uno llamado ***app.py*** y un archivo llamado ***models.py***

7. En el archivo ***models.py*** agregar las siguientes lineas de codigo:

```python
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
```

8. En el archivo ***app.py*** agregar las siguientes importaciones

```python
import os
import datetime
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
```

9. Cargar las variables de entorno del archivo ***.env***

```python

load_dotenv() # cargar las variables de entorno

```

10. Instanciar una variable de Flask

```python
app = Flask(__name__)
```

11. Configurar parametros de opciones de flask

```python

app.config['DEBUG'] = True # Permite ver los errores
app.config['ENV'] = 'development' # Activa el servidor en modo desarrollo
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASEURI') # Leemos la url de conexion a la base de datos

```

12. Vincular el archivo ***models.py*** a nuestro archivo ***app.py***

```python
db.init_app(app)
```

13. Habilitar los comandos para crear las migraciones

```python
Migrate(app, db) # db init, db migrate, db upgrade, db downgrade
```

14. Crear modelo de ejemplo en el archivo ***models.py***:

```python 

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

```

15. Habilitar el comando flask en el terminal (flask):

windows
```shell
SET FLASK_APP=src/app.py
```

Linux o Mac
```shell
export FLASK_APP=src/app.py
```

16. Ejecutar los comandos de las migraciones

Crear la carpeta migrations esto es solo la primera vez 
```shell
flask db init
```

Crear las migraciones
```shell
flask db migrate
```

Generar las migraciones en la base de datos
```shell
flask db upgrade
```

17. Crear endpoint principal

```python
@app.route('/')
def main():
    return jsonify({ "status": "Server Up"}), 200
```

18. Validamos nuestra aplicacion

```python
if __name__ == '__main__':
    app.run()
```

19. Iniciar nuestra app desde el terminal ("python3" si estoy en maco o linux, "python" si estoy en windows) 

```shell
python src/app.py
```

20. Abrir un nuevo terminal y instalar el siguiente modulo:

```shell
pipenv install flask-jwt-extended
```

21. Agregar al archivo ***.env*** la siguiente linea

```env
SECRET_KEY="455a0595071af6e2385c0ec556cb329c"
```
* Nota: cambiar por tu propio "secret-key"

22. Agregar las siguientes importaciones en nuestro archivo ***app.py***

```python
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
```

23. Agregar la opcion de configuracion de JWT

```python
# Configuracion de JWT
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
```

24. Crear una instancia de JWT

```python
jwt = JWTManager(app)
```

25. Crear los siguientes endpoints: login, register, private

```python
@app.route('/login', methods=['POST'])
def login():
    pass

@app.route('/register', methods=['POST'])
def register():
    pass

@app.route('/private', methods=['GET'])
def private():
    pass
```

26. Modificar el endpoint register con la siguiente informacion:

Para encriptar el password agregar la siguiente importacion
```python
from werkzeug.security import generate_password_hash, check_password_hash
```

Para registrar el usuario:

```python
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
```

27. Modificar el endpoint login con el siguiente codigo:

```python 
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
    access_token =  create_access_token(identity=userFound.id, expire_delta=expires)

    # creamos un diccionario para devolver el token y la informacion del usuario
    data = {
        "access_token": access_token,
        "user": userFound.serialize()
    }

    return jsonify(data), 200

```

28. Modificar el endpoint private para que funcione como una ruta privada y solo los usuarios validos puedan consultar:

```python 
@app.route('/private', methods=['GET'])
@jwt_required() # convierte el endpoint en una ruta privada
def private():

    # Saber quien es el usuario podemos hacerlo de la siguiente manera
    id = get_jwt_identity() # devuelve el valor unico del usuario
    user = User.query.get(id)

    return jsonify({ "success": { "user": user.serialize() }}), 200

```

Notas:

Si quieres saber mas sobre JWT pueden revisar la siguiente pagina
["JWT"](https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage.html)