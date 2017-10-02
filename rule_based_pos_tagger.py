from __future__ import division
import random
from conllu.parser import parse, parse_tree

# function to get tag of a word
def get_most_likely_tag(form):
	if form in upostag_dict:
		candidate_tags = upostag_dict[form]
		tag = max(candidate_tags, key=candidate_tags.get)		
		# print('Candidate: %s => %s' % (candidate_tags, tag))
	else:
		# assume OOV word as noun
		tag = 'NOUN'
	return tag

# for consistency
# SEED = 7

# read training data from file
with open('id-ud-train.conllu', 'r') as f:
	raw_train_data = f.read()

full_train_data = parse(raw_train_data)
num_full_train_data = len(full_train_data)
print("Num full train data: %s" %num_full_train_data)

# create validation data by splitting training data
# the split: 90% training data : 10% validation data
# random.seed(SEED)
random.shuffle(full_train_data)

validation_data = full_train_data[0:559]
train_data = full_train_data[559:]

num_validation_data = len(validation_data)
print("Num validation data: %s" %num_validation_data)

num_train_data = len(train_data)
print("Num train data: %s" %num_train_data)

# read testing data from file
with open('id-ud-dev.conllu', 'r') as f:
	raw_test_data = f.read()

test_data = parse(raw_test_data)
num_test_data = len(test_data)
print("Num test data: %s" %num_test_data)

# create dictionary of upostag
upostag_dict = {}
for sentence in train_data:
	for word in sentence:
		form = word['form']
		upostag = word['upostag']
		# print('%s: %s' % (form, upostag))

		if form not in upostag_dict:
			upostag_dict[form] = {}
		if upostag not in upostag_dict[form]:
			upostag_dict[form][upostag] = 0
		upostag_dict[form][upostag] += 1


# 
count_true = 0
count_false = 0
tagging_error_dict = {}

# patch templates
one_previous_tag_dict = {}
one_next_tag_dict = {}
two_previous_tag_dict = {}
two_next_tag_dict = {}
three_previous_tag_dict = {}
three_next_tag_dict = {}
between_tag_dict = {}

for sentence in validation_data:
	for i, word in enumerate(sentence):
		form = word['form']
		target_tag = word['upostag']
		# Step 1: Assign most likely tag without considering context
		tag = get_most_likely_tag(form)
		
			# print('%s not in train data' % form)
		if tag != target_tag:
			# Step 2: Create a list of tagging errors
			if (tag, target_tag) not in tagging_error_dict:
				tagging_error_dict[(tag, target_tag)] = 0
			tagging_error_dict[(tag, target_tag)] += 1
			# Step 3a: Get 1 previous tag, if exists
			if i > 0:
				previous_tag = get_most_likely_tag(sentence[i-1]['form'])
				if (tag, previous_tag) not in one_previous_tag_dict:
					one_previous_tag_dict[(tag, previous_tag)] = {}
				if target_tag not in  [(tag, previous_tag)]:
					one_previous_tag_dict[(tag, previous_tag)][target_tag] = 0
				one_previous_tag_dict[(tag, previous_tag)][target_tag] += 1
			# Step 3b: Get 1 next tag, if exists
			if i < len(sentence)-2:
				next_tag = get_most_likely_tag(sentence[i+1]['form'])
				if (tag, next_tag) not in one_next_tag_dict:
					one_next_tag_dict[(tag, next_tag)] = {}
				if target_tag not in one_next_tag_dict[(tag, next_tag)]:
					one_next_tag_dict[(tag, next_tag)][target_tag] = 0
				one_next_tag_dict[(tag, next_tag)][target_tag] += 1
			# Step 3c: Get 2 previous tag, if exists
			if i > 1:
				previous_tag = get_most_likely_tag(sentence[i-2]['form'])
				if (tag, previous_tag) not in two_previous_tag_dict:
					two_previous_tag_dict[(tag, previous_tag)] = {}
				if target_tag not in  [(tag, previous_tag)]:
					two_previous_tag_dict[(tag, previous_tag)][target_tag] = 0
				two_previous_tag_dict[(tag, previous_tag)][target_tag] += 1
			# Step 3d: Get 2 next tag, if exists
			if i < len(sentence)-3:
				next_tag = get_most_likely_tag(sentence[i+2]['form'])
				if (tag, next_tag) not in two_next_tag_dict:
					two_next_tag_dict[(tag, next_tag)] = {}
				if target_tag not in two_next_tag_dict[(tag, next_tag)]:
					two_next_tag_dict[(tag, next_tag)][target_tag] = 0
				two_next_tag_dict[(tag, next_tag)][target_tag] += 1
			# Step 3e: Get 3 previous tag, if exists
			if i > 2:
				previous_tag = get_most_likely_tag(sentence[i-3]['form'])
				if (tag, previous_tag) not in three_previous_tag_dict:
					three_previous_tag_dict[(tag, previous_tag)] = {}
				if target_tag not in  [(tag, previous_tag)]:
					three_previous_tag_dict[(tag, previous_tag)][target_tag] = 0
				three_previous_tag_dict[(tag, previous_tag)][target_tag] += 1
			# Step 3f: Get 3 next tag, if exists
			if i < len(sentence)-4:
				next_tag = get_most_likely_tag(sentence[i+3]['form'])
				if (tag, next_tag) not in three_next_tag_dict:
					three_next_tag_dict[(tag, next_tag)] = {}
				if target_tag not in three_next_tag_dict[(tag, next_tag)]:
					three_next_tag_dict[(tag, next_tag)][target_tag] = 0
				three_next_tag_dict[(tag, next_tag)][target_tag] += 1
			# Step 3g: Get previous and next tag, if exists
			if i > 0 and i < len(sentence)-2:
				previous_tag = get_most_likely_tag(sentence[i-1]['form'])
				next_tag = get_most_likely_tag(sentence[i+1]['form'])
				if (previous_tag, tag, next_tag) not in between_tag_dict:
					between_tag_dict[(previous_tag, tag, next_tag)] = {}
				if target_tag not in between_tag_dict[(previous_tag, tag, next_tag)]:
					between_tag_dict[(previous_tag, tag, next_tag)][target_tag] = 0
				between_tag_dict[(previous_tag, tag, next_tag)][target_tag] += 1
			count_false += 1
		else:
			count_true += 1

