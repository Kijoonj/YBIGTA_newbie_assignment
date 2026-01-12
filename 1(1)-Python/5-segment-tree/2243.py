from lib import SegmentTree
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