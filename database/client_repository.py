"""
Repository pour la gestion des clients.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, List
from database.base_repository import BaseRepository
from models.client import Client


class ClientRepository(BaseRepository[Client]):
    """
    Repository pour les opérations CRUD sur les clients.
    
    Gère l'accès aux données de la table 'clients'.
    """
    
    def create(self, client: Client) -> Client:
        """
        Crée un nouveau client.
        
        Args:
            client: Client à créer
            
        Returns:
            Client: Client créé avec son ID
        """
        query = """
            INSERT INTO clients (
                code, first_name, last_name, phone, email,
                address, loyalty_points, total_spent, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            client.code,
            client.first_name,
            client.last_name,
            client.phone,
            client.email,
            client.address,
            client.loyalty_points,
            client.total_spent,
            1 if client.is_active else 0
        )
        
        self.db.execute(query, params)
        client.id = self.db.get_last_insert_id()
        return client
    
    def get_by_id(self, client_id: int) -> Optional[Client]:
        """
        Récupère un client par son ID.
        
        Args:
            client_id: ID du client
            
        Returns:
            Optional[Client]: Client trouvé ou None
        """
        query = "SELECT * FROM clients WHERE id = ?"
        result = self.db.fetch_one(query, (client_id,))
        
        if result is None:
            return None
        
        return Client.from_dict(result)
    
    def get_by_code(self, code: str) -> Optional[Client]:
        """
        Récupère un client par son code.
        
        Args:
            code: Code client
            
        Returns:
            Optional[Client]: Client trouvé ou None
        """
        query = "SELECT * FROM clients WHERE code = ?"
        result = self.db.fetch_one(query, (code,))
        
        if result is None:
            return None
        
        return Client.from_dict(result)
    
    def get_by_phone(self, phone: str) -> Optional[Client]:
        """
        Récupère un client par son téléphone.
        
        Args:
            phone: Numéro de téléphone
            
        Returns:
            Optional[Client]: Client trouvé ou None
        """
        query = "SELECT * FROM clients WHERE phone = ?"
        result = self.db.fetch_one(query, (phone,))
        
        if result is None:
            return None
        
        return Client.from_dict(result)
    
    def get_all(self) -> List[Client]:
        """
        Récupère tous les clients actifs.
        
        Returns:
            List[Client]: Liste des clients
        """
        query = "SELECT * FROM clients WHERE is_active = 1 ORDER BY last_name, first_name"
        results = self.db.fetch_all(query)
        return [Client.from_dict(row) for row in results]
    
    def search(self, keyword: str) -> List[Client]:
        """
        Recherche des clients par mot-clé.
        
        Args:
            keyword: Mot-clé (nom, prénom, téléphone, code)
            
        Returns:
            List[Client]: Clients correspondants
        """
        query = """
            SELECT * FROM clients 
            WHERE is_active = 1 AND (
                code LIKE ? OR
                first_name LIKE ? OR 
                last_name LIKE ? OR
                phone LIKE ?
            )
            ORDER BY last_name, first_name
        """
        pattern = f"%{keyword}%"
        params = (pattern, pattern, pattern, pattern)
        
        results = self.db.fetch_all(query, params)
        return [Client.from_dict(row) for row in results]
    
    def update(self, client: Client) -> bool:
        """
        Met à jour un client.
        
        Args:
            client: Client à mettre à jour
            
        Returns:
            bool: True si mise à jour réussie
        """
        query = """
            UPDATE clients SET
                code = ?, first_name = ?, last_name = ?, phone = ?,
                email = ?, address = ?, loyalty_points = ?, 
                total_spent = ?, is_active = ?
            WHERE id = ?
        """
        params = (
            client.code,
            client.first_name,
            client.last_name,
            client.phone,
            client.email,
            client.address,
            client.loyalty_points,
            client.total_spent,
            1 if client.is_active else 0,
            client.id
        )
        
        cursor = self.db.execute(query, params)
        return cursor.rowcount > 0
    
    def update_loyalty_points(self, client_id: int, points_change: int) -> bool:
        """
        Met à jour les points de fidélité.
        
        Args:
            client_id: ID du client
            points_change: Changement de points (+/-)
            
        Returns:
            bool: True si mise à jour réussie
        """
        query = """
            UPDATE clients 
            SET loyalty_points = loyalty_points + ?
            WHERE id = ? AND (loyalty_points + ?) >= 0
        """
        cursor = self.db.execute(query, (points_change, client_id, points_change))
        return cursor.rowcount > 0
    
    def update_total_spent(self, client_id: int, amount: float) -> bool:
        """
        Ajoute un montant au total dépensé.
        
        Args:
            client_id: ID du client
            amount: Montant à ajouter
            
        Returns:
            bool: True si mise à jour réussie
        """
        query = "UPDATE clients SET total_spent = total_spent + ? WHERE id = ?"
        cursor = self.db.execute(query, (amount, client_id))
        return cursor.rowcount > 0
    
    def delete(self, client_id: int) -> bool:
        """
        Désactive un client (suppression logique).
        
        Args:
            client_id: ID du client
            
        Returns:
            bool: True si désactivation réussie
        """
        query = "UPDATE clients SET is_active = 0 WHERE id = ?"
        cursor = self.db.execute(query, (client_id,))
        return cursor.rowcount > 0
    
    def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """Vérifie si un code client existe."""
        if exclude_id:
            query = "SELECT id FROM clients WHERE code = ? AND id != ?"
            result = self.db.fetch_one(query, (code, exclude_id))
        else:
            query = "SELECT id FROM clients WHERE code = ?"
            result = self.db.fetch_one(query, (code,))
        
        return result is not None
    
    def phone_exists(self, phone: str, exclude_id: Optional[int] = None) -> bool:
        """Vérifie si un téléphone existe."""
        if not phone:
            return False
            
        if exclude_id:
            query = "SELECT id FROM clients WHERE phone = ? AND id != ?"
            result = self.db.fetch_one(query, (phone, exclude_id))
        else:
            query = "SELECT id FROM clients WHERE phone = ?"
            result = self.db.fetch_one(query, (phone,))
        
        return result is not None
    
    def generate_code(self) -> str:
        """
        Génère un nouveau code client unique.
        
        Returns:
            str: Code client au format CLI-XXXXX
        """
        query = "SELECT MAX(CAST(SUBSTR(code, 5) AS INTEGER)) as max_num FROM clients WHERE code LIKE 'CLI-%'"
        result = self.db.fetch_one(query)
        
        next_num = 1
        if result and result['max_num']:
            next_num = result['max_num'] + 1
        
        return f"CLI-{next_num:05d}"
    
    def count_total(self) -> int:
        """Compte le nombre total de clients actifs."""
        query = "SELECT COUNT(*) as count FROM clients WHERE is_active = 1"
        result = self.db.fetch_one(query)
        return result['count'] if result else 0