print('Validation Data Accuracy: %s%%' % (count_true / (count_true + count_false)))

# for key, value in one_previous_tag_dict.iteritems():
# 	print("%s: %s" % (key, value))

list = sorted(tagging_error_dict.items(), key=lambda x: x[1])

threshold = 0
final_one_previous_tag_dict = {}
final_one_next_tag_dict = {}
final_two_previous_tag_dict = {}
final_two_next_tag_dict = {}
final_three_previous_tag_dict = {}
final_three_next_tag_dict = {}
final_between_tag_dict = {}
for key, value in tagging_error_dict.iteritems():
	if value > threshold:
		# print("> Considering %s, %s" % key)
		error_tag = key[0]
		actual_tag = key[1]
		best_patch = -1
		best_patch_true = 0
		count_true_patch = 0
		count_false_patch = 0
		# try applying patch #1
		for sentence in validation_data:
			for i, word in enumerate(sentence):
				is_changed = False
				form = word['form']
				target_tag = word['upostag']
				tag = get_most_likely_tag(form)
				if i > 0 and tag == error_tag:
					previous_tag = get_most_likely_tag(sentence[i-1]['form'])
					if (tag, previous_tag) in one_previous_tag_dict:
						# tag = max(one_previous_tag_dict[(tag, previous_tag)], key=one_previous_tag_dict[(tag, previous_tag)].get)
						tag = actual_tag
						is_changed = True
						# print(tag)
				if tag == target_tag:
					count_true_patch += 1
					if is_changed:
						z = previous_tag
				else:
					count_false_patch += 1
		if count_true_patch > count_true:
			# print("Patch #1 works!")
			# print("Patch #1 : %s (%s)" % (count_true_patch, count_true_patch / (count_true_patch + count_false_patch)))
			best_patch = 0
			best_patch_true = count_true_patch
		# else:
		# 	print("Patch #1 didn't work.")

		count_true_patch = 0
		count_false_patch = 0
		# try applying patch #2
		for sentence in validation_data:
			for i, word in enumerate(sentence):
				is_changed = False
				form = word['form']
				target_tag = word['upostag']
				tag = get_most_likely_tag(form)
				if i < len(sentence)-2 and tag == error_tag:
					next_tag = get_most_likely_tag(sentence[i+1]['form'])
					if (tag, next_tag) in one_next_tag_dict:
						# tag = max(one_next_tag_dict[(tag, next_tag)], key=one_next_tag_dict[(tag, next_tag)].get)
						tag = actual_tag
						is_changed = True
						# print(tag)
				if tag == target_tag:
					count_true_patch += 1
					if is_changed:
						z = next_tag
				else:
					count_false_patch += 1
		if count_true_patch > count_true:
			# print("Patch #2 works!")
			# print("Patch #2 : %s (%s)" % (count_true_patch, count_true_patch / (count_true_patch + count_false_patch)))
			if count_true_patch > best_patch_true:
				best_patch = 1
				best_patch_true = count_true_patch
		# else:
		# 	print("Patch #2 didn't work.")

		count_true_patch = 0
		count_false_patch = 0
		# try applying patch #3
		for sentence in validation_data:
			for i, word in enumerate(sentence):
				is_changed = False
				form = word['form']
				target_tag = word['upostag']
				tag = get_most_likely_tag(form)
				if i > 1 and tag == error_tag:
					previous_tag = get_most_likely_tag(sentence[i-2]['form'])
					if (tag, previous_tag) in two_previous_tag_dict:
						# tag = max(two_previous_tag_dict[(tag, previous_tag)], key=two_previous_tag_dict[(tag, previous_tag)].get)
						tag = actual_tag
						is_changed = True
						# print(tag)
				if tag == target_tag:
					count_true_patch += 1
					if is_changed:
						z = previous_tag
				else:
					count_false_patch += 1
		if count_true_patch > count_true:
			# print("Patch #3 works!")
			# print("Patch #3 : %s (%s)" % (count_true_patch, count_true_patch / (count_true_patch + count_false_patch)))
			if count_true_patch > best_patch_true:
				best_patch = 2
				best_patch_true = count_true_patch
		# else:
		# 	print("Patch #1 didn't work.")

		count_true_patch = 0
		count_false_patch = 0
		# try applying patch #4
		for sentence in validation_data:
			for i, word in enumerate(sentence):
				is_changed = False
				form = word['form']
				target_tag = word['upostag']
				tag = get_most_likely_tag(form)
				if i < len(sentence)-3 and tag == error_tag:
					next_tag = get_most_likely_tag(sentence[i+2]['form'])
					if (tag, next_tag) in two_next_tag_dict:
						# tag = max(two_next_tag_dict[(tag, next_tag)], key=two_next_tag_dict[(tag, next_tag)].get)
						tag = actual_tag
						is_changed = True
						# print(tag)
				if tag == target_tag:
					count_true_patch += 1
					if is_changed:
						z = next_tag
				else:
					count_false_patch += 1
		if count_true_patch > count_true:
			# print("Patch #4 works!")
			# print("Patch #4 : %s (%s)" % (count_true_patch, count_true_patch / (count_true_patch + count_false_patch)))
			if count_true_patch > best_patch_true:
				best_patch = 3
				best_patch_true = count_true_patch
		# else:
		# 	print("Patch #2 didn't work.")

		count_true_patch = 0
		count_false_patch = 0
		# try applying patch #5
		for sentence in validation_data:
			for i, word in enumerate(sentence):
				is_changed = False
				form = word['form']
				target_tag = word['upostag']
				tag = get_most_likely_tag(form)
				if i > 2 and tag == error_tag:
					previous_tag = get_most_likely_tag(sentence[i-3]['form'])
					if (tag, previous_tag) in three_previous_tag_dict:
						# tag = max(three_previous_tag_dict[(tag, previous_tag)], key=three_previous_tag_dict[(tag, previous_tag)].get)
						tag = actual_tag
						is_changed = True
						# print(tag)
				if tag == target_tag:
					count_true_patch += 1
					if is_changed:
						z = previous_tag
				else:
					count_false_patch += 1
		if count_true_patch > count_true:
			# print("Patch #5 works!")
			# print("Patch #5 : %s (%s)" % (count_true_patch, count_true_patch / (count_true_patch + count_false_patch)))
			if count_true_patch > best_patch_true:
				best_patch = 4
				best_patch_true = count_true_patch
		# else:
		# 	print("Patch #1 didn't work.")

		count_true_patch = 0
		count_false_patch = 0
		# try applying patch #6
		for sentence in validation_data:
			for i, word in enumerate(sentence):
				is_changed = False
				form = word['form']
				target_tag = word['upostag']
				tag = get_most_likely_tag(form)
				if i < len(sentence)-4 and tag == error_tag:
					next_tag = get_most_likely_tag(sentence[i+3]['form'])
					if (tag, next_tag) in three_next_tag_dict:
						# tag = max(three_next_tag_dict[(tag, next_tag)], key=three_next_tag_dict[(tag, next_tag)].get)
						tag = actual_tag
						is_changed = True
						# print(tag)
				if tag == target_tag:
					count_true_patch += 1
					if is_changed:
						z = next_tag
				else:
					count_false_patch += 1
		if count_true_patch > count_true:
			# print("Patch #6 works!")
			# print("Patch #6 : %s (%s)" % (count_true_patch, count_true_patch / (count_true_patch + count_false_patch)))
			if count_true_patch > best_patch_true:
				best_patch = 5
				best_patch_true = count_true_patch
		# else:
		# 	print("Patch #2 didn't work.")

		count_true_patch = 0
		count_false_patch = 0
		# try applying patch #7
		for sentence in validation_data:
			for i, word in enumerate(sentence):
				is_changed = False
				form = word['form']
				target_tag = word['upostag']
				tag = get_most_likely_tag(form)
				if i < len(sentence)-2 and i > 0 and tag == error_tag:
					previous_tag = get_most_likely_tag(sentence[i-1]['form'])
					next_tag = get_most_likely_tag(sentence[i+1]['form'])
					if (previous_tag, tag, next_tag) in between_tag_dict:
						# tag = max(between_tag_dict[(previous_tag, tag, next_tag)], key=between_tag_dict[(previous_tag, tag, next_tag)].get)
						tag = actual_tag
						is_changed = True
						# print(tag)
				if tag == target_tag:
					count_true_patch += 1
					if is_changed:
						y = previous_tag
						z = next_tag
				else:
					count_false_patch += 1
		if count_true_patch > count_true:
			# print("Patch #7 works!")
			# print("Patch #7 : %s (%s)" % (count_true_patch, count_true_patch / (count_true_patch + count_false_patch)))
			if count_true_patch > best_patch_true:
				best_patch = 6
				best_patch_true = count_true_patch
		
		# apply best patch
		if best_patch == 0:
			print(best_patch, error_tag, z, actual_tag)
			final_one_previous_tag_dict[(error_tag, z)] = actual_tag
		elif best_patch == 1:
			print(best_patch, error_tag, z, actual_tag)
			final_one_next_tag_dict[(error_tag, z)] = actual_tag
		elif best_patch == 2:
			print(best_patch, error_tag, z, actual_tag)
			final_two_previous_tag_dict[(error_tag, z)] = actual_tag
		elif best_patch == 3:
			print(best_patch, error_tag, z, actual_tag)
			final_two_next_tag_dict[(error_tag, z)] = actual_tag
		elif best_patch == 4:
			print(best_patch, error_tag, z, actual_tag)
			final_three_previous_tag_dict[(error_tag, z)] = actual_tag
		elif best_patch == 5:
			print(best_patch, error_tag, z, actual_tag)
			final_three_next_tag_dict[(error_tag, z)] = actual_tag
		elif best_patch == 6:
			print(best_patch, y, error_tag, z, actual_tag)
			final_between_tag_dict[(y, error_tag, z)] = actual_tag

