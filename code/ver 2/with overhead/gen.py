 #**************************************************************************
 # gen.py
 #
 # Generate the graph randomly or based on a predefined structure.
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
import random

dep_list = [] # The list of available dependant parts in the data dependency
desc_rel_flag = 0 # The flag for the descendant relation between tasks

# Look for a parent #
def look_for_parent(parts_list_tmp, child, parent_list, system_model):
	# Find an appropriate parent based on a random process #
	p_id = random.randint(0, len(parts_list_tmp) - 1)
	while parent_list[parts_list_tmp[p_id].t_id] == 0 or parts_list_tmp[p_id].t_id == child.t_id:
		p_id = random.randint(0, len(parts_list_tmp) - 1)

	sel_parent = parts_list_tmp[p_id]
	parent_list[child.t_id] = 1

	return sel_parent, parent_list

# Look for the descendant relation between tasks #
def look_for_desc_rel(num_tasks, parent_child_rel, curr_task, descendant_task):
	global desc_rel_flag

	if curr_task == descendant_task:
		desc_rel_flag = 1
	else:
		# Check child tasks #
		for i in range(num_tasks):
			if parent_child_rel[curr_task][i] == 1:
				look_for_desc_rel(num_tasks, parent_child_rel, i, descendant_task)

# Specify an execution time for each part and create the list of tasks #
def specify_et(num_tasks, part_list, et_min, et_max, deadline_min, deadline_max):
	global desc_rel_flag

	# Specify an execution time for each part #
	for i in range(num_tasks):
		for j in range(len(part_list[i])):
			part_list[i][j].et = random.randint(et_min, et_max)

	# Determine the deadline of the whole system #
	sum_et = 0
	for i in range(num_tasks):
		for j in range(len(part_list[i])):
			sum_et += part_list[i][j].et
	deadline = (random.randint(int(deadline_min * 10), int(deadline_max * 10)) / 10) * sum_et

	# Determine response time of the parts #
	for i in range(num_tasks):
		for j in range(len(part_list[i])):
			part_list[i][j].rt = deadline * part_list[i][j].et / sum_et

	# Specify the descendant relation between tasks #
	parent_child_rel = [] # The parent-child relation
	desc_rel = [] # The descendant relation

	for i in range(num_tasks):
		parent_child_rel.append([])
		for j in range(num_tasks):
			parent_child_rel_flag = 0

			for k in range(len(part_list[i])):
				for z in range(len(part_list[j])):
					if part_list[j][z].parent == part_list[i][k]:
						parent_child_rel_flag = 1
						break

			parent_child_rel[i].append([])
			parent_child_rel[i][j] = parent_child_rel_flag

	for i in range(num_tasks):
		desc_rel.append([])
		for j in range(num_tasks):
			desc_rel_flag = 0

			for k in range(num_tasks):
				if parent_child_rel[i][k] == 1:
					look_for_desc_rel(num_tasks, parent_child_rel, k, j)

			desc_rel[i].append([])
			desc_rel[i][j] = desc_rel_flag

	return part_list, deadline, desc_rel

