

class TranslitMixin(object):

    @staticmethod
    def translit(local_lang_string):
        conversion = {
            '\u0410': 'A', '\u0430': 'a',
            '\u0411': 'B', '\u0431': 'b',
            '\u0412': 'V', '\u0432': 'v',
            '\u0413': 'G', '\u0433': 'g',
            '\u0414': 'D', '\u0434': 'd',
            '\u0415': 'E', '\u0435': 'e',
            '\u0401': 'Yo', '\u0451': 'yo',
            '\u0416': 'Zh', '\u0436': 'zh',
            '\u0417': 'Z', '\u0437': 'z',
            '\u0418': 'I', '\u0438': 'i',
            '\u0419': 'Y', '\u0439': 'y',
            '\u041a': 'K', '\u043a': 'k',
            '\u041b': 'L', '\u043b': 'l',
            '\u041c': 'M', '\u043c': 'm',
            '\u041d': 'N', '\u043d': 'n',
            '\u041e': 'O', '\u043e': 'o',
            '\u041f': 'P', '\u043f': 'p',
            '\u0420': 'R', '\u0440': 'r',
            '\u0421': 'S', '\u0441': 's',
            '\u0422': 'T', '\u0442': 't',
            '\u0423': 'U', '\u0443': 'u',
            '\u0424': 'F', '\u0444': 'f',
            '\u0425': 'H', '\u0445': 'h',
            '\u0426': 'Ts', '\u0446': 'ts',
            '\u0427': 'Ch', '\u0447': 'ch',
            '\u0428': 'Sh', '\u0448': 'sh',
            '\u0429': 'Sch', '\u0449': 'sch',
            '\u042a': '', '\u044a': '',
            '\u042b': 'Y', '\u044b': 'y',
            '\u042c': '', '\u044c': '',
            '\u042d': 'E', '\u044d': 'e',
            '\u042e': 'Yu', '\u044e': 'yu',
            '\u042f': 'Ya', '\u044f': 'ya',
        }
        translit_string = []
        for c in local_lang_string:
            translit_string.append(conversion.setdefault(c, c))
        return ''.join(translit_string).replace('.', '_').replace('-', '_')