count_false_test = 0
count_true_test = 0
for sentence in test_data:
	for i, word in enumerate(sentence):
		form = word['form']
		target_tag = word['upostag']
		tag = get_most_likely_tag(form)
		
		if tag != target_tag:
			count_false_test += 1
		else:
			count_true_test += 1

print('Testing Data Accuracy: %s%%' % (count_true_test / (count_true_test + count_false_test)))

count_false_test = 0
count_true_test = 0
for sentence in test_data:
	for i, word in enumerate(sentence):
		form = word['form']
		target_tag = word['upostag']
		tag = get_most_likely_tag(form)

		if i > 0 and final_one_previous_tag_dict:
			previous_tag = get_most_likely_tag(sentence[i-1]['form'])
			if (tag, previous_tag) in final_one_previous_tag_dict:
				tag = final_one_previous_tag_dict[(tag, previous_tag)]

		if i < len(sentence)-2 and final_one_next_tag_dict:
			next_tag = get_most_likely_tag(sentence[i+1]['form'])
			if (tag, next_tag) in final_one_next_tag_dict:
				tag = final_one_next_tag_dict[(tag, next_tag)]

		if i > 1 and final_two_previous_tag_dict:
			previous_tag = get_most_likely_tag(sentence[i-2]['form'])
			if (tag, previous_tag) in final_two_previous_tag_dict:
				tag = final_two_previous_tag_dict[(tag, previous_tag)]

		if i < len(sentence)-3 and final_two_next_tag_dict:
			next_tag = get_most_likely_tag(sentence[i+2]['form'])
			if (tag, next_tag) in final_two_next_tag_dict:
				tag = final_two_next_tag_dict[(tag, next_tag)]

		if i > 3 and final_three_previous_tag_dict:
			previous_tag = get_most_likely_tag(sentence[i-3]['form'])
			if (tag, previous_tag) in final_three_previous_tag_dict:
				tag = final_three_previous_tag_dict[(tag, previous_tag)]

		if i < len(sentence)-4 and final_three_next_tag_dict:
			next_tag = get_most_likely_tag(sentence[i+3]['form'])
			if (tag, next_tag) in final_three_next_tag_dict:
				tag = final_three_next_tag_dict[(tag, next_tag)]

		if i < len(sentence)-2 and i > 0 and final_between_tag_dict:
			previous_tag = get_most_likely_tag(sentence[i-1]['form'])
			next_tag = get_most_likely_tag(sentence[i+1]['form'])
			if (previous_tag, tag, next_tag) in final_between_tag_dict:
				tag = final_between_tag_dict[(previous_tag, tag, next_tag)]
		
		if tag != target_tag:
			count_false_test += 1
		else:
			count_true_test += 1

print('Patch Testing Data Accuracy: %s%%' % (count_true_test / (count_true_test + count_false_test)))