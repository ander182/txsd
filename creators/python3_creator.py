import copy

from creators.mixins import TranslitMixin
from models import XSElement, XSBaseNumericType


class Py3Creator(object):

    def __init__(self, xs_elements=None):
        super().__init__()
        self.xs_elements = xs_elements or []

    @staticmethod
    def get_header():
        return 'class BaseRepresent(object):\n' \
               '    def __init__(self):\n' \
               '        super().__init__()\n\n' \
               '    def export_children(self, *args, **kwargs):\n' \
               '        pass\n\n' \
               '    def quote_xml(self, inStr):\n' \
               '        if not inStr:\n' \
               '            return ""\n' \
               '        s1 = (isinstance(inStr, str) and inStr or "%s" % inStr)\n' \
               '        s1 = s1.replace("&", "&amp;")\n' \
               '        s1 = s1.replace("<", "&lt;")\n' \
               '        s1 = s1.replace(">", "&gt;")\n' \
               '        return s1\n\n' \
               '    def quote_attrib(self, inStr):\n' \
               '        s1 = (isinstance(inStr, str) and inStr or "%s" % inStr)\n' \
               '        s1 = s1.replace("&", "&amp;")\n' \
               '        s1 = s1.replace("<", "&lt;")\n' \
               '        s1 = s1.replace(">", "&gt;")\n' \
               '        s1 = s1.replace("\\\"", "&quot;")\n' \
               '        return s1\n\n\n'

    def make(self, result_file):
        result_file.write(self.get_header())
        complex_type_for_build = []
        used_names = {}
        for xs_element in self.xs_elements:
            if not xs_element.complex_type.name:
                if xs_element.name in used_names:
                    class_index = used_names.get(xs_element.name)
                else:
                    class_index = None
                cls_builder = CommonClassBuilder(xs_element, xs_element.complex_type, class_index=class_index)
                result_file.write(cls_builder.build_cls())
                used_names[xs_element.name] = class_index + 1 if class_index is not None else 1
            elif xs_element.complex_type not in complex_type_for_build:
                complex_type_for_build.append(xs_element.complex_type)
        for complex_type in complex_type_for_build:
            cls_builder = CommonClassBuilder(complex_type, complex_type)
            result_file.write(cls_builder.build_cls())


