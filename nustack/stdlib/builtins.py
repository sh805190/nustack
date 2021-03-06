#!python3
"Nustack Standard Library\nYou don't need to import this, it is loaded automatically."
import os
import importlib
from nustack.extensionbase import Module, Token
import nustack.interpreter
from nustack.utils import log
import nustack.stdlib; stddir = os.path.dirname(nustack.stdlib.__file__); del nustack.stdlib

class ScopeWrapper:
    def __init__(self, s):
        self.scope = s
    def get(self, name):
        return self.scope[name]
    def __repr__(self):
        return "ScopeWrapper: " + repr(self.scope)
    def __iter__(self):
        return iter(self.scope)
    def __getitem__(self, name):
        return self.get(name)

def namespaceWrapper(pth, scope):
    pth = reversed(pth[1:])
    for name in pth:
        scope = ScopeWrapper({name:scope})
    return scope

module = Module("builtins")

@module.register("show")
def show(env) -> "(a -- )":
    "Shows the top of the stack"
    thing = env.stack.pop()
    if type(thing) != Token:
        print(thing)
    elif thing.type == "lit_bool":
        print("#t" if thing.val else "#f")
    elif thing.type in ("lit_list", "lit_symbol"):
        print(repr(thing))
    else:
        print(thing.val)

@module.register("peek")
def peek(env) -> "(a -- a)":
    "Shows the top of the stack without popping it."
    thing = env.stack.pop()
    if type(thing) != Token:
        s = thing
    elif thing.type == "lit_bool":
        s = "#t" if thing.val else "#f"
    elif thing.type in ("lit_list", "lit_symbol"):
        s = repr(thing)
    else:
        s = thing.val
    print(s)
    env.stack.push(thing)

@module.register("show.repr")
def showr(env) -> "(a -- a)":
    "Shows the top of the stack and its type"
    thing = env.stack.pop()
    if type(thing) != Token:
        print(thing)
        return
    elif thing.type == "lit_bool":
        s = "#t" if thing.val else "#f"
    elif thing.type in ("lit_list", "lit_symbol"):
        s = repr(thing)
    else:
        s = thing.val
    print("%s: %s" % (thing.type, s))

@module.register("peek.repr")
def peekr(env) -> "(a -- a)":
    "Shows the top of the stack and its type without popping it."
    thing = env.stack.pop()
    if type(thing) != Token:
        print(thing)
        env.stack.push(thing)
        return
    elif thing.type == "lit_bool":
        s = "#t" if thing.val else "#f"
    elif thing.type in ("lit_list", "lit_symbol"):
        s = repr(thing)
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
    env.stack.push(Token("lit_float", a.val / b.val))

@module.register("%", "mod")
def div(env) -> "(n n -- n)":
    'Returns the modulo of 2 numbers'
    a, b = env.stack.popN(2)
    env.stack.push(Token("lit_float", a.val % b.val))

@module.register("eq", "=")
def eq_(env) -> "(a1 a2 -- b)":
    "Returns true if the top two values on the stack equal each other"
    a, b = env.stack.popN(2)
    eq = a == b
    env.stack.push(Token("lit_bool", eq))

@module.register("lt", "<")
def lt_(env) -> "(a1 a2 -- b)":
    "Returns true if a1 < a2"
    a, b = env.stack.popN(2)
    try:
        val = a < b
    except TypeError:
        val = False
    env.stack.push(Token("lit_bool", val))

@module.register("gt", ">")
def lt_(env) -> "(a1 a2 -- b)":
    "Returns true if a1 > a2"
    a, b = env.stack.popN(2)
    try:
        val = a > b
    except TypeError:
        val = False
    env.stack.push(Token("lit_bool", val))

@module.register("not")
def not_(env) -> "(b1 -- b)":
    "Returns true if b1 and b2 are true"
    b1 = env.stack.pop()
    env.stack.push(Token("lit_bool", not b1.val))

@module.register("or", "|")
def or_(env) -> "(b1 b2 -- b)":
    "Returns true if b1 or b2 are true"
    b1, b2 = env.stack.popN(2)
    env.stack.push(Token("lit_any", b1.val or b2.val))

