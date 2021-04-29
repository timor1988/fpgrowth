import fpgrowth
import time

# '''simple data'''
# simDat = fpgrowth.loadSimpDat()
# initSet = fpgrowth.createInitSet(simDat)
# myFPtree, myHeaderTab = fpgrowth.createFPtree(initSet, 3)
# myFPtree.disp()

# print fpgrowth.findPrefixPath('z', myHeaderTab)
# print fpgrowth.findPrefixPath('r', myHeaderTab)
# print fpgrowth.findPrefixPath('t', myHeaderTab)

# freqItems = []
# fpgrowth.mineFPtree(myFPtree, myHeaderTab, 3, set([]), freqItems)
# for x in freqItems:
#     print (x)

'''kosarak data'''
start = time.time()
n = 20000
with open("./data/kosarak.dat", "rb") as f:
    parsedDat = [line.split() for line in f.readlines()]
print(len(parsedDat))
initSet = fpgrowth.createInitSet(parsedDat) # {[原始数据，它的每一条记录是某个用户浏览过的新闻报道]:10,...}
myFPtree, myHeaderTab = fpgrowth.createFPtree(initSet, n)
freqItems = []
fpgrowth.mineFPtree(myFPtree, myHeaderTab, n, set([]), freqItems)
for x in freqItems:
    print (x)
print (time.time()-start, 'sec')

# compute support values of freqItems
suppData = fpgrowth.calSuppData(myHeaderTab, freqItems, len(parsedDat))
suppData[frozenset([])] = 1.0
for x,v in suppData.items():
    print (x,v)

freqItems = [frozenset(x) for x in freqItems]
fpgrowth.generateRules(freqItems, suppData)