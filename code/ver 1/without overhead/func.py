 #**************************************************************************
 # func.py
 #
 # This file includes most of the functions that can be used by different
 # files.
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
from PIL import Image, ImageDraw, ImageFont

# Traverse the graph through the task parts #
def traverse(num_tasks, part_list, task_part):
	print('p' + str(task_part.t_id) + str(task_part.p_id))

	child_list = discover_child(num_tasks, part_list, task_part)
	for i in range(len(child_list)):
		traverse(num_tasks, part_list, child_list[i])

	if task_part.sibling != None:
		traverse(num_tasks, part_list, task_part.sibling)

# Clear the details of the list of parts #
def clear(num_tasks, part_list):
	for i in range(num_tasks):
		for j in range(len(part_list[i])):
			part_list[i][j].status = None
			part_list[i][j].s_w_time = None
			part_list[i][j].f_w_time = None
			part_list[i][j].s_time = None
			part_list[i][j].f_time = None

	return part_list

# Discover the child tasks of a part #
def discover_child(num_tasks, part_list, parent_part):
	child_list = []

	for i in range(num_tasks):
		for j in range(len(part_list[i])):
			if part_list[i][j].parent == parent_part:
				child_list.append(part_list[i][j])

	return child_list

# Find an idle thread #
def find_idle_thread(num_threads, thread_queue, curr_thread_num):
	thread_num = None

	# If the number of threads is less than or equal to 2 #
	if num_threads <= 2:
		if curr_thread_num == 0:
			for i in range(num_threads)[::-1]:
				if not bool(thread_queue[i]) or thread_queue[i][len(thread_queue[i]) - 1].status == 'f':
					thread_num = i
					break			
		else:
			for i in range(num_threads)[::]:
				if not bool(thread_queue[i]) or thread_queue[i][len(thread_queue[i]) - 1].status == 'f':
					thread_num = i
					break				

	# If the number of threads is more than 2 #
	else:
		if curr_thread_num != num_threads - 1:
			for i in range(num_threads)[curr_thread_num + 1::]:
				if not bool(thread_queue[i]) or thread_queue[i][len(thread_queue[i]) - 1].status == 'f':
					thread_num = i
					break

			if thread_num == None:
				for i in range(num_threads)[:curr_thread_num:]:
					if not bool(thread_queue[i]) or thread_queue[i][len(thread_queue[i]) - 1].status == 'f':
						thread_num = i
						break
		else:
			for i in range(num_threads):
				if not bool(thread_queue[i]) or thread_queue[i][len(thread_queue[i]) - 1].status == 'f':
					thread_num = i
					break

	return thread_num

# Calculate the idle times #
def idle_time(num_threads, queue, t):
	idle_time_thr = [] # Idle time of each thread
	# Determine the idle time of each thread separately #
	for i in range(num_threads):
		busy_time = [] # Busy time
		# Look for the queue of the thread #
		for j in range(len(queue[i])):
			s_time = 0
			f_time = 0

			# Specify whether the part existing in the queue includes a waiting process #
			if queue[i][j].s_w_time != None:
				s_time = queue[i][j].s_w_time
			else:
				s_time = queue[i][j].s_time

			# Determine whether the part existing in the queue has been executed completely #
			if queue[i][j].f_time != None:
				f_time = queue[i][j].f_time
			else:
				f_time = t

			busy_time.append([s_time, f_time])

		# Calculate the idle time of the thread based on its busy (wait and/or execution) times #
		idle_time_thr.append([])
		idle_time_thr[i] = 0
		for k in range(t):
			flag = False
			for m in range(len(busy_time)):
				if (k + 1) >= busy_time[m][0] and (k + 1) <= busy_time[m][1]:
					flag = True
			# Identify whether the thread is idle at time k #
			if flag == False:
				idle_time_thr[i] += 1

	return idle_time_thr

# Calculate the waiting time of the threads (data dependency)
def wait_time(num_threads, queue):
	time = 0
	for i in range(num_threads):
		for j in range(len(queue[i])):
			if queue[i][j].s_w_time != None and queue[i][j].f_w_time != None:
				time += queue[i][j].f_w_time - queue[i][j].s_w_time

	return time

