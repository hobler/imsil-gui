"""This Module handles the actual parsing of the .tex files.

After parsing the file and converting the latex specific syntax to
reStructuredText, the function parse_file returns a list of the collected
parameters.

The parseFile function uses mostly string operations some of which are defined
as separate functions if the type of operation is used multiple times.
"""

from code.parameter import Parameter
import re
import os


def parse_file(filename, tablename, parse_private, manual_path):
    r"""Parse the .tex files from the manual.

    This function uses all \keydescription environments to create new instances
    of the parameter class. Additionally, the text is converted to reST.

    :param filename: File name with abspath
    :param tablename: Name of record = name of sqlite table
    :return: List of Parameter objects
    """
    print('>>>>>> Filename: ', filename)
    with open(filename) as fp:
        content = ''

        # Remove comments
        for line in fp:
            if line[0] is not '%':
                content += line
        
        content = replace_texttt_mathwrapper(content)
        content = parse_private_sections(content, private=parse_private)
        content = remove_iffalse(content)
        content = replace_latex_macros(content, {r'\&': '&', r'\AA': r'$\AA$',
                                               '~': ' ', r'\%': '%'})
        content = content.replace(r'\ ', ' ')
        content = replace_tt(content)
        content = replace_citations(content)
        content = replace_mathrm(content)
        
        # aux file is needed to find reference bindings
        with open(manual_path.replace(".tex", ".aux"), 'r') as aux_file:
            manual_aux = aux_file.read()
        
        content = replace_references(content, manual_aux)
        content = repair_rest_warnings(content)
        content = replace_math_symbols(content)
        content = remove_inline_math_environment(content)
        content = remove_curly_brackets(content)
        

        # List of the parameters to be returned
        parameters = []

        # Record name for parameter class
        record = tablename
        # Split into params
        entries = content.split(r"\begin{keydescription}{")[1:]

        for entry in entries:
            # Get title
            title = entry.split('---')[0]
            title = ' '.join(title.split())

            # Get short_desc
            sd_pattern = r'(?<=---\s)(.*?)(?=}(?:\n\t%\n\t|\n  | \n  |\n))'
            sd_regex = re.compile(sd_pattern, re.DOTALL)
            sd_match = sd_regex.search(entry)
            short_desc = sd_match.group(1)
            short_desc = ' '.join(short_desc.split())
            short_desc = short_desc.replace('\\', '\\\\')

            # Get long_desc
            ld_pattern = r'(?:}\n\t%\n\t|}\n  |} \n  |}\n|} \n)(.*?)(?:\\begin\{keytab\}|\\end\{keydescription\})'
            ld_regex = re.compile(ld_pattern, re.DOTALL)
            ld_match = ld_regex.search(entry)
            long_desc = ld_match.group(1)
            long_desc = ' '.join(long_desc.split())
            long_desc = long_desc.replace('\\', '\\\\')

            # Get keytab
            try:
                keytab = entry.split(r"\begin{keytab}")[1]
            except IndexError:
                continue

            # Get type
            p_type = keytab.split('Type:')[1]
            p_type = p_type.split('Default:')[0].strip()
            p_type = ' '.join(p_type.split())
            p_type = p_type.strip(r'\>')
            
            # Get default value
            default_value = keytab.split('Default:')[1]
            default_value = default_value.split('Range:')[0].strip()
            # in case there is no range defined
            if 'keytab' in default_value:
                default_value = default_value.split(r'\end{keytab}')[0].strip()
            default_value = ' '.join(default_value.split())
            default_value = replace_nodefault(default_value)
            default_value = default_value.replace('\\', '\\\\')
            default_value = process_list(default_value)
            default_value = process_table(default_value)

            # Get range (if defined)
            try:
                p_range = keytab.split('Range:')[1]
                p_range = p_range.split(r'\end{keytab}')[0].strip()
            except IndexError:
                p_range = 'No range defined in manual'
            else:
                p_range = ' '.join(p_range.split())
                p_range = p_range.strip(r'\>')
                p_range = p_range.replace(' ldots ', '...')
                p_range = p_range.replace('\\', '\\\\')
                p_range = p_range.rstrip("}")
                p_range = process_list(p_range)
                
            # Get string condition
            condition = get_range_condition(title, p_range)

            parameters.append(Parameter(record, title, short_desc, long_desc,
                                        p_type, default_value, p_range, condition))

    return parameters


