"""
Module database - Couche d'accès aux données.
"""

from .database_manager import DatabaseManager
from .base_repository import BaseRepository
from .user_repository import UserRepository
from .medicament_repository import MedicamentRepository
from .client_repository import ClientRepository
from .loyalty_tier_repository import LoyaltyTierRepository
from .sale_repository import SaleRepository
from .stock_movement_repository import StockMovementRepository

__all__ = [
    'DatabaseManager',
    'BaseRepository',
    'UserRepository',
    'MedicamentRepository',
    'ClientRepository',
    'LoyaltyTierRepository',
    'SaleRepository',
    'StockMovementRepository'
]