 #**************************************************************************
 # new.py
 #
 # Map the task parts of the graph using the new mapping algorithm.
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
from operator import itemgetter
import func

# Global variables #
alloc_queue = [] # The allocation queues of the threads
suspend_list = [] # The list of tasks suspended on the threads
last_idle = [] # Last idle time of the threads (-1 for a busy thread)
execution_queue = [] # The execution queues of the threads
curr_thr = 0 # The current thread
parts_cnt = 0 # The number of all the parts
comp_parts_cnt = 0 # The number of completed parts

alpha = 0.2
beta = 0.5
gamma = 0.3

theta = 0.4
psi = 0.6

# Select an allocation queue using one of the scheduling heuristics #
def schedule_heuristic(num_threads, schedule_alg, t):
	global last_idle, alloc_queue, curr_thr, alpha, beta, gamma, delta

	thr_list = [] # The thread numbers
	thr_list_sort = [] # The sorted thread numbers

	# The MNTP heuristic #
	if schedule_alg == 'MNTP':
		# Determine the number of parts existing in the queues #
		for i in range(num_threads):
			thr_list.append([i, len(alloc_queue[i])])

		# Sort the numbers based on the minimum number of parts #
		thr_list = sorted(thr_list, key = itemgetter(1), reverse = False)
		for i in range(num_threads):
			thr_list_sort.append(thr_list[i][0])

	# The NT heuristic #
	if schedule_alg == 'NT':
		# Specify the numbers based on the current thread #
		for i in range(num_threads)[curr_thr + 1::]:
			thr_list_sort.append(i)
		for i in range(num_threads)[:curr_thr + 1:]:
			thr_list_sort.append(i)

	# The MRIT heuristic #
	if schedule_alg == 'MRIT':
		# Calculate the recent idle time of the threads #
		for i in range(num_threads):
			if last_idle[i] != -1:
				thr_list.append([i, t - last_idle[i]])
			else:
				thr_list.append([i, 0])

		# Sort the numbers based on the most recent idle time #
		thr_list = sorted(thr_list, key = itemgetter(1), reverse = True)
		for i in range(num_threads):
			thr_list_sort.append(thr_list[i][0])

	# The MTET heuristic #
	elif schedule_alg == 'MTET':
		# Calculate the total execution time of the queues #
		for i in range(num_threads):
			total_et = 0
			for j in range(len(alloc_queue[i])):
				total_et += alloc_queue[i][j].et

			thr_list.append([i, total_et])

		# Sort the numbers based on the minimum total execution time #
		thr_list = sorted(thr_list, key = itemgetter(1), reverse = False)
		for i in range(num_threads):
			thr_list_sort.append(thr_list[i][0])

	# The MTRT heuristic #
	elif schedule_alg == 'MTRT':
		# Calculate the total response time of the queues #
		for i in range(num_threads):
			total_rt = 0
			for j in range(len(alloc_queue[i])):
				total_rt += alloc_queue[i][j].rt

			thr_list.append([i, total_rt])

		# Sort the numbers based on the maximum total response time #
		thr_list = sorted(thr_list, key = itemgetter(1), reverse = True)
		for i in range(num_threads):
			thr_list_sort.append(thr_list[i][0])

	# The TMCD heuristic #
	elif schedule_alg == 'TMCD':
		# Calculate the recent idle time of the threads #
		rec_idle_time = []
		for i in range(num_threads):
			if last_idle[i] != -1:
				rec_idle_time.append(t - last_idle[i])
			else:
				rec_idle_time.append(0)

		# Calculate total number of parts, total execution time, and total response time of the queues #
		total_num_parts = 0
		total_it = 0
		total_et = 0
		for i in range(num_threads):
			total_it += rec_idle_time[i]
			for j in range(len(alloc_queue[i])):
				total_num_parts += 1
				total_et += alloc_queue[i][j].et

		if total_num_parts == 0:
			total_num_parts = 1
		if total_et == 0:
			total_et = 1

		# Calculate the cost of the queues #
		for i in range(num_threads):
			sum_et = 0
			for j in range(len(alloc_queue[i])):
				sum_et += alloc_queue[i][j].et

			if rec_idle_time[i] != 0:
				val_it = 1 / (rec_idle_time[i] / total_it)
			else:
				val_it = 0

			thr_list.append([i, alpha * len(alloc_queue[i]) / total_num_parts + beta * val_it + gamma * sum_et / total_et])

		# Sort the numbers based on the least cost #
		thr_list = sorted(thr_list, key = itemgetter(1), reverse = False)
		for i in range(num_threads):
			thr_list_sort.append(thr_list[i][0])

	return thr_list_sort

