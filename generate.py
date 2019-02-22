# coding:utf-8
from creators.python2_creator import PyCreator
from parser import Parser


def main():
    parser = Parser()
    # parser.parse_xsd(filepath='./schemas/NO_RASCHSV.xsd', encoding='windows-1251')
    parser.parse_xsd(filepath='./schemas/SRCHIS.xsd', encoding='utf-8')
    creator = PyCreator(xs_elements=parser.external_objects)
    with open('./result_module.py', 'w') as f:
        creator.make(result_file=f)


if __name__ == '__main__':
    main()
