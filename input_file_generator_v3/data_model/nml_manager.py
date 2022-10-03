"""
    Module for creation of f90 Namelist files.
"""
import f90nml

from utility import get_size_string


def create_nml(parameter_data):
    """
    Creates a Namelist Object that can be used to save the parameter_data
    into a file.

    :param parameter_data: ParameterData object to save

    :return: Resulting Namelist object
    """

    # resulting Namelist object
    nml = f90nml.namelist.Namelist()
    nml.false_repr = 'f'
    nml.true_repr = 't'

    # dictionary that stores the IVArrays. Used because IVArrays need to be
    # written into the Namelist file differently than normal values.
    #
    # An IVArray with n entries uses n different Namelists, which are written
    # into the main Namelist as a list of Namelist objects.
    iva_nml_dict = dict()

    # for each tab in the parameter data.
    for tab_name in parameter_data:
        # create a list which will store the normal Parameters as a single
        # Namelist and then other Namelists depending on the amount and
        # size of the IVArrays.
        nml[tab_name] = []
        # tab namelist for only the normal parameters
        tab_nml = f90nml.namelist.Namelist()

        # loop over every parameter in this tab
        for p_entry in parameter_data[tab_name]:
            p_name = p_entry.get_name()
            p_value = p_entry.get_value()
            p_default_value = p_entry.get_default_value()
            p_type = p_entry.get_type()

            # don't save parameters that have the default value
            if p_value == p_default_value:
                continue

            # special case of IVArrays
            if p_entry.get_is_index_var():

                # using size_string for grouping of the parameters.
                # same size_String means same namelist object
                index_vars = p_entry.get_index_vars()
                size_string = str(index_vars)

                # If it doesn't exist, create new dict for storing the namelists
                # before writing them into the file
                if tab_name not in iva_nml_dict:
                    iva_nml_dict[tab_name] = dict()
                    nml[tab_name] = []

                # to determine the correct indexing of all
                # values inside the IVArray
                array_size = p_value.get_size()
                # create new list of Namelist objects if the size_string isn't
                # already in the ivarray dict
                if size_string not in iva_nml_dict[tab_name]:
                    nml_list = []

                    # depending on the length, either create a simple list
                    # for 1D IVArrays or a nested list of lists for 2D IVArrays
                    if len(array_size) == 1:
                        rang = array_size[0]
                        # special case of POS array
                        # (for more info look at iv_data.py)
                        if p_name == "POS":
                            rang = rang - 1
                        # for every value and index create a Namelist and
                        # write the indexing inside it.
                        # for example: an array of ATOM will create n Namelists.
                        # Each with the parameter "atom=i" (i in n) in it.
                        for i in range(rang):
                            temp = f90nml.namelist.Namelist()
                            temp[index_vars[0]] = i+1
                            # save the Namelist in the nml_list for for
                            # accessing and indexing it later
                            # also write it into the actual nml object
                            nml_list.append(temp)
                            nml[tab_name].append(temp)
                    # same as 1D but with extra loop and nested lists
                    elif len(array_size) == 2:
                        for m in range(array_size[0]):
                            nml_sub_list = []
                            for n in range(array_size[1]):
                                temp = f90nml.namelist.Namelist()

                                if len(index_vars) == 2:
                                    temp[index_vars[0]] = m+1
                                    temp[index_vars[1]] = n+1
                                else:
                                    if array_size[0] > 1:
                                        # points is 0 indexed
                                        if p_name == "POINTS":
                                            m -= 1
                                        temp[index_vars[0]] = m+1
                                    if array_size[1] > 1:
                                        temp[index_vars[0]] = n+1
                                    if array_size[0] == 1 and array_size[1] == 1:
                                        temp[index_vars[0]] = 1
                                nml_sub_list.append(temp)
                                nml[tab_name].append(temp)
                            nml_list.append(nml_sub_list)

                    # store the nml_list in the temporary ivarray dict
                    # so that it can be accessed later
                    iva_nml_dict[tab_name][size_string] = nml_list

                # Here the values of the IVArray are written into the Namelists
                # The Namelists are accessed by indexing into the ivarray dict.
                # The values are accessed by the same index via the
                # get_value method from IVData
                # Depending on the p_type, the values are parsed from string.
                if len(array_size) == 1:
                    rang = array_size[0]
                    if p_name == "POS":
                        rang = rang - 1
                    for i in range(rang):
                        index = i
                        if p_name == "POS":
                            index = i + 1
                        value = p_value.get_value(index, None)
                        if value != "":
                            if p_type.endswith("logical"):
                                value = (value == "T")
                            elif p_type.endswith("simple array (2) of real"):
                                values = value
                                value = []
                                for v in values.split(","):
                                    value.append(float(v.strip()))
                            elif p_type.endswith("real"):
                                value = float(value)
                            elif p_type.endswith("integer"):
                                value = int(value)
                            iva_nml_dict[tab_name][size_string][i][p_name] = value
                elif len(array_size) == 2:
                    for m in range(array_size[0]):
                        for n in range(array_size[1]):
                            value = p_value.get_value(m, n)
                            if value != "":
                                if p_type.endswith("logical"):
                                    value = (value == "T")
                                elif p_type.endswith("simple array (2) of real"):
                                    values = value
                                    value = []
                                    for v in values.split(","):
                                        value.append(float(v.strip()))
                                elif p_type.endswith("real"):
                                    value = float(value)
                                elif p_type.endswith("integer"):
                                    value = int(value)
                                iva_nml_dict[tab_name][size_string][m][n][p_name] = value

                continue  # ivarrays are already written into the nml list

            # other types. Parse the values according to the p_type
            elif p_type == "logical":
                p_value = (p_value == "T")
            elif p_type == "real":
                p_value = float(p_value)
            elif p_type == "integer":
                p_value = int(p_value)
            elif p_type == "character string":
                pass
            elif p_type.startswith("character("):  # TODO maybe check here
                pass
            elif p_type.startswith("simple array"):
                if p_type.endswith("integer"):
                    values = p_value
                    p_value = []
                    for value in values.split(","):
                        p_value.append(int(value.strip()))
                elif p_type.endswith("real"):
                    values = p_value
                    p_value = []
                    for value in values.split(","):
                        p_value.append(float(value.strip()))
                elif p_type.endswith("logical"):
                    values = p_value
                    p_value = []
                    if len(values) >= 3:
                        for value in values[1:-1].split(","):
                            p_value.append(value.strip() == "T")
                    else:
                        print("Logic array of 2 has wrong "
                              "string representation.")
                        continue
            elif p_type.startswith("character array"):
                if len(p_value) >= 2:
                    p_value = p_value[1:-1]
                else:
                    print("String too short.")
                    continue
            else:
                print(p_type, "missing")

            # write the parsed parameter value into the Namelist for this tab
            tab_nml[p_name] = p_value
        if tab_nml:
            nml[tab_name].append(tab_nml)

    # delete empty namelists
    for tab_name in parameter_data:
        for nl in reversed(nml[tab_name]):
            if not nl:
                del nml[tab_name][nml[tab_name].index(nl)]
            else:
                # if namelist only contains indexes of
                # region/atom it can be deleted
                hasother = False
                ind_vars = ["atom", "atom1", "atom2", "region", "point"]

                for key in nl.keys():
                    if key not in ind_vars:
                        hasother = True
                        break

                if not hasother:
                    del nml[tab_name][nml[tab_name].index(nl)]

    return nml