# Choose a part from the allocation queue using one of the allocation heuristics #
def alloc_heuristic(sel_parts, alloc_alg):
	global theta, psi

	# The MET heuristic #
	if alloc_alg == 'MET':
		part_id = 0
		# Find the queue with the minimum execution time #
		for i in range(len(sel_parts))[1::]:
			if sel_parts[i].et < sel_parts[part_id].et:
				part_id = i

	# The MRT heuristic #
	if alloc_alg == 'MRT':
		part_id = 0
		# Find the queue with the maximum response time #
		for i in range(len(sel_parts))[1::]:
			if sel_parts[i].rt > sel_parts[part_id].rt:
				part_id = i

	# The MCD heuristic #
	if alloc_alg == 'MCD':
		# Calculate total execution time and total response time of the parts #
		total_et = 0
		total_rt = 0
		for i in range(len(sel_parts)):
			total_et += sel_parts[i].et
			total_rt += sel_parts[i].rt

		# Calculate the cost of each part #
		cost = []
		for i in range(len(sel_parts)):
			cost.append(theta * sel_parts[i].et / total_et + psi * 1 / (sel_parts[i].rt / total_rt))

		# Select the part with the least cost #
		part_id = 0
		for i in range(len(sel_parts)):
			if cost[i] < cost[part_id]:
				part_id = i

	return sel_parts[part_id]

# The mapping process for tied tasks #
def mapping_tied(num_tasks, num_threads, part_list, desc_rel, schedule_alg, alloc_alg):
	global alloc_queue, suspend_list, last_idle, execution_queue, curr_thr, parts_cnt, comp_parts_cnt

	t = 0 # Response time

	# Continue the mapping process while the allocation queues of the threads are not empty, as well as #
	# the execution queues of the threads include any parts in the execution status #
	while comp_parts_cnt < parts_cnt:
		for thr_num in range(num_threads):
			# Check the execution queue of each thread separately #
			if bool(execution_queue[thr_num]):
				part = execution_queue[thr_num][len(execution_queue[thr_num]) - 1]
				# The part is in the execution status and its process has been already finished #
				if part.status == 's' and part.f_time <= t:
					part.status = 'f'

					last_idle[thr_num] = t
					curr_thr = thr_num
					comp_parts_cnt += 1

					# Remove the task from the list of suspended tasks #
					if part.p_id == len(part_list[part.t_id]) - 1:
						suspend_list[thr_num].remove(part.t_id)

					# The part has a sibling part #
					if part.sibling != None:
						alloc_queue[thr_num].append(part.sibling)

					# The part has any child parts #
					new_ready_parts = []
					child_list = func.discover_child(num_tasks, part_list, part)
					for i in range(len(child_list)):
						new_ready_parts.append(child_list[i])

					# Check the new ready parts and allocate them to the allocation queues of the threads #
					if bool(new_ready_parts):
						thr_list = schedule_heuristic(num_threads, schedule_alg, t)

						# Remove thr_num from the list of threads if the part has a sibling part #
						if part.sibling != None:
							thr_list.remove(thr_num)

						# Assign the new ready parts to the allocation queues #
						index = 0
						for i in range(len(new_ready_parts)):
							# Select an allocation queue from the list #
							thread_id = thr_list[index]

							# Add the part to the selected allocation queue #
							alloc_queue[thread_id].append(new_ready_parts[i])

							# Increase the index #
							if index < len(thr_list) - 1:
								index += 1
							else:
								index = 0

			# Check whether the thread is idle #
			if not bool(execution_queue[thr_num]) or execution_queue[thr_num][len(execution_queue[thr_num]) - 1].status == 'f':
				# Check the allocation queue of each thread separately and assign one of the parts to the thread, if any #
				if bool(alloc_queue[thr_num]):
					# Build the list of parts that do not have a data dependency or have a dependency but the related part is finished #
					elg_parts = [] # Eligible parts

					for i in range(len(alloc_queue[thr_num])):
						if alloc_queue[thr_num][i].dep != None:
							flag_finished = False
							for j in range(num_threads):
								for k in range(len(execution_queue[j])):
									if alloc_queue[thr_num][i].dep == execution_queue[j][k] and execution_queue[j][k].status == 'f':
										flag_finished = True

						# Append the part to the selected parts #
						if alloc_queue[thr_num][i].dep == None or (alloc_queue[thr_num][i].dep != None and flag_finished == True):
							elg_parts.append(alloc_queue[thr_num][i])

					# Check whether there are any non-dependent parts #
					if bool(elg_parts):
						# There are not any tasks currently suspended on the thread #
						if not bool(suspend_list[thr_num]):
							# Choose one of the parts using the heuristic algorithm #
							sel_part = alloc_heuristic(elg_parts, alloc_alg)

							# Assign the part to the thread #
							execution_queue[thr_num].append(sel_part)
							part = execution_queue[thr_num][len(execution_queue[thr_num]) - 1]

							part.status = 's'
							part.s_time = t
							part.f_time = t + part.et

							# Append the task to the list of suspended tasks #
							if part.p_id == 0:
								suspend_list[thr_num].append(part.t_id)

							last_idle[thr_num] = -1

							# Remove the part from the queue #
							for i in range(len(alloc_queue[thr_num])):
								if alloc_queue[thr_num][i] == sel_part:
									alloc_queue[thr_num].remove(alloc_queue[thr_num][i])
									break

						# There are any tasks currently suspended on the thread #
						else:
							# Find the parts that belong to or are descendant of the tasks suspended to the thread #
							sel_parts = []
							for i in range(len(elg_parts)):
								# The part is related to a currently suspended task #
								if elg_parts[i].p_id > 0:
									sel_parts.append(elg_parts[i])

								# The part is related to a new task #
								else:
									flag = True
									for j in range(len(suspend_list[thr_num])):
										if desc_rel[suspend_list[thr_num][j]][elg_parts[i].t_id] == 0:
											flag = False

									if flag == True:
										sel_parts.append(elg_parts[i])

							# Check whether there are any selected parts #
							if bool(sel_parts):
								# Choose one of the parts using the heuristic algorithm #
								sel_part = alloc_heuristic(sel_parts, alloc_alg)

								# Assign the part to the thread #
								execution_queue[thr_num].append(sel_part)
								part = execution_queue[thr_num][len(execution_queue[thr_num]) - 1]

								part.status = 's'
								part.s_time = t
								part.f_time = t + part.et

								# Append the task to the list of suspended tasks #
								if part.p_id == 0:
									suspend_list[thr_num].append(part.t_id)

								last_idle[thr_num] = -1

								# Remove the part from the queue #
								for i in range(len(alloc_queue[thr_num])):
									if alloc_queue[thr_num][i] == sel_part:
										alloc_queue[thr_num].remove(alloc_queue[thr_num][i])
										break

		t += 1

	return t