# Specify the missed deadline status of the whole system #
def miss_deadline(num_tasks, num_threads, part_list, queue, deadline, t):
	s_time = 0 # Start time
	f_time = 0 # Finish time
	# Check the parts existing in the queue of each thread #
	for i in range(num_threads):
		for j in range(len(queue[i])):
			# Determine start time of the first part of the first task based on the waiting or execution process #
			if queue[i][j].t_id == 0 and queue[i][j].p_id == 0:
				# Specify whether the part includes a waiting time #
				if queue[i][j].s_w_time != None:
					s_time = queue[i][j].s_w_time
				else:
					s_time = queue[i][j].s_time

			# Determine finish time of the last part of the last task #
			if queue[i][j].t_id == (num_tasks - 1) and queue[i][j].p_id == (len(part_list[num_tasks - 1]) - 1):
				# Specify whether the part has been finished completely #
				if queue[i][j].f_time != None:
					f_time = queue[i][j].f_time
				else:
					f_time = t

	# Determine whether the whole system has not missed its deadline #
	if (f_time - s_time) <= deadline:
		return 0
	else:
		return 1

# Draw the graphical result #
def graphic_result(num_threads, queue, alg_name, task_type, par1, par2):
	# Specify the width and height of the window #
	win_width = num_threads * 100 + (num_threads - 1) * 10 + 100
	queue_height = 0
	for i in range(num_threads):
		if bool(queue[i]):
			if queue_height < queue[i][len(queue[i]) - 1].f_time:
				queue_height = queue[i][len(queue[i]) - 1].f_time
	win_height = queue_height * 10 + 100

	# Prepare the drawing process #
	im = Image.new('RGB', (win_width, win_height), (255, 255, 255))
	draw = ImageDraw.Draw(im)

	# Draw the name and content of each thread separately #
	l_point = 50
	font_thr_id = ImageFont.truetype(r'C:\Users\System-Pc\Desktop\arial.ttf', 20) 
	font_part_id = ImageFont.truetype(r'C:\Users\System-Pc\Desktop\arial.ttf', 15)
	for j in range(num_threads):
		# Draw the name of the thread #
		thr_id = 'Thr ' + str(j)
		draw.text((l_point + 25, 20), thr_id, fill = "black", font = font_thr_id, align = "center")

		# Draw the main box of the thread #
		draw.rectangle((l_point, 50, l_point + 100, queue_height * 10 + 60), fill = (255, 255, 255), outline = (0, 0, 0), width = 2)

		for k in range(len(queue[j])):
			# Draw the box related to the waiting process #
			if queue[j][k].s_w_time != None and queue[j][k].f_w_time != None:
				draw.rectangle((l_point, queue[j][k].s_w_time * 10 + 50, l_point + 100, queue[j][k].f_w_time * 10 + 50), fill = (200, 200, 200), outline = (0, 0, 0), width = 1)
			# Draw the box related to the execution process #
			draw.rectangle((l_point, queue[j][k].s_time * 10 + 50, l_point + 100, queue[j][k].f_time * 10 + 50), fill = (0, 255, 0), outline = (0, 0, 0), width = 1)
			# Draw the name of each part #
			part_id = 'p' + str(queue[j][k].t_id) + str(queue[j][k].p_id)
			draw.text((l_point + 40, (queue[j][k].s_time + (queue[j][k].f_time - queue[j][k].s_time) // 2) * 10 + 45), part_id, fill = "black", font = font_part_id, align = "center")

		l_point += 110

	# Create the output file #
	if alg_name == 'bfs':
		if task_type == 'tied':
			im.save('bfs_tied.jpg', quality = 300)
		else:
			im.save('bfs_untied.jpg', quality = 300)
	elif alg_name == 'wfs':
		if task_type == 'tied':
			im.save('wfs_tied.jpg', quality = 300)
		else:
			im.save('wfs_untied.jpg', quality = 300)
	elif alg_name == 'new':
		if task_type == 'tied':
			im.save('new_' + par1 + '_' + par2 + '_tied.jpg', quality = 300)
		else:
			im.save('new_' + par1 + '_' + par2 + '_untied.jpg', quality = 300)
	elif alg_name == 'lnsnl':
		if task_type == 'tied':
			im.save('lnsnl_tied.jpg', quality = 300)
		else:
			im.save('lnsnl_untied.jpg', quality = 300)
