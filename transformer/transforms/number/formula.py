from transformer.registry import register
from transformer.transforms.base import BaseTransform
from transformer.transforms.number.formula_tokenizer import shunting_yard, FunctionNode, OperatorNode, OperandNode, RangeNode
from transformer.util import math, int_or_float

import fractions
import operator


def get_default_functions():
    """ generate a mapping of default functions allowed for evaluation """
    return {
        'MAX': Func(0, wrap_reduce(max)),
        'MIN': Func(0, wrap_reduce(min)),
        'MOD': Func(2, operator.mod),
        'SQRT': Func(1, math.sqrt),
        'POW': Func(2, math.pow),
        'ABS': Func(1, operator.abs),
        'GCD': Func(-2, wrap_reduce(fractions.gcd)),
        'LCM': Func(-2, wrap_reduce(func_lcm)),
        'CEILING': Func(-1, math.ceil),
        'FLOOR': Func(-1, math.floor),
        'ROUND': Func(-1, round),
        'IF': Func(-2, func_if),
        'AND': Func(-1, wrap_varlist(all)),
        'OR': Func(-1, wrap_varlist(any)),
        'NOT': Func(1, operator.not_),
        'TRUE': Func(0, lambda: 1),
        'FALSE': Func(0, lambda: 0),
    }


def get_default_operators():
    """ generate a mapping of default operators allowed for evaluation """
    return {
        'u-': Func(1, operator.neg),             # unary negation
        'u%': Func(1, lambda a: a / float(100)), # unary percentage
        '+': Func(2, operator.add),
        '-': Func(2, operator.sub),
        '/': Func(2, operator.truediv),
        '*': Func(2, operator.mul),
        '=': Func(2, operator.eq),
        '<>': Func(2, lambda a, b: not operator.eq(a, b)),
        '>': Func(2, operator.gt),
        '<': Func(2, operator.lt),
        '>=': Func(2, operator.ge),
        '<=': Func(2, operator.le),
    }


def evaluate(formula, functions=None, operators=None):
    """
    evaluate an excel-style formula using the functions and operators provided

    """
    if functions is None:
        functions = get_default_functions()
    if operators is None:
        operators = get_default_operators()

    # first, parse the formula into reverse polish notation
    rpn = shunting_yard(formula)

    # check the nodes to make sure they are valid
    for i, n in enumerate(rpn):
        key = str(n).upper()
        if isinstance(n, RangeNode):
            if n.token.tsubtype not in ('logical', 'text'):
                raise Exception('Invalid Syntax: Only numeric values are allowed')
        if isinstance(n, FunctionNode) and key not in functions:
            raise Exception('Unknown Function: {}'.format(n))
        if isinstance(n, OperatorNode) and key not in operators and 'u{}'.format(key) not in operators:
            raise Exception('Unknown Operation: {}'.format(n))

    # evaluate the reverse polish notation
    stack = []
    for n in rpn:
        if isinstance(n, OperandNode):
            stack.append(eval_operand(n))

        if isinstance(n, FunctionNode):
            num = n.num_args
            func = functions.get(str(n).upper())
            if func.n < 0 and num < -func.n:
                raise Exception('Invalid Formula: {} requires at least {} arguments'.format(str(n), -func.n))
            if func.n > 0 and num != func.n:
                raise Exception('Invalid Formula: {} requires {} arguments ({} provided)'.format(str(n), func.n, num))
            stack, args = stack[:-num], stack[-num:]
            stack.append(func.f(*args))

        if isinstance(n, OperatorNode):
            num = 2 if n.token.ttype.endswith('infix') else 1
            key = str(n).upper()
            if num == 1:
                key = 'u{}'.format(key)
            op = operators.get(key)
            if op.n < 0 and num < -op.n:
                raise Exception('Invalid Formula: {} requires at least {} arguments'.format(str(n), -op.n))
            if op.n > 0 and num != op.n:
                raise Exception('Invalid Formula: {} requires {} arguments ({} provided)'.format(str(n), op.n, num))
            stack, args = stack[:-num], stack[-num:]
            stack.append(op.f(*args))

    # if there's any stack left...the formula is invalid
    # all formulas should reduce to a single value
    if len(stack) > 1:
        raise Exception('Invalid Formula')

    return stack.pop()


class Func(object):
    """
    wrapper of a function and it's argument count

    if n > 0 then the function call requires n arguments
    if n =< 0 then the function call requires -n or more arguments
    """
    def __init__(self, n, f):
        self.n = n
        self.f = f


def eval_operand(n):
    """ evaluate an operand into a numeric value """
    if not isinstance(n, OperandNode):
        return None
    if n.token.tsubtype == 'number':
        return int_or_float(float(n.token.tvalue))
    if n.token.tsubtype == 'logical':
        return 1 if 'TRUE' in n.token.tvalue else 0
    # if we want to use allow text output, this will be needed
    # if n.token.tsubtype == 'text':
    #     return n.token.tvalue
    raise Exception('Invalid Syntax: Only numeric values allowed ({} provided)'.format(n.token.tsubtype))


def wrap_reduce(f):
    """ wrap a 2 argument function as a multi-argument function via reduce """
    def _wrap(*args):
        if len(args) <= 2:
            return f(*args)
        return reduce(f, args)
    return _wrap


def wrap_varlist(f):
    """ wrap a 1 argument function as a multi-argument function via list """
    def _wrap(*args):
        return f(args)
    return _wrap


def func_if(test, true_value, *args):
    """ functor for ifs """
    false_value = args[0] if args else None
    return true_value if test else false_value


def func_lcm(a, b):
    """ functor for lowest common multiple """
    return a * b // fractions.gcd(a, b)


class NumberFormulaTransform(BaseTransform):
    category = 'number'
    name = 'formula'
    label = 'Number Formula'
    help_text = 'Transform a number with an Excel-style formula.'

    def transform(self, formula):
        return evaluate(formula)

    def all_fields(self, *args, **kwargs):
        input_field = self.build_input_field()
        input_field['label'] = 'Formula'
        input_field['help_text'] = 'Excel-style formula to evaluate'
        return [input_field]

register(NumberFormulaTransform())
