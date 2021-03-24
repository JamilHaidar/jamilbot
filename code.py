class Solution:
    def calcEquation(self, equations: List[List[str]], values: List[float], queries: List[List[str]]) -> List[float]:
        def search(key,target):
            
            if not(key in graph):
                return -1.0
            
            if key == target:return 1.0
            
            visited[key]=True
            
            for neighbor in graph[key]:
                if(not(visited[neighbor])):
                    if target == neighbor:
                        return graph[key][neighbor]
                    ans = search(neighbor,target)
                    if ans!=-1.0:
                        return graph[key][neighbor]*ans    
            return -1.0

        result = []
        graph = dict()
        visited = dict()

        for index,pair in enumerate(equations):
            key,target = pair
            visited[key]=False
            visited[target]=False

            if not(key in graph):
                graph[key] = dict()
            graph[key][target]=values[index]
            
            if not(target in graph):
                graph[target] = dict()
            graph[target][key]=1.0/values[index]

        for query in queries:
            result.append(search(query[0],query[1]))
            for key in visited:
                visited[key]=False
        return result
        