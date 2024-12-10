import os
import json

from flask import Flask, send_file
import plotly.express as px
import pandas as pd

app = Flask(__name__)

@app.route("/")
def index():
    return send_file('src/index.html')



@app.route("/cargarfuentedatos")
def cargaFuenteDatos():
    import csv  # Usaremos el módulo csv para manejar el archivo correctamente
    
    with open("solarEnergyConsumptio.csv", "r") as archivo:
        reader = csv.reader(archivo)
        miTabla = "<table id='t_wind' class='table table-hover'>"  # Abrimos la tabla
        miTabla += "<thead>"     
        miTabla += "  <tr>"
        miTabla += "       <th>Pais</th>"
        miTabla += "       <th>Codigo</th>"
        miTabla += "       <th>Año</th>"
        miTabla += "       <th>Ahorro</th>"
        miTabla += "  </tr>"
        miTabla += "</thead>"
        miTabla += "<tbody>"

        paises = set()  # Usamos un set para evitar duplicados
        for i, elemento in enumerate(reader):  # Leemos línea por línea
            if i == 0:  # Salta la cabecera del CSV si existe
                continue
            paises.add(elemento[0])  # Agregamos el país al set
            miTabla += "<tr>"
            miTabla += f"<td>{elemento[0]}</td>"
            miTabla += f"<td>{elemento[1]}</td>"
            miTabla += f"<td>{elemento[2]}</td>"
            miTabla += f"<td>{elemento[3]}</td>"
            miTabla += "</tr>"

        miTabla += "</tbody></table>"

        # Creamos el select para los países
        select_paises = "<select id='sl_paises' class='form-control'>"
        for pais in sorted(paises):  # Ordenamos los países alfabéticamente
            select_paises += f"<option value='{pais}'>{pais}</option>"
        select_paises += "</select>"

        # Creamos el select para el gráfico
        select_grafico = "<select id='sl_grafico' class='form-control'>"
        select_grafico += "<option value='Lines'>Línea</option>"
        select_grafico += "<option value='Torta'>Torta</option>"
        select_grafico += "<option value='Barras'>Barras</option>"
        select_grafico += "<option value='Area'>Área</option>"
        select_grafico += "</select>"

        # Construimos el contenedor con los select y botón
        todo = "<div class='row'>"
        todo += f"<div class='col-md-7'>{select_paises}</div>"
        todo += f"<div class='col-md-3'>{select_grafico}</div>"
        todo += "<div class='col-md-2'><button onclick='mostrarGrafico()' class='btn btn-success'>Graficar</button></div>"
        todo += "</div>"

        return todo + "<hr>" + miTabla

@app.route("/grafico")
def graficos():
    #grafico barras
    df = pd.DataFrame({'Tipo de fuente de energía': ["Hidraulica", "Eolica", "Fotoboltaica", "Geotermica", "Bioenergia"],'Valor porcentual':[42.4,28.4,20.77,7.1,1.3]})
    
    # creamos el grafico interativo con plotly
    fig = px.bar(df,x='Tipo de fuente de energía',y='Valor porcentual', title='Producción de energía renovable por fuente en el año 2020')
    graph_html = fig.to_html(full_html=False)

    return graph_html

@app.route('/graficar/<pais>/<grafico>')
def graficar(pais, grafico):
        df = pd.read_csv("solarEnergyConsumptio.csv", header=None)     # Cargar el archivo en un DataFrame
        df.columns = ["País", "Código", "Año", "Ahorro"]  # Asegurar nombres de columnas

        # Filtrar los datos por el país proporcionado
        df_filtrado = df[df["País"] == pais]

        if df_filtrado.empty:
            return f"<h3>No hay datos disponibles para el país: {pais}</h3>"

        # Crear el gráfico según el tipo seleccionado
        if grafico == "Linea":
            fig = px.line(df_filtrado,
                          x="Año",
                          y="Ahorro",
                          title=f"Ahorro de energía en {pais} (Línea)",
                          markers=True)
        elif grafico == "Torta":
            # Para un gráfico de torta, usamos un único valor por categoría, ejemplo: total por año
            df_agg = df_filtrado.groupby("Año").sum().reset_index()
            fig = px.pie(df_agg,
                         names="Año",
                         values="Ahorro",
                         title=f"Ahorro de energía en {pais} (Torta)")
        elif grafico == "Barras":
            fig = px.bar(df_filtrado,
                         x="Año",
                         y="Ahorro",
                         title=f"Ahorro de energía en {pais} (Barras)",
                         text_auto=True)
        elif grafico == "Area":
            fig = px.area(df_filtrado,
                          x="Año",
                          y="Ahorro",
                          title=f"Ahorro de energía en {pais} (Área)")
        else:
            return f"<h3>Tipo de gráfico '{grafico}' no reconocido.</h3>"
        # Convertir el gráfico a HTML
        graph_html = fig.to_html(full_html=False)
        return graph_html

def main():
    app.run(port=int(os.environ.get('PORT', 80)))

if __name__ == "__main__":
    main()
