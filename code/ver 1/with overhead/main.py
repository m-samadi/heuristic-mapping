 #**************************************************************************
 # main.py
 #
 # This tool conducts the mapping process of task parts on threads in
 # OpenMP-based programs using several heuristics.
 #**************************************************************************
 # Copyright 2023 Instituto Superior de Engenharia do Porto
 #
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 #              http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
 #**************************************************************************
import gen
import func
import bfs
import wfs
import lnsnl
import new

# Global variables #
num_tasks = 7 # The number of tasks
num_parts = 5 # The maximum number of parts for each task
et_min = 3 # Minimum execution time for each task part
et_max = 10 # Maximum execution time for each task part
deadline = 0 # Deadline of the whole system
deadline_min = 0.5 # The minimum probability for determining the deadline of the whole system
deadline_max = 1 # The maximum probability for determining the deadline of the whole system
graph_gen_type = 1 # 1: Generate the graph one time, 2: Generate the graph in each iteration
system_model = 1 # 1: The first task is the parent of the other tasks,
				 # 2: Each task (all parts) can have a random number of child tasks,
				 # 3: Each task (only the first part) can have [m, n] child tasks
min_num_child = 2 # The minimum number of child tasks (in the system model 3)
max_num_child = 3 # The maximum number of child tasks (in the system model 3)
dep_pro = 0.6 # The probability of selecting the sibling tasks in the dependency graph
num_dep_level = 2 # The maximum number of dependencies (at each level) in the dependency graph between sibling tasks
num_threads = 4 # The number of threads
graphic_result = 0 # 0: Not show, 1: Show
itr = 1 # The number of iterations

# Define the class of the task part #
class part:
	def __init__(self, t_id, p_id, et, dep, parent, sibling, rt, status, s_w_time, f_w_time, s_time, f_time):
		self.t_id = t_id # Task ID
		self.p_id = p_id # Part ID
		self.et = et # Execution time of the part
		self.dep = dep # The task related to input data dependency
		self.parent = parent # The child task
		self.sibling = sibling # The next part in the same task
		self.rt = rt # Response time of the part (only used in the new method)
		self.status = status # s: started; w : waiting for a data dependency; f : finished
		self.s_w_time = s_w_time # Start time of the waiting process (data dependency)
		self.f_w_time = f_w_time # Finish time of the waiting process (data dependency)
		self.s_time = s_time # Start time of the execution process
		self.f_time = f_time # Finish time of the execution process

# Generate the graph #
print("Perform the scheduling process based on the predefined graph? (y/n)")
graph_type = input()

if graph_gen_type == 1:
	if graph_type == 'y':
		# Generate it according to a predefined structure #
		part_list = gen.graph_predef(num_tasks, part)
	else:
		# Generate it randomly #
		part_list = gen.graph_rand(num_tasks, num_parts, system_model, part, dep_pro, num_dep_level, min_num_child, max_num_child)

	# Show the details of the graph #
	#print('\nThe traverse of the graph:')
	#func.traverse(num_tasks, part_list, part_list[0][0])

	print('\nThe task parts:')
	for i in range(num_tasks):
		for j in range(len(part_list[i])):
			print('p' + str(part_list[i][j].t_id) + str(part_list[i][j].p_id))

	print('\nThe parent of the child tasks:')
	for i in range(num_tasks):
		for j in range(len(part_list[i])):
			if part_list[i][j].parent != None:
				print('p' + str(part_list[i][j].t_id) + str(part_list[i][j].p_id) + ' --> ' + 'p' + str(part_list[i][j].parent.t_id) + str(part_list[i][j].parent.p_id))

	print('\nThe data dependencies:')
	for i in range(num_tasks):
		for j in range(len(part_list[i])):
			if part_list[i][j].dep != None:
				print('p' + str(part_list[i][j].t_id) + str(part_list[i][j].p_id) + ' --> ' + 'p' + str(part_list[i][j].dep.t_id) + str(part_list[i][j].dep.p_id))

	# Wait for pressing a key to continue #
	print('\nPress key to continue ...')
	input()

# Show the status of the scheduling process #
print('The scheduling process is in progress. Please wait ...')

# Reset the file to write the results #
file = open("results.dat", "w")
file.close()

