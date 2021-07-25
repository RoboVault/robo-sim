import numpy

def createLp(token1, token2, vol1, vol2) : 
    amm = {token1 : vol1, token2 : vol2}
    return amm

def getPrices(token1, token2, vol1, vol2) : 
    prices = {token1 : vol2/vol1, token2 : vol1/vol2}
    return prices
    

def makeTrade(amount, vol1, vol2, fees = 0.003) : 
    maxTrade = 0.3 #max amount of total volume that can be traded in single trade
    amount = max(min(maxTrade*vol1, amount), -1*maxTrade*vol1)
    k = vol1 * vol2 
    vol1_new = vol1 + amount 
    vol2_new = k / (vol1 + amount)
    
    if amount > 0 : 
        fee = amount*fees
        vol1_new += fee
    else :
        fee = (vol2_new - vol2)*fees 
        vol2_new += fee
    
    
    return vol1_new, vol2_new

        
    
def createVault(amount, lendAllocation, vaultToken, secondaryToken, vol1, vol2) : 
    collateral = lendAllocation * amount
    borrowAllocation = 1 - lendAllocation 
    prices = getPrices(vaultToken, secondaryToken, vol1, vol2)
    amountBorrowed = borrowAllocation*amount*prices[vaultToken]
    lpHolding = amountBorrowed / vol2
    return {'collateral' : collateral, 'debtAmount' : amountBorrowed, 'lpHolding' : lpHolding, 'pendingHarvest' : 0}
    

def getVaultValue(vault, vaultToken, secondaryToken, vol1, vol2) : 
    prices = getPrices(vaultToken, secondaryToken, vol1, vol2)
    balance = vault['collateral']  - vault['debtAmount'] / prices[vaultToken] + vault['lpHolding']*vol1*2 + vault['pendingHarvest']
    return balance


def adjVault(vault, adjRates, vol1): 
    vault['collateral'] += vault['collateral']*adjRates['lend']
    vault['debtAmount'] += vault['debtAmount']*adjRates['borrow']
    vault['pendingHarvest'] += (vault['lpHolding']*vol1*2)*adjRates['farm']
    
    
def calcDebtRatio(vault, vaultToken, secondaryToken, vol1, vol2) : 
    debtRatio = vault['debtAmount'] / (vault['lpHolding']*vol2) 
    return debtRatio

def calcCollatRatio(vault, vaultToken, secondaryToken, vol1, vol2) : 
    prices = getPrices(vaultToken, secondaryToken, vol1, vol2)
    collatRatio = (vault['debtAmount'] / prices[vaultToken]) / vault['collateral']
    return collatRatio


def rebalanceDebt(vault, vaultToken, secondaryToken, vol1, vol2, debtLow, debtHigh, rebalanceAdj = .996) : 
    debtRatio = calcDebtRatio(vault, vaultToken, secondaryToken, vol1, vol2)
    if debtRatio > debtHigh : 
        #too much debt ~ remove some LP
        lpRemoveAmt = (vault['debtAmount'] - vault['lpHolding']*vol2) #how much of secondary asset will be removed from LP
        lpAdj = (vault['debtAmount'] - vault['lpHolding']*vol2) / (vol2) #how much will LP holdings decrease by 
        vault['lpHolding'] -= lpAdj
        vault['debtAmount'] -= lpRemoveAmt * ( 1 + rebalanceAdj) 
        
    if debtRatio < debtLow : 
        borrowAmt = 2*(vault['lpHolding']*vol2 - vault['debtAmount'])
        vault['debtAmount'] += borrowAmt
        lpAdj = (0.5 * borrowAmt / vol2)   * ( 1 + rebalanceAdj ) /  2
        vault['lpHolding'] += lpAdj
      
        
