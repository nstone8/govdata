import shelve
def parseRecursively(item):
    '''Try to parse item as python code. If it parses sucessfully attempt to parse its children and return it, otherwise attempt to parse its children'''
    if isinstance(item,str):
        try:
            item=eval(item)
        except Exception:
            #parse failed, this is already a python string
            return(item)
    #is it now a dict? if so, parse all of its entries
    if isinstance(item,dict):
        for key in item:
            item[key]=parseRecursively(item[key])
    #is it now a list? if so, parse all of its entries
    elif isinstance(item,list):
        for i in range(len(item)):
            item[i]=parseRecursively(item[i])
    else:
        #it's some other type of python object, like a number
        return item
    #now that its children are parsed, return it
    return item

def parseCatalog(f,shelf):
    '''parse entire jsonl catalog in file object f and save in shelf object shelf and return record names that were not strings'''
    i=0
    notStr=[]
    for line in f: 
        rec=parseRecursively(line)
        if not isinstance(rec['name'],str):
            print(rec['name'])
            notStr.append(rec['name'])
            rec['name']=str(rec['name'])
        shelf[rec['name']]=rec 
        i+=1        
        print(i)
    return(notStr)

class Catalog:
    '''Class representing a parsed/indexed data.gov catalog file'''
    def __init__(self,shelfpath):
        '''Create a new Catalog object representing the catalog stored in the shelf with base path shelfpath (which should be first created using parseCatalog)'''
        self.data=shelve.open(shelfpath)
        self.records=list(self.data.keys())
        self.shelfpath=shelfpath

    def searchByName(self,*contains,exclude=None):
        '''Search catalog for records whose names contain all the provided keywords in contains and none of the keywords in exclude (which should be a list) and return the names of matching entries'''
        test=lambda w:(lambda l:w in l) #test(w) will return a function which returns true if w is in its argument
        negTest=lambda w:(lambda l: not w in l)
        matchingEntries=self.records
        for word in contains:
            matchingEntries=filter(test(word),matchingEntries)
        if exclude:
            for word in exclude:
                matchingEntries=filter(negTest(word),matchingEntries)
        return list(matchingEntries)
    
    def fetchRecord(self,recName):
        '''Return the record with name recName'''
        return self.data[recName]

    def close(self):
        '''Close shelf'''
        self.data.close()

    def __del__(self):
        '''Make sure related shelf is closed when object is destroyed'''
        self.close()
