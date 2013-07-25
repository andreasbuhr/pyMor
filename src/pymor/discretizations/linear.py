# -*- coding: utf-8 -*-
# This file is part of the pyMor project (http://www.pymor.org).
# Copyright Holders: Felix Albrecht, Rene Milk, Stephan Rave
# License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

import numpy as np

from pymor.core import defaults
from pymor.la import NumpyVectorArray
from pymor.tools import selfless_arguments
from pymor.operators import OperatorInterface
from pymor.discretizations.interfaces import DiscretizationInterface


class StationaryLinearDiscretization(DiscretizationInterface):
    '''Generic class for discretizations of stationary linear problems.

    This class describes discrete problems given by the equation ::

        L_h(μ) ⋅ u_h(μ) = f_h(μ)

    which is to be solved for u_h.

    Parameters
    ----------
    operator
        The operator L_h given as a `LinearOperator`.
    rhs
        The functional f_h given as a `LinearOperator` with `dim_range == 1`.
    visualizer
        A function visualize(U) which visualizes the solution vectors. Can be None,
        in which case no visualization is availabe.
    name
        Name of the discretization.

    Attributes
    ----------
    operator
        The operator L_h. A synonym for operators['operator'].
    operators
        Dictionary of all operators contained in this discretization. The idea is
        that this attribute will be common to all discretizations such that it can
        be used for introspection. Compare the implementation of `reduce_generic_rb`.
        For this class, operators has the keys 'operator' and 'rhs'.
    rhs
        The functional f_h. A synonym for operators['rhs'].
    '''

    def __init__(self, operator, rhs, products=None, parameter_space=None, estimator=None, visualizer=None,
                 caching='disk', name=None):
        assert isinstance(operator, OperatorInterface) and operator.linear
        assert isinstance(rhs, OperatorInterface) and rhs.linear
        assert operator.dim_source == operator.dim_range == rhs.dim_source
        assert rhs.dim_range == 1

        operators = {'operator': operator, 'rhs': rhs}
        super(StationaryLinearDiscretization, self).__init__(operators=operators, products=products,
                                                             estimator=estimator, visualizer=visualizer,
                                                             caching=caching, name=name)
        self.operator = operator
        self.rhs = rhs
        self.operators = operators
        self.solution_dim = operator.dim_range
        self.build_parameter_type(inherits=(operator, rhs))
        self.parameter_space = parameter_space
        self.lock()

    with_arguments = set(selfless_arguments(__init__)).union(['operators'])

    def with_(self, **kwargs):
        assert set(kwargs.keys()) <= self.with_arguments
        assert 'operators' not in kwargs or 'rhs' not in kwargs and 'operator' not in kwargs
        assert 'operators' not in kwargs or set(kwargs['operators'].keys()) <= set(('operator', 'rhs'))

        if 'operators' in kwargs:
            kwargs.update(kwargs.pop('operators'))

        return self._with_via_init(kwargs)

    def _solve(self, mu=None):
        mu = self.parse_parameter(mu)

        # explicitly checking if logging is disabled saves the expensive str(mu) call
        if not self.logging_disabled:
            sparse = 'sparsity unknown' if getattr(self.operator, 'sparse', None) is None \
                else ('sparse' if self.operator.sparse else 'dense')
            self.logger.info('Solving {} ({}) for {} ...'.format(self.name, sparse, mu))

        return self.operator.apply_inverse(self.rhs.as_vector(mu), mu=mu)
