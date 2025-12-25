"""
Repository pour la gestion des paliers de fidélité.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, List
from database.base_repository import BaseRepository
from models.loyalty_tier import LoyaltyTier


class LoyaltyTierRepository(BaseRepository[LoyaltyTier]):
    """
    Repository pour les opérations sur les paliers de fidélité.
    """
    
    def create(self, tier: LoyaltyTier) -> LoyaltyTier:
        """Crée un nouveau palier."""
        query = """
            INSERT INTO loyalty_tiers (name, min_points, discount_percentage, description, is_active)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            tier.name,
            tier.min_points,
            tier.discount_percentage,
            tier.description,
            1 if tier.is_active else 0
        )
        
        self.db.execute(query, params)
        tier.id = self.db.get_last_insert_id()
        return tier
    
    def get_by_id(self, tier_id: int) -> Optional[LoyaltyTier]:
        """Récupère un palier par son ID."""
        query = "SELECT * FROM loyalty_tiers WHERE id = ?"
        result = self.db.fetch_one(query, (tier_id,))
        
        if result is None:
            return None
        
        return LoyaltyTier.from_dict(result)
    
    def get_all(self) -> List[LoyaltyTier]:
        """Récupère tous les paliers actifs."""
        query = "SELECT * FROM loyalty_tiers WHERE is_active = 1 ORDER BY min_points"
        results = self.db.fetch_all(query)
        return [LoyaltyTier.from_dict(row) for row in results]
    
    def get_tier_for_points(self, points: int) -> Optional[LoyaltyTier]:
        """
        Détermine le palier correspondant à un nombre de points.
        
        Args:
            points: Nombre de points du client
            
        Returns:
            Optional[LoyaltyTier]: Palier correspondant
        """
        query = """
            SELECT * FROM loyalty_tiers 
            WHERE is_active = 1 AND min_points <= ?
            ORDER BY min_points DESC
            LIMIT 1
        """
        result = self.db.fetch_one(query, (points,))
        
        if result is None:
            return None
        
        return LoyaltyTier.from_dict(result)
    
    def update(self, tier: LoyaltyTier) -> bool:
        """Met à jour un palier."""
        query = """
            UPDATE loyalty_tiers SET
                name = ?, min_points = ?, discount_percentage = ?,
                description = ?, is_active = ?
            WHERE id = ?
        """
        params = (
            tier.name,
            tier.min_points,
            tier.discount_percentage,
            tier.description,
            1 if tier.is_active else 0,
            tier.id
        )
        
        cursor = self.db.execute(query, params)
        return cursor.rowcount > 0
    
    def delete(self, tier_id: int) -> bool:
        """Désactive un palier."""
        query = "UPDATE loyalty_tiers SET is_active = 0 WHERE id = ?"
        cursor = self.db.execute(query, (tier_id,))
        return cursor.rowcount > 0