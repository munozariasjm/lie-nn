import itertools
import re
from dataclasses import dataclass
from typing import Iterator

import numpy as np

import lie_nn as lie
from scipy.linalg import sqrtm
from ..irrep import Irrep
from .sl2c import SL2C


@dataclass(frozen=True)
class SO13(Irrep):  # TODO(ilyes): think if this class shoulb be a subclass of SL2C. mario: Not anymore
    l: int  # First integer weight
    k: int  # Second integer weight

    def __post_init__(rep):
        assert isinstance(rep.l, int)
        assert isinstance(rep.k, int)
        assert rep.l >= 0
        assert rep.k >= 0
        assert (rep.l + rep.k) % 2 == 0

    @classmethod
    def from_string(cls, s: str) -> "SO13":
        m = re.match(r"\((\d+),(\d+)\)", s.strip())
        assert m is not None
        return cls(l=int(m.group(1)), k=int(m.group(2)))

    def __mul__(rep1: "SO13", rep2: "SO13") -> Iterator["SO13"]:
        for rep in SL2C(l=rep1.l, k=rep1.k) * SL2C(l=rep2.l, k=rep2.k):
            yield SO13(l=rep.l, k=rep.k)

    @classmethod
    def clebsch_gordan(cls, rep1: "SO13", rep2: "SO13", rep3: "SO13") -> np.ndarray:
        # Call the generic implementation
        return lie.clebsch_gordan(lie.GenericRep.from_rep(rep1), rep2, rep3, round_fn=lie.util.round_to_sqrt_rational)

    @property
    def dim(rep: "SO13") -> int:
        return SL2C(l=rep.l, k=rep.k).dim

    def is_scalar(rep: "SO13") -> bool:
        """Equivalent to ``l == 0 and k == 0``"""
        return rep.l == 0 and rep.k == 0

    def __lt__(rep1: "SO13", rep2: "SO13") -> bool:
        return (rep1.l + rep1.k, rep1.l) < (rep2.l + rep2.k, rep2.l)

    @classmethod
    def iterator(cls) -> Iterator["SO13"]:
        for sum in itertools.count(0, 2):
            for l in range(0, sum + 1):
                yield SO13(l=l, k=sum - l)

    def discrete_generators(rep: "SO13") -> np.ndarray:
        return np.zeros((0, rep.dim, rep.dim))

    def continuous_generators(rep: "SO13") -> np.ndarray:
        X = SL2C(rep.l, rep.k).continuous_generators().copy()

        # Change algebra from SL2C to SO13
        X[3:] *= 1j

        return X

        # TODO(mario): fix this
        # Make the generators explicitly real, if possible
        S = lie.util.infer_change_of_basis(np.conjugate(X), X) * np.sqrt(rep.dim)
        if S.shape[0] == 0:
            assert rep.l != rep.k
            return X
        assert rep.l == rep.k
        W = sqrtm(S[0])
        iW = np.linalg.inv(W)
        assert np.allclose(W @ iW, np.eye(rep.dim))
        X = W @ X @ iW
        assert np.allclose(X.imag, 0)
        return X.real

    def algebra(rep=None) -> np.ndarray:
        # [X_i, X_j] = A_ijk X_k
        algebra = np.zeros((6, 6, 6))

        # for generators J_0, J_1, J_2, K_0, K_1, K_2
        for i, j, k in itertools.permutations((0, 1, 2)):
            algebra[i, j, k] = lie.util.sign((i, j, k))  # [J_i, J_j] = eps_ijk J_k
            algebra[3 + i, 3 + j, k] = -lie.util.sign((i, j, k))  # [K_i, K_j] = -eps_ijk J_k
            algebra[i, 3 + j, 3 + k] = lie.util.sign((i, j, k))  # [J_i, K_j] = eps_ijk K_k
            algebra[3 + i, j, 3 + k] = lie.util.sign((i, j, k))  # [K_i, J_j] = eps_ijk K_k

        return algebra
