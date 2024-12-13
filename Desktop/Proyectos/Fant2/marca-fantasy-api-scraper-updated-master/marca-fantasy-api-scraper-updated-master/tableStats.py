import os
import json
import locale
from datetime import datetime, timedelta

from flask import Flask, render_template



# Directorio principal donde se encuentran las carpetas de equipos
directorio_principal = "players"

import os
import json
from datetime import datetime, timedelta

# Funcions auxiliares

def reverseFormatMiles(cadena):
    print(float(cadena.replace(".", "").replace(",", ".")))
    return float(cadena.replace(".", "").replace(",", "."))

def reverseFormatDecimal(cadena):
    # Establecer la configuración regional para español
    locale.setlocale(locale.LC_ALL, 'es_ES.utf-8')

    # Reemplazar el punto decimal por la coma
    cadena_con_coma = cadena.replace(".", ",")

    # Intentar convertir la cadena formateada a un número
    try:
        numero = locale.atof(cadena_con_coma)
        return numero
    except ValueError:
        # En caso de error, devolver None o lanzar una excepción según sea necesario
        return None

def formatMiles(numero):
    return "{:,}".format(numero).replace(",", ".")

def formatDecimal(numero):
    # Establecer la configuración regional para español
    locale.setlocale(locale.LC_ALL, 'es_ES.utf-8')
    # Formatear el número como cadena con el formato local
    numero_formateado = locale.format_string("%.2f", numero)
    return numero_formateado

# Crear una lista para almacenar los datos de todos los jugadores
datos_jugadores = []
contID = 0

# Recorre las carpetas de equipos
for equipo in os.listdir(directorio_principal):
    equipo_path = os.path.join(directorio_principal, equipo)

    # Verifica si el elemento en el directorio principal es una carpeta
    if os.path.isdir(equipo_path):
        # Recorre los archivos JSON en la carpeta del equipo
        for jugador_file in os.listdir(equipo_path):
            if jugador_file.endswith(".json"):
                jugador_path = os.path.join(equipo_path, jugador_file)

                # Analiza el archivo JSON del jugador
                with open(jugador_path, 'r', encoding='utf-8') as file:  # Especifica la codificación UTF-8
                    jugador_data = json.load(file)
                    # Verifica si el jugador tiene datos de la primera semana y al menos 10 estadísticas
                    if "playerStats" in jugador_data:
                        if jugador_data["playerStats"]:
                            stats = jugador_data["playerStats"][0]["stats"]
                        if len(stats) != 4:
                            # Obtén la fecha actual
                            fecha_actual = datetime.now()
                            fecha_ayer = fecha_actual - timedelta(days=1)

                            # Formatea la fecha como "dd/mm/aaaa" y comprueba que esté disponible
                            fecha_formateada = fecha_actual.strftime("%d/%m/%Y")
                            if fecha_formateada in jugador_data["marketValue"]:
                                fecha_formateada_ayer = fecha_ayer.strftime("%d/%m/%Y")
                            else:
                                fecha_actual = fecha_actual - timedelta(days=1)
                                fecha_ayer = fecha_actual - timedelta(days=1)
                                fecha_formateada = fecha_actual.strftime("%d/%m/%Y")
                                fecha_formateada_ayer = fecha_ayer.strftime("%d/%m/%Y")

                            if fecha_formateada_ayer in jugador_data["marketValue"] and fecha_formateada in jugador_data["marketValue"]:
                                variacionPrecio = int(jugador_data["marketValue"][fecha_formateada]) - int(jugador_data["marketValue"][fecha_formateada_ayer])
                                #calculo prop subida/valor con última subida
                                propSubida = round(variacionPrecio / int(jugador_data["marketValue"][fecha_formateada]) * 100, 2)

                            if "images" in jugador_data:
                                imagen = jugador_data["images"]["transparent"]["256x256"]
                            else:
                                imagen = "https://assets-fantasy.llt-services.com/players/no-player-sq.png"
                                                        
                            # Crea un diccionario para almacenar los datos de puntos
                            pointsData = {}

                            # Recorre las entradas de jugador_data y extrae los números de jornada y puntos totales
                            for entry in jugador_data["playerStats"]:
                                week_number = entry["weekNumber"]
                                total_points = entry["totalPoints"]
                                pointsData[week_number] = total_points

                            # Llena con valor 0 para las claves faltantes del 1 al 38
                            for i in range(1, 39):
                                week_number = i
                                if week_number not in pointsData:
                                    pointsData[week_number] = 0

                            # Convierte el diccionario marketValueData en una cadena JSON
                            pointsDataJSON = json.dumps(pointsData, indent=4)

                            valueDataJSON = json.dumps(jugador_data["marketValue"], indent=4)

                            # Imprime el JSON resultante
                            #print(pointsDataJSON)

                            #sumamos 1 al id para hacerlo único
                            contID = contID + 1
                            # Extrae los datos relevantes del jugador
                            jugador = {
                                "nombre": jugador_data["nickname"],
                                "equipo": jugador_data["team"]["badgeColor"],
                                "valor": jugador_data["marketValue"][fecha_formateada],
                                "subida": variacionPrecio,
                                "propSubida": propSubida,
                                "points": jugador_data["points"],
                                "weekPoints": jugador_data.get("weekPoints", 0),
                                "averagePoints": round(float(jugador_data["averagePoints"]), 2),
                                "imagen": imagen,
                                "position": jugador_data["position"],
                                "estado": jugador_data["playerStatus"],
                                "registroPuntos": pointsDataJSON,
                                "registroValor": valueDataJSON,
                                "subidaFormateado": formatMiles(variacionPrecio),
                                "valorFormateado": formatMiles(jugador_data["marketValue"][fecha_formateada]),
                                "propSubidaFormateado": formatDecimal(propSubida),
                                "id": contID,
                            }

                            # Agrega los datos del jugador a la lista
                            datos_jugadores.append({"jugador": jugador})

