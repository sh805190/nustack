#!python3
"String - String utils and constants\nImport with `std::String import"
import string
from nustack.extensionbase import Module, Token
module = Module("std::Seq")

def strtok(val):
    return Token("lit_string", val)


module.registerValue("ascii_letters", strtok(string.ascii_letters))
module.registerValue("ascii_lowercase", strtok(string.ascii_lowercase))
module.registerValue("ascii_uppercase", strtok(string.ascii_uppercase))
module.registerValue("digits", strtok(string.digits))
module.registerValue("hexdigits", strtok(string.hexdigits))
module.registerValue("octdigits", strtok(string.octdigits))
module.registerValue("punctuation", strtok(string.punctuation))
module.registerValue("printable", strtok(string.printable))
module.registerValue("whitespace", strtok(string.whitespace))

@module.register("split")
def split(env) -> "(s1 s2 -- l)":
    "Splits s1 by s2"
    s1, s2 = env.stack.popN(2)
    res = list(map(strtok, s1.val.split(s2.val)))
    env.stack.push(Token("lit_list", res))

@module.register("join")
def join(env) -> "(sequence s1 -- s2)":
    "Returns a new string formed by inserting s1 between every member of sequence."
    seq, s1 = env.stack.popN(2)
    s2 = s1.val.join(t.val for t in seq.val)
    env.stack.push(strtok(s2))

@module.register("contains")
def contains(env) -> "(s1 s2 -- b)":
    "Returns #t if the string s1 contains s2.\nDo not use this for arbitary sequences, use Seq::contains instead."
    s1, s2 = env.stack.popN(2)
    b = s2.val in s1.val
    env.stack.push(Token("lit_bool", b))
