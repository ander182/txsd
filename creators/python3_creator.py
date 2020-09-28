from creators.base_python_creator import BaseCommonClassBuilder


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


class CommonClassBuilder(BaseCommonClassBuilder):

    def _init_super_template(self):
        return 'super().__init__()'

    def _export_children_super_template(self):
        return 'super().export_children(outfile, level)'
