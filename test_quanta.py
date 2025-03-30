# test_quanta.py
from scheduler import RoundRobinScheduler

def test_multiple_quanta(filename, quanta):
    for q in quanta:
        scheduler = RoundRobinScheduler(q)
        scheduler.load_processes(filename)
        scheduler.run()
        scheduler.print_results()

test_multiple_quanta('processes.csv', [1, 2, 3, 4, 5])