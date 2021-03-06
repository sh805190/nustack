#!python3
# Nustack tokenizer/parser

from nustack.utils import log
import re, pprint
LEGAL_IDS = re.escape(r'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&()*+,-./:;<=>?@\^_|~')
COMMENT = re.compile(r"(?:/\*.+?\*/)|(?:[ \t\n\r\x0b\x0c]+)|(?://.+?$)", re.DOTALL)
INT     = re.compile(r"(?:-)?\d+(?!\.)")
FLOAT   = re.compile(r"(?:-)?\d*\.\d+")
BOOL    = re.compile("#t|#f")
STRING  = re.compile(r"('.*?(?<!\\)')|(\".*?(?<!\\)\")")
BYTE    = re.compile(r"b(('.*?(?<!\\)')|(\".*?(?<!\\)\"))")
SYMBOL  = re.compile(r"`[%s]+" % LEGAL_IDS)
CALL    = re.compile(r"[%s]+" % LEGAL_IDS)

class TokenizeError(Exception): pass

def addescapes(s):
    escapes = {
    r"\\": "\\",
    r"\'": "'",
    r'\"': '"',
    r"\b": "\b",
    r"\n": "\n",
    r"\r": "\r",
    r"\t": "\t",
    r"\v": "\v",
    }
    for (k,v) in escapes.items():
        s = s.replace(k,v)
    return s

class Token:
    def __init__(self, type, val):
        self.type = type
        self.val  = val

    def __eq__(self, other):
        if self.type in ("lit_int", "lit_float") and other.type in ("lit_int", "lit_float"):
            # Numbers can be equal even if they are of different types.
            eq = self.val == other.val
        else:
            eq = self.type == other.type and self.val == other.val
        return eq

    def __lt__(self, other):
        if self.type in ("lit_int", "lit_float") and other.type in ("lit_int", "lit_float"):
            # Numbers can be equal even if they are of different types.
            eq = self.val < other.val
        else:
            eq = self.type == other.type and self.val < other.val
        return eq

    def __gt__(self, other):
        if self.type in ("lit_int", "lit_float") and other.type in ("lit_int", "lit_float"):
            # Numbers can be equal even if they are of different types.
            eq = self.val > other.val
        else:
            eq = self.type == other.type and self.val > other.val
        return eq

    def __hash__(self):
        return hash(self.type) & hash((self.val, ))

    def detailstr(self):
         return "Token(type=%s, val=%s)" % (repr(self.type), repr(self.val),)

    def __repr__(self):
        if self.type == 'lit_list':
            return "[ " + ' '.join(map(str, self.val)) + " ]"
        elif self.type == 'lit_symbol':
            return "`"  + self.val
        return repr(self.val)

    def __iter__(self):
        return iter(self.val)

    def get(self, attr):
        val = getattr(self.val, attr)
        if type(val) in (str, int, float, bool, bytes):
            if type(val) in (str, bytes):
                type_ = "lit_string"
            else:
                type_ = "lit_" + val.__class__.__name__
            return Token(type_, val)
        else:
            return val

def tokenize(code):
    tokens = []
    while code:
        commentmatch = COMMENT.match(code)
        intmatch = INT.match(code)
        floatmatch = FLOAT.match(code)
        boolmatch = BOOL.match(code)
        stringmatch = STRING.match(code)
        bytematch = BYTE.match(code)
        symbolmatch = SYMBOL.match(code)
        callmatch = CALL.match(code)
        if commentmatch:
            log("Parsing: Found comment/whitespace")
            commentend = commentmatch.span()[1]
            code = code[commentend:]
        elif intmatch:
            span = intmatch.span()[1]
            n = code[:span]
            n = int(n)
            tokens.append(Token("lit_int", n))
            code = code[span:]
            log("Parsing: Found int", n)
        elif floatmatch:
            span = floatmatch.span()[1]
            n = code[:span]
            n = float(n)
            tokens.append(Token("lit_float", n))
            code = code[span:]
            log("Parsing: Found float", n)
        elif boolmatch:
            span = boolmatch.span()[1]
            b = code[:span]
            if b == "#t":
                bool = True
            else:
                bool = False
            code = code[span:]
            tokens.append(Token("lit_bool", bool))
            log("Parsing: Found bool", b)
        elif stringmatch:
            span = stringmatch.span()[1]
            s = code[:span]
            s = addescapes(s)
            tokens.append(Token("lit_string", s[1:-1]))
            code = code[span:]
            log("Parsing: Found string", s[1:-1])
        elif bytematch:
            span = bytematch.span()[1]
            s = code[:span]
            s = addescapes(s)
            tokens.append(Token("lit_bytes", bytes(s[2:-1], "utf8")))
            code = code[span:]
            log("Parsing: Found bytes", bytes(s[2:-1], "utf8"))
        elif code[0] == "[":
            tokens.append(Token("lit_liststart","["))
            code = code[1:]
            log("Parsing: Found list start")
        elif code[0] == "]":
            tokens.append(Token("listend", "]"))
            code = code[1:]
            log("Parsing: Found list end")
        elif code[0] == "{":
            tokens.append(Token("codestart", "{"))
            code = code[1:]
            log("Parsing: Found code start")
        elif code[0] == "}":
            subcode = []
            while True:
                t = tokens.pop()
                if t.type == "codestart":
                    break
                subcode.append(t)
            tokens.append(Token("lit_code", list(reversed(subcode))))
            code = code[1:]
            log("Parsing: Found code end")
        elif callmatch:
            span = callmatch.span()[1]
            sym = code[:span]
            code = code[span:]
            tokens.append(Token("call", sym))
            log("Parsing: Found call", sym)
        elif symbolmatch:
            span = symbolmatch.span()[1]
            sym = code[1:span]
            code = code[span:]
            tokens.append(Token("lit_symbol", sym))
            log("Parsing: Found symbol", sym)
        else:
            print(code)
            raise TokenizeError("Can not find a token!")
    return tokens

if __name__ == '__main__':
    code = input("Enter code: ")
    for token in tokenize(code):
        print(token)
