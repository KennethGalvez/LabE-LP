import re
from postfix import *
from afn import *

def tokens(filename):
    # Función para obtener los tokens del archivo
    rege = r'let\s+([a-zA-Z0-9_-]+)\s+=\s+"([^"]*)"'
    with open(filename, 'r') as f:
        content = f.read()
    tonkensito = re.findall(rege, content)
    tokens = {}
    for name, regex in tonkensito:
        token_info = {'regex': regex, 'variable': name}
        tokens[name] = token_info
    return tokens

def convert_to_afn(regex, counter):
    # Función para convertir una expresión regular a un AFN
    exp = convertExpression(len(regex))
    # Postfix
    exp.RegexToPostfix(regex)
    if exp.ver:
        postfix = exp.res
        # AFN
        afn = PostifixToAFN(postfix=postfix, counter=counter)
        # método para convertir AFN
        afn.conversion(name)
        counter = afn.counter
        almacen_de_afns.append((name, afn))
    return counter

def simulate_string(mega_automata, string):
    # Función para simular una cadena en el AFN final y obtener el resultado
    return mega_automata.simular(string)

# archivo yalex
archivo = 'ya.lex'

# Obtener los tokens del archivo
tokens = tokens(archivo)

# Crear una lista para almacenar los AFN
almacen_de_afns = []
counter = -1

# creamos un AFN por cada token
for name, token in tokens.items():
    if 'regex' in token:
        regex = token['regex']
        counter = convert_to_afn(regex, counter)

tokens_nuevo = []

# Crear una nueva lista de tokens con las expresiones regulares modificadas
for name, token in tokens.items():
    if 'regex' in token:
        tokens_nuevo.append((name, token['regex'], True))
    else:
        operandos = []
        split = re.findall('\w+|[+*?()|.]', token)
        operandos.extend(split)

        for i, element in enumerate(operandos):
            for afn in almacen_de_afns:
                if element == afn[0]:
                    operandos[i] = "(" + afn[1] + ")"
        regex_n = ''.join(operandos)

        tokens_nuevo.append((name, regex_n, False))

# Por cada token compuesto en tokens creamos un AFN
for name, token, is_simple in tokens_nuevo:
    if not is_simple:
        counter = convert_to_afn(token, counter)

# Crear una lista con solo los AFN
chiquito = []
for afn in almacen_de_afns:
    chiquito.append(afn[1])

# Instancia de clase para convertir a AFN
mega_automata = PostifixToAFN(counter=counter, afns=chiquito)

# Unir todos los AFN y graficarlos
mega_automata.union("mega")
counter = mega_automata.counter
