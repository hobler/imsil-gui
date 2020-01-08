import f90nml


class InputFile:
    def __init__(self, file_path):
        self.file = f90nml.read(file_path)

    def get_parameters(self, key_name):
        if key_name in self.file.keys():
            return self.file[key_name]
        else:
            return None
