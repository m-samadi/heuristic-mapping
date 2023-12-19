 #**************************************************************************
 # lnsnl.py
 #
 # Schedule and execute the task parts of the graph using the LNSNL heuristic
 # presented in the following paper:
 # A static scheduling approach to enable safety-critical OpenMP applications
 #*************************************************************************
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
import func
import threading
import time

# Global variables #
t = 0 # Scheduling time
ready_queue = [] # The ready queue
suspend_list = [] # The list of tasks suspended on the threads
last_idle = [] # Last idle time of the threads (-1 for a busy thread)
thread_queue = [] # The thread queues of the threads
parts_cnt = 0 # The number of all the parts
comp_parts_cnt = 0 # The number of completed parts

# Specify the clock of the system #
def clock(num_threads):
	global t, parts_cnt, comp_parts_cnt

	while comp_parts_cnt < parts_cnt:
		t += 1
		time.sleep(0.001)

# The scheduling process for tied tasks #
def schedule_tied(thr_num, num_tasks, num_threads, part_list, desc_rel):
	global ready_queue, suspend_list, last_idle, thread_queue, t, parts_cnt, comp_parts_cnt

	# Continue the scheduling process while the ready queue and/or the thread queues of the threads are not empty #
	while comp_parts_cnt < parts_cnt:
		# Check the thread queue of each thread separately #
		if bool(thread_queue[thr_num]):
			part = thread_queue[thr_num][len(thread_queue[thr_num]) - 1]
			# The part is in the execution status and its process has been already finished #
			if part.status == 's' and part.f_time <= t:
				part.status = 'f'
				last_idle[thr_num] = t
				comp_parts_cnt += 1

				# If the part has any child parts #
				child_list = func.discover_child(num_tasks, part_list, part)
				for i in range(len(child_list)):
					ready_queue.append(child_list[i])

				# The part has a sibling part #
				if part.sibling != None:
					ready_queue.append(part.sibling)

				# Remove the task from the list of suspended tasks #
				if part.p_id == len(part_list[part.t_id]) - 1:
					suspend_list[thr_num].remove(part.t_id)

		# This process is done just by the master thread #
		if thr_num == 0:
			# Check the ready queue and allocate one of its parts to an idle thread #
			if bool(ready_queue):
				# Select and sort the idle threads #
				temp_idle_list = last_idle.copy()
				sort_idle_list = []
				for i in range(num_threads):
					thread_id = -1
					min_idle_time = -1
					for j in range(num_threads):
						if temp_idle_list[j] != -1:
							thread_id = j
							min_idle_time = temp_idle_list[j]
							break

					for k in range(num_threads)[j+1::]:
						if temp_idle_list[k] != -1:
							if temp_idle_list[k] < min_idle_time:
								thread_id = k
								min_idle_time = temp_idle_list[k]

					if thread_id != -1:
						sort_idle_list.append(thread_id)
						temp_idle_list[thread_id] = -1

				# Allocate and execute ready parts by idle threads #
				for index in range(len(sort_idle_list)):
					thread_id = sort_idle_list[index]
					sel_parts = []
					# Look for any parts in the ready queue and find suitable ones #
					for i in range(len(ready_queue)):
						# Check whether there is a data dependency, so the related part is finished #
						flag_finished = False
						if ready_queue[i].dep != None:
							for j in range(num_threads):
								for k in range(len(thread_queue[j])):
									if ready_queue[i].dep == thread_queue[j][k] and thread_queue[j][k].status == 'f':
										flag_finished = True

						# Put the part in the list if there is not a data dependency, or #
						# there is a data dependency but the related part is finished #
						if ready_queue[i].dep == None or (ready_queue[i].dep != None and flag_finished == True):
							# Check whether the part is the first part of its task #
							# The part is the first part of the task #
							if ready_queue[i].p_id == 0:
								flag = True
								for j in range(len(suspend_list[thread_id])):
									if desc_rel[suspend_list[thread_id][j]][ready_queue[i].t_id] == 0:
										flag = False

								if flag == True:
									sel_parts.append(ready_queue[i])

							# The part is not the first part of the task #
							else:
								# Look for the first part of the task in the thread queue #
								flag = False
								for j in range(len(thread_queue[thread_id])):
									if ready_queue[i].t_id == thread_queue[thread_id][j].t_id:
										flag = True
										break

								if flag == True:
									# Add the part to the selected parts #
									sel_parts.append(ready_queue[i])

					# Choose one of the parts from the selected parts by the LNSNL heuristic #
					# Determine the number of immediate successors #
					num_successors = []
					for i in range(len(sel_parts)):
						count = 0
						if sel_parts[i].sibling != None:
							count += 1
						child_list = func.discover_child(num_tasks, part_list, part)
						count += len(child_list)

						num_successors.append(count)

					# Select the part with the largest number of immediate successors #					
					if bool(num_successors):
						max_index = 0
						max_value = num_successors[0]

						for i in range(len(num_successors))[1::]:
							if num_successors[i] > max_value:
								max_index = i
								max_value = num_successors[i]


						# Assign the part to the thread #
						thread_queue[thread_id].append(sel_parts[max_index])
						part = thread_queue[thread_id][len(thread_queue[thread_id]) - 1]

						part.status = 's'
						part.s_time = t
						part.f_time = t + part.et

						# Append the task to the list of suspended tasks #
						if part.p_id == 0:
							suspend_list[thread_id].append(part.t_id)

						last_idle[thread_id] = -1

						# Remove the part from the ready queue #
						ready_queue.remove(sel_parts[max_index])

