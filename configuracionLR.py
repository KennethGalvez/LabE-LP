import re

from afn import procesados, primera_funcion,siguiente_funcion, graficar


def partido(content):
    errorStack = []
    tokens_section = None
    productions_section = None
    sections = content.split('%%')
    if len(sections)!= 2:
        errorStack.append("No hay division clara en el archivo.")
    else:
        tokens_section = sections[0]
        productions_section = sections[1]
    return tokens_section, productions_section,errorStack

def seccion_de_resultado(content):
    productions = {}
    lines = content.split('\n')
    current_production = None
    production_rules = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.endswith(':'):
            if current_production:
                productions[current_production] = production_rules
                production_rules = []
            current_production = line[:-1]
        elif line.endswith(';'):
            line = line[:-1]
            if line != "":
                production_rules.append(line)
            productions[current_production] = production_rules
            production_rules = []
            current_production = None
        else:
            if (line.startswith('|') or line.startswith('->')) and current_production:
                line = line.strip().split('|')
                for item in line: 
                    if item.strip() != "":
                        production_rules.append(item.strip())

            elif ('|' in line) and current_production:
                line = line.strip()
                production_rules.extend(line.split('|'))
            else:
                production_rules.append(line)
    return productions


def archivo_yalp(tokens_section, productions_section, tokens, productions):
    error_stack = []

    if not tokens_section or not productions_section:
        error_stack.append("No hay division clara en el archivo.")

    lines = tokens_section.split('\n')
    for line in lines:
        if not line.startswith("%token") and not line.startswith("IGNORE") and line.strip():
            error_stack.append(f"No esta bien declarado el token usando el simbolo '%' ")
            break
    for token in tokens:
        if token in productions:
            error_stack.append(f"No concuerda el nombre del token con la regla")
            break

    return error_stack


def fin_yalp(filename,error_stack):
    with open(filename, 'r') as file:
        content = file.read()
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)  
    tokens_section, productions_section,divisionError = partido(content)
    tokens = None
    productions = None
    if(divisionError):
        error_stack.extend(divisionError)
    else:
        tokens = []
        lines = content.split('\n')
        for line in lines:
            if line.startswith("%token"):
                line_tokens = line[len("%token"):].strip().split(' ')
                tokens.extend(line_tokens)
        productions = seccion_de_resultado(productions_section)

        error_stack.extend(archivo_yalp(tokens_section, productions_section, tokens, productions))

    return tokens, productions,error_stack

def cambiar_valors(productions_dict):
    converted_productions = {}
    for key, value in productions_dict.items():
        converted_productions[key] = [rule.split() for rule in value]
    return converted_productions



def ver_contenido(file_content):
    replacements = {"\'\"\'": "(' 1 ')","\"\'\"": "(' 2 ')","\'`\'": "(' 3 ')",'"': " ' ","'": " ' "}
    for pattern, replacement in replacements.items():
        file_content = file_content.replace(pattern, replacement)

    pattern = re.compile(r'\(\*.*?\*\)', re.DOTALL)
    file_content = re.sub(pattern, '', file_content)

    return file_content

def constructor(file_content,inicio):
    ErrorStack = []
    patron = re.compile(r'\{.*?\}', re.DOTALL)
    content = re.sub(patron, '', file_content)
    content = content.split('\n')
    content = file_content.split('\n')
    simple_pattern = r"\[(\w)\s*-\s*(\w)\]"
    compound_pattern = r"\[(\w)\s*-\s*(\w)\s*(\w)\s*-\s*(\w)\]"
    simple_regex_pattern = r"^let\s+\w+\s+=\s+(.*?)$"
    regex = {}

    # Verificar llaves y paréntesis desbalanceados
    open_brackets = ['{', '(']
    close_brackets = ['}', ')']
    stack = []

    for line_num, line in enumerate(content, start=1):
        for char in line:
            if char in open_brackets:
                stack.append((char, line_num))
            elif char in close_brackets:
                if not stack or stack[-1][0] != open_brackets[close_brackets.index(char)]:
                    ErrorStack.append(f"Llaves desbalanceados en la línea")
                    break
                else:
                    stack.pop()

        line = line.strip()
        if line:
            if re.match(simple_regex_pattern, line):
                regex,ErrorStack = add_common_regex(line, regex, simple_pattern, compound_pattern,ErrorStack)
            elif line.startswith("let"):
                ErrorStack.append(f"Expresión regular inválida")
            elif line.startswith("rule tokens"):
                break

    if stack:
        for bracket, line_num in stack:
            ErrorStack.append(f"Llave '{bracket}' sin cerrar")

    fin = line_num+inicio
    return regex, ErrorStack,fin


