// SUPONIENDO QUE TIENES UNA FUNCIÓN QUE PROCESA CADA CELDA:
function calcularSignificancia(p1, n1, p2, n2, letraColumna2) {
  // 1. Calcular el valor Z
  let p = (p1 * n1 + p2 * n2) / (n1 + n2);
  let errorEstandar = Math.sqrt(p * (1 - p) * ((1 / n1) + (1 / n2)));
  let z = (p1 - p2) / errorEstandar;

  // 2. Determinar si hay significancia
  if (z >= 1.282) { 
    return letraColumna2.toUpperCase(); // 90% Confianza -> MAYÚSCULA
  } else if (z >= 0.842) {
    return letraColumna2.toLowerCase(); // 80% Confianza -> minúscula
  }
  return ""; // Sin diferencia significativa
}

// AL MOMENTO DE MOSTRAR LA TABLA EN PANTALLA / TEXTO:
let resultadoTexto = "";

filas.forEach(fila => {
  fila.celdas.forEach((celda, index) => {
    // Agregamos el valor y sus letras de significancia
    resultadoTexto += celda.valor + celda.letrasSignificancia;
    
    // IMPORTANTE: Agregar tabulación entre columnas para que no se peguen
    resultadoTexto += "\t"; 
  });
  // IMPORTANTE: Salto de línea al terminar la fila
  resultadoTexto += "\n"; 
});
