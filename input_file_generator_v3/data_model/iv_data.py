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