def rebalanceCollat(vault, vaultToken, secondaryToken, vol1, vol2, collatLow, collatTarget ,collatHigh) : 
    collatRatio = calcCollatRatio(vault, vaultToken, secondaryToken, vol1, vol2) 
    prices = getPrices(vaultToken, secondaryToken, vol1, vol2)
    if collatRatio < collatLow :
        adjAmt = (( vault['debtAmount']/prices[vaultToken]) - vault['collateral']*collatTarget) /  ( 1 + collatTarget)
        borrowAmt = adjAmt * prices[vaultToken]
        vault['debtAmount'] += borrowAmt
        vault['collateral'] -= adjAmt
        lpAdj = adjAmt / vol1 
        vault['lpHolding'] += lpAdj
        
        
    if collatRatio > collatLow : 
        adjAmt = (( vault['debtAmount']/prices[vaultToken]) - vault['collateral']*collatTarget) /  ( 1 + collatTarget)
        repayAmt = adjAmt * prices[vaultToken]
        vault['debtAmount'] -= repayAmt
        vault['collateral'] += adjAmt
        lpAdj = adjAmt / vol1 
        vault['lpHolding'] -= lpAdj
        
def harvest(vault, debtRatio, prices, vaultToken, harvestThreshold = 1, slippageAdj = .996) : 
    if debtRatio < harvestThreshold : 
        vault['collateral'] += vault['pendingHarvest']*(slippageAdj**2) #assume trade takes path through two LP's 
    else : 
        vault['debtAmount'] -= vault['pendingHarvest'] * prices[vaultToken] *(slippageAdj**2)
        
    vault['pendingHarvest'] = 0
    
    
    
       
def simulate(allTrades, vaultInitial, lp, vaultToken, secondaryToken, vol1, vol2, adjRates, 
             collatLow = .5, collatTarget = .55, collatHigh = .6, 
             debtLow = .97, debtHigh = 1.03, rebalance = True, harvestFrequency = 5, ammFee = 0.003) : 
    
    vault = vaultInitial
    priceLog = []
    vaultLog = []
    debtRatioLog = []
    collatRatioLog = []
    
    
    prices = getPrices(vaultToken, secondaryToken, vol1, vol2)
    debtRatio = calcDebtRatio(vault, vaultToken, secondaryToken, vol1, vol2)
    collatRatio = calcCollatRatio(vault, vaultToken, secondaryToken, vol1, vol2)   
    vaultValue = getVaultValue(vault, vaultToken, secondaryToken, vol1, vol2)
    vaultLog.append(vaultValue)
    p0 = prices[secondaryToken]
    priceLog.append(1.)
    
    


    
    debtRatioLog.append(debtRatio)
    collatRatioLog.append(collatRatio)
    
    harvestCount = 0
    
    nSteps = len(allTrades)
    for i in range(nSteps) : 

        
        trades = allTrades[i]
        for amt in trades : vol1, vol2 = makeTrade(amt,vol1, vol2)
        
        adjVault(vault, adjRates, vol1)
        if rebalance == True : 
            rebalanceDebt(vault, vaultToken, secondaryToken, vol1, vol2, debtLow, debtHigh)
            rebalanceCollat(vault, vaultToken, secondaryToken, vol1, vol2, collatLow, collatTarget ,collatHigh)
        
        
        prices = getPrices(vaultToken, secondaryToken, vol1, vol2)
        debtRatio = calcDebtRatio(vault, vaultToken, secondaryToken, vol1, vol2)
        collatRatio = calcCollatRatio(vault, vaultToken, secondaryToken, vol1, vol2) 
        harvestCount += 1
        if harvestCount == harvestFrequency : 
            harvestCount = 0 
            harvest(vault, debtRatio, prices, vaultToken)
        
        vaultValue = getVaultValue(vault, vaultToken, secondaryToken, vol1, vol2)
        vaultLog.append(vaultValue)
        priceLog.append(prices[secondaryToken] / p0)

    
        
        debtRatioLog.append(debtRatio)
        collatRatioLog.append(collatRatio)
        
    return vaultLog, priceLog, debtRatioLog, collatRatioLog
        
 

#vault = createVault(vaultTVL, lendAllocation, vaultToken, secondaryToken, vol1, vol2)



    

def genTradesRandom(lambdaTrades, expScale, pBuy) : 
    nTrades = numpy.random.poisson(lambdaTrades)
    tradeSize = numpy.random.exponential(expScale, nTrades)
    rand = numpy.random.uniform(size = nTrades)
    trades = []
    for i in range(nTrades) : 
        amt = tradeSize[i]
        if rand[i] < pBuy : 
            amt = -1*amt
        trades.append(amt)
    return trades


