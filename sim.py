#import model as model
# LP INFO
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
rebalanceAdj = .996 #when rebalancing losses from swapping 

# APY's
lendRate = .05
borrowRate = .03
farmRate = .45

#SIM INFO
stepsPerYear = 365*24 

annualRates = {'lend' : lendRate, 'borrow' : borrowRate, 'farm' : farmRate}
adjRates = {'lend' : ((1 + lendRate)**(1/stepsPerYear) - 1), 
            'borrow' : ((1 + borrowRate)**(1/stepsPerYear) - 1),
            'farm' : ((1 + farmRate)**(1/stepsPerYear) - 1)}

"""
lp = model.createLp(vaultToken, secondaryToken, vol1, vol2)
vault = model.createVault(vaultToken, vaultTVL, lendAllocation)





print(model.getPrices())

vol1, vol2 = model.makeTrade(-1*vol1/10)

print(model.getPrices())

print(model.getVaultValue())
model.adjVault()

#rebalanceDebt()
#calcDebtRatio()
"""