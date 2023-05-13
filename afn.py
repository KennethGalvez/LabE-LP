from re import S
import re
import pandas as pd
from graphviz import Digraph


class PostifixToAFN():
    def __init__(self, postfix=None, counter=None, afns=None):
        self.postfix = postfix
        self.estados = []
        self.estados_list = []
        self.e0 = None
        self.ef = []
        self.transiciones = []
        self.transiciones_splited = []
        self.simbolos = []
        self.afn_final = []
        self.error = False
        self.counter = counter
        self.afns = afns

    def union(self, nombre):
        # Crear nuevas listas para almacenar los estados y transiciones del nuevo AFN
        nuevos_estados = []
        nuevas_transiciones = []

        # Crear un conjunto para almacenar los estados finales del nuevo AFN
        nuevos_estados_finales = set()

        # Crear un contador para generar nuevos nombres de estados
        counter = self.counter + 1

        # Crear un nuevo estado inicial
        e0 = counter

        for afn in self.afns:
            nuevos_estados_finales |= set(afn.ef)  # Unir los estados finales
            nuevas_transiciones += afn.transiciones_splited  # Unir las transiciones
            nuevos_estados += afn.estados  # Unir los estados
            nuevas_transiciones.append([e0, "ε", afn.e0])  # Agregar transiciones al nuevo estado inicial

        # Actualizar las variables de instancia con los nuevos valores
        self.ef = list(nuevos_estados_finales)
        self.transiciones_splited = nuevas_transiciones
        self.estados = nuevos_estados
        self.e0 = e0

        # Crear el gráfico del nuevo AFN usando la librería graphviz
        dot = Digraph()
        for estado in self.estados:
            if estado in self.ef:
                dot.node(str(estado), shape="doublecircle")
            else:
                dot.node(str(estado), shape="circle")
        for transicion in self.transiciones_splited:
            if transicion[1] == "ε":
                dot.edge(str(transicion[0]), str(transicion[2]), label="ε")
            else:
                dot.edge(str(transicion[0]), str(transicion[2]), label=transicion[1])
        dot.render(nombre, format='png', view=True)

    # Graficar
    def graficar(self, nombre):
        dot = Digraph()
        for estado in self.estados:
            if estado in self.ef:
                dot.node(str(estado), shape="doublecircle")
            else:
                dot.node(str(estado), shape="circle")
        for transicion in self.transiciones_splited:
            if transicion[1] == "ε":
                dot.edge(str(transicion[0]), str(transicion[2]), label="ε")
            else:
                dot.edge(str(transicion[0]), str(transicion[2]), label=transicion[1])
        dot.render(nombre, format='png', view=True)

    def operando(self, caracter):
        if(caracter.isalpha() or caracter.isnumeric() or caracter == "ε" or caracter == "-" or caracter == "=" or caracter == "."):
            return True
        else:
            return False

    def reemplazar_interrogacion(self):
        self.postfix = self.postfix.replace('?', 'ε?')

    def conversion(self, indice):
        self.reemplazar_interrogacion()
        simbolos = []
        postfix = self.postfix
        for i in postfix:
            if self.operando(i):
                if i not in simbolos:
                    simbolos.append(i)

        self.simbolos = sorted(simbolos)

        stack = []
        start = self.counter+1
        end = self.counter+2

        c1 = self.counter+1
        c2 = self.counter+1

        # implementation del algoritmo de thompson

        for i in postfix:
            # si es un simbolo
            if i in simbolos:
                self.counter = self.counter+1
                c1 = self.counter
                if c1 not in self.estados:
                    self.estados.append(c1)
                self.counter = self.counter+1
                c2 = self.counter
                if c2 not in self.estados:
                    self.estados.append(c2)
                self.afn_final.append({})
                self.afn_final.append({})
                stack.append([c1, c2])
                #self.afn_final[c1][i] = c2
                self.transiciones_splited.append([c1, i, c2])
            # si es un kleene
            elif i == '*':
                try:
                    r1, r2 = stack.pop()
                    self.counter = self.counter+1
                    c1 = self.counter
                    if c1 not in self.estados:
                        self.estados.append(c1)
                    self.counter = self.counter+1
                    c2 = self.counter
                    if c2 not in self.estados:
                        self.estados.append(c2)
                    self.afn_final.append({})
                    self.afn_final.append({})
                    stack.append([c1, c2])
                    #self.afn_final[r2]['ε'] = (r1, c2)
                    #self.afn_final[c1]['ε'] = (r1, c2)
                    if start == r1:
                        start = c1
                    if end == r2:
                        end = c2
                    self.transiciones_splited.append([r2, "ε", r1])
                    self.transiciones_splited.append([r2, "ε", c2])
                    self.transiciones_splited.append([c1, "ε", r1])
                    self.transiciones_splited.append([c1, "ε", c2])
                except:
                    self.error = True
                    print("\nEr")
            # si es una cerradura positiva
            elif i == '+':
                try:
                    r1, r2 = stack.pop()
                    self.counter = self.counter+1
                    c1 = self.counter
                    if c1 not in self.estados:
                        self.estados.append(c1)
                    self.counter = self.counter+1
                    c2 = self.counter
                    if c2 not in self.estados:
                        self.estados.append(c2)
                    # self.afn_final.append({})
                    # self.afn_final.append({})
                    stack.append([c1, c2])
                    self.afn_final[r2]['ε'] = (r1, c2)
                    if start == r1:
                        start = c1
                    if end == r2:
                        end = c2
                    self.transiciones_splited.append([r2, "ε", r1])
                    self.transiciones_splited.append([r2, "ε", c2])
                    self.transiciones_splited.append([c1, "ε", r1])
                except:
                    self.error = True
                    print("\nEr")

            # si es una concatenacion
            elif i == '^':
                try:
                    r11, r12 = stack.pop()
                    r21, r22 = stack.pop()
                    stack.append([r21, r12])
                    #self.afn_final[r22]['ε'] = r11
                    if start == r11:
                        start = r21
                    if end == r22:
                        end = r12
                    self.transiciones_splited.append([r22, "ε", r11])

                except:
                    self.error = True
                    print(
                        "\nEr")
            # si es un or
            elif i == "|":
                try:
                    self.counter = self.counter+1
                    c1 = self.counter
                    if c1 not in self.estados:
                        self.estados.append(c1)
                    self.counter = self.counter+1
                    c2 = self.counter
                    if c2 not in self.estados:
                        self.estados.append(c2)
                    self.afn_final.append({})
                    self.afn_final.append({})

                    r11, r12 = stack.pop()
                    r21, r22 = stack.pop()
                    stack.append([c1, c2])
                    #self.afn_final[c1]['ε'] = (r21, r11)
                    #self.afn_final[r12]['ε'] = c2
                    #self.afn_final[r22]['ε'] = c2
                    if start == r11 or start == r21:
                        start = c1
                    if end == r22 or end == r12:
                        end = c2
                    self.transiciones_splited.append([c1, "ε", r21])
                    self.transiciones_splited.append([c1, "ε", r11])
                    self.transiciones_splited.append([r12, "ε", c2])
                    self.transiciones_splited.append([r22, "ε", c2])
                except:
                    self.error = True
                    print("\n Er")
            # si es un uno o cero ?
            elif i == "?":
                self.counter = self.counter+1
                c1 = self.counter
                if c1 not in self.estados:
                    self.estados.append(c1)
                self.counter = self.counter+1
                c2 = self.counter
                if c2 not in self.estados:
                    self.estados.append(c2)
                self.afn_final.append({})
                self.afn_final.append({})

                r11, r12 = stack.pop()
                r21, r22 = stack.pop()
                stack.append([c1, c2])
                #self.afn_final[c1]['ε'] = (r21, r11)
                #self.afn_final[r12]['ε'] = c2
                #self.afn_final[r22]['ε'] = c2
                if start == r11 or start == r21:
                    start = c1
                if end == r22 or end == r12:
                    end = c2
                self.transiciones_splited.append([c1, "ε", r21])
                self.transiciones_splited.append([c1, "ε", r11])
                self.transiciones_splited.append([r12, "ε", c2])
                self.transiciones_splited.append([r22, "ε", c2])

        # asignacion de estados finales e iniciales
        self.e0 = start
        self.ef.append(end)

        # Guardar variables para impresión
        df = pd.DataFrame(self.afn_final)
        string_afn = df.to_string()
        for i in range(len(self.transiciones_splited)):
            self.transiciones.append(
                "(" + str(self.transiciones_splited[i][0]) + " - " + str(self.transiciones_splited[i][1]) + " - " + str(self.transiciones_splited[i][2]) + ")")
        self.transiciones = ', '.join(self.transiciones)

        for i in range(len(self.estados)):
            if i == len(self.estados)-1:
                ef = i
            self.estados_list.append(str(self.estados[i]))
        self.estados_list = ", ".join(self.estados_list)

        if self.error == False:
            #nombre = 'afn_grafico_'+str(indice)
            #self.graficar(nombre)  # imagen del AFN
            print("\n")
        else:
            print("\nEr")

    def cerradura_epsilon(self, estados):
        """
        Aplica la cerradura epsilon a los estados dados y devuelve todos los estados alcanzables.
        """
        # Inicializar una lista con los estados iniciales
        resultado = estados.copy()
        # Inicializar una pila con los estados iniciales
        pila = estados.copy()
        # Mientras la pila no esté vacía
        while pila:
            # Obtener el siguiente estado de la pila
            actual = pila.pop()
            # Obtener todas las transiciones epsilon desde el estado actual
            epsilon_transiciones = [
                t[2] for t in self.transiciones_splited if t[0] == actual and t[1] == "ε"]
            # Para cada estado alcanzable a través de una transición epsilon
            for e in epsilon_transiciones:
                # Si el estado no está en el resultado
                if e not in resultado:
                    # Agregar el estado al resultado y a la pila
                    resultado.append(e)
                    pila.append(e)
        # Devolver todos los estados alcanzables
        return resultado

    # simular una cadena en un afn    
    def simular(self, cadena):
        estados_actuales = self.cerradura_epsilon([self.e0])
        estados_finales = []

        # Cambio 1: Utilizar un bucle while en lugar de un bucle for para iterar sobre la cadena
        i = 0
        while i < len(cadena):
            nuevos_estados = []
            for estado in estados_actuales:
                for transicion in self.transiciones_splited:
                    if estado == transicion[0] and cadena[i] == transicion[1]:
                        nuevos_estados.append(transicion[2])
            if not nuevos_estados:
                return False
            estados_actuales = self.cerradura_epsilon(nuevos_estados)
            i += 1

        estados_finales = self.cerradura_epsilon(estados_actuales)
        if isinstance(self.ef, list):
            for estado_final in self.ef:
                if estado_final in estados_finales:
                    return (True, estado_final)
            return False
        else:
            return self.ef in estados_finales


