"""
API integration module for Trade Allocations.
"""

from .trade_client import TradeAllocationsClient
from .trade_mapper import TradeDataMapper

__all__ = ['TradeAllocationsClient', 'TradeDataMapper']
