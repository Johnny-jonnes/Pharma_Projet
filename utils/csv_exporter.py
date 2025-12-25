"""
Exportateur de données au format CSV.

Auteur: Alsény Camara
Version: 1.0
"""

import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


class CSVExporter:
    """
    Classe utilitaire pour l'export de données au format CSV.
    
    Fournit des méthodes pour exporter différents types de données
    vers des fichiers CSV correctement formatés.
    """
    
    # Encodage par défaut
    DEFAULT_ENCODING = 'utf-8-sig'  # Avec BOM pour Excel
    
    # Délimiteur par défaut
    DEFAULT_DELIMITER = ';'  # Adapté pour Excel en français
    
    @staticmethod
    def export(
        data: List[Dict[str, Any]],
        filepath: str,
        columns: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        encoding: str = DEFAULT_ENCODING,
        delimiter: str = DEFAULT_DELIMITER
    ) -> bool:
        """
        Exporte une liste de dictionnaires vers un fichier CSV.
        
        Args:
            data: Liste de dictionnaires à exporter
            filepath: Chemin du fichier de destination
            columns: Liste des colonnes à exporter (ordre)
            headers: Mapping colonne -> en-tête affiché
            encoding: Encodage du fichier
            delimiter: Délimiteur de colonnes
            
        Returns:
            bool: True si export réussi
        """
        if not data:
            return False
        
        try:
            # Créer le répertoire si nécessaire
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Déterminer les colonnes
            if columns is None:
                columns = list(data[0].keys())
            
            # Déterminer les en-têtes
            if headers is None:
                headers = {col: col for col in columns}
            
            with open(filepath, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.writer(csvfile, delimiter=delimiter)
                
                # Écrire les en-têtes
                header_row = [headers.get(col, col) for col in columns]
                writer.writerow(header_row)
                
                # Écrire les données
                for row in data:
                    values = [CSVExporter._format_value(row.get(col, '')) for col in columns]
                    writer.writerow(values)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export CSV: {e}")
            return False
    
    @staticmethod
    def _format_value(value: Any) -> str:
        """
        Formate une valeur pour l'export CSV.
        
        Args:
            value: Valeur à formater
            
        Returns:
            str: Valeur formatée
        """
        if value is None:
            return ""
        
        if isinstance(value, bool):
            return "Oui" if value else "Non"
        
        if isinstance(value, float):
            return f"{value:.2f}"
        
        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y %H:%M")
        
        return str(value)
    
    @staticmethod
    def export_medicaments(
        medicaments: List[Dict[str, Any]],
        filepath: str
    ) -> bool:
        """
        Exporte une liste de médicaments.
        
        Args:
            medicaments: Liste des médicaments
            filepath: Chemin du fichier
            
        Returns:
            bool: True si export réussi
        """
        columns = [
            'code', 'name', 'category', 'manufacturer',
            'purchase_price', 'selling_price', 'quantity_in_stock',
            'stock_threshold', 'expiration_date'
        ]
        
        headers = {
            'code': 'Code',
            'name': 'Nom',
            'category': 'Catégorie',
            'manufacturer': 'Fabricant',
            'purchase_price': 'Prix achat',
            'selling_price': 'Prix vente',
            'quantity_in_stock': 'Stock',
            'stock_threshold': 'Seuil alerte',
            'expiration_date': 'Date péremption'
        }
        
        return CSVExporter.export(
            data=medicaments,
            filepath=filepath,
            columns=columns,
            headers=headers
        )
    
    @staticmethod
    def export_clients(
        clients: List[Dict[str, Any]],
        filepath: str
    ) -> bool:
        """
        Exporte une liste de clients.
        
        Args:
            clients: Liste des clients
            filepath: Chemin du fichier
            
        Returns:
            bool: True si export réussi
        """
        columns = [
            'code', 'last_name', 'first_name', 'phone',
            'email', 'loyalty_points', 'total_spent'
        ]
        
        headers = {
            'code': 'Code',
            'last_name': 'Nom',
            'first_name': 'Prénom',
            'phone': 'Téléphone',
            'email': 'Email',
            'loyalty_points': 'Points fidélité',
            'total_spent': 'Total dépensé'
        }
        
        return CSVExporter.export(
            data=clients,
            filepath=filepath,
            columns=columns,
            headers=headers
        )
    
    @staticmethod
    def export_sales(
        sales: List[Dict[str, Any]],
        filepath: str
    ) -> bool:
        """
        Exporte une liste de ventes.
        
        Args:
            sales: Liste des ventes
            filepath: Chemin du fichier
            
        Returns:
            bool: True si export réussi
        """
        columns = [
            'sale_number', 'sale_date', 'client_name', 'seller_name',
            'subtotal', 'discount_amount', 'total', 'status'
        ]
        
        headers = {
            'sale_number': 'N° Vente',
            'sale_date': 'Date',
            'client_name': 'Client',
            'seller_name': 'Vendeur',
            'subtotal': 'Sous-total',
            'discount_amount': 'Remise',
            'total': 'Total',
            'status': 'Statut'
        }
        
        return CSVExporter.export(
            data=sales,
            filepath=filepath,
            columns=columns,
            headers=headers
        )
    
    @staticmethod
    def export_stock_movements(
        movements: List[Dict[str, Any]],
        filepath: str
    ) -> bool:
        """
        Exporte une liste de mouvements de stock.
        
        Args:
            movements: Liste des mouvements
            filepath: Chemin du fichier
            
        Returns:
            bool: True si export réussi
        """
        columns = [
            'created_at', 'medicament_name', 'movement_type',
            'quantity', 'user_name', 'reason'
        ]
        
        headers = {
            'created_at': 'Date',
            'medicament_name': 'Médicament',
            'movement_type': 'Type',
            'quantity': 'Quantité',
            'user_name': 'Utilisateur',
            'reason': 'Motif'
        }
        
        return CSVExporter.export(
            data=movements,
            filepath=filepath,
            columns=columns,
            headers=headers
        )