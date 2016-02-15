#!python3
"Nustack Standard Library\nYou don't need to import this, it is loaded automatically."
import os
import importlib
from nustack.extensionbase import Module, Token
import nustack.interpreter

class ScopeWrapper:
    def __init__(self, s):
        self.scope = s._scopes[0]
    def get(self, name):
        return self.scope[name]
    def __repr__(self):
        return "ScopeWrapper: " + repr(self.scope)

module = Module("builtins")

@module.register("show")
def show(env) -> "(a -- )":
    "Shows the top of the stack"
    thing = env.stack.pop()
    if thing.type == "lit_bool":
        s = "#t" if thing.val else "#f"
    else:
        s = thing.val
    print(s)

@module.register("peek")
def peek(env) -> "(a -- a)":
    "Shows the top of the stack without popping it."
    thing = env.stack.pop()
    if thing.type == "lit_bool":
        s = "#t" if thing.val else "#f"
    else:
        s = thing.val
    print(s)
    env.stack.push(thing)

@module.register("show.repr")
def showr(env) -> "(a -- a)":
    "Shows the top of the stack and its type"
    thing = env.stack.pop()
    if thing.type == "lit_bool":
        s = "#t" if thing.val else "#f"
    else:
        s = thing.val
    print("%s: %s" % (thing.type, s))

@module.register("peek.repr")
def peekr(env) -> "(a -- a)":
    "Shows the top of the stack and its type without popping it."
    thing = env.stack.pop()
    if thing.type == "lit_bool":
        s = "#t" if thing.val else "#f"
    else:
        s = thing.val
    print("%s: %s" % (thing.type, s))
    env.stack.push(thing)

@module.register("+", "add")
def plus(env) -> "(n n -- n)":
    "Adds two numbers"
    a, b = env.stack.popN(2)
    t = a.type
    env.stack.push(Token(t, a.val + b.val))

@module.register("-", "sub")
def sub(env) -> "(n n -- n)":
    "Subtracts 2 numbers"
    a, b = env.stack.popN(2)
    t = a.type
    env.stack.push(Token(t, a.val - b.val))

@module.register("*", "mul")
def mul(env) -> "(n n -- n)":
    'Multiplies 2 numbers'
    a, b = env.stack.popN(2)
    t = a.type
    env.stack.push(Token(t, a.val * b.val))

@module.register("/", "div")
def div(env) -> "(n n -- n)":
    'Divides 2 numbers'
    a, b = env.stack.popN(2)
    t = a.type
    env.stack.push(Token(t, a.val / b.val))

@module.register("eq", "=")
def eq_(env) -> "(a1 a2 -- b)":
    "Returns true if the top two values on the stack equal each other"
    a, b = env.stack.popN(2)
    eq = a.type == b.type and a.val == b.val
    env.stack.push(Token("lit_bool", eq))

@module.register("not")
def not_(env) -> "(b1 -- b)":
    "Returns true if b1 and b2 are true"
    b1 = env.stack.pop()
    env.stack.push(Token("lit_bool", not b1.val))

@module.register("or", "|")
def or_(env) -> "(b1 b2 -- b)":
    "Returns true if b1 or b2 are true"
    b1, b2 = env.stack.popN(2)
    env.stack.push(Token("lit_bool", b1.val or b2.val))

@module.register("and", "&")
def and_(env) -> "(b1 b2 -- b)":
    "Returns true if b1 and b2 are true"
    b1, b2 = env.stack.popN(2)
    env.stack.push(Token("lit_bool", b1.val and b2.val))

@module.register("if")
def if_(env) -> "(b c c -- )":
    'Performs if branching'
    b, t, f = env.stack.popN(3)
    if b.val:
        env.eval(t.val)
    else:
        env.eval(f.val)

@module.register("define", "def")
def define(env) -> "(a s -- )":
    'Defines a value in the current scope'
    val, name = env.stack.popN(2)
    env.scope.assign(name.val, val)

@module.register("show.scopes")
def show_scopes(env) -> "( -- )":
    'Shows the current scopes'
    from pprint import pprint
    print("Scopes")
    for s in reversed(env.scope._scopes):
        pprint(s)
        print()

@module.register("input", "in")
def input_(env) -> "(a -- s)":
    'Shows a, prompts for input, and returns it as a string'
    a = env.stack.pop().val
    s = input(a)
    env.stack.push(Token("lit_string", s))

@module.register("to.string")
def to_string(env) -> "(a -- s)":
    'Pops a value a from the stack and converts it to a string'
    a = env.stack.pop()
    if a.type == 'lit_code':
        a = "Code: %s" % str(a.val)
    else:
        a = a.val
    v = str(a)
    env.stack.push(Token("lit_string", v))

@module.register("to.int")
def to_int(env) -> "(a -- i)":
    'Pops a value a from the stack and converts it to an int'
    a = env.stack.pop().val
    v = int(a)
    env.stack.push(Token("lit_int", v))

@module.register("to.float")
def to_float(env) -> "(a -- f)":
    'Pops a value a from the stack and converts it to a float'
    a = env.stack.pop().val
    v = float(a)
    env.stack.push(Token("lit_float", v))

@module.register("to.symbol")
def to_symbol(env) -> "(a -- sym)":
    'Pops a value a from the stack and converts it to a symbol'
    a = env.stack.pop().val
    if a.type == 'lit_code':
        a = "Code.%s" % str(a.val)
    else:
        a = a.val
    v = str(a)
    env.stack.push(Token("lit_symbol", v))

@module.register("to.bool")
def to_bool(env) -> "(a -- b)":
    'Pops a value a from the stack and converts it to a bool'
    a = env.stack.pop().val
    v = bool(a)
    env.stack.push(Token("lit_bool", v))

@module.register("swap")
def swap(env) -> "(a1 a2 -- a2 a1)":
    "Swaps the two things on top of the stack"
    a, b = env.stack.popN(2)
    env.stack.push(b, a)

@module.register("drop")
def drop(env) -> "(a -- )":
    "Pops the top of the stack"
    env.stack.pop()

@module.register("dup")
def dub(env) -> "(a -- a a)":
    "Duplicates the top of the stack"
    a = env.stack.pop()
    env.stack.push(a, a)

@module.register("over")
def over(env) -> "(a1 a2 -- a1 a2 a1)":
    "Adds the item next to the top of the stack to the top of the stack"
    a, b = env.stack.popN(2)
    env.stack.push(a, b, a)

@module.register("importnu")
def impnu(env) -> "(sym -- )":
    'Import Nustack module'
    curdir = env.getDir()
    name = env.stack.pop().val
    pth = "/".join(name.split("::"))
    try:
        f = open(os.path.join(curdir, pth) + ".nu", "r")
        code = f.read()
        f.close()
        interp = nustack.interpreter.Interpreter()
        _, s = interp.run(code)
        scope = ScopeWrapper(s)
        env.scope.assign(name, scope)
    except IOError as e:
        raise e

@module.register("importext")
def impext(env) -> "(sym -- )":
    'Import extension module'
    name = env.stack.pop().val
    if name.startswith("std::"):
        usestd = True
        name = name[5:]
    else:
        usestd = False
    name = ".".join(name.split("::"))
    if usestd:
        m = importlib.import_module("nustack.stdlib.%s" % name)
    else:
        try:
            m = importlib.import_module("nu_ext_" + name)
        except ImportError:
            m = importlib.import_module("nustack.stdlib.%s" % name)
    env.scope.assign(name, m.module)