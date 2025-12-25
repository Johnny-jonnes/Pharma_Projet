"""
Modèle StockMovement - Représente un mouvement de stock.

Auteur: Alsény Camara
Version: 1.0
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class StockMovement:
    """
    Entité représentant un mouvement de stock.
    
    Attributes:
        id: Identifiant unique
        medicament_id: ID du médicament concerné
        user_id: ID de l'utilisateur ayant effectué le mouvement
        movement_type: Type (entry, exit, adjustment)
        quantity: Quantité déplacée (positive ou négative)
        reference_id: ID de référence (ex: ID vente)
        reason: Motif du mouvement
        created_at: Date du mouvement
    """
    
    medicament_id: int
    user_id: int
    movement_type: str
    quantity: int
    id: Optional[int] = None
    reference_id: Optional[int] = None
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
    
    # Champs additionnels pour affichage
    medicament_name: Optional[str] = None
    user_name: Optional[str] = None
    
    def __post_init__(self):
        """Validation après initialisation."""
        if self.movement_type not in ('entry', 'exit', 'adjustment'):
            raise ValueError(f"Type de mouvement invalide: {self.movement_type}")
        
        if self.quantity == 0:
            raise ValueError("La quantité ne peut pas être nulle")
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'medicament_id': self.medicament_id,
            'user_id': self.user_id,
            'movement_type': self.movement_type,
            'quantity': self.quantity,
            'reference_id': self.reference_id,
            'reason': self.reason,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StockMovement':
        """Crée une instance depuis un dictionnaire."""
        return cls(
            id=data.get('id'),
            medicament_id=data['medicament_id'],
            user_id=data['user_id'],
            movement_type=data['movement_type'],
            quantity=int(data['quantity']),
            reference_id=data.get('reference_id'),
            reason=data.get('reason'),
            created_at=data.get('created_at'),
            medicament_name=data.get('medicament_name'),
            user_name=data.get('user_name')
        )
    
    def is_entry(self) -> bool:
        """Vérifie si c'est une entrée de stock."""
        return self.movement_type == 'entry'
    
    def is_exit(self) -> bool:
        """Vérifie si c'est une sortie de stock."""
        return self.movement_type == 'exit'
    
    def is_adjustment(self) -> bool:
        """Vérifie si c'est un ajustement."""
        return self.movement_type == 'adjustment'