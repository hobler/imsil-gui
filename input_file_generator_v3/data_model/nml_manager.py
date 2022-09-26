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
                                        temp[index_vars[0]] = m+1
                                    if array_size[1] > 1:
                                        temp[index_vars[0]] = n+1
                                    else:
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


def create_parameter_data(nml, parameter_data):
    pass


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
        return nml
