from __future__ import annotations
import copy
from collections import deque
from collections import defaultdict
from typing import DefaultDict, List


"""
TODO:
- __init__ 구현하기
- add_edge 구현하기
- dfs 구현하기 (재귀 또는 스택 방식 선택)
- bfs 구현하기
"""


class Graph:
    def __init__(self, n: int) -> None:
        """
        그래프 초기화
        n: 정점의 개수 (1번부터 n번까지)
        """
        self.n : int = n
        # 구현하세요!
        self.graph : list[list[int]] = [[] for _ in range(n+1)]

    
    def add_edge(self, u: int, v: int) -> None:
        """
        양방향 간선 추가
        """
        # 구현하세요!
        self.graph[u].append(v)
        self.graph[v].append(u)
    
    def dfs(self, start: int) -> list[int]:
        """
        깊이 우선 탐색 (DFS)
        
        구현 방법 선택:
        1. 재귀 방식: 함수 내부에서 재귀 함수 정의하여 구현
        2. 스택 방식: 명시적 스택을 사용하여 반복문으로 구현
        """
        # 구현하세요!
        visited : list[bool] = [False]*(self.n+1)
        res : list[int] = []
        
        def _dfs(node : int) -> None:
            visited[node] = True
            res.append(node)
            for next_node in sorted(self.graph[node]):
                if visited[next_node]:
                    continue
                _dfs(next_node)
        _dfs(start)

        return res
        
        
    
    def bfs(self, start: int) -> list[int]:
        """
        너비 우선 탐색 (BFS)
        큐를 사용하여 구현
        """
        # 구현하세요!
        visited : list[bool] = [False]*(self.n+1)
        res : list[int] = []

        queue : deque[int] = deque()
        queue.append(start)
        visited[start] = True

        while queue:
            cur : int = queue.popleft()
            res.append(cur)
            for next_node in sorted(self.graph[cur]):
                if visited[next_node]:
                    continue
                visited[next_node] = True
                queue.append(next_node)

        return res
    

    def search_and_print(self, start: int) -> None:
        """
        DFS와 BFS 결과를 출력
        """
        dfs_result = self.dfs(start)
        bfs_result = self.bfs(start)
        
        print(' '.join(map(str, dfs_result)))
        print(' '.join(map(str, bfs_result)))