class CommonClassBuilder(TranslitMixin):

    def __init__(self, el, complex_type, class_index=None):
        super().__init__()
        self.el = el
        self.complex_type = complex_type
        self.class_name = ''
        self.class_name_index = class_index

        self.attrib_names = {}
        for attrib in el.attributes:
            self.attrib_names[attrib.name] = self.translit(attrib.name)
        self.sequence_names = {}
        for seq in el.sequence:
            self.sequence_names[seq.name] = self.translit(seq.name)
        self.choice_names = {}
        for choice in el.choice:
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

        self.class_name = self.translit(self.el.name)
        result += 'class {}{}(BaseRepresent):\n\n'.format(self.class_name, self.class_name_index or '')
        result += self.build_init()
        result += self.build_setters()
        result += self.build_has_children()
        result += self.build_has_content()
        result += self.build_export()
        result += self.build_export_attrs()
        result += self.build_export_children()
        result += '\n'
        return result

    def build_init(self):
        trans_params = self.all_names.values()
        params_list = ['{}=None'.format(param) for param in trans_params]
        result = self.add_row('def __init__(self, {}):'.format(', '.join(params_list)), level=1)
        result += self.add_row('super().__init__()', level=2)
        for param in (self.el.attributes + self.el.sequence + self.el.choice):
            param_name = self.all_names.get(param.name)
            result += self.add_row('self.{0} = {0}{1}'.format(
                param_name,
                ' or []' if isinstance(param, XSElement) and param.max_occurs != 1 else ''
            ), level=2)
        result += '\n'

        return result

    def build_setters(self):
        result = ''
        for param in (self.el.attributes + self.el.sequence):
            param_name = self.all_names.get(param.name)
            result += self.add_row('def set_{}(self, value=None):'.format(param_name), 1)
            result += self.add_row('self.{} = value{}'.format(
                param_name,
                ' or []' if isinstance(param, XSElement) and param.max_occurs != 1 else ''), 2)
            result += '\n'

            if isinstance(param, XSElement) and param.max_occurs != 1:
                result += self.add_row('def add_{}(self, value=None):'.format(param_name), 1)
                if param.max_occurs == 0:
                    result += self.add_row('self.{}.append(value)'.format(param_name), 2)
                else:
                    result += self.add_row('if len(self.{}) < {}:'.format(param_name, param.max_occurs), 2)
                    result += self.add_row('self.{}.append(value)'.format(param_name), 3)
                    result += self.add_row('else:', 2)
                    result += self.add_row('raise RuntimeError("Number of children {} exceeded.")'.format(param_name), 3)
                result += '\n'

        for choice in self.el.choice:
            result += self.add_row('def set_{}(self, value=None):'.format(self.all_names.get(choice.name)), 1)
            result += self.add_row('self.{} = value'.format(self.all_names.get(choice.name)), 2)
            other_choices = filter(lambda x: x.name != choice.name, copy.deepcopy(self.complex_type.choice))
            result += self.add_row('if value:', 2)
            for choice_to_clear in other_choices:
                result += self.add_row('self.{} = None'.format(self.all_names.get(choice_to_clear.name)), 3)
            result += '\n'
        return result

    def build_has_children(self):
        result = ''
        result += self.add_row('def has_children(self):', level=1)
        children_condition = ' or '.join([
            'self.{}'.format(x) for x in (list(self.sequence_names.values()) + list(self.choice_names.values()))
        ])
        result += self.add_row(
            'return {}'.format('bool(' + children_condition + ')' if children_condition else 'False'),
            level=2)
        result += '\n'
        return result

    def build_has_content(self):
        result = ''
        result += self.add_row('def has_content(self):', level=1)
        if self.all_names:
            result += self.add_row('return (', level=2)
            names_length = len(self.all_names.values())
            names_count = 0
            for name in self.all_names.values():
                names_count += 1
                result += self.add_row('self.{name} is not None{_or}'.format(
                    name=name, _or=' or' if names_count < names_length else ''
                ), level=3)
            result += self.add_row(')', level=2)
        else:
            result += self.add_row('return False', level=2)
        result += '\n'
        return result

    def build_export_attrs(self):
        result = ''
        result += self.add_row('def export_attrs(self):', level=1)
        result += self.add_row('result = ""', level=2)
        for attr in self.el.attributes:
            attr_name = self.attrib_names.get(attr.name)
            attr_lower_name = attr_name.lower()
            attr_value_template = self.get_attr_value_template(attr)
            result += self.add_row('{attr_low} = {template} if self.{name} is not None else {default}'.format(
                attr_low=attr_lower_name,
                template=attr_value_template.format(attr='self.' + attr_name),
                name=attr_name,
                default=self.get_default_attr(attr)
            ), level=2)
            if not attr.required:
                result += self.add_row('if {}:'.format(attr_lower_name), level=2)
                setter_level = 3
            else:
                setter_level = 2
            result += self.add_row('result += \' {raw_name}="{{}}"\'.format({lower_name})'.format(
                raw_name=attr.name,
                lower_name=attr_lower_name
            ), level=setter_level)

        result += self.add_row('return result', level=2)
        result += '\n'
        return result

    def get_default_attr(self, attr):
        result = '""'
        if attr.required:
            if isinstance(attr.simple_type, XSBaseNumericType):
                result = '0'
        return result

    def get_attr_value_template(self, attribute):
        return 'self.quote_attrib({attr})'

    def get_simple_type_value_template(self, stype):
        return '{attr}'

    def build_export_children(self):
        result = ''
        result += self.add_row('def export_children(self, outfile, level):', level=1)
        result += self.add_row('super().export_children(outfile, level)', level=2)
        if self.el.sequence or self.el.choice:
            result += self.add_row('child_level = level + 1', level=2)
            if self.el.sequence:
                result += self.add_row('# sequence', level=2)
                for seq_el in self.el.sequence:

                    seq_el_name = self.sequence_names.get(seq_el.name)
                    if not seq_el.min_occurs:
                        result += self.add_row('if self.{}:'.format(seq_el_name), level=2)
                        next_level = 3
                    else:
                        next_level = 2
                    if seq_el.complex_type:
                        if seq_el.max_occurs == 1:
                            result += self.add_row('self.{}.export(outfile, level=child_level, name="{}")'.format(seq_el_name, seq_el.name), level=next_level)
                        else:
                            result += self.add_row('for el in self.{}:'.format(seq_el_name), level=next_level)
                            result += self.add_row('el.export(outfile, level=child_level, name="{}")'.format(seq_el.name), level=next_level+1)
                    elif seq_el.simple_type:
                        stype_template = self.get_simple_type_value_template(seq_el.simple_type)
                        if seq_el.max_occurs == 1:
                            _default = "''" if seq_el.min_occurs else 'None'
                        else:
                            _default = "[]"
                        result += self.add_row('{stype_low} = {template} if self.{name} is not None else {default}'.format(
                            stype_low=seq_el_name.lower(),
                            template=stype_template.format(attr='self.' + seq_el_name),
                            name=seq_el_name,
                            default=_default,
                        ), level=next_level)
                        result += self.add_row("if {} is not None:".format(seq_el_name.lower()), level=next_level)
                        if seq_el.max_occurs == 1:
                            result += self.add_row("outfile.write('{{level}}<{{namespace}}{{tag}}>{{content}}</{{namespace}}{{tag}}>\\n'.format("
                                                   "level='  ' * level, namespace='{namespace}', tag='{tag}', "
                                                   "content=self.quote_xml({stype_low})))".format(
                                namespace='', tag=seq_el.name, stype_low=seq_el_name.lower()
                            ), level=next_level+1)
                        else:
                            result += self.add_row('for content in {}:'.format(seq_el_name.lower()), level=next_level+1)
                            result += self.add_row("outfile.write('{{level}}<{{namespace}}{{tag}}>{{content}}</{{namespace}}{{tag}}>\\n'.format("
                                                   "level='  ' * level, namespace='{namespace}', tag='{tag}', "
                                                   "content=self.quote_xml(content)))".format(
                                namespace='', tag=seq_el.name
                            ), level=next_level+2)

            if self.el.choice:
                result += self.add_row('# choice', level=2)
                for choice_el in self.el.choice:
                    choice_index = self.el.choice.index(choice_el)
                    choice_el_name = self.choice_names.get(choice_el.name)
                    if choice_index == 0:
                        result += self.add_row('if self.{}:'.format(choice_el_name), level=2)
                    else:
                        result += self.add_row('elif self.{}:'.format(choice_el_name), level=2)
                    if choice_el.complex_type:
                        if choice_el.max_occurs == 1:
                            result += self.add_row('self.{}.export(outfile, level=child_level, name="{}")'.format(choice_el_name, choice_el.name), level=3)
                        else:
                            result += self.add_row('for el in self.{}:'.format(choice_el_name), level=3)
                            result += self.add_row('el.export(outfile, level=child_level, name="{}")'.format(choice_el.name), level=4)
                    elif choice_el.simple_type:
                        stype_template = self.get_simple_type_value_template(choice_el.simple_type)
                        result += self.add_row('{stype_low} = {template} if self.{name} is not None else None'.format(
                            stype_low=choice_el_name.lower(),
                            template=stype_template.format(attr='self.' + choice_el_name),
                            name=choice_el_name
                        ), level=3)
                        result += self.add_row("if {} is not None:".format(choice_el_name.lower()), level=3)
                        result += self.add_row(
                            "outfile.write('{{level}}<{{namespace}}{{tag}}>{{content}}</{{namespace}}{{tag}}>\\n'.format("
                            "level='  ' * level, namespace='{namespace}', tag='{tag}', "
                            "content={stype_low}))".format(
                                namespace='', tag=choice_el.name, stype_low=choice_el_name.lower()
                            ), level=4)

        result += '\n'
        return result

    def build_export(self):
        result = ''
        result += self.add_row('def export(self, outfile, level, name="{}", ns_def=""):'.format(self.el.name), level=1)
        result += self.add_row('attrs = self.export_attrs()', level=2)
        result += self.add_row("outfile.write('{{level}}<{{namespace}}{{tag}}{{ns_def}}{{attrs}}{{close_letter}}\\n'.format("
                               "level='  ' * level, namespace='{namespace}', tag=name, ns_def=(ns_def and ' ' + ns_def or ''), attrs=attrs, "
                               "close_letter='>' if self.has_children() else '/>'))".format(
                namespace='', tag=self.el.name),
            level=2)
        result += self.add_row('self.export_children(outfile, level=level + 1)', level=2)
        result += self.add_row('if self.has_children():', level=2)
        result += self.add_row("outfile.write('{{level}}</{{namespace}}{{tag}}>\\n'.format("
                               "level='  ' * level, "
                               "namespace='{namespace}', "
                               "tag=name))".format(
                namespace='', tag=self.el.name
        ), level=3)

        result += '\n'
        return result
