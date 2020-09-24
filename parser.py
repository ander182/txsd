from lxml import etree
from exceptions import XSInputError, XSParserError, XSParserNotImplemented
from models import XSStringType, XSIntegerType, XSDecimalType, XSComplexType, XSAttribute, XSElement, XSSimpleType


class CTRelation(object):
    """ Объект хранящий в себе связи одного complexType с другими """
    def __init__(self, name, relation_list=None):
        super().__init__()

        self.name = name
        self.relation_list = relation_list or []


def ct_sorted(ct_relation_dict):
    """ Функция принимает словарь {"название": СTRelation}. Возвращает отсортированный список CTRelation.
      Гарантируется что элемент будет находится после связаных с ним элементов.
      """
    result_names = []
    ct_relation_list = ct_relation_dict.values()
    current_step = ct_relation_list
    _round = 0
    while True:
        for_next_step = []
        for ct_relation in current_step:
            if not len(ct_relation.relation_list):
                result_names.insert(0, ct_relation.name)
            else:
                indexes = []
                for rel in ct_relation.relation_list:
                    try:
                        indexes.append(result_names.index(rel))
                    except ValueError:
                        for_next_step.append(ct_relation)
                        break
                if not len(indexes):
                    continue
                result_names.insert(max(indexes)+1, ct_relation.name)
        if _round and not _round % 10:
            print('Internal warning: Sorting of complexTypes passed through {} rounds'.format(_round))
        if _round > 1000:
            raise XSParserError('complexType relation deadlock found.')
        if len(for_next_step):
            current_step = for_next_step
            _round += 1
        else:
            break
    return map(lambda x: ct_relation_dict.get(x), result_names)


class MainMap(object):

    def __init__(self, schema_ns):
        super().__init__()
        self.schema_ns = schema_ns
        self.mm = {}

    def set(self, name, element):
        if name not in self.mm:
            self.mm[name] = element

    def get(self, name):
        result = self.mm.get(name)
        if not result and name.startswith('{}:'.format(self.schema_ns)):
            result = XSStringType(name=name)
        return result


