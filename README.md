# txsd
Translating XSD-Schema to Python class tree. 

To use you need Python3 and `lxml` installed in it.

### Example:

    python3 ./generate.py -i /path/to/sxhema.xsd -o /path/to/python/module
 
### Available parameters:

`-i`  `--input` -  path to XSD-schema file. Thr only required parameter.

`-o` `--output` - path to target python module. If file exists, then it will be overwritten. if paramenter is not specified, using input name + '.xsd'

`-e` `--encoding` - encoding xsd-schema. Default `utf-8`

`-c` `--creator` - version python code on output module. Default `py3`

`-n` `--schema_ns` - namespace tag of "http://www.w3.org/2001/XMLSchema" in input file. Default `xs`
