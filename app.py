from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

# Connection credentials
db_user = 'root'
db_pass = ''
db_name = 'test01'
db_url = 'localhost:3306'

# configuring our database uri
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{username}:{password}@{url}/{dbname}".format(
    username=db_user, password=db_pass, url=db_url, dbname=db_name)

db = SQLAlchemy(app)


class Pais(db.Model):
    __tablename__ = 'pais'
    codigoPais = db.Column(db.BigInteger(), primary_key=True)
    nombrePais = db.Column(db.String(50))
    capitalPais = db.Column(db.String(50))
    _codigoPais = 1

    def __init__(self):
        self.codigoPais = Pais._codigoPais
        Pais._codigoPais += 1


@app.route("/")
def home():
    return "Hello, Flask!"


@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name=None):
    return render_template(
        "hola.html",
        name=name,
        date=datetime.now()
    )


@app.route("/numbers")
def mostrarNumeros():
    return render_template(
        "numeros.html",
        valores=range(1, 10)
    )


@app.route("/paises")
def mostrarPaises():
    return render_template(
        "paises.html",
        paises=Pais.query.all()
    )

@app.route("/cargarPaises")
def cargarPaises():
    url = "http://restcountries.eu/rest/v2/callingcode/{code}"
    paises = []
    for i in range(30):
        try:
            resp = requests.get(url = url.format(code = i))
            if not resp.ok:
                raise Exception("No hay paises para codigo '{code}'".format(code = i))
            data = resp.json()
            if type(data) is list and len(data) > 0:
                for country in data:
                    pais = Pais()
                    pais.nombrePais = country['name']
                    pais.capitalPais = country['capital']
                    p = Pais.query.filter_by(nombrePais=pais.nombrePais).first()
                    if p is not None:
                        p.nombrePais = pais.nombrePais
                        p.capitalPais = pais.capitalPais
                        db.session.commit()
                    else:
                        db.session.add(pais)
                        db.session.commit()
                    paises.append(pais.nombrePais)
        except Exception as e:
            print(e)
    return render_template(
        "listado.html",
        paises = paises
    )
        