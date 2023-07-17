# Tomando Esta app modificar y lo entregado en del CRUD de Tareas, realizar :

# 1 - Crear o modifcar las rutas del CRUD de Tares para Guadar o ver los datos desde una BD
# 2 - Hacer que en el index pida el usuario y contraseña para poder ingresar y ver las tareas
# 3 - Cuando se crea, elimina, modifica o consulta una Tarea deben ser del usuario actualmente logueado

# NOTA: usar el usuario admin, con la clave admin, para crear usuario, solo él puede ver el crud de usuarios.

from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

app = Flask(__name__)
app.secret_key = 'mysecretkey'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(app)

# Definición de modelos
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)



# Ruta de inicio de sesión
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["logged_in"] = True
        return redirect("/tareas")
    return render_template("login.html")

# Ruta principal (tareas)
@app.route("/tareas")
def main():
    # Verificar si el usuario está logueado
    if not session.get("logged_in"):
        return redirect("/")
    
    # Obtener el usuario actualmente logueado y sus tareas asociadas
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    tasks = user.tasks
    
    return render_template("index.html", tasks=tasks)

# Ruta para crear una nueva tarea
@app.route("/create", methods=["GET", "POST"])
def create():
    # Verificar si el usuario está logueado
    if not session.get("logged_in"):
        return redirect("/")
    
    # Obtener el usuario actualmente logueado
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        
        # Crear la nueva tarea asociada al usuario
        task_id = str(uuid4())  # Generar un nuevo ID único para la tarea
        task = Task(id=task_id, title=title, description=description, user_id=user.id)
        db.session.add(task)
        db.session.commit()
        
        return redirect("/tareas")
    else:
        return render_template("create.html")

# Ruta para editar una tarea existente
@app.route("/edit/<string:task_id>", methods=["GET", "POST"])
def edit(task_id):
    # Verificar si el usuario está logueado
    if not session.get("logged_in"):
        return redirect("/")
    
    # Obtener el usuario actualmente logueado
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    
    # Obtener la tarea a editar solo si pertenece al usuario actual
    task = Task.query.filter_by(id=task_id, user_id=user.id).first()
    if not task:
        return "Tarea no encontrada"
    
    if request.method == "POST":
        task.title = request.form["title"]
        task.description = request.form["description"]
        db.session.commit()
        return redirect("/tareas")
    else:
        return render_template("edit.html", task=task)

# Ruta para eliminar una tarea
@app.route("/delete/<string:task_id>")
def delete(task_id):
    # Verificar si el usuario está logueado
    if not session.get("logged_in"):
        return redirect("/")
    
    # Obtener el usuario actualmente logueado
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    
    # Obtener la tarea a eliminar solo si pertenece al usuario actual
    task = Task.query.filter_by(id=task_id, user_id=user.id).first()
    if not task:
        return "Tarea no encontrada"

    db.session.delete(task)
    db.session.commit()
    return redirect("/tareas")

if __name__ == "__main__":
    app.run(debug=True)



