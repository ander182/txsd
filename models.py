# -*- coding: utf-8 -*-


class XSSimpleType(object):

    def __init__(self, name=None, documentation=''):
        super().__init__()
        self.available_restriction_map = {}
        self.multiple_fields = []

        self.name = name
        self.documentation = documentation

    def init_restriction(self, field_name, key, multiple=False):
        assert isinstance(field_name, str)
        assert isinstance(key, str)
        setattr(self, field_name, [] if multiple else None)
        self.available_restriction_map[key] = field_name
        if multiple:
            self.multiple_fields.append(field_name)


class XSStringType(XSSimpleType):

    def __init__(self, name=None, documentation=''):
        super().__init__(name=name, documentation=documentation)

        self.init_restriction('length', 'length')
        self.init_restriction('min_length', 'minLength')
        self.init_restriction('max_length', 'maxLength')
        self.init_restriction('enumeration', 'enumeration', multiple=True)


class XSBaseNumericType(XSSimpleType):

    def __init__(self, name=None, documentation=''):
        super().__init__(name=name, documentation=documentation)

        self.init_restriction('total_digits', 'totalDigits')

        self.init_restriction('min_inclusive', 'minInclusive')
        self.init_restriction('max_inclusive', 'maxInclusive')
        self.init_restriction('min_exclusive', 'minExclusive')
        self.init_restriction('max_exclusive', 'maxExclusive')


class XSIntegerType(XSBaseNumericType):

    def __init__(self, name=None, documentation=''):
        super().__init__(name=name, documentation=documentation)


class XSDecimalType(XSBaseNumericType):

    def __init__(self, name=None, documentation=''):
        super().__init__(name=name, documentation=documentation)
        self.init_restriction('fraction_digits', 'fractionDigits')


class XSAttribute(object):

    def __init__(self, name, required=False):
        super().__init__()
        self.name = name
        self.required = required

        self.simple_type = None

        self.documentation = None


class XSComplexType(object):
    def __init__(self, name=None):
        super().__init__()
        self.name = name
        self.documentation = ''

        self.attributes = []

        self.sequence = []
        self.choice = []

    def add_attribute(self, attribute):
        assert isinstance(attribute, XSAttribute)
        self.attributes.append(attribute)


class XSElement(object):

    def __init__(self, name=None):
        super().__init__()

        self.name = name
        self.documentation = ''

        self.min_occurs = 1
        # 0 == infinity in max_occurs
        self.max_occurs = 1

        self.complex_type = None

    @property
    def attributes(self):
        return self.complex_type.attributes if self.complex_type else []

    @property
    def sequence(self):
        return self.complex_type.sequence if self.complex_type else []

    @property
    def choice(self):
        return self.complex_type.choice if self.complex_type else []