def constructor_tokens(file_content, regex,errorStack,inicio):
    content = file_content.split('rule tokens =')
    matches = re.findall(r"'([^']+)'", content[1])
    for element in matches:
        text = element
        content[1] = content[1].replace("'" + text + "'", "'" + text.strip() + "'")
    content = content[1]
    content = content.strip().split('|')
    new_list = []
    for element in content:
        element = element.replace('\n', '')
        element = element.strip()
        new_list.append(element)
    content = new_list
    simple_pattern = r"\[(\w)\s*-\s*(\w)\]"
    compound_pattern = r"\[(\w)\s*-\s*(\w)\s*(\w)\s*-\s*(\w)\]"
    new_list = []
    for element in content:
        line_number = inicio + content.index(element)
        splitted = re.split(r'\s+', element, maxsplit=1)
        if len(splitted) >= 2:
            first_part = splitted[0]
            if first_part not in regex.keys():
                first_part,errorStack = common_regex(first_part.split(" "),regex, simple_pattern, compound_pattern,errorStack,line_number)
            second_part = splitted[1].replace('\t', '')
            second_part = second_part.replace('{' , '')
            second_part = second_part.replace('}', '')
            second_part = second_part.strip()
            element = [first_part, second_part]
            new_list.append(element)
        else:
            errorStack.append(f"Error en la línea {line_number}")
    content,errorStack =  new_list,errorStack
    new_list = []
    for element in content:
        expression = element[0]
        if "'" in expression or '"' in expression:
            element[0] = add_meta_character_string(expression)
        if "\\" in expression:
            element[0] = element[0].replace("\\", "")
        new_list.append(element)
    content = new_list
    new_list = []
    for element in content:
        r = element[0]
        if r in regex:
            replacement = regex[r]
            element.append(replacement)
        new_list.append(element)
    content = new_list
    return content,errorStack

def apertura_cerradura(file_content):
    content = file_content.split('\n')
    header_result = ''
    trailer_result = ''
    i = 0
    j = len(content) - 1

    # Build header
    while i < len(content):
        line = content[i]
        if '{' in line:
            header_result += line.rstrip('{').strip()
            break
        i += 1

    file_content = '\n'.join(content[i + 1:])

    # Build trailer
    while j >= 0:
        line = content[j]
        if '}' in line:
            trailer_result = line.lstrip('}').strip() + trailer_result
            break
        j -= 1

    real_trailer = ''
    for lines in range(j + 1, len(content)):
        line = content[lines]
        if '}' in line:
            real_trailer += line.rstrip('}')
            break
        else:
            real_trailer += line

    trailer_result = real_trailer + '\n' + trailer_result

    file_content = '\n'.join(content[:i]) + '\n' + '\n'.join(content[j + 1:])
    
    return header_result, trailer_result, file_content, i

def operadores_utils(line):
    operators = '*+|?()'
    for operator in operators:
        line = line.replace(operator, ' ' + operator + ' ')
    return line

def remplazar_regex(regex, simple_pattern, compound_pattern):
    search_spaces = re.search(r"\[(\\s|\\t|\\n|,|\s)+\]", regex)
    search_simple_regex_result = re.search(simple_pattern, regex)
    search_compound_regex_result = re.search(compound_pattern, regex)
    
    letters = 'abcdefghijklmnopqrstuvwxyz'
    upper_letters = letters.upper()
    numbers = '0123456789'

    if search_simple_regex_result and not search_compound_regex_result:
        regex = simple(regex, search_simple_regex_result, letters, numbers,upper_letters)
    elif search_compound_regex_result:
        regex = compuesto(regex, search_compound_regex_result, letters, numbers,upper_letters)
    elif search_spaces:
        regex = rango_variables(regex, search_spaces)
    return regex

def rango_variables(regex, search_spaces):
    space_map = {'\\s': r'\♦','\\t': r'\♥','\\n': r'\♠','"': r'\"',}
    space_list = re.findall(r"(\\s|\\t|\\n)", search_spaces.group(0))
    space_regex = '|'.join([space_map[space_type] for space_type in space_list])
    regex = re.sub(r"\[(\\s|\\t|\\n|,|\s)+\]", f'({space_regex})', regex)
    return regex

