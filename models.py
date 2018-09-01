# -*- coding: utf-8 -*-


class Element(object):

    def __init__(self):
        super().__init__()

        self.childs = []
        self.multiple_childs = []
        self.choise_childs = []

        self.attributes = []
        self.required_attributes = []

        self.annotation = None


class XSAttribute(object):

    def __init__(self, name, required=False):
        super().__init__()
        self.name = name
        self.required = required

        self.xs_type = None

        self.annotation = None


class XSSimpleType(object):

    def __init__(self, name=None, documentation=''):
        super().__init__()
        self.name = name
        self.documentation = documentation


class XSStringType(XSSimpleType):

    def __init__(self, name=None, documentation=''):
        super().__init__(name=name, documentation=documentation)
        self.length = None
        self.min_length = None
        self.max_length = None


class XSBaseNumericType(XSSimpleType):

    def __init__(self, name=None, documentation=''):
        super().__init__(name=name, documentation=documentation)
        self.total_digits = None

        self.min_inclusive = None
        self.max_inclusive = None
        self.min_exclusive = None
        self.max_exclusive = None


class XSIntegerType(XSBaseNumericType):

    def __init__(self, name=None, documentation=''):
        super().__init__(name=name, documentation=documentation)


class XSDecimalType(XSBaseNumericType):

    def __init__(self, name=None, documentation=''):
        super().__init__(name=name, documentation=documentation)
        self.fraction_digits = None


class XSComplexType(object):
    def __init__(self, name=None):
        super().__init__()
        self.name = name