# Convierte los datos a JSON
datos_jugadores_json = json.dumps(datos_jugadores, ensure_ascii=False, indent=4)

# Guarda el JSON en un archivo
with open('datos_jugadores.json', 'w', encoding='utf-8') as json_file:
    json_file.write(datos_jugadores_json)





# Crear una tabla HTML
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Resto de tus etiquetas head y estilos CSS -->
        <link rel="stylesheet" href="{{ url_for('static', filename='estilo.css') }}">
</head>

<input type="text" id="searchInput" placeholder=" &#x1F50D">
<div class="search-results" id="searchResults" style="position: absolute; color:white"></div>

<!-- Resto de tu código HTML -->

<script>
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    var enfocar = false;

    const jugadores = {{ jugadores | tojson | safe }};

    // Restricción: Permitir solo letras y espacios
    searchInput.addEventListener('input', function () {
        const searchText = this.value.toLowerCase();
        enfocar = true
        const filteredPlayers = jugadores.filter(player => player.jugador.nombre.toLowerCase().startsWith(searchText));
        renderSearchResults(filteredPlayers);
    });

    searchInput.addEventListener('blur', function () {
        // Borra el contenido del campo de búsqueda cuando pierde el enfoque
        if(enfocar == false){
            this.value = '';
            searchResults.style.display = 'none'; // Oculta la lista de resultados
            searchResults.innerHTML = ''; // Borra el contenido de la lista
        }
        else{
            
            enfocar = false;
        }
    });

    // Cuando el mouse entra en los resultados
    searchResults.addEventListener('mouseover', function () {
        // Dar el enfoque al campo de búsqueda
        searchInput.focus();
        enfocar = true;
        
    });

function renderSearchResults(results) {
    if (results.length === 0 || searchInput.value === '') {
        searchResults.style.display = 'none';
        searchResults.innerHTML = '';
        enfocar = false;
        return;
    }

    const resultList = document.createElement('ul');
    resultList.style.marginLeft = '25%';
    resultList.style.marginTop = '3%';
    results.forEach(player => {
        const listItem = document.createElement('li');
        listItem.style.width = '160px';
        listItem.style.cursor = 'pointer';

        // Agrega un enlace al jugador
        const playerLink = document.createElement('a');
        playerLink.href = `/${player.jugador.nombre}`; // Usa el nombre del jugador para construir la URL
        playerLink.textContent = player.jugador.nombre;
        playerLink.style.marginLeft = '5%';

        // Agrega un evento de clic al elemento <li> para redirigir al usuario
        listItem.addEventListener('click', function () {
            window.location.href = playerLink.href;
        });

        listItem.appendChild(playerLink);
        resultList.appendChild(listItem);
    });

    searchResults.innerHTML = '';
    searchResults.appendChild(resultList);
    searchResults.style.display = 'block';
}

</script>


<!-- Resto de tu código HTML -->

<script>
 var table;
var columnSortDirections = Array(7).fill("asc");
var currentPage = 1;
var rowsPerPage = 10;
var contVerMas = 0;

function initTable() {
    table = document.getElementById("jugadoresTable");
    updateTable();
}

