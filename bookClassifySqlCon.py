import MySQLdb as mdb
import sys
import time
import math      
import random
import numpy as np
import book



class BOOKDICTSQLCON:
    def __init__(self):
        self.v_con = None
        self.v_cur = None
        self.v_trivial = ['the', 'and', 'or', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'as', 'has', 'have', 'in', 'on', 'at', 'for', 'to', 'with']
        self.v_cates = None
    
    def openConn(self, hostname, usrname, usrpwd, dbname):
        try:
            self.v_con = mdb.connect(hostname, usrname, usrpwd, dbname, local_infile=1)
            self.v_cur = self.v_con.cursor()
            #self.v_con=mysql.connector.connect(user=usrname, password=usrpwd, host=hostname, database=dbname)
            #self.v_cur = self.v_con.cursor(buffered=True, raw=True)
            #self.v_con.autocommit(True);
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0],e.args[1])
            sys.exit(1)  
    
            
    def commit(self):
        self.v_con.commit()        
    
                            
    def closeConn(self):
        if self.v_con:    
            self.v_con.close()   
            
    def outputQuery(self, queryStr, printEnable, num):
        selectstr = queryStr + " ;"
        self.v_cur.execute(selectstr)
        row = self.v_cur.fetchall()
        
        if printEnable==1:
            for i in range(len(row)):
                print row[i][0]
        else:
            ret=[]
            for i in range(len(row)):
                raw = []
                for j in range(num):
                    raw.append(row[i][j])
                ret.append(raw)
            return ret                    


    def createTabWDICT(self):
        qStr = " create table if not exists wdict (word varchar(64), category varchar(64), bid varchar(64), frequency int, primary key(word, category, bid),"\
            +  " index bid(bid ASC), index word(word ASC), index category(category ASC), index frequency(frequency ASC) ) ";
        self.v_cur.execute(qStr)
        
        qStr = "truncate table wdict"
        self.v_cur.execute(qStr)
        
    
    def createTabAuthors(self):
        qStr = " create table if not exists authors (bid varchar(64) not null, author varchar(128), category varchar(64), primary key(bid, author),"\
            +  " index bid(bid ASC), index author(author ASC), index category(category ASC) ) ";
        self.v_cur.execute(qStr)
        
        qStr = "truncate table authors"
        self.v_cur.execute(qStr)
        
        
    def createTabFeatureMI(self):
        qStr = " create table if not exists featureMI (word varchar(128), category varchar(64), N11 int, N01 int, N10 int, N00 int, MI float, primary key(word, category),"\
            +  " index word(word ASC), index category(category ASC) ) ";
        self.v_cur.execute(qStr)
        
        qStr = "truncate table featureMI"
        self.v_cur.execute(qStr)        
        
        
    def createTabSelFeatures(self):
        # pr_MN: multinormial; pr_BN: bernoulli
        qStr = " create table if not exists selFeatures (word varchar(128), category varchar(64), pr_MN float, pr_BN float, primary key(word, category),"\
            +  " index word(word ASC), index category(category ASC) ) ";
        self.v_cur.execute(qStr)
        
        qStr = "truncate table selFeatures"
        self.v_cur.execute(qStr)         
        
        
    def getCates(self):
        qStr = " select distinct(category) from wdict"
        ret=self.outputQuery(qStr,0,1)
        return ret
        
        
    def insertBook(self, book):
        quote="\""
        cate = book.getCate()
        authors = book.getAuthors()
        bid = book.getID()
        # title
        words = book.getTitle().split()
        words += book.getContent().split()
        # INSERT INTO table (a,b,c) VALUES (1,2,3)
        #    ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id), c=3;
        for w in words:
            if (w not in self.v_trivial) and len(w)>1:
                qStr= " insert into wdict (bid, word, category, frequency) values (" + quote + bid + quote + "," \
                      + quote + w + quote + "," + quote + cate + quote + ",1) "\
                      " on duplicate key update frequency=frequency+1"
                self.v_cur.execute(qStr)
        
        # authors
        for author in authors:
            qStr= " insert into authors (bid, author, category) values (" + quote + book.getID() + quote + "," + quote + author + quote + ","\
                 + quote + cate + quote + ") on duplicate key update category=" + quote + cate + quote
            self.v_cur.execute(qStr)
        
        
    # total number of unique words
    def totalWords(self):
        qStr="select count(distinct(word)) from wdict"
        ret=self.outputQuery(qStr,0,1)
        return int(ret[0][0])

    # only return the words in selFeatures
    def vocabularyList(self):
        qStr="select distinct(word) from selFeatures"
        ret=self.outputQuery(qStr,0,1)
        return ret

    # total number of unique authors
    def totalAuthors(self):
        qStr="select count(distinct(author)) from authors"
        ret=self.outputQuery(qStr,0,1)
        return int(ret[0][0])
    
    def totalBooks(self):
        quote="\""
        qStr="select count(distinct(bid)) from authors"
        B=self.outputQuery(qStr,0,1)[0][0]
        return int(B)
    
    # number of words in cate's books (count duplicated)
    def cateWordsLength(self, cate):
        quote="\""
        qStr="select sum(frequency) from wdict where category=" + quote + cate + quote
        ret=self.outputQuery(qStr,0,1)
        return int(ret[0][0])        
    
    # number of authors cate's books (count duplicated)
    def cateAuthorsLength(self, cate):
        quote="\""
        qStr="select count(author) from authors where category=" + quote + cate + quote
        ret=self.outputQuery(qStr,0,1)
        return int(ret[0][0])  
    
    #books belong to this cate
    def cateBooks(self, cate):
        quote="\""
        qStr="select count(distinct(bid)) from authors where category=" + quote + cate + quote
        A=self.outputQuery(qStr,0,1)[0][0]
        return int(A)        
    

            
    # probability a category appears
    def catePr(self, cate):
        A=self.cateBooks(cate)
        B=self.totalBooks()
        return 1.0*int(A)/int(B)
    
    # return word's frequency
    def wordFreq(self, w, cate):
        quote="\""
        qStr = "select sum(frequency) from wdict where word=" + quote + w + quote + " and category=" + quote + cate + quote
        ret=self.outputQuery(qStr,0,1)
        if len(ret)==0:
            ret=0
        else:
            ret=int(ret[0][0])
        return ret
    
    #multinominal
    # the log probability of a word belongs to a cate 
    def wordPrM(self, words, cate):
        tuw = self.totalWords()
        cwl = self.cateWordsLength(cate)
        pr=0         
        quote="\""
        for w in words:
            qStr="select ifnull(pr_MN,0) from selFeatures where word=" + quote + w + quote + " and category=" + quote + cate + quote
            ret=self.outputQuery(qStr,0,1)
            if len(ret)==0: # the word not in vocabulary
                pr += math.log( 1.0/(cwl + tuw) )
            else:
                pr += math.log(float(ret[0][0])) 
        
        return pr
    
    #bernoulli
    def wordPrB(self, words, cate):
        # count how many books in this category use the word   (Nct + 1)/(Nc + 2)
        V =  self.vocabularyList()
        Nc = self.cateBooks(cate) 
        quote="\""
        pr=0
        
        words=list(set(words))
        for v in V:
            qStr="select pr_BN from selFeatures where word=" + quote + v[0] + quote + " and category=" + quote + cate + quote
            ret = self.outputQuery(qStr,0,1)
            if len(ret)==0: # the v is not in this category
                ret = 1.0/(Nc + 2)
            else:
                ret = float(ret[0][0])
                            
            if v in words:
                pr += math.log(ret)
            else:
                pr += math.log(1-ret)
                
        return pr
        
        
    # the log probability of an author belongs to a cate    
    def authorPr(self, author, cate):
        tua = self.totalAuthors()
        cal = self.cateAuthorsLength(cate)
        quote="\""
        qStr="select ifnull(count(bid),0) from authors where author=" + quote + author + quote + " and category=" + quote + cate + quote
        ret=self.outputQuery(qStr,0,1)
        return math.log( 1.0*(ret[0][0] + 1)/(cal + tua) )
                
        
    
    # calculate the mutual information score for each word of each category
    def featureMI(self, K):
        quote="\""
        qStr=" truncate table featureMI"
        self.v_cur.execute(qStr)
          
        qStr= "insert featureMI (word, category,N11) (select word as w, category as c, count(distinct(bid)) as n11 from wdict as w1 group by category,word)"\
               + " on duplicate key update word=word"
        self.v_cur.execute(qStr)
          
        qStr="update featureMI, (select count(distinct(bid)) as s, category as c from wdict group by category) as t"\
            + " set featureMI.N01=t.s-featureMI.N11 where featureMI.category=t.c"
        self.v_cur.execute(qStr)
          
        qStr="update featureMI, (select count(distinct(bid)) as s, word as w from wdict group by word) as t"\
            + " set featureMI.N10=t.s-featureMI.N11 where featureMI.word=t.w"
        self.v_cur.execute(qStr)
          
        qStr="update featureMI, (select count(distinct(bid)) as s from wdict) as t set featureMI.N00=t.s-featureMI.N10"
        self.v_cur.execute(qStr)
          
          
        qStr=" update featureMI set MI="\
            + "   N11/(N11+N01+N10+N00)*log( (N11+N01+N10+N00)*N11/( (N10+N11)*(N01+N11)) )"\
            + " + N01/(N11+N01+N10+N00)*log( (N11+N01+N10+N00)*N01/( (N00+N01)*(N01+N11) )) "\
            + " + N10/(N11+N01+N10+N00)*log( (N11+N01+N10+N00)*N10/( (N10+N11)*(N00+N10) )) "\
            + " + N00/(N11+N01+N10+N00)*log( (N11+N01+N10+N00)*N00/( (N00+N01)*(N00+N10) )) "
        self.v_cur.execute(qStr)
        
        
        qStr="select category from featureMI group by category"
        cates=self.outputQuery(qStr,0,1)
        
        qStr=" truncate table selFeatures"
        self.v_cur.execute(qStr)        
        
        for c in cates:
            qStr="insert selFeatures (word, category) "\
                 + "(select word,category from featureMI where category=" + quote + c[0] + quote\
                 + " order by MI DESC limit 0," + str(K) + ")"
            self.v_cur.execute(qStr)
            
        
        self.commit()
            
        
    def updatePr(self):
        tuw = self.totalWords()
        qStr="select category from featureMI group by category"
        cates=self.outputQuery(qStr,0,1)
        quote="\""        
        for c in cates: 
            cwl = self.cateWordsLength(c[0]) 
            Nc = self.cateBooks(c[0])        
    
            qStr="update selFeatures, (select sum(frequency) as f, count(distinct(bid)) as e, word as w, category as c from wdict "\
                + " where category=" + quote + c[0] + quote + " group by word,category) as t"\
                + " set selFeatures.pr_MN=1.0*(ifnull(t.f,0)+1)/(" + str(cwl) + "+" + str(tuw) + ")"\
                + " ,   selFeatures.pr_BN=1.0*(ifnull(t.e,0)+1)/(" + str(Nc) + "+2)"\
                + " where selFeatures.word=t.w and selFeatures.category=t.c;"
            self.v_cur.execute(qStr)
        self.commit()
        
