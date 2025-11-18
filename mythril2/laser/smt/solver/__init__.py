import z3

from mythril2.laser.smt.solver.independence_solver import IndependenceSolver
from mythril2.laser.smt.solver.solver import BaseSolver, Optimize, Solver
from mythril2.laser.smt.solver.solver_statistics import SolverStatistics
from mythril2.support.support_args import args

if args.parallel_solving:
    z3.set_param("parallel.enable", True)
