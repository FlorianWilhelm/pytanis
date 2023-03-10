"""Some helper functions for HiGHS (https://highs.dev/)

`pyomo` and `highspy` need to be installed, consider `pip install 'pytanis[all]'`.

ToDo:
    * Introduce a function `check_model_vars` that checks the names of variables and sets to be alphanumeric
      before reading in a solution in `set_solution_from_file`.
"""
import re
from typing import Iterator, Tuple

from pyomo.contrib.appsi.solvers import Highs
from pyomo.core.base.PyomoModel import ConcreteModel


def read_sol_file(file_name: str) -> Iterator[Tuple[str, float]]:
    """Read a solution file from HiGHS solver with default output style

    Attention: We assume here that your variable names are alphanumeric!
               No underscores, no dashes, etc.!
    """
    line_re = re.compile(r"(\w+)(?:\((\w+)\))?(_binary_indicator_var)? ([.\w-]+)")

    with open(file_name) as fh:
        while True:
            line = fh.readline()
            if line.startswith("# Columns"):
                break
        for line in fh.readlines():
            if line.startswith("#"):
                break
            if (match_obj := line_re.match(line.strip())) is None:
                raise RuntimeError(f"Could not interpret line: {line}")
            else:
                var_name, idx, binary, val = match_obj.groups()
            val = float(val)
            binary = binary.replace('_', '.', 1) if binary else ""

            if idx is None:
                yield f"{var_name}{binary}", val
            else:
                idx = idx.replace('_', ',')
                yield f"{var_name}[{idx}]{binary}", val


def set_solution_from_file(model: ConcreteModel, file_name: str):
    """Given a HiGHS solution file set the variables of a Pyomo model accordingly.

    This is a workaround to set a Pyomo model's variables to the solution
    from a HiGHS solution file.
    """
    # just to initialize we read it in using HiGHS. The result is incorrect though,
    # as the order of variables is mixed up quite often. We fix this below!
    opt = Highs()
    opt.set_instance(model)
    opt._solver_model.readSolution(file_name, 0)
    opt._sol = opt._solver_model.getSolution()
    opt.load_vars()

    # read the actual mapping of the variable names to the values
    file_sol = {name: val for name, val in read_sol_file(file_name)}

    # overwrite the values of the variables again using the symbolic names from the file
    for v, ref_info in opt._referenced_variables.items():
        using_cons, using_sos, using_obj = ref_info
        if using_cons or using_sos or (using_obj is not None):
            var = opt._vars[v][0]
            var.set_value(file_sol[var.name], skip_validation=True)
