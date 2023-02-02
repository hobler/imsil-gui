"""
Perform functions to analyze molecule names and to get all the unique atoms.

Parameters:
    `MOLECULE_END`
        = -1. Indicates the end of a molecule in get_unique_atoms.
    `VALUE_ERROR`
        = -2. Indicates a wrong character in the molecule name.

Functions:
    `get_all_elements`
        Extracts all of the Elements of the element.f90 file and returns them
            as a List of Element Objects
    `get_unique_atoms`
        Returns all unique Elements of a given list of molecule names
            as a List of Element Objects.
    `analyze_molecule`
        Analyse molecule name and return atom name,
            atomic number, and abundance.
    `get_element_names`
        Returns a string List of the names of the given Elements

Classes:
    `Element`
        Chemical element data type
"""
import os

MOLECULE_END = -1
VALUE_ERROR = -2


def get_all_elements():
    """
    Extract all chemical elements from the element.f90 file.

    Returns the element properties as a list of Element objects.
    """
    f90_fname = os.path.join(os.path.dirname(__file__), 'element.f90')
    with open(f90_fname, "r") as f:
        data = f.readlines()
    elements = []
    for line in data:
        if "Elem_type( '" in line:
            items = line.split('(')[1].split(')')[0].split(',')
            items = [item.replace('\'', '').strip() for item in items]
            element = Element(*items)
            elements.append(element)
    return elements


def get_unique_atoms(molecule_list, elements):
    """
    Returns all unique Elements of a given list of molecule names
    as a List of Element Objects.

    :param molecule_list: string list of molecule names
    :param elements: list of all elements, as returned by get_all_elements()

    EXAMPLE:
        get_unique_atoms(molecules, get_all_elements())
    """
    unique_atoms = []
    for molecule in molecule_list:
        if molecule == "":
            unique_atoms.append("")
            continue
        molec = [molecule.strip()]
        while True:
            molec = analyze_molecule(molec[0], get_element_names(elements))
            if molec == MOLECULE_END:
                break
            elif molec == VALUE_ERROR:
                raise ValueError

            if elements[molec[2]] not in unique_atoms:
                unique_atoms.append(elements[molec[2]])
    return unique_atoms


def analyze_molecule(molecule, elements_short):
    """
    Analyze the molecule name and extract the name, atomic number, and
    abundance of the first atom referenced. Return the molecule name minus
    the first atom.

    :param molecule: molecule name (string) e.g. "SiO2"
    :param elements_short: list of all short names of all elements.
        e.g. [H, HE, LI, BE, ...]

    :return: tuple of molecule name minus first element, element name,
                      index and abundance

    EXAMPLE:
        analyze_molecule(molecule, get_element_names(get_all_elements()))
    """
    ele = ""
    nabund = 0
    k = 0

    if len(molecule) > k:
        if molecule[k].isalpha() and molecule[k].isupper():
            ele += molecule[k]
            k += 1
        else:
            return VALUE_ERROR
    else:
        return MOLECULE_END

    if len(molecule) > k:
        if molecule[k].isalpha() and molecule[k].islower():
            ele += molecule[k]
            k += 1
    else:
        return molecule[k:], ele, elements_short.index(ele.upper()), 1

    if len(molecule) > k:
        if molecule[k].isnumeric():
            while len(molecule) > k and molecule[k].isnumeric():
                nabund = nabund * 10 + int(molecule[k])
                k += 1
            return molecule[k:], ele, elements_short.index(ele.upper()), nabund
        else:
            return molecule[k:], ele, elements_short.index(ele.upper()), 1
    else:
        return molecule[k:], ele, elements_short.index(ele.upper()), 1


def get_element_names(elements):
    """
    Return the short name for each element in a list.

    :param elements: elements (Element object list)

    :return: string list of short element names

    EXAMPLE:
        get_element_names(get_all_elements())
    """
    ele_list = []
    for element in elements:
        ele_list.append(element.name)
    return ele_list


class Element:
    """
    Element data type.

    """

    def __init__(self, name, mass1, mass2, dens, name1, name2, t_debye, esurf):
        """
        Initialization of Element

        :param name: short name of the element
        :param mass1: mass
        :param mass2: mass
        :param dens: density
        :param name1: long name
        :param name2: alternative long name
        :param t_debye: Debye temperature
        :param esurf: surface binding energy
        """

        self.name = name
        self.mass1 = mass1
        self.mass2 = mass2
        self.dens = dens
        self.name1 = name1
        self.name2 = name2
        self.t_debye = t_debye
        self.esurf = esurf

    def print_element(self):
        """
        Prints all the attributes.
        """
        print(str(self.name) + ", " + str(self.mass1) + ", "
              + str(self.mass2) + ", " + str(self.dens) + ", "
              + str(self.name1) + ", " + str(self.name2) + ", "
              + str(self.t_debye) + ", " + str(self.esurf))
