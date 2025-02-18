import PyPDF2
import json
from pathlib import Path
import re


def obtener_titulos_por_nivel():
    """Extrae las listas de títulos para cada nivel."""
    # Estructura conocida del documento
    estructura_conocida = {
        "nivel1": {
            "Índice": {},
            "Preámbulo": {
                "subtitulos": [
                    "El legado de la Unidad Popular",
                    "Seguridad alimentaria",
                    "Seguridad energética",
                    "La propiedad",
                    "Lecciones históricas",
                    "Asamblea Constituyente",
                    "Libertad",
                    "Política internacional",
                    "Palabras finales"
                ]
            },
            "El programa": {
                "subtitulos": {
                    "La Refundación de Chile": {
                        "subtitulos": {
                            "Nueva economía y el desarrollo de una industria nacional": [
                                "(Re)nacionalización y Expropiación",
                                "Propiedad",
                                "Industrialización",
                                "Energía",
                                "Industria alimentaria"
                            ],
                            "Asamblea Constituyente": [],
                            "Independencia económica y política": [],
                            "Garantías democráticas": [],
                            "Gobierno y oposición": [],
                            "Planes de plazo inmediato": [],
                            "Cibernética, desarrollo industrial e inteligencia artificial": [],
                            "Deuda y Gasto Público": [],
                            "Reservas Internacionales y oro": [],
                            "Reforma tributaria y distribución del ingreso": [],
                            "Gobierno austero": [],
                            "Derecho al trabajo y el deber de trabajar": [],
                            "Estabilidad monetaria": [],
                            "Política internacional": []
                        }
                    },
                    "Un nuevo orden institucional": {
                        "subtitulos": {
                            "Estado plurinacional": [],
                            "Organización política": [],
                            "Descentralización administrativa": [],
                            "Organización de la justicia": [],
                            "Refundación de las Fuerzas Armadas y de Orden": []
                        }
                    },
                    "Tareas sociales": {
                        "subtitulos": {
                            "Justicia": [],
                            "Sistema penitenciario y carcelario": [],
                            "Educación": [],
                            "Salud": [],
                            "Sistema de pensiones": [],
                            "Desarrollo sustentable": [],
                            "Defensa del laicismo": [],
                            "Emancipación de la mujer popular": [],
                            "Diversidad sexual": [
                                "Relaciones sexuales libres",
                                "Pedrastería y otras patologías"
                            ],
                            "Inmigración y racismo": [],
                            "Derecho a la vivienda y deuda habitacional": [],
                            "Crimen organizado": [],
                            "Derecho al transporte público": [
                                "Metro",
                                "Ferrocarriles"
                            ],
                            "¿Y qué tan rápido todo esto?": []
                        }
                    }
                }
            },
            "Despedida": {}
        }
    }

    nivel1 = list(estructura_conocida["nivel1"].keys())
    nivel2 = []
    nivel3 = []
    nivel4 = []

    # Recorrer estructura para extraer títulos por nivel
    for titulo1, contenido1 in estructura_conocida["nivel1"].items():
        if "subtitulos" in contenido1:
            if isinstance(contenido1["subtitulos"], list):
                nivel2.extend(contenido1["subtitulos"])
            else:
                for titulo2, contenido2 in contenido1["subtitulos"].items():
                    nivel2.append(titulo2)
                    if "subtitulos" in contenido2:
                        for titulo3, contenido3 in contenido2["subtitulos"].items():
                            nivel3.append(titulo3)
                            if isinstance(contenido3, list):
                                nivel4.extend(contenido3)

    return nivel1, nivel2, nivel3, nivel4, estructura_conocida


def detectar_nivel_titulo(texto, estructura, titulo_padre=None):
    """
    Determina el nivel jerárquico de un título (1-4) o retorna 0 si no es título.
    """
    texto = texto.strip()

    # Obtener listas de títulos por nivel
    nivel1, nivel2, nivel3, nivel4 = obtener_titulos_por_nivel()[0:4]

    # Verificar cada nivel
    if texto in nivel1:
        return 1
    if texto in nivel2:
        return 2
    if texto in nivel3:
        return 3
    if texto in nivel4:
        if titulo_padre and titulo_padre in nivel3:
            # Verificar que pertenece al padre correcto
            for seccion in estructura["nivel1"].values():
                if "subtitulos" in seccion and isinstance(seccion["subtitulos"], dict):
                    for subseccion in seccion["subtitulos"].values():
                        if "subtitulos" in subseccion:
                            for titulo3, contenido3 in subseccion["subtitulos"].items():
                                if titulo3 == titulo_padre and isinstance(contenido3, list):
                                    if texto in contenido3:
                                        return 4
        return 0
    return 0


