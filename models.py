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

    def __init__(self):
        super().__init__()


class XSStringType(XSSimpleType):

    def __init__(self):
        super().__init__()
        self.min_length = None
        self.max_length = None


class XSIntegerType(XSSimpleType):

    def __init__(self):
        super().__init__()
        self.totalDigits = None


class XSComplexType(object):
    def __init__(self, name=None):
        super().__init__()
        self.name = name

