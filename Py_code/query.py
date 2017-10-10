from multiprocessing import Process, Lock, Queue, Value
from os import walk
import cyth_query
num_processes 	= 8
class HandleArticles(Process):
	
	should_run 			= True
	
	def __init__(self, words, W ,S, H, in_between, match_idx, end, n, sizes, Count, val_lock, files, result_dir, should_print):
		
		super(HandleArticles, self).__init__()
		self.files		= files
		self.words		= words
		self.H			= H
		# this will be a queue, hence it is thread and process safe
		self.W			= W
		self.S			= S
		self.in_between		= in_between
		self.match_idx		= match_idx
		self.end		= end
		self.n			= n
		self.sizes		= sizes
		self.Count		= Count
		self.val_lock		= val_lock
		self.len_w		= [len(w) for w in self.words]
		self.len_W		= [len(w) for w in self.W]
		self.result_dir		= result_dir + self.name + ".txt"
		self.sequences		= []
		self.should_print	= should_print
	# Take an article, a list of words and of sizes and print all the match
	def handle_sequences(self):
		with open(self.result_dir, "w") as f:
			for matches in self.sequences:
				for match in matches:
					f.write(match + "\n")

	def query_txt_file(self, txt_file):
		with open(txt_file, "r") as articles:
			for art in articles:
				index_bag 	= cyth_query.weighted_query(art, self.W, self.S,self.H, self.in_between, self.match_idx, self.end, self.n, self.len_W)
				#index_bag	= cyth_query.it_query(art, self.words, self.sizes, self.len_w, self.match_idx, self.end, self.n)
				if index_bag:
					with self.val_lock:
						self.Count.value += len(index_bag)
				if self.should_print:	
					self.sequences.append([art[start:end] for start, end in index_bag])
	
	def run(self):
		while self.should_run:
			for txt_file in self.files:
				self.query_txt_file(txt_file)
			self.should_run = False
			if self.should_print:
				self.handle_sequences()
				

def handle_query(query):
	import re
	#parse queries
	query = re.split('\W', query)
	return query[::3], zip(map(int,query[1::3]), map(int,query[2::3]))


def find_match_and_print_one_article(filename, result_dir, words, W , S, H, in_between, match_idx, end, n, sizes, Count, val_lock, should_print):
	len_w		= [len(w) for w in words]
	len_W		= [len(w) for w in W]
	with open(filename[0], "r") as articles:
				for art in articles:
					index_bag 	= cyth_query.weighted_query(art, W, S,H, in_between, match_idx, end, n, len_W)
					#index_bag	= cyth_query.it_query(art, words, sizes, len_w, match_idx, end, n)
					if index_bag:
						Count.value += len(index_bag)
						sequence = [art[start:end] for start, end in index_bag]
	if should_print:
		with open(result_dir, "w") as f:
				for match in sequence:
					f.write(match + "\n")

def main(query, file_queue, result_dir, should_print):
	# we might get a small speed up by only importing modules within functions
	from collections import deque
	words, sizes 			= handle_query(query)
	
	H, W ,S, in_between 		= cyth_query.Hierarchy(words, sizes)
	n 				= len(W)
	match_idx			= [0]*n
	end 				= [0]*n
	article_handler_processes 	= deque()
	Count 				= Value('i', 0)
	val_lock			= Lock()
	# saving the append method as a function "append" should add a little speed, as we do not call a method every time
	append			= article_handler_processes.append
	def create_article_process(files):
		article_handler		= HandleArticles(words, W , S, H, in_between, match_idx, end, n, sizes, Count, val_lock, files, result_dir, should_print)
		article_handler.start()
		append(article_handler)
	
	# start all processes
	if len(file_queue) > 1:
		for i in range(num_processes):
			create_article_process(file_queue[i])
	else:
		find_match_and_print_one_article(file_queue, result_dir + 'Handle.txt', words, W , S, H, in_between, match_idx, end, n, sizes, Count, val_lock, should_print)

	# wait til all processes are done
	for process in article_handler_processes:
		process.join()
	print Count.value


if __name__ == "__main__":
	# we might get a small speed up by only importing modules within functions
	import argparse, os
	from os import listdir
	from os.path import isfile, join
	
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--query", type = str,  help = "Specify query to search through the Wikipedia")
	parser.add_argument("--wiki_size", type = str,  help = "Specify which data to use", default = "all_wiki", choices = ["all_wiki", "wiki_cat", "wiki_starting_with_a"])
	parser.add_argument("--should_print", action = 'store_true', help = "Specify if to print the result or not")
	
	args 		= parser.parse_args()
	wiki_size	= args.wiki_size
	should_print	= args.should_print
	current_dir 	= os.path.dirname(__file__)
	path 		= os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir, "preprocessed_data",wiki_size))
	join_paths	= lambda x: os.path.abspath(os.path.join(path,x))
	for (dirpath, dirnames, filenames) in walk(path):
		n_files		= len(filenames)
		if n_files > 1:
			n 		= len(filenames) / num_processes
			file_queue 	= [map(join_paths, filenames[n*i:n*(i + 1)]) for i in xrange(0, num_processes - 1)]
			last		=  map(join_paths,filenames[n*(num_processes - 1 ):])
			file_queue.append(last)
		else:
			file_queue 	= [join_paths(filenames[0])]
		break
	result_dir	= os.path.abspath(os.path.join(current_dir, os.pardir, "query_results", wiki_size, args.query))

	main(args.query, file_queue, result_dir, should_print)
