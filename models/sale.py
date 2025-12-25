"""
Modèle Sale - Représente une vente.

Auteur: Alsény Camara
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from models.sale_line import SaleLine


@dataclass
class Sale:
    """
    Entité représentant une vente.
    
    Attributes:
        id: Identifiant unique
        sale_number: Numéro de vente unique
        client_id: ID client (optionnel pour ventes anonymes)
        user_id: ID du vendeur
        sale_date: Date et heure de la vente
        subtotal: Sous-total avant remise
        discount_percentage: Pourcentage de remise appliqué
        discount_amount: Montant de la remise
        total: Total final
        loyalty_points_earned: Points gagnés
        loyalty_points_used: Points utilisés
        status: Statut (completed, cancelled)
        created_at: Date de création
        lines: Liste des lignes de vente
    """
    
    sale_number: str
    user_id: int
    sale_date: datetime
    subtotal: float
    total: float
    id: Optional[int] = None
    client_id: Optional[int] = None
    discount_percentage: float = 0.0
    discount_amount: float = 0.0
    loyalty_points_earned: int = 0
    loyalty_points_used: int = 0
    status: str = 'completed'
    created_at: Optional[datetime] = None
    lines: List['SaleLine'] = field(default_factory=list)
    
    # Champs additionnels pour affichage (non stockés)
    client_name: Optional[str] = None
    seller_name: Optional[str] = None
    
    def __post_init__(self):
        """Validation après initialisation."""
        if not self.sale_number or len(self.sale_number.strip()) == 0:
            raise ValueError("Le numéro de vente est obligatoire")
        
        if self.user_id is None or self.user_id <= 0:
            raise ValueError("L'ID du vendeur est obligatoire")
        
        if self.subtotal < 0:
            raise ValueError("Le sous-total ne peut pas être négatif")
        
        if self.total < 0:
            raise ValueError("Le total ne peut pas être négatif")
        
        if self.status not in ('completed', 'cancelled'):
            raise ValueError(f"Statut invalide: {self.status}")
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'sale_number': self.sale_number,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'subtotal': self.subtotal,
            'discount_percentage': self.discount_percentage,
            'discount_amount': self.discount_amount,
            'total': self.total,
            'loyalty_points_earned': self.loyalty_points_earned,
            'loyalty_points_used': self.loyalty_points_used,
            'status': self.status,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Sale':
        """Crée une instance depuis un dictionnaire."""
        sale_date = data.get('sale_date')
        if sale_date and isinstance(sale_date, str):
            sale_date = datetime.fromisoformat(sale_date)
        
        return cls(
            id=data.get('id'),
            sale_number=data['sale_number'],
            client_id=data.get('client_id'),
            user_id=data['user_id'],
            sale_date=sale_date or datetime.now(),
            subtotal=float(data.get('subtotal', 0)),
            discount_percentage=float(data.get('discount_percentage', 0)),
            discount_amount=float(data.get('discount_amount', 0)),
            total=float(data.get('total', 0)),
            loyalty_points_earned=int(data.get('loyalty_points_earned', 0)),
            loyalty_points_used=int(data.get('loyalty_points_used', 0)),
            status=data.get('status', 'completed'),
            created_at=data.get('created_at'),
            client_name=data.get('client_name'),
            seller_name=data.get('seller_name')
        )
    
    def is_completed(self) -> bool:
        """Vérifie si la vente est terminée."""
        return self.status == 'completed'
    
    def is_cancelled(self) -> bool:
        """Vérifie si la vente est annulée."""
        return self.status == 'cancelled'
    
    def add_line(self, line: 'SaleLine') -> None:
        """Ajoute une ligne à la vente."""
        self.lines.append(line)
    
    def get_items_count(self) -> int:
        """Retourne le nombre total d'articles."""
        return sum(line.quantity for line in self.lines)