class Parser(object):

    _NS_XS = 'http://www.w3.org/2001/XMLSchema'

    def __init__(self, namespace=None, schema_ns='xs'):
        super().__init__()

        self.namespace = namespace
        self.schema_ns = schema_ns

        self._ns_path = None

        self.xs_etree = None
        self.root = None

        # мапа связей complexType между собой
        self.ct_relations = {}

        # мапа всех типов и элементов
        self.main_map = MainMap(schema_ns=schema_ns)

        # объекты, которые должны превратится в итоговые классы
        self.external_objects = []

    @property
    def ns_path(self):
        return self._ns_path or self._NS_XS

    def get_tag(self, name, namespace=None):
        if namespace is None:
            namespace = self.ns_path
        return '{{{}}}{}'.format(namespace, name)

    def add_ct_relation(self, name, relation_list):
        self.ct_relations[name] = CTRelation(name, relation_list=relation_list)

    def parse_xsd(self, filepath=None, from_string=None, encoding=None):
        if filepath:
            parser = etree.XMLParser(encoding=encoding)
            self.xs_etree = etree.parse(filepath, parser=parser)
        elif from_string:
            self.xs_etree = etree.fromstring(from_string)
        else:
            raise XSInputError()

        self.root = self.xs_etree.getroot()
        ns_xs = self.root.nsmap.get(self.schema_ns)
        if ns_xs:
            self._ns_path = ns_xs

        sorted_nodes = self.determine_sequence()

        for primary_node in sorted_nodes:
            if primary_node.tag == self.get_tag('simpleType'):
                s_type = self.make_simple_type(primary_node)
                if s_type.name is None:
                    raise XSParserError('XSD-schema error: external xs:simpleType not found name')
                self.main_map.set(s_type.name, s_type)
            if primary_node.tag == self.get_tag('complexType'):
                c_type = self.make_complex_type(primary_node, as_external=True)
                if c_type.name is None:
                    raise XSParserError('XSD-schema error: external xs:complexType not found name')
                self.main_map.set(c_type.name, c_type)

            if primary_node.tag == self.get_tag('element'):
                element = self.make_element(primary_node, as_external=True)
                if element.name is None:
                    raise XSParserError('XSD-schema error: external xs:element not found name')
                self.main_map.set(element.name, element)
                if element.complex_type:
                    self.external_objects.append(element)


    def determine_sequence(self):
        # Возвращает элементы первого уровня схемы в необходимом порядке их загрузки.
        # зависимые ноды идут последними
        # Список simpleType. обрабатываются самые первые
        simple_types = []
        # Список element. Должны обработаться после complexType и simpleType
        raw_elements = []
        # Список complexType. Последовательность определить по ct_relations
        complex_types_map = {}

        for schema_node in self.root.getchildren():
            if isinstance(schema_node, etree._Comment):
                continue
            if schema_node.tag == self.get_tag('element'):
                raw_elements.append(schema_node)
            elif schema_node.tag == self.get_tag('complexType'):
                node_name = schema_node.attrib.get('name')
                complex_types_map[node_name] = schema_node

                relation_containers = []
                first_container = []
                relation_containers.append(first_container)
                self.add_ct_relation(node_name, self.get_etree_relations(schema_node, containers=relation_containers))

            elif schema_node.tag == self.get_tag('simpleType'):
                simple_types.append(schema_node)

        sorted_complex_types = []
        if self.ct_relations:
            self.remove_stypes_from_ct_relations(simple_types)
            for ct in ct_sorted(self.ct_relations):
                sorted_ct_node = complex_types_map.get(ct.name)
                if sorted_ct_node is None:
                    XSParserError('Internal error: ComplexType node not found by name')
                sorted_complex_types.append(sorted_ct_node)

        result = simple_types + sorted_complex_types + raw_elements
        return result

    def remove_stypes_from_ct_relations(self, simple_types):
        for stype_el in simple_types:
            name = stype_el.attrib.get('name')
            if name:
                for relation in self.ct_relations.values():
                    if relation.relation_list.count(name):
                        relation.relation_list.remove(name)

    def get_etree_relations(self, node, containers=None):
        assert containers

        container = []
        containers.append(container)

        needed_tags = [self.get_tag('sequence'), self.get_tag('choice')]

        for sub_node in node.getchildren():
            if sub_node.tag in needed_tags:
                for rel_element in sub_node.getchildren():
                    if rel_element.attrib.get('type'):
                        for c in containers:
                            c.append(rel_element.attrib.get('type'))
                    elif rel_element.attrib.get('name'):
                        if rel_element.xpath('complexType'):
                            for c in containers:
                                c.append(rel_element.attrib.get('name'))
                            self.add_ct_relation(sub_node.attrib.get('name'), self.get_etree_relations(
                                rel_element,
                                containers=containers
                            ))
                    elif isinstance(rel_element, etree._Comment):
                        continue
                    else:
                        raise XSParserError('Relation type name not found')

        return container

    def make_simple_type(self, node):
        _xs = self.schema_ns

        name = node.attrib.get('name')
        documentation = ''
        doc = self.xpath_get(node, '{0}:annotation/{0}:documentation'.format(_xs), namespaces=node.nsmap)
        if doc is not None:
            documentation = doc.text

        restriction = self.xpath_get(node, './/{0}:restriction[@base]'.format(_xs), namespaces=node.nsmap)
        base = restriction.attrib.get('base')
        if not base:
            raise XSParserError('Internal error: restriction base not found on simpleType')

        if base == _xs+':string':
            s_type = XSStringType(name=name, documentation=documentation)

        elif base == _xs+':integer':
            s_type = XSIntegerType(name=name, documentation=documentation)

        elif base == _xs+':decimal':
            s_type = XSDecimalType(name=name, documentation=documentation)

        elif self.main_map.get(base):
            s_type = self.main_map.get(base)

        else:
            raise XSParserNotImplemented('simpleType with base="{} now is not implemented"'.format(base))

        for key, field_name in s_type.available_restriction_map.items():
            if field_name in s_type.multiple_fields:
                container = getattr(s_type, field_name, [])
                for param in self.xpath_list(restriction, _xs + ':{}'.format(key), namespaces=restriction.nsmap):
                    container.append(param.attrib.get('value'))
            else:
                _ = self.xpath_get(restriction, _xs + ':{}'.format(key), namespaces=node.nsmap)
                if _ is not None:
                    setattr(s_type, field_name, _.attrib.get('value'))

        return s_type

    def make_complex_type(self, node, as_external=False):

        _xs = self.schema_ns
        name = node.attrib.get('name')
        documentation = ''
        doc = self.xpath_get(node, '{0}:annotation/{0}:documentation'.format(_xs), namespaces=node.nsmap)
        if doc is not None:
            documentation = doc.text

        c_type = XSComplexType(name=name)
        c_type.documentation = documentation

        for node_attribute in self.xpath_list(node, '{0}:attribute'.format(_xs), namespaces=node.nsmap):
            attr_name = node_attribute.attrib.get('name')
            attribute = XSAttribute(
                name=attr_name,
                required=node_attribute.attrib.get('use') == 'required'
            )

            s_type_name = node_attribute.attrib.get('type')
            s_type_node = None
            if not s_type_name:
                s_type_node = self.xpath_get(node_attribute, '{}:simpleType'.format(_xs), namespaces=node_attribute.nsmap)

            if s_type_name:
                s_type_name = node_attribute.attrib.get('type')
                s_type = self.main_map.get(s_type_name)
                if s_type is not None:
                    attribute.simple_type = s_type
                else:
                    raise XSParserError('Attribute {} not found simpleType {}'.format(attr_name, s_type_name))

            elif s_type_node is not None:
                s_type = self.make_simple_type(s_type_node)
                if s_type is not None:
                    attribute.simple_type = s_type
                else:
                    raise XSParserError('Attribute {} contains broken simpleType'.format(attr_name))
            else:
                raise XSParserError('XSD-schema error: xs_attribute {} not found simpleType'.format(attr_name))
            c_type.add_attribute(attribute)

        node_sequence = self.xpath_get(node, '{}:sequence'.format(_xs), namespaces=node.nsmap)
        if node_sequence is not None:
            self._make_sequence(node_sequence, c_type, as_external=as_external)
        node_choice = self.xpath_get(node, '{}:choice'.format(_xs), namespaces=node.nsmap)
        if node_choice is not None:
            self._make_choice(node_choice, c_type, as_external=as_external)

        return c_type

    def _make_sequence(self, node_sequence, parent_c_type, as_external=False):
        _xs = self.schema_ns
        for node_el in self.xpath_list(node_sequence, '{}:element'.format(_xs), namespaces=node_sequence.nsmap):
            seq_el = self.make_element(node_el, as_external=as_external)
            self.main_map.set(seq_el.name, seq_el)
            if as_external and seq_el.complex_type:
                self.external_objects.append(seq_el)
            parent_c_type.sequence.append(seq_el)
        node_choice = self.xpath_get(node_sequence, '{}:choice'.format(_xs), namespaces=node_sequence.nsmap)
        if node_choice is not None:
            self._make_choice(node_choice, parent_c_type, as_external=as_external)

    def _make_choice(self, node_choice, parent_c_type, as_external=False):
        _xs = self.schema_ns
        for node_el in self.xpath_list(node_choice, '{}:element'.format(_xs), namespaces=node_choice.nsmap):
            choice_el = self.make_element(node_el, as_external=as_external)
            self.main_map.set(choice_el.name, choice_el)
            if as_external and choice_el.complex_type:
                self.external_objects.append(choice_el)
            parent_c_type.choice.append(choice_el)

    def make_element(self, node, as_external=False):

        _xs = self.schema_ns
        name = node.attrib.get('name')
        documentation = ''
        doc = self.xpath_get(node, '{0}:annotation/{0}:documentation'.format(_xs), namespaces=node.nsmap)
        if doc is not None:
            documentation = doc.text

        el = XSElement(name=name)
        el.documentation = documentation

        min_occurs = node.attrib.get('minOccurs')
        if min_occurs:
            el.min_occurs = int(min_occurs)
        max_occurs = node.attrib.get('maxOccurs')
        if max_occurs:
            el.max_occurs = 0 if max_occurs == 'unbounded' else int(max_occurs)

        ttype = node.attrib.get('type')
        if ttype:
            parent_type = self.main_map.get(ttype)
            if isinstance(parent_type, XSComplexType):
                el.complex_type = parent_type
            elif isinstance(parent_type, XSSimpleType):
                el.simple_type = parent_type
            else:
                raise XSParserError('type {} not found for element {}'.format(ttype, name))

        #todo element "base" attribute not implemented

        else:
            child_ctype_node = self.xpath_get(node, '{}:complexType'.format(_xs), namespaces=node.nsmap)
            if child_ctype_node is not None:
                el.complex_type = self.make_complex_type(child_ctype_node, as_external=as_external)
            else:
                child_stype_node = self.xpath_get(node, '{}:simpleType'.format(_xs), namespaces=node.nsmap)
                if child_stype_node is not None:
                    el.simple_type = self.make_simple_type(child_stype_node)

        if not (el.complex_type or el.simple_type):
            raise XSParserError('xs_type not found for element {}'.format(name))

        return el

    @staticmethod
    def xpath_get(node, path, namespaces=None):
        # Note that XPath does not have a notion of a default namespace. The empty prefix is therefore undefined
        # for XPath and cannot be used in namespace prefix mappings.
        if namespaces and namespaces.get(None):
            namespaces.pop(None)

        for result in node.xpath(path, namespaces=namespaces):
            return result

    @staticmethod
    def xpath_list(node, path, namespaces=None):
        # Note that XPath does not have a notion of a default namespace. The empty prefix is therefore undefined
        # for XPath and cannot be used in namespace prefix mappings.
        if namespaces and namespaces.get(None):
            namespaces.pop(None)

        return node.xpath(path, namespaces=namespaces)


def main():
    parser = Parser()
    parser.parse_xsd(filepath='./schemas/NO_RASCHSV.xsd', encoding='windows-1251')


if __name__ == '__main__':
    main()
