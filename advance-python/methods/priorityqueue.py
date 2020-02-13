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
        max_value = 0
        try:
            for i in range(len(self.queue)):
                if self.queue[i] > self.queue[max_value]:
                    max_value = i
                item = self.queue[max_value]
                del self.queue[max_value]
                return item
        except IndexError:
            print('Index Out of bound')
            exit(404)


if __name__ == '__main__':
    myqueue = PriorityQueue()
    myqueue.insert(12)
    myqueue.insert(1)
    myqueue.insert(14)
    myqueue.insert(7)
    print(myqueue)
    while not myqueue.isempty:
        print(myqueue.delete())
