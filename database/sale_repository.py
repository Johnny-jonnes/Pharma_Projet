"""
Repository pour la gestion des ventes.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, List, Tuple
from datetime import datetime, date
from database.base_repository import BaseRepository
from models.sale import Sale
from models.sale_line import SaleLine


class SaleRepository(BaseRepository[Sale]):
    """
    Repository pour les opérations CRUD sur les ventes.
    """
    
    def create(self, sale: Sale) -> Sale:
        """
        Crée une nouvelle vente avec ses lignes.
        
        Args:
            sale: Vente à créer (avec lignes)
            
        Returns:
            Sale: Vente créée avec son ID
        """
        # Insérer l'en-tête de vente
        query = """
            INSERT INTO sales (
                sale_number, client_id, user_id, sale_date, subtotal,
                discount_percentage, discount_amount, total,
                loyalty_points_earned, loyalty_points_used, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            sale.sale_number,
            sale.client_id,
            sale.user_id,
            sale.sale_date.isoformat() if sale.sale_date else datetime.now().isoformat(),
            sale.subtotal,
            sale.discount_percentage,
            sale.discount_amount,
            sale.total,
            sale.loyalty_points_earned,
            sale.loyalty_points_used,
            sale.status
        )
        
        self.db.execute(query, params)
        sale.id = self.db.get_last_insert_id()
        
        # Insérer les lignes de vente
        if sale.lines:
            self._create_lines(sale.id, sale.lines)
        
        return sale
    
    def _create_lines(self, sale_id: int, lines: List[SaleLine]) -> None:
        """Crée les lignes d'une vente."""
        query = """
            INSERT INTO sale_lines (sale_id, medicament_id, quantity, unit_price, line_total)
            VALUES (?, ?, ?, ?, ?)
        """
        params_list = [
            (sale_id, line.medicament_id, line.quantity, line.unit_price, line.line_total)
            for line in lines
        ]
        
        self.db.execute_many(query, params_list)
    
    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        """Récupère une vente par son ID."""
        query = """
            SELECT s.*, 
                   c.first_name || ' ' || c.last_name AS client_name,
                   u.full_name AS seller_name
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            INNER JOIN users u ON s.user_id = u.id
            WHERE s.id = ?
        """
        result = self.db.fetch_one(query, (sale_id,))
        
        if result is None:
            return None
        
        sale = Sale.from_dict(result)
        sale.lines = self.get_lines(sale_id)
        return sale
    
    def get_by_number(self, sale_number: str) -> Optional[Sale]:
        """Récupère une vente par son numéro."""
        query = """
            SELECT s.*, 
                   c.first_name || ' ' || c.last_name AS client_name,
                   u.full_name AS seller_name
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            INNER JOIN users u ON s.user_id = u.id
            WHERE s.sale_number = ?
        """
        result = self.db.fetch_one(query, (sale_number,))
        
        if result is None:
            return None
        
        sale = Sale.from_dict(result)
        sale.lines = self.get_lines(sale.id)
        return sale
    
    def get_lines(self, sale_id: int) -> List[SaleLine]:
        """Récupère les lignes d'une vente."""
        query = """
            SELECT sl.*, m.name AS medicament_name, m.code AS medicament_code
            FROM sale_lines sl
            INNER JOIN medicaments m ON sl.medicament_id = m.id
            WHERE sl.sale_id = ?
            ORDER BY sl.id
        """
        results = self.db.fetch_all(query, (sale_id,))
        return [SaleLine.from_dict(row) for row in results]
    
    def get_all(self) -> List[Sale]:
        """Récupère toutes les ventes."""
        query = """
            SELECT s.*, 
                   c.first_name || ' ' || c.last_name AS client_name,
                   u.full_name AS seller_name
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            INNER JOIN users u ON s.user_id = u.id
            ORDER BY s.sale_date DESC
        """
        results = self.db.fetch_all(query)
        return [Sale.from_dict(row) for row in results]
    
    def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Sale]:
        """
        Récupère les ventes sur une période.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            List[Sale]: Ventes de la période
        """
        query = """
            SELECT s.*, 
                   c.first_name || ' ' || c.last_name AS client_name,
                   u.full_name AS seller_name
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            INNER JOIN users u ON s.user_id = u.id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
            ORDER BY s.sale_date DESC
        """
        results = self.db.fetch_all(query, (start_date.isoformat(), end_date.isoformat()))
        return [Sale.from_dict(row) for row in results]
    
    def get_today_sales(self) -> List[Sale]:
        """Récupère les ventes du jour."""
        today = date.today()
        return self.get_by_date_range(today, today)
    
    def get_by_client(self, client_id: int) -> List[Sale]:
        """Récupère les ventes d'un client."""
        query = """
            SELECT s.*, 
                   c.first_name || ' ' || c.last_name AS client_name,
                   u.full_name AS seller_name
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            INNER JOIN users u ON s.user_id = u.id
            WHERE s.client_id = ?
            ORDER BY s.sale_date DESC
        """
        results = self.db.fetch_all(query, (client_id,))
        return [Sale.from_dict(row) for row in results]
    
    def update(self, sale: Sale) -> bool:
        """Met à jour une vente."""
        query = """
            UPDATE sales SET
                client_id = ?, subtotal = ?, discount_percentage = ?,
                discount_amount = ?, total = ?, loyalty_points_earned = ?,
                loyalty_points_used = ?, status = ?
            WHERE id = ?
        """
        params = (
            sale.client_id,
            sale.subtotal,
            sale.discount_percentage,
            sale.discount_amount,
            sale.total,
            sale.loyalty_points_earned,
            sale.loyalty_points_used,
            sale.status,
            sale.id
        )
        
        cursor = self.db.execute(query, params)
        return cursor.rowcount > 0
    
    def cancel(self, sale_id: int) -> bool:
        """Annule une vente."""
        query = "UPDATE sales SET status = 'cancelled' WHERE id = ?"
        cursor = self.db.execute(query, (sale_id,))
        return cursor.rowcount > 0
    
    def delete(self, sale_id: int) -> bool:
        """
        Supprime une vente (déconseillé, préférer cancel).
        Les lignes sont supprimées en cascade.
        """
        query = "DELETE FROM sales WHERE id = ?"
        cursor = self.db.execute(query, (sale_id,))
        return cursor.rowcount > 0
    
    def generate_sale_number(self) -> str:
        """
        Génère un numéro de vente unique.
        
        Returns:
            str: Numéro au format VNT-YYYYMMDD-XXX
        """
        today = date.today()
        prefix = f"VNT-{today.strftime('%Y%m%d')}-"
        
        query = """
            SELECT MAX(CAST(SUBSTR(sale_number, 14) AS INTEGER)) as max_num 
            FROM sales 
            WHERE sale_number LIKE ?
        """
        result = self.db.fetch_one(query, (f"{prefix}%",))
        
        next_num = 1
        if result and result['max_num']:
            next_num = result['max_num'] + 1
        
        return f"{prefix}{next_num:03d}"
    
    def get_daily_total(self, target_date: date = None) -> float:
        """Calcule le total des ventes d'un jour."""
        if target_date is None:
            target_date = date.today()
        
        query = """
            SELECT COALESCE(SUM(total), 0) AS total 
            FROM sales 
            WHERE DATE(sale_date) = ? AND status = 'completed'
        """
        result = self.db.fetch_one(query, (target_date.isoformat(),))
        return result['total'] if result else 0.0
    
    def get_daily_count(self, target_date: date = None) -> int:
        """Compte les ventes d'un jour."""
        if target_date is None:
            target_date = date.today()
        
        query = """
            SELECT COUNT(*) AS count 
            FROM sales 
            WHERE DATE(sale_date) = ? AND status = 'completed'
        """
        result = self.db.fetch_one(query, (target_date.isoformat(),))
        return result['count'] if result else 0
    
    def get_top_products(
        self, 
        start_date: date, 
        end_date: date, 
        limit: int = 10
    ) -> List[dict]:
        """
        Récupère les produits les plus vendus sur une période.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            limit: Nombre de résultats
            
        Returns:
            List[dict]: Produits avec quantités et totaux
        """
        query = """
            SELECT 
                m.id, m.code, m.name,
                SUM(sl.quantity) AS total_quantity,
                SUM(sl.line_total) AS total_revenue
            FROM sale_lines sl
            INNER JOIN sales s ON sl.sale_id = s.id
            INNER JOIN medicaments m ON sl.medicament_id = m.id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
                AND s.status = 'completed'
            GROUP BY m.id, m.code, m.name
            ORDER BY total_quantity DESC
            LIMIT ?
        """
        return self.db.fetch_all(query, (
            start_date.isoformat(), 
            end_date.isoformat(), 
            limit
        ))
    
    def get_by_date_range_and_user(
        self,
        start_date: date,
        end_date: date,
        user_id: int
    ) -> List[Sale]:
        """
        Récupère les ventes sur une période pour un utilisateur spécifique.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            user_id: ID de l'utilisateur
            
        Returns:
            List[Sale]: Liste des ventes
        """
        query = """
            SELECT 
                s.*,
                c.first_name || ' ' || c.last_name AS client_name,
                u.full_name AS seller_name
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            LEFT JOIN users u ON s.user_id = u.id
            WHERE DATE(s.sale_date) >= DATE(?)
            AND DATE(s.sale_date) <= DATE(?)
            AND s.user_id = ?
            ORDER BY s.sale_date DESC
        """
        
        # CORRECTION: utiliser self.db.fetch_all et non self._fetch_all
        results = self.db.fetch_all(query, (
            start_date.isoformat(),
            end_date.isoformat(),
            user_id
        ))
        
        return [Sale.from_dict(row) for row in results]