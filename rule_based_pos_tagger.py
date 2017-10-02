from conllu.parser import parse, parse_tree

# read train data
with open('id-ud-train.conllu', 'r') as f:
	raw_train_data = f.read()

train_data = parse(raw_train_data)
num_train_data = len(train_data)
print("Num train data: %s" %num_train_data)

# read test data
with open('id-ud-dev.conllu', 'r') as f:
	raw_test_data = f.read()

test_data = parse(raw_test_data)
num_test_data = len(test_data)
print("Num test data: %s" %num_test_data)

# create vocabulary from train data
vocabulary = []
for sentence in train_data:
	for word in sentence:
		vocabulary.append(word['form'])

vocabulary = set(vocabulary)
print(len(vocabulary))

# create dictionary of upostag
upostag_dict = {}
for sentence in train_data:
	for word in sentence:
		form = word['form']
		upostag = word['upostag']
		if upostag not in upostag_dict:
			upostag_dict[upostag] = []
		upostag_dict[upostag].append(form)

for key, value in upostag_dict.iteritems():
	upostag_dict[key] = set(value)

for key, value in upostag_dict.iteritems():
	print("%s: %s" % (key, len(value)))

# test testing data with rules
for sentence in test_data:
	for word in sentence:
		form = word['form']
		# Rule 1: check if capital
		is_capital = form.istitle()
		# Rule 2: check if exists in vocabulary
		is_in_vocabulary = form in vocabulary