for i in range(itr):
	print('\n++++++++++++++++++++\nIteration = ' + str(i + 1) + '\n++++++++++++++++++++')

	# Generate the random graph randomly #
	if graph_gen_type == 2:
		part_list = gen.graph_rand(num_tasks, num_parts, system_model, part, dep_pro, num_dep_level, min_num_child, max_num_child)

	# Determine the execution time and generate the list of tasks #
	part_list, deadline, desc_rel = gen.specify_et(num_tasks, part_list, et_min, et_max, deadline_min, deadline_max)

	# +++++++++++++++++++Tied+++++++++++++++++++++ #

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# BFS scheduling algorithm for tied tasks #
	scheduling_time_1, idle_time_1, waiting_time_1, num_miss_deadline_1 = bfs.execute('tied', num_tasks, num_threads, part_list, deadline, part_list[0][0], graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# WFS scheduling algorithm for tied tasks #
	scheduling_time_2, idle_time_2, waiting_time_2, num_miss_deadline_2 = wfs.execute('tied', num_tasks, num_threads, part_list, deadline, part_list[0][0], graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# LNSNL scheduling algorithm for tied tasks #
	scheduling_time_3, idle_time_3, waiting_time_3, num_miss_deadline_3 = lnsnl.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_4, idle_time_4, waiting_time_4, num_miss_deadline_4 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_5, idle_time_5, waiting_time_5, num_miss_deadline_5 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_6, idle_time_6, waiting_time_6, num_miss_deadline_6 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MCD', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_7, idle_time_7, waiting_time_7, num_miss_deadline_7 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_8, idle_time_8, waiting_time_8, num_miss_deadline_8 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_9, idle_time_9, waiting_time_9, num_miss_deadline_9 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MCD', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_10, idle_time_10, waiting_time_10, num_miss_deadline_10 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_11, idle_time_11, waiting_time_11, num_miss_deadline_11 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_12, idle_time_12, waiting_time_12, num_miss_deadline_12 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MCD', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_13, idle_time_13, waiting_time_13, num_miss_deadline_13 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_14, idle_time_14, waiting_time_14, num_miss_deadline_14 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_15, idle_time_15, waiting_time_15, num_miss_deadline_15 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MCD', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_16, idle_time_16, waiting_time_16, num_miss_deadline_16 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_17, idle_time_17, waiting_time_17, num_miss_deadline_17 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_18, idle_time_18, waiting_time_18, num_miss_deadline_18 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MCD', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_19, idle_time_19, waiting_time_19, num_miss_deadline_19 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_20, idle_time_20, waiting_time_20, num_miss_deadline_20 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for tied tasks #
	scheduling_time_21, idle_time_21, waiting_time_21, num_miss_deadline_21 = new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MCD', graphic_result)

	# +++++++++++++++++++Untied+++++++++++++++++++++ #

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# BFS scheduling algorithm for untied tasks #
	scheduling_time_22, idle_time_22, waiting_time_22, num_miss_deadline_22 = bfs.execute('untied', num_tasks, num_threads, part_list, deadline, part_list[0][0], graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# WFS scheduling algorithm for untied tasks #
	scheduling_time_23, idle_time_23, waiting_time_23, num_miss_deadline_23 = wfs.execute('untied', num_tasks, num_threads, part_list, deadline, part_list[0][0], graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# LNSNL scheduling algorithm for untied tasks #
	scheduling_time_24, idle_time_24, waiting_time_24, num_miss_deadline_24 = lnsnl.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_25, idle_time_25, waiting_time_25, num_miss_deadline_25 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_26, idle_time_26, waiting_time_26, num_miss_deadline_26 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_27, idle_time_27, waiting_time_27, num_miss_deadline_27 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MCD', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_28, idle_time_28, waiting_time_28, num_miss_deadline_28 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_29, idle_time_29, waiting_time_29, num_miss_deadline_29 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_30, idle_time_30, waiting_time_30, num_miss_deadline_30 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MCD', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_31, idle_time_31, waiting_time_31, num_miss_deadline_31 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_32, idle_time_32, waiting_time_32, num_miss_deadline_32 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_33, idle_time_33, waiting_time_33, num_miss_deadline_33 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MCD', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_34, idle_time_34, waiting_time_34, num_miss_deadline_34 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_35, idle_time_35, waiting_time_35, num_miss_deadline_35 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_36, idle_time_36, waiting_time_36, num_miss_deadline_36 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MCD', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_37, idle_time_37, waiting_time_37, num_miss_deadline_37 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_38, idle_time_38, waiting_time_38, num_miss_deadline_38 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_39, idle_time_39, waiting_time_39, num_miss_deadline_39 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MCD', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_40, idle_time_40, waiting_time_40, num_miss_deadline_40 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MET', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_41, idle_time_41, waiting_time_41, num_miss_deadline_41 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MRT', graphic_result)

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW scheduling algorithm for untied tasks #
	scheduling_time_42, idle_time_42, waiting_time_42, num_miss_deadline_42 = new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MCD', graphic_result)

	# Open the file, write the results, and close ir #
	file = open("results.dat", "a")

	file.write(str(scheduling_time_1) + "\t")
	file.write(str(idle_time_1) + "\t")
	file.write(str(waiting_time_1) + "\t")
	file.write(str(num_miss_deadline_1) + "\t")

	file.write(str(scheduling_time_2) + "\t")
	file.write(str(idle_time_2) + "\t")
	file.write(str(waiting_time_2) + "\t")
	file.write(str(num_miss_deadline_2) + "\t")

	file.write(str(scheduling_time_3) + "\t")
	file.write(str(idle_time_3) + "\t")
	file.write(str(waiting_time_3) + "\t")
	file.write(str(num_miss_deadline_3) + "\t")

	file.write(str(scheduling_time_4) + "\t")
	file.write(str(idle_time_4) + "\t")
	file.write(str(waiting_time_4) + "\t")
	file.write(str(num_miss_deadline_4) + "\t")

	file.write(str(scheduling_time_5) + "\t")
	file.write(str(idle_time_5) + "\t")
	file.write(str(waiting_time_5) + "\t")
	file.write(str(num_miss_deadline_5) + "\t")

	file.write(str(scheduling_time_6) + "\t")
	file.write(str(idle_time_6) + "\t")
	file.write(str(waiting_time_6) + "\t")
	file.write(str(num_miss_deadline_6) + "\t")

	file.write(str(scheduling_time_7) + "\t")
	file.write(str(idle_time_7) + "\t")
	file.write(str(waiting_time_7) + "\t")
	file.write(str(num_miss_deadline_7) + "\t")

	file.write(str(scheduling_time_8) + "\t")
	file.write(str(idle_time_8) + "\t")
	file.write(str(waiting_time_8) + "\t")
	file.write(str(num_miss_deadline_8) + "\t")

	file.write(str(scheduling_time_9) + "\t")
	file.write(str(idle_time_9) + "\t")
	file.write(str(waiting_time_9) + "\t")
	file.write(str(num_miss_deadline_9) + "\t")

	file.write(str(scheduling_time_10) + "\t")
	file.write(str(idle_time_10) + "\t")
	file.write(str(waiting_time_10) + "\t")
	file.write(str(num_miss_deadline_10) + "\t")

	file.write(str(scheduling_time_11) + "\t")
	file.write(str(idle_time_11) + "\t")
	file.write(str(waiting_time_11) + "\t")
	file.write(str(num_miss_deadline_11) + "\t")

	file.write(str(scheduling_time_12) + "\t")
	file.write(str(idle_time_12) + "\t")
	file.write(str(waiting_time_12) + "\t")
	file.write(str(num_miss_deadline_12) + "\t")

	file.write(str(scheduling_time_13) + "\t")
	file.write(str(idle_time_13) + "\t")
	file.write(str(waiting_time_13) + "\t")
	file.write(str(num_miss_deadline_13) + "\t")

	file.write(str(scheduling_time_14) + "\t")
	file.write(str(idle_time_14) + "\t")
	file.write(str(waiting_time_14) + "\t")
	file.write(str(num_miss_deadline_14) + "\t")

	file.write(str(scheduling_time_15) + "\t")
	file.write(str(idle_time_15) + "\t")
	file.write(str(waiting_time_15) + "\t")
	file.write(str(num_miss_deadline_15) + "\t")

	file.write(str(scheduling_time_16) + "\t")
	file.write(str(idle_time_16) + "\t")
	file.write(str(waiting_time_16) + "\t")
	file.write(str(num_miss_deadline_16) + "\t")

	file.write(str(scheduling_time_17) + "\t")
	file.write(str(idle_time_17) + "\t")
	file.write(str(waiting_time_17) + "\t")
	file.write(str(num_miss_deadline_17) + "\t")

	file.write(str(scheduling_time_18) + "\t")
	file.write(str(idle_time_18) + "\t")
	file.write(str(waiting_time_18) + "\t")
	file.write(str(num_miss_deadline_18) + "\t")

	file.write(str(scheduling_time_19) + "\t")
	file.write(str(idle_time_19) + "\t")
	file.write(str(waiting_time_19) + "\t")
	file.write(str(num_miss_deadline_19) + "\t")

	file.write(str(scheduling_time_20) + "\t")
	file.write(str(idle_time_20) + "\t")
	file.write(str(waiting_time_20) + "\t")
	file.write(str(num_miss_deadline_20) + "\t")

	file.write(str(scheduling_time_21) + "\t")
	file.write(str(idle_time_21) + "\t")
	file.write(str(waiting_time_21) + "\t")
	file.write(str(num_miss_deadline_21) + "\t")

	file.write(str(scheduling_time_22) + "\t")
	file.write(str(idle_time_22) + "\t")
	file.write(str(waiting_time_22) + "\t")
	file.write(str(num_miss_deadline_22) + "\t")

	file.write(str(scheduling_time_23) + "\t")
	file.write(str(idle_time_23) + "\t")
	file.write(str(waiting_time_23) + "\t")
	file.write(str(num_miss_deadline_23) + "\t")

	file.write(str(scheduling_time_24) + "\t")
	file.write(str(idle_time_24) + "\t")
	file.write(str(waiting_time_24) + "\t")
	file.write(str(num_miss_deadline_24) + "\t")

	file.write(str(scheduling_time_25) + "\t")
	file.write(str(idle_time_25) + "\t")
	file.write(str(waiting_time_25) + "\t")
	file.write(str(num_miss_deadline_25) + "\t")

	file.write(str(scheduling_time_26) + "\t")
	file.write(str(idle_time_26) + "\t")
	file.write(str(waiting_time_26) + "\t")
	file.write(str(num_miss_deadline_26) + "\t")

	file.write(str(scheduling_time_27) + "\t")
	file.write(str(idle_time_27) + "\t")
	file.write(str(waiting_time_27) + "\t")
	file.write(str(num_miss_deadline_27) + "\t")

	file.write(str(scheduling_time_28) + "\t")
	file.write(str(idle_time_28) + "\t")
	file.write(str(waiting_time_28) + "\t")
	file.write(str(num_miss_deadline_28) + "\t")

	file.write(str(scheduling_time_29) + "\t")
	file.write(str(idle_time_29) + "\t")
	file.write(str(waiting_time_29) + "\t")
	file.write(str(num_miss_deadline_29) + "\t")

	file.write(str(scheduling_time_30) + "\t")
	file.write(str(idle_time_30) + "\t")
	file.write(str(waiting_time_30) + "\t")
	file.write(str(num_miss_deadline_30) + "\t")

	file.write(str(scheduling_time_31) + "\t")
	file.write(str(idle_time_31) + "\t")
	file.write(str(waiting_time_31) + "\t")
	file.write(str(num_miss_deadline_31) + "\t")

	file.write(str(scheduling_time_32) + "\t")
	file.write(str(idle_time_32) + "\t")
	file.write(str(waiting_time_32) + "\t")
	file.write(str(num_miss_deadline_32) + "\t")

	file.write(str(scheduling_time_33) + "\t")
	file.write(str(idle_time_33) + "\t")
	file.write(str(waiting_time_33) + "\t")
	file.write(str(num_miss_deadline_33) + "\t")

	file.write(str(scheduling_time_34) + "\t")
	file.write(str(idle_time_34) + "\t")
	file.write(str(waiting_time_34) + "\t")
	file.write(str(num_miss_deadline_34) + "\t")

	file.write(str(scheduling_time_35) + "\t")
	file.write(str(idle_time_35) + "\t")
	file.write(str(waiting_time_35) + "\t")
	file.write(str(num_miss_deadline_35) + "\t")

	file.write(str(scheduling_time_36) + "\t")
	file.write(str(idle_time_36) + "\t")
	file.write(str(waiting_time_36) + "\t")
	file.write(str(num_miss_deadline_36) + "\t")

	file.write(str(scheduling_time_37) + "\t")
	file.write(str(idle_time_37) + "\t")
	file.write(str(waiting_time_37) + "\t")
	file.write(str(num_miss_deadline_37) + "\t")

	file.write(str(scheduling_time_38) + "\t")
	file.write(str(idle_time_38) + "\t")
	file.write(str(waiting_time_38) + "\t")
	file.write(str(num_miss_deadline_38) + "\t")

	file.write(str(scheduling_time_39) + "\t")
	file.write(str(idle_time_39) + "\t")
	file.write(str(waiting_time_39) + "\t")
	file.write(str(num_miss_deadline_39) + "\t")

	file.write(str(scheduling_time_40) + "\t")
	file.write(str(idle_time_40) + "\t")
	file.write(str(waiting_time_40) + "\t")
	file.write(str(num_miss_deadline_40) + "\t")

	file.write(str(scheduling_time_41) + "\t")
	file.write(str(idle_time_41) + "\t")
	file.write(str(waiting_time_41) + "\t")
	file.write(str(num_miss_deadline_41) + "\t")

	file.write(str(scheduling_time_42) + "\t")
	file.write(str(idle_time_42) + "\t")
	file.write(str(waiting_time_42) + "\t")
	file.write(str(num_miss_deadline_42))

	file.write("\n")

	file.close()