def load_nml_to_parameter_data(parameter_data, nml):
    """
    Writes the parameters from the loaded Namelist file into the ParameterData
    object of the application.

    :param parameter_data: ParameterData object to load the data into
    :param nml: Loaded Namelist file
    """

    # reset all values in the ParameterData
    parameter_data.reset()

    # get the default nr and natom
    natom = int(parameter_data.get_natom())
    nr = int(parameter_data.get_nr())

    # read the correct NR and NATOM from the Namelist file and correct the
    # values in the ParameterData object
    if "setup" in nml:
        if "natom" in nml["setup"]:
            # add the remaining atoms
            natom = nml["setup"]["natom"] - natom
            for a in range(natom):
                parameter_data.add_atom()
        if "nr" in nml["setup"]:
            # add the remaining regions
            nr = nml["setup"]["nr"] - nr
            for r in range(nr):
                parameter_data.add_region()

    # preallocate the array for POS
    # 1 extra value for the hidden entry field
    # because the POS array is stored "as-is" in the IVData
    n_points = 1
    if "geom" in nml:
        for sub_nml in nml["geom"]:
            if "pos" in sub_nml:
                n_points += 1
        # add the extra POS entries
        p_entry = parameter_data.get_entry("geom", "POS")
        ivdata = p_entry.get_value()
        ivdata.values = []
        for i in range(n_points):
            ivdata.values.append('')
        # This has to be written so that the values are correctly written into
        # the entry fields when expanding the array
        ivdata.values[0] = 'Multiple values'

    # for every namelist or list of namelists add the contained
    # parameters to ParameterData
    for tab_name in parameter_data:
        if tab_name in nml:
            # list of namelists
            if type(nml[tab_name]) == list:
                for sub_nml in nml[tab_name]:
                    load_tab_nml_to_parameter_data(parameter_data,
                                                   sub_nml,
                                                   tab_name)
            # normal namelist
            else:
                load_tab_nml_to_parameter_data(parameter_data,
                                               nml[tab_name],
                                               tab_name)


