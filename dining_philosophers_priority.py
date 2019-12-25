# In[1]:


import threading
import time
import sys
import numpy


# In[2]:


number_of_process = 5
number_of_entries = 5

RESOURCE_MESSAGE = True
STATUS_MESSAGE = True

priority = [i for i in range(number_of_process-1,-1,-1)]
latency = [0 for i in range(number_of_process)]


# In[3]:


class Process(threading.Thread):
    def __init__(self, pid, first, second):
        threading.Thread.__init__(self)
        self.first_neighbor = pid-1 if pid-1 != -1 else number_of_process-1
        self.second_neighbor = (pid+1)%number_of_process
        self.pid = pid           
        self.first = first
        self.second = second
        self.number_of_entries = number_of_entries

    def run(self):
        while self.number_of_entries:
            if self.first.allotted==False and self.second.allotted==False and max(priority[self.first_neighbor],priority[self.second_neighbor]) < priority[self.pid]:        
                latency[self.pid] += 1
                self.first.assign(self.pid)     
                time.sleep(0.1)                 
                self.second.assign(self.pid)    
                time.sleep(0.1)                
                self.second.unassign(self.pid)    
                self.first.unassign(self.pid)     
                self.number_of_entries -= 1
                priority[self.pid] = 0
            else:
                priority[self.pid] = (priority[self.pid]+1)%number_of_process
        if STATUS_MESSAGE:
            sys.stdout.write('\nPROCESS {} HAS RUN ITS COURSE\n\n'.format(self.pid))


# In[4]:


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


# In[5]:


def main():  
    resource_array = [Resource(rid) for rid in range(number_of_process)]

    process_array = [Process(pid, resource_array[pid], resource_array[(pid+1)%number_of_process]) for pid in range(number_of_process)]

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