def limpiar_texto(texto):
    """Elimina encabezados y elementos repetitivos."""
    lineas = texto.split('\n')
    lineas_limpiadas = []
    encabezado = [
        "Programa Político Básico de Unión Patriótica",
        "Por una patria industrializada, soberana y de perspectiva socialista",
        "¡A Refundar Chile!"
    ]

    for linea in lineas:
        linea = linea.strip()
        if linea and linea not in encabezado:
            if not re.match(r'^\d+$', linea) and not re.match(r'^.*\d+(\.\d+)?%?$', linea):
                lineas_limpiadas.append(linea)

    return '\n'.join(lineas_limpiadas)


def encontrar_numero_pagina(texto, pos):
    """Encuentra el número de página más cercano antes de una posición."""
    matches = list(re.finditer(r'<<PAGINA:(\d+)>>', texto[:pos]))
    return int(matches[-1].group(1)) if matches else 1


def procesar_documento(ruta_pdf):
    """Función principal que coordina todo el proceso."""
    print(f"\n=== INICIANDO PROCESAMIENTO DE DOCUMENTO ===")

    # Obtener estructura
    _, _, _, _, estructura = obtener_titulos_por_nivel()

    # Leer el PDF
    with open(ruta_pdf, 'rb') as archivo:
        lector_pdf = PyPDF2.PdfReader(archivo)
        texto_completo = ""
        documento = {
            "titulo": "Programa Político Básico de Unión Patriótica",
            "secciones": []
        }

        # Procesar páginas (saltando las dos primeras en blanco)
        for num_pagina, pagina in enumerate(lector_pdf.pages[2:], 3):
            texto_pagina = pagina.extract_text()
            texto_limpio = limpiar_texto(texto_pagina)

            if texto_limpio.strip():
                texto_completo += f"\n<<PAGINA:{num_pagina - 2}>>\n{texto_limpio}"

        # Procesar el texto completo
        titulo_actual = None
        nivel2_actual = None
        nivel3_actual = None
        lineas = texto_completo.split('\n')

        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue

            nivel = detectar_nivel_titulo(linea, estructura, nivel3_actual)
            pagina = encontrar_numero_pagina(texto_completo, texto_completo.find(linea))

            if nivel == 1:
                titulo_actual = {
                    "titulo": linea,
                    "nivel": 1,
                    "pagina": pagina,
                    "secciones": []
                }
                documento["secciones"].append(titulo_actual)
                nivel2_actual = None
                nivel3_actual = None
            elif nivel == 2 and titulo_actual:
                nivel2_actual = {
                    "titulo": linea,
                    "nivel": 2,
                    "pagina": pagina,
                    "secciones": []
                }
                titulo_actual["secciones"].append(nivel2_actual)
                nivel3_actual = None
            elif nivel == 3 and nivel2_actual:
                nivel3_actual = {
                    "titulo": linea,
                    "nivel": 3,
                    "pagina": pagina,
                    "secciones": []
                }
                nivel2_actual["secciones"].append(nivel3_actual)
            elif nivel == 4 and nivel3_actual:
                nivel3_actual["secciones"].append({
                    "titulo": linea,
                    "nivel": 4,
                    "pagina": pagina
                })

    # Guardar resultado
    nombre_json = Path(ruta_pdf).stem + "_procesado.json"
    with open(nombre_json, 'w', encoding='utf-8') as f:
        json.dump(documento, f, ensure_ascii=False, indent=2)

    # Mostrar resumen
    print("\n=== RESUMEN DE ESTRUCTURA ===")
    for seccion in documento["secciones"]:
        print(f"\nNivel 1: {seccion['titulo']} (pág. {seccion['pagina']})")
        for nivel2 in seccion["secciones"]:
            print(f"  Nivel 2: {nivel2['titulo']} (pág. {nivel2['pagina']})")
            for nivel3 in nivel2["secciones"]:
                print(f"    Nivel 3: {nivel3['titulo']} (pág. {nivel3['pagina']})")
                for nivel4 in nivel3["secciones"]:
                    print(f"      Nivel 4: {nivel4['titulo']} (pág. {nivel4['pagina']})")

    return documento


if __name__ == "__main__":
    ruta_pdf = "ProgramaArtes2017.pdf"
    resultado = procesar_documento(ruta_pdf)