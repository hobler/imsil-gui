import f90nml


class InputFile:
    """
    This class use the f90nml module to read a Fortran namelist file.

    :get_parameters: return all parameters for the given key name.
    """

    def __init__(self, file_path):
        self.nml = f90nml.read(file_path)

    def get_parameters(self, record_name):
        if record_name in self.nml.keys():
            return self.nml[record_name]
        else:
            return None
