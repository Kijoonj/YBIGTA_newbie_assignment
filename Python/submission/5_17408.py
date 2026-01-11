from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Callable


"""
TODO:
- SegmentTree 구현하기
"""


T = TypeVar("T")
U = TypeVar("U")


class SegmentTree(Generic[T, U]):
    # 구현하세요!
    def __init__(self,arr : list[int]) -> None:
        """
        Tree initialization
        """
        self.arr : list[int] = arr
        self.n : int = len(self.arr)
        self.tree : list[int] = [0]*(2*n)
    
    def update(self,idx:int, val:int) -> None:
        """
        Adds val to idx-th element(1-indexed) and updates corresponding parents
        """
        pos : int = idx-1+self.n
        self.arr[idx-1] += val
        self.tree[pos] += val
        pos //= 2

        while pos > 0:
            self.tree[pos] = self.tree[pos*2] + self.tree[pos*2+1]
            pos //= 2
    
    def getKthFlavor(self,k:int) -> int:
        """
        Returns flavor(1-indexed) of K-th candy 
        """
        res : int = 1 #starts at the root node
        k -= self.tree[res]

        while res < self.n:
            left_node : int = self.tree[res*2]
            right_node : int = self.tree[res*2+1]

            if k <= left_node:
                res *= 2
            else:
                k -= left_node
                res = res*2 + 1
        flavor:int = res-self.n+1
        self.update(flavor,-1) # remove 1 candy
        
        return flavor




import sys


"""
TODO:
- 일단 SegmentTree부터 구현하기
- main 구현하기
"""


class Pair(tuple[int, int]):
    """
    힌트: 2243, 3653에서 int에 대한 세그먼트 트리를 만들었다면 여기서는 Pair에 대한 세그먼트 트리를 만들 수 있을지도...?
    """
    def __new__(cls, a: int, b: int) -> 'Pair':
        return super().__new__(cls, (a, b))

    @staticmethod
    def default() -> 'Pair':
        """
        기본값
        이게 왜 필요할까...?
        """
        return Pair(0, 0)

    @staticmethod
    def f_conv(w: int) -> 'Pair':
        """
        원본 수열의 값을 대응되는 Pair 값으로 변환하는 연산
        이게 왜 필요할까...?
        """
        return Pair(w, 0)

    @staticmethod
    def f_merge(a: Pair, b: Pair) -> 'Pair':
        """
        두 Pair를 하나의 Pair로 합치는 연산
        이게 왜 필요할까...?
        """
        return Pair(*sorted([*a, *b], reverse=True)[:2])

    def sum(self) -> int:
        return self[0] + self[1]


def main() -> None:
    # 구현하세요!
    pass


if __name__ == "__main__":
    main()