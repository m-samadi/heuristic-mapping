 #**************************************************************************
 # wfs.py
 #
 # Schedule and execute the task parts of the graph using the work-first
 # scheduler (WFS).
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

# Global variables #
part_queue = [] # The queue of ready parts
thread_queue = [] # The queues of the threads
curr_thread_num = None # The thread number of the last finished task part
parts_cnt = 0 # The number of all the parts
comp_parts_cnt = 0 # The number of completed parts

# The scheduling process for tied tasks #
def schedule_tied(num_tasks, num_threads, part_list):
	global thread_queue, part_queue, curr_thread_num, parts_cnt, comp_parts_cnt

	t = 0 # Scheduling time

	# Continue the scheduling process while the queue of ready parts is not empty and #
	# the queues of the threads do not include any part in the execution status #
	while comp_parts_cnt < parts_cnt:
		for thr_num in range(num_threads):
			# Check the queue of each thread separately #
			if bool(thread_queue[thr_num]):
				part = thread_queue[thr_num][len(thread_queue[thr_num]) - 1]
				# The task is in the execution status and its process has been finished #
				if part.status == 's' and part.f_time <= t:
					part.status = 'f'
					curr_thread_num = thr_num
					comp_parts_cnt += 1

					child_sibling = []

					# If the part includes any child parts #
					child_list = func.discover_child(num_tasks, part_list, part)
					for i in range(len(child_list)):
						child_sibling.append(child_list[i])

					# The part has a sibling part #
					if part.sibling != None:
						child_sibling.append(part.sibling)

					# Insert the child and sibling parts at the beginning of the queue of ready parts #
					for i in range(len(child_sibling))[::-1]:
						part_queue.insert(0, child_sibling[i])

			# Check the list of ready parts and assign them to the threads #
			# This process is done just by the master thread #
			if thr_num == 0:
				if bool(part_queue):
					remove_list = []
					# Look for any part in the queue of ready parts and find a suitable thread for each one #
					for i in range(len(part_queue)):
						# Check whether there is a data dependency, so the related part is finished #
						flag_finished = False
						if part_queue[i].dep != None:
							for j in range(num_threads):
								for k in range(len(thread_queue[j])):
									if part_queue[i].dep == thread_queue[j][k] and thread_queue[j][k].status == 'f':
										flag_finished = True

						# Schedule the part if there is not a data dependency, or #
						# there is a data dependency but the related part is finished #
						if part_queue[i].dep == None or (part_queue[i].dep != None and flag_finished == True):
							# Check whether the part is the first part of the related task #
							if part_queue[i].p_id == 0:
								# Find the thread number of the parent task #
								thread_num = None
								for j in range(num_threads):
									for k in range(len(thread_queue[j])):
										if part_queue[i].parent.t_id == thread_queue[j][k].t_id:
											thread_num = j
											break

								# If the thread number is found #
								if thread_num != None and thread_queue[thread_num][len(thread_queue[thread_num]) - 1].status == 'f':
									thread_queue[thread_num].append(part_queue[i])
									new_part = thread_queue[thread_num][len(thread_queue[thread_num]) - 1]

									new_part.status = 's'
									new_part.s_time = t
									new_part.f_time = t + part_queue[i].et

									remove_list.append(part_queue[i])
							else:
								# Find the thread number of the first part #
								thread_num = None
								for j in range(num_threads):
									for k in range(len(thread_queue[j])):
										if part_queue[i].t_id == thread_queue[j][k].t_id:
											thread_num = j
											break

								# If the thread number is found #
								if thread_num != None and thread_queue[thread_num][len(thread_queue[thread_num]) - 1].status == 'f':
									thread_queue[thread_num].append(part_queue[i])
									new_part = thread_queue[thread_num][len(thread_queue[thread_num]) - 1]

									new_part.status = 's'
									new_part.s_time = t
									new_part.f_time = t + part_queue[i].et

									remove_list.append(part_queue[i])

					# Remove the parts, which were processed, from the queue of ready parts #
					for j in range(len(remove_list)):
						list_index = part_queue.index(remove_list[j])
						part_queue.remove(part_queue[list_index])

		t += 1

	return t

