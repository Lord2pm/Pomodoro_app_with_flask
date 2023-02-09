from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from pygame import mixer
from time import sleep
import threading
from random import choice
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tarefas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIOS"] = False
db = SQLAlchemy(app)
mixer.init()

som1 = "static/music/1.mp3"
som2 = "static/music/2.mp3"
som3 = "static/music/3.mp3"
som4 = "static/music/4.mp3"
musicas = [som1, som2, som3, som4]


class Tarefa(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	titulo = db.Column(db.String(100))
	estado = db.Column(db.Boolean)
	data = db.Column(db.String)

	def __init__(self, titulo, data):
		self.titulo = titulo
		self.estado = False
		self.data = data

	def __repr__(self):
		return f"{self.titulo}"


@app.route('/')
def index():
	tarefas = Tarefa.query.all()
	
	return render_template("index.html", tarefas=tarefas)


@app.route("/add_tarefa", methods=["POST"])
def add_tarefa():
	titulo_tarefa = request.form.get("titulo_tarefa")
	data = datetime.now()
	data = f"{data.day} - {data.month} - {data.year}"
	tarefa = Tarefa(titulo_tarefa.capitalize(), data)
	db.session.add(tarefa)
	db.session.commit()

	return redirect(url_for("index"))


@app.route("/pesquisar", methods=["POST"])
def pesquisar():
	titulo_tarefa = request.form.get("titulo_tarefa")
	tarefas = Tarefa.query.filter(Tarefa.titulo.like(f"%{titulo_tarefa}%")).all()

	return render_template("index.html", tarefas=tarefas)


@app.route("/eliminar/<id_tarefa>")
def eliminar(id_tarefa):
	tarefa = Tarefa.query.filter_by(id=id_tarefa).first()
	db.session.delete(tarefa)
	db.session.commit()

	return redirect(url_for("index"))


@app.route("/editar/<id_tarefa>", methods=["GET", "POST"])
def editar(id_tarefa):
	if request.method == "POST":
		titulo_tarefa = request.form.get("titulo_tarefa")
		tarefa = Tarefa.query.filter_by(id=id_tarefa).first()
		tarefa.titulo = titulo_tarefa
		db.session.commit()
		return redirect(url_for("index"))
	else:
		tarefa = Tarefa.query.filter_by(id=id_tarefa).first()

		return render_template("editar.html", tarefa=tarefa)


@app.route("/tocar_som")
def tocar_som():
	mixer.music.load(choice(musicas))
	mixer.music.play()

	return redirect(url_for("index"))


@app.route("/comecar_tarefa/<id_tarefa>")
def comecar_tarefa(id_tarefa):
	tarefa = Tarefa.query.filter_by(id=id_tarefa).first()
	def timer():
		sleep(1800)
		mixer.music.load(som1)
		mixer.music.play()

	threading.Thread(target=timer).start()

	tarefa.estado = True
	db.session.commit()

	return redirect(url_for("index"))


if __name__ == '__main__':
	app.run(
		host="127.0.0.1",
		port=8000,
		debug=True
	)