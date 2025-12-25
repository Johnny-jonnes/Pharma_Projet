"""
Vue du tableau de bord.

Auteur: Alsény Camara
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import UI_CONFIG
from controllers.report_controller import ReportController
from utils.format_utils import FormatUtils


class DashboardView(ttk.Frame):
    """
    Vue du tableau de bord principal.
    
    Affiche:
    - Indicateurs clés (KPI)
    - Alertes stock faible
    - Alertes péremption
    - Ventes du jour
    """
    
    def __init__(self, parent: tk.Widget, **kwargs):
        """
        Initialise le tableau de bord.
        
        Args:
            parent: Widget parent
        """
        super().__init__(parent, **kwargs)
        
        self._report_controller = ReportController()
        
        self._create_widgets()
        self.refresh()
    
    def _create_widgets(self) -> None:
        """Crée les widgets du tableau de bord."""
        # Configuration du grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Titre
        title_frame = ttk.Frame(self)
        title_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=20, pady=(20, 10))
        
        ttk.Label(
            title_frame,
            text="📊 Tableau de Bord",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_title'], 'bold')
        ).pack(side='left')
        
        # Bouton rafraîchir
        refresh_btn = ttk.Button(
            title_frame,
            text="🔄 Actualiser",
            command=self.refresh
        )
        refresh_btn.pack(side='right')
        
        # Zone des KPIs
        self._create_kpi_section()
        
        # Zone des alertes et ventes
        self._create_alerts_section()
    
    def _create_kpi_section(self) -> None:
        """Crée la section des indicateurs clés."""
        kpi_frame = ttk.Frame(self)
        kpi_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=20, pady=10)
        
        # 4 cartes KPI
        kpi_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        # Carte 1: Total médicaments
        self._kpi_total_products = self._create_kpi_card(
            kpi_frame, 0, "💊", "Médicaments", "0", UI_CONFIG['primary_color']
        )
        
        # Carte 2: Stock faible
        self._kpi_low_stock = self._create_kpi_card(
            kpi_frame, 1, "⚠️", "Stock Faible", "0", UI_CONFIG['warning_color']
        )
        
        # Carte 3: Péremption proche
        self._kpi_expiring = self._create_kpi_card(
            kpi_frame, 2, "📅", "Péremption Proche", "0", UI_CONFIG['danger_color']
        )
        
        # Carte 4: Ventes du jour
        self._kpi_today_sales = self._create_kpi_card(
            kpi_frame, 3, "💰", "Ventes du Jour", "0 GNF", UI_CONFIG['success_color']
        )
    
    def _create_kpi_card(
        self,
        parent: tk.Widget,
        column: int,
        icon: str,
        title: str,
        value: str,
        color: str
    ) -> Dict[str, tk.Widget]:
        """
        Crée une carte KPI.
        
        Args:
            parent: Widget parent
            column: Colonne du grid
            icon: Icône emoji
            title: Titre de la carte
            value: Valeur à afficher
            color: Couleur de la bordure
            
        Returns:
            Dict avec les widgets de la carte
        """
        card = tk.Frame(
            parent,
            bg='white',
            highlightbackground=color,
            highlightthickness=3,
            padx=15,
            pady=15
        )
        card.grid(row=0, column=column, padx=10, pady=5, sticky='ew')
        
        # Icône
        icon_label = tk.Label(
            card,
            text=icon,
            font=('Segoe UI Emoji', 24),
            bg='white'
        )
        icon_label.pack()
        
        # Valeur
        value_var = tk.StringVar(value=value)
        value_label = tk.Label(
            card,
            textvariable=value_var,
            font=(UI_CONFIG['font_family'], 18, 'bold'),
            bg='white',
            fg=color
        )
        value_label.pack(pady=(5, 0))
        
        # Titre
        title_label = tk.Label(
            card,
            text=title,
            font=(UI_CONFIG['font_family'], 10),
            bg='white',
            fg='gray'
        )
        title_label.pack()
        
        return {'frame': card, 'value_var': value_var}
    
    def _create_alerts_section(self) -> None:
        """Crée la section des alertes et informations."""
        # Frame gauche: Alertes stock
        left_frame = ttk.LabelFrame(self, text="⚠️ Alertes Stock Faible", padding=10)
        left_frame.grid(row=2, column=0, sticky='nsew', padx=(20, 10), pady=10)
        
        self._low_stock_list = self._create_alert_list(left_frame)
        
        # Frame droite: Alertes péremption
        right_frame = ttk.LabelFrame(self, text="📅 Alertes Péremption", padding=10)
        right_frame.grid(row=2, column=1, sticky='nsew', padx=(10, 20), pady=10)
        
        self._expiring_list = self._create_alert_list(right_frame)
        
        # Frame bas: Ventes du jour
        sales_frame = ttk.LabelFrame(self, text="💰 Résumé des Ventes du Jour", padding=10)
        sales_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=20, pady=(0, 20))
        
        self._create_sales_summary(sales_frame)
    
    def _create_alert_list(self, parent: tk.Widget) -> tk.Listbox:
        """Crée une liste d'alertes."""
        frame = ttk.Frame(parent)
        frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')
        
        listbox = tk.Listbox(
            frame,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            height=6,
            yscrollcommand=scrollbar.set,
            selectmode='browse',
            bg='white',
            relief='flat',
            highlightthickness=1
        )
        listbox.pack(fill='both', expand=True)
        
        scrollbar.config(command=listbox.yview)
        
        return listbox
    
    def _create_sales_summary(self, parent: tk.Widget) -> None:
        """Crée le résumé des ventes."""
        summary_frame = ttk.Frame(parent)
        summary_frame.pack(fill='x')
        
        # Nombre de ventes
        ttk.Label(
            summary_frame,
            text="Nombre de ventes:",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(side='left', padx=(0, 10))
        
        self._sales_count_var = tk.StringVar(value="0")
        ttk.Label(
            summary_frame,
            textvariable=self._sales_count_var,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'], 'bold')
        ).pack(side='left', padx=(0, 30))
        
        # Total
        ttk.Label(
            summary_frame,
            text="Chiffre d'affaires:",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(side='left', padx=(0, 10))
        
        self._sales_total_var = tk.StringVar(value="0 GNF")
        ttk.Label(
            summary_frame,
            textvariable=self._sales_total_var,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_large'], 'bold'),
            foreground=UI_CONFIG['success_color']
        ).pack(side='left')
        
        # Valeur du stock
        ttk.Label(
            summary_frame,
            text="Valeur du stock:",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(side='left', padx=(50, 10))
        
        self._stock_value_var = tk.StringVar(value="0 GNF")
        ttk.Label(
            summary_frame,
            textvariable=self._stock_value_var,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_large'], 'bold'),
            foreground=UI_CONFIG['primary_color']
        ).pack(side='left')
    
    def refresh(self) -> None:
        """Rafraîchit les données du tableau de bord."""
        success, message, data = self._report_controller.get_dashboard_data()
        
        if not success:
            return
        
        # Mettre à jour les KPIs
        self._kpi_total_products['value_var'].set(str(data.get('total_products', 0)))
        self._kpi_low_stock['value_var'].set(str(data.get('low_stock_count', 0)))
        self._kpi_expiring['value_var'].set(str(data.get('expiring_count', 0)))
        self._kpi_today_sales['value_var'].set(data.get('today_sales_total_display', '0 GNF'))
        
        # Mettre à jour la liste des stocks faibles
        self._low_stock_list.delete(0, tk.END)
        for item in data.get('low_stock_items', []):
            text = f"⚠️ {item['name']} - Stock: {item['quantity']}/{item['threshold']}"
            self._low_stock_list.insert(tk.END, text)
        
        if not data.get('low_stock_items'):
            self._low_stock_list.insert(tk.END, "✅ Aucune alerte de stock")
        
        # Mettre à jour la liste des péremptions
        self._expiring_list.delete(0, tk.END)
        for item in data.get('expiring_items', []):
            days = item.get('days_left', 0)
            if days <= 7:
                icon = "🔴"
            elif days <= 15:
                icon = "🟠"
            else:
                icon = "🟡"
            text = f"{icon} {item['name']} - Expire: {item['expiration']} ({days}j)"
            self._expiring_list.insert(tk.END, text)
        
        if not data.get('expiring_items'):
            self._expiring_list.insert(tk.END, "✅ Aucune alerte de péremption")
        
        # Mettre à jour le résumé des ventes
        self._sales_count_var.set(str(data.get('today_sales_count', 0)))
        self._sales_total_var.set(data.get('today_sales_total_display', '0 GNF'))
        self._stock_value_var.set(data.get('stock_value_display', '0 GNF'))