"""
Contrôleur de gestion des médicaments.

Gère les opérations sur les médicaments et le stock.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, Tuple, List
from datetime import date
from models.medicament import Medicament
from services.stock_service import StockService
from services.auth_service import AuthService


class MedicamentController:
    """
    Contrôleur pour la gestion des médicaments.
    
    Responsabilités:
    - CRUD des médicaments
    - Gestion du stock
    - Recherche et filtrage
    """
    
    def __init__(self):
        """Initialise le contrôleur."""
        self._stock_service = StockService()
    
    def _check_permission(self) -> Tuple[bool, str]:
        """Vérifie les permissions de gestion des médicaments."""
        current = AuthService.get_current_user()
        
        if current is None:
            return False, "Utilisateur non connecté"
        
        if not current.can_manage_medicaments():
            return False, "Permission refusée"
        
        return True, ""
    
    def get_all_medicaments(self) -> List[Medicament]:
        """
        Récupère tous les médicaments.
        
        Returns:
            List[Medicament]: Liste des médicaments
        """
        return self._stock_service.get_all_medicaments()
    
    def get_medicament(self, medicament_id: int) -> Optional[Medicament]:
        """
        Récupère un médicament par son ID.
        
        Args:
            medicament_id: ID du médicament
            
        Returns:
            Optional[Medicament]: Médicament trouvé ou None
        """
        return self._stock_service.get_medicament(medicament_id)
    
    def search_medicaments(
        self,
        keyword: str = "",
        category: str = "",
        in_stock_only: bool = False
    ) -> List[Medicament]:
        """
        Recherche des médicaments.
        
        Args:
            keyword: Mot-clé de recherche
            category: Catégorie
            in_stock_only: Uniquement en stock
            
        Returns:
            List[Medicament]: Médicaments correspondants
        """
        return self._stock_service.search_medicaments(
            keyword=keyword,
            category=category,
            in_stock_only=in_stock_only
        )
    
    def get_categories(self) -> List[str]:
        """Retourne la liste des catégories."""
        return self._stock_service.get_categories()
    
    def create_medicament(
        self,
        code: str,
        name: str,
        purchase_price: str,
        selling_price: str,
        description: str = "",
        category: str = "",
        quantity: str = "0",
        threshold: str = "",
        expiration_date: Optional[date] = None,
        manufacturer: str = ""
    ) -> Tuple[bool, str]:
        """
        Crée un nouveau médicament.
        
        Args:
            code: Code unique
            name: Nom
            purchase_price: Prix d'achat (string pour validation)
            selling_price: Prix de vente (string pour validation)
            description: Description
            category: Catégorie
            quantity: Quantité initiale
            threshold: Seuil d'alerte
            expiration_date: Date de péremption
            manufacturer: Fabricant
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        # Vérifier les permissions
        allowed, message = self._check_permission()
        if not allowed:
            return False, message
        
        # Validation des champs obligatoires
        if not code or not code.strip():
            return False, "Le code est obligatoire"
        
        if not name or not name.strip():
            return False, "Le nom est obligatoire"
        
        # Validation et conversion des prix
        try:
            purchase = float(purchase_price) if purchase_price else 0.0
            if purchase < 0:
                return False, "Le prix d'achat doit être positif"
        except ValueError:
            return False, "Prix d'achat invalide"
        
        try:
            selling = float(selling_price) if selling_price else 0.0
            if selling < 0:
                return False, "Le prix de vente doit être positif"
        except ValueError:
            return False, "Prix de vente invalide"
        
        # Validation quantité
        try:
            qty = int(quantity) if quantity else 0
            if qty < 0:
                return False, "La quantité ne peut pas être négative"
        except ValueError:
            return False, "Quantité invalide"
        
        # Validation seuil
        thresh = None
        if threshold:
            try:
                thresh = int(threshold)
                if thresh < 0:
                    return False, "Le seuil doit être positif"
            except ValueError:
                return False, "Seuil invalide"
        
        # Créer le médicament
        success, message, _ = self._stock_service.create_medicament(
            code=code.strip(),
            name=name.strip(),
            purchase_price=purchase,
            selling_price=selling,
            description=description.strip() if description else None,
            category=category.strip() if category else None,
            quantity=qty,
            threshold=thresh,
            expiration_date=expiration_date,
            manufacturer=manufacturer.strip() if manufacturer else None
        )
        
        return success, message
    
    def update_medicament(
        self,
        medicament_id: int,
        code: str,
        name: str,
        purchase_price: str,
        selling_price: str,
        description: str = "",
        category: str = "",
        threshold: str = "",
        expiration_date: Optional[date] = None,
        manufacturer: str = ""
    ) -> Tuple[bool, str]:
        """
        Met à jour un médicament.
        
        Args:
            medicament_id: ID du médicament
            Autres args: Nouvelles valeurs
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        # Vérifier les permissions
        allowed, message = self._check_permission()
        if not allowed:
            return False, message
        
        # Validation des champs
        if not code or not code.strip():
            return False, "Le code est obligatoire"
        
        if not name or not name.strip():
            return False, "Le nom est obligatoire"
        
        try:
            purchase = float(purchase_price) if purchase_price else 0.0
            if purchase < 0:
                return False, "Le prix d'achat doit être positif"
        except ValueError:
            return False, "Prix d'achat invalide"
        
        try:
            selling = float(selling_price) if selling_price else 0.0
            if selling < 0:
                return False, "Le prix de vente doit être positif"
        except ValueError:
            return False, "Prix de vente invalide"
        
        thresh = None
        if threshold:
            try:
                thresh = int(threshold)
            except ValueError:
                return False, "Seuil invalide"
        
        return self._stock_service.update_medicament(
            medicament_id=medicament_id,
            code=code.strip(),
            name=name.strip(),
            purchase_price=purchase,
            selling_price=selling,
            description=description.strip() if description else None,
            category=category.strip() if category else None,
            threshold=thresh,
            expiration_date=expiration_date,
            manufacturer=manufacturer.strip() if manufacturer else None
        )
    
    def delete_medicament(self, medicament_id: int) -> Tuple[bool, str]:
        """
        Supprime un médicament.
        
        Args:
            medicament_id: ID du médicament
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        allowed, message = self._check_permission()
        if not allowed:
            return False, message
        
        return self._stock_service.delete_medicament(medicament_id)
    
    def add_stock(
        self,
        medicament_id: int,
        quantity: str,
        reason: str = ""
    ) -> Tuple[bool, str]:
        """
        Ajoute du stock à un médicament.
        
        Args:
            medicament_id: ID du médicament
            quantity: Quantité à ajouter
            reason: Motif
            
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
        
        return self._stock_service.add_stock(
            medicament_id=medicament_id,
            quantity=qty,
            reason=reason or "Réapprovisionnement"
        )
    
    def adjust_stock(
        self,
        medicament_id: int,
        new_quantity: str,
        reason: str = ""
    ) -> Tuple[bool, str]:
        """
        Ajuste le stock d'un médicament.
        
        Args:
            medicament_id: ID du médicament
            new_quantity: Nouvelle quantité
            reason: Motif
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        allowed, message = self._check_permission()
        if not allowed:
            return False, message
        
        try:
            qty = int(new_quantity)
            if qty < 0:
                return False, "La quantité ne peut pas être négative"
        except ValueError:
            return False, "Quantité invalide"
        
        return self._stock_service.adjust_stock(
            medicament_id=medicament_id,
            new_quantity=qty,
            reason=reason or "Ajustement inventaire"
        )
    
    def get_stock_statistics(self) -> dict:
        """Retourne les statistiques du stock."""
        return self._stock_service.get_stock_statistics()
    
    def get_medicaments_for_table(self) -> List[dict]:
        """
        Prépare les données des médicaments pour affichage tableau.
        
        Returns:
            List[dict]: Données formatées
        """
        medicaments = self.get_all_medicaments()
        
        result = []
        for med in medicaments:
            result.append({
                'id': med.id,
                'code': med.code,
                'name': med.name,
                'category': med.category or "-",
                'purchase_price': med.purchase_price,
                'selling_price': med.selling_price,
                'quantity': med.quantity_in_stock,
                'threshold': med.stock_threshold,
                'expiration': med.expiration_date.strftime("%d/%m/%Y") if med.expiration_date else "-",
                'is_low_stock': med.is_low_stock(),
                'is_expiring': med.is_expiring_soon(),
                'is_expired': med.is_expired()
            })
        
        return result