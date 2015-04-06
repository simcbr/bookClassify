import math      
import random    
from datetime import datetime
import os
import sys
import re


class WDICT:
    def __init__(self):
        self.v_dict={}  # based on category
        self.v_trivial = ['the', 'and', 'or', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'as', 'has', 'have', 'in', 'on', 'at']
        self.v_booksNum=0
        
    def setBooksNum(self, num):
        self.v_booksNum = num
        
    def insertBook(self, book):
        cate = book.getCate()
        if cate not in self.v_dict.keys():
            self.v_dict[cate]=[{}, {}, 0] # first dict for words, second for authors
        
        words = book.getTitle().split()
        for w in words:
            if w not in self.v_trivial and len(w)>1:
                if w not in self.v_dict[cate][0].keys():
                    self.v_dict[cate][0][w] = 1
                else:
                    self.v_dict[cate][0][w] += 1
                    
        words = book.getContent().split()
        for w in words:
            if w not in self.v_trivial and len(w)>1:
                if w not in self.v_dict[cate][0].keys():
                    self.v_dict[cate][0][w] = 1
                else:
                    self.v_dict[cate][0][w] += 1                    

        authors = book.getAuthors()
        for author in authors:
            if author not in self.v_dict[cate][1].keys():
                self.v_dict[cate][1][author]=1
            else:
                self.v_dict[cate][1][author] +=1
    
        self.v_dict[cate][2] += 1  # books belong to this cate
        
    
    # total number of unique words
    def totalWords(self):
        ret=0
        for c in self.v_dict.keys():
            ret += len(self.v_dict[c][0].keys())
        return ret
    
    # total number of unique authors
    def totalAuthors(self):
        ret=0
        for c in self.v_dict.keys():
            ret += len(self.v_dict[c][1].keys())
        return ret
    
    # number of words in cate's books (count duplicated)
    def cateWordsLength(self, cate):
        return sum(self.v_dict[cate][0].values())
    
    # number of authors cate's books (count duplicated)
    def cateAuthorsLength(self, cate):
        return sum(self.v_dict[cate][1].values())
    
    def catePr(self, cate):
        return 1.0*self.v_dict[cate][2]/self.v_booksNum
            
            
    def testCate(self, cate, book):
        # the function returns the probability a book belongs to a cate
        authors = book.getAuthors()
        words = book.getTitle().split()
        pr = 0
        tuw = self.totalWords()
        tua = self.totalAuthors()
        
        for w in words:
            if w in self.v_dict[cate][0].keys():
                pr += math.log( 1.0*(self.v_dict[cate][0][w] + 1)/(self.cateWordsLength(cate) + tuw)  )
            else:
                pr += math.log( 1.0/(self.cateWordsLength(cate) + tuw)  )

        words = book.getContent().split()                
        for w in words:
            if w in self.v_dict[cate][0].keys():
                pr += math.log( 1.0*(self.v_dict[cate][0][w] + 1)/(self.cateWordsLength(cate) + tuw)  )
            else:
                pr += math.log( 1.0/(self.cateWordsLength(cate) + tuw)  )                
                
        for author in authors:
            if author in self.v_dict[cate][1].keys():
                pr += math.log( 1.0*(self.v_dict[cate][1][author] + 1)/(self.cateAuthorsLength(cate) + tua)   )
            else:
                pr += math.log( 1.0/(self.cateAuthorsLength(cate) + tua)  )
            
        pr += math.log(self.catePr(cate))
        
        return pr
    
    
    def classify(self, book):
        max_pr = -sys.maxint - 1
        cate = ""
        for c in self.v_dict.keys():
            pr = self.testCate(c, book)
            if pr > max_pr:
                max_pr = pr
                cate = c
        
        return cate
            

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
    

