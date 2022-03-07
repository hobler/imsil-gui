"""
Data structures to hold and modify the data in the IVArrays.

Classes:
    `IVDict`
        Dictionary object for IVData with methods to
        add and remove region and atom entries.
    `IVData`
        Datatype to re-create and re-fill the same
        IndexVariableArray along with some helper-functions.
"""
from utility import get_size_string


class IVDict(dict):
    """
    Dictionary object for IVData with methods to
    add and remove region and atom entries.
    Inherits from dict.
    """
    def add_atom(self):
        """
        Adds an Atom to every IVArray
        """
        for tab in self:
            # for all index variable arrays in that tab
            for ivdata in self[tab]:
                ivdata.add_atom()

    def add_region(self):
        """
        Adds a Region to every IVArray
        """
        for tab in self:
            # for all index variable arrays in that tab
            for ivdata in self[tab]:
                ivdata.add_region()

    def add_atom_at(self, index):
        """
        Adds an Atom to every IVArray at a given position

        :param index: index
        """
        for tab in self:
            # for all index variable arrays in that tab
            for ivdata in self[tab]:
                ivdata.add_atom_at(index)

    def add_region_at(self, index):
        """
        Adds a Region to every IVArray at a given position

        :param index: index
        """
        for tab in self:
            # for all index variable arrays in that tab
            for ivdata in self[tab]:
                ivdata.add_region_at(index)

    def remove_atom(self, index):
        """
        Removes an Atom from every IVArray at a given position

        :param index: index
        """
        for tab in self:
            # for all index variable arrays in that tab
            for ivdata in self[tab]:
                ivdata.remove_atom(index)

    def remove_region(self, index):
        """
        Removes a Region from every IVArray at a given position

        :param index: index
        """
        for tab in self:
            # for all index variable arrays in that tab
            for ivdata in self[tab]:
                ivdata.remove_region(index)

    def swap_atom(self, index_1, index_2):
        """
        Swap the contents of the atoms at index 1 and 2

        :param index_1: index of the first atom
        :param index_2: index of the second atom
        """
        for tab in self:
            # for all index variable arrays in that tab
            for ivdata in self[tab]:
                ivdata.swap_atom(index_1, index_2)

    def swap_region(self, index_1, index_2):
        """
        Swap the contents of the regions at index 1 and 2

        :param index_1: index of the first regions
        :param index_2: index of the second regions
        """
        for tab in self:
            # for all index variable arrays in that tab
            for ivdata in self[tab]:
                ivdata.swap_region(index_1, index_2)


