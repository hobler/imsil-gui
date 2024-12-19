"""This Module handles the actual parsing of the .tex files.

After parsing the file and converting the latex specific syntax to
reStructuredText, the function parse_file returns a list of the collected
parameters.

The parseFile function uses mostly string operations some of which are defined
as separate functions if the type of operation is used multiple times.
"""

from code.parameter import Parameter


def parse_file(filename, tablename, parse_private):
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
        content = replace_references(content)
        content = repair_rest_warnings(content)
        content = replace_math_symbols(content)

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
            short_desc = entry.split('---')[1]
            short_desc = short_desc.split('}\n')[0].strip()
            short_desc = ' '.join(short_desc.split())
            short_desc = short_desc.replace('\\', '\\\\')

            # Get long_desc
            long_desc = entry.split('---')[1]
            long_desc = long_desc.split('}\n', 1)[1]
            long_desc = long_desc.split(r"\begin{keytab}")[0]
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
                p_range = 'no range defined in manual'
            else:
                p_range = ' '.join(p_range.split())
                p_range = p_range.strip(r'\>')
                p_range = p_range.replace(' ldots ', '...')
                p_range = p_range.replace('\\', '\\\\')
                p_range = process_list(p_range)

            parameters.append(Parameter(record, title, short_desc, long_desc,
                                        p_type, default_value, p_range))

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


def replace_references(inp):
    r"""This function converts the references from LaTeX to reStructuredText

    See project report for detailed information

    :param inp: String to be processed
    :return: Processed string
    """
    output = ''
    if r'\ref{' in inp:
        begin, end = inp.split(r'\ref{', 1)
        name, end = end.split('}', 1)

        name = name.replace(':', '_')
        output = begin + ' :ref:`' + name + '`' + end
        return replace_references(output)
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
            list_rst = list_rst + '- ' + elem.strip().strip(r'\\\\') + '\n'

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
    

def replace_math_symbols(string):
    """
    Replace latex math symbols with their unicode equivalent.
    
    :param string: String with latex math symbols
    :return: String with unicode math symbols
    """
    
    # Use the latex command to be raplced as the key and the replacement as the value
    # Note that order matters, ie. ^\\circ must be replaced before \\circ
    symbols = {"\\le": "≤", "\\ge": "≥", "\\times": "×",
               "\\infty": "∞", "\\ldots": "…", "\\langle": "⟨",
               "\\rangle": "⟩", "^\\circ": "°", "\\circ": "∘",
               "\\pi": "π", "\\AA": "Å"}
    
    for symbol in symbols:
        string = string.replace(symbol, symbols[symbol])
    
    return string

