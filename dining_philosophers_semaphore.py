# In[ ]:


import threading
import time
import sys
import numpy


# In[ ]:


number_of_process = 5
number_of_entries = 5

RESOURCE_MESSAGE = True
STATUS_MESSAGE = True

latency = [0 for i in range(number_of_process)]


# In[ ]:


class Counting_semaphore(object):
    def __init__(self, sem_count):
        self.sem_lock = threading.Condition(threading.Lock())
        self.sem_count = sem_count

    def enter(self,pid):
        with self.sem_lock:
            while self.sem_count == 0:
                self.sem_lock.wait()
                latency[pid] += 2
            self.sem_count -= 1
            latency[pid] += 2
              
    def exit(self,pid):
        with self.sem_lock: 
            self.sem_count += 1
            self.sem_lock.notify() 


# In[ ]:


class Process(threading.Thread):
    def __init__(self, pid, first, second, sem):
        threading.Thread.__init__(self)
        self.pid = pid           
        self.first = first
        self.second = second
        self.sem = sem

    def run(self):
        for i in range(number_of_entries): 
            latency[self.pid] += 1
            self.sem.enter(self.pid)       
            self.first.assign(self.pid)     
            time.sleep(0.1)                 
            self.second.assign(self.pid)    
            time.sleep(0.1)                
            self.second.unassign(self.pid)    
            self.first.unassign(self.pid)  
            self.sem.exit(self.pid)       
        if STATUS_MESSAGE:
            sys.stdout.write('\nPROCESS {} HAS RUN ITS COURSE\n\n'.format(self.pid))


# In[ ]:


class Resource(object):
    def __init__(self, rid):
        self.rid = rid           
        self.pid = -1                 
        self.r_lock = threading.Condition(threading.Lock())
        self.allotted = False

    def unassign(self, pid):         
        with self.r_lock:
            while self.allotted == False:
                self.r_lock.wait()
            self.pid = -1
            self.allotted = False
            if RESOURCE_MESSAGE:
                sys.stdout.write('Process {} has returned Resource {}\n'.format(pid, self.rid))
            self.r_lock.notifyAll()
            
    def assign(self, pid):         
        with self.r_lock:
            while self.allotted == True:
                self.r_lock.wait()
                latency[pid] += 2
            self.pid = pid
            self.allotted = True
            if RESOURCE_MESSAGE:
                sys.stdout.write('Process {} has been assigned Resource {}\n'.format(pid, self.rid))
            self.r_lock.notifyAll()
            latency[pid] += 4


# In[ ]:


def main():  
    sem = Counting_semaphore(number_of_process-1)
    
    resource_array = [Resource(rid) for rid in range(number_of_process)]

    process_array = [Process(pid, resource_array[pid], resource_array[(pid+1)%number_of_process], sem) for pid in range(number_of_process)]

    start_time = time.monotonic_ns()
    for pid in range(number_of_process):
        process_array[pid].start()
    for pid in range(number_of_process):
        process_array[pid].join()
    end_time = time.monotonic_ns()

    print('\n\n\n########## TIME ELAPSED : {} s ############\n'.format((end_time-start_time)/(10**9)))
    print('########## AVERAGE LATENCY : {} ############'.format(numpy.mean(latency)))
    
if __name__ == "__main__":
    main()

