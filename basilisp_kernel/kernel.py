from ipykernel.kernelbase import Kernel

import basilisp
from basilisp import main as basilisp
from basilisp.lang import compiler as compiler
from basilisp.lang import reader as reader
from basilisp.lang import runtime as runtime
from basilisp.lang import symbol as sym
from typing import Any, Callable, Optional, Sequence, Type
import traceback

from io import StringIO

def eval_str(s: str, ctx: compiler.CompilerContext, ns: runtime.Namespace, eof: Any):
    """Evaluate the forms in a string into a Python module AST node."""
    last = eof
    for form in reader.read_str(s, resolver=runtime.resolve_alias, eof=eof):
        assert not isinstance(form, reader.ReaderConditional)
        last = compiler.compile_and_exec_form(form, ctx, ns)
    return last

opts = {}
basilisp.init(opts)
ctx = compiler.CompilerContext(filename="basilisp-kernel", opts=opts)
eof = object()
ns = runtime.Namespace.get_or_create(runtime.CORE_NS_SYM)

class BasilispKernel(Kernel):
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

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        bas_out = StringIO()
        bas_err = StringIO()
        ret = None
        try:
            with runtime.bindings({
                    runtime.Var.find_safe(sym.symbol("*out*", ns=runtime.CORE_NS)) : bas_out,
                    runtime.Var.find_safe(sym.symbol("*err*", ns=runtime.CORE_NS)) : bas_err
            }):
                result = eval_str(code, ctx, ns, eof)
                if not silent:
                    out = f"{bas_out.getvalue()}\n{str(result)}" if bas_out.tell() > 0 else str(result)
                    stream_content = {'name': 'stdout', 'text': out}
                    self.send_response(self.iopub_socket, 'stream', stream_content)
                serr = bas_err.getvalue() 
                if bas_err.tell() > 0:
                    stream_content = {'name': 'stderr', 'text': bas_err.getvalue()}
                    self.send_response(self.iopub_socket, 'stream', stream_content)

            ret = {'status': 'ok',
                   # The base class increments the execution count
                   'execution_count': self.execution_count,
                   'payload': [],
                   'user_expressions': {},
                   }

        # except reader.SyntaxError as e:
        #     exc = format_exception(e, reader.SyntaxError, e.__traceback__)
        # except compiler.CompilerException as e:
        #     exc = format_exception(e, compiler.CompilerException, e.__traceback__)
        # except Exception as e:  # pylint: disable=broad-exception-caught
        #     exc = format_exception(e, Exception, e.__traceback__)

        except Exception as e:
            stream_content = {'name': 'stderr', 'text': traceback.format_exc()}
            self.send_response(self.iopub_socket, 'stream', stream_content)
            ret = {'status': 'error',
                   'ename': 'exception',
                   'evalue': str(e),
                   'traceback': []
                   }


        return ret