class BOOKCLASSIFIER:
    def __init__(self):
        self.v_dirpath='D:/workspace/bookClassify/datasets/'
        self.v_train_books={}
        self.v_test_books={}
        self.v_wdict=WDICT()

    def readInput1(self):
        # since the dataset is not big, just save them into memory.
        fo = open(self.v_dirpath + 'input1.txt')
        line=fo.readline()
        read_train=0
        read_test=0
        
        fw = open(self.v_dirpath + 'myoutput.txt', "w+")
        fw.write("bookID\tpredictedLabel\n")
        
        while line:
            if "N=" in line and "H=[" in line:
                # read train data
                train_num = (line.split('\t')[0]).split('=')[1]
                self.v_wdict.setBooksNum(int(train_num))
                read_train=1
                read_test=0
            
            elif "M=" in line and "H=[" in line:
                test_num = (line.split('\t')[0]).split('=')[1]
                read_test=1
                read_train=0
                
            elif read_train==1:
                terms = line.split('\t')
                cate = terms[0]
                bid = terms[1]
                title = terms[2]
                authors = terms[3]
                book = BOOK(bid, cate, title, authors, "")
                self.v_wdict.insertBook(book)
                
            elif read_test==1:
                terms = line.split('\t')
                bid = terms[0]
                title = terms[1]
                authors = terms[2]
                book = BOOK(bid, "", title, authors, "")
                cate = self.v_wdict.classify(book)
                fw.write(str(bid))
                fw.write('\t')
                fw.write(str(cate))
                fw.write('\n')
            
            else:
                pass
            
            line=fo.readline()
            
        fo.close()
        fw.close()
        
        
    def readInput12(self):
        # since the dataset is not big, just save them into memory.
        fo1 = open(self.v_dirpath + 'input1.txt')
        line1=fo1.readline()
        fo2 = open(self.v_dirpath + 'input2.txt')
        line2=fo2.readline()
        read_train=0
        read_test=0
        
        fw = open(self.v_dirpath + 'myoutput.txt', "w+")
        fw.write("bookID\tpredictedLabel\n")
        
        while line1 and line2:
            if len(line1)<2:
                line1=fo1.readline()
            elif len(line2)<2:
                line2=fo2.readline()
            elif "N=" in line1 and "H=[" in line1:
                # read train data
                train_num = (line1.split('\t')[0]).split('=')[1]
                self.v_wdict.setBooksNum(int(train_num))
                ind=0;
                read_train=1
                read_test=0
                line1=fo1.readline()
                line2=fo2.readline()
            
            elif "M=" in line1 and "H=[" in line1:
                test_num = (line1.split('\t')[0]).split('=')[1]
                ind=0
                read_test=1
                read_train=0
                line1=fo1.readline()
                
            elif read_train==1:
                terms = line1.split('\t')
                cate = terms[0]
                bid1 = terms[1]
                title = terms[2]
                authors = terms[3]
                bid2 = line2.split('\t')[0]
                content = line2.split('\t')[1]
                if bid1==bid2:
                    ind +=1
                    print "loading book:", bid1, " ", ind, "/", train_num 
                    book = BOOK(bid1, cate, title, authors, content)
                    self.v_wdict.insertBook(book)
                else:
                    print "loading error 1: bid mismatch!"
                
                line1=fo1.readline()
                line2=fo2.readline()
                
            elif read_test==1:
                terms = line1.split('\t')
                bid1 = terms[0]
                title = terms[1]
                authors = terms[2]
                bid2 = line2.split('\t')[0]
                content = line2.split('\t')[1]
                if bid1 == bid2:
                    ind += 1
                    print "testing book:", bid1, " ", ind, "/", test_num 
                    book = BOOK(bid1, "", title, authors, content)
                    cate = self.v_wdict.classify(book)
                    fw.write(str(bid1))
                    fw.write('\t')
                    fw.write(str(cate))
                    fw.write('\n')
                else:
                    print "testing error 2: bid mismatch!"
                
                line1=fo1.readline()
                line2=fo2.readline()
            
            else:
                pass
            

            
        fo1.close()
        fo2.close()
        fw.close()        
        
        
    def accuracy(self, testResult, groundTruth):
        fo1 = open(self.v_dirpath + testResult)
        fo2 = open(self.v_dirpath + groundTruth)
        
        true_positive = 0
        total = 0
        
        line1 = fo1.readline()
        line2 = fo2.readline()
        while line1 and line2:
            terms1 = line1.split('\t')
            terms2 = line2.split('\t')
            
            
            if terms1[0]==terms2[0]:
                if "bookID"==terms1:
                    pass
                else:
                    total += 1
                    if terms1[1] == terms2[1]:
                        true_positive += 1
                
            else:
                print "Wrong, book id mismatch!"
                return
            line1 = fo1.readline()
            line2 = fo2.readline()
        print "accuracy: " + str(1.0*true_positive/total)
        
        
def main():
    classifier=BOOKCLASSIFIER()   
    classifier.readInput12()
    classifier.accuracy('myoutput.txt', 'output.txt')
        
if __name__ == '__main__':
    main()      