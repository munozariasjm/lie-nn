import itertools
from typing import Iterator

import numpy as np

from . import IrrepFamily, static_jax_pytree
from ._so3_real import SO3Rep


@static_jax_pytree
class O3Rep(IrrepFamily):
    l: int  # non-negative integer
    p: int  # 1 or -1

    def __mul__(rep1: "O3Rep", rep2: "O3Rep") -> Iterator["O3Rep"]:
        assert isinstance(rep2, O3Rep)
        p = rep1.p * rep2.p
        return [O3Rep(l=l, p=p) for l in range(abs(rep1.l - rep2.l), rep1.l + rep2.l + 1, 1)]

    @classmethod
    def clebsch_gordan(cls, rep1: "O3Rep", rep2: "O3Rep", rep3: "O3Rep") -> np.ndarray:
        if rep1.p * rep2.p == rep3.p:
            return SO3Rep.clebsch_gordan(rep1, rep2, rep3)
        else:
            return np.zeros((0, rep1.dim, rep2.dim, rep3.dim))

    @property
    def dim(rep: "O3Rep") -> int:
        return 2 * rep.l + 1

    @classmethod
    def iterator(cls) -> Iterator["O3Rep"]:
        for l in itertools.count(0):
            yield O3Rep(l=l, p=1)
            yield O3Rep(l=l, p=-1)

    def continuous_generators(rep: "O3Rep") -> np.ndarray:
        return SO3Rep(l=rep.l).continuous_generators()

    def discrete_generators(rep: "O3Rep") -> np.ndarray:
        return rep.p * np.eye(rep.dim)[None]

    @classmethod
    def algebra(cls) -> np.ndarray:
        return SO3Rep.algebra()
