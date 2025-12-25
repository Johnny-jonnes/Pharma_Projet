"""
Contrôleur des rapports et statistiques.

Gère la génération des rapports et exports.

Auteur: Alsény Camara
Version: 1.2
"""

from typing import Tuple, List, Optional
from datetime import date, datetime, timedelta
from services.auth_service import AuthService
from services.stock_service import StockService
from database.sale_repository import SaleRepository
from database.medicament_repository import MedicamentRepository
from utils.format_utils import FormatUtils


class ReportController:
    """
    Contrôleur pour les rapports et statistiques.
    """
    
    def __init__(self):
        """Initialise le contrôleur."""
        self._stock_service = StockService()
        self._sale_repo = SaleRepository()
        self._medicament_repo = MedicamentRepository()
    
    def _check_permission(self) -> Tuple[bool, str]:
        """Vérifie les permissions de consultation des rapports."""
        current = AuthService.get_current_user()
        
        if current is None:
            return False, "Utilisateur non connecté"
        
        if not current.can_view_reports():
            return False, "Permission refusée"
        
        return True, ""
    
    def get_users_for_filter(self) -> List[Tuple[int, str]]:
        """
        Récupère la liste des utilisateurs pour le filtre.
        
        Returns:
            List[Tuple[int, str]]: Liste (id, nom)
        """
        from database.user_repository import UserRepository
        user_repo = UserRepository()
        users = user_repo.get_all()
        return [(u.id, u.full_name) for u in users]
    
    def get_dashboard_data(self) -> Tuple[bool, str, dict]:
        """
        Récupère les données pour le tableau de bord.
        
        Returns:
            Tuple[bool, str, dict]: (succès, message, données)
        """
        current = AuthService.get_current_user()
        if current is None:
            return False, "Utilisateur non connecté", {}
        
        # Statistiques stock
        stock_stats = self._stock_service.get_stock_statistics()
        
        # Ventes du jour
        today_total = self._sale_repo.get_daily_total()
        today_count = self._sale_repo.get_daily_count()
        
        # Médicaments en alerte
        low_stock = self._medicament_repo.get_low_stock()
        expiring = self._medicament_repo.get_expiring_soon()
        
        data = {
            'total_products': stock_stats['total_products'],
            'low_stock_count': stock_stats['low_stock_count'],
            'expiring_count': stock_stats['expiring_soon_count'],
            'stock_value': stock_stats['total_value'],
            'stock_value_display': FormatUtils.format_currency(stock_stats['total_value']),
            'today_sales_total': today_total,
            'today_sales_total_display': FormatUtils.format_currency(today_total),
            'today_sales_count': today_count,
            'low_stock_items': [
                {
                    'name': m.name,
                    'quantity': m.quantity_in_stock,
                    'threshold': m.stock_threshold
                }
                for m in low_stock[:5]
            ],
            'expiring_items': [
                {
                    'name': m.name,
                    'expiration': m.expiration_date.strftime("%d/%m/%Y") if m.expiration_date else "",
                    'days_left': m.days_until_expiry()
                }
                for m in expiring[:5]
            ]
        }
        
        return True, "", data
    
    def get_sales_report(
        self,
        start_date: date,
        end_date: date,
        user_id: Optional[int] = None
    ) -> Tuple[bool, str, dict]:
        """
        Génère un rapport de ventes sur une période.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            user_id: ID de l'utilisateur (optionnel)
            
        Returns:
            Tuple[bool, str, dict]: (succès, message, données)
        """
        allowed, message = self._check_permission()
        if not allowed:
            return False, message, {}
        
        if start_date > end_date:
            return False, "La date de début doit être antérieure à la date de fin", {}
        
        # Récupérer les ventes
        sales = self._sale_repo.get_by_date_range(start_date, end_date)
        
        # Filtrer par utilisateur si spécifié
        if user_id is not None:
            sales = [s for s in sales if s.user_id == user_id]
        
        # Calculer les totaux
        completed_sales = [s for s in sales if s.status == 'completed']
        cancelled_sales = [s for s in sales if s.status == 'cancelled']
        
        total_revenue = sum(s.total for s in completed_sales)
        total_discount = sum(s.discount_amount for s in completed_sales)
        
        data = {
            'period': f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
            'total_sales': len(completed_sales),
            'cancelled_sales': len(cancelled_sales),
            'total_revenue': total_revenue,
            'total_revenue_display': FormatUtils.format_currency(total_revenue),
            'total_discount': total_discount,
            'total_discount_display': FormatUtils.format_currency(total_discount),
            'average_sale': total_revenue / len(completed_sales) if completed_sales else 0,
            'sales': [
                {
                    'number': s.sale_number,
                    'date': s.sale_date.strftime("%d/%m/%Y %H:%M"),
                    'client': s.client_name or "Anonyme",
                    'seller': s.seller_name or "Inconnu",
                    'total': s.total,
                    'total_display': FormatUtils.format_currency(s.total)
                }
                for s in completed_sales
            ]
        }
        
        return True, "", data
    
    def get_sales_by_seller(
        self,
        start_date: date,
        end_date: date
    ) -> Tuple[bool, str, dict]:
        """
        Récupère les ventes groupées par vendeur.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Tuple[bool, str, dict]: (succès, message, données)
        """
        allowed, message = self._check_permission()
        if not allowed:
            return False, message, {}
        
        if start_date > end_date:
            return False, "La date de début doit être antérieure à la date de fin", {}
        
        # Récupérer toutes les ventes
        sales = self._sale_repo.get_by_date_range(start_date, end_date)
        
        # Grouper par vendeur
        sellers_data = {}
        
        for sale in sales:
            if sale.status != 'completed':
                continue
            
            seller_id = sale.user_id
            seller_name = sale.seller_name or "Inconnu"
            
            if seller_id not in sellers_data:
                sellers_data[seller_id] = {
                    'id': seller_id,
                    'name': seller_name,
                    'total_sales': 0,
                    'total_revenue': 0.0,
                    'total_discount': 0.0,
                    'sales': []
                }
            
            sellers_data[seller_id]['total_sales'] += 1
            sellers_data[seller_id]['total_revenue'] += sale.total
            sellers_data[seller_id]['total_discount'] += sale.discount_amount
            sellers_data[seller_id]['sales'].append({
                'number': sale.sale_number,
                'date': sale.sale_date.strftime("%d/%m/%Y %H:%M"),
                'client': sale.client_name or "Anonyme",
                'total': sale.total,
                'total_display': FormatUtils.format_currency(sale.total)
            })
        
        # Convertir en liste et formater
        sellers_list = []
        for seller_id, data in sellers_data.items():
            sellers_list.append({
                'id': data['id'],
                'name': data['name'],
                'total_sales': data['total_sales'],
                'total_revenue': data['total_revenue'],
                'total_revenue_display': FormatUtils.format_currency(data['total_revenue']),
                'total_discount': data['total_discount'],
                'total_discount_display': FormatUtils.format_currency(data['total_discount']),
                'average_sale': data['total_revenue'] / data['total_sales'] if data['total_sales'] > 0 else 0,
                'average_sale_display': FormatUtils.format_currency(
                    data['total_revenue'] / data['total_sales'] if data['total_sales'] > 0 else 0
                ),
                'sales': data['sales']
            })
        
        # Trier par chiffre d'affaires décroissant
        sellers_list.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        # Calculer les totaux globaux
        total_revenue = sum(s['total_revenue'] for s in sellers_list)
        total_sales = sum(s['total_sales'] for s in sellers_list)
        
        result = {
            'period': f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
            'total_revenue': total_revenue,
            'total_revenue_display': FormatUtils.format_currency(total_revenue),
            'total_sales': total_sales,
            'sellers': sellers_list
        }
        
        return True, "", result
    
    def get_products_sold_by_seller(
        self,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> Tuple[bool, str, List[dict]]:
        """
        Récupère les produits vendus par un vendeur avec les détails clients.
        
        Args:
            user_id: ID du vendeur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Tuple[bool, str, List[dict]]: (succès, message, produits)
        """
        allowed, message = self._check_permission()
        if not allowed:
            return False, message, []
        
        # Requête détaillée avec client
        query = """
            SELECT 
                s.sale_number,
                s.sale_date,
                m.code AS product_code,
                m.name AS product_name,
                sl.quantity,
                sl.unit_price,
                sl.line_total,
                COALESCE(c.first_name || ' ' || c.last_name, 'Client anonyme') AS client_name,
                c.phone AS client_phone
            FROM sale_lines sl
            INNER JOIN sales s ON sl.sale_id = s.id
            INNER JOIN medicaments m ON sl.medicament_id = m.id
            LEFT JOIN clients c ON s.client_id = c.id
            WHERE s.user_id = ?
            AND DATE(s.sale_date) BETWEEN ? AND ?
            AND s.status = 'completed'
            ORDER BY s.sale_date DESC, m.name
        """
        
        results = self._sale_repo.db.fetch_all(query, (
            user_id,
            start_date.isoformat(),
            end_date.isoformat()
        ))
        
        products = [
            {
                'sale_number': row['sale_number'],
                'date': datetime.fromisoformat(row['sale_date']).strftime("%d/%m/%Y %H:%M") if row['sale_date'] else "",
                'product_code': row['product_code'],
                'product_name': row['product_name'],
                'quantity': row['quantity'],
                'unit_price': row['unit_price'],
                'unit_price_display': FormatUtils.format_currency(row['unit_price']),
                'line_total': row['line_total'],
                'line_total_display': FormatUtils.format_currency(row['line_total']),
                'client_name': row['client_name'],
                'client_phone': row['client_phone'] or ""
            }
            for row in results
        ]
        
        return True, "", products
    
    def get_stock_report(self) -> Tuple[bool, str, dict]:
        """
        Génère un rapport de l'état du stock.
        
        Returns:
            Tuple[bool, str, dict]: (succès, message, données)
        """
        allowed, message = self._check_permission()
        if not allowed:
            return False, message, {}
        
        medicaments = self._medicament_repo.get_all()
        low_stock = self._medicament_repo.get_low_stock()
        expiring = self._medicament_repo.get_expiring_soon()
        
        try:
            expired = self._medicament_repo.get_expired()
        except AttributeError:
            expired = []
        
        total_value = sum(m.quantity_in_stock * m.purchase_price for m in medicaments)
        
        data = {
            'total_products': len(medicaments),
            'low_stock_count': len(low_stock),
            'expiring_count': len(expiring),
            'expired_count': len(expired),
            'total_value': total_value,
            'total_value_display': FormatUtils.format_currency(total_value),
            'products': [
                {
                    'code': m.code,
                    'name': m.name,
                    'category': m.category or "-",
                    'quantity': m.quantity_in_stock,
                    'threshold': m.stock_threshold,
                    'value': m.quantity_in_stock * m.purchase_price,
                    'value_display': FormatUtils.format_currency(m.quantity_in_stock * m.purchase_price),
                    'status': self._get_stock_status(m)
                }
                for m in medicaments
            ],
            'low_stock_products': [
                {
                    'code': m.code,
                    'name': m.name,
                    'quantity': m.quantity_in_stock,
                    'threshold': m.stock_threshold,
                    'needed': m.stock_threshold - m.quantity_in_stock
                }
                for m in low_stock
            ],
            'expiring_products': [
                {
                    'code': m.code,
                    'name': m.name,
                    'expiration': m.expiration_date.strftime("%d/%m/%Y") if m.expiration_date else "",
                    'days_left': m.days_until_expiry() if hasattr(m, 'days_until_expiry') else 0,
                    'quantity': m.quantity_in_stock
                }
                for m in expiring
            ]
        }
        
        return True, "", data
    
    def _get_stock_status(self, medicament) -> str:
        """Détermine le statut du stock."""
        try:
            if hasattr(medicament, 'is_expired') and medicament.is_expired():
                return "⛔ Périmé"
            if hasattr(medicament, 'is_expiring_soon') and medicament.is_expiring_soon():
                return "⚠️ Expire bientôt"
            if hasattr(medicament, 'is_out_of_stock') and medicament.is_out_of_stock():
                return "❌ Rupture"
            if hasattr(medicament, 'is_low_stock') and medicament.is_low_stock():
                return "⚠️ Stock faible"
            return "✅ OK"
        except Exception:
            return "✅ OK"
    
    def get_top_products(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> Tuple[bool, str, List[dict]]:
        """
        Récupère les produits les plus vendus.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            limit: Nombre maximum de résultats
            
        Returns:
            Tuple[bool, str, List[dict]]: (succès, message, produits)
        """
        allowed, message = self._check_permission()
        if not allowed:
            return False, message, []
        
        products = self._sale_repo.get_top_products(start_date, end_date, limit)
        
        result = [
            {
                'rank': i + 1,
                'code': p['code'],
                'name': p['name'],
                'quantity_sold': p['total_quantity'],
                'revenue': p['total_revenue'],
                'revenue_display': FormatUtils.format_currency(p['total_revenue'])
            }
            for i, p in enumerate(products)
        ]
        
        return True, "", result
    
    # ==================== EXPORTS ====================
    
    def export_sales_csv(
        self,
        start_date: date,
        end_date: date,
        filepath: str
    ) -> Tuple[bool, str]:
        """Exporte les ventes en CSV."""
        from utils.csv_exporter import CSVExporter
        
        allowed, message = self._check_permission()
        if not allowed:
            return False, message
        
        sales = self._sale_repo.get_by_date_range(start_date, end_date)
        
        data = [
            {
                'Numéro': s.sale_number,
                'Date': s.sale_date.strftime("%d/%m/%Y %H:%M"),
                'Client': s.client_name or "Anonyme",
                'Vendeur': s.seller_name or "Inconnu",
                'Sous-total': s.subtotal,
                'Remise': s.discount_amount,
                'Total': s.total,
                'Statut': "Validée" if s.status == 'completed' else "Annulée"
            }
            for s in sales
        ]
        
        try:
            CSVExporter.export(data, filepath)
            return True, f"Export réussi: {filepath}"
        except Exception as e:
            return False, f"Erreur d'export: {str(e)}"
    
    def export_sales_by_seller_csv(
        self,
        start_date: date,
        end_date: date,
        filepath: str
    ) -> Tuple[bool, str]:
        """Exporte les ventes par vendeur en CSV."""
        from utils.csv_exporter import CSVExporter
        
        allowed, message = self._check_permission()
        if not allowed:
            return False, message
        
        success, msg, result = self.get_sales_by_seller(start_date, end_date)
        if not success:
            return False, msg
        
        data = [
            {
                'Vendeur': seller['name'],
                'Nombre de ventes': seller['total_sales'],
                'Chiffre d\'affaires': seller['total_revenue'],
                'Remises accordées': seller['total_discount'],
                'Panier moyen': seller['average_sale']
            }
            for seller in result['sellers']
        ]
        
        try:
            CSVExporter.export(data, filepath)
            return True, f"Export réussi: {filepath}"
        except Exception as e:
            return False, f"Erreur d'export: {str(e)}"
    
    def export_stock_csv(self, filepath: str) -> Tuple[bool, str]:
        """Exporte l'état du stock en CSV."""
        from utils.csv_exporter import CSVExporter
        
        allowed, message = self._check_permission()
        if not allowed:
            return False, message
        
        medicaments = self._medicament_repo.get_all()
        
        data = [
            {
                'Code': m.code,
                'Nom': m.name,
                'Catégorie': m.category or "",
                'Prix achat': m.purchase_price,
                'Prix vente': m.selling_price,
                'Quantité': m.quantity_in_stock,
                'Seuil': m.stock_threshold,
                'Péremption': m.expiration_date.strftime("%d/%m/%Y") if m.expiration_date else "",
                'Valeur stock': m.quantity_in_stock * m.purchase_price
            }
            for m in medicaments
        ]
        
        try:
            CSVExporter.export(data, filepath)
            return True, f"Export réussi: {filepath}"
        except Exception as e:
            return False, f"Erreur d'export: {str(e)}"
    
    def export_top_products_csv(
        self,
        start_date: date,
        end_date: date,
        limit: int,
        filepath: str
    ) -> Tuple[bool, str]:
        """Exporte les top produits en CSV."""
        from utils.csv_exporter import CSVExporter
        
        allowed, message = self._check_permission()
        if not allowed:
            return False, message
        
        products = self._sale_repo.get_top_products(start_date, end_date, limit)
        
        data = [
            {
                'Rang': i + 1,
                'Code': p['code'],
                'Nom': p['name'],
                'Quantité vendue': p['total_quantity'],
                'Chiffre d\'affaires': p['total_revenue']
            }
            for i, p in enumerate(products)
        ]
        
        try:
            CSVExporter.export(data, filepath)
            return True, f"Export réussi: {filepath}"
        except Exception as e:
            return False, f"Erreur d'export: {str(e)}"
        

    def export_complete_sellers_report(
        self,
        start_date: date,
        end_date: date,
        filepath: str
    ) -> Tuple[bool, str]:
        """
        Exporte le rapport complet des ventes par vendeur (résumé + détails).
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            filepath: Chemin du fichier
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        import csv
        
        allowed, message = self._check_permission()
        if not allowed:
            return False, message
        
        # Récupérer les données des vendeurs
        success, msg, sellers_data = self.get_sales_by_seller(start_date, end_date)
        if not success:
            return False, msg
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # ==================== EN-TÊTE DU RAPPORT ====================
                writer.writerow(['RAPPORT COMPLET DES VENTES PAR VENDEUR'])
                writer.writerow([f"Période: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"])
                writer.writerow([f"Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}"])
                writer.writerow([])
                
                # ==================== RÉSUMÉ GLOBAL ====================
                writer.writerow(['=' * 80])
                writer.writerow(['RÉSUMÉ GLOBAL'])
                writer.writerow(['=' * 80])
                writer.writerow([f"Nombre total de ventes: {sellers_data['total_sales']}"])
                writer.writerow([f"Chiffre d'affaires total: {sellers_data['total_revenue_display']}"])
                writer.writerow([])
                
                # ==================== TABLEAU DES VENDEURS ====================
                writer.writerow(['=' * 80])
                writer.writerow(['PERFORMANCE PAR VENDEUR'])
                writer.writerow(['=' * 80])
                writer.writerow([
                    'Vendeur',
                    'Nombre de ventes',
                    'Chiffre d\'affaires',
                    'Remises accordées',
                    'Panier moyen'
                ])
                writer.writerow(['-' * 20] * 5)
                
                for seller in sellers_data['sellers']:
                    writer.writerow([
                        seller['name'],
                        seller['total_sales'],
                        seller['total_revenue_display'],
                        seller['total_discount_display'],
                        seller['average_sale_display']
                    ])
                
                writer.writerow([])
                writer.writerow([])
                
                # ==================== DÉTAIL PAR VENDEUR ====================
                writer.writerow(['=' * 80])
                writer.writerow(['DÉTAIL DES VENTES PAR VENDEUR'])
                writer.writerow(['=' * 80])
                writer.writerow([])
                
                for seller in sellers_data['sellers']:
                    # Récupérer les détails de ce vendeur
                    success_detail, msg_detail, details = self.get_products_sold_by_seller(
                        seller['id'], start_date, end_date
                    )
                    
                    if not success_detail:
                        continue
                    
                    # Titre du vendeur
                    writer.writerow(['-' * 80])
                    writer.writerow([f"VENDEUR: {seller['name']}"])
                    writer.writerow([f"Total: {seller['total_sales']} ventes | CA: {seller['total_revenue_display']}"])
                    writer.writerow(['-' * 80])
                    
                    # En-tête du tableau détaillé
                    writer.writerow([
                        'Date',
                        'N° Vente',
                        'Produit',
                        'Quantité',
                        'Prix unitaire',
                        'Montant',
                        'Client',
                        'Téléphone client'
                    ])
                    
                    # Données
                    for detail in details:
                        writer.writerow([
                            detail.get('date', ''),
                            detail.get('sale_number', ''),
                            detail.get('product_name', ''),
                            detail.get('quantity', ''),
                            detail.get('unit_price_display', ''),
                            detail.get('line_total_display', ''),
                            detail.get('client_name', ''),
                            detail.get('client_phone', '')
                        ])
                    
                    writer.writerow([])
                
                # ==================== FIN DU RAPPORT ====================
                writer.writerow(['=' * 80])
                writer.writerow(['FIN DU RAPPORT'])
                writer.writerow(['=' * 80])
            
            return True, f"Rapport complet exporté avec succès:\n{filepath}"
        
        except Exception as e:
            return False, f"Erreur lors de l'export: {str(e)}"