@module.register("and", "&")
def and_(env) -> "(b1 b2 -- b)":
    "Returns true if b1 and b2 are true"
    b1, b2 = env.stack.popN(2)
    env.stack.push(Token("lit_any", b1.val and b2.val))

@module.register("if")
def if_(env) -> "(b c c -- )":
    'Performs if branching'
    b, t, f = env.stack.popN(3)
    if b.val:
        env.eval(t.val)
    else:
        env.eval(f.val)
@module.register("cond")
def cond_(env) -> "(l -- )":
    """Takes a list of 2 item lists.
    The first item must be a code object that is run to produce a boolean value.
    If the result of running the first code object is `#t`, the second item in the list,
    which must be a code object, is run."""
    conds = env.stack.pop().val
    for cond in conds:
        env.eval(cond.val[0].val)
        if env.stack.pop().val:
            env.eval(cond.val[1].val)
            break

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


@module.register("rot")
def rot(env) -> "(a1 a2 a3 -- a2 a3 a1)":
    "Rotates the top 3 items on the stack"
    a1, a2, a3 = env.stack.popN(3)
    env.stack.push(a2, a3, a1)

shouldbreak = False

@module.register("for.each")
def for_each(env) -> "(sequence c -- )":
    "Calls a code object for each item of a sequence"
    seq, code = env.stack.popN(2)
    for item in seq.val:
        if isinstance(item, Token):
            env.stack.push(item)
        else:
            env.stack.push(Token("lit_any", item))
        env.eval(code.val)

@module.register("repeat.n")
def for_each(env) -> "(cn -- )":
    "Calls c n times"
    code, n = env.stack.popN(2)
    for i in range(n.val):
        env.eval(code.val)

@module.register("map")
def map_(env) -> "(sequence1 c -- sequence2)":
    "Maps a code object over each item of a sequence and collects the results as a new list."
    seq, code = env.stack.popN(2)
    res = []
    for item in seq.val:
        if isinstance(item, Token):
            env.stack.push(item)
        else:
            env.stack.push(Token("lit_any", item))
        env.eval(code.val)
        res.append(env.stack.pop())
    env.stack.push(Token("lit_list", res))

@module.register("filter")
def filter_(env) -> "(sequence1 c -- sequence2)":
    "Filters a sequence."
    seq, code = env.stack.popN(2)
    res = []
    for item in seq.val:
        if isinstance(item, Token):
            item = item
        else:
            item = Token("lit_any", item)
        env.stack.push(item)
        env.eval(code.val)
        cond = env.stack.pop().val
        if cond:
            res.append(item)
    env.stack.push(Token("lit_list", res))

@module.register("reduce")
def reduce_(env) -> "(sequence1 a c -- a)":
    "Reduces a sequence to a single value"
    seq, start, code = env.stack.popN(3)
    for item in seq.val:
        if isinstance(item, Token):
            item = item
        else:
            item = Token("lit_any", item)
        env.stack.push(start, item)
        env.eval(code.val)
        start = env.stack.pop()
    env.stack.push(start)

@module.register("forever")
def forever(env) -> "(c -- )":
    "Executes a code object repeatedly forever"
    global shouldbreak
    code = env.stack.pop().val
    while True:
        if shouldbreak:
            shouldbreak = False
            break
        env.eval(code)

@module.register("break")
def break_(env) -> "( -- )":
    "Breaks out of a loop"
    global shouldbreak
    shouldbreak = True

@module.register("while")
def while_(env) -> "(c c -- )":
    '''Pops two code objects. While running the first code object results in #t, the second code object is run.
    The second code object might not run at all'''
    global shouldbreak
    cond, code = env.stack.popN(2)
    while True:
        env.eval(cond.val)
        if not env.stack.pop().val or shouldbreak:
            shouldbreak = False
            break
        env.eval(code.val)

@module.register("do.while")
def do_while_(env) -> "(c c -- )":
    '''Pops two code objects. While running the first code object results in #t, the second code object is run.
    The second code object is run at least once.'''
    global shouldbreak
    cond, code = env.stack.popN(2)
    env.eval(code.val)
    while True:
        env.eval(cond.val)
        if not env.stack.pop().val or shouldbreak:
            shouldbreak = False
            break
        env.eval(code.val)