class IVData:
    """
    Contains all the necessary data to re-create and re-fill an IVArray
    and some methods to add or remove entries
    """

    def __init__(self, size_string, natom, nr, array_state, array_settings):
        """
        Removes a Region from every IVArray at a given position

        :param size_string: size string in the format [1/a/r, 1/a/r]
        :param natom: number of atoms
        :param nr: number of regions
        :param array_state: open/closed state of the array
        :param array_settings: data to re-create the array
        """
        self.size_string = size_string
        self.natom = natom
        self.nr = nr
        self.values = []
        self.array_state = array_state
        self.array_settings = array_settings

    def add_atom(self):
        change = self.add_variable("a")
        if change:
            self.natom += 1

    def add_region(self):
        change = self.add_variable("r")
        if change:
            self.nr += 1

    def add_variable(self, variable):
        """
        Adds a new empty spot for the given variable in the values array.

        :param variable: "a" or "r" for atom or region
        """
        # determines which dimension has to change
        # by looking at which axis depends on the given variable (a or r)
        change_m = self.size_string[0] == variable
        change_n = self.size_string[1] == variable
        pre_m = self.get_m()
        pre_n = self.get_n()

        if not change_m and not change_n:
            return
        else:
            if change_m:
                self.values.append([''] * pre_n)
                pre_m += 1
            if change_n:
                for i in range(0, pre_m):
                    self.values[i].append('')

        return change_n or change_m

    def add_atom_at(self, index):
        change = self.add_variable_at("a", index)
        if change:
            self.natom += 1

    def add_region_at(self, index):
        change = self.add_variable_at("r", index)
        if change:
            self.nr += 1

    def add_variable_at(self, variable, index):
        """
        Adds a new empty spot for the given variable
        in the values array at the given position.

        :param variable: "a" or "r" for atom or region
        :param index: Position for the new variable
        """
        # determines which dimension has to change
        # by looking at which axis depends on the given variable (a or r)
        change_m = self.size_string[0] == variable
        change_n = self.size_string[1] == variable
        pre_m = self.get_m()
        pre_n = self.get_n()

        if not change_m and not change_n:
            return
        else:
            if change_m:
                self.values.insert(index, [''] * pre_n)
                pre_m += 1
            if change_n:
                for i in range(0, pre_m):
                    self.values[i].insert(index, '')

        return change_n or change_m

    def remove_atom(self, index):
        change = self.remove_variable("a", index)
        if change:
            self.natom -= 1

    def remove_region(self, index):
        change = self.remove_variable("r", index)
        if change:
            self.nr -= 1

    def remove_variable(self, variable, index):
        """
        Removes a variable from the array at the given index

        :param variable: "a" or "r" for atom or region
        :param index: Delete Position

        :return: Flag indicating whether array has changed
        """
        # determine which dimension has to change by looking at which axis
        # depends on the given variable ("a" or "r")
        change_m = (self.size_string[0] == variable)
        change_n = (self.size_string[1] == variable)
        pre_m = self.get_m()

        if not change_m and not change_n:
            return
        else:
            if change_m:
                del self.values[index]
                pre_m -= 1
            if change_n:
                for i in range(0, pre_m):
                    del self.values[i][index]

        return change_n or change_m

    def swap_atom(self, index_1, index_2):
        self.swap_variable("a", index_1, index_2)

    def swap_region(self, index_1, index_2):
        self.swap_variable("r", index_1, index_2)

    def swap_variable(self, variable, index_1, index_2):
        """
        Swaps content of 2 given variables

        :param variable: "a" or "r" for atom or region
        :param index_1: variable index 1
        :param index_2: variable index 1

        """
        change_m = (self.size_string[0] == variable)
        change_n = (self.size_string[1] == variable)
        pre_m = self.get_m()

        if not change_m and not change_n:
            return
        else:
            if change_m:
                temp = self.values[index_1]
                self.values[index_1] = self.values[index_2]
                self.values[index_2] = temp
            if change_n:
                for i in range(0, pre_m):
                    temp = self.values[i][index_1]
                    self.values[i][index_1] = self.values[i][index_2]
                    self.values[i][index_2] = temp

    def get_m(self):
        """
        Return the size of the m x n index variable array in m direction.

        :return: m
        """
        if self.size_string[0] == "a":
            return self.natom
        else:
            if self.size_string[0] == "r":
                return self.nr
            else:
                return 1

    def get_n(self):
        """
        Return the size of the m x n index variable array in n direction.

        :return: n
        """
        if self.size_string[1] == "a":
            return self.natom
        else:
            if self.size_string[1] == "r":
                return self.nr
            else:
                return 1

    def print_data(self):
        """
        Prints all available data of the array.
        """
        print("nr: " + str(self.nr))
        print("natom: " + str(self.natom))
        print("size_string: " + str(self.size_string))
        print("array_state: " + str(self.array_state))
        print("array_settings: " + str(self.array_settings))

        # special case of POS array
        if self.size_string[0] == "0":
            print(self.values)
        else:
            for m in range(self.get_m()):
                for n in range(self.get_n()):
                    print(self.values[m][n])

    def to_list(self):
        """
        return the values as a list.

        :return: list of values.
        """
        values = []
        # special case of POS array
        if self.size_string[0] == "0":
            return self.values
        else:
            for m in range(self.get_m()):
                for n in range(self.get_n()):
                    values.append(self.values[m][n])

        return values

    @staticmethod
    def create_iv_data_from_list(values, parameter_entry, nr, natom):
        """
        Create and return an IVData object, based on a list of values.
        Structure of the IV Array is provided
        with the parameter_entry, nr and natom.

        :param values: value list, has to be the right size.
            Size depends on size_string, nr and natom
        :param parameter_entry: ParameterEntry object
        :param nr: number of regions
        :param natom: number of atoms

        :return: IVData representation
        """
        # copy previous data
        size_string = get_size_string(parameter_entry.get_name(),
                                      parameter_entry.get_index_vars())
        array_settings = (parameter_entry.get_name(),
                          parameter_entry.get_index_vars(),
                          parameter_entry.get_default_value(),
                          parameter_entry.get_short_desc(),
                          parameter_entry.get_long_desc())
        ivdata = IVData(size_string, natom, nr, (False, False), array_settings)
        # fill new values into array
        m = ivdata.get_m()
        n = ivdata.get_n()
        for i in range(m * n):
            if i % n == 0:
                ivdata.values.append([])
            ivdata.values[i // n].append(values[i])
        return ivdata
