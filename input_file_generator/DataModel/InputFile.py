import f90nml


class InputFile:
    """
    This class use the f90nml module to read an Fortran namelist file.

    :get_parameters: return all parameters for the given key name.
    """

    def __init__(self, file_path):
        self.file = f90nml.read(file_path)

    def get_parameters(self, key_name):
        if key_name in self.file.keys():
            return self.file[key_name]
        else:
            return None
