from collections import deque
from decimal import Decimal
from typing import Any, List

import numpy as np

from dojo.actions.base_action import BaseAction
from dojo.actions.uniswapV3 import UniswapV3Trade
from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniswapV3Observation
from dojo.policies import BasePolicy

class BollingerBandsPolicy(BasePolicy):
    """Bollinger Bands trading strategy using SMA and correlation for a UniswapV3Env with a single pool.

    :param agent: The agent which is using this policy.
    :param pool: The liquidity pool for trading.
    :param window: The window size for calculating the SMA and Bollinger Bands.
    :param std_dev_multiplier: The multiplier for the standard deviation to set band widths.
    :param corr_window: The window size for calculating rolling correlation.
    :param direction: The trade direction; 0 for all, -1 for short only, 1 for long only.
    """

    def __init__(
        self, agent: BaseAgent, pool: str, window: int = 20, std_dev_multiplier: float = 2.0, corr_window: int = 20, direction: int = 0
    ) -> None:
        super().__init__(agent=agent)
        self.pool = pool
        self.window = window
        self.std_dev_multiplier = std_dev_multiplier
        self.corr_window = corr_window  # Window for calculating rolling correlation
        self.direction = direction  # 0 for both, -1 for short only, 1 for long only
        self.price_window: deque[float] = deque(maxlen=window)
        self.price_hist = []
        self.liquidity = []
        self.upper_band = []
        self.lower_band = []
        self.correlation_hist = []

    def calculate_sma(self) -> float:
        """Calculate the Simple Moving Average (SMA) based on the price window."""
        return np.mean(self.price_window)

    def calculate_bollinger_bands(self) -> tuple[float, float, float]:
        """Calculate the Bollinger Bands based on the SMA."""
        if len(self.price_window) < self.window:
            return 0.0, 0.0, 0.0  # Not enough data yet

        middle_band = self.calculate_sma()  # Use SMA for the middle band
        std_dev = np.std(self.price_window)
        upper_band = middle_band + (std_dev * self.std_dev_multiplier)
        lower_band = middle_band - (std_dev * self.std_dev_multiplier)

        # Save bands for analysis or debugging
        self.upper_band.append(upper_band)
        self.lower_band.append(lower_band)
        
        return lower_band, middle_band, upper_band

    def calculate_correlation(self) -> float:
        """Calculate the rolling correlation between price and liquidity."""
        if len(self.price_hist) >= self.corr_window and len(self.liquidity) >= self.corr_window:
            # Extract the most recent `corr_window` values
            prices = np.array(self.price_hist[-self.corr_window:], dtype=float)
            liquidity = np.array(self.liquidity[-self.corr_window:], dtype=float)

            # Ensure arrays are of the same shape and dimension
            if prices.shape == liquidity.shape and prices.ndim == 1:
                corr = np.corrcoef(prices, liquidity)[0, 1]
                self.correlation_hist.append(corr)
                return corr
        return 0.0  # Default correlation when insufficient data


    def predict(self, obs: UniswapV3Observation) -> List[BaseAction[Any]]:
        """Generate trade signals based on Bollinger Bands with SMA and correlation."""
        pool = obs.pools[0]
        pool_tokens = obs.pool_tokens(pool=self.pool)
        
        # Fetch current price and liquidity, and update data history in every step
        price = float(obs.price(token=pool_tokens[0], unit=pool_tokens[1], pool=self.pool))
        self.price_window.append(price)
        self.price_hist.append(price)
        self.liquidity.append(obs.liquidity(pool))  # Ensure liquidity is added every step

        # Calculate Bollinger Bands and rolling correlation
        lower_band, middle_band, upper_band = self.calculate_bollinger_bands()
        correlation = self.calculate_correlation()
        obs.add_signal("Correlation", correlation)
        """Generate trade signals based on Bollinger Bands with SMA and correlation."""
        pool = obs.pools[0]
        pool_tokens = obs.pool_tokens(pool=self.pool)
        
        # Fetch current price and liquidity, and update data history
        price = float(obs.price(token=pool_tokens[0], unit=pool_tokens[1], pool=self.pool))
        self.price_window.append(price)
        self.price_hist.append(price)
        self.liquidity.append(obs.liquidity(pool))

        # Calculate Bollinger Bands and rolling correlation
        lower_band, middle_band, upper_band = self.calculate_bollinger_bands()
        correlation = self.calculate_correlation()
        obs.add_signal("Correlation", correlation)

        # Only start trading when enough data is available
        if len(self.price_window) < self.window:
            return []

        actions = []
        
        # Buy Signal: Price crosses below lower band, and correlation suggests an inverse relationship
        if self.direction >= 0 and price < lower_band and correlation < -0.5:  # Long trades or both
            y_quantity = self.agent.quantity(pool_tokens[1]) * Decimal("0.3")  # Trade 10% of asset y
            actions.append(
                UniswapV3Trade(
                    agent=self.agent,
                    pool=self.pool,
                    quantities=(Decimal(0), y_quantity),  # Buy action
                )
            )

        # Sell Signal: Price crosses above upper band, and correlation suggests an inverse relationship
        if self.direction <= 0 and price > upper_band and correlation < -0.5:  # Short trades or both
            x_quantity = self.agent.quantity(pool_tokens[0]) * Decimal("0.3")  # Trade 10% of asset x
            actions.append(
                UniswapV3Trade(
                    agent=self.agent,
                    pool=self.pool,
                    quantities=(x_quantity, Decimal(0)),  # Sell action
                )
            )

        return actions
