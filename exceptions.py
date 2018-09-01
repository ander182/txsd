# -*- coding: utf-8 -*-


class XSInputError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class XSParserError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class XSParserNotImplemented(XSParserError):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)