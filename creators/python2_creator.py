# coding:utf-8
import copy

from models import XSElement


class TranslitMixin(object):

    @staticmethod
    def translit(local_lang_string):
        conversion = {
            u'\u0410': 'A', u'\u0430': 'a',
            u'\u0411': 'B', u'\u0431': 'b',
            u'\u0412': 'V', u'\u0432': 'v',
            u'\u0413': 'G', u'\u0433': 'g',
            u'\u0414': 'D', u'\u0434': 'd',
            u'\u0415': 'E', u'\u0435': 'e',
            u'\u0401': 'Yo', u'\u0451': 'yo',
            u'\u0416': 'Zh', u'\u0436': 'zh',
            u'\u0417': 'Z', u'\u0437': 'z',
            u'\u0418': 'I', u'\u0438': 'i',
            u'\u0419': 'Y', u'\u0439': 'y',
            u'\u041a': 'K', u'\u043a': 'k',
            u'\u041b': 'L', u'\u043b': 'l',
            u'\u041c': 'M', u'\u043c': 'm',
            u'\u041d': 'N', u'\u043d': 'n',
            u'\u041e': 'O', u'\u043e': 'o',
            u'\u041f': 'P', u'\u043f': 'p',
            u'\u0420': 'R', u'\u0440': 'r',
            u'\u0421': 'S', u'\u0441': 's',
            u'\u0422': 'T', u'\u0442': 't',
            u'\u0423': 'U', u'\u0443': 'u',
            u'\u0424': 'F', u'\u0444': 'f',
            u'\u0425': 'H', u'\u0445': 'h',
            u'\u0426': 'Ts', u'\u0446': 'ts',
            u'\u0427': 'Ch', u'\u0447': 'ch',
            u'\u0428': 'Sh', u'\u0448': 'sh',
            u'\u0429': 'Sch', u'\u0449': 'sch',
            u'\u042a': '', u'\u044a': '',
            u'\u042b': 'Y', u'\u044b': 'y',
            u'\u042c': '', u'\u044c': '',
            u'\u042d': 'E', u'\u044d': 'e',
            u'\u042e': 'Yu', u'\u044e': 'yu',
            u'\u042f': 'Ya', u'\u044f': 'ya',
        }
        translit_string = []
        for c in local_lang_string:
            translit_string.append(conversion.setdefault(c, c))
        return ''.join(translit_string).replace('.', '_').replace('-', '_')


class PyCreator(object):

    def __init__(self, xs_elements=None):
        super().__init__()
        self.xs_elements = xs_elements or []

    @staticmethod
    def get_header():
        return '# coding:utf-8\n' +\
        'from __future__ import unicode_literals\n\n\n'

    def make(self, result_file):
        result_file.write(self.get_header())
        for xs_element in self.xs_elements:
            if not xs_element.complex_type.name:
                cls_builder = ClassBuilder(xs_element)
                result_file.write(cls_builder.build_cls())


class ClassBuilder(TranslitMixin):

    def __init__(self, el):
        super().__init__()
        self.el = el

        self.attrib_names = {}
        for attrib in el.complex_type.attributes:
            self.attrib_names[attrib.name] = self.translit(attrib.name)
        self.sequence_names = {}
        for seq in el.complex_type.sequence:
            self.sequence_names[seq.name] = self.translit(seq.name)
        self.choice_names = {}
        for choice in el.complex_type.choice:
            self.choice_names[choice.name] = self.translit(choice.name)

    @property
    def all_names(self):
        _ = {}
        _.update(self.attrib_names)
        _.update(self.sequence_names)
        _.update(self.choice_names)
        return _

    @staticmethod
    def add_row(row, level=0):
        return '    '*level + row + '\n'

    def build_cls(self):
        result = ''

        class_name = self.translit(self.el.name)
        result += 'class {}(object):\n\n'.format(class_name)
        result += self.build_init()
        result += self.build_setters()

        result += '\n'
        return result

    def build_init(self):
        raw_params = self.all_names
        trans_params = raw_params.values()
        params_list = ['{}=None'.format(param) for param in trans_params]
        result = self.add_row('def __init__(self, {}):'.format(', '.join(params_list)), level=1)
        for param in trans_params:
            result += self.add_row('self.{0} = {0}'.format(param), level=2)
        result += '\n'

        return result

    def build_setters(self):
        result = ''
        for param in (self.el.complex_type.attributes + self.el.complex_type.sequence):
            result += self.add_row('def set_{}(self, value=None):'.format(self.all_names.get(param.name)), 1)
            result += self.add_row('self.{} = value'.format(self.all_names.get(param.name)), 2)
            result += '\n'

        for choice in self.el.complex_type.choice:
            result += self.add_row('def set_{}(self, value=None):'.format(self.all_names.get(choice.name)), 1)
            result += self.add_row('self.{} = value'.format(self.all_names.get(choice.name)), 2)
            other_choices = filter(lambda x: x.name != choice.name, copy.deepcopy(self.el.complex_type.choice))
            result += self.add_row('if value:', 2)
            for choice_to_clear in other_choices:
                result += self.add_row('self.{} = None'.format(self.all_names.get(choice_to_clear.name)), 3)
            result += '\n'
        return result
