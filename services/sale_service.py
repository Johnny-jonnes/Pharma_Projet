"""
Service de gestion des ventes.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.sale import Sale
from models.sale_line import SaleLine
from models.client import Client
from models.medicament import Medicament
from database.sale_repository import SaleRepository
from database.client_repository import ClientRepository
from database.medicament_repository import MedicamentRepository
from services.stock_service import StockService
from services.loyalty_service import LoyaltyService
from services.auth_service import AuthService
from utils.format_utils import FormatUtils
from config import LOYALTY_CONFIG


@dataclass
class CartItem:
    """Article du panier."""
    medicament: Medicament
    quantity: int
    unit_price: float
    
    @property
    def line_total(self) -> float:
        return FormatUtils.round_currency(self.quantity * self.unit_price)


@dataclass
class Cart:
    """Panier de vente."""
    items: List[CartItem] = field(default_factory=list)
    client: Optional[Client] = None
    
    @property
    def subtotal(self) -> float:
        return FormatUtils.round_currency(
            sum(item.line_total for item in self.items)
        )
    
    @property
    def items_count(self) -> int:
        return sum(item.quantity for item in self.items)
    
    def is_empty(self) -> bool:
        return len(self.items) == 0
    
    def clear(self) -> None:
        self.items = []
        self.client = None


class SaleService:
    """
    Service gérant les opérations de vente.
    
    Responsabilités:
    - Gestion du panier
    - Calcul des totaux et remises
    - Validation et enregistrement des ventes
    - Génération des tickets
    """
    
    def __init__(self):
        """Initialise le service."""
        self._sale_repo = SaleRepository()
        self._client_repo = ClientRepository()
        self._medicament_repo = MedicamentRepository()
        self._stock_service = StockService()
        self._loyalty_service = LoyaltyService()
        
        # Panier courant
        self._cart = Cart()
    
    @property
    def cart(self) -> Cart:
        """Retourne le panier courant."""
        return self._cart
    
    def new_cart(self) -> Cart:
        """Crée un nouveau panier."""
        self._cart = Cart()
        return self._cart
    
    def add_to_cart(
        self,
        medicament_id: int,
        quantity: int = 1
    ) -> Tuple[bool, str]:
        """
        Ajoute un article au panier.
        
        Args:
            medicament_id: ID du médicament
            quantity: Quantité à ajouter
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        if quantity <= 0:
            return False, "La quantité doit être positive"
        
        medicament = self._medicament_repo.get_by_id(medicament_id)
        if medicament is None:
            return False, "Médicament non trouvé"
        
        if not medicament.is_active:
            return False, "Ce médicament n'est plus disponible"
        
        # Vérifier le stock
        current_in_cart = 0
        existing_item = None
        
        for item in self._cart.items:
            if item.medicament.id == medicament_id:
                current_in_cart = item.quantity
                existing_item = item
                break
        
        total_needed = current_in_cart + quantity
        
        if medicament.quantity_in_stock < total_needed:
            available = medicament.quantity_in_stock - current_in_cart
            return False, f"Stock insuffisant. Disponible: {max(0, available)}"
        
        # Ajouter ou mettre à jour
        if existing_item:
            existing_item.quantity += quantity
        else:
            self._cart.items.append(CartItem(
                medicament=medicament,
                quantity=quantity,
                unit_price=medicament.selling_price
            ))
        
        return True, f"{medicament.name} ajouté au panier"
    
    def remove_from_cart(self, medicament_id: int) -> Tuple[bool, str]:
        """
        Retire un article du panier.
        
        Args:
            medicament_id: ID du médicament
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        for i, item in enumerate(self._cart.items):
            if item.medicament.id == medicament_id:
                removed = self._cart.items.pop(i)
                return True, f"{removed.medicament.name} retiré du panier"
        
        return False, "Article non trouvé dans le panier"
    
    def update_cart_quantity(
        self,
        medicament_id: int,
        quantity: int
    ) -> Tuple[bool, str]:
        """
        Met à jour la quantité d'un article.
        
        Args:
            medicament_id: ID du médicament
            quantity: Nouvelle quantité
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        if quantity <= 0:
            return self.remove_from_cart(medicament_id)
        
        for item in self._cart.items:
            if item.medicament.id == medicament_id:
                # Vérifier le stock
                if item.medicament.quantity_in_stock < quantity:
                    return False, f"Stock insuffisant. Disponible: {item.medicament.quantity_in_stock}"
                
                item.quantity = quantity
                return True, "Quantité mise à jour"
        
        return False, "Article non trouvé dans le panier"
    
    def set_client(self, client_id: int) -> Tuple[bool, str]:
        """
        Associe un client au panier.
        
        Args:
            client_id: ID du client
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        client = self._client_repo.get_by_id(client_id)
        
        if client is None:
            return False, "Client non trouvé"
        
        if not client.is_active:
            return False, "Ce client est désactivé"
        
        self._cart.client = client
        return True, f"Client {client.get_full_name()} associé"
    
    def remove_client(self) -> None:
        """Retire le client du panier."""
        self._cart.client = None
    
    def calculate_totals(self) -> Dict[str, Any]:
        """
        Calcule les totaux de la vente.
        
        Returns:
            dict: Totaux et informations de calcul
        """
        subtotal = self._cart.subtotal
        discount_percentage = 0.0
        discount_amount = 0.0
        points_earned = 0
        
        # Appliquer la remise fidélité si client associé
        if self._cart.client:
            final, discount_percentage, discount_amount = \
                self._loyalty_service.apply_discount(subtotal, self._cart.client)
            total = final
            
            # Calculer les points gagnés
            points_earned = self._loyalty_service.calculate_points_earned(total)
        else:
            total = subtotal
        
        return {
            'subtotal': subtotal,
            'discount_percentage': discount_percentage,
            'discount_amount': discount_amount,
            'total': FormatUtils.round_currency(total),
            'points_earned': points_earned,
            'items_count': self._cart.items_count
        }
    
    def validate_sale(self) -> Tuple[bool, str, Optional[Sale]]:
        """
        Valide et enregistre la vente.
        
        Returns:
            Tuple[bool, str, Optional[Sale]]: (succès, message, vente)
        """
        # Vérifications
        if self._cart.is_empty():
            return False, "Le panier est vide", None
        
        current_user = AuthService.get_current_user()
        if current_user is None:
            return False, "Utilisateur non connecté", None
        
        # Vérifier les stocks une dernière fois
        for item in self._cart.items:
            available, stock = self._stock_service.check_stock_availability(
                item.medicament.id,
                item.quantity
            )
            if not available:
                return False, f"Stock insuffisant pour {item.medicament.name}", None
        
        # Calculer les totaux
        totals = self.calculate_totals()
        
        try:
            # Créer la vente
            sale = Sale(
                sale_number=self._sale_repo.generate_sale_number(),
                user_id=current_user.id,
                client_id=self._cart.client.id if self._cart.client else None,
                sale_date=datetime.now(),
                subtotal=totals['subtotal'],
                discount_percentage=totals['discount_percentage'],
                discount_amount=totals['discount_amount'],
                total=totals['total'],
                loyalty_points_earned=totals['points_earned'],
                loyalty_points_used=0,
                status='completed'
            )
            
            # Créer les lignes
            for item in self._cart.items:
                line = SaleLine(
                    sale_id=0,  # Sera mis à jour après création
                    medicament_id=item.medicament.id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total
                )
                sale.add_line(line)
            
            # Enregistrer la vente
            created_sale = self._sale_repo.create(sale)
            
            # Mettre à jour les stocks
            for item in self._cart.items:
                self._stock_service.remove_stock(
                    medicament_id=item.medicament.id,
                    quantity=item.quantity,
                    reason="Vente",
                    reference_id=created_sale.id
                )
            
            # Mettre à jour le client si associé
            if self._cart.client:
                # Ajouter les points
                self._loyalty_service.add_points_to_client(
                    self._cart.client.id,
                    totals['total']
                )
                
                # Mettre à jour le total dépensé
                self._client_repo.update_total_spent(
                    self._cart.client.id,
                    totals['total']
                )
            
            # Vider le panier
            self._cart.clear()
            
            return True, f"Vente {created_sale.sale_number} enregistrée", created_sale
            
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}", None
    
    def cancel_sale(self, sale_id: int) -> Tuple[bool, str]:
        """
        Annule une vente.
        
        Args:
            sale_id: ID de la vente
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        sale = self._sale_repo.get_by_id(sale_id)
        
        if sale is None:
            return False, "Vente non trouvée"
        
        if sale.status == 'cancelled':
            return False, "Cette vente est déjà annulée"
        
        # Annuler la vente
        success = self._sale_repo.cancel(sale_id)
        
        if success:
            # Remettre le stock
            for line in sale.lines:
                self._stock_service.add_stock(
                    medicament_id=line.medicament_id,
                    quantity=line.quantity,
                    reason=f"Annulation vente {sale.sale_number}"
                )
            
            # Retirer les points si client associé
            if sale.client_id and sale.loyalty_points_earned > 0:
                self._loyalty_service.use_client_points(
                    sale.client_id,
                    sale.loyalty_points_earned
                )
            
            return True, "Vente annulée avec succès"
        else:
            return False, "Erreur lors de l'annulation"
    
    def get_sale(self, sale_id: int) -> Optional[Sale]:
        """Récupère une vente par son ID."""
        return self._sale_repo.get_by_id(sale_id)
    
    def get_sale_by_number(self, sale_number: str) -> Optional[Sale]:
        """Récupère une vente par son numéro."""
        return self._sale_repo.get_by_number(sale_number)
    
    def get_today_sales(self) -> List[Sale]:
        """Récupère les ventes du jour."""
        return self._sale_repo.get_today_sales()
    
    def get_client_sales(self, client_id: int) -> List[Sale]:
        """Récupère les ventes d'un client."""
        return self._sale_repo.get_by_client(client_id)
    
    def get_sale_for_receipt(self, sale_id: int) -> Dict[str, Any]:
        """
        Prépare les données pour un ticket de caisse.
        
        Args:
            sale_id: ID de la vente
            
        Returns:
            dict: Données formatées pour le ticket
        """
        sale = self._sale_repo.get_by_id(sale_id)
        
        if sale is None:
            return {}
        
        lines_data = []
        for line in sale.lines:
            lines_data.append({
                'name': line.medicament_name,
                'code': line.medicament_code,
                'quantity': line.quantity,
                'unit_price': line.unit_price,
                'line_total': line.line_total
            })
        
        client_points = None
        if sale.client_id:
            client = self._client_repo.get_by_id(sale.client_id)
            if client:
                client_points = client.loyalty_points
        
        return {
            'sale_number': sale.sale_number,
            'sale_date': sale.sale_date.strftime("%d/%m/%Y %H:%M"),
            'seller_name': sale.seller_name,
            'client_name': sale.client_name,
            'lines': lines_data,
            'subtotal': sale.subtotal,
            'discount_percentage': sale.discount_percentage,
            'discount_amount': sale.discount_amount,
            'total': sale.total,
            'loyalty_points_earned': sale.loyalty_points_earned,
            'client_points': client_points
        }