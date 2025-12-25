"""
Service de gestion du stock.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, Tuple, List
from datetime import date

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.medicament import Medicament
from models.stock_movement import StockMovement
from database.medicament_repository import MedicamentRepository
from database.stock_movement_repository import StockMovementRepository
from services.auth_service import AuthService
from config import STOCK_CONFIG, MovementType


class StockService:
    """
    Service gérant les opérations de stock.
    
    Responsabilités:
    - CRUD des médicaments
    - Mouvements de stock (entrées/sorties)
    - Calculs d'inventaire
    - Détection des anomalies
    """
    
    def __init__(self):
        """Initialise le service avec les repositories."""
        self._medicament_repo = MedicamentRepository()
        self._movement_repo = StockMovementRepository()
    
    def create_medicament(
        self,
        code: str,
        name: str,
        purchase_price: float,
        selling_price: float,
        description: str = None,
        category: str = None,
        quantity: int = 0,
        threshold: int = None,
        expiration_date: date = None,
        manufacturer: str = None
    ) -> Tuple[bool, str, Optional[Medicament]]:
        """
        Crée un nouveau médicament.
        
        Args:
            code: Code unique
            name: Nom du médicament
            purchase_price: Prix d'achat
            selling_price: Prix de vente
            description: Description
            category: Catégorie
            quantity: Quantité initiale
            threshold: Seuil d'alerte
            expiration_date: Date de péremption
            manufacturer: Fabricant
            
        Returns:
            Tuple[bool, str, Optional[Medicament]]: (succès, message, médicament)
        """
        # Validations
        if not code or not name:
            return False, "Code et nom obligatoires", None
        
        if purchase_price < 0 or selling_price < 0:
            return False, "Les prix doivent être positifs", None
        
        if self._medicament_repo.code_exists(code):
            return False, "Ce code existe déjà", None
        
        # Créer le médicament
        try:
            medicament = Medicament(
                code=code.strip().upper(),
                name=name.strip(),
                description=description,
                category=category,
                purchase_price=purchase_price,
                selling_price=selling_price,
                quantity_in_stock=quantity,
                stock_threshold=threshold or STOCK_CONFIG["default_threshold"],
                expiration_date=expiration_date,
                manufacturer=manufacturer
            )
            
            created = self._medicament_repo.create(medicament)
            
            # Enregistrer le mouvement de stock initial si quantité > 0
            if quantity > 0:
                self._record_movement(
                    medicament_id=created.id,
                    movement_type=MovementType.ENTRY,
                    quantity=quantity,
                    reason="Stock initial"
                )
            
            return True, "Médicament créé avec succès", created
            
        except Exception as e:
            return False, f"Erreur lors de la création: {str(e)}", None
    
    def update_medicament(
        self,
        medicament_id: int,
        code: str,
        name: str,
        purchase_price: float,
        selling_price: float,
        description: str = None,
        category: str = None,
        threshold: int = None,
        expiration_date: date = None,
        manufacturer: str = None
    ) -> Tuple[bool, str]:
        """
        Met à jour un médicament.
        
        Args:
            medicament_id: ID du médicament
            Autres args: Nouvelles valeurs
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        medicament = self._medicament_repo.get_by_id(medicament_id)
        if medicament is None:
            return False, "Médicament non trouvé"
        
        # Vérifier l'unicité du code
        if code != medicament.code:
            if self._medicament_repo.code_exists(code, exclude_id=medicament_id):
                return False, "Ce code existe déjà"
        
        # Mettre à jour
        medicament.code = code.strip().upper()
        medicament.name = name.strip()
        medicament.description = description
        medicament.category = category
        medicament.purchase_price = purchase_price
        medicament.selling_price = selling_price
        medicament.stock_threshold = threshold or STOCK_CONFIG["default_threshold"]
        medicament.expiration_date = expiration_date
        medicament.manufacturer = manufacturer
        
        success = self._medicament_repo.update(medicament)
        
        if success:
            return True, "Médicament mis à jour avec succès"
        else:
            return False, "Erreur lors de la mise à jour"
    
    def delete_medicament(self, medicament_id: int) -> Tuple[bool, str]:
        """
        Supprime un médicament (logiquement).
        
        Args:
            medicament_id: ID du médicament
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        medicament = self._medicament_repo.get_by_id(medicament_id)
        if medicament is None:
            return False, "Médicament non trouvé"
        
        success = self._medicament_repo.delete(medicament_id)
        
        if success:
            return True, "Médicament supprimé avec succès"
        else:
            return False, "Erreur lors de la suppression"
    
    def get_medicament(self, medicament_id: int) -> Optional[Medicament]:
        """Récupère un médicament par son ID."""
        return self._medicament_repo.get_by_id(medicament_id)
    
    def get_medicament_by_code(self, code: str) -> Optional[Medicament]:
        """Récupère un médicament par son code."""
        return self._medicament_repo.get_by_code(code)
    
    def get_all_medicaments(self) -> List[Medicament]:
        """Récupère tous les médicaments actifs."""
        return self._medicament_repo.get_all()
    
    def search_medicaments(
        self,
        keyword: str = "",
        category: str = "",
        in_stock_only: bool = False
    ) -> List[Medicament]:
        """
        Recherche des médicaments.
        
        Args:
            keyword: Mot-clé (code ou nom)
            category: Catégorie
            in_stock_only: Uniquement ceux en stock
            
        Returns:
            List[Medicament]: Médicaments correspondants
        """
        return self._medicament_repo.search(keyword, category, in_stock_only)
    
    def get_categories(self) -> List[str]:
        """Retourne la liste des catégories."""
        return self._medicament_repo.get_categories()
    
    def add_stock(
        self,
        medicament_id: int,
        quantity: int,
        reason: str = "Réapprovisionnement"
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
        if quantity <= 0:
            return False, "La quantité doit être positive"
        
        medicament = self._medicament_repo.get_by_id(medicament_id)
        if medicament is None:
            return False, "Médicament non trouvé"
        
        # Mettre à jour le stock
        success = self._medicament_repo.update_stock(medicament_id, quantity)
        
        if success:
            # Enregistrer le mouvement
            self._record_movement(
                medicament_id=medicament_id,
                movement_type=MovementType.ENTRY,
                quantity=quantity,
                reason=reason
            )
            return True, f"Stock ajouté. Nouveau stock: {medicament.quantity_in_stock + quantity}"
        else:
            return False, "Erreur lors de la mise à jour du stock"
    
    def remove_stock(
        self,
        medicament_id: int,
        quantity: int,
        reason: str = "Sortie manuelle",
        reference_id: int = None
    ) -> Tuple[bool, str]:
        """
        Retire du stock d'un médicament.
        
        Args:
            medicament_id: ID du médicament
            quantity: Quantité à retirer
            reason: Motif
            reference_id: ID de référence (ex: vente)
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        if quantity <= 0:
            return False, "La quantité doit être positive"
        
        medicament = self._medicament_repo.get_by_id(medicament_id)
        if medicament is None:
            return False, "Médicament non trouvé"
        
        # Vérifier le stock disponible
        if medicament.quantity_in_stock < quantity:
            return False, f"Stock insuffisant. Disponible: {medicament.quantity_in_stock}"
        
        # Mettre à jour le stock
        success = self._medicament_repo.update_stock(medicament_id, -quantity)
        
        if success:
            # Enregistrer le mouvement
            self._record_movement(
                medicament_id=medicament_id,
                movement_type=MovementType.EXIT,
                quantity=-quantity,
                reason=reason,
                reference_id=reference_id
            )
            return True, f"Stock retiré. Nouveau stock: {medicament.quantity_in_stock - quantity}"
        else:
            return False, "Erreur lors de la mise à jour du stock"
    
    def adjust_stock(
        self,
        medicament_id: int,
        new_quantity: int,
        reason: str = "Ajustement inventaire"
    ) -> Tuple[bool, str]:
        """
        Ajuste le stock à une nouvelle valeur.
        
        Args:
            medicament_id: ID du médicament
            new_quantity: Nouvelle quantité
            reason: Motif
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        if new_quantity < 0:
            return False, "La quantité ne peut pas être négative"
        
        medicament = self._medicament_repo.get_by_id(medicament_id)
        if medicament is None:
            return False, "Médicament non trouvé"
        
        difference = new_quantity - medicament.quantity_in_stock
        
        if difference == 0:
            return True, "Le stock est déjà à cette valeur"
        
        # Mettre à jour
        medicament.quantity_in_stock = new_quantity
        success = self._medicament_repo.update(medicament)
        
        if success:
            # Enregistrer le mouvement
            self._record_movement(
                medicament_id=medicament_id,
                movement_type=MovementType.ADJUSTMENT,
                quantity=difference,
                reason=reason
            )
            return True, f"Stock ajusté à {new_quantity}"
        else:
            return False, "Erreur lors de l'ajustement"
    
    def _record_movement(
        self,
        medicament_id: int,
        movement_type: str,
        quantity: int,
        reason: str = None,
        reference_id: int = None
    ) -> None:
        """Enregistre un mouvement de stock."""
        current_user = AuthService.get_current_user()
        user_id = current_user.id if current_user else 1
        
        movement = StockMovement(
            medicament_id=medicament_id,
            user_id=user_id,
            movement_type=movement_type,
            quantity=quantity,
            reference_id=reference_id,
            reason=reason
        )
        
        self._movement_repo.create(movement)
    
    def check_stock_availability(
        self,
        medicament_id: int,
        quantity: int
    ) -> Tuple[bool, int]:
        """
        Vérifie la disponibilité du stock.
        
        Args:
            medicament_id: ID du médicament
            quantity: Quantité demandée
            
        Returns:
            Tuple[bool, int]: (disponible, stock_actuel)
        """
        medicament = self._medicament_repo.get_by_id(medicament_id)
        
        if medicament is None:
            return False, 0
        
        available = medicament.quantity_in_stock >= quantity
        return available, medicament.quantity_in_stock
    
    def get_stock_movements(
        self,
        medicament_id: int = None,
        start_date: date = None,
        end_date: date = None
    ) -> List[StockMovement]:
        """
        Récupère l'historique des mouvements de stock.
        
        Args:
            medicament_id: Filtrer par médicament
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            List[StockMovement]: Mouvements correspondants
        """
        if medicament_id:
            return self._movement_repo.get_by_medicament(medicament_id)
        
        if start_date and end_date:
            return self._movement_repo.get_by_date_range(start_date, end_date)
        
        return self._movement_repo.get_all()
    
    def get_total_stock_value(self) -> float:
        """Calcule la valeur totale du stock."""
        return self._medicament_repo.get_total_stock_value()
    
    def get_stock_statistics(self) -> dict:
        """
        Retourne les statistiques du stock.
        
        Returns:
            dict: Statistiques
        """
        return {
            'total_products': self._medicament_repo.count_total(),
            'low_stock_count': self._medicament_repo.count_low_stock(),
            'expiring_soon_count': self._medicament_repo.count_expiring_soon(),
            'total_value': self._medicament_repo.get_total_stock_value()
        }