# The mapping process for untied tasks #
def mapping_untied(num_tasks, num_threads, part_list, schedule_alg, alloc_alg):
	global alloc_queue, last_idle, execution_queue, curr_thr, parts_cnt, comp_parts_cnt

	t = 0 # Response time

	# Continue the mapping process while the allocation queues of the threads are not empty, as well as #
	# the execution queues of the threads include any parts in the execution status #
	while comp_parts_cnt < parts_cnt:
		for thr_num in range(num_threads):
			# Check the execution queue of each thread separately #
			if bool(execution_queue[thr_num]):
				part = execution_queue[thr_num][len(execution_queue[thr_num]) - 1]
				# The part is in the execution status and its process has been already finished #
				if part.status == 's' and part.f_time <= t:
					part.status = 'f'

					last_idle[thr_num] = t
					curr_thr = thr_num
					comp_parts_cnt += 1

					new_ready_parts = []
					# The part has a sibling part #
					if part.sibling != None:
						new_ready_parts.append(part.sibling)
					# The part has any child parts #
					child_list = func.discover_child(num_tasks, part_list, part)
					for i in range(len(child_list)):
						new_ready_parts.append(child_list[i])

					# Check the new ready parts and allocate them to the allocation queues of the threads #
					if bool(new_ready_parts):
						thr_list = schedule_heuristic(num_threads, schedule_alg, t)

						index = 0
						# Assign the new ready parts to the allocation queues #
						for i in range(len(new_ready_parts)):
							# Select an allocation queue from the list #
							thread_id = thr_list[index]

							# Add the part to the selected allocation queue #
							alloc_queue[thread_id].append(new_ready_parts[i])

							# Increase the index #
							if index < num_threads - 1:
								index += 1
							else:
								index = 0

			# Check whether the thread is idle #
			if not bool(execution_queue[thr_num]) or execution_queue[thr_num][len(execution_queue[thr_num]) - 1].status == 'f':
				# Check the allocation queue of each thread separately and assign one of the parts to the thread, if any #
				if bool(alloc_queue[thr_num]):
					# Build the list of parts that do not have a data dependency or have a dependency but the related part is finished #
					elg_parts = [] # Eligible parts

					for i in range(len(alloc_queue[thr_num])):
						if alloc_queue[thr_num][i].dep != None:
							flag_finished = False
							for j in range(num_threads):
								for k in range(len(execution_queue[j])):
									if alloc_queue[thr_num][i].dep == execution_queue[j][k] and execution_queue[j][k].status == 'f':
										flag_finished = True

						# Append the part to the selected parts #
						if alloc_queue[thr_num][i].dep == None or (alloc_queue[thr_num][i].dep != None and flag_finished == True):
							elg_parts.append(alloc_queue[thr_num][i])

					# Check whether there are any non-dependent parts #
					if bool(elg_parts):
						# Choose one of the parts using the heuristic algorithm #
						sel_part = alloc_heuristic(elg_parts, alloc_alg)

						# Assign the part to the thread #
						execution_queue[thr_num].append(sel_part)
						part = execution_queue[thr_num][len(execution_queue[thr_num]) - 1]

						part.status = 's'
						part.s_time = t
						part.f_time = t + part.et

						last_idle[thr_num] = -1

						# Remove the part from the queue #
						for i in range(len(alloc_queue[thr_num])):
							if alloc_queue[thr_num][i] == sel_part:
								alloc_queue[thr_num].remove(alloc_queue[thr_num][i])
								break

		t += 1

	return t

