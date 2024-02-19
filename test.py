a = [1,2,3,4]

# from functools import reduce
# print(reduce(lambda x,y: x+y, a))

# b = [2,4,6,8]
# print(list(map(lambda x,y: (x,y), a,b)))

# import re
# def is_valid_email(str):
#     pattern = r'^[a-zA-Z0-9.+-]+@[a-zA-Z0-9.+-]+\.[a-zA-Z0-9.-]+'
#     return re.match(pattern, str) is not None

# test_emails = ["example@example.com", "invalid-email", "example@example", "example@.com"]
# validity = {email: is_valid_email(email) for email in test_emails}
# print(validity)

import heapq as hp

class InfiniteStacks:
    def __init__(self, capacity):
        self.data = []
        self.capacity = capacity
        self.available_heap = []
    
    def show_table(self):
        print(self.data)

    def push_left(self, item):        
        if not self.data or not self.available_heap:
            self.data.append([])
            self.available_heap.append(len(self.data)-1)

        self.data[self.available_heap[0]].append(item)
        if len(self.data[-1]) == self.capacity:
            hp.heappop(self.available_heap)

    def pop_right(self):
        if not self.data:
            return -1
        
        for i,stk in reversed(list(enumerate(self.data))):
            if not stk:
                self.data.pop()
            else:
                stk.pop()
                hp.heappush(i)
        item = self.data[-1].pop()
    
        if not self.data[-1]:
            self.data.pop()

        return item

    def pop_at_index(self, index):
        if index >= len(self.data) or not self.data[index]:
            return -1

        return self.data[index].pop()

# Example usage
stacks = InfiniteStacks(2)
stacks.push_left(1)
stacks.push_left(2)
stacks.push_left(3)
stacks.push_left(4)  # Starts a new stack
stacks.show_table()
print(stacks.pop_right())  # Pops from the first stack (3)
print(stacks.pop_at_index(1))  # Pops from the second stack (4), if it exists
stacks.show_table()