def graficar(items, transitions):
    # Crear diccionario de estados
    states = {}
    for i, state in enumerate(items):
        if i == len(items) - 1: 
            label = 'Aceptacion'
        else:
            non_derived = []
            derived = []
            for item in state:
                if item.verific:
                    derived.append(str(item))
                else:
                    non_derived.append(str(item))

            label = f'{i}\n-----------\n'
            label += '\n'.join(non_derived) + '\n-----------\n' + '\n'.join(derived)

        states[i] = {'label': label, 'items': state}

    # Crear lista de transiciones
    edges = []
    for t in transitions:
        edges.append((t[0], t[1], t[2]))

    # Crear grafo
    dot = Digraph("LR0", format='png')
    dot.attr(rankdir="LR")
    dot.attr('node', shape='rectangle')

    for i, state in states.items():
        dot.node(str(i), label=state['label'])

    for t in edges:
        dot.edge(str(t[0]), str(t[2]), label=t[1])

    # Generar y guardar el gráfico como imagen PNG
    dot.render("mega_automata_LR", cleanup=True)

def procesar(producciones):
    no_terminales = set(producciones.keys())
    terminales = set()

    for lista_producciones in producciones.values():
        for produccion in lista_producciones:
            terminales.update(simbolo for simbolo in produccion if simbolo not in no_terminales)

    return terminales, no_terminales