# The scheduling process for untied tasks #
def schedule_untied(num_tasks, num_threads, part_list):
	global thread_queue, part_queue, curr_thread_num, parts_cnt, comp_parts_cnt

	t = 0 # Scheduling time

	# Doing the scheduling process while the queues of the threads and #
	# the queue of ready parts are not empty #
	while comp_parts_cnt < parts_cnt:
		for thr_num in range(num_threads):
			# Check the queue of each thread separately #
			if bool(thread_queue[thr_num]):
				part = thread_queue[thr_num][len(thread_queue[thr_num]) - 1]
				# The task is in the execution status and its process has been finished #
				if part.status == 's' and part.f_time <= t:
					part.status = 'f'
					curr_thread_num = thr_num
					comp_parts_cnt += 1

					child_sibling = []

					# If the part includes any child parts #
					child_list = func.discover_child(num_tasks, part_list, part)
					for i in range(len(child_list)):
						child_sibling.append(child_list[i])

					# The part has a sibling part #
					if part.sibling != None:
						child_sibling.append(part.sibling)

					# Insert the child and sibling parts at the beginning of the queue of ready parts #
					for i in range(len(child_sibling))[::-1]:
						part_queue.insert(0, child_sibling[i])

			# Check the list of ready parts and assign them to the threads #
			# This process is done just by the master thread #
			if thr_num == 0:
				if bool(part_queue):
					remove_list = []
					# Look for any part in the queue of ready parts and find an idle thread for each one #
					for i in range(len(part_queue)):
						# Check whether there is a data dependency, so the related part is finished #
						flag_finished = False
						if part_queue[i].dep != None:
							for j in range(num_threads):
								for k in range(len(thread_queue[j])):
									if part_queue[i].dep == thread_queue[j][k] and thread_queue[j][k].status == 'f':
										flag_finished = True

						# Schedule the part if there is not a data dependency, or #
						# there is a data dependency but the related part is finished #
						if part_queue[i].dep == None or (part_queue[i].dep != None and flag_finished == True):
							# Find an idle thread for the part #
							thread_num = func.find_idle_thread(num_threads, thread_queue, curr_thread_num)

							# An idle thread is found #
							if thread_num != None:
								thread_queue[thread_num].append(part_queue[i])
								new_part = thread_queue[thread_num][len(thread_queue[thread_num]) - 1]

								new_part.status = 's'
								new_part.s_time = t
								new_part.f_time = t + part_queue[i].et

								remove_list.append(part_queue[i])

					# Remove the parts, which were processed, from the queue of ready parts #
					for j in range(len(remove_list)):
						list_index = part_queue.index(remove_list[j])
						part_queue.remove(part_queue[list_index])

		t += 1

	return t

# The main scheduling process #
def execute(task_type, num_tasks, num_threads, part_list, deadline, first_task_part, graphic_result):
	global thread_queue, part_queue, parts_cnt

	# Determine the number of all the parts #
	for i in range(num_tasks):
		parts_cnt += len(part_list[i])

	# Initialize the ready queue #
	part_queue = []

	# Create a queue for each thread #
	thread_queue = []
	for i in range(num_threads):
		thread_queue.append([])

	# Put the first part of the system in the queue of the first thread #
	thread_queue[0].append(first_task_part)
	thread_queue[0][0].status = 's'
	thread_queue[0][0].s_time = 1
	thread_queue[0][0].f_time = 1 + thread_queue[0][0].et

	if task_type == 'tied':
		print('\nWFS for tied tasks\n***********************************')
		t = schedule_tied(num_tasks, num_threads, part_list)
	else:
		print('\nWFS for untied tasks\n***********************************')
		t = schedule_untied(num_tasks, num_threads, part_list)

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
	print("\nThe queues of the threads:") # The contents of the queues of the threads
	for i in range(num_threads):
		print('Thr ' + str(i) + ':')
		for j in range(len(thread_queue[i])):
			print('p' + str(thread_queue[i][j].t_id) + str(thread_queue[i][j].p_id) + ' --> status = ' + thread_queue[i][j].status + ', start waiting time = ' + str(thread_queue[i][j].s_w_time) +\
			 ', finish waiting time = ' + str(thread_queue[i][j].f_w_time) + ', start time = ' + str(thread_queue[i][j].s_time) + ', finish time = ' + str(thread_queue[i][j].f_time))
	'''
	if graphic_result == 1:
		func.graphic_result(num_threads, thread_queue, 'wfs', task_type, '', '') # The graphical output

	# Return the results to the main program #
	return scheduling_time, idle_time, waiting_time, miss_deadline
