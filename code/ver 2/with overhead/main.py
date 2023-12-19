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
				 # 3: Each task (only the first part) can have m:n child tasks
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
		self.rt = rt # Response time of the part (only used in the new mapping algorithm)
		self.status = status # s: started; w : waiting for a data dependency; f : finished
		self.s_w_time = s_w_time # Start time of the waiting process (data dependency)
		self.f_w_time = f_w_time # Finish time of the waiting process (data dependency)
		self.s_time = s_time # Start time of the execution process
		self.f_time = f_time # Finish time of the execution process

# Generate the graph #
print("Perform the mapping process based on the predefined graph? (y/n)")
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

# Show the status of the mapping process #
print('The mapping process is in progress. Please wait ...')

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

	results = []

	# +++++++++++++++++++Tied+++++++++++++++++++++ #

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# BFS mapping algorithm for tied tasks #
	results.append(bfs.execute('tied', num_tasks, num_threads, part_list, deadline, part_list[0][0], graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# WFS mapping algorithm for tied tasks #
	results.append(wfs.execute('tied', num_tasks, num_threads, part_list, deadline, part_list[0][0], graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# LNSNL mapping algorithm for tied tasks #
	results.append(lnsnl.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MCD', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MCD', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MCD', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MCD', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MCD', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for tied tasks #
	results.append(new.execute('tied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MCD', graphic_result))

	# +++++++++++++++++++Untied+++++++++++++++++++++ #

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# BFS mapping algorithm for untied tasks #
	results.append(bfs.execute('untied', num_tasks, num_threads, part_list, deadline, part_list[0][0], graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# WFS mapping algorithm for untied tasks #
	results.append(wfs.execute('untied', num_tasks, num_threads, part_list, deadline, part_list[0][0], graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# LNSNL mapping algorithm for untied tasks #
	results.append(lnsnl.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MNTP', 'MCD', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'NT', 'MCD', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MRIT', 'MCD', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTET', 'MCD', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'MTRT', 'MCD', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MET', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MRT', graphic_result))

	# Clear the detailed contents of the list #
	part_list = func.clear(num_tasks, part_list)

	# NEW mapping algorithm for untied tasks #
	results.append(new.execute('untied', num_tasks, num_threads, part_list, deadline, desc_rel, part_list[0][0], 'TMCD', 'MCD', graphic_result))

	# Open the file, write the results, and close ir #
	file = open("results.dat", "a")

	for i in range(0, 42):
		file.write(str(results[i][0]) + "\t")
		file.write(str(results[i][1]) + "\t")
		file.write(str(results[i][2]) + "\t")
		file.write(str(results[i][3]))
		if i != 41:
			file.write("\t")

	file.close()