def primera_funcion(producciones):
    terminales, no_terminales = procesar(producciones)
    first = {no_terminal: set() for no_terminal in no_terminales}

    cambiado = True
    while cambiado:
        cambiado = False
        for no_terminal, lista_producciones in producciones.items():
            for produccion in lista_producciones:
                for simbolo in produccion:
                    if simbolo in terminales:
                        if simbolo not in first[no_terminal]:
                            first[no_terminal].add(simbolo)
                            cambiado = True
                        break
                    else:
                        agregados = len(first[no_terminal])
                        first[no_terminal].update(first[simbolo] - {None})
                        if len(first[no_terminal]) != agregados:
                            cambiado = True
                        if None not in first[simbolo]:
                            break
                else:
                    if None not in first[no_terminal]:
                        first[no_terminal].add(None)
                        cambiado = True

    return first


def siguiente_funcion(producciones, conjuntos_first):
    terminales, no_terminales = procesar(producciones)
    follow = {no_terminal: set() for no_terminal in no_terminales}
    simbolo_inicial = next(iter(no_terminales))
    follow[simbolo_inicial].add('INIC')

    cambiado = True
    while cambiado:
        cambiado = False
        for no_terminal, lista_producciones in producciones.items():
            for produccion in lista_producciones:
                for i, simbolo in enumerate(produccion):
                    if simbolo in no_terminales:
                        if i + 1 < len(produccion):
                            siguiente_simbolo = produccion[i + 1]
                            if siguiente_simbolo in no_terminales:
                                agregados = len(follow[simbolo])
                                follow[simbolo].update(conjuntos_first[siguiente_simbolo] - {None})
                                if len(follow[simbolo]) != agregados:
                                    cambiado = True
                            else:
                                if siguiente_simbolo not in follow[simbolo]:
                                    follow[simbolo].add(siguiente_simbolo)
                                    cambiado = True
                        else:
                            agregados = len(follow[simbolo])
                            follow[simbolo].update(follow[no_terminal])
                            if len(follow[simbolo]) != agregados:
                                cambiado = True
    return follow


