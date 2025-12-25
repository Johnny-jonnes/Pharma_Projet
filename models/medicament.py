"""
Modèle Medicament - Représente un médicament en stock.

Auteur: Alsény Camara
Version: 1.0
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import STOCK_CONFIG


@dataclass
class Medicament:
    """
    Entité représentant un médicament.
    
    Attributes:
        id: Identifiant unique
        code: Code barre / référence unique
        name: Nom du médicament
        description: Description détaillée
        category: Catégorie thérapeutique
        purchase_price: Prix d'achat HT
        selling_price: Prix de vente TTC
        quantity_in_stock: Quantité en stock
        stock_threshold: Seuil d'alerte stock faible
        expiration_date: Date de péremption
        manufacturer: Fabricant / Laboratoire
        is_active: Statut actif (suppression logique)
        created_at: Date de création
        updated_at: Date de modification
    """
    
    code: str
    name: str
    purchase_price: float
    selling_price: float
    id: Optional[int] = None
    description: Optional[str] = None
    category: Optional[str] = None
    quantity_in_stock: int = 0
    stock_threshold: int = STOCK_CONFIG["default_threshold"]
    expiration_date: Optional[date] = None
    manufacturer: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validation après initialisation."""
        if not self.code or len(self.code.strip()) == 0:
            raise ValueError("Le code du médicament est obligatoire")
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Le nom du médicament est obligatoire")
        
        if self.purchase_price < 0:
            raise ValueError("Le prix d'achat ne peut pas être négatif")
        
        if self.selling_price < 0:
            raise ValueError("Le prix de vente ne peut pas être négatif")
        
        if self.quantity_in_stock < 0:
            raise ValueError("La quantité en stock ne peut pas être négative")
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'purchase_price': self.purchase_price,
            'selling_price': self.selling_price,
            'quantity_in_stock': self.quantity_in_stock,
            'stock_threshold': self.stock_threshold,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'manufacturer': self.manufacturer,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Medicament':
        """Crée une instance depuis un dictionnaire."""
        exp_date = data.get('expiration_date')
        if exp_date and isinstance(exp_date, str):
            exp_date = date.fromisoformat(exp_date)
        
        return cls(
            id=data.get('id'),
            code=data['code'],
            name=data['name'],
            description=data.get('description'),
            category=data.get('category'),
            purchase_price=float(data['purchase_price']),
            selling_price=float(data['selling_price']),
            quantity_in_stock=int(data.get('quantity_in_stock', 0)),
            stock_threshold=int(data.get('stock_threshold', STOCK_CONFIG["default_threshold"])),
            expiration_date=exp_date,
            manufacturer=data.get('manufacturer'),
            is_active=bool(data.get('is_active', True)),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def is_low_stock(self) -> bool:
        """Vérifie si le stock est faible."""
        return self.quantity_in_stock <= self.stock_threshold
    
    def is_out_of_stock(self) -> bool:
        """Vérifie si le produit est en rupture."""
        return self.quantity_in_stock == 0
    
    def is_expiring_soon(self, days: int = STOCK_CONFIG["expiry_alert_days"]) -> bool:
        """
        Vérifie si le médicament expire bientôt.
        
        Args:
            days: Nombre de jours pour l'alerte
            
        Returns:
            bool: True si expire dans les X jours
        """
        if self.expiration_date is None:
            return False
        
        today = date.today()
        delta = (self.expiration_date - today).days
        return 0 <= delta <= days
    
    def is_expired(self) -> bool:
        """Vérifie si le médicament est périmé."""
        if self.expiration_date is None:
            return False
        return self.expiration_date < date.today()
    
    def days_until_expiry(self) -> Optional[int]:
        """Retourne le nombre de jours avant péremption."""
        if self.expiration_date is None:
            return None
        return (self.expiration_date - date.today()).days
    
    def get_margin(self) -> float:
        """Calcule la marge brute."""
        return self.selling_price - self.purchase_price
    
    def get_margin_percentage(self) -> float:
        """Calcule le pourcentage de marge."""
        if self.purchase_price == 0:
            return 0.0
        return (self.get_margin() / self.purchase_price) * 100