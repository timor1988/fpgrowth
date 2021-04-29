# coding:utf-8


class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        """
        树结点定义如下，name存放结点名字，count用于计数，nodeLink用于连接相似结点（即图中箭头），
        parent用于存放父节点，用于回溯，children存放儿子结点（即图中实线）。disp仅用于输出调试。
        :param nameValue:
        :param numOccur:
        :param parentNode:
        """
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None # nodeLink用于连接相似结点（即图中箭头）
        self.parent = parentNode
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

    def disp(self, ind=1):
        print('  ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)


def updateHeader(nodeToTest, targetNode):
    while nodeToTest.nodeLink != None:
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode


def updateFPtree(items, inTree, headerTable, count):
    """
    更新FPtree
    因此每次只需判断第一个结点是否是根的儿子，若是则增加计数，
    若不是则增加分枝，然后递归调用构造FP树，传入第二个元素开始的子树即可。
    :param items: list. 排序后的项集
    :param inTree: 初始化的树 treeNode('Null Set', 1, None)
    :param headerTable: dict. 项集:[count, node]
    :param count: int. 该条数据出现的次数。用于确定每次更新树时候项集后面的数字。
    :return:
    """

    if items[0] in inTree.children: # 首先检查是否存在该节点
        # 判断items的第一个结点是否已作为子结点
        inTree.children[items[0]].inc(count) # 存在则计数增加
    else: # 不存在则创建新的分支
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        if headerTable[items[0]][1] == None: #若原来不存在该类别，更新头指针列表
            headerTable[items[0]][1] = inTree.children[items[0]] # 更新指向
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    # 递归
    if len(items) > 1:
        updateFPtree(items[1::], inTree.children[items[0]], headerTable, count)

    """
    第一条记录 ACEBF,都执行else创建新的分支。然后都执行第一个if。 headerTable[A] = [1,节点A]
    第二条记录ACG。A执行计数增加。
    第三条记录，新建一个E分支。 此时headerTable[E] = [1,C后面的E节点]。把当前项头表指向的E节点和新的E节点
    传入updateHeader方法。此时 oldE.nodeLink==None,所以oldE.nodelink = newE。即图中E:1 ————> E:1的箭头。   
    """


def createFPtree(dataSet, minSup=1):
    """
    {[原始数据，它的每一条记录是某个用户浏览过的新闻报道]:10,...}
    :param dataSet:
    :param minSup:
    :return:
    """
    headerTable = {}
    for trans in dataSet:   # 第一次遍历：统计各个数据的频繁度 frozenset({b'2226', b'7', b'32', b'27', b'28'}): 1
        for item in trans:
            # print(item)
            # 用头指针表统计各个类别的出现的次数，计算频繁量：头指针表[类别]=出现次数。
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
    for k in list(headerTable):
        if headerTable[k] < minSup:
            del (headerTable[k])  # 删除不满足最小支持度的元素
    freqItemSet = set(headerTable.keys())  # 满足最小支持度的频繁项集
    if len(freqItemSet) == 0:
        return None, None
    for k in headerTable:
        headerTable[k] = [headerTable[k], None]  # element: [count, node] 保存计数值及指向每种类型第一个元素项的指针

    retTree = treeNode('Null Set', 1, None) # 初始化tree
    for tranSet, count in dataSet.items():  #第二次遍历：对于每条数据剔除非频繁1项集，并按照支持度降序排列
        # dataSet：[elements, count]
        localD = {}
        for item in tranSet:
            if item in freqItemSet:  # 过滤，只取该样本中满足最小支持度的频繁项
                localD[item] = headerTable[item][0]  # element : count
        if len(localD) > 0:
            # 根据全局频数从大到小对单样本排序
            #使得两元素在频次相同时按照字母顺序排序。即建立了最终的项头表
            orderedItem = [v[0] for v in sorted(localD.items(), key=lambda p: (p[1], int(p[0])), reverse=True)]
            # 用过滤且排序后的样本更新树
            updateFPtree(orderedItem, retTree, headerTable, count)
    return retTree, headerTable


# 回溯
def ascendFPtree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendFPtree(leafNode.parent, prefixPath)


# 条件模式基
def findPrefixPath(basePat, myHeaderTab):
    treeNode = myHeaderTab[basePat][1]  # basePat在FP树中的第一个结点
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendFPtree(treeNode, prefixPath)  # prefixPath是倒过来的，从treeNode开始到根
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count  # 关联treeNode的计数
        treeNode = treeNode.nodeLink  # 下一个basePat结点
    return condPats


def mineFPtree(inTree, headerTable, minSup, preFix, freqItemList):
    # 最开始的频繁项集是headerTable中的各元素
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1])]  # 根据频繁项的总频次排序
    for basePat in bigL:  # 对每个频繁项
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        freqItemList.append(newFreqSet)
        condPattBases = findPrefixPath(basePat, headerTable)  # 当前频繁项集的条件模式基
        myCondTree, myHead = createFPtree(condPattBases, minSup)  # 构造当前频繁项的条件FP树
        if myHead != None:
            # print 'conditional tree for: ', newFreqSet
            # myCondTree.disp(1)
            mineFPtree(myCondTree, myHead, minSup, newFreqSet, freqItemList)  # 递归挖掘条件FP树


