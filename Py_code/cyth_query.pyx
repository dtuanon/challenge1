def it_query(art, words, sizes, len_w, match_idx, end, int n):
	cdef int i, end_query, start, count
	i = 0
	end_query = n-1
	start = 0
	index_bag = set()
	end[0] = len(art)
	while i!= -1:
		match_idx[i] = art.find(words[i],start,end[i])
		if match_idx[i] != -1:
			if i == end_query:
				start = match_idx[i]+1
				index_bag.add((match_idx[0],  match_idx[end_query] + len_w[end_query]))
			else:
				j= i
				i+=1
				start = match_idx[j]+len_w[j]+sizes[j][0]
				end[i] = match_idx[j]+len_w[j]+sizes[j][1]+len_w[i]
		else:
			i -= 1
			start = match_idx[i]+1
		# ensure limits of start and end
		start 	= min(max(start,0), len(art))
		end[i]	= min(end[i],len(art))
	return index_bag

def weighted_query(art,W,S,H,in_between,match_idx,end,int n, len_W):
	cdef  i, length, end_query, start 
	i 		= 0
	length 		= len(art)
	end_query 	= n-1
	start 		= 0
	find_idx 	= art.find
	end[0] 		= length
	index_bag 	= set()
	first_idx 	= H.index(0)
	last_idx 	= H.index(end_query)
	while i!= -1:
		match_idx[i] = find_idx(W[i],start,end[i])
		if match_idx[i] != -1:
			if i == end_query:
				start	=match_idx[i]+1
				index_bag.add((match_idx[first_idx],  match_idx[last_idx] + len_W[last_idx]))
				string 	= art[int(match_idx[first_idx]):int(match_idx[last_idx]) + int(len_W[last_idx])]
			else:
				j= i
				i+=1
				if in_between[j]:
					start 	= match_idx[S[j][2]]+S[j][0],match_idx[S[j][5]]+S[j][3]
					end[i] 	= max(min(match_idx[S[j][2]]+S[j][1],match_idx[S[j][5]]+S[j][4]), start)
				else:
					start 	= match_idx[S[j][2]]+S[j][0]
					end[i]	= max(match_idx[S[j][2]]+S[j][1], start)
				# ensure limits of start and end
				start 	= min( max(start, 0) , length)
				end[i]	= min( max(end[i], 0) , length)
		else:
			i -= 1
			start = match_idx[i]+1
	return index_bag
          
cdef find_close_left(H,int h):
	cdef int closest, idx, i, j, temp
	closest = -1
	idx = -1
	for j,i in enumerate(H):
		if i<h and i>closest:
			closest = i
			idx = j
	return closest,idx  
    
cdef find_close_right(H,int h):
	cdef int closest, idx, i, j, temp
	closest = -1
	idx = -1
	for j,i in enumerate(H):
		if i>h:
			temp = i
			if j>0:
				if temp < closest:
					closest = temp
					idx = j
			else:
				closest = temp
				idx = j
	return closest,idx 
    
def Hierarchy(words,sizes):
	cdef int i, h, a, b, left, l_idx, right, r_idx
	H = [x[0] for x in sorted(enumerate(words),key=lambda i:len(i[1]),reverse=True)]
	W = sorted(words,key = lambda s: len(s),reverse = True)
	I = sizes
	L = [len(w) for w in words]
	S = [0]*(len(W)-1)
	in_between= [False]*(len(W)-1)
	i = 1
    	
    	# calculate the distance (including the length of the words to the left)
    	# This distance has to include the distance of the word itself
	def left_dist(int the_left, int the_word):
		cdef int a, b, k
		a = 0
		b = L[the_word]
		for k in range(the_left,the_word):
			a += L[k]+I[k][0]
			b += L[k]+I[k][1]
		return a,b
	# calculate the distance (including the length of the words to the right)
	# This distance has to account for the length of the word itself
	def right_dist(int the_right, int the_word):
		cdef int a, b, k
		a = -L[the_word]-I[the_word][1]
		b = -I[the_word][0]
		for k in range(the_word + 1, the_right):
			a -= L[k]+I[k][1]
			b -= L[k]+I[k][0]
		return a,b
		
	for h in H[1:]:
		# find the closest word to the right
		left,l_idx = find_close_left(H[0:i],h)
		# find the closest word to the left
		right,r_idx = find_close_right(H[0:i],h)
		if left != -1 and right != -1:
			a,b = left_dist(left, h)
			c,d = right_dist(right, h)
			size = (a,b,l_idx,c,d,r_idx)
			in_between[i-1] = True
		elif left != -1:
			a,b = left_dist(left, h) 
			size = (a,b,l_idx)
		else:
			a,b = right_dist(right, h)
			size = (a,b,r_idx)
		S[i-1] = size
		i += 1 
	return H,W,S,in_between 