# The scheduling process for untied tasks #
def schedule_untied(thr_num, num_tasks, num_threads, part_list):
	global ready_queue, last_idle, thread_queue, t, parts_cnt, comp_parts_cnt

	# Continue the scheduling process while the ready queue and/or the thread queues of the threads are not empty #
	while comp_parts_cnt < parts_cnt:
		# Check the thread queue of each thread separately #
		if bool(thread_queue[thr_num]):
			part = thread_queue[thr_num][len(thread_queue[thr_num]) - 1]
			# The part is in the execution status and its process has been already finished #
			if part.status == 's' and part.f_time <= t:
				part.status = 'f'
				last_idle[thr_num] = t
				comp_parts_cnt += 1

				# If the part has any child parts #
				child_list = func.discover_child(num_tasks, part_list, part)
				for i in range(len(child_list)):
					ready_queue.append(child_list[i])

				# The part has a sibling part #
				if part.sibling != None:
					ready_queue.append(part.sibling)

		# This process is done just by the master thread #
		if thr_num == 0:
			# Check the ready queue and allocate one of its parts to an idle thread #
			if bool(ready_queue):
				# Select and sort the idle threads #
				temp_idle_list = last_idle.copy()
				sort_idle_list = []
				for i in range(num_threads):
					thread_id = -1
					min_idle_time = -1
					for j in range(num_threads):
						if temp_idle_list[j] != -1:
							thread_id = j
							min_idle_time = temp_idle_list[j]
							break

					for k in range(num_threads)[j+1::]:
						if temp_idle_list[k] != -1:
							if temp_idle_list[k] < min_idle_time:
								thread_id = k
								min_idle_time = temp_idle_list[k]

					if thread_id != -1:
						sort_idle_list.append(thread_id)
						temp_idle_list[thread_id] = -1

				# Allocate and execute ready parts by idle threads #
				for index in range(len(sort_idle_list)):
					thread_id = sort_idle_list[index]
					sel_parts = []
					# Look for any parts in the ready queue and find suitable ones #
					for i in range(len(ready_queue)):
						# Check whether there is a data dependency, so the related part is finished #
						flag_finished = False
						if ready_queue[i].dep != None:
							for j in range(num_threads):
								for k in range(len(thread_queue[j])):
									if ready_queue[i].dep == thread_queue[j][k] and thread_queue[j][k].status == 'f':
										flag_finished = True

						# Put the part in the list if there is not a data dependency, or #
						# there is a data dependency but the related part is finished #
						if ready_queue[i].dep == None or (ready_queue[i].dep != None and flag_finished == True):
							# Add the part to the selected parts #
							sel_parts.append(ready_queue[i])

					# Choose one of the parts from the selected parts by the LNSNL heuristic #
					# Determine the number of immediate successors #
					num_successors = []
					for i in range(len(sel_parts)):
						count = 0
						if sel_parts[i].sibling != None:
							count += 1
						child_list = func.discover_child(num_tasks, part_list, part)
						count += len(child_list)

						num_successors.append(count)

					# Select the part with the largest number of immediate successors #					
					if bool(num_successors):
						max_index = 0
						max_value = num_successors[0]

						for i in range(len(num_successors))[1::]:
							if num_successors[i] > max_value:
								max_index = i
								max_value = num_successors[i]


						# Assign the part to the thread #
						thread_queue[thread_id].append(sel_parts[max_index])
						part = thread_queue[thread_id][len(thread_queue[thread_id]) - 1]

						part.status = 's'
						part.s_time = t
						part.f_time = t + part.et

						last_idle[thread_id] = -1

						# Remove the part from the ready queue #
						ready_queue.remove(sel_parts[max_index])

