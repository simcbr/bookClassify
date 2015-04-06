import re

class BOOK:
    
    def __init__(self, bid, cate, title, authors, content):
        self.v_id=bid
        self.v_category=cate    
        self.v_title=re.sub('[^A-Za-z]+', ' ', title)
        self.v_title=self.v_title.lower()
        self.v_authors=re.sub('[^A-Za-z.,; ]+', '', authors)
        self.v_authors=self.v_authors.lower()
        self.v_authors=self.v_authors.split(';')
        self.v_content=re.sub('[^A-Za-z]+', ' ', content)
        self.v_content=self.v_content.lower()
        self.v_gramm={}

    def getID(self):
        return self.v_id

    def getTitle(self):
        return self.v_title
    
    def getCate(self):
        return self.v_category
    
    def getAuthors(self):
        return self.v_authors
    
    def getContent(self):
        return self.v_content
    
    def genGrammFromTitle(self):
        # this function generate the grammar based on title
        i=1
        level= len(self.v_title.split())
        while i<=level:
            if i==1:
                self.v_gramm[i]=self.v_title.split()
            else:
                self.v_gramm[i]=[]
                for k in self.v_gramm[i-1]:
                    for j in self.v_gramm[1]:
                        substr = k + " " + j
                        if substr in self.v_title:
                            self.v_gramm[i].append(substr)
                if len(self.v_gramm[i])==0:
                    break


    def grammMatch(self, title):
        # the function compares the similarity between the title and gramm
        score=0
        
        for k in self.v_gramm.keys():
            tmp=0
            for ind in self.v_gramm[k]:
                if ind in title:
                    tmp += math.pow(2, k)   # the longer gramm match, the high socre
            
            if tmp==0:
                break
            else:
                score += tmp
        
        return score