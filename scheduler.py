import csv
from collections import deque
from dataclasses import dataclass
from typing import List, Optional


CONTEXT_SWITCH_TIME = 0.1  

@dataclass
class Process:
    pid: int
    arrival_time: int
    burst_time: int
    remaining_time: int
    completion_time: Optional[int] = None
    waiting_time: int = 0
    turnaround_time: int = 0

class RoundRobinScheduler:
    def __init__(self, time_quantum: int):
        self.time_quantum = time_quantum
        self.clock = 0
        self.ready_queue = deque()
        self.processes: List[Process] = []
        self.completed_processes: List[Process] = []
        self.context_switches = 0
        self.total_execution_time = 0
        
    def load_processes(self, filename: str):
        with open(filename, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                process = Process(
                    pid=int(row['pid']),
                    arrival_time=int(row['arrive']),
                    burst_time=int(row['burst']),
                    remaining_time=int(row['burst'])
                )
                self.processes.append(process)
        self.processes.sort(key=lambda x: (x.arrival_time, x.pid))
        
    def run(self):
        remaining_processes = self.processes.copy()
        current_process = None
        
        while remaining_processes or self.ready_queue or current_process:
            while remaining_processes and remaining_processes[0].arrival_time <= self.clock:
                self.ready_queue.append(remaining_processes.pop(0))
            
            if not current_process and self.ready_queue:
                current_process = self.ready_queue.popleft()
                self.context_switches += 1
            
            if current_process:
                execution_time = min(self.time_quantum, current_process.remaining_time)
                self.clock += execution_time
                current_process.remaining_time -= execution_time
                
                for process in self.ready_queue:
                    process.waiting_time += execution_time
                
                if current_process.remaining_time == 0:
                    current_process.completion_time = self.clock
                    current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                    self.completed_processes.append(current_process)
                    current_process = None
                elif execution_time == self.time_quantum:
                    self.ready_queue.append(current_process)
                    current_process = None
            else:
                self.clock += 1
        
        self.total_execution_time = self.clock
    
    def calculate_metrics(self):
        if not self.completed_processes:
            return {
                'cpu_utilization': 0,
                'throughput': 0,
                'avg_waiting_time': 0,
                'avg_turnaround_time': 0,
                'total_context_switches': 0
            }
        
        total_waiting_time = sum(p.waiting_time for p in self.completed_processes)
        total_turnaround_time = sum(p.turnaround_time for p in self.completed_processes)
        num_processes = len(self.completed_processes)
        
        idle_time = CONTEXT_SWITCH_TIME * self.context_switches
        cpu_utilization = 1 - (idle_time / self.total_execution_time)
        
        return {
            'cpu_utilization': cpu_utilization,
            'throughput': num_processes / self.total_execution_time,
            'avg_waiting_time': total_waiting_time / num_processes,
            'avg_turnaround_time': total_turnaround_time / num_processes,
            'total_context_switches': self.context_switches
        }
    
    def print_results(self):
        metrics = self.calculate_metrics()
        print(f"\nResults for Time Quantum: {self.time_quantum}")
        print("-" * 50)
        print(f"CPU Utilization: {metrics['cpu_utilization']:.2%}")
        print(f"Throughput: {metrics['throughput']:.2f} processes/unit time")
        print(f"Average Waiting Time: {metrics['avg_waiting_time']:.2f} units")
        print(f"Average Turnaround Time: {metrics['avg_turnaround_time']:.2f} units")
        print(f"Total Context Switches: {metrics['total_context_switches']}")
        
        print("\nProcess Completion Details:")
        print("PID  Arrival  Burst  Completion  Turnaround  Waiting")
        print("-" * 55)
        for p in self.completed_processes:
            print(f"{p.pid:3d}  {p.arrival_time:7d}  {p.burst_time:5d}  "
                  f"{p.completion_time:10d}  {p.turnaround_time:10d}  {p.waiting_time:7d}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py <process_file> <time_quantum>")
        sys.exit(1)
    
    process_file = sys.argv[1]
    time_quantum = int(sys.argv[2])
    main = RoundRobinScheduler(time_quantum)
    main.load_processes(process_file)
    main.run()
    main.print_results()