class Node:
    def __init__(self, content):
        self.value = content
        self.next = None
        self.previous = None

    def __str__(self):
        return ('CONTENT:{}\n'.format(self.value))

    __repr__=__str__


class ContentItem:
    def __init__(self, cid, size, header, content):
        self.cid = cid
        self.size = size
        self.header = header
        self.content = content

    def __str__(self):
        return f'CONTENT ID: {self.cid} SIZE: {self.size} HEADER: {self.header} CONTENT: {self.content}'

    __repr__=__str__

    def __eq__(self, other):
        if isinstance(other, ContentItem):
            return self.cid == other.cid and self.size == other.size and self.header == other.header and self.content == other.content
        return False

    def __hash__(self):
        return sum(ord(c) for c in self.header) % 3

class CacheList:
    def __init__(self, size):
        self.head = None
        self.tail = None
        self.maxSize = size
        self.remainingSpace = size
        self.numItems = 0

    def __str__(self):
        listString = ""
        current = self.head
        while current is not None:
            listString += "[" + str(current.value) + "]\n"
            current = current.next
        return 'REMAINING SPACE:{}\nITEMS:{}\nLIST:\n{}'.format(self.remainingSpace, self.numItems, listString)  

    __repr__=__str__

    def __len__(self):
        return self.numItems
    
    #Add a content item to the cache with specified eviction policy
    def put(self, content, evictionPolicy):
        current = self.head
        exists = False
        while current and not exists:
            if current.value.cid == content.cid:
                exists = True
            else:
                current = current.next
        
        if exists:
            return f'Content {content.cid} already in cache, insertion not allowed'

        if content.size > self.maxSize:
            return 'Insertion not allowed'
        
        while self.remainingSpace < content.size:
            if evictionPolicy == 'lru':
                self.lruEvict()
            elif evictionPolicy == 'mru':
                self.mruEvict()
            else:
                return 'Invalid eviction policy'

        newNode = Node(content)
        newNode.next = self.head
        if self.head:
            self.head.previous = newNode
        self.head = newNode
        if self.tail is None: 
            self.tail = newNode

        self.numItems += 1
        self.remainingSpace -= content.size
        return f'INSERTED: {content}'


    def __contains__(self, cid):
        prev = None
        current = self.head
        while current is not None:
            if current.value.cid == cid:
                if prev: 
                    #Detach current
                    prev.next = current.next
                    if current.next:
                        current.next.previous = prev
                    else: 
                        self.tail = prev
                        
                    #Current to front
                    current.next = self.head
                    current.previous = None
                    if self.head:
                        self.head.previous = current
                    self.head = current
                    
                    if self.tail is None:
                        self.tail = current
                        
                return True
            prev = current
            current = current.next
        return False

    #Update the content item with the given CID in CacheList
    def update(self, cid, content):
        if not self.__contains__(cid):
            return 'Cache miss!'
        
        if self.remainingSpace + self.head.value.size >= content.size:
            self.remainingSpace += self.head.value.size - content.size
            self.head.value = content
            return f'UPDATED: {content}'
        else:
            return f'Not enough space to update content {cid}'

    def mruEvict(self):
        if self.head is None:
            return
        
        self.remainingSpace += self.head.value.size
        if self.head == self.tail:  
            self.head = self.tail = None
        else:
            self.head = self.head.next
            self.head.previous = None
        self.numItems -= 1

    
    def lruEvict(self):
        if self.tail is None:
            return
        
        self.remainingSpace += self.tail.value.size
        if self.tail == self.head:  
            self.head = self.tail = None
        else:
            self.tail = self.tail.previous
            self.tail.next = None
        self.numItems -= 1

    
    def clear(self):
        self.head = self.tail = None
        self.remainingSpace = self.maxSize
        self.numItems = 0
        return 'Cleared cache!'


class Cache:
    def __init__(self, lst_capacity):
        self.hierarchy = [CacheList(lst_capacity), CacheList(lst_capacity), CacheList(lst_capacity)]
        self.size = 3
    
    def __str__(self):
        return ('L1 CACHE:\n{}\nL2 CACHE:\n{}\nL3 CACHE:\n{}\n'.format(self.hierarchy[0], self.hierarchy[1], self.hierarchy[2]))
    
    __repr__=__str__

    def clear(self):
        for item in self.hierarchy:
            item.clear()
        return 'Cache cleared!'

    
    def insert(self, content, evictionPolicy):
        level = hash(content) % self.size  
        return self.hierarchy[level].put(content, evictionPolicy)


    def __getitem__(self, content):
        level = hash(content) % self.size  
        current = self.hierarchy[level].head
        while current:
            if current.value.cid == content.cid:
                return current
            current = current.next
        return 'Cache miss!'


    def __setitem__(self, cid, content):
        level = hash(content) % self.size
        self.hierarchy[level].update(cid, content)