def simple(regex, search_simple_regex_result, letters, numbers,upper_letters):
    initial = search_simple_regex_result.group(1)
    final = search_simple_regex_result.group(2)
    result = manejar_rango(initial, final, letters, numbers,upper_letters)
    result = '(' + result + ')'
    regex = regex.replace('['+initial+'-'+final+']', result)
    return regex

def compuesto(regex, search_compound_regex_result, letters, numbers,upper_letters):
    first_initial = search_compound_regex_result.group(1)
    first_final = search_compound_regex_result.group(2)

    last_initial = search_compound_regex_result.group(3)
    last_final = search_compound_regex_result.group(4)

    first_range = manejar_rango(first_initial, first_final, letters, numbers,upper_letters)
    second_range = manejar_rango(last_initial, last_final, letters, numbers,upper_letters)

    result = '(' + first_range + '|' + second_range + ')'
    replaced = ''
    i = 0
    closed = False
    while not closed:
        if regex[i] == ']':
            closed = True
        replaced += regex[i]
        i += 1
    regex = regex.replace(replaced, result)
    return regex

def manejar_rango(initial, final, letters, numbers,upper_letters):
    result = str(initial) + '|'
    if initial.lower() in numbers and final.lower() in letters:
        result += max_num(initial, '9') + '|'
        initial_letter = 'A' if final in upper_letters else 'a'
        result += initial_letter + '|'
        result += max_strings(initial_letter, final, letters)
    elif initial.lower() in letters:
        final_letter = 'Z' if initial in upper_letters else 'z'
        if final in numbers:
            result += max_strings(initial, final_letter, letters) + '|'
            result += '0' + '|' + max_num('0', final)
        else:
            result += max_strings(initial, final, letters)
    elif initial in numbers:
            result += max_num(initial, final)
    return result

def max_strings(initial, final, letters):
    result = ''
    if ord(initial) > ord(final) and final.lower() in letters:
        result += max_strings(initial, 'z', letters) + '|'
        result += max_strings(chr(ord(initial.upper()) -1), final, letters)
    else:
        for i in range(ord(initial) + 1, ord(final)):
            between_letter = chr(i)
            result += between_letter + '|'
        result += final
    return result

def max_num(initial, final):
    result = ''
    for i in range(int(initial) + 1, int(final)):
        result += str(i) + '|'
    result += final
    return result


def common_regex(line, regex, simple_pattern, compound_pattern, errorStack,line_number=0):
    body,erroStack = build_common_regex(line, regex,errorStack,line_number)
    body = body.replace('ε', ' ')
    body = remplazar_regex(body, simple_pattern, compound_pattern)
    body = body.strip()
    return body,erroStack

def add_common_regex(line, regex, simple_pattern, compound_pattern,errorStack):
    line = operadores_utils(line)
    matches = re.findall(r"'([^']+)'", line)
    for element in matches:
        text = element
        line = line.replace("'" + text + "'", "'" + text.strip() + "'")
    line = line.replace('" "', '"ε"')
    line = line.replace("' '", "'ε'")
    line = line.split(" ")
    body,errorStack = common_regex(line[3:], regex, simple_pattern, compound_pattern,errorStack)
    regex[line[1]] = body
    return regex,errorStack

def build_common_regex(line, regex, errorStack, line_number=0):
    body = ''
    i = 0
    while i < len(line):
        element = line[i]
        if "'" in element or '"' in element or '`' in element:
            if "''" == element:
                body += "\\s"
            else:
                element = element.replace('"', '')
                element = element.replace("'", "")
                element = element.replace('+', '\+')
                element = element.replace('.', '\.')
                element = element.replace('*', '\*')
                element = element.replace('(', '\(')
                element = element.replace(')', '\)')
                body += element
        elif not check_operators(element) and len(element) > 1:
            if element in regex:
                replacement = regex[element]
                body += replacement
            else:
                errorStack.append(f"Error: {element} no esta en la rule")
        else:
            body += element
        i += 1
    return body, errorStack

def check_operators(element):
    operators = '*+|?'
    for operator in operators:
        if operator in element:
            return True
    return False

def add_meta_character_string(expression):
    expression = expression.replace('.', '\.')
    expression = expression.replace('+', '\+')
    expression = expression.replace('*', '\*')
    expression = expression.replace('"', '')
    expression = expression.replace("'", "")
    return expression

def evalToken(token):
    return eval(token[1])