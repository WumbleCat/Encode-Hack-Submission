# Encode Hack Bounty 2 Submission: Bollinger Bands Trading Strategy with UniswapV3 Integration
## Overview

This project uses a Bollinger Bands-based trading strategy for a Uniswap V3 liquidity pool. The code includes a trading policy that leverages a combination of Simple Moving Average (SMA), Bollinger Bands, and rolling correlation with liquidity to make automated trading decisions in the UniswapV3 environment. The strategy is designed for use in a hackathon environment to showcase algorithmic the Dojo Library created by Compass Labs for DeFi trading.
Code Structure
Files

    run.py: This is the main script that contains the BollingerBandsPolicy class, which defines the trading policy and logic for trade execution.
    policy.py: Houses the base policy structure and is utilized by run.py to enforce the BollingerBandsPolicy.

Classes and Methods
1. BollingerBandsPolicy (in run.py)

This class implements a trading policy using Bollinger Bands, SMA, and correlation analysis. Key parameters include:

    Window: The look-back period for calculating SMA and Bollinger Bands.
    Standard Deviation Multiplier: Controls the width of the upper and lower Bollinger Bands, which is the variance.
    Correlation Window: The look-back period for calculating rolling correlation between price and liquidity.
    Direction: Determines trade direction (0 for all, -1 for short only, and 1 for long only).

Key Method:

    predict(): Main function that generates trade signals. It checks the Bollinger Bands and correlation values to decide when to buy or sell.

2. UniswapV3Observation, BaseAction, and UniswapV3Trade

These are classes from the dojo library, which provide the simulation environment (UniswapV3Observation), action structure (BaseAction), and trade action (UniswapV3Trade) used for executing trades.
Trading Logic

The strategy generates signals based on Bollinger Bands and correlation:

    Buy Signal: If the price crosses below the lower band and correlation suggests an inverse relationship, the policy initiates a buy.
    Sell Signal: If the price crosses above the upper band and correlation suggests an inverse relationship, the policy initiates a sell.
    
    Remark: The trade quantities are proportional to 30% of the agent's asset holdings.

Dependencies

    numpy: For mathematical computations.
    decimal: For precision in trade quantities.
    collections.deque: For maintaining a rolling window of historical prices.

Usage

This code can be directly used with the Dojo environment for testing trading strategies in a simulated DeFi market. Ensure all necessary classes from dojo are available and initialized for the BollingerBandsPolicy to function.