def weighted_query(art,W,S,in_between,H,match_idx,end,n):    
    count = 0
    i = 0
    length = len(art)
    end_query = n-1
    start = 0
    find_idx = art.find
    while i!= -1:
        match_idx[i] = find_idx(W[i],start,end[i])
        if match_idx[i] != -1:
            if i == end_query:
                count +=1
                #print(len(art[match_idx[H.index(0)]:match_idx[H.index(end_query)]+len(W[H.index(end_query)])]))
                #if l>209:
                #    print(l)
                start=match_idx[i]+1
            else:
                j= i
                i+=1
                if in_between[j]:
                    start = max(match_idx[S[j][2]]+S[j][0],match_idx[S[j][5]]+S[j][3],0)
                    end[i] = min(match_idx[S[j][2]]+S[j][1],match_idx[S[j][5]]+S[j][4])
                else:
                    start = max(match_idx[S[j][2]]+S[j][0],0)
                    end[i] = match_idx[S[j][2]]+S[j][1]
        else:
            i -= 1
            start = match_idx[i]+1
    return count        
def find_close_left(H,h):
    closest = -1
    idx = -1
    for j,i in enumerate(H):
        if i<h and i>closest:
            closest = i
            idx = j
    return closest,idx  
def find_close_right(H,h):
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
    H = [b[0] for b in sorted(enumerate(words),key=lambda i:len(i[1]),reverse=True)]
    W = sorted(words,key = lambda s: len(s),reverse = True)
    I = sizes
    L = [len(w) for w in words]
    S = [0]*(len(W)-1)
    in_between= [False]*(len(W)-1)
    def left_dist(s,t):
        a = 0
        b = L[h]
        for k in range(s,t):
            a += L[k]+I[k][0]
            b += L[k]+I[k][1]
        return a,b
    def right_dist(g,t):
        a = -L[g]-I[g][1]
        b = -I[g][0]
        for k in range(g+1,t):
            a -= L[k]+I[k][1]
            b -= L[k]+I[k][0]
        return a,b
    i = 1
    for h in H[1:]:
        left,l_idx = find_close_left(H[0:i],h)
        right,r_idx = find_close_right(H[0:i],h)
        if left != -1 and right != -1:
            a,b = left_dist(left,h)
            c,d = right_dist(h,right)
            size = (a,b,l_idx,c,d,r_idx)
            in_between[i-1] = True
        elif left != -1:
            a,b = left_dist(left,h) 
            size = (a,b,l_idx)
        else:
            a,b = right_dist(h,right)    
            size = (a,b,r_idx)
        S[i-1] = size
        i += 1 
    return H,W,S,in_between 