# The main scheduling process #
def execute(task_type, num_tasks, num_threads, part_list, deadline, desc_rel, first_task_part, graphic_result):
	global ready_queue, suspend_list, last_idle, thread_queue, t, parts_cnt

	# Determine the number of all the parts
	for i in range(num_tasks):
		parts_cnt += len(part_list[i])

	# Initialize the scheduling time and the ready queue #
	t = 0
	ready_queue = []

	# Create the initial list of suspended tasks #
	suspend_list = []
	for i in range(num_threads):
		suspend_list.append([])

	# Create a list for the last idle time of the threads #
	last_idle = []
	for i in range(num_threads):
		last_idle.append(0)

	# Create an thread queue for each thread #
	thread_queue = []
	for i in range(num_threads):
		thread_queue.append([])

	# Put the first part of the system in the thread queue of the first thread #
	thread_queue[0].append(first_task_part)
	thread_queue[0][0].status = 's'
	thread_queue[0][0].s_time = 1
	thread_queue[0][0].f_time = 1 + thread_queue[0][0].et

	suspend_list[0].append(0) # Append Task 0 to the list of suspended tasks of Thread 0

	# Show the scheduling name and the task type #
	if task_type == 'tied':
		print('\nLNSNL for tied tasks\n***********************************')
	else:
		print('\nLNSNL for untied tasks\n***********************************')

	# Create and start the threads #
	thr_clock = threading.Thread(target = clock, args = (num_threads, ))
	thr_clock.start()

	threads = []
	for i in range(num_threads):
		if task_type == 'tied':
			thr = threading.Thread(target = schedule_tied, args = (i, num_tasks, num_threads, part_list, desc_rel, ))
		else:
			thr = threading.Thread(target = schedule_untied, args = (i, num_tasks, num_threads, part_list, ))
		threads.append(thr)
		thr.start()

	# Wait until the threads are executed completely #
	thr_clock.join()
	for thr in threads:
		thr.join()
	threads = []

	# Calculate the results #
	scheduling_time = t # The scheduling time
	idle_time = sum(func.idle_time(num_threads, thread_queue, t)) # The idle time of the system
	waiting_time = func.wait_time(num_threads, thread_queue) # The waiting time of the threads
	miss_deadline = func.miss_deadline(num_tasks, num_threads, part_list, thread_queue, deadline, t) # The missed deadline status of the system

	# Show the results #
	print('Scheduling time: ' + str(scheduling_time))
	print('Idle time: ' + str(idle_time))
	print('Waiting time: ' + str(waiting_time))
	print('Missed deadline: ' + str(miss_deadline))
	'''
	print("\nThe thread queues of the threads:") # The contents of the thread queues of the threads
	for i in range(num_threads):
		print('Thr ' + str(i) + ':')
		for j in range(len(thread_queue[i])):
			print('p' + str(thread_queue[i][j].t_id) + str(thread_queue[i][j].p_id) + ' --> status = ' + thread_queue[i][j].status + ', start waiting time = ' + str(thread_queue[i][j].s_w_time) +\
			 ', finish waiting time = ' + str(thread_queue[i][j].f_w_time) + ', start time = ' + str(thread_queue[i][j].s_time) + ', finish time = ' + str(thread_queue[i][j].f_time))
	'''
	if graphic_result == 1:
		func.graphic_result(num_threads, thread_queue, 'lnsnl', task_type, '', '') # The graphical output

	# Return the results to the main program #
	return scheduling_time, idle_time, waiting_time, miss_deadline
