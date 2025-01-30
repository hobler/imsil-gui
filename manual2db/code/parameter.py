class Parameter:
    """Class that represents input parameters for IMSIL.

    Attributes:
        record (str): represents the associated table in the db (e.g. SETUP)
        name (str): Name of the input parameter (e.g TILT)
        short_desc (str): Short description of the input parameter
        long_desc (str): Long description of the input parameter
        type (str): Type of the input parameter (e.g. real)
        default_value (str): Default value of the parameter (e.g. 0)
        range (str): Range (e.g. 0 < TILT < 90)
        condition (str): String condition for validation, based on range value
    """

    def __init__(self, record, name, short_desc, long_desc, type, default_value,
                 range, condition):
        self.record = record
        self.name = name
        self.short_desc = short_desc
        self.long_desc = long_desc
        self.type = type
        self.defaultValue = default_value
        self.range = range
        self.condition = condition

    def get_dict(self):
        """Generate dictionary with all attributes of the parameter

        Is used for formatting the sql query for writing parameters to the
        database.
        """

        p_dict = {'name': self.name,
                  'short_desc': self.short_desc,
                  'long_desc': self.long_desc,
                  'type': self.type,
                  'defaultValue': self.defaultValue,
                  'range': self.range,
                  'condition': self.condition
                 }
        return p_dict
