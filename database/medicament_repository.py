"""
Repository pour la gestion des médicaments.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, List
from database.base_repository import BaseRepository
from models.medicament import Medicament


class MedicamentRepository(BaseRepository[Medicament]):
    """
    Repository pour les opérations CRUD sur les médicaments.
    
    Gère l'accès aux données de la table 'medicaments'.
    """
    
    def create(self, medicament: Medicament) -> Medicament:
        """
        Crée un nouveau médicament.
        
        Args:
            medicament: Médicament à créer
            
        Returns:
            Medicament: Médicament créé avec son ID
        """
        query = """
            INSERT INTO medicaments (
                code, name, description, category, purchase_price,
                selling_price, quantity_in_stock, stock_threshold,
                expiration_date, manufacturer, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            medicament.code,
            medicament.name,
            medicament.description,
            medicament.category,
            medicament.purchase_price,
            medicament.selling_price,
            medicament.quantity_in_stock,
            medicament.stock_threshold,
            medicament.expiration_date.isoformat() if medicament.expiration_date else None,
            medicament.manufacturer,
            1 if medicament.is_active else 0
        )
        
        self.db.execute(query, params)
        medicament.id = self.db.get_last_insert_id()
        return medicament
    
    def get_by_id(self, medicament_id: int) -> Optional[Medicament]:
        """
        Récupère un médicament par son ID.
        
        Args:
            medicament_id: ID du médicament
            
        Returns:
            Optional[Medicament]: Médicament trouvé ou None
        """
        query = "SELECT * FROM medicaments WHERE id = ?"
        result = self.db.fetch_one(query, (medicament_id,))
        
        if result is None:
            return None
        
        return Medicament.from_dict(result)
    
    def get_by_code(self, code: str) -> Optional[Medicament]:
        """
        Récupère un médicament par son code.
        
        Args:
            code: Code du médicament
            
        Returns:
            Optional[Medicament]: Médicament trouvé ou None
        """
        query = "SELECT * FROM medicaments WHERE code = ?"
        result = self.db.fetch_one(query, (code,))
        
        if result is None:
            return None
        
        return Medicament.from_dict(result)
    
    def get_all(self) -> List[Medicament]:
        """
        Récupère tous les médicaments actifs.
        
        Returns:
            List[Medicament]: Liste des médicaments
        """
        query = "SELECT * FROM medicaments WHERE is_active = 1 ORDER BY name"
        results = self.db.fetch_all(query)
        return [Medicament.from_dict(row) for row in results]
    
    def get_all_including_inactive(self) -> List[Medicament]:
        """
        Récupère tous les médicaments.
        
        Returns:
            List[Medicament]: Liste complète
        """
        query = "SELECT * FROM medicaments ORDER BY is_active DESC, name"
        results = self.db.fetch_all(query)
        return [Medicament.from_dict(row) for row in results]
    
    def search(
        self, 
        keyword: str = "", 
        category: str = "",
        in_stock_only: bool = False
    ) -> List[Medicament]:
        """
        Recherche des médicaments selon plusieurs critères.
        
        Args:
            keyword: Mot-clé (code ou nom)
            category: Catégorie
            in_stock_only: Uniquement en stock
            
        Returns:
            List[Medicament]: Médicaments correspondants
        """
        conditions = ["is_active = 1"]
        params = []
        
        if keyword:
            conditions.append("(code LIKE ? OR name LIKE ?)")
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern])
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if in_stock_only:
            conditions.append("quantity_in_stock > 0")
        
        query = f"""
            SELECT * FROM medicaments 
            WHERE {' AND '.join(conditions)}
            ORDER BY name
        """
        
        results = self.db.fetch_all(query, tuple(params))
        return [Medicament.from_dict(row) for row in results]
    
    def get_low_stock(self) -> List[Medicament]:
        """
        Récupère les médicaments avec stock faible.
        
        Returns:
            List[Medicament]: Médicaments sous le seuil
        """
        query = """
            SELECT * FROM medicaments 
            WHERE is_active = 1 AND quantity_in_stock <= stock_threshold
            ORDER BY quantity_in_stock ASC
        """
        results = self.db.fetch_all(query)
        return [Medicament.from_dict(row) for row in results]
    
    def get_expiring_soon(self, days: int = 30) -> List[Medicament]:
        """
        Récupère les médicaments proches de la péremption.
        
        Args:
            days: Nombre de jours avant péremption
            
        Returns:
            List[Medicament]: Médicaments expirant bientôt
        """
        query = """
            SELECT * FROM medicaments 
            WHERE is_active = 1 
                AND expiration_date IS NOT NULL
                AND julianday(expiration_date) - julianday('now') BETWEEN 0 AND ?
            ORDER BY expiration_date ASC
        """
        results = self.db.fetch_all(query, (days,))
        return [Medicament.from_dict(row) for row in results]
    
    def get_expired(self) -> List[Medicament]:
        """
        Récupère les médicaments périmés.
        
        Returns:
            List[Medicament]: Médicaments périmés
        """
        query = """
            SELECT * FROM medicaments 
            WHERE is_active = 1 
                AND expiration_date IS NOT NULL
                AND expiration_date < DATE('now')
            ORDER BY expiration_date ASC
        """
        results = self.db.fetch_all(query)
        return [Medicament.from_dict(row) for row in results]
    
    def get_categories(self) -> List[str]:
        """
        Récupère la liste des catégories distinctes.
        
        Returns:
            List[str]: Liste des catégories
        """
        query = """
            SELECT DISTINCT category FROM medicaments 
            WHERE category IS NOT NULL AND category != '' AND is_active = 1
            ORDER BY category
        """
        results = self.db.fetch_all(query)
        return [row['category'] for row in results]
    
    def update(self, medicament: Medicament) -> bool:
        """
        Met à jour un médicament.
        
        Args:
            medicament: Médicament à mettre à jour
            
        Returns:
            bool: True si mise à jour réussie
        """
        query = """
            UPDATE medicaments SET
                code = ?, name = ?, description = ?, category = ?,
                purchase_price = ?, selling_price = ?, quantity_in_stock = ?,
                stock_threshold = ?, expiration_date = ?, manufacturer = ?,
                is_active = ?
            WHERE id = ?
        """
        params = (
            medicament.code,
            medicament.name,
            medicament.description,
            medicament.category,
            medicament.purchase_price,
            medicament.selling_price,
            medicament.quantity_in_stock,
            medicament.stock_threshold,
            medicament.expiration_date.isoformat() if medicament.expiration_date else None,
            medicament.manufacturer,
            1 if medicament.is_active else 0,
            medicament.id
        )
        
        cursor = self.db.execute(query, params)
        return cursor.rowcount > 0
    
    def update_stock(self, medicament_id: int, quantity_change: int) -> bool:
        """
        Met à jour la quantité en stock.
        
        Args:
            medicament_id: ID du médicament
            quantity_change: Changement de quantité (+/-)
            
        Returns:
            bool: True si mise à jour réussie
        """
        query = """
            UPDATE medicaments 
            SET quantity_in_stock = quantity_in_stock + ?
            WHERE id = ? AND (quantity_in_stock + ?) >= 0
        """
        cursor = self.db.execute(query, (quantity_change, medicament_id, quantity_change))
        return cursor.rowcount > 0
    
    def delete(self, medicament_id: int) -> bool:
        """
        Désactive un médicament (suppression logique).
        
        Args:
            medicament_id: ID du médicament
            
        Returns:
            bool: True si désactivation réussie
        """
        query = "UPDATE medicaments SET is_active = 0 WHERE id = ?"
        cursor = self.db.execute(query, (medicament_id,))
        return cursor.rowcount > 0
    
    def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un code existe déjà.
        
        Args:
            code: Code à vérifier
            exclude_id: ID à exclure
            
        Returns:
            bool: True si existe
        """
        if exclude_id:
            query = "SELECT id FROM medicaments WHERE code = ? AND id != ?"
            result = self.db.fetch_one(query, (code, exclude_id))
        else:
            query = "SELECT id FROM medicaments WHERE code = ?"
            result = self.db.fetch_one(query, (code,))
        
        return result is not None
    
    def count_total(self) -> int:
        """Compte le nombre total de médicaments actifs."""
        query = "SELECT COUNT(*) as count FROM medicaments WHERE is_active = 1"
        result = self.db.fetch_one(query)
        return result['count'] if result else 0
    
    def count_low_stock(self) -> int:
        """Compte les médicaments en stock faible."""
        query = """
            SELECT COUNT(*) as count FROM medicaments 
            WHERE is_active = 1 AND quantity_in_stock <= stock_threshold
        """
        result = self.db.fetch_one(query)
        return result['count'] if result else 0
    
    def count_expiring_soon(self, days: int = 30) -> int:
        """Compte les médicaments expirant bientôt."""
        query = """
            SELECT COUNT(*) as count FROM medicaments 
            WHERE is_active = 1 
                AND expiration_date IS NOT NULL
                AND julianday(expiration_date) - julianday('now') BETWEEN 0 AND ?
        """
        result = self.db.fetch_one(query, (days,))
        return result['count'] if result else 0
    
    def get_total_stock_value(self) -> float:
        """Calcule la valeur totale du stock."""
        query = """
            SELECT SUM(quantity_in_stock * purchase_price) as total 
            FROM medicaments WHERE is_active = 1
        """
        result = self.db.fetch_one(query)
        return result['total'] if result and result['total'] else 0.0