"""
Contrôleur de gestion des ventes.

Gère les opérations de vente (POS).

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, Tuple, List, Any
from models.sale import Sale
from models.medicament import Medicament
from services.sale_service import SaleService, Cart, CartItem
from services.auth_service import AuthService
from utils.format_utils import FormatUtils


class SaleController:
    """
    Contrôleur pour la gestion des ventes.
    
    Responsabilités:
    - Gestion du panier
    - Validation des ventes
    - Annulation des ventes
    """
    
    def __init__(self):
        """Initialise le contrôleur."""
        self._sale_service = SaleService()
    
    def _check_permission(self) -> Tuple[bool, str]:
        """Vérifie les permissions de vente."""
        current = AuthService.get_current_user()
        
        if current is None:
            return False, "Utilisateur non connecté"
        
        return True, ""
    
    def new_sale(self) -> Cart:
        """
        Démarre une nouvelle vente (vide le panier).
        
        Returns:
            Cart: Nouveau panier
        """
        return self._sale_service.new_cart()
    
    def get_cart(self) -> Cart:
        """
        Retourne le panier courant.
        
        Returns:
            Cart: Panier actuel
        """
        return self._sale_service.cart
    
    def add_product(
        self,
        medicament_id: int,
        quantity: str = "1"
    ) -> Tuple[bool, str]:
        """
        Ajoute un produit au panier.
        
        Args:
            medicament_id: ID du médicament
            quantity: Quantité
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        allowed, message = self._check_permission()
        if not allowed:
            return False, message
        
        try:
            qty = int(quantity)
            if qty <= 0:
                return False, "La quantité doit être positive"
        except ValueError:
            return False, "Quantité invalide"
        
        return self._sale_service.add_to_cart(medicament_id, qty)
    
    def add_product_by_code(
        self,
        code: str,
        quantity: str = "1"
    ) -> Tuple[bool, str]:
        """
        Ajoute un produit par son code.
        
        Args:
            code: Code du médicament
            quantity: Quantité
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        from services.stock_service import StockService
        stock_service = StockService()
        
        medicament = stock_service.get_medicament_by_code(code.strip().upper())
        
        if medicament is None:
            return False, f"Produit '{code}' non trouvé"
        
        return self.add_product(medicament.id, quantity)
    
    def remove_product(self, medicament_id: int) -> Tuple[bool, str]:
        """
        Retire un produit du panier.
        
        Args:
            medicament_id: ID du médicament
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        return self._sale_service.remove_from_cart(medicament_id)
    
    def update_quantity(
        self,
        medicament_id: int,
        quantity: str
    ) -> Tuple[bool, str]:
        """
        Met à jour la quantité d'un produit.
        
        Args:
            medicament_id: ID du médicament
            quantity: Nouvelle quantité
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        try:
            qty = int(quantity)
        except ValueError:
            return False, "Quantité invalide"
        
        return self._sale_service.update_cart_quantity(medicament_id, qty)
    
    def set_client(self, client_id: int) -> Tuple[bool, str]:
        """
        Associe un client à la vente.
        
        Args:
            client_id: ID du client
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        return self._sale_service.set_client(client_id)
    
    def remove_client(self) -> None:
        """Retire le client de la vente."""
        self._sale_service.remove_client()
    
    def get_totals(self) -> dict:
        """
        Calcule les totaux de la vente.
        
        Returns:
            dict: Totaux formatés
        """
        totals = self._sale_service.calculate_totals()
        
        return {
            'subtotal': totals['subtotal'],
            'subtotal_display': FormatUtils.format_currency(totals['subtotal']),
            'discount_percentage': totals['discount_percentage'],
            'discount_display': FormatUtils.format_percentage(totals['discount_percentage']),
            'discount_amount': totals['discount_amount'],
            'discount_amount_display': FormatUtils.format_currency(totals['discount_amount']),
            'total': totals['total'],
            'total_display': FormatUtils.format_currency(totals['total']),
            'points_earned': totals['points_earned'],
            'items_count': totals['items_count']
        }
    
    def validate_sale(self) -> Tuple[bool, str, Optional[Sale]]:
        """
        Valide et enregistre la vente.
        
        Returns:
            Tuple[bool, str, Optional[Sale]]: (succès, message, vente)
        """
        allowed, message = self._check_permission()
        if not allowed:
            return False, message, None
        
        return self._sale_service.validate_sale()
    
    def cancel_sale(self, sale_id: int) -> Tuple[bool, str]:
        """
        Annule une vente.
        
        Args:
            sale_id: ID de la vente
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        # Vérifier les permissions (admin/pharmacien)
        current = AuthService.get_current_user()
        if current is None:
            return False, "Utilisateur non connecté"
        
        if current.role == 'vendeur':
            return False, "Permission refusée"
        
        return self._sale_service.cancel_sale(sale_id)
    
    def get_sale(self, sale_id: int) -> Optional[Sale]:
        """Récupère une vente."""
        return self._sale_service.get_sale(sale_id)
    
    def get_today_sales(self) -> List[Sale]:
        """Récupère les ventes du jour."""
        return self._sale_service.get_today_sales()
    
    def get_sale_for_receipt(self, sale_id: int) -> dict:
        """Prépare les données pour le ticket."""
        return self._sale_service.get_sale_for_receipt(sale_id)
    
    def get_cart_items_for_table(self) -> List[dict]:
        """
        Prépare les articles du panier pour affichage.
        
        Returns:
            List[dict]: Données formatées
        """
        cart = self.get_cart()
        
        result = []
        for item in cart.items:
            result.append({
                'id': item.medicament.id,
                'code': item.medicament.code,
                'name': item.medicament.name,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'unit_price_display': FormatUtils.format_currency(item.unit_price),
                'line_total': item.line_total,
                'line_total_display': FormatUtils.format_currency(item.line_total),
                'stock_available': item.medicament.quantity_in_stock
            })
        
        return result
    
    def get_sales_for_table(self, sales: List[Sale]) -> List[dict]:
        """
        Prépare les ventes pour affichage tableau.
        
        Args:
            sales: Liste des ventes
            
        Returns:
            List[dict]: Données formatées
        """
        result = []
        for sale in sales:
            result.append({
                'id': sale.id,
                'sale_number': sale.sale_number,
                'date': sale.sale_date.strftime("%d/%m/%Y %H:%M"),
                'client': sale.client_name or "Client anonyme",
                'seller': sale.seller_name,
                'total': sale.total,
                'total_display': FormatUtils.format_currency(sale.total),
                'status': sale.status,
                'status_display': "Validée" if sale.status == 'completed' else "Annulée"
            })
        
        return result