def replace_texttt(inp, replace=''):
    r"""Replace latex command \texttt for typewriter look.

    It recursively replaces all occurrences of \texttt that the inp text
    contains.

    NOTE: There might be some interferences with the reST syntax if the string
          replace is not empty

    :param inp: String string to be processed
    :param replace: Optional string that replaces '\texttt{' as well as '}'
    :return: Processed string
    """
    output = ''
    if r'\texttt{' in inp:
        begin, end = inp.split(r'\texttt{', 1)
        begin = begin + replace
        end = end.replace('}', replace, 1)
        output = output + begin + end
        return replace_texttt(output, replace)
    else:
        return inp


def replace_texttt_mathwrapper(inp, replace=''):
    r"""Wrapper function for replace_texttt.

    As the equations get rendered by MathJax, in any section enclosed by $
    occurrences of \texttt{} must be changed to {}.

    :param inp: String to be processed
    :param replace: optinal string that replaces '\texttt{' as well as '}'
    :return: Processed string
    """
    chunks = inp.split('$')
    is_math = False
    output = ''

    for chunk in chunks:
        if is_math:
            output += chunk.replace(r'\texttt', '')
        else:
            output += replace_texttt(chunk, replace)
        output += '$'
        is_math = not is_math

    output = output[:-1]
    return output


def replace_tt(inp, replace=''):
    r"""Replace latex command \tt for typewriter look

    It recursively replaces all occurrences of {\tt that the inp string
    contains.

    NOTE: There might be some interferences with the reST syntax if the string
          replace is not empty

    :param inp: String to be processed
    :param replace: Optional string that replaces '{\tt' as well as '}'
    :return: Processed string
    """
    output = ''
    if r'{\tt' in inp:
        begin, end = inp.split(r'{\tt', 1)
        begin = begin + replace
        end = end.replace('}', replace, 1)
        output = output + begin.strip() + end
        return replace_tt(output, replace)
    else:
        return inp


def replace_mathrm(inp):
    r"""Replace the latex command \mathrm

    :param inp: String to be processed
    :return: Processed string
    """
    output = ''
    if r'\mathrm' in inp:
        begin, end = inp.split(r'\mathrm{', 1)
        begin = begin + '{'
        output = output + begin + end
        return replace_mathrm(output)
    else:
        return inp


def replace_nodefault(inp):
    r"""For parameters where there is no default value assigned

    :param inp: String to be processed
    :return: Processed string
    """
    if '~ -- ~~~' in inp:
        output = inp.replace('~', ' ', 4)
        return output
    else:
        return inp


def repair_rest_warnings(inp):
    r"""This Function deals with problems regarding the reST Syntax

    For example changing single quotes with double quotes

    :param inp: string to be processed
    :return: returns processed string
    """
    output = inp.replace('``', '"').replace("''", '"')

    return output


def replace_references(inp, manual_aux):
    r"""This function converts the references from LaTeX to reStructuredText

    See project report for detailed information

    :param inp: String to be processed
    :return: Processed string
    """
    output = ''
    if r'\ref{' in inp:
        begin, end = inp.split(r'\ref{', 1)
        name, end = end.split('}', 1)

        manual_pattern = r'\{' + name + r'\}\{\{(\d+(?:\.\d+)?)\}'
        manual_match = re.search(manual_pattern, manual_aux)

        if manual_match:
            name = manual_match.group(1)
            output = begin + name + ' of the manual' + end
        else:
            name = name.replace(':', '_')
            output = begin + ' :ref:`' + name + '`' + end
            
        return replace_references(output, manual_aux)
    else:
        return inp


def process_list(inp):
    """This function processes lists in default and range attributes.

    :param inp: String to be processed
    :return: Processed string
    """
    inp = inp.strip(r'\\>')
    elements = inp.split(r'\\>')
    if len(elements) > 1:
        list_rst = ''
        for elem in elements:
            list_rst = list_rst + elem.strip().strip(r'\\\\') + '\n'

        list_rst = list_rst + '\n'
        return list_rst
    else:
        return elements[0]


