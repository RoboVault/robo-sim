# robo-sim

This is a working doc to test various scenarious and the impact of extreme price movements + various paramaters on strategy

model.py contains underlying logic for simulation including while simulation.iypnb can be used to simulate various scenarious such as
1) simulating AMM price movements for given randomly generated trades with varying degrees of volatility 
2) tracking performance of LP vs holding for extreme price movements
3) tracking vault performance using robovault strategy with given return paramaters
4) tracking fees for LP for given trades over period
5) tracking IL for given price movements 
6) varying paramaters for robovault strategy to measure return

to illustrate upside / risk of various strategies + mechanics of robo vault stragey some examples have been included in the jupyter notebook. 

Feel free to adjust anything and test various scenarious! 

Some future changes to include 
1) varying slippage on rebalancing based on AMM + showing it's impact
2) showing impact of varying rebalancing thresholds under different market conditions (i.e. narrow range outperform in one directional market while wider thresholds likely to perform better in mean reverting market)
3) add links to actual price data for various pairs from cctx 
