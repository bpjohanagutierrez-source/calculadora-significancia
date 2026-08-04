<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora de Significancia Estadística (80% / 90%)</title>
    <style>
        :root {
            --primary: #1e3a8a;
            --primary-hover: #1e40af;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #0f172a;
            --border-color: #cbd5e1;
            --accent-80: #2563eb;
            --accent-90: #dc2626;
        }

        * {
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 24px;
            display: flex;
            justify-content: center;
        }

        .container {
            max-width: 1000px;
            width: 100%;
            background: var(--card-bg);
            padding: 32px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        h1 {
            color: var(--primary);
            margin-top: 0;
            font-size: 1.75rem;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 12px;
        }

        .instructions {
            background-color: #eff6ff;
            border-left: 4px solid var(--accent-80);
            padding: 12px 16px;
            margin-bottom: 24px;
            border-radius: 0 8px 8px 0;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #334155;
        }

        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 0.95rem;
            font-family: monospace;
            background-color: #f1f5f9;
        }

        textarea {
            height: 180px;
            resize: vertical;
        }

        input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: var(--primary);
            background-color: #fff;
        }

        .btn-group {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
        }

        button {
            padding: 12px 24px;
            font-size: 1rem;
            font-weight: 600;
            color: #fff;
            background-color: var(--primary);
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        button:hover {
            background-color: var(--primary-hover);
        }

        button.btn-secondary {
            background-color: #475569;
        }

        button.btn-secondary:hover {
            background-color: #334155;
        }

        .result-section {
            margin-top: 32px;
            display: none;
        }

        .table-container {
            overflow-x: auto;
            margin-bottom: 16px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: center;
            font-size: 0.95rem;
        }

        th, td {
            padding: 10px 14px;
            border: 1px solid var(--border-color);
        }

        th {
            background-color: #f1f5f9;
            font-weight: 700;
            color: var(--primary);
        }

        tr:nth-child(even) {
            background-color: #f8fafc;
        }

        .sig-upper {
            font-weight: bold;
            color: var(--accent-90);
        }

        .sig-lower {
            font-weight: bold;
            color: var(--accent-80);
        }

        .badge-info {
            display: inline-block;
            margin-top: 8px;
            font-size: 0.85rem;
            color: #64748b;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Calculadora de Significancia Estadística (80% / 90%)</h1>
    
    <div class="instructions">
        <strong>Instrucciones:</strong><br>
        1. Ingresa las muestras ($N$) separadas por comas, espacios o tabulaciones.<br>
        2. Pega la matriz de porcentajes o números. Puedes copiarlos directamente desde Excel o un archivo de texto.<br>
        3. Haz clic en <strong>"Calcular Significancias"</strong>.<br>
        4. Haz clic en <strong>"Copiar para Excel / Sheets"</strong> y pégalo directamente en tu hoja de cálculo.
    </div>

    <div class="form-group">
        <label for="sampleSizes">Tamaños de muestra (N por columna, ej: 590, 598, 618, 595, 597, 577):</label>
        <input type="text" id="sampleSizes" placeholder="590, 598, 618, 595, 597, 577">
    </div>

    <div class="form-group">
        <label for="dataMatrix">Matriz de datos (porcentajes/valores de las columnas):</label>
        <textarea id="dataMatrix" placeholder="Pega los datos aquí. Puede ser separados por tabulaciones (copiados de Excel) o por filas..."></textarea>
    </div>

    <div class="btn-group">
        <button onclick="procesarMatriz()">Calcular Significancias</button>
        <button class="btn-secondary" onclick="cargarEjemplo()">Cargar Ejemplo de Tu Consulta</button>
    </div>

    <div class="result-section" id="resultSection">
        <h2>Resultado de la Tabla</h2>
        <div class="btn-group">
            <button class="btn-secondary" onclick="copiarAExcel()">📋 Copiar para Excel / Sheets</button>
        </div>
        <div class="table-container" id="tableContainer"></div>
        <div class="badge-info">
            * <strong>MAYÚSCULA</strong> = Diferencia significativa al 90% ($Z \ge 1.282$).<br>
            * <strong>minúscula</strong> = Diferencia significativa al 80% ($Z \ge 0.842$).
        </div>
    </div>
</div>

<script>
    let tablaResultadoArray = [];

    function parsearN(str) {
        return str.trim().split(/[\s,	]+/).map(v => parseFloat(v)).filter(v => !isNaN(v));
    }

    function parsearMatriz(str, numCols) {
        // Limpiar texto
        let lineas = str.trim().split('\n').map(l => l.trim()).filter(l => l.length > 0);
        let matriz = [];

        // Si la entrada es una sola linea con todos los numeros pegados/seguidos o viene por lineas tabuladas
        let todosLosNumeros = [];
        lineas.forEach(linea => {
            let partes = linea.split(/[\s,	]+/);
            partes.forEach(p => {
                let val = parseFloat(p);
                if (!isNaN(val)) todosLosNumeros.push(val);
            });
        });

        // Agrupar en filas de numCols
        for (let i = 0; i < todosLosNumeros.length; i += numCols) {
            let fila = todosLosNumeros.slice(i, i + numCols);
            if (fila.length === numCols) {
                matriz.push(fila);
            }
        }
        return matriz;
    }

    function calcularLetrasSig(val1, n1, val2, n2, colLetra) {
        // Convertir de porcentaje 0-100 a proporción 0-1 si es necesario
        let p1 = val1 > 1 ? val1 / 100 : val1;
        let p2 = val2 > 1 ? val2 / 100 : val2;

        if (p1 <= p2) return ""; // Solo indicamos si es mayor

        let pPool = (p1 * n1 + p2 * n2) / (n1 + n2);
        let se = Math.sqrt(pPool * (1 - pPool) * ((1 / n1) + (1 / n2)));
        if (se === 0) return "";

        let z = (p1 - p2) / se;

        if (z >= 1.282) {
            return colLetra.toUpperCase(); // 90%
        } else if (z >= 0.842) {
            return colLetra.toLowerCase(); // 80%
        }
        return "";
    }

    function getLetraColumna(index) {
        return String.fromCharCode(65 + index); // 0 -> A, 1 -> B...
    }

    function procesarMatriz() {
        let nInput = document.getElementById("sampleSizes").value;
        let dataInput = document.getElementById("dataMatrix").value;

        let muestras = parsearN(nInput);
        if (muestras.length < 2) {
            alert("Por favor, ingresa al menos 2 tamaños de muestra separados por coma.");
            return;
        }

        let numCols = muestras.length;
        let matriz = parsearMatriz(dataInput, numCols);

        if (matriz.length === 0) {
            alert("No se pudieron organizar los datos con " + numCols + " columnas. Revisa los valores ingresados.");
            return;
        }

        tablaResultadoArray = [];

        // Encabezados
        let headers = ["Fila"];
        for (let j = 0; j < numCols; j++) {
            headers.push(getLetraColumna(j) + " (n=" + muestras[j] + ")");
        }
        tablaResultadoArray.push(headers);

        // Construir HTML de la tabla
        let htmlTable = "<table><thead><tr>";
        headers.forEach(h => htmlTable += "<th>" + h + "</th>");
        htmlTable += "</tr></thead><tbody>";

        matriz.forEach((fila, idxFila) => {
            let filaResult = ["Fila " + (idxFila + 1)];
            htmlTable += "<tr><td><strong>" + (idxFila + 1) + "</strong></td>";

            fila.forEach((val1, col1Idx) => {
                let n1 = muestras[col1Idx];
                let letrasSig = "";

                // Comparar contra todas las demás columnas
                fila.forEach((val2, col2Idx) => {
                    if (col1Idx !== col2Idx) {
                        let n2 = muestras[col2Idx];
                        let colLetra = getLetraColumna(col2Idx);
                        letrasSig += calcularLetrasSig(val1, n1, val2, n2, colLetra);
                    }
                });

                let textoCelda = val1.toFixed(2) + " " + letrasSig;
                filaResult.push(textoCelda.trim());

                // Formato HTML con colores visuales
                let letrasHtml = "";
                for (let char of letrasSig) {
                    if (char === char.toUpperCase()) {
                        letrasHtml += '<span class="sig-upper">' + char + '</span>';
                    } else {
                        letrasHtml += '<span class="sig-lower">' + char + '</span>';
                    }
                }

                htmlTable += "<td>" + val1.toFixed(2) + " " + letrasHtml + "</td>";
            });

            tablaResultadoArray.push(filaResult);
            htmlTable += "</tr>";
        });

        htmlTable += "</tbody></table>";

        document.getElementById("tableContainer").innerHTML = htmlTable;
        document.getElementById("resultSection").style.display = "block";
    }

    function copiarAExcel() {
        if (tablaResultadoArray.length === 0) return;

        let tsvContent = tablaResultadoArray.map(f => f.join("\t")).join("\n");

        navigator.clipboard.writeText(tsvContent).then(() => {
            alert("¡Tabla copiada al portapapeles! Ya puedes ir a Excel o Google Sheets y presionar Ctrl + V (Cmd + V en Mac).");
        }).catch(err => {
            alert("Error al copiar. Copia manualmente desde la tabla.");
        });
    }

    function cargarEjemplo() {
        document.getElementById("sampleSizes").value = "590, 598, 618, 595, 597, 577";
        document.getElementById("dataMatrix").value = `63.10 60.50 63.27 61.01 60.60 57.50
52.00 51.00 52.43 52.27 51.40 47.70
45.60 41.60 41.26 38.99 40.90 38.80
40.30 37.50 37.54 35.97 36.70 33.80
53.60 52.00 50.97 51.60 53.90 48.20
40.00 41.30 39.48 42.18 41.50 41.20
56.90 55.50 57.93 54.29 54.40 55.10
2.00 3.20 2.59 3.53 4.00 3.60
34.70 33.30 37.22 35.63 35.00 32.40
46.40 41.80 44.66 43.87 45.90 40.90
60.80 57.20 56.31 58.99 62.30 59.10
86.40 81.30 83.82 84.20 82.60 82.30
52.90 50.80 53.56 52.10 49.40 51.10
21.70 21.10 22.82 17.48 22.30 21.80
19.50 21.60 18.45 20.00 22.30 20.50
58.80 57.40 58.74 62.52 55.40 57.70
66.80 63.70 64.72 65.38 68.30 61.50
59.20 59.20 58.32 56.30 60.10 56.80
56.10 54.00 54.12 53.95 55.40 49.60
58.00 55.40 54.60 55.97 57.10 53.40
52.20 50.70 53.31 54.12 52.40 52.00
52.90 53.70 55.09 57.14 56.30 54.80
59.80 60.20 60.58 62.69 60.60 58.40
60.00 58.20 60.58 60.00 60.60 59.10
54.20 49.70 53.31 53.78 50.80 49.40
13.60 12.70 11.31 12.61 13.40 12.00
62.90 61.20 61.07 61.68 64.50 59.30
49.50 48.70 48.47 50.92 50.80 47.00
64.20 59.70 62.84 63.19 65.00 59.80
56.80 58.00 56.54 60.84 59.50 55.60
55.30 55.00 56.38 56.64 57.50 58.60
55.60 57.00 57.51 59.16 57.80 55.60
53.20 53.50 52.18 53.95 55.30 50.80
30.70 25.00 30.40 34.05 27.70 32.70
14.20 13.60 13.66 13.36 12.30 15.10
3.20 8.90 4.41 3.88 3.80 5.70
8.30 9.30 7.49 8.19 11.10 13.10
9.60 11.00 8.81 5.60 6.80 6.90
6.00 4.70 4.41 6.47 8.10 4.90
4.10 1.30 3.08 2.59 2.60 2.00
2.80 5.50 4.41 6.90 4.70 4.10`;
        procesarMatriz();
    }
</script>

</body>
</html>