function updateTable() {
    // Oculta todas las filas
    var rows = Array.from(table.tBodies[0].rows).slice(1);
    rows.forEach(row => {
        row.style.display = 'none';
    });

    // Calcula el índice de inicio y fin para las filas en la página actual
    var startIndex = 0;
    var endIndex = startIndex + rowsPerPage;

    // Muestra solo las filas de la página actual
    var visibleRows = rows.slice(startIndex, endIndex);
    visibleRows.forEach(row => {
        row.style.display = '';
    });

    // Muestra u oculta el botón "Ver más" según si hay más filas
    var moreButton = document.getElementById('verMasButton');
    if (endIndex < rows.length) {
        moreButton.style.display = '';
    } else {
        moreButton.style.display = 'none';
    }
}

function verMas() {
    rowsPerPage = rowsPerPage+10; // Incrementa la página actual
    updateTable(); // Actualiza la tabla con las nuevas filas visibles
}

function reverseFormatDecimal(cadena) {
  // Reemplazar la coma por el punto decimal
  var cadena_con_punto = cadena.replace(",", ".");

  // Intentar convertir la cadena formateada a un número
  var numero = parseFloat(cadena_con_punto);

  // Verificar si la conversión fue exitosa
  if (!isNaN(numero)) {
    return numero;
  } else {
    // En caso de error, devolver NaN o lanzar una excepción según sea necesario
    return null;
  }
}

function reverseFormatMiles(cadena) {
  // Eliminar los puntos y reemplazar la coma por el punto decimal
  var cadena_sin_puntos = cadena.replace(/\./g, "");

  // Intentar convertir la cadena formateada a un número
  var numero = parseInt(cadena_sin_puntos);

  return numero;
}

// ... (Tu código existente)



    function sortTable(columnIndex) {
    var dir = columnSortDirections[columnIndex];
    
    var compareFunction;
    if (columnIndex < 2) {
        // Columnas 0 y 1 (Nombres y Equipos): Ordenación alfabética
        compareFunction = function (a, b) {
            var aValue = a.cells[columnIndex].textContent.toLowerCase();
            var bValue = b.cells[columnIndex].textContent.toLowerCase();
            return dir === "desc" ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        };
    } else {
        // Otras columnas: Ordenación numérica
if (columnIndex === 2 || columnIndex === 3) {
    compareFunction = function (a, b) {
        // Elimina caracteres no numéricos al principio de la cadena
        var regex = /[\€,]/;
        var aValue = reverseFormatMiles(a.cells[columnIndex].textContent.replace(regex, ""));
        var bValue = reverseFormatMiles(b.cells[columnIndex].textContent.replace(regex, ""));
        return dir === "asc" ? aValue - bValue : bValue - aValue;
    };
}
        if(columnIndex === 4){
                compareFunction = function (a, b) {
                    var aValue = parseFloat(a.cells[columnIndex].textContent.replace(/[^0-9.-]+/g,""));
                    var bValue = parseFloat(b.cells[columnIndex].textContent.replace(/[^0-9.-]+/g,""));
                    return dir === "asc" ? aValue - bValue : bValue - aValue;
            };
        }

        compareFunction = function (a, b) {
            var aValue = parseFloat(a.cells[columnIndex].textContent.replace(/[^0-9.-]+/g,""));
            var bValue = parseFloat(b.cells[columnIndex].textContent.replace(/[^0-9.-]+/g,""));
            return dir === "asc" ? aValue - bValue : bValue - aValue;
        };
    }

    var rows = Array.from(table.rows).slice(1);
    rows.sort(compareFunction);

    for (var i = 0; i < rows.length; i++) {
        table.tBodies[0].appendChild(rows[i]);
    }

    // Cambia las flechas de ordenamiento en las columnas
    var headers = table.getElementsByTagName("th");
    for (var i = 0; i < headers.length; i++) {
        var span = headers[i].getElementsByTagName("span")[0];
        if (span) {
            span.innerHTML = "";
        }
    }
    var currentHeader = headers[columnIndex];
    var span = currentHeader.getElementsByTagName("span")[0];
    if (!span) {
        span = document.createElement("span");
        currentHeader.appendChild(span);
    }
    span.innerHTML = dir === "asc" ? "&#8595;" : "&#8593;";

    // Cambia la dirección de orden actual
    columnSortDirections[columnIndex] = dir === "asc" ? "desc" : "asc";
    currentPage = 1;
    rowsPerPage = 10;
    contVerMas = 0;
    updateTable()
}

</script>
<title>Tabla de Jugadores</title>
</head>
<body onload="initTable()">

