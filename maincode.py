import threading
import time
import tkinter as tk
from tkinter import ttk

import psutil

HIGH_PRIORITY = 1
MEDIUM_PRIORITY = 2
LOW_PRIORITY = 3

tasks = []
interrupt_queue = []
task_execution_details = []
lock = threading.Lock()

def handle_interrupt(priority):
    global interrupt_queue
    with lock:
        interrupt_queue.append(priority)

def update_gui():
    display_task_execution_details()
    root.after(1000, update_gui)
    
def update_task_status(pid, priority, status):
    global task_execution_details
    for i, (task_pid, task_priority, exec_time, _) in enumerate(task_execution_details):
        if task_pid == pid and task_priority == priority:
            task_execution_details[i] = (pid, priority, exec_time, status)
            break

def execute_tasks():
    global tasks
    global interrupt_queue
    global task_execution_details
    sorted_tasks = sorted(tasks, key=lambda x: x[0])
    for priority, exec_time in sorted_tasks:
        pid = threading.get_ident()
        start_time = time.time()
        execution_status = "Running"
        task_execution_details.append((pid, priority, exec_time, execution_status))
        print(f"Task with priority {priority} started execution.")
        elapsed_time = 0
        while elapsed_time < exec_time:
            time.sleep(1)
            elapsed_time += 1
            execution_status = f"Running ({elapsed_time}/{exec_time} seconds)"
            update_task_status(pid, priority, execution_status)

            if interrupt_queue:
                with lock:
                    interrupt_priority = interrupt_queue.pop(0)
                execution_status = f"Interrupted by Priority {interrupt_priority}"
                update_task_status(pid, priority, execution_status)
                # Update the execution time after the interrupt
                exec_time += interrupt_priority
                execution_status = f"Running ({elapsed_time}/{exec_time} seconds)"
                update_task_status(pid, priority, execution_status)
                
        execution_status = "Completed"
        update_task_status(pid, priority, execution_status)

        # Additional step: Update task status to "Completed"
        update_task_status(pid, priority, "Completed")

def handle_interrupt_choice(priority):
    handle_interrupt(priority)
    update_gui()

def update_task_status(pid, priority, status):
    global task_execution_details
    for i, (task_pid, task_priority, exec_time, _) in enumerate(task_execution_details):
        if task_pid == pid and task_priority == priority:
            task_execution_details[i] = (pid, priority, exec_time, status)
            
            break

def handle_interrupts():
    global interrupt_queue
    while True:
        if interrupt_queue:
            with lock:
                priority = interrupt_queue.pop(0)
                update_task_status(threading.get_ident(), priority, f"Interrupted by Priority {priority}")
            print(f"Interrupt with priority {priority} occurred.")
        time.sleep(1)
def get_memory_usage():
    mem_usage = psutil.virtual_memory().used
    return mem_usage

def add_tasks(num_tasks):
    global tasks
    tasks.clear()
    for _ in range(num_tasks):
        priority = int(input("Enter priority for the task: "))
        exec_time = int(input("Enter execution time for the task (seconds): "))
        tasks.append((priority, exec_time))

def execute_with_interrupts():
    task_thread = threading.Thread(target=execute_tasks)
    interrupt_thread = threading.Thread(target=handle_interrupts)

    task_thread.start()
    interrupt_thread.start()
    update_gui()

def display_task_execution_details():
    global task_execution_details
    if not hasattr(display_task_execution_details, 'root'):
        display_task_execution_details.root = tk.Tk()
        display_task_execution_details.root.title("Task Execution Details")
        
        tree = ttk.Treeview(display_task_execution_details.root)
        tree["columns"] = ("pid", "priority", "exec_time", "status")
        tree.heading("#0", text="Task ID")
        tree.heading("pid", text="PID")
        tree.heading("priority", text="Priority")
        tree.heading("exec_time", text="Execution Time (s)")
        tree.heading("status", text="Status")
        
        tree.pack(expand=True, fill="both")
        
        display_task_execution_details.tree = tree
    
    tree = display_task_execution_details.tree
    tree.delete(*tree.get_children())
    
    cumulative_interrupt_time = 0
    for i, (pid, priority, exec_time, status) in enumerate(task_execution_details):
        if status.startswith("Interrupted by Priority"):
            cumulative_interrupt_time += priority
            total_exec_time = exec_time + cumulative_interrupt_time
            original_priority = next((item[1] for item in reversed(task_execution_details[:i]) if not item[3].startswith("Interrupted")), None)
            if original_priority is not None:
                priority = original_priority
        else:
            total_exec_time = exec_time
        tree.insert("", "end", text=str(i+1), values=(pid, priority,exec_time, status))
        0
    tree.insert("", "end", text=str(len(task_execution_details)+1), values=("", "", ""))
    display_task_execution_details.root.mainloop()

root = tk.Tk()
root.title("Priority Based Interrupt Handler")

task_frame = ttk.Frame(root)
task_frame.pack()

num_tasks_label = ttk.Label(task_frame, text="Enter number of tasks:")
num_tasks_label.grid(row=0, column=0, padx=5, pady=5)

num_tasks_entry = ttk.Entry(task_frame)
num_tasks_entry.grid(row=0, column=1, padx=5, pady=5)

submit_tasks_button = ttk.Button(task_frame, text="Submit", command=lambda: add_tasks(int(num_tasks_entry.get())))
submit_tasks_button.grid(row=0, column=2, padx=5, pady=5)

start_button = ttk.Button(task_frame, text="Start Execution", command=execute_with_interrupts)
start_button.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

high_priority_button = ttk.Button(task_frame, text="High Priority Interrupt", command=lambda: handle_interrupt_choice(HIGH_PRIORITY))
high_priority_button.grid(row=2, column=0, padx=5, pady=5)

medium_priority_button = ttk.Button(task_frame, text="Medium Priority Interrupt", command=lambda: handle_interrupt_choice(MEDIUM_PRIORITY))
medium_priority_button.grid(row=2, column=1, padx=5, pady=5)

low_priority_button = ttk.Button(task_frame, text="Low Priority Interrupt", command=lambda: handle_interrupt_choice(LOW_PRIORITY))
low_priority_button.grid(row=2, column=2, padx=5, pady=5)

display_button = ttk.Button(task_frame, text="Display Task Execution Details", command=display_task_execution_details)
display_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()

print(f"Memory usage: {get_memory_usage()} bytes")