def parse_private_sections(inp, private='True'):
    """Remove private sections if private==True

    :param inp: String to be processed
    :param private: Flag indicating removal of private sections
    :return: Processed string
    """
    if r'\ifprivate' in inp:
        begin, end = inp.split(r'\ifprivate', 1)
        private_section, end = end.split(r'\fi', 1)

        if private:
            output = begin + end
        else:
            output = begin + private_section + end
        return parse_private_sections(output, private)
    else:
        return inp


def remove_iffalse(inp):
    r"""Remove sections within \iffalse \fi blocks

    :param inp: String to be processed
    :return: returns Processed string
    """
    if r'\iffalse' in inp:
        begin, end = inp.split(r'\iffalse', 1)
        _, end = end.split(r'\fi', 1)

        return remove_iffalse(begin + end)
    else:
        return inp


def replace_latex_macros(inp, macros):
    r"""Replaces special latex characters with the reStrucuredText pendant.

    E.g. \\% gets replaced with %

    :param inp: String to be processed
    :param macros: Dictionary containing strings to be replaced as keys and
    replacements as values
    :return: Processed string
    """
    for key in macros:
        inp = inp.replace(key, macros[key])

    return inp


def replace_citations(inp):
    r"""Convert the references from LaTeX to reStructuredText

    See project report for detailed information

    :param inp: String to be processed
    :return: Processed string
    """
    if r'\cite{' in inp:
        begin, end = inp.split(r'\cite{', 1)
        citation, end = end.split('}', 1)

        output = begin + '[' + citation + ']_' + end
        return replace_citations(output)
    else:
        return inp


def process_table(inp):
    """Process table from DENSITY in material

    NOTE: This function cannot parse all tables

    :param inp: String containing table
    :return: Input string with table formatted in reStructured text
    """
    if r'begin{tabular}' in inp:
        begin, table = inp.split(r'begin{tabular}', 1)
        #remove label
        table = table.split('}', 1)[1]

        table, end = table.split(r'\\end{tabular}', 1)
        lines = table.split(r'\\\\')[0:-1]

        table_str = ''
        begin = begin.rstrip().rstrip('-') #table cannot be bullet of a list
        for line in lines:
            values = line.split('&')
            table_str = table_str + '\n' + values[0] + '    ' + values[1] + '\n'

        table_str += '\n'
        return begin + table_str + end
    else:
        return inp


def remove_inline_math_environment(string):
    """
    Remove inline math environment, ie. $x$ -> x, from a string.
    Also removes any whitespaces in formulas
    
    :param string: String with inline math environment
    :return: String without inline math environment
    """
    
    return_string = string
    replacement_string = ""
    in_math = False
    
    for ch in string:
        if ch == "$":
            
            if in_math:
                return_string = return_string.replace(f"${replacement_string}$", replacement_string.replace(" ", ""))
                replacement_string = ""
                in_math = False
            else:
                in_math = True
                
        else:
            
            if in_math:
                replacement_string += ch
        
    
    return return_string


def remove_curly_brackets(string):
    """
    Remove curly brackets from a string.
    
    Does take into account that brackets might have a mathematical meaning.
    
    :param string: String with curly brackets
    :return: String without curly brackets
    """
    # Don't remove the brackets if they are after ^, _, √, \begin, \end, "}"
    symbols_before = ["^", "_", "√", "t", "n", "d", "}"]
    # Also don't remove if brackets are before "\n"
    symbols_after = ["\n"]
    
    return_string = [None]*len(string)
    
    # To remember what happened to the last matching bracket
    brackets = []
    
    # Build the string char by char, checking if the brackets should be added or not
    for i in range(len(string)):
        
        match string[i]:
            case "{":
                # Skip first bracket
                if i == 0:
                    brackets.append("skip")
                else:
                    if string[i-1] in symbols_before:
                        return_string[i] = string[i]
                        brackets.append("add")
                    else:
                        brackets.append("skip")
                    
            case "}":
                if (brackets and brackets.pop() == "add") or string[i+1] in symbols_after:
                    return_string[i] = string[i]
            
            case _:
                return_string[i] = string[i]
        
    return "".join(filter(None, return_string))


