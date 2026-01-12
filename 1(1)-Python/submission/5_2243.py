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
        self.tree : list[int] = [0]*(2*self.n)
    
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


def main() -> None:
    n:int = int(sys.stdin.readline())
    tree:SegmentTree = SegmentTree([0]*1048576)

    for _ in range(n):
        temp : list[int]  = list(map(int,sys.stdin.readline().split()))
        if len(temp) == 3:
            mode:int = temp[0]
            flavor:int = temp[1]
            count:int = temp[2]
            tree.update(flavor,count)
        else:
            mode = temp[0]
            k : int = temp[1]
            print(tree.getKthFlavor(k))


if __name__ == "__main__":
    main()