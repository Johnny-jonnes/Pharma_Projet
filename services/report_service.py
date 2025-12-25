"""
Service de génération des rapports.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from dataclasses import dataclass

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.sale_repository import SaleRepository
from database.medicament_repository import MedicamentRepository
from database.client_repository import ClientRepository
from database.stock_movement_repository import StockMovementRepository
from config import BASE_DIR


@dataclass
class ReportPeriod:
    """Période d'un rapport."""
    start_date: date
    end_date: date
    label: str


class ReportService:
    """
    Service de génération des rapports et statistiques.
    
    Responsabilités:
    - Génération de rapports de ventes
    - Rapports de stock
    - Statistiques diverses
    - Export PDF/CSV
    """
    
    def __init__(self):
        """Initialise le service."""
        self._sale_repo = SaleRepository()
        self._medicament_repo = MedicamentRepository()
        self._client_repo = ClientRepository()
        self._movement_repo = StockMovementRepository()
        
        # Répertoire des exports
        self._export_dir = os.path.join(BASE_DIR, "exports")
    
    def _ensure_export_dir(self) -> str:
        """Crée le répertoire d'export si nécessaire."""
        if not os.path.exists(self._export_dir):
            os.makedirs(self._export_dir)
        return self._export_dir
    
    def _format_date(self, d: date) -> str:
        """Formate une date pour affichage."""
        return d.strftime("%d/%m/%Y")
    
    def _format_datetime(self, dt: datetime) -> str:
        """Formate une date/heure pour affichage."""
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        return dt.strftime("%d/%m/%Y %H:%M")
    
    def _format_currency(self, amount: float) -> str:
        """Formate un montant en devise."""
        return f"{amount:.2f} €"
    
    def _round_currency(self, amount: float) -> float:
        """Arrondit un montant à 2 décimales."""
        return round(amount, 2)
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques pour le tableau de bord.
        
        Returns:
            dict: Statistiques principales
        """
        today = date.today()
        
        return {
            # Ventes du jour
            'today_sales_count': self._sale_repo.get_daily_count(today),
            'today_sales_total': self._sale_repo.get_daily_total(today),
            
            # Stock
            'total_products': self._medicament_repo.count_total(),
            'low_stock_count': self._medicament_repo.count_low_stock(),
            'expiring_soon_count': self._medicament_repo.count_expiring_soon(),
            'stock_value': self._medicament_repo.get_total_stock_value(),
            
            # Clients
            'total_clients': self._client_repo.count_total()
        }
    
    def get_sales_report(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Génère un rapport de ventes sur une période.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            dict: Données du rapport
        """
        sales = self._sale_repo.get_by_date_range(start_date, end_date)
        
        # Filtrer les ventes complétées
        completed_sales = [s for s in sales if s.status == 'completed']
        cancelled_sales = [s for s in sales if s.status == 'cancelled']
        
        # Calculs
        total_revenue = sum(s.total for s in completed_sales)
        total_discount = sum(s.discount_amount for s in completed_sales)
        total_items = sum(s.get_items_count() for s in completed_sales)
        
        avg_sale = total_revenue / len(completed_sales) if completed_sales else 0
        
        # Ventes par jour
        daily_sales = self._aggregate_daily_sales(completed_sales)
        
        return {
            'period': {
                'start': self._format_date(start_date),
                'end': self._format_date(end_date)
            },
            'summary': {
                'total_sales': len(completed_sales),
                'cancelled_sales': len(cancelled_sales),
                'total_revenue': self._round_currency(total_revenue),
                'total_discount': self._round_currency(total_discount),
                'total_items': total_items,
                'average_sale': self._round_currency(avg_sale)
            },
            'sales': [
                {
                    'sale_number': s.sale_number,
                    'sale_date': self._format_datetime(s.sale_date),
                    'client_name': s.client_name or 'Anonyme',
                    'seller_name': s.seller_name,
                    'total': self._round_currency(s.total),
                    'items_count': s.get_items_count(),
                    'status': s.status
                }
                for s in sales
            ],
            'daily_breakdown': daily_sales
        }
    
    def _aggregate_daily_sales(self, sales: List) -> List[Dict[str, Any]]:
        """
        Agrège les ventes par jour.
        
        Args:
            sales: Liste des ventes
            
        Returns:
            list: Ventes agrégées par jour
        """
        daily = {}
        
        for sale in sales:
            sale_date = sale.sale_date
            if isinstance(sale_date, str):
                sale_date = datetime.fromisoformat(sale_date)
            
            day_key = sale_date.date().isoformat()
            
            if day_key not in daily:
                daily[day_key] = {
                    'date': self._format_date(sale_date.date()),
                    'count': 0,
                    'total': 0.0
                }
            
            daily[day_key]['count'] += 1
            daily[day_key]['total'] += sale.total
        
        # Convertir en liste et arrondir
        result = []
        for day_data in daily.values():
            day_data['total'] = self._round_currency(day_data['total'])
            result.append(day_data)
        
        return sorted(result, key=lambda x: x['date'])
    
    def get_stock_report(self) -> Dict[str, Any]:
        """
        Génère un rapport de l'état du stock.
        
        Returns:
            dict: Données du rapport stock
        """
        all_products = self._medicament_repo.get_all()
        low_stock = self._medicament_repo.get_low_stock()
        expiring_soon = self._medicament_repo.get_expiring_soon()
        expired = self._medicament_repo.get_expired()
        
        # Calculs
        total_value = sum(m.quantity_in_stock * m.purchase_price for m in all_products)
        total_selling_value = sum(m.quantity_in_stock * m.selling_price for m in all_products)
        total_items = sum(m.quantity_in_stock for m in all_products)
        
        # Regroupement par catégorie
        by_category = self._aggregate_by_category(all_products)
        
        return {
            'generated_at': self._format_datetime(datetime.now()),
            'summary': {
                'total_products': len(all_products),
                'total_items': total_items,
                'stock_value_purchase': self._round_currency(total_value),
                'stock_value_selling': self._round_currency(total_selling_value),
                'potential_margin': self._round_currency(total_selling_value - total_value),
                'low_stock_count': len(low_stock),
                'expiring_soon_count': len(expiring_soon),
                'expired_count': len(expired)
            },
            'low_stock': [
                {
                    'code': m.code,
                    'name': m.name,
                    'quantity': m.quantity_in_stock,
                    'threshold': m.stock_threshold,
                    'needed': m.stock_threshold - m.quantity_in_stock
                }
                for m in low_stock
            ],
            'expiring_soon': [
                {
                    'code': m.code,
                    'name': m.name,
                    'quantity': m.quantity_in_stock,
                    'expiration_date': self._format_date(m.expiration_date) if m.expiration_date else 'N/A',
                    'days_until_expiry': m.days_until_expiry()
                }
                for m in expiring_soon
            ],
            'expired': [
                {
                    'code': m.code,
                    'name': m.name,
                    'quantity': m.quantity_in_stock,
                    'expiration_date': self._format_date(m.expiration_date) if m.expiration_date else 'N/A'
                }
                for m in expired
            ],
            'by_category': by_category,
            'all_products': [
                {
                    'code': m.code,
                    'name': m.name,
                    'category': m.category or 'Non catégorisé',
                    'quantity': m.quantity_in_stock,
                    'purchase_price': self._round_currency(m.purchase_price),
                    'selling_price': self._round_currency(m.selling_price),
                    'stock_value': self._round_currency(m.quantity_in_stock * m.purchase_price),
                    'expiration_date': self._format_date(m.expiration_date) if m.expiration_date else 'N/A'
                }
                for m in all_products
            ]
        }
    
    def _aggregate_by_category(self, products: List) -> List[Dict[str, Any]]:
        """
        Agrège les produits par catégorie.
        
        Args:
            products: Liste des produits
            
        Returns:
            list: Produits agrégés par catégorie
        """
        categories = {}
        
        for product in products:
            cat = product.category or 'Non catégorisé'
            
            if cat not in categories:
                categories[cat] = {
                    'category': cat,
                    'products_count': 0,
                    'total_items': 0,
                    'total_value': 0.0
                }
            
            categories[cat]['products_count'] += 1
            categories[cat]['total_items'] += product.quantity_in_stock
            categories[cat]['total_value'] += product.quantity_in_stock * product.purchase_price
        
        # Arrondir les valeurs
        for cat_data in categories.values():
            cat_data['total_value'] = self._round_currency(cat_data['total_value'])
        
        return sorted(categories.values(), key=lambda x: x['category'])
    
    def get_top_products_report(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Génère un rapport des produits les plus vendus.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            limit: Nombre de produits à afficher
            
        Returns:
            dict: Données du rapport
        """
        top_products = self._sale_repo.get_top_products(start_date, end_date, limit)
        
        total_quantity = sum(p['total_quantity'] for p in top_products)
        total_revenue = sum(p['total_revenue'] for p in top_products)
        
        return {
            'period': {
                'start': self._format_date(start_date),
                'end': self._format_date(end_date)
            },
            'summary': {
                'products_count': len(top_products),
                'total_quantity': total_quantity,
                'total_revenue': self._round_currency(total_revenue)
            },
            'products': [
                {
                    'rank': idx + 1,
                    'code': p['code'],
                    'name': p['name'],
                    'quantity_sold': p['total_quantity'],
                    'revenue': self._round_currency(p['total_revenue']),
                    'percentage': round((p['total_quantity'] / total_quantity * 100) if total_quantity > 0 else 0, 1)
                }
                for idx, p in enumerate(top_products)
            ]
        }
    
    def get_client_history_report(self, client_id: int) -> Dict[str, Any]:
        """
        Génère un rapport d'historique pour un client.
        
        Args:
            client_id: ID du client
            
        Returns:
            dict: Données du rapport
        """
        client = self._client_repo.get_by_id(client_id)
        if not client:
            return {'error': 'Client non trouvé'}
        
        sales = self._sale_repo.get_by_client(client_id)
        completed_sales = [s for s in sales if s.status == 'completed']
        
        total_spent = sum(s.total for s in completed_sales)
        total_visits = len(completed_sales)
        avg_basket = total_spent / total_visits if total_visits > 0 else 0
        
        return {
            'client': {
                'code': client.code,
                'name': client.get_full_name(),
                'phone': client.phone or 'N/A',
                'email': client.email or 'N/A',
                'loyalty_points': client.loyalty_points,
                'member_since': self._format_datetime(client.created_at) if client.created_at else 'N/A'
            },
            'summary': {
                'total_visits': total_visits,
                'total_spent': self._round_currency(total_spent),
                'average_basket': self._round_currency(avg_basket),
                'loyalty_points': client.loyalty_points
            },
            'purchases': [
                {
                    'sale_number': s.sale_number,
                    'date': self._format_datetime(s.sale_date),
                    'total': self._round_currency(s.total),
                    'items_count': s.get_items_count(),
                    'points_earned': s.loyalty_points_earned
                }
                for s in completed_sales[:50]  # Limiter à 50 dernières
            ]
        }
    
    def get_movement_history_report(
        self,
        medicament_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Génère un rapport d'historique des mouvements de stock.
        
        Args:
            medicament_id: ID du médicament
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            dict: Données du rapport
        """
        medicament = self._medicament_repo.get_by_id(medicament_id)
        if not medicament:
            return {'error': 'Médicament non trouvé'}
        
        movements = self._movement_repo.get_by_medicament(medicament_id)
        
        # Filtrer par date si spécifié
        if start_date and end_date:
            movements = [
                m for m in movements
                if start_date <= m.created_at.date() <= end_date
            ]
        
        total_entries = sum(m.quantity for m in movements if m.is_entry())
        total_exits = sum(abs(m.quantity) for m in movements if m.is_exit())
        
        return {
            'medicament': {
                'code': medicament.code,
                'name': medicament.name,
                'current_stock': medicament.quantity_in_stock
            },
            'summary': {
                'total_entries': total_entries,
                'total_exits': total_exits,
                'net_change': total_entries - total_exits,
                'movements_count': len(movements)
            },
            'movements': [
                {
                    'date': self._format_datetime(m.created_at) if m.created_at else 'N/A',
                    'type': m.movement_type,
                    'type_label': self._get_movement_type_label(m.movement_type),
                    'quantity': m.quantity,
                    'user': m.user_name,
                    'reason': m.reason or 'N/A'
                }
                for m in movements
            ]
        }
    
    def _get_movement_type_label(self, movement_type: str) -> str:
        """Retourne le libellé d'un type de mouvement."""
        labels = {
            'entry': 'Entrée',
            'exit': 'Sortie',
            'adjustment': 'Ajustement'
        }
        return labels.get(movement_type, movement_type)
    
    def export_sales_report_csv(
        self,
        start_date: date,
        end_date: date
    ) -> str:
        """
        Exporte le rapport de ventes en CSV.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            str: Chemin du fichier généré
        """
        report = self.get_sales_report(start_date, end_date)
        
        export_dir = self._ensure_export_dir()
        filename = f"ventes_{start_date.isoformat()}_{end_date.isoformat()}.csv"
        filepath = os.path.join(export_dir, filename)
        
        # En-têtes
        headers = ['Numéro', 'Date', 'Client', 'Vendeur', 'Total', 'Articles', 'Statut']
        
        # Données
        rows = []
        for sale in report['sales']:
            rows.append([
                sale['sale_number'],
                sale['sale_date'],
                sale['client_name'],
                sale['seller_name'],
                str(sale['total']),
                str(sale['items_count']),
                sale['status']
            ])
        
        # Écriture du fichier
        self._write_csv(filepath, headers, rows)
        
        return filepath
    
    def export_stock_report_csv(self) -> str:
        """
        Exporte le rapport de stock en CSV.
        
        Returns:
            str: Chemin du fichier généré
        """
        report = self.get_stock_report()
        
        export_dir = self._ensure_export_dir()
        filename = f"stock_{date.today().isoformat()}.csv"
        filepath = os.path.join(export_dir, filename)
        
        # En-têtes
        headers = [
            'Code', 'Nom', 'Catégorie', 'Quantité', 
            'Prix Achat', 'Prix Vente', 'Valeur Stock', 'Péremption'
        ]
        
        # Données
        rows = []
        for product in report['all_products']:
            rows.append([
                product['code'],
                product['name'],
                product['category'],
                str(product['quantity']),
                str(product['purchase_price']),
                str(product['selling_price']),
                str(product['stock_value']),
                product['expiration_date']
            ])
        
        # Écriture du fichier
        self._write_csv(filepath, headers, rows)
        
        return filepath
    
    def _write_csv(
        self, 
        filepath: str, 
        headers: List[str], 
        rows: List[List[str]]
    ) -> None:
        """
        Écrit un fichier CSV.
        
        Args:
            filepath: Chemin du fichier
            headers: En-têtes
            rows: Lignes de données
        """
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)
            writer.writerows(rows)
    
    def export_sales_report_pdf(
        self,
        start_date: date,
        end_date: date
    ) -> str:
        """
        Exporte le rapport de ventes en PDF.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            str: Chemin du fichier généré
        """
        report = self.get_sales_report(start_date, end_date)
        
        export_dir = self._ensure_export_dir()
        filename = f"ventes_{start_date.isoformat()}_{end_date.isoformat()}.pdf"
        filepath = os.path.join(export_dir, filename)
        
        # Utiliser le générateur PDF
        from utils.pdf_generator import PDFGenerator
        pdf_gen = PDFGenerator()
        
        pdf_gen.generate_sales_report(report, filepath)
        
        return filepath
    
    def export_stock_report_pdf(self) -> str:
        """
        Exporte le rapport de stock en PDF.
        
        Returns:
            str: Chemin du fichier généré
        """
        report = self.get_stock_report()
        
        export_dir = self._ensure_export_dir()
        filename = f"stock_{date.today().isoformat()}.pdf"
        filepath = os.path.join(export_dir, filename)
        
        # Utiliser le générateur PDF
        from utils.pdf_generator import PDFGenerator
        pdf_gen = PDFGenerator()
        
        pdf_gen.generate_stock_report(report, filepath)
        
        return filepath
    
    @staticmethod
    def get_predefined_periods() -> List[ReportPeriod]:
        """
        Retourne les périodes prédéfinies pour les rapports.
        
        Returns:
            list: Liste des périodes disponibles
        """
        today = date.today()
        
        # Début du mois
        month_start = today.replace(day=1)
        
        # Début de la semaine (lundi)
        week_start = today - timedelta(days=today.weekday())
        
        # Mois précédent
        if today.month == 1:
            prev_month_start = today.replace(year=today.year - 1, month=12, day=1)
        else:
            prev_month_start = today.replace(month=today.month - 1, day=1)
        
        prev_month_end = month_start - timedelta(days=1)
        
        return [
            ReportPeriod(today, today, "Aujourd'hui"),
            ReportPeriod(week_start, today, "Cette semaine"),
            ReportPeriod(month_start, today, "Ce mois"),
            ReportPeriod(prev_month_start, prev_month_end, "Mois précédent"),
            ReportPeriod(
                today - timedelta(days=30), 
                today, 
                "30 derniers jours"
            ),
            ReportPeriod(
                today - timedelta(days=90), 
                today, 
                "90 derniers jours"
            )
        ]