# The main mapping process #
def execute(task_type, num_tasks, num_threads, part_list, deadline, desc_rel, first_task_part, schedule_alg, alloc_alg, graphic_result):
	global alloc_queue, suspend_list, last_idle, execution_queue, parts_cnt

	# Determine the number of all the parts #
	for i in range(num_tasks):
		parts_cnt += len(part_list[i])

	# Create an allocation queue for each thread #
	alloc_queue = []
	for i in range(num_threads):
		alloc_queue.append([])

	# Create the initial list of suspended tasks #
	suspend_list = []
	for i in range(num_threads):
		suspend_list.append([])

	# Create a list for the last idle time of the threads #
	last_idle = []
	for i in range(num_threads):
		last_idle.append(0)

	# Create an execution queue for each thread #
	execution_queue = []
	for i in range(num_threads):
		execution_queue.append([])

	# Put the first part of the system in the execution queue of the first thread #
	execution_queue[0].append(first_task_part)
	execution_queue[0][0].status = 's'
	execution_queue[0][0].s_time = 1
	execution_queue[0][0].f_time = 1 + execution_queue[0][0].et

	suspend_list[0].append(0) # Append Task 0 to the list of suspended tasks of Thread 0

	# Show the mapping algorithm and the task type #
	if task_type == 'tied':
		print('\nNEW for tied tasks (' + schedule_alg + ', ' + alloc_alg + ')' + '\n***********************************')
		t = mapping_tied(num_tasks, num_threads, part_list, desc_rel, schedule_alg, alloc_alg)
	else:
		print('\nNEW for untied tasks (' + schedule_alg + ', ' + alloc_alg + ')' + '\n***********************************')
		t = mapping_untied(num_tasks, num_threads, part_list, schedule_alg, alloc_alg)

	# Calculate the results #
	response_time = t # The response time
	idle_time = sum(func.idle_time(num_threads, execution_queue, t)) # The idle time of the system
	waiting_time = func.wait_time(num_threads, execution_queue) # The waiting time of the threads
	miss_deadline = func.miss_deadline(num_tasks, num_threads, part_list, execution_queue, deadline, t) # The missed deadline status of the system

	# Show the results #
	print('Response time: ' + str(response_time))
	print('Idle time: ' + str(idle_time))
	print('Waiting time: ' + str(waiting_time))
	print('Missed deadline: ' + str(miss_deadline))
	'''
	print("\nThe execution queues of the threads:") # The contents of the execution queues of the threads
	for i in range(num_threads):
		print('Thr ' + str(i) + ':')
		for j in range(len(execution_queue[i])):
			print('p' + str(execution_queue[i][j].t_id) + str(execution_queue[i][j].p_id) + ' --> status = ' + execution_queue[i][j].status + ', start waiting time = ' + str(execution_queue[i][j].s_w_time) +\
			 ', finish waiting time = ' + str(execution_queue[i][j].f_w_time) + ', start time = ' + str(execution_queue[i][j].s_time) + ', finish time = ' + str(execution_queue[i][j].f_time))
	'''
	if graphic_result == 1:
		func.graphic_result(num_threads, execution_queue, 'new', task_type, schedule_alg, alloc_alg) # The graphical output

	# Return the results to the main program #
	return response_time, idle_time, waiting_time, miss_deadline
