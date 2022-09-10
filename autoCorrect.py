# By WERDXZ
# On 2022-09-08



def autoCorrect(doubleList:list,precision:int=2,accuracy:int=50)->list:
    """
    Takes a list of doubles and returns a list of doubles with the same length
    but with the values corrected to the nearest 0.5
    @param doubleList: list of doubles
    @param precision: number of decimal places to round to
    @param accuracy: number of decimal places to check for accuracy
    @return: list of doubles
    """
    deltaList=[]
    for i in range(len(doubleList)):
        deltaList.append(round(doubleList[i],precision)-doubleList[i])
    
    