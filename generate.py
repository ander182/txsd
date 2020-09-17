#!/usr/bin/python3
from creators.python2_creator import Py2Creator
from creators.python3_creator import Py3Creator
from parser import Parser
import argparse


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--input', action='store', required=True)
    arg_parser.add_argument('-o', '--output', action='store', )
    arg_parser.add_argument('-e', '--encoding', action='store', default='utf-8')
    arg_parser.add_argument('-c', '--creator', action='store', default='py3')
    args = arg_parser.parse_args()
    if not args.output:
        args.output = args.input + '.py'
    make_file(
        input_xsd_path=args.input,
        output_path=args.output,
        encoding=args.encoding,
        creator=args.creator,
    )


def get_creator_class(creator_key):
    if creator_key == 'py2':
        return Py2Creator
    elif creator_key == 'py3':
        return Py3Creator
    else:
        print('Creator is not specified or specified incorrectly')


def make_file(input_xsd_path, output_path, encoding, creator):
    parser = Parser()
    parser.parse_xsd(filepath=input_xsd_path, encoding=encoding)
    creator_class = get_creator_class(creator)
    creator = creator_class(xs_elements=parser.external_objects)
    with open(output_path, 'w') as f:
        creator.make(result_file=f)


if __name__ == '__main__':
    main()
