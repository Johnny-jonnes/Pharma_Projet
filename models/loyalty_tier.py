"""
Modèle LoyaltyTier - Représente un palier de fidélité.

Auteur: Alsény Camara
Version: 1.0
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LoyaltyTier:
    """
    Entité représentant un palier du programme de fidélité.
    
    Attributes:
        id: Identifiant unique
        name: Nom du palier
        min_points: Points minimum requis
        discount_percentage: Pourcentage de remise
        description: Description des avantages
        is_active: Statut actif
        created_at: Date de création
    """
    
    name: str
    min_points: int
    discount_percentage: float
    id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validation après initialisation."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Le nom du palier est obligatoire")
        
        if self.min_points < 0:
            raise ValueError("Les points minimum ne peuvent pas être négatifs")
        
        if self.discount_percentage < 0 or self.discount_percentage > 100:
            raise ValueError("Le pourcentage de remise doit être entre 0 et 100")
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'name': self.name,
            'min_points': self.min_points,
            'discount_percentage': self.discount_percentage,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LoyaltyTier':
        """Crée une instance depuis un dictionnaire."""
        return cls(
            id=data.get('id'),
            name=data['name'],
            min_points=int(data['min_points']),
            discount_percentage=float(data['discount_percentage']),
            description=data.get('description'),
            is_active=bool(data.get('is_active', True)),
            created_at=data.get('created_at')
        )