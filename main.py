"""
Point d'entrée principal de l'application Pharmacie.

Auteur: Alsény Camara
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import UI_CONFIG
from models.user import User
from ui.login_view import LoginView
from ui.main_window import MainWindow


class PharmacyApp:
    """
    Classe principale de l'application.
    """
    
    def __init__(self):
        """Initialise l'application."""
        self._root = tk.Tk()
        self._setup_styles()
        self._current_view = None
        
        # Afficher l'écran de login
        self._show_login()
    
    def _setup_styles(self) -> None:
        """Configure les styles ttk."""
        style = ttk.Style()
        
        # Thème
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')
        
        # Styles personnalisés
        style.configure(
            'TLabel',
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        )
        
        style.configure(
            'TButton',
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            padding=5
        )
        
        style.configure(
            'TEntry',
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            padding=5
        )
        
        style.configure(
            'TLabelframe.Label',
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'], 'bold')
        )
        
        style.configure(
            'TNotebook.Tab',
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            padding=[10, 5]
        )
    
    def _center_window(self, width: int, height: int) -> None:
        """Centre la fenêtre sur l'écran."""
        # Forcer la mise à jour pour obtenir les bonnes dimensions
        self._root.update_idletasks()
        
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self._root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _clear_view(self) -> None:
        """Supprime la vue actuelle."""
        if self._current_view:
            self._current_view.destroy()
            self._current_view = None
    
    def _show_login(self) -> None:
        """Affiche l'écran de connexion."""
        self._clear_view()
        
        # Configuration de la fenêtre pour le login
        self._root.title(UI_CONFIG['window_title'])
        self._root.resizable(False, False)
        self._root.configure(bg=UI_CONFIG['background_color'])
        
        # Configurer le grid
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        
        # Définir la taille et centrer AVANT d'afficher
        login_width = 450
        login_height = 520
        self._root.geometry(f"{login_width}x{login_height}")
        
        # Centrer la fenêtre
        self._root.update_idletasks()
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()
        x = (screen_width - login_width) // 2
        y = (screen_height - login_height) // 2
        self._root.geometry(f"{login_width}x{login_height}+{x}+{y}")
        
        # Icône (si disponible)
        try:
            icon_path = os.path.join(
                os.path.dirname(__file__),
                'assets', 'icons', 'app_icon.ico'
            )
            if os.path.exists(icon_path):
                self._root.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Gérer la fermeture
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Créer la vue de login
        self._current_view = LoginView(
            self._root,
            on_login_success=self._on_login_success
        )
        self._current_view.grid(row=0, column=0, sticky='nsew')
    
    def _on_login_success(self, user: User) -> None:
        """Callback après connexion réussie."""
        self._show_main_window(user)
    
    def _show_main_window(self, user: User) -> None:
        """Affiche la fenêtre principale."""
        self._clear_view()
        
        # Reconfigurer la fenêtre
        self._root.resizable(True, True)
        
        # Définir la taille minimale
        self._root.minsize(
            UI_CONFIG['window_min_width'],
            UI_CONFIG['window_min_height']
        )
        
        # Centrer avec la nouvelle taille
        self._center_window(1280, 800)
        
        # Maximiser si possible
        try:
            self._root.state('zoomed')  # Windows
        except Exception:
            try:
                self._root.attributes('-zoomed', True)  # Linux
            except Exception:
                pass
        
        # Créer la vue principale
        self._current_view = MainWindow(
            self._root,
            user=user,
            on_logout=self._on_logout
        )
        self._current_view.grid(row=0, column=0, sticky='nsew')
    
    def _on_logout(self) -> None:
        """Callback après déconnexion."""
        self._show_login()
    
    def _on_close(self) -> None:
        """Gère la fermeture de l'application."""
        from ui.components.alert_box import ConfirmDialog
        
        dialog = ConfirmDialog(
            self._root,
            title="Quitter",
            message="Êtes-vous sûr de vouloir quitter l'application ?",
            confirm_text="Quitter",
            cancel_text="Annuler",
            icon="question"
        )
        
        if dialog.result:
            try:
                from database.database_manager import DatabaseManager
                db = DatabaseManager()
                db.close()
            except Exception:
                pass
            
            self._root.destroy()
    
    def run(self) -> None:
        """Lance l'application."""
        self._root.mainloop()


def main():
    """Point d'entrée."""
    if sys.version_info < (3, 8):
        print("Python 3.8 ou supérieur est requis")
        sys.exit(1)
    
    app = PharmacyApp()
    app.run()


if __name__ == "__main__":
    main()