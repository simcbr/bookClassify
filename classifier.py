import math      
import random    
from bookClassifySqlCon import BOOKDICTSQLCON
from book import BOOK
from datetime import datetime
import os
import sys


class CLASSIFIER:
    def __init__(self):
        self.v_dirpath='./datasets/'
        self.v_sql = BOOKDICTSQLCON()
        self.v_sql.openConn('localhost', 'root', 'cbiru', 'Chegg')
        self.v_alg = 0
        
    def dirPath(self):
        return self.v_dirpath    
      
    def installAlg(self, option):
        self.v_alg = option
        
    def createTables(self):
        self.v_sql.createTabWDICT()
        self.v_sql.createTabAuthors()
        self.v_sql.createTabFeatureMI()
        self.v_sql.createTabSelFeatures()
               
            
    def testCate(self, cate, book):
        # the function returns the probability a book belongs to a cate
        # using multinominal algorithm
        authors = book.getAuthors()        
        pr = 0

        words = book.getTitle().split()
        words += book.getContent().split()
        if self.v_alg == 0:  # multinominal
            pr += self.v_sql.wordPrM(words, cate)
        elif self.v_alg == 1:  # bernoulli
            pr += self.v_sql.wordPrB(words, cate)
                
        #for author in authors:
        #    pr += self.v_sql.authorPr(author, cate)
            
        pr += math.log(self.v_sql.catePr(cate))
        
        return pr      
        
    
    
    def classify(self, book):

        max_pr = -sys.maxint - 1
        cate = ""
        cates = self.v_sql.getCates()
        for c in cates:
            pr = self.testCate(c[0], book)
            if pr > max_pr:
                max_pr = pr
                cate = c[0]
            
        return cate
                    
            

    def readTrainFiles(self, option):
        if option==1:
            #only read input1
            fo = open(self.v_dirpath + 'input1.txt')
            line=fo.readline()
            if "N=" in line and "H=[" in line:
                # read train data
                train_num = int((line.split('\t')[0]).split('=')[1])
                ind=1
                
            line=fo.readline()
            while line and ind <= train_num:
                print "loading book: ", ind , "/", train_num
                
                terms = line.split('\t')
                cate = terms[0]
                bid = terms[1]
                title = terms[2]
                authors = terms[3]
                
                book = BOOK(bid, cate, title, authors, "")
                self.v_sql.insertBook(book)
            
                line=fo.readline()
                ind += 1
            
            fo.close()
            
        elif option==2:
            #read input1 and 2
            fo1 = open(self.v_dirpath + 'input1.txt')
            fo2 = open(self.v_dirpath + 'input2.txt')
            line1=fo1.readline()
            line2=fo2.readline()
            if "N=" in line1 and "H=[" in line1:
                # read train data
                train_num = int((line1.split('\t')[0]).split('=')[1])
                ind=1
                
            line1=fo1.readline()
            line2=fo2.readline()
            
            while line1 and line2 and ind <= train_num:
                terms = line1.split('\t')
                cate = terms[0]
                bid1 = terms[1]
                title = terms[2]
                authors = terms[3]
                bid2 = line2.split('\t')[0]
                content = line2.split('\t')[1]
                if bid1==bid2:
                    print "loading book:", bid1, " ", ind, "/", train_num 
                    book = BOOK(bid1, cate, title, authors, content)
                    self.v_sql.insertBook(book)
                    ind += 1
                else:
                    print "loading error 2: bid mismatch!"
            
                line1=fo1.readline()
                line2=fo2.readline()
            
            fo1.close()            
            fo2.close()
            
        self.v_sql.commit()
            
            
            
    def testNewBooks(self, option):
        
        fw = open(self.v_dirpath + 'myoutput.txt', "w+")
        fw.write("bookID\tpredictedLabel\n")
        
        if option==1:
            #using input1
            fo = open(self.v_dirpath + 'input1.txt')
            line=fo.readline()
            read_test=0
            while line:
                if "M=" in line and "H=[" in line:
                    test_num = (line.split('\t')[0]).split('=')[1]
                    read_test=1
                
                elif read_test==1:
                    terms = line.split('\t')
                    bid = terms[0]
                    title = terms[1]
                    authors = terms[2]
                    book = BOOK(bid, "", title, authors, "")
                    cate = self.classify(book)
                    fw.write(str(bid))
                    fw.write('\t')
                    fw.write(str(cate))
                    fw.write('\n')
            
                else:
                    pass
            
                line=fo.readline()
            
        elif option==2:
            #using input1 and 2
            fo1 = open(self.v_dirpath + 'input1.txt')
            fo2 = open(self.v_dirpath + 'input2.txt')
            line1=fo1.readline()
            line2=fo2.readline()
            read_test=0
            while line1 and line2:
                if len(line1)<=1:
                    line1=fo1.readline()
                elif len(line2)<=1:
                    line2=fo2.readline()
                elif "M=" in line1 and "H=[" in line1:
                    test_num = (line1.split('\t')[0]).split('=')[1]
                    read_test=1
                    ind=0
                    line1=fo1.readline()
                
                elif read_test==1:
                    terms = line1.split('\t')
                    bid1 = terms[0]
                    title = terms[1]
                    authors = terms[2]
                    bid2 = line2.split('\t')[0]
                    content = line2.split('\t')[1]
                    
                    if bid1==bid2:
                        ind +=1
                        print "testing book:", bid1, " ", ind, "/", test_num 
                        book = BOOK(bid1, "", title, authors, content)
                        cate = self.classify(book)
                        fw.write(str(bid1))
                        fw.write('\t')
                        fw.write(str(cate))
                        fw.write('\n')
                    else:
                        print "loading error 2: bid mismatch!"                    
                    
                    line1=fo1.readline()
                    line2=fo2.readline()
            
                else:
                    line1=fo1.readline()
                    line2=fo2.readline()
        
            
    def filterFeatures(self, K):
        print "filtering features..."
        self.v_sql.featureMI(K)
        self.v_sql.updatePr()
        
        
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
        return 1.0*true_positive/total
        
def main():
    classifier=CLASSIFIER()
    classifier.createTables() 
    classifier.readTrainFiles(2)
    classifier.installAlg(0)
    fw = open(classifier.dirPath() + 'accuracy_features_2_MN.txt', "w+")
    fw.write("#features\t accuracy\n")
    
    for k in [10, 100, 500, 1000, 5000, 10000]:
    #for k in [100]:
        classifier.filterFeatures(k)
        classifier.testNewBooks(2)
        ret=classifier.accuracy('myoutput.txt', 'output.txt')
        
        fw.write(str(k))
        fw.write("\t")
        fw.write(str(ret))
        fw.write("\n")
        
    fw.close()
    
if __name__ == '__main__':
    main()      