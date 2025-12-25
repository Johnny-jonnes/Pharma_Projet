"""
Repository pour la gestion des mouvements de stock.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, List
from datetime import date
from database.base_repository import BaseRepository
from models.stock_movement import StockMovement


class StockMovementRepository(BaseRepository[StockMovement]):
    """
    Repository pour les opérations sur les mouvements de stock.
    """
    
    def create(self, movement: StockMovement) -> StockMovement:
        """Crée un nouveau mouvement de stock."""
        query = """
            INSERT INTO stock_movements (
                medicament_id, user_id, movement_type, 
                quantity, reference_id, reason
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            movement.medicament_id,
            movement.user_id,
            movement.movement_type,
            movement.quantity,
            movement.reference_id,
            movement.reason
        )
        
        self.db.execute(query, params)
        movement.id = self.db.get_last_insert_id()
        return movement
    
    def get_by_id(self, movement_id: int) -> Optional[StockMovement]:
        """Récupère un mouvement par son ID."""
        query = """
            SELECT sm.*, m.name AS medicament_name, u.full_name AS user_name
            FROM stock_movements sm
            INNER JOIN medicaments m ON sm.medicament_id = m.id
            INNER JOIN users u ON sm.user_id = u.id
            WHERE sm.id = ?
        """
        result = self.db.fetch_one(query, (movement_id,))
        
        if result is None:
            return None
        
        return StockMovement.from_dict(result)
    
    def get_all(self) -> List[StockMovement]:
        """Récupère tous les mouvements."""
        query = """
            SELECT sm.*, m.name AS medicament_name, u.full_name AS user_name
            FROM stock_movements sm
            INNER JOIN medicaments m ON sm.medicament_id = m.id
            INNER JOIN users u ON sm.user_id = u.id
            ORDER BY sm.created_at DESC
        """
        results = self.db.fetch_all(query)
        return [StockMovement.from_dict(row) for row in results]
    
    def get_by_medicament(self, medicament_id: int) -> List[StockMovement]:
        """Récupère les mouvements d'un médicament."""
        query = """
            SELECT sm.*, m.name AS medicament_name, u.full_name AS user_name
            FROM stock_movements sm
            INNER JOIN medicaments m ON sm.medicament_id = m.id
            INNER JOIN users u ON sm.user_id = u.id
            WHERE sm.medicament_id = ?
            ORDER BY sm.created_at DESC
        """
        results = self.db.fetch_all(query, (medicament_id,))
        return [StockMovement.from_dict(row) for row in results]
    
    def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[StockMovement]:
        """Récupère les mouvements sur une période."""
        query = """
            SELECT sm.*, m.name AS medicament_name, u.full_name AS user_name
            FROM stock_movements sm
            INNER JOIN medicaments m ON sm.medicament_id = m.id
            INNER JOIN users u ON sm.user_id = u.id
            WHERE DATE(sm.created_at) BETWEEN ? AND ?
            ORDER BY sm.created_at DESC
        """
        results = self.db.fetch_all(query, (
            start_date.isoformat(), 
            end_date.isoformat()
        ))
        return [StockMovement.from_dict(row) for row in results]
    
    def update(self, movement: StockMovement) -> bool:
        """Les mouvements de stock ne sont pas modifiables."""
        raise NotImplementedError("Les mouvements de stock ne peuvent pas être modifiés")
    
    def delete(self, movement_id: int) -> bool:
        """Les mouvements de stock ne sont pas supprimables."""
        raise NotImplementedError("Les mouvements de stock ne peuvent pas être supprimés")