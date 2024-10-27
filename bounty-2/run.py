import logging
import os
import sys
from datetime import timedelta
from decimal import Decimal
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from typing import Any, Optional
from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from dateutil import parser as dateparser
from policies.passiveLP import PassiveConcentratedLP
from policy import BollingerBandsPolicy  # Import the new BollingerBandsPolicy

from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run

def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    run_length: timedelta = timedelta(minutes=10),
    **kwargs: dict[str, Any],
) -> None:
    pools = ["USDC/WETH-0.05"]
    start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
    end_time = start_time + run_length

    bb_agent = UniswapV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)},
        name="BB_Agent",
    )
    lp_agent = UniswapV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)},
        name="LP_Agent",
    )

    # simulation environment
    env = UniswapV3Env(
        chain=Chain.ETHEREUM,
        date_range=(start_time, end_time),
        agents=[ bb_agent, lp_agent],
        pools=pools,
        backend_type="forked",
        market_impact="replay",
    )

    bb_policy = BollingerBandsPolicy(
        agent=bb_agent, pool="USDC/WETH-0.05", window=20, std_dev_multiplier=1.5, corr_window=10, direction=1
    )

    passive_lp_policy = PassiveConcentratedLP(
        agent=lp_agent, lower_price_bound=0.95, upper_price_bound=1.05
    )

    # Run the backtest
    backtest_run(
        env=env,
        policies=[bb_policy, passive_lp_policy],
        dashboard_server_port=dashboard_server_port,
        output_file="trading_strategies.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="Multi-Strategy Backtest",
        simulation_description="Backtest for Moving Average, Bollinger Bands, and Passive LP strategies.",
    )

if __name__ == "__main__":
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        run_length=timedelta(hours=2),
    )
