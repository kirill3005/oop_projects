from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Set, Optional, Union
from abc import ABC, abstractmethod
import math



class Move(ABC):
    name: str

    @abstractmethod
    def apply(self, s: int) -> int:
        pass


@dataclass(frozen=True)
class AddMove(Move):
    k: int
    name: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "name", f"+{self.k}")

    def apply(self, s: int) -> int:
        return s + self.k


@dataclass(frozen=True)
class SubtractMove(Move):
    k: int
    name: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "name", f"-{self.k}")

    def apply(self, s: int) -> int:
        return s - self.k


@dataclass(frozen=True)
class MultiplyMove(Move):
    factor: int
    name: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "name", f"*{self.factor}")

    def apply(self, s: int) -> int:
        return s * self.factor


@dataclass(frozen=True)
class DivideMove(Move):
    divisor: int
    mode: str = "floor"
    name: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "name", f"//{self.divisor}({self.mode})")

    def apply(self, s: int) -> int:
        d = self.divisor
        if self.mode == "floor":
            return s // d
        elif self.mode == "ceil":
            return -(-s // d)
        elif self.mode == "round":
            return int(round(s / d))
        else:
            raise ValueError(f"Unknown divide mode: {self.mode}")


@dataclass(frozen=True)
class FuncMove(Move):
    f: Callable[[int], int]
    label: str = "f(s)"
    name: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "name", self.label)

    def apply(self, s: int) -> int:
        return self.f(s)


@dataclass(frozen=True)
class TerminalCondition:
    threshold: int
    comparator: str = "le"

    def is_terminal(self, s: int) -> bool:
        if self.comparator == "le":
            return s <= self.threshold
        elif self.comparator == "ge":
            return s >= self.threshold
        else:
            raise ValueError("Comparator must be 'le' or 'ge'")



@dataclass
class Game:
    terminal: TerminalCondition
    moves: List[Move]
    s_min: int
    s_max: int
    monotonic: str = "decreasing"

    def next_states(self, s: int) -> List[int]:
        return sorted({m.apply(s) for m in self.moves})



class Analyzer:
    def __init__(self, game: Game):
        self.g = game

    def classify_up_to_k2(self) -> Dict[int, str]:
        g = self.g
        t = g.terminal

        labels: Dict[int, str] = {}

        W: Dict[int, Set[int]] = {1: set(), 2: set()}
        L: Dict[int, Set[int]] = {0: set(), 1: set(), 2: set()}

        if t.comparator == "le":
            L[0] = set(range(g.s_min, min(g.s_max, t.threshold) + 1))
            state_iter = range(t.threshold + 1, g.s_max + 1)
        else:
            L[0] = set(range(max(g.s_min, t.threshold), g.s_max + 1))
            state_iter = range(min(g.s_max, t.threshold - 1), g.s_min - 1, -1)

        for s in state_iter:
            dests = g.next_states(s)

            if any(t.is_terminal(d) for d in dests):
                labels[s] = "W1"
                W[1].add(s)
                continue

            if dests and all(d in W[1] for d in dests):
                labels[s] = "L1"
                L[1].add(s)
                continue

            if any(d in L[1] for d in dests):
                labels[s] = "W2"
                W[2].add(s)
                continue

            if dests and all((d in W[1] or d in W[2]) for d in dests):
                labels[s] = "L2"
                L[2].add(s)
                continue

            labels[s] = "UNRESOLVED"

        return labels

    def solve_19_20_21(self) -> Dict[str, Union[int, List[int], None]]:
        labels = self.classify_up_to_k2()

        s19 = min((s for s, lab in labels.items() if lab == "L1"), default=None)

        w2_list = sorted(s for s, lab in labels.items() if lab == "W2")
        s20 = w2_list[:2]

        s21 = min((s for s, lab in labels.items() if lab == "L2"), default=None)

        return {"19": s19, "20": s20, "21": s21}