class Element(object):

    def __init__(self):
        super()

        self.childs = []
        self.multiple_childs = []
        self.choise_childs = []

        self.attributes = []
        self.required_attributes = []

        self.annotation = None

class XSAttribute(object):

    def __init__(self, name, required=False):
        super()
        self.name = name
        self.required = required

        self.xs_type = None

        self.annotation = None


class XSSimpleType(object):

    def __init__(self):
        super()


class XSStringType(XSSimpleType):

    def __init__(self):
        self.min_length = None
        self.max_length = None


class XSIntegerType(XSSimpleType):

    def __init__(self):
        self.totalDigits = None


class XSComplexType(object):
    def __init__(self, name=None):
        super()
        self.name = name
        