"""

html += f"""
<h2 style="color: white; font-size: x-large; padding: 1%; margin-left: 38%;">Tabla Jugadores a día: {fecha_formateada}</h2>
<table id="jugadoresTable" border="1">
    <tr>
        <th onclick="sortTable(0)" class="active">Nombre<span></span></th>
        <th onclick="sortTable(1)" class="active">Equipo<span></span></th>
        <th onclick="sortTable(2)" class="active">Valor mercado<span></span></th>
        <th onclick="sortTable(3)" class="active">Subida mercado<span></span></th>
        <th onclick="sortTable(4)" class="active">Prop Subida<span></span></th>
        <th onclick="sortTable(5)" class="active">Puntos totales<span></span></th>
        <th onclick="sortTable(6)" class="active">Puntos previos<span></span></th>
        <th onclick="sortTable(7)" class="active">Media puntos<span></span></th>
    </tr>
    <!-- Filas de datos aquí -->

"""
# Agrega filas para cada jugador

for jugador in datos_jugadores:
    jugador_data = jugador.get("jugador", {})  # Obtiene los datos del jugador del JSON

    # Verifica si hay datos del jugador
    if jugador_data:
        html += f"<tr onclick=\"window.location.href='/{jugador_data.get('nombre', '')}'\" style='cursor: pointer;'>"
        for clave, valor in jugador_data.items():
            if isinstance(valor, str):
                if clave == "nombre":  # Comprueba si es el nombre del jugador
                    # Agrega un enlace al detalle del jugador usando el nombre
                    html += f"<td><a href='/{valor}'>{valor}</a></td>"
                elif clave == "equipo":
                    html += f"<td><img src={valor} style='width:55px;'></td>"
            else:
                if clave == "valor":  # Comprueba si es el nombre del jugador
                    html += f"<td>{formatMiles(valor)} €</td>"
                if clave == "subida":  # Comprueba si es el nombre del jugador
                    html += f"<td>{valor} €</td>"
                if clave == "propSubida":  # Comprueba si es el nombre del jugador
                    html += f"<td>{formatDecimal(valor)} %</td>"
                if clave == "points":  # Comprueba si es el nombre del jugador
                    html += f"<td>{valor}</td>"
                if clave == "weekPoints":  # Comprueba si es el nombre del jugador
                    html += f"<td>{valor}</td>"
                if clave == "averagePoints":  # Comprueba si es el nombre del jugador
                    html += f"<td>{formatDecimal(valor)}</td>"    
                
        html += "</tr>"

html += "</table>"
html += "<button id='verMasButton' onclick='verMas()' style='display: none; margin-left: 44%'>Ver más</button>"


# Cargar la plantilla HTML desde el archivo
with open("plantilla.html", "r") as plantilla_file:
    plantilla_html = plantilla_file.read()


# Insertar el contenido específico en la zona de contenido de la plantilla
plantilla_html = plantilla_html.replace("<!-- Contenido especifico de cada pagina ira aqui -->", html)

# Guardar el HTML resultante en un archivo o usarlo como desees
with open("bigdata.html", "w", encoding='utf-8') as pagina_file:
    pagina_file.write(plantilla_html)

print("Página de inicio generada con éxito.")

# Guarda la tabla HTML en un archivo
with open("tabla_jugadores.html", "w", encoding='utf-8') as file:  # Especifica la codificación UTF-8
    file.write(html)

print("Tabla de jugadores generada con éxito.")

# Obtiene la ruta completa del directorio actual
current_directory = os.path.abspath(os.path.dirname(__file__))

# Crea una instancia de la aplicación Flask y configura la ruta de las plantillas
app = Flask(__name__, template_folder=current_directory, static_url_path="/css")


@app.route('/<string:player_name>')
def player_detail(player_name):
    selected_player = None

    # Busca al jugador en datos_jugadores por su nombre
    for jugador in datos_jugadores:
        if jugador.get("jugador", {}).get("nombre") == player_name:
            selected_player = jugador
            break

    if selected_player:
        # Renderiza la plantilla con los datos del jugador seleccionado
        rp =selected_player.get("jugador", {}).get("registroPuntos")
        rv =selected_player.get("jugador", {}).get("registroValor")

        return render_template('plantillaJugador.html', player=selected_player, registroPuntos = rp, registroValor = rv)
    else:
        # Maneja el caso en el que no se encuentra el jugador
        return None

@app.route('/bigdata.html')
def bigdata():
    return render_template('bigdata.html', jugadores=datos_jugadores)

@app.route('/inicio.html')
def inicio():
    # Tu lógica para la página de inicio.html
    return render_template('inicio.html')

@app.route('/miequipo.html')
def miequipo():
    # Tu lógica para la página de inicio.html
    return render_template('miequipo.html', jugadores=datos_jugadores_json)

@app.route('/predictor.html')
def predictor():
    # Tu lógica para la página de inicio.html
    return render_template('predictor.html')


if __name__ == '__main__':
    app.run(debug=True)
