"""
Example use of jupyter_kernel_test, with tests for the default python3 kernel
(IPyKernel). This includes all the currently available tests.
"""

import unittest

import jupyter_kernel_test as jkt


class BasilispKernelTests(jkt.KernelTests):

    # REQUIRED

    # the kernel to be tested
    # this is the normally the name of the directory containing the
    # kernel.json file - you should be able to do
    # `jupyter console --kernel KERNEL_NAME`
    kernel_name = "basilisp"

    # Everything else is OPTIONAL

    # the name of the language the kernel executes
    # checked against language_info.name in kernel_info_reply
    language_name = "clojure"

    # the normal file extension (including the leading dot) for this language
    # checked against language_info.file_extension in kernel_info_reply
    file_extension = ".lpy"

    # code which should write the exact string `hello, world` to STDOUT
    code_hello_world = "(println \"hello, world\")"

    # code which should cause (any) text to be written to STDERR
    code_stderr = "(binding [*out* *err*] (println \"hi\"))"

    # samples for the autocompletion functionality
    # for each dictionary, `text` is the input to try and complete, and
    # `matches` the list of all complete matching strings which should be found
    completion_samples = [
        {
            "text": "[abc print",
            "matches": {"printf", "println", "println-str", "print", "print-str"},
        },
    ]

    # code which should generate a (user-level) error in the kernel, and send
    # a traceback to the client
    code_generate_error = "(throw (Exception. \"based\"))"

if __name__ == "__main__":
    unittest.main()
