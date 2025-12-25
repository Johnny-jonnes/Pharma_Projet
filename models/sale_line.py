"""
Modèle SaleLine - Représente une ligne de vente.

Auteur: Alsény Camara
Version: 1.0
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SaleLine:
    """
    Entité représentant une ligne de détail d'une vente.
    
    Attributes:
        id: Identifiant unique
        sale_id: ID de la vente parente
        medicament_id: ID du médicament
        quantity: Quantité vendue
        unit_price: Prix unitaire au moment de la vente
        line_total: Total de la ligne
        created_at: Date de création
        medicament_name: Nom du médicament (pour affichage)
        medicament_code: Code du médicament (pour affichage)
    """
    
    sale_id: int
    medicament_id: int
    quantity: int
    unit_price: float
    line_total: float
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    # Champs additionnels pour affichage (non stockés)
    medicament_name: Optional[str] = None
    medicament_code: Optional[str] = None
    
    def __post_init__(self):
        """Validation après initialisation."""
        if self.quantity <= 0:
            raise ValueError("La quantité doit être supérieure à zéro")
        
        if self.unit_price < 0:
            raise ValueError("Le prix unitaire ne peut pas être négatif")
        
        if self.line_total < 0:
            raise ValueError("Le total ligne ne peut pas être négatif")
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'medicament_id': self.medicament_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'line_total': self.line_total,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SaleLine':
        """Crée une instance depuis un dictionnaire."""
        return cls(
            id=data.get('id'),
            sale_id=data['sale_id'],
            medicament_id=data['medicament_id'],
            quantity=int(data['quantity']),
            unit_price=float(data['unit_price']),
            line_total=float(data['line_total']),
            created_at=data.get('created_at'),
            medicament_name=data.get('medicament_name'),
            medicament_code=data.get('medicament_code')
        )
    
    def calculate_total(self) -> float:
        """Recalcule le total de la ligne."""
        return self.quantity * self.unit_price