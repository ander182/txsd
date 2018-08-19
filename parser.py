from lxml import etree
from exceptions import XSInputError, XSParserError


class Parser(object):
    def __init__(self, namespace=None, schema_ns='ns'):
        super()

        self.namespace = namespace
        self.schema_ns = schema_ns

        self._NS_XS = 'http://www.w3.org/2001/XMLSchema'

        self.xs_etree = None
        self.root = None

    @classmethod
    def get_tag(name, namespace=None):
        if namespace is None:
            namespace = self._NS_XS

        return '{{{}}}{}'.format(namespace, name)


    def parse_xsd(self, like_file_obj=None, from_string=None):
        if (like_file_obj):
            self.xs_etree = etree.parse(like_file_obj)
        elif (from_string):
            self.xs_etree = etree.fromstring(from_string)
        else:
            raise XSInputError()

        self.root = self.xs_etree.getroot()
        ns_xs = self.root.nsmap.get(self.schema_ns)
        if ns_xs:
            self._NS_XS = ns_xs

        sorted_nodes = self.determine_sequence()

    def determine_sequence():
        # Возвращает элементы первого уровня схемы в необходимом порядке их загрузки.
        # зависимые ноды идут последними
        # Список simpleType. обрабатываются самые первые
        simple_types = []
        # Список element. Должны обработаться после complexType и simpleType
        raw_elements = []
        # Список complexType. Последовательность определить по ct_relations
        complex_types = []
        complex_types_map = {}
        sorted_complex_types = []
        ct_relations = {}

        for schema_node in self.root.getchildren():
            if isinstance(schema_node, etree._Comment):
                continue
            if schema_node.tag == self.get_tag('element')
                raw_elements.append(schema_node)
            elif schema_node.tag == self.get_tag('complexType'):
                complex_types.append(schema_node)
                node_name = schema_node.attrib.get('name')
                relation_container = []
                ct_relations[node_name] = self.get_etree_relations(schema_node, container=relation_container)
            elif schema_node.tag == self.get_tag('simpleType'):
                simple_types.append(schema_node)

        if ct_relations:
            # todo Сортировка по порядку определения
            pass

        result = simple_types + sorted_complex_types + raw_elements
        return result

    def get_etree_relations(node, container=None):
        assert container

        needed_tags = [self.get_tag('sequence'), self.get_tag('choice')]

        for sub_node in node.getchildren():
            if sub_node.tag in needed_tags:
                #todo найти используемые элементы
                for rel_element in sub_node.getchildren():
                    if rel_element.attrib.get('type'):
                        container.append(rel_element.attrib.get('type'))
                    elif rel_element.attrib.get('name'):
                        container.append(rel_element.attrib.get('name'))
                    else:
                        raise XSParserError('Relation type name not found')

                    if rel_element.xpath(self.get_tag('complexType')):
                        self.get_etree_relations(rel_element, container=container)
        return container


def main():
    parser = Parser()
    with open('schemas.NO_NDFL6.xsd', 'r') as f
        parser.parse_xsd(like_file_obj=f)

if __name__ == '__main__':
    main()
