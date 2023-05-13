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

import pickle

#Transportar los datos al compi
almacen = pickle.dumps(almacen_de_afns)
gigante = pickle.dumps(mega_automata)
with open('almacen.pkl', 'wb') as i:
    i.write(almacen)
with open('gigante.pkl', 'wb') as i:
    i.write(gigante)

librerias = """
# -*- coding: utf-8 -*-
from afn import PostifixToAFN 
import pickle
import re
"""
compilado = """

with open('almacen.pkl', 'rb') as i:
    almacen = i.read()
with open('gigante.pkl', 'rb') as i:
    gigante = i.read()


almacen_de_afns = pickle.loads(almacen)
mega_automata = pickle.loads(gigante)

muchas = []

def spaces(value):
    return value.replace(' ', ',')

def read_file(file_name):
    with open(file_name, 'r') as f:
        return f.read()

def split_words(text):
    pattern = re.compile(r'"[^"]*"|\S+')
    return [spaces(texto) for texto in pattern.findall(text)]

def check_words(muchas, automaton_list):
    results = []
    for texto in muchas:
        texto = spaces(texto)
        value = mega_automata.simular(texto)
        try:
            if value[0] == True:
                for afn in automaton_list:
                    if value[1] in afn[1].ef:
                        results.append(f"'{texto}' = Pertence a {afn[0].upper()}")
                        break
            elif value == False:
                results.append(f"'{texto}' = No Pertence")
        except:
            pass
    return results

def write_file(file_name, results):
    with open(file_name, 'w') as f:
        for result in results:
            f.write(result)

cadenas = "cadena.txt"
contenido = read_file(cadenas)
muchas = split_words(contenido)
archivo_salida = "result.txt"
comparaciones = check_words(muchas, almacen_de_afns)
write_file(archivo_salida, comparaciones)
"""

with open('analizador.py', 'w') as archivo:
    archivo.write(librerias)
    archivo.write(compilado)