class Custom:
    def __init__(self, num, lenght,verific=False):
        self.num = (num[0], tuple(num[1]))
        self.lenght = lenght
        self.verific = verific
    def __repr__(self):
        return f'{self.num[0]} -->{" ".join(self.num[1][:self.lenght]) + "•" + " ".join(self.num[1][self.lenght:])}'
    def __eq__(self, other):
        return self.num == other.num and self.lenght == other.lenght
    def __hash__(self):
        return hash((self.num, self.lenght))

def cerrar(items, nums):
    terminados = set(items)
    changed = True
    while changed:
        changed = False
        for item in list(terminados):
            if item.lenght < len(item.num[1]) and item.num[1][item.lenght] in nums:
                non_terminal = item.num[1][item.lenght]
                for num in nums[non_terminal]:
                    new_item = Custom((non_terminal, num), 0,True)
                    if new_item not in terminados:
                        terminados.add(new_item)
                        changed = True
    return terminados

def compar(items, symbol, nums):
    recorrido = set()
    for item in items:
        if item.lenght < len(item.num[1]) and item.num[1][item.lenght] == symbol:
            recorrido.add(Custom(item.num, item.lenght + 1))
    return cerrar(recorrido, nums)

def procesados(nums):
    items = Custom((list(nums.keys())[0]+'\'', [list(nums.keys())[0]]), 0)
    states = [cerrar({items}, nums)]
    stack = [states[0]]
    transitions = []

    while stack:
        state = stack.pop()
        for symbol in set(sym for item in state for sym in item.num[1][item.lenght:item.lenght + 1]):
            next_state = compar(state, symbol, nums)
            if not next_state:
                continue
            if next_state not in states:
                states.append(next_state)
                stack.append(next_state)
            transitions.append((states.index(state), symbol, states.index(next_state)))
    
    accept_state = len(states)
    for i,state in enumerate(states):
        for item in state:
            if item.num[0] == list(nums.keys())[0]+'\'' and item.lenght == len(item.num[1]) and item.verific == False:
                transitions.append((i,'INIC',accept_state))
                break
    states.append(set())

    return states, transitions