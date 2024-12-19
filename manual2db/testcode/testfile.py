import os
import re
import time
import timeit

# Generate the filepath for the manual.tex file
manual_subfolder = "manual_2024-03"
manual_filename = "manual.tex"
current_file_location = os.path.dirname(__file__)
manual_path = os.path.join(current_file_location, manual_subfolder, manual_filename)

def get_param_filenames(manuak_path):
    """
    Return list of the filenames in the parameters section of the manual.
    """
    
    with open(manual_path, 'r', encoding='utf-8') as manual:
            manual_content = manual.read()
        
    # Find all parameter filenames in the file by matching "param_*.tex"
    regex_filenames = re.findall(r'param_\w+\.tex', manual_content)
    
    return regex_filenames

def replace_math_symbols(string):
    """
    Replace latex math symbols with their unicode equivalent.
    
    :param string: String with latex math symbols
    :return: String with unicode math symbols
    """
    
    # Use the latex command to be replaced as the key and the replacement as the value
    symbols = {"\\le": "≤", "\\ge": "≥", "\\times": "×", "\\infty": "∞", "\\ldots": "…"}
    
    for symbol in symbols:
        string = string.replace(symbol, symbols[symbol])
    
    return string

def remove_inline_math_environment(string):
    """
    Remove inline math environment, ie. $x$ -> x, from a string.
    
    :param string: String with inline math environment
    :return: String without inline math environment
    """
    
    return string.replace("$", "")

def remove_curly_brackets(string):
    """
    Remove curly brackets from a string.
    
    Does take into account that brackets might have a mathematical meaning.
    
    :param string: String with curly brackets
    :return: String without curly brackets
    """
    # Don't remove the brackets if they are after ^, _, \frac, \sqrt, \begin, \end, "}"
    symbols_before = ["^", "_", "c", "t", "n", "d", "}"]
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
                    

myStr = "FAC2SCR ---  $x^{nl}=1$}  factor $f$ for the  \\> $≥ 0$"
myStr2 = "1.53 / \\min( 1, \\sqrt{0.15+0.85 {ENERGY}^{{ATOM}^{1/2}}/10^{keV}} )"
myStr3 = "^{foo{foofoo}{foofoo}} {bar^{barbar}}\n \begin{foo}{bar} {bar}\n"
#print(remove_curly_brackets(myStr))
time1 = time.time()
#remove_curly_brackets(myStr2)
print(time.time() - time1)
print(remove_curly_brackets(myStr3))