def apply_modifier(text, modifier, symbols):
    """
    Called by replace_math_symbols() to apply the modifier to the given text.
    Used to replace latex subscripts and superscript characters with their unicode equivalent.
    This function was modifed from https://github.com/ypsu/latex-to-unicode
    
    :param text: The text to apply the modifier to.
    :param modifier: The modifier to search for, "_" or "^".
    :param symbols: The dictionary of symbols to replace the modifier with.
    :return: The text with unicode subscripts or superscripts.
    """
	
    return_text = ""
    new_text = ""
    
    # tags that should not be replaced with subscript or superscript
    exclude_tags = ["keytab", "keydescription"]
    
    mode_normal, mode_modified, mode_long = range(3)
    mode = mode_normal
    
    for ch in text:
        
        # enter modified mode. don't save the modifier
        if mode == mode_normal and ch == modifier:
            mode = mode_modified
        
        elif mode == mode_modified:
            
            # modify entire parantehsis
            if ch == '{':
                new_text += ch
                mode = mode_long
            
            # modify only one char
            else:
                nch = symbols.get(ch)
                # if no replacement exists, the modifier should be kept
                return_text += nch if nch else f"{modifier}{ch}"
                    
                mode = mode_normal
        
        # exit modified mode. save the modifier and the string if applicable
        elif mode == mode_long and ch == '}':
            new_text += ch
            mode = mode_normal
            
            # don't check for sub and super replacements when the tag is excluded
            if new_text[1:-1] in exclude_tags:
                return_text += new_text
                new_text = ""
                mode = mode_normal
                continue
            
            # check if new_text can be modified and applied
            replace_text = ""
            for nch in new_text:
                
                if nch in ["{", "}"]:
                    continue
                
                nch = symbols.get(nch)
                
                if nch:
                    replace_text += nch
                else:
                    return_text += modifier + new_text
                    new_text = ""
                    break
            else:
                return_text += replace_text
                new_text = ""
                continue

            continue
        
        # Inside curly brackets, add characters
        elif mode == mode_long:
            new_text += ch
                
        # Normal mode, add characters
        else:
            return_text += ch
    
    return return_text


def replace_fractions(text):
    """
    Replace latex fractions with parantheses and a division sign.
    
    :param text: The text to replace fractions in.
    :return: The text with the fractions replaced.
    """
    
    # Pattern to match \frac{STR1}{STR2} with nested brackets
    pattern = r'\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}'
    
    text_match = re.search(pattern, text)
    
    while text_match:
        nom = f"({text_match.group(1)})" if len(text_match.group(1)) > 1 else f"{text_match.group(1)}"
        denom = f"({text_match.group(2)})" if len(text_match.group(2)) > 1 else f"{text_match.group(2)}"
        text = text.replace(text_match.group(0), f"{nom}/{denom}")
        text_match = re.search(pattern, text)
    
    return text
    

def replace_math_symbols(input_string):
    """
    Replace latex math symbols with their unicode equivalent, also in subscripts and superscripts.
    This function was modifed from https://github.com/ypsu/latex-to-unicode
    
    :param string: String with latex math symbols
    :return: String with unicode math symbols
    """
    
    filepath = os.path.dirname(__file__)
    
    # Dictionary of latex math symbols and their unicode equivalent
    # Symbol list found at https://github.com/ypsu/latex-to-unicode
    with open(f"{filepath}/symbols", "r", encoding="utf-8") as file:
        symbols_raw = file.read()
        
    with open(f"{filepath}/superscripts", "r", encoding="utf-8") as file:
        superscripts_raw = file.read()
        
    with open(f"{filepath}/subscripts", "r", encoding="utf-8") as file:
        subscripts_raw = file.read()
        
    # Save the symbols in dictionaries to be used in the apply_modifier function
    superscripts_dict = {}
    subscripts_dict = {}
    
    for line in superscripts_raw.split("\n"):
        if line:
            latex, unicode = line.split(" ")
            superscripts_dict[latex] = unicode
            
    for line in subscripts_raw.split("\n"):
        if line:
            latex, unicode = line.split(" ")
            subscripts_dict[latex] = unicode
            
    # Replace latex symbols at once
    for line in symbols_raw.split("\n"):
        if line:
            latex, unicode = line.split(" ", maxsplit=1)
            # First replace symbols with optional whitespace
            input_string = input_string.replace(latex, unicode)
    
    input_string = apply_modifier(input_string, "^", superscripts_dict)
    input_string = apply_modifier(input_string, "_", subscripts_dict)
    input_string = replace_fractions(input_string)
    
    return input_string