def loadSimpDat():
    simDat = [['r', 'z', 'h', 'j', 'p'],
              ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'],
              ['z'],
              ['r', 'x', 'n', 'o', 's'],
              ['y', 'r', 'x', 'z', 'q', 't', 'p'],
              ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]
    return simDat


def createInitSet(dataSet):
    """

    :param dataSet: list. 长度=990002
    :return:
    """
    retDict = {}
    for trans in dataSet:
        key = frozenset(trans) # frozenset之后的对象可以用做字典的key
        if key in retDict.keys():
            retDict[frozenset(trans)] += 1
        else:
            retDict[frozenset(trans)] = 1
    return retDict


def calSuppData(headerTable, freqItemList, total):
    suppData = {}
    for Item in freqItemList:
        # 找到最底下的结点
        Item = sorted(Item, key=lambda x: headerTable[x][0])
        base = findPrefixPath(Item[0], headerTable)
        # 计算支持度
        support = 0
        for B in base:
            if frozenset(Item[1:]).issubset(set(B)):
                support += base[B]
        # 对于根的儿子，没有条件模式基
        if len(base) == 0 and len(Item) == 1:
            support = headerTable[Item[0]][0]

        suppData[frozenset(Item)] = support / float(total)
    return suppData


def aprioriGen(Lk, k):
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i + 1, lenLk):
            L1 = list(Lk[i])[:k - 2];
            L2 = list(Lk[j])[:k - 2]
            L1.sort();
            L2.sort()
            if L1 == L2:
                retList.append(Lk[i] | Lk[j])
    return retList


def calcConf(freqSet, H, supportData, br1, minConf=0.7):
    prunedH = []
    for conseq in H:
        conf = supportData[freqSet] / supportData[freqSet - conseq]
        if conf >= minConf:
            print("{0} --> {1} conf:{2}".format(freqSet - conseq, conseq, conf))
            br1.append((freqSet - conseq, conseq, conf))
            prunedH.append(conseq)
    return prunedH


def rulesFromConseq(freqSet, H, supportData, br1, minConf=0.7):
    m = len(H[0])
    if len(freqSet) > m + 1:
        Hmp1 = aprioriGen(H, m + 1)
        Hmp1 = calcConf(freqSet, Hmp1, supportData, br1, minConf)
        if len(Hmp1) > 1:
            rulesFromConseq(freqSet, Hmp1, supportData, br1, minConf)


def generateRules(freqItemList, supportData, minConf=0.7):
    bigRuleList = []
    for freqSet in freqItemList:
        H1 = [frozenset([item]) for item in freqSet]
        if len(freqSet) > 1:
            rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
        else:
            calcConf(freqSet, H1, supportData, bigRuleList, minConf)
    return bigRuleList
