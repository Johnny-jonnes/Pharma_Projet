"""
Service de gestion du programme de fidélité.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, Tuple, List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.client import Client
from models.loyalty_tier import LoyaltyTier
from database.client_repository import ClientRepository
from database.loyalty_tier_repository import LoyaltyTierRepository
from config import LOYALTY_CONFIG


class LoyaltyService:
    """
    Service gérant le programme de fidélité.
    
    Responsabilités:
    - Calcul des points
    - Gestion des paliers
    - Application des remises
    """
    
    def __init__(self):
        """Initialise le service."""
        self._client_repo = ClientRepository()
        self._tier_repo = LoyaltyTierRepository()
    
    def calculate_points_earned(self, amount: float) -> int:
        """
        Calcule les points gagnés pour un montant.
        
        Args:
            amount: Montant de l'achat
            
        Returns:
            int: Nombre de points gagnés
        """
        points_per_unit = LOYALTY_CONFIG.get("points_per_unit", 10)
        
        if amount <= 0 or points_per_unit <= 0:
            return 0
        
        return int(amount // points_per_unit)
    
    def calculate_points_value(self, points: int) -> float:
        """
        Calcule la valeur monétaire des points.
        
        Args:
            points: Nombre de points
            
        Returns:
            float: Valeur en devise
        """
        point_value = LOYALTY_CONFIG.get("points_value", 0.1)
        return points * point_value
    
    def get_client_tier(self, client: Client) -> Optional[LoyaltyTier]:
        """
        Détermine le palier d'un client.
        
        Args:
            client: Client
            
        Returns:
            Optional[LoyaltyTier]: Palier du client
        """
        if client is None:
            return None
        
        return self._tier_repo.get_tier_for_points(client.loyalty_points)
    
    def get_client_discount(self, client: Client) -> float:
        """
        Retourne le pourcentage de remise du client.
        
        Args:
            client: Client
            
        Returns:
            float: Pourcentage de remise
        """
        tier = self.get_client_tier(client)
        
        if tier is None:
            return 0.0
        
        return tier.discount_percentage
    
    def apply_discount(
        self,
        amount: float,
        client: Client
    ) -> Tuple[float, float, float]:
        """
        Applique la remise fidélité à un montant.
        
        Args:
            amount: Montant avant remise
            client: Client
            
        Returns:
            Tuple[float, float, float]: 
                (montant_final, pourcentage_remise, montant_remise)
        """
        if client is None or amount <= 0:
            return amount, 0.0, 0.0
        
        discount_percentage = self.get_client_discount(client)
        
        if discount_percentage <= 0:
            return amount, 0.0, 0.0
        
        discount_amount = amount * (discount_percentage / 100)
        final_amount = amount - discount_amount
        
        return round(final_amount, 2), discount_percentage, round(discount_amount, 2)
    
    def add_points_to_client(
        self,
        client_id: int,
        amount: float
    ) -> Tuple[bool, int, str]:
        """
        Ajoute des points à un client après un achat.
        
        Args:
            client_id: ID du client
            amount: Montant de l'achat
            
        Returns:
            Tuple[bool, int, str]: (succès, points_ajoutés, message)
        """
        client = self._client_repo.get_by_id(client_id)
        if client is None:
            return False, 0, "Client non trouvé"
        
        points = self.calculate_points_earned(amount)
        
        if points > 0:
            success = self._client_repo.update_loyalty_points(client_id, points)
            if success:
                new_total = client.loyalty_points + points
                return True, points, f"+{points} points (Total: {new_total})"
            else:
                return False, 0, "Erreur lors de l'ajout des points"
        
        return True, 0, "Aucun point gagné"
    
    def use_client_points(
        self,
        client_id: int,
        points: int
    ) -> Tuple[bool, str]:
        """
        Utilise des points d'un client.
        
        Args:
            client_id: ID du client
            points: Points à utiliser
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        if points <= 0:
            return False, "Le nombre de points doit être positif"
        
        client = self._client_repo.get_by_id(client_id)
        if client is None:
            return False, "Client non trouvé"
        
        if client.loyalty_points < points:
            return False, f"Points insuffisants. Disponible: {client.loyalty_points}"
        
        success = self._client_repo.update_loyalty_points(client_id, -points)
        
        if success:
            return True, f"{points} points utilisés"
        else:
            return False, "Erreur lors de l'utilisation des points"
    
    def get_all_tiers(self) -> List[LoyaltyTier]:
        """Retourne tous les paliers."""
        return self._tier_repo.get_all()
    
    def get_next_tier(self, client: Client) -> Tuple[Optional[LoyaltyTier], int]:
        """
        Retourne le prochain palier et les points manquants.
        
        Args:
            client: Client
            
        Returns:
            Tuple[Optional[LoyaltyTier], int]: 
                (prochain_palier, points_manquants)
        """
        if client is None:
            return None, 0
        
        tiers = self.get_all_tiers()
        current_points = client.loyalty_points
        
        for tier in tiers:
            if tier.min_points > current_points:
                points_needed = tier.min_points - current_points
                return tier, points_needed
        
        # Client au palier maximum
        return None, 0
    
    def get_client_loyalty_info(self, client_id: int) -> dict:
        """
        Retourne les informations de fidélité d'un client.
        
        Args:
            client_id: ID du client
            
        Returns:
            dict: Informations de fidélité
        """
        client = self._client_repo.get_by_id(client_id)
        
        if client is None:
            return {}
        
        current_tier = self.get_client_tier(client)
        next_tier, points_needed = self.get_next_tier(client)
        
        return {
            'client_id': client.id,
            'client_name': client.get_full_name(),
            'current_points': client.loyalty_points,
            'points_value': self.calculate_points_value(client.loyalty_points),
            'current_tier': current_tier.name if current_tier else "Standard",
            'current_discount': current_tier.discount_percentage if current_tier else 0,
            'next_tier': next_tier.name if next_tier else None,
            'points_to_next': points_needed,
            'total_spent': client.total_spent
        }