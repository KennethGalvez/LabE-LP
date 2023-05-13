import re
from configuracionLR import *

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def write_to_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

def verificar_archivo_yalep(nombre_archivo):
    errores = []
    with open(nombre_archivo) as archivo:
        contenido = archivo.read()
        
        # Verificar si el archivo comienza con el encabezado esperado
        if not contenido.startswith("/* Configuración del parser para gramática No.1 */"):
            errores.append("El archivo no comienza con el encabezado esperado.")
        
        # Verificar si el archivo define los tokens esperados
        tokens_esperados = {"ID", "PLUS", "TIMES", "LPAREN", "RPAREN", "WS"}
        tokens_definidos = set(re.findall(r"%token\s+(\w+)", contenido))
        if tokens_definidos != tokens_esperados:
            errores.append(f"El archivo define los siguientes tokens: {tokens_definidos}. Se esperaba: {tokens_esperados}.")
        
        # Verificar si se define la regla de la gramática esperada
        regla_esperada = "expression:\n    expression PLUS term\n  | term\n;\nterm:\n    term TIMES factor\n  | factor\n;\nfactor:\n    LPAREN expression RPAREN\n  | ID\n;"
        if regla_esperada not in contenido:
            errores.append("El archivo no define la regla de la gramática esperada.")
    
    # Devolver la lista de errores (vacia si no se encontraron errores)
    return errores


# Archivos a utilizar
yalex_file = 'slr-1.yal'
yalp_file = 'slr-1.yalp'
output_file = 'funciones.txt'

# Uso de la función
errores = verificar_archivo_yalep(yalp_file)

# Leer contenido de yalex_file
yalex_content = read_file_content(yalex_file)








# Construir el encabezado y pie de página
header_result, trailer_result, file_content, i = apertura_cerradura(yalex_content)

# Modificar el contenido del archivo
file_content = ver_contenido(file_content)

# Construir las expresiones regulares
regex, errorStack, fin = constructor(file_content, i)

# Construir los tokens
LEXtokens, errorStack = constructor_tokens(file_content, regex, errorStack, fin+1)

# Analizar el archivo yalp
tokens, productions_dict, errorStack = fin_yalp(yalp_file, errorStack)

# Verificar los tokens definidos en LEXtokens
gooTokens = []

for token in tokens:
    for lex_token in LEXtokens:
        evald = evalToken(lex_token)
        if token == evald:
            gooTokens.append(token)
    if token not in gooTokens:
        errorStack.append(f"Token {token} no definido en el YALEX")

if len(gooTokens) < len(LEXtokens):
    errorStack.append("Faltaron Definir tokens en el YAPAR")

# Convertir las producciones
converted_productions = cambiar_valors(productions_dict)

# Procesar las producciones
states, transitions = procesados(converted_productions)

# Graficar los estados y transiciones
graficar(states, transitions)

# Funciones para obtener los First y Follow sets
def cambiar_valors(productions):
    converted_productions = {}
    for key, value in productions.items():
        converted_productions[key] = [prod.split() for prod in value]
    return converted_productions

converted_prod = cambiar_valors(productions_dict)
first = primera_funcion(converted_prod)
follow = siguiente_funcion(converted_prod, first)

# Escribir el contenido en el archivo de salida
output_content = "\n"
for non_terminal, first_set in first.items():
    output_content += f"{non_terminal}: {first_set}\n"
output_content += "\n"
for non_terminal, follow_set in follow.items():
    output_content += f"{non_terminal}: {follow_set}\n"

write_to_file(output_file, output_content)