def getsearchpath(env):
    nupath = os.environ.get("NUSTACKPATH", "").split(os.path.pathsep)
    nupath.insert(0, env.getDir())
    return [path.strip().rstrip(os.path.sep) for path in nupath if path]

def loadModule(env, name):
    "Returns a module"
    curdir = env.getDir()
    if name.startswith("std::"):
        usestd = True
        name = name[5:]
    else:
        usestd = False
    namesplit = name.split("::")
    try:
        if usestd:
            log("loadModule: Force loading stdlib", os.path.join(stddir, *namesplit) + ".nu")
            f = open(os.path.join(stddir, *namesplit) + '.nu', "r")
            code = f.read()
            f.close()
            interp = nustack.interpreter.Interpreter()
            _, s = interp.run(code)
            scope = ScopeWrapper(s._scopes[0])
            return namesplit, scope
        nupath = getsearchpath(env)
        log("loadModule: Module Search Path =", nupath)
        for pth in nupath:
            pth = os.path.join(pth, *namesplit) + ".nu"
            log("loadModule: Trying to load", pth)
            if os.path.exists(pth):
                f = open(pth, "r")
                code = f.read()
                f.close()
                interp = nustack.interpreter.Interpreter()
                _, s = interp.run(code)
                scope = ScopeWrapper(s._scopes[0])
                return namesplit, scope
        raise IOError()
    except IOError:
        log("loadModule: Couldn't find nustack module, trying extensions...")
        name = ".".join(namesplit)
        if usestd:
            m = importlib.import_module("nustack.stdlib.%s" % name)
            log("loadModule: Force loading stdlib", name)
        else:
            try:
                m = importlib.import_module("nu_ext.%s" % name )
                log("loadModule: Loading extension module", name, "in nu_ext package")
            except ImportError:
                try:
                    m = importlib.import_module("nu_ext_%s" % name)
                    log("loadModule: Loading extension module", name, "with nu_ext prefix")
                except ImportError:
                    m = importlib.import_module("nustack.stdlib.%s" % name)
                    log("loadModule: Loading stdlib", name)
        return namesplit, m.module

@module.register("import", "imp")
def import_(env) -> "(sym -- )":
    name = env.stack.pop().val
    namesplit, mod = loadModule(env, name)
    env.scope.assign(namesplit[0], namespaceWrapper(namesplit, mod))

@module.register("import*", "imp*")
def import_all(env) -> "(sym -- )":
    name = env.stack.pop().val
    namesplit, mod = loadModule(env, name)
    if type(mod) == ScopeWrapper:
        conts  = mod.scope
    else:
        conts = mod.contents
    for (k,v) in conts.items():
        env.scope.assign(k,v)

@module.register("argv")
def argv(env) -> "( -- l)":
    """Returns a list of the command line arguments passed to the program.
    The first item is either the name of the program or <<INTERACTIVE>>"""
    env.stack.push(env.argv[:])

# Exception handling
def getBaseNames(Cls):
	return [Base.__name__ for Base in Cls.__mro__]

def raisename(name, args):
    ExcClass = type(name, (Exception,),  {})
    raise ExcClass(args)

@module.register("try")
def try_(env):
    tclause, eclauses = env.stack.popN(2)
    try:
        env.eval(tclause.val)
    except BaseException as e:
        bases = getBaseNames(e.__class__)
        for (name, handler) in eclauses.val:
            if name.val in bases:
                env.stack.push(Token("lit_list", [Token("lit_any", val) for val in e.args]))
                env.eval(handler.val)
                break
        else:
            raise e

@module.register("raise")
def raise_(env):
    excname = env.stack.pop().val
    raisename(excname, "")

@module.register("raise.details")
def raise_details(env):
    excname, excargs = env.stack.popN(2)
    raisename(excname.val, excargs.val)

@module.register("lookup")
def lookup(env) -> "(sym -- any)":
    "Returns the variable that has the name of sym's val. Useful for dynamic variable lookup"
    name = env.stack.pop().val
    env.stack.push(env.lookup(name))

@module.register("call")
def call(env) -> "(code -- )":
    "Runs `code`, which can be either a code object or a python function"
    code = env.stack.pop()
    if type(code) in env.FUNCTION_TYPES:
        env.call_external(code)
    else:
        env.eval(code.val)
