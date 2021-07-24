


def createLp(token1, token2, vol1, vol2) : 
    amm = {token1 : vol1, token2 : vol2}
    return amm

def getPrices() : 
    prices = {vaultToken : vol2/vol1, secondaryToken : vol1/vol2}
    return prices
    

def makeTrade(amount) : 
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

        
    
def createVault(vaultToken, amount, lendAllocation) : 
    collateral = lendAllocation * amount
    borrowAllocation = 1 - lendAllocation 
    prices = getPrices()
    amountBorrowed = borrowAllocation*amount*prices[vaultToken]
    lpHolding = amountBorrowed / vol2
    return {'collateral' : collateral, 'debtAmount' : amountBorrowed, 'lpHolding' : lpHolding, 'pendingHarvest' : 0}
    

def getVaultValue() : 
    prices = getPrices()
    balance = vault['collateral']  - vault['debtAmount'] / prices[vaultToken] + vault['lpHolding']*vol1*2
    return balance


def adjVault(): 
    vault['collateral'] += vault['collateral']*adjRates['lend']
    vault['debtAmount'] += vault['debtAmount']*adjRates['borrow']
    vault['pendingHarvest'] += (vault['lpHolding']*vol1*2)*adjRates['farm']
    
    
def calcDebtRatio() : 
    debtRatio = vault['debtAmount'] / (vault['lpHolding']*vol2) 
    return debtRatio

def calcCollatRatio() : 
    prices = getPrices()
    collatRatio = (vault['debtAmount'] / prices[vaultToken]) / vault['collateral']
    return collatRatio


def rebalanceDebt() : 
    debtRatio = calcDebtRatio()
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
      
        
def rebalanceCollat() : 
    collatRatio = calcCollatRatio()
    prices = getPrices()
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

def harvestTreshold        
        
        
def simulate(allTrades, vault, lp, vaultToken) : 
    
    nSteps = len(allTrades)
    for i in range(nSteps) : 
        trades = allTrades[i]
        for amt in trades : vol1, vol2 = makeTrade(amt)
        adjVault()
        rebalanceDebt()
        rebalanceCollat()
 
vaultToken = 'USDC'
secondaryToken = 'FTM'
vol1 =  10000
vol2 =  50000
fees = .003 # fee added to AMM on each exchange

# VAULT INFO
vaultTVL = 1000
lendAllocation = .65
debtLow = .97
debtHigh = 1.03
collatLow = .3
collatTarget = .35
collatHigh = .4
harvestTreshold = 1
rebalanceAdj = .996 #when rebalancing losses from swapping 

# APY's
lendRate = .05
borrowRate = .03
farmRate = .45

#SIM INFO
stepsPerYear = 365

annualRates = {'lend' : lendRate, 'borrow' : borrowRate, 'farm' : farmRate}
adjRates = {'lend' : ((1 + lendRate)**(1/stepsPerYear) - 1), 
            'borrow' : ((1 + borrowRate)**(1/stepsPerYear) - 1),
            'farm' : ((1 + farmRate)**(1/stepsPerYear) - 1)}

lp = createLp(vaultToken, secondaryToken, vol1, vol2)
vault = createVault(vaultToken, vaultTVL, lendAllocation)
       
nSteps = 100

pBuy = .5
lambdaTrades = 5 # input for poisson distribution
expScale = 10 # input for exponential distribution to determine size of trade 

import numpy

def genTrades() : 
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
    
allTrades = []
        
for i in range(nSteps) : 
    tradeStep = genTrades()
    allTrades.append(tradeStep)
    
print(getVaultValue())
simulate(allTrades, vault, lp, vaultToken)
print(getVaultValue())


