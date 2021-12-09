# -*- coding: utf-8 -*-
#   Copyright 2014 Joseph Blaylock <jrbl@jrbl.org>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""WTF is an inspect wrapper that pretty prints common items.

Using a debugger is probably better, but this may be more convenient if
you're already used to sprinkling debug output throughout your program.
And this can be helpful for figuring out where to invoke the debugger.
"""

import inspect
import sys


def __get_watchstring(wvars, frame):
    """Utility method to pretty-print the watched variables in a frame."""
    watching = ""
    watchvars = ""
    frame_vars = frame.f_locals
    for v in wvars:
        if v in frame_vars:
            watchvars += " {}={}".format(v, frame_vars[v])
        elif v in frame_vars.get('kwargs', {}):
            watchvars += " kwargs[{}]={}".format(v, frame_vars['kwargs'][v])
    watching = "watching{}".format(watchvars) if watchvars else ""
    if watching:
        watching = "\n" + " "*10 + watching
    return watching


# TODO: We should print timestamp and thread ID
# TODO: We should have a way to output a JSON structure
def wtf(wvars=[], callstack=4, to_stream=None, to_out=True, 
        to_err=False, flush=True):
    """Pretty-print commonly-needed information about the call stack.

    wvars = a list of strings giving the names of variables whose values
            should be printed after whatever call depth they appear
    callstack = the number of callers to list; defaults to 4, which seems 
            useful. Set to 0 to print the entire callstack.
    to_stream = an open file-like object to which output should be written.
    to_out = a boolean describing whether to print to stdout. default True.
    to_err = a boolean describing whether to print to stderr. default False.
    flush = default True. If True, flush all I/o buffers after every write.
    """
    outerframes = inspect.getouterframes(inspect.currentframe())
    wtf_place = ""
    callers = ""
    watching = ""
    # Add 2 to requested callstack depth to account for wtf itself
    # and also the location in which wtf was inserted
    callstack = callstack+2 if callstack > 0 else len(outerframes)
    for i in range(callstack):
        frame, c_file, c_line, c_fun,c_src, ignore = outerframes[i]
        watching = __get_watchstring(wvars, frame)
        if i == 1:
            wtf_place = "{}:{}:{}{}".format(c_file, c_line, c_fun, watching)
        if i > 1:
            callers += "    {}:{}:{}{}\n".format(c_file, c_line, c_fun, watching)
    output = "****DEBUG: {}\n{}{}\n".format(wtf_place, watching, callers)
    if to_stream:
        to_stream.write(output)
        if flush:
            to_stream.flush()
    if to_out:
        sys.stdout.write(output)
        if flush:
            sys.stdout.flush()
    if to_err:
        sys.stderr.write(output)
        if flush:
            sys.stderr.flush()