def load_tab_nml_to_parameter_data(parameter_data, sub_nml, tab_name):
    """
    Writes the parameters from the loaded Namelist file tab into the ParameterData
    object of the application.

    :param parameter_data: ParameterData object to load the data into
    :param sub_nml: Sub Namelist in the loaded Namelist file
    :param tab_name: Tab name of the tab that contains the
        parameters of this Namelist
    """
    # if any key in the nml is one of the ones in the string list,
    # it's an IVArray.
    index_variables = [i for i in ["atom", "atom1",
                                   "atom2", "region", "point"] if i in sub_nml]
    if index_variables:
        # 2D arrays
        if len(index_variables) == 2:
            # every key in the sub_nml that is not in the
            # index_variables is a parameter name
            for p_name in [i for i in sub_nml if i not in index_variables]:
                # get the corresponding ParameterEntry
                p_entry = parameter_data.get_entry(tab_name, p_name.upper())
                p_type = p_entry.get_type()
                # get the original index_variables, because
                # index_variables is unordered
                # (probably alphabetically instead of the
                # real order of keys from the database)
                index_vars_orig = p_entry.get_index_vars()

                # get the indexes for the value
                m = sub_nml[index_vars_orig[0]] - 1
                n = sub_nml[index_vars_orig[1]] - 1

                # get the IVData object that holds the data of this parameter
                ivdata = p_entry.get_value()

                # convert to string according to correct datatype
                string = convert_nml_value_to_string(p_type, sub_nml[p_name])

                # set the value on the given index
                ivdata.set_value(string, m, n)

        # 1D arrays
        elif len(index_variables) == 1:
            # same as 2D
            for p_name in [i for i in sub_nml if i not in index_variables]:

                p_entry = parameter_data.get_entry(tab_name, p_name.upper())
                p_type = p_entry.get_type()
                index_vars_orig = p_entry.get_index_vars()

                string = convert_nml_value_to_string(p_type, sub_nml[p_name])

                ivdata = p_entry.get_value()
                array_size = ivdata.get_size()

                # 1D arrays can be opened in x or y direction
                # depending on the array_size
                if len(array_size) == 2:
                    if array_size[0] > 1:

                        m = sub_nml[index_vars_orig[0]] - 1
                        if p_name == "points":
                            m += 1
                        ivdata.set_value(string, m, 0)
                    elif array_size[1] > 1:
                        n = sub_nml[index_vars_orig[0]] - 1
                        ivdata.set_value(string, 0, n)
                    # 1x1 array
                    else:
                        ivdata.set_value(string, 0, 0)
                # POS array
                else:
                    i = sub_nml[index_vars_orig[0]]
                    ivdata.set_value(string, i, None)
    # all the other types
    else:
        for p_name in sub_nml:
            p_entry = parameter_data.get_entry(tab_name, p_name.upper())
            p_type = p_entry.get_type()

            # other types. Parse the values according to the p_type
            string = convert_nml_value_to_string(p_type, sub_nml[p_name])
            p_entry.set_value(string)


def convert_nml_value_to_string(p_type, value):
    """
    Converts a "simple array" value to a string representation

    :param p_type: Parameter type
    :param value: value array
    """
    string = ""

    if p_type == "logical":
        string = "T" if value else "F"
    elif p_type == "real":
        string = str(value)
    elif p_type == "integer":
        string = str(value)
    elif p_type == "character string":
        string = str(value)
    elif p_type.startswith("character("):  # TODO maybe check here
        string = str(value)
    elif p_type.startswith("simple array"):
        string = array_to_string(p_type, value)
    elif p_type.startswith("character array"):
        string = str(value)
    elif p_type.startswith("index variable"):
        if "simple array" in p_type:
            values = value
            string = ", ".join([str(value) for value in values])
        elif p_type.endswith("logical"):
            string = ("T" if value else "F")
        elif p_type.endswith("real"):
            string = str(value)
        elif p_type.endswith("integer"):
            string = str(value)
        else:
            string = str(value)
    else:
        print(p_type, "missing")

    return string


def array_to_string(p_type, value):
    """
    Converts a "simple array" value to a string representation

    :param p_type: Parameter type
    :param value: value array
    """
    string = ""
    if p_type.endswith("integer") or p_type.endswith("real"):
        values = value
        string = ", ".join([str(value) for value in values])
    elif p_type.endswith("logical"):
        values = value
        if len(values) == 2:
            string = "("
            string += ",".join(["T" if value else "F"
                                for value in values])
            string += ")"
        else:
            print("Logic array of 2 has wrong "
                  "string representation.")
    return string


def save_nml(nml, path):
    """
    Saves the Namelist object into a file.

    :param nml: Namelist file.
    :param path: Path for the resulting file.
    """
    with open(path, 'w') as nml_file:
        f90nml.write(nml, nml_file)


def load_nml(path):
    """
    Loads a Namelist Object from a given Namelist file.

    :param path: Path to the file.

    :return: Resulting Namelist object
    """
    with open(path) as nml_file:
        nml = f90nml.read(nml_file)
        nml.false_repr = 'f'
        nml.true_repr = 't'
        return nml