# Generate the graph randomly #
def graph_rand(num_tasks, num_parts, system_model, part, dep_pro, num_dep_level, min_num_child, max_num_child):
	global dep_list

	# Initialize the task parts #
	part_list = []
	for i in range(num_tasks):
		part_list.append([])

	if system_model == 1:
		# The number of parts for the first task equals the number of tasks #
		for i in range(num_tasks):
			part_list[0].append(part(0, i, None, None, None, None, None, None, None, None, None, None))
		# The number of parts for the next tasks equals 1 #
		for i in range(num_tasks)[1::]:
			part_list[i].append(part(i, 0, None, None, None, None, None, None, None, None, None, None))
	elif system_model == 2:
		for i in range(num_tasks):
			sel_num_parts = random.randint(1, num_parts)
			for j in range(sel_num_parts):
				part_list[i].append(part(i, j, None, None, None, None, None, None, None, None, None, None))
	elif system_model == 3:
		# Only the first part of each task can create child task, so the number of parts for each task equals 2 #
		for i in range(num_tasks):
			sel_num_parts = 2
			for j in range(sel_num_parts):
				part_list[i].append(part(i, j, None, None, None, None, None, None, None, None, None, None))

	# Specify the sibling parts into each task #
	for i in range(num_tasks):
		if len(part_list[i]) > 1:
			for j in range(len(part_list[i]) - 1):
				part_list[i][j].sibling = part_list[i][j + 1]

	# Specify the parent of each child task #
	if system_model == 1:
		for i in range(num_tasks)[1::]:
			part_list[i][0].parent = part_list[0][i - 1]
	elif system_model == 2:
		parent_list = []
		for i in range(num_tasks):
			parent_list.append(0)
		parent_list[0] = 1

		parts_list_tmp = []
		for i in range(num_tasks):
			for j in range(len(part_list[i])):
				parts_list_tmp.append(part_list[i][j])

		for i in range(num_tasks)[1::]:
			parent, parent_list = look_for_parent(parts_list_tmp, part_list[i][0], parent_list, 2)
			part_list[i][0].parent = parent
	elif system_model == 3:
		completed_list = [] # The list of parts that have child tasks
		inprogress_list = [] # The list of parts that have not yet had child tasks
		waiting_list = [] # The list of waiting parts

		# Initialize the lists #
		inprogress_list.append(part_list[0][0])

		for i in range(num_tasks)[1::]:
			waiting_list.append(part_list[i][0])

		# Specify a parent for each part existing in waiting_list #
		while bool(waiting_list):
			num_child = min_num_child + int(random.random() * (max_num_child - min_num_child)) # The number of child tasks
			if num_child <= len(waiting_list):
				if bool(inprogress_list):
					for i in range(num_child):
						waiting_list[0].parent = inprogress_list[0]
						inprogress_list.append(waiting_list[0])
						waiting_list.remove(waiting_list[0])

					completed_list.append(inprogress_list[0])
					inprogress_list.remove(inprogress_list[0])
			else:
				if bool(inprogress_list):
					for i in range(len(waiting_list)):
						waiting_list[0].parent = inprogress_list[0]
						waiting_list.remove(waiting_list[0])
				else:
					for i in range(len(waiting_list)):
						waiting_list[0].parent = completed_list[len(completed_list) - 1]
						waiting_list.remove(waiting_list[0])

	# Specify the data dependencies between sibling tasks #
	if system_model == 1:
		sel_child_list = [] # The selected list of child tasks
		for i in range(num_tasks)[1::]:
			if random.random() <= dep_pro:
				sel_child_list.append(part_list[i][0])

		index = 0
		num_curr_dep = 0 # The number of current dependencies
		while num_curr_dep < len(sel_child_list) - 1:
			non_dep_list = [] # The non-dependent tasks in the list of child tasks
			for i in range(len(sel_child_list))[index + 1::]:
				if sel_child_list[i].dep == None:
					non_dep_list.append(sel_child_list[i])

			count = 0
			for i in range(len(non_dep_list)):
				if count < num_dep_level:
					non_dep_list[i].dep = sel_child_list[index]
					count += 1
					num_curr_dep += 1
				else:
					break

			index += 1
	elif system_model == 2:
		for i in range(num_tasks):
			for j in range(len(part_list[i])):
				child_list = []
				for k in range(num_tasks):
					if part_list[k][0].parent == part_list[i][j]:
						child_list.append(part_list[k][0])

				sel_child_list = [] # The selected list of child tasks
				for k in range(len(child_list))[1::]:
					if random.random() <= dep_pro:
						sel_child_list.append(child_list[k])

				index = 0
				num_curr_dep = 0 # The number of current dependencies
				while num_curr_dep < len(sel_child_list) - 1:
					non_dep_list = [] # The non-dependent tasks in the list of child tasks
					for k in range(len(sel_child_list))[index + 1::]:
						if sel_child_list[k].dep == None:
							non_dep_list.append(sel_child_list[k])

					count = 0
					for k in range(len(non_dep_list)):
						if count < num_dep_level:
							non_dep_list[k].dep = sel_child_list[index]
							count += 1
							num_curr_dep += 1
						else:
							break

					index += 1
	elif system_model == 3:
		for i in range(num_tasks):
			child_list = []
			for j in range(num_tasks):
				if part_list[j][0].parent == part_list[i][0]:
					child_list.append(part_list[j][0])

			sel_child_list = [] # The selected list of child tasks
			for k in range(len(child_list))[1::]:
				if random.random() <= dep_pro:
					sel_child_list.append(child_list[k])

			index = 0
			num_curr_dep = 0 # The number of current dependencies
			while num_curr_dep < len(sel_child_list) - 1:
				non_dep_list = [] # The non-dependent tasks in the list of child tasks
				for k in range(len(sel_child_list))[index + 1::]:
					if sel_child_list[k].dep == None:
						non_dep_list.append(sel_child_list[k])

				count = 0
				for k in range(len(non_dep_list)):
					if count < num_dep_level:
						non_dep_list[k].dep = sel_child_list[index]
						count += 1
						num_curr_dep += 1
					else:
						break

				index += 1

	return part_list

#  Generate the graph based on a predefined structure #
def graph_predef(num_tasks, part):
	# Initialize the task parts #
	part_list = []
	for i in range(num_tasks):
		part_list.append([])

	part_list[0].append(part(0, 0, None, None, None, None, None, None, None, None, None, None))
	part_list[0].append(part(0, 1, None, None, None, None, None, None, None, None, None, None))
	part_list[0].append(part(0, 2, None, None, None, None, None, None, None, None, None, None))
	part_list[1].append(part(1, 0, None, None, None, None, None, None, None, None, None, None))
	part_list[1].append(part(1, 1, None, None, None, None, None, None, None, None, None, None))
	part_list[1].append(part(1, 2, None, None, None, None, None, None, None, None, None, None))
	part_list[2].append(part(2, 0, None, None, None, None, None, None, None, None, None, None))
	part_list[2].append(part(2, 1, None, None, None, None, None, None, None, None, None, None))
	part_list[3].append(part(3, 0, None, None, None, None, None, None, None, None, None, None))
	part_list[4].append(part(4, 0, None, None, None, None, None, None, None, None, None, None))
	part_list[5].append(part(5, 0, None, None, None, None, None, None, None, None, None, None))
	part_list[5].append(part(5, 1, None, None, None, None, None, None, None, None, None, None))
	part_list[6].append(part(6, 0, None, None, None, None, None, None, None, None, None, None))

	# Specify the sibling parts into each task #
	part_list[0][0].sibling = part_list[0][1]
	part_list[0][1].sibling = part_list[0][2]
	part_list[1][0].sibling = part_list[1][1]
	part_list[1][1].sibling = part_list[1][2]
	part_list[2][0].sibling = part_list[2][1]
	part_list[5][0].sibling = part_list[5][1]

	# Specify the parent of each child task #
	part_list[1][0].parent = part_list[0][0]
	part_list[2][0].parent = part_list[1][0]
	part_list[3][0].parent = part_list[2][0]
	part_list[4][0].parent = part_list[0][1]
	part_list[5][0].parent = part_list[0][2]
	part_list[6][0].parent = part_list[5][0]

	# Specify the data dependencies #
	part_list[1][2].dep = part_list[2][1]
	part_list[5][0].dep = part_list[4][0]

	return part_list
