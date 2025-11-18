"""Plugin implementations

This module contains the implementation of some features

- benchmarking
- pruning
"""

from mythril2.laser.plugin.plugins.benchmark import BenchmarkPluginBuilder
from mythril2.laser.plugin.plugins.call_depth_limiter import CallDepthLimitBuilder
from mythril2.laser.plugin.plugins.coverage.coverage_plugin import CoveragePluginBuilder
from mythril2.laser.plugin.plugins.coverage_metrics import CoverageMetricsPluginBuilder
from mythril2.laser.plugin.plugins.dependency_pruner import DependencyPrunerBuilder
from mythril2.laser.plugin.plugins.instruction_profiler import InstructionProfilerBuilder
from mythril2.laser.plugin.plugins.mutation_pruner import MutationPrunerBuilder
from mythril2.laser.plugin.plugins.state_merge import StateMergePluginBuilder
from mythril2.laser.plugin.plugins.summary import SymbolicSummaryPluginBuilder
from mythril2.laser.plugin.plugins.trace import TraceFinderBuilder
