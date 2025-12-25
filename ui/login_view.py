"""
Vue de connexion (Login).

Auteur: Alsény Camara
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import UI_CONFIG
from controllers.auth_controller import AuthController
from ui.components.alert_box import AlertBox


class LoginView(ttk.Frame):
    """
    Vue de l'écran de connexion.
    
    Interface épurée avec:
    - Logo/Titre de l'application
    - Champs identifiant et mot de passe
    - Bouton de connexion
    - Messages d'erreur
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        on_login_success: Callable = None,
        **kwargs
    ):
        """
        Initialise la vue de connexion.
        
        Args:
            parent: Widget parent
            on_login_success: Callback après connexion réussie
        """
        super().__init__(parent, **kwargs)
        
        self._on_login_success = on_login_success
        self._auth_controller = AuthController()
        self._is_destroyed = False
        
        self._create_widgets()
        self._setup_bindings()
    
    def _create_widgets(self) -> None:
        """Crée les widgets de la vue."""
        # Centrer le contenu
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Conteneur principal centré
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0)
        
        # Logo / Titre
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=(0, 30))
        
        # Icône pharmacie
        ttk.Label(
            title_frame,
            text="💊",
            font=('Segoe UI Emoji', 48)
        ).pack()
        
        ttk.Label(
            title_frame,
            text=UI_CONFIG['window_title'],
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_title'], 'bold'),
            foreground=UI_CONFIG['primary_color']
        ).pack(pady=(10, 0))
        
        ttk.Label(
            title_frame,
            text="Connectez-vous pour accéder au système",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            foreground='gray'
        ).pack(pady=(5, 0))
        
        # Formulaire de connexion
        form_frame = ttk.LabelFrame(main_frame, text="Connexion", padding=20)
        form_frame.pack(fill='x', padx=50)
        
        # Champ identifiant
        ttk.Label(
            form_frame,
            text="Identifiant",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(anchor='w', pady=(0, 2))
        
        self._username_var = tk.StringVar()
        self._username_entry = ttk.Entry(
            form_frame,
            textvariable=self._username_var,
            width=35,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        )
        self._username_entry.pack(fill='x', pady=(0, 15))
        
        # Champ mot de passe
        ttk.Label(
            form_frame,
            text="Mot de passe",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(anchor='w', pady=(0, 2))
        
        self._password_var = tk.StringVar()
        self._password_entry = ttk.Entry(
            form_frame,
            textvariable=self._password_var,
            width=35,
            show='•',
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        )
        self._password_entry.pack(fill='x', pady=(0, 10))
        
        # Message d'erreur
        self._error_var = tk.StringVar()
        self._error_label = ttk.Label(
            form_frame,
            textvariable=self._error_var,
            foreground=UI_CONFIG['danger_color'],
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            wraplength=280
        )
        self._error_label.pack(fill='x', pady=(0, 10))
        
        # Bouton de connexion
        self._login_btn = tk.Button(
            form_frame,
            text="Se connecter",
            command=self._handle_login,
            bg=UI_CONFIG['primary_color'],
            fg='white',
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'], 'bold'),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10
        )
        self._login_btn.pack(fill='x', pady=(10, 0))
        
        # Effet hover sur le bouton
        self._login_btn.bind('<Enter>', self._on_btn_enter)
        self._login_btn.bind('<Leave>', self._on_btn_leave)
        
        # Info copyright
        ttk.Label(
            main_frame,
            text="© 2025 - Système de Gestion Pharmacie",
            font=(UI_CONFIG['font_family'], 8),
            foreground='gray'
        ).pack(pady=(30, 0))
    
    def _on_btn_enter(self, event):
        """Effet hover - entrée."""
        if not self._is_destroyed:
            try:
                self._login_btn.configure(bg=UI_CONFIG['secondary_color'])
            except tk.TclError:
                pass
    
    def _on_btn_leave(self, event):
        """Effet hover - sortie."""
        if not self._is_destroyed:
            try:
                self._login_btn.configure(bg=UI_CONFIG['primary_color'])
            except tk.TclError:
                pass
    
    def _setup_bindings(self) -> None:
        """Configure les raccourcis clavier."""
        self._username_entry.bind('<Return>', lambda e: self._password_entry.focus())
        self._password_entry.bind('<Return>', lambda e: self._handle_login())
        
        # Focus initial
        self._username_entry.focus_set()
    
    def _handle_login(self) -> None:
        """Gère la tentative de connexion."""
        username = self._username_var.get()
        password = self._password_var.get()
        
        # Effacer l'erreur précédente
        self._error_var.set("")
        
        # Désactiver le bouton pendant le traitement
        try:
            self._login_btn.configure(state='disabled', text='Connexion...')
            self.update()
        except tk.TclError:
            return
        
        success, message = self._auth_controller.login(username, password)
        
        if success:
            # Connexion réussie - marquer comme détruit avant d'appeler le callback
            self._is_destroyed = True
            if self._on_login_success:
                self._on_login_success(self._auth_controller.get_current_user())
        else:
            # Échec - réactiver le bouton seulement si pas détruit
            if not self._is_destroyed:
                try:
                    self._error_var.set(message)
                    self._password_var.set("")
                    self._password_entry.focus_set()
                    self._login_btn.configure(state='normal', text='Se connecter')
                except tk.TclError:
                    pass
    
    def reset(self) -> None:
        """Réinitialise le formulaire."""
        if not self._is_destroyed:
            try:
                self._username_var.set("")
                self._password_var.set("")
                self._error_var.set("")
                self._username_entry.focus_set()
            except tk.TclError:
                pass
    
    def destroy(self):
        """Surcharge pour marquer la vue comme détruite."""
        self._is_destroyed = True
        super().destroy()