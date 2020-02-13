class PriorityQueue(object):
    def __init__(self):
        self.queue = []

    def __str__(self):
        return " ".join([str(i) for i in self.queue])

    @property
    def isempty(self):
        return len(self.queue) == 0

    def insert(self, data):
        self.queue.append(data)

    def delete(self):
        max = 0
        try:
            for i in range(len(self.queue)):
                if self.queue[i] > self.queue[max]:
                    max = i
                item = self.queue[max]
                del self.queue[max]
                return item
        except IndexError:
            print('Index Out of bound')
            exit(404)
