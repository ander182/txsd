#!/usr/bin/python3
from creators.python2_creator import PyCreator
from parser import Parser
import argparse


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--input', action='store', required=True)
    arg_parser.add_argument('-o', '--output', action='store', )
    arg_parser.add_argument('-e', '--encoding', action='store', default='utf-8')
    args = arg_parser.parse_args()
    if not args.output:
        args.output = args.input + '.py'
    make_file(
        input_xsd_path=args.input,
        output_path=args.output,
        encoding=args.encoding,
    )


def make_file(input_xsd_path, output_path, encoding):
    parser = Parser()
    parser.parse_xsd(filepath=input_xsd_path, encoding=encoding)
    creator = PyCreator(xs_elements=parser.external_objects)
    with open(output_path, 'w') as f:
        creator.make(result_file=f)


if __name__ == '__main__':
    main()