def get_range_condition(parameter, range):
    """
    Parse the range string to get a condition for the database
    that can be used with eval() to check if a value is within the range.
    
    :param parameter: The name of the parameter
    :param range: The range string from the manual
    :return: The condition string
    """
    
    # conditions with only one bound such as "< 0"
    pattern = r'^\s*(\d+\s*[><≥≤]\s*\d*|\d*\s*[><≥≤]\s*\d+)\s*\.?\s*$'
    search = re.search(pattern, range)
    
    if search:
        # replace for eval() to function
        condition = range.replace("≤", "<=").replace("≥", ">=").replace(".", "").replace(" ", "")
        
        if condition[0].isnumeric():
            return f"{condition}{parameter}"
        else:
            return f"{parameter}{condition}"
    
    # condition with the parameter present like "DAMAMO > 0"
    pattern = r'^\s*(\w+)\s*([><≥≤])\s*(\w+)\s*$'
    search = re.search(pattern, range)
    
    if search:
        condition = range.replace("≤", "<=").replace("≥", ">=").replace(" ", "")
        return condition
    
    # conditions with upper and lower bounds such as 0 ≤ NRAD2 ≤ 32
    pattern = r'^\s*(\w+)\s*([><≥≤])\s*(\w+)\s*([><≥≤])\s*(\w+)\s*$'
    search = re.search(pattern, range)
    
    if search:
        condition = range.replace("≤", "<=").replace("≥", ">=").replace(" ", "")
        
        return condition
        
    # true and false condition such as "T,F" strictly without extra conditions
    pattern = r'^\s*T\s*,\s*F\s*$'
    search = re.findall(pattern, range)
    
    if search:
        return f"{parameter}.lower() in ['true', 'false']"
    
    # lists of names, like 'wurtzite', 'wurzite', '2H'
        # strictly match list of names without extra conditions
    if range.lstrip("- ")[0] == "'" and range.rstrip(".")[-1] == "'":
        pattern = r"'([^']+)'(?:\s*[,\n-]\s*|\s+)?+"
        search = re.findall(pattern, range)
        
        if search:
            return f"{parameter}.lower() in {[x.lower() for x in search]}"
        
    # condition is "arbitrary" or "any"
    if range.strip("- ").lower() in ["arbitrary", "any"]:
        return "True"
    
    # special cases
    if parameter == "IARAND":
            return "1 ≤ IARAND ≤ 70000 if RNG.lower() == 'haas' else 1 ≤ IARAND ≤ 131071"
        
    elif parameter == "NAME":
        if range.strip() == "any chemical name of an atom":
            return f"NAME.lower() in {get_chemical_elements()}"
        else:
            return "NAME.lower() in ['sc', 'bcc', 'fcc', 'zincblende', '3c', 'wurtzite', 'wurzite', '2h', '4h', '6h']"

    elif range.strip() == "any real number":
        return f"{parameter}.replace('.', '').replace(',', '').isnumeric()"
    
    elif parameter == "NDAMDIM":
        return "1<=NDAMDIM<=3"
    
    elif parameter == "LAMZON":
        #  T if LDAMDYN=T \\\\ T, F otherwise
        return "LAMZON.lower() == 'true' if LDAMDYN.lower() == 'true' else LAMZON.lower() in ['true', 'false']"
    
    elif parameter == "XTAL":
        return "len(XTAL) <= 80"
    
    # "no range defined in manual"
    return "No condition parsed"

def get_chemical_elements():
    """Returns a list of chemical element names in lowercase."""
    elements = [
        'h', 'he', 'li', 'be', 'b', 'c', 'n', 'o', 'f', 'ne',
        'na', 'mg', 'al', 'si', 'p', 's', 'cl', 'ar', 'k', 'ca',
        'sc', 'ti', 'v', 'cr', 'mn', 'fe', 'co', 'ni', 'cu', 'zn',
        'ga', 'ge', 'as', 'se', 'br', 'kr', 'rb', 'sr', 'y', 'zr']
    return elements