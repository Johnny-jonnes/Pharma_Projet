"""
Fenêtre principale de l'application.

Auteur: Alsény Camara
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Type

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import UI_CONFIG
from models.user import User
from controllers.auth_controller import AuthController
from ui.components.alert_box import AlertBox, ConfirmDialog


class MainWindow(ttk.Frame):
    """
    Fenêtre principale après connexion.
    
    Structure:
    - Barre latérale de navigation (sidebar)
    - Zone de contenu principale
    - Barre d'état
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        user: User,
        on_logout: callable = None,
        **kwargs
    ):
        """
        Initialise la fenêtre principale.
        
        Args:
            parent: Widget parent
            user: Utilisateur connecté
            on_logout: Callback de déconnexion
        """
        super().__init__(parent, **kwargs)
        
        self._user = user
        self._on_logout = on_logout
        self._auth_controller = AuthController()
        self._current_view: Optional[ttk.Frame] = None
        self._views: Dict[str, ttk.Frame] = {}
        
        self._create_widgets()
        self._create_views()
        self._show_default_view()
    
    def _create_widgets(self) -> None:
        """Crée les widgets de la fenêtre."""
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Sidebar
        self._create_sidebar()
        
        # Zone de contenu
        self._content_frame = ttk.Frame(self)
        self._content_frame.grid(row=0, column=1, sticky='nsew')
        self._content_frame.columnconfigure(0, weight=1)
        self._content_frame.rowconfigure(0, weight=1)
        
        # Barre d'état
        self._create_statusbar()
    
    def _create_sidebar(self) -> None:
        """Crée la barre latérale de navigation."""
        sidebar = tk.Frame(
            self,
            bg=UI_CONFIG['primary_color'],
            width=220
        )
        sidebar.grid(row=0, column=0, sticky='ns')
        sidebar.grid_propagate(False)
        
        # En-tête avec info utilisateur
        header = tk.Frame(sidebar, bg=UI_CONFIG['primary_color'])
        header.pack(fill='x', pady=20, padx=10)
        
        tk.Label(
            header,
            text="💊",
            font=('Segoe UI Emoji', 28),
            bg=UI_CONFIG['primary_color'],
            fg='white'
        ).pack()
        
        tk.Label(
            header,
            text="PHARMACIE",
            font=(UI_CONFIG['font_family'], 14, 'bold'),
            bg=UI_CONFIG['primary_color'],
            fg='white'
        ).pack(pady=(5, 0))
        
        # Séparateur
        tk.Frame(sidebar, bg='white', height=1).pack(fill='x', padx=20, pady=10)
        
        # Info utilisateur
        user_frame = tk.Frame(sidebar, bg=UI_CONFIG['primary_color'])
        user_frame.pack(fill='x', padx=10, pady=(0, 20))
        
        tk.Label(
            user_frame,
            text=f"👤 {self._user.full_name}",
            font=(UI_CONFIG['font_family'], 10),
            bg=UI_CONFIG['primary_color'],
            fg='white',
            anchor='w'
        ).pack(fill='x')
        
        role_display = {
            'admin': 'Administrateur',
            'pharmacien': 'Pharmacien',
            'vendeur': 'Vendeur'
        }.get(self._user.role, self._user.role)
        
        tk.Label(
            user_frame,
            text=f"📋 {role_display}",
            font=(UI_CONFIG['font_family'], 9),
            bg=UI_CONFIG['primary_color'],
            fg='#BDC3C7',
            anchor='w'
        ).pack(fill='x')
        
        # Menu de navigation
        nav_frame = tk.Frame(sidebar, bg=UI_CONFIG['primary_color'])
        nav_frame.pack(fill='both', expand=True, padx=5)
        
        # Définition des menus selon les permissions
        menus = self._get_menu_items()
        
        self._nav_buttons = {}
        
        for menu in menus:
            btn = tk.Button(
                nav_frame,
                text=f"  {menu['icon']}  {menu['label']}",
                font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
                bg=UI_CONFIG['primary_color'],
                fg='white',
                bd=0,
                anchor='w',
                padx=10,
                pady=12,
                cursor='hand2',
                activebackground=UI_CONFIG['secondary_color'],
                activeforeground='white',
                command=lambda v=menu['view']: self._show_view(v)
            )
            btn.pack(fill='x', pady=2)
            
            # Effet hover
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#34495E'))
            btn.bind('<Leave>', lambda e, b=btn: self._reset_button_color(b))
            
            self._nav_buttons[menu['view']] = btn
        
        # Bouton déconnexion en bas
        logout_frame = tk.Frame(sidebar, bg=UI_CONFIG['primary_color'])
        logout_frame.pack(fill='x', side='bottom', pady=20, padx=5)
        
        tk.Frame(sidebar, bg='white', height=1).pack(fill='x', padx=20, side='bottom')
        
        logout_btn = tk.Button(
            logout_frame,
            text="  🚪  Déconnexion",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            bg=UI_CONFIG['danger_color'],
            fg='white',
            bd=0,
            anchor='w',
            padx=10,
            pady=12,
            cursor='hand2',
            command=self._handle_logout
        )
        logout_btn.pack(fill='x')
    
    def _get_menu_items(self) -> list:
        """Retourne les éléments du menu selon le rôle."""
        items = []
        
        # Dashboard (admin, pharmacien)
        if self._user.role in ('admin', 'pharmacien'):
            items.append({
                'icon': '📊',
                'label': 'Tableau de bord',
                'view': 'dashboard'
            })
        
        # Ventes (tous)
        items.append({
            'icon': '🛒',
            'label': 'Point de vente',
            'view': 'sale'
        })
        
        # Médicaments (admin, pharmacien)
        if self._user.role in ('admin', 'pharmacien'):
            items.append({
                'icon': '💊',
                'label': 'Médicaments',
                'view': 'medicament'
            })
        
        # Clients (tous)
        items.append({
            'icon': '👥',
            'label': 'Clients',
            'view': 'client'
        })
        
        # Rapports (admin, pharmacien)
        if self._user.role in ('admin', 'pharmacien'):
            items.append({
                'icon': '📈',
                'label': 'Rapports',
                'view': 'report'
            })
        
        # Utilisateurs (admin uniquement)
        if self._user.role == 'admin':
            items.append({
                'icon': '👤',
                'label': 'Utilisateurs',
                'view': 'user'
            })
        
        return items
    
    def _reset_button_color(self, button: tk.Button) -> None:
        """Réinitialise la couleur d'un bouton."""
        # Vérifier si c'est le bouton actif
        for view_name, btn in self._nav_buttons.items():
            if btn == button:
                if self._current_view_name == view_name:
                    button.configure(bg=UI_CONFIG['secondary_color'])
                else:
                    button.configure(bg=UI_CONFIG['primary_color'])
                return
        button.configure(bg=UI_CONFIG['primary_color'])
    
    def _create_statusbar(self) -> None:
        """Crée la barre d'état."""
        self._statusbar = ttk.Frame(self)
        self._statusbar.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        self._status_var = tk.StringVar(value="Prêt")
        
        ttk.Label(
            self._statusbar,
            textvariable=self._status_var,
            font=(UI_CONFIG['font_family'], 9),
            foreground='gray'
        ).pack(side='left', padx=10, pady=5)
        
        # Date/heure
        import datetime
        date_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        ttk.Label(
            self._statusbar,
            text=date_str,
            font=(UI_CONFIG['font_family'], 9),
            foreground='gray'
        ).pack(side='right', padx=10, pady=5)
    
    def _create_views(self) -> None:
        """Crée les vues de l'application."""
        from ui.dashboard_view import DashboardView
        from ui.sale_view import SaleView
        from ui.medicament_view import MedicamentView
        from ui.client_view import ClientView
        from ui.report_view import ReportView
        from ui.user_view import UserView
        
        # Créer les vues selon les permissions
        if self._user.role in ('admin', 'pharmacien'):
            self._views['dashboard'] = DashboardView(self._content_frame)
        
        self._views['sale'] = SaleView(self._content_frame)
        
        if self._user.role in ('admin', 'pharmacien'):
            self._views['medicament'] = MedicamentView(self._content_frame)
        
        self._views['client'] = ClientView(self._content_frame)
        
        if self._user.role in ('admin', 'pharmacien'):
            self._views['report'] = ReportView(self._content_frame)
        
        if self._user.role == 'admin':
            self._views['user'] = UserView(self._content_frame)
    
    def _show_default_view(self) -> None:
        """Affiche la vue par défaut."""
        if self._user.role in ('admin', 'pharmacien'):
            self._show_view('dashboard')
        else:
            self._show_view('sale')
    
    @property
    def _current_view_name(self) -> str:
        """Retourne le nom de la vue courante."""
        for name, view in self._views.items():
            if view == self._current_view:
                return name
        return ""
    
    def _show_view(self, view_name: str) -> None:
        """
        Affiche une vue.
        
        Args:
            view_name: Nom de la vue
        """
        if view_name not in self._views:
            return
        
        # Cacher la vue courante
        if self._current_view:
            self._current_view.grid_forget()
        
        # Afficher la nouvelle vue
        self._current_view = self._views[view_name]
        self._current_view.grid(row=0, column=0, sticky='nsew')
        
        # Rafraîchir la vue si elle a une méthode refresh
        if hasattr(self._current_view, 'refresh'):
            self._current_view.refresh()
        
        # Mettre à jour les boutons de navigation
        for name, btn in self._nav_buttons.items():
            if name == view_name:
                btn.configure(bg=UI_CONFIG['secondary_color'])
            else:
                btn.configure(bg=UI_CONFIG['primary_color'])
        
        # Mettre à jour la barre d'état
        view_labels = {
            'dashboard': 'Tableau de bord',
            'sale': 'Point de vente',
            'medicament': 'Gestion des médicaments',
            'client': 'Gestion des clients',
            'report': 'Rapports et statistiques',
            'user': 'Gestion des utilisateurs'
        }
        self._status_var.set(f"📍 {view_labels.get(view_name, view_name)}")
    
    def _handle_logout(self) -> None:
        """Gère la déconnexion."""
        dialog = ConfirmDialog(
            self,
            title="Déconnexion",
            message="Êtes-vous sûr de vouloir vous déconnecter ?",
            confirm_text="Déconnexion",
            cancel_text="Annuler",
            confirm_color=UI_CONFIG['danger_color'],
            icon="question"
        )
        
        if dialog.result:
            self._auth_controller.logout()
            if self._on_logout:
                self._on_logout()
    
    def set_status(self, message: str) -> None:
        """Met à jour le message de la barre d'état."""
        self._status_var.set(message)