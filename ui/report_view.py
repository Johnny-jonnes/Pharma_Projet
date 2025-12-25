"""
Vue des rapports et statistiques.

Auteur: Alsény Camara
Version: 1.5
"""

import tkinter as tk
from tkinter import ttk, filedialog
from datetime import date, timedelta
from typing import Optional, List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import UI_CONFIG
from controllers.report_controller import ReportController
from ui.components.data_table import DataTable
from ui.components.form_field import FormDatePicker
from ui.components.alert_box import AlertBox


class ReportView(ttk.Frame):
    """
    Vue des rapports et statistiques.
    """
    
    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, **kwargs)
        
        self._controller = ReportController()
        self._sellers_data: List[dict] = []
        self._current_seller_details: List[dict] = []
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Crée les widgets."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_tabs()
    
    def _create_header(self) -> None:
        """Crée l'en-tête."""
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky='ew', padx=20, pady=(20, 10))
        
        ttk.Label(
            header,
            text="📈 Rapports et Statistiques",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_title'], 'bold')
        ).pack(side='left')
    
    def _create_tabs(self) -> None:
        """Crée les onglets de rapports."""
        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0, 20))
        
        # Onglet Ventes par Vendeur
        self._sellers_tab = self._create_sellers_tab(notebook)
        notebook.add(self._sellers_tab, text="👤 Ventes par Vendeur")
        
        # Onglet Stock
        self._stock_tab = self._create_stock_tab(notebook)
        notebook.add(self._stock_tab, text="📦 Stock")
        
        # Onglet Top Produits
        self._top_tab = self._create_top_products_tab(notebook)
        notebook.add(self._top_tab, text="🏆 Top Produits")
    
    def _create_sellers_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        """Crée l'onglet des ventes par vendeur."""
        tab = ttk.Frame(parent, padding=15)
        tab.columnconfigure(0, weight=1, minsize=300)
        tab.columnconfigure(1, weight=3, minsize=600)
        tab.rowconfigure(2, weight=1)
        
        # ==================== FILTRES ====================
        filter_frame = ttk.LabelFrame(tab, text="📅 Période", padding=15)
        filter_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        
        dates_frame = ttk.Frame(filter_frame)
        dates_frame.pack(fill='x')
        
        # Date début
        ttk.Label(
            dates_frame, 
            text="Du:",
            font=(UI_CONFIG['font_family'], 10, 'bold')
        ).pack(side='left', padx=(0, 10))
        
        self._sellers_start_date = FormDatePicker(dates_frame, label="")
        self._sellers_start_date.pack(side='left', padx=(0, 30))
        self._sellers_start_date.set_value(date.today() - timedelta(days=30))
        
        # Date fin
        ttk.Label(
            dates_frame, 
            text="Au:",
            font=(UI_CONFIG['font_family'], 10, 'bold')
        ).pack(side='left', padx=(0, 10))
        
        self._sellers_end_date = FormDatePicker(dates_frame, label="")
        self._sellers_end_date.pack(side='left', padx=(0, 30))
        self._sellers_end_date.set_value(date.today())
        
        # Boutons
        ttk.Button(
            dates_frame,
            text="🔍 Générer le rapport",
            command=self._generate_sellers_report
        ).pack(side='left', padx=15)
        
        ttk.Button(
            dates_frame,
            text="📥 Exporter tout en CSV",
            command=self._export_complete_report
        ).pack(side='right', padx=5)
        
        # ==================== RÉSUMÉ GLOBAL ====================
        summary_frame = ttk.LabelFrame(tab, text="📊 Résumé global", padding=15)
        summary_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        
        self._sellers_summary_var = tk.StringVar(value="Cliquez sur 'Générer le rapport' pour afficher les statistiques")
        ttk.Label(
            summary_frame,
            textvariable=self._sellers_summary_var,
            font=(UI_CONFIG['font_family'], 11)
        ).pack(anchor='w')
        
        # ==================== LISTE DES VENDEURS ====================
        left_frame = ttk.LabelFrame(tab, text="👤 Performance des vendeurs", padding=10)
        left_frame.grid(row=2, column=0, sticky='nsew', padx=(0, 10), pady=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        sellers_columns = [
            {'key': 'name', 'label': 'Vendeur', 'width': 120},
            {'key': 'total_sales', 'label': 'Nb Ventes', 'width': 70, 'anchor': 'center'},
            {'key': 'total_revenue_display', 'label': 'Chiffre d\'affaires', 'width': 110, 'anchor': 'e'}
        ]
        
        self._sellers_table = DataTable(
            left_frame,
            columns=sellers_columns,
            show_search=False,
            on_select=self._on_seller_select,
            height=18
        )
        self._sellers_table.grid(row=0, column=0, sticky='nsew')
        
        # ==================== DÉTAIL DES VENTES ====================
        right_frame = ttk.LabelFrame(tab, text="📋 Détail des ventes", padding=10)
        right_frame.grid(row=2, column=1, sticky='nsew', padx=(10, 0), pady=(0, 5))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Info vendeur sélectionné
        info_frame = ttk.Frame(right_frame)
        info_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        self._seller_info_var = tk.StringVar(value="← Sélectionnez un vendeur dans la liste pour voir ses ventes détaillées")
        ttk.Label(
            info_frame,
            textvariable=self._seller_info_var,
            font=(UI_CONFIG['font_family'], 11, 'bold'),
            foreground=UI_CONFIG['primary_color'],
            wraplength=600
        ).pack(side='left', fill='x', expand=True)
        
        # Tableau des ventes détaillées
        detail_columns = [
            {'key': 'date', 'label': 'Date/Heure', 'width': 110},
            {'key': 'sale_number', 'label': 'N° Vente', 'width': 100},
            {'key': 'product_name', 'label': 'Produit vendu', 'width': 180},
            {'key': 'quantity', 'label': 'Qté', 'width': 50, 'anchor': 'center'},
            {'key': 'line_total_display', 'label': 'Montant', 'width': 100, 'anchor': 'e'},
            {'key': 'client_name', 'label': 'Client', 'width': 140},
            {'key': 'client_phone', 'label': 'Téléphone', 'width': 100}
        ]
        
        self._seller_detail_table = DataTable(
            right_frame,
            columns=detail_columns,
            show_search=True,
            height=18
        )
        self._seller_detail_table.grid(row=1, column=0, sticky='nsew')
        
        return tab
    
    def _create_stock_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        """Crée l'onglet du stock."""
        tab = ttk.Frame(parent, padding=15)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)
        
        # Actions
        actions_frame = ttk.Frame(tab)
        actions_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        
        ttk.Button(
            actions_frame,
            text="🔍 Actualiser",
            command=self._generate_stock_report
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            actions_frame,
            text="📥 Exporter CSV",
            command=self._export_stock_csv
        ).pack(side='left', padx=5)
        
        # Résumé
        self._stock_summary_frame = ttk.LabelFrame(tab, text="📊 Résumé du stock", padding=15)
        self._stock_summary_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        
        summary_grid = ttk.Frame(self._stock_summary_frame)
        summary_grid.pack(fill='x')
        
        self._stock_total_var = tk.StringVar(value="0")
        self._stock_low_var = tk.StringVar(value="0")
        self._stock_expiring_var = tk.StringVar(value="0")
        self._stock_value_var = tk.StringVar(value="0 GNF")
        
        indicators = [
            ("Total produits:", self._stock_total_var, UI_CONFIG['primary_color']),
            ("Stock faible:", self._stock_low_var, UI_CONFIG['warning_color']),
            ("Péremption proche:", self._stock_expiring_var, UI_CONFIG['danger_color']),
            ("Valeur totale:", self._stock_value_var, UI_CONFIG['success_color'])
        ]
        
        for label, var, color in indicators:
            frame = ttk.Frame(summary_grid)
            frame.pack(side='left', padx=30, pady=10)
            
            ttk.Label(
                frame, 
                text=label,
                font=(UI_CONFIG['font_family'], 10)
            ).pack()
            ttk.Label(
                frame,
                textvariable=var,
                font=(UI_CONFIG['font_family'], 16, 'bold'),
                foreground=color
            ).pack()
        
        # Tableau
        columns = [
            {'key': 'code', 'label': 'Code', 'width': 90},
            {'key': 'name', 'label': 'Nom du produit', 'width': 200},
            {'key': 'category', 'label': 'Catégorie', 'width': 120},
            {'key': 'quantity', 'label': 'Quantité', 'width': 80, 'anchor': 'center'},
            {'key': 'value_display', 'label': 'Valeur stock', 'width': 120, 'anchor': 'e'},
            {'key': 'status', 'label': 'Statut', 'width': 120, 'anchor': 'center'}
        ]
        
        self._stock_table = DataTable(
            tab,
            columns=columns,
            show_search=True,
            height=12
        )
        self._stock_table.grid(row=2, column=0, sticky='nsew')
        
        return tab
    
    def _create_top_products_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        """Crée l'onglet des top produits."""
        tab = ttk.Frame(parent, padding=15)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        
        # Filtres
        filter_frame = ttk.LabelFrame(tab, text="📅 Période", padding=15)
        filter_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        
        dates_frame = ttk.Frame(filter_frame)
        dates_frame.pack(fill='x')
        
        ttk.Label(
            dates_frame, 
            text="Du:",
            font=(UI_CONFIG['font_family'], 10, 'bold')
        ).pack(side='left', padx=(0, 10))
        
        self._top_start_date = FormDatePicker(dates_frame, label="")
        self._top_start_date.pack(side='left', padx=(0, 30))
        self._top_start_date.set_value(date.today() - timedelta(days=30))
        
        ttk.Label(
            dates_frame, 
            text="Au:",
            font=(UI_CONFIG['font_family'], 10, 'bold')
        ).pack(side='left', padx=(0, 10))
        
        self._top_end_date = FormDatePicker(dates_frame, label="")
        self._top_end_date.pack(side='left', padx=(0, 30))
        self._top_end_date.set_value(date.today())
        
        ttk.Label(
            dates_frame, 
            text="Nombre:",
            font=(UI_CONFIG['font_family'], 10, 'bold')
        ).pack(side='left', padx=(20, 10))
        
        self._top_limit_var = tk.StringVar(value="10")
        top_combo = ttk.Combobox(
            dates_frame,
            textvariable=self._top_limit_var,
            values=["5", "10", "20", "50", "100"],
            state='readonly',
            width=6
        )
        top_combo.pack(side='left', padx=(0, 30))
        
        ttk.Button(
            dates_frame,
            text="🔍 Générer",
            command=self._generate_top_products
        ).pack(side='left', padx=15)
        
        ttk.Button(
            dates_frame,
            text="📥 Exporter CSV",
            command=self._export_top_products_csv
        ).pack(side='right', padx=5)
        
        # Tableau
        columns = [
            {'key': 'rank', 'label': 'Rang', 'width': 60, 'anchor': 'center'},
            {'key': 'code', 'label': 'Code', 'width': 100},
            {'key': 'name', 'label': 'Nom du produit', 'width': 250},
            {'key': 'quantity_sold', 'label': 'Quantité vendue', 'width': 120, 'anchor': 'center'},
            {'key': 'revenue_display', 'label': 'Chiffre d\'affaires', 'width': 150, 'anchor': 'e'}
        ]
        
        self._top_table = DataTable(
            tab,
            columns=columns,
            show_search=False,
            height=15
        )
        self._top_table.grid(row=1, column=0, sticky='nsew')
        
        return tab
    
    # ==================== GÉNÉRATION DES RAPPORTS ====================
    
    def _generate_sellers_report(self) -> None:
        """Génère le rapport par vendeur."""
        start = self._sellers_start_date.get_value()
        end = self._sellers_end_date.get_value()
        
        if not start or not end:
            AlertBox.show_warning("Attention", "Veuillez sélectionner les dates de début et de fin", self)
            return
        
        try:
            success, message, data = self._controller.get_sales_by_seller(start, end)
        except AttributeError as e:
            AlertBox.show_error("Erreur", f"Méthode non disponible: {e}", self)
            return
        
        if not success:
            AlertBox.show_error("Erreur", message, self)
            return
        
        # Résumé global
        summary = (
            f"📅 Période: {data['period']}  |  "
            f"🛒 Total ventes: {data['total_sales']}  |  "
            f"💰 CA global: {data['total_revenue_display']}"
        )
        self._sellers_summary_var.set(summary)
        
        # Stocker les données
        self._sellers_data = data['sellers']
        
        # Charger le tableau des vendeurs
        self._sellers_table.load_data(data['sellers'])
        
        # Vider le détail
        self._seller_info_var.set("← Sélectionnez un vendeur dans la liste pour voir ses ventes détaillées")
        self._seller_detail_table.load_data([])
        self._current_seller_details = []
    
    def _on_seller_select(self, item: dict) -> None:
        """Gère la sélection d'un vendeur - affiche les ventes détaillées."""
        if not item:
            return
        
        seller_id = item.get('id')
        seller_name = item.get('name', 'Inconnu')
        
        # Récupérer les dates
        start = self._sellers_start_date.get_value()
        end = self._sellers_end_date.get_value()
        
        if not start or not end:
            return
        
        # Afficher info vendeur
        seller_data = None
        for s in self._sellers_data:
            if s['id'] == seller_id:
                seller_data = s
                break
        
        if seller_data:
            self._seller_info_var.set(
                f"👤 {seller_name}  |  "
                f"🛒 {seller_data['total_sales']} ventes  |  "
                f"💰 CA: {seller_data['total_revenue_display']}  |  "
                f"🛍️ Panier moyen: {seller_data['average_sale_display']}"
            )
        
        # Récupérer les ventes détaillées
        try:
            success, message, details = self._controller.get_products_sold_by_seller(
                seller_id, start, end
            )
            
            if success:
                self._current_seller_details = details
                self._seller_detail_table.load_data(details)
            else:
                AlertBox.show_error("Erreur", message, self)
        except AttributeError as e:
            AlertBox.show_error("Erreur", f"Méthode non disponible: {e}", self)
    
    def _generate_stock_report(self) -> None:
        """Génère le rapport du stock."""
        success, message, data = self._controller.get_stock_report()
        
        if not success:
            AlertBox.show_error("Erreur", message, self)
            return
        
        self._stock_total_var.set(str(data['total_products']))
        self._stock_low_var.set(str(data['low_stock_count']))
        self._stock_expiring_var.set(str(data['expiring_count']))
        self._stock_value_var.set(data['total_value_display'])
        
        self._stock_table.load_data(data['products'])
    
    def _generate_top_products(self) -> None:
        """Génère le rapport des top produits."""
        start = self._top_start_date.get_value()
        end = self._top_end_date.get_value()
        
        if not start or not end:
            AlertBox.show_warning("Attention", "Veuillez sélectionner les dates", self)
            return
        
        limit = int(self._top_limit_var.get())
        
        success, message, data = self._controller.get_top_products(start, end, limit)
        
        if not success:
            AlertBox.show_error("Erreur", message, self)
            return
        
        self._top_table.load_data(data)
    
    # ==================== EXPORTS ====================
    
    def _export_complete_report(self) -> None:
        """Exporte le rapport complet (vendeurs + détails) en CSV."""
        start = self._sellers_start_date.get_value()
        end = self._sellers_end_date.get_value()
        
        if not start or not end:
            AlertBox.show_warning("Attention", "Veuillez d'abord générer un rapport", self)
            return
        
        if not self._sellers_data:
            AlertBox.show_warning("Attention", "Aucune donnée à exporter. Générez d'abord le rapport.", self)
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfile=f"rapport_complet_vendeurs_{start}_{end}.csv"
        )
        
        if filepath:
            try:
                success, message = self._controller.export_complete_sellers_report(
                    start, end, filepath
                )
                
                if success:
                    AlertBox.show_success("Succès", message, self)
                else:
                    AlertBox.show_error("Erreur", message, self)
            except AttributeError:
                AlertBox.show_error("Erreur", "Fonction d'export non disponible. Mettez à jour le contrôleur.", self)
    
    def _export_stock_csv(self) -> None:
        """Exporte le stock en CSV."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfile=f"stock_{date.today()}.csv"
        )
        
        if filepath:
            success, message = self._controller.export_stock_csv(filepath)
            
            if success:
                AlertBox.show_success("Succès", message, self)
            else:
                AlertBox.show_error("Erreur", message, self)
    
    def _export_top_products_csv(self) -> None:
        """Exporte les top produits en CSV."""
        start = self._top_start_date.get_value()
        end = self._top_end_date.get_value()
        
        if not start or not end:
            AlertBox.show_warning("Attention", "Veuillez d'abord générer un rapport", self)
            return
        
        limit = int(self._top_limit_var.get())
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfile=f"top_produits_{start}_{end}.csv"
        )
        
        if filepath:
            try:
                success, message = self._controller.export_top_products_csv(start, end, limit, filepath)
                
                if success:
                    AlertBox.show_success("Succès", message, self)
                else:
                    AlertBox.show_error("Erreur", message, self)
            except AttributeError:
                AlertBox.show_error("Erreur", "Fonction d'export non disponible", self)
    
    def refresh(self) -> None:
        """Rafraîchit la vue."""
        self._generate_stock_report()