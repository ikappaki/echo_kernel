from ipykernel.kernelbase import Kernel
from ipykernel.ipkernel import IPythonKernel

from basilisp import main as basilisp
from basilisp import cli
from basilisp.lang import compiler as compiler
from basilisp.lang import reader as reader
from basilisp.lang import runtime as runtime
from basilisp.lang import symbol as sym
from typing import Any, Callable, Optional, Sequence, Type
import re
import sys

from io import StringIO

opts = {}
basilisp.init(opts)
ctx = compiler.CompilerContext(filename="basilisp-kernel", opts=opts)
eof = object()

user_ns = runtime.Namespace.get_or_create(sym.symbol("user"))
core_ns = runtime.Namespace.get(runtime.CORE_NS_SYM)
cli.eval_str("(ns user (:require clojure.core))", ctx, core_ns, eof)

_DELIMITED_WORD_PATTERN = re.compile(r"[\[\](){\}\s]+")

def do_execute(code):
    bas_out = StringIO()
    bas_err = StringIO()
    ret = None
    with runtime.bindings({
            runtime.Var.find_safe(sym.symbol("*out*", ns=runtime.CORE_NS)) : bas_out,
            runtime.Var.find_safe(sym.symbol("*err*", ns=runtime.CORE_NS)) : bas_err
    }):
        result = None
        try:
            result = cli.eval_str(code, ctx, user_ns, eof)
            if bas_err.tell() > 0:
                print(bas_err.getvalue(), file=sys.stderr)
            if bas_out.tell() > 0:
                print(bas_out.getvalue())
        except:
            if bas_err.tell() > 0:
                print(bas_err.getvalue(), file=sys.stderr)
            if bas_out.tell() > 0:
                print(bas_out.getvalue())
            raise

        return result

class BasilispKernel(IPythonKernel):
    implementation = 'basilisp_kernel'
    implementation_version = '1.0'
    language = 'clojure'
    language_version = '0.1'
    language_info = {
        'name': 'clojure',
        'codemirror-mode': "clojure",
        'mimetype': 'text/x-clojure',
        'file_extension': '.lpy',
    }
    banner = "Basilisp: a Clojure-compatible(-ish) Lisp dialect in Python"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.imported = False

    def do_complete(self, code, cursor_pos):
        if cursor_pos > len(code):
            cursor_pos = len(code)

        words = re.split(_DELIMITED_WORD_PATTERN, code)

        last_word = ""
        current_length = 0
        for word in words:
            current_length += len(word)
            if current_length > cursor_pos:
                break
            last_word = word

        word_before_cursor = last_word
        completions = runtime.repl_completions(word_before_cursor) or ()
        return {"status" : "ok",
                "matches" : completions,
                "cursor_start" : cursor_pos,
                "cursor_end" : cursor_pos,
                "metadata" : dict()
                }

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        bas_code = f'basilisp_kernel.kernel.do_execute({repr(code)})'
        if not self.imported:
            bas_code = f'import basilisp_kernel\n{bas_code}'
            self.imported = True
        return super().do_execute(code=bas_code, silent=silent, store_history=store_history,
                                  user_expressions=user_expressions, allow_stdin=allow_stdin)
    
