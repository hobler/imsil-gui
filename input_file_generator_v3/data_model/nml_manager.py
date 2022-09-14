"""
    Module for creation of f90 Namelist files.
"""
import f90nml


def create_nml(parameter_data):

    nml = f90nml.namelist.Namelist()

    for tab_name in parameter_data:
        tab_nml = f90nml.namelist.Namelist()
        for p_entry in parameter_data[tab_name]:
            p_name = p_entry.get_name()
            p_value = p_entry.get_value()
            p_default_value = p_entry.get_default_value()
            p_type = p_entry.get_type()

            if p_value == p_default_value:
                continue

            if p_entry.get_is_index_var():
                continue # TODO index variable stuff
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
                print(p_type)

            tab_nml[p_name] = p_value
        nml[tab_name] = tab_nml

    return nml


def create_parameter_data(nml, parameter_data):
    pass


def save_nml(nml, path):
    with open(path, 'w') as nml_file:
        f90nml.write(nml, nml_file)


def load_nml(path):
    with open(path) as nml_file:
        nml = f90nml.read(nml_file)
        return nml
