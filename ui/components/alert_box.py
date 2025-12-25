"""
Composants de boîtes de dialogue et alertes.

Auteur: Alsény Camara
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import UI_CONFIG


class AlertBox:
    """
    Classe utilitaire pour afficher des alertes et messages.
    """
    
    @staticmethod
    def show_info(title: str, message: str, parent: tk.Widget = None) -> None:
        """
        Affiche un message d'information.
        
        Args:
            title: Titre de la boîte
            message: Message à afficher
            parent: Widget parent
        """
        messagebox.showinfo(title, message, parent=parent)
    
    @staticmethod
    def show_warning(title: str, message: str, parent: tk.Widget = None) -> None:
        """
        Affiche un avertissement.
        
        Args:
            title: Titre
            message: Message
            parent: Widget parent
        """
        messagebox.showwarning(title, message, parent=parent)
    
    @staticmethod
    def show_error(title: str, message: str, parent: tk.Widget = None) -> None:
        """
        Affiche une erreur.
        
        Args:
            title: Titre
            message: Message
            parent: Widget parent
        """
        messagebox.showerror(title, message, parent=parent)
    
    @staticmethod
    def show_success(title: str, message: str, parent: tk.Widget = None) -> None:
        """
        Affiche un message de succès.
        
        Args:
            title: Titre
            message: Message
            parent: Widget parent
        """
        messagebox.showinfo(title, f"✓ {message}", parent=parent)
    
    @staticmethod
    def ask_yes_no(title: str, message: str, parent: tk.Widget = None) -> bool:
        """
        Affiche une question Oui/Non.
        
        Args:
            title: Titre
            message: Message
            parent: Widget parent
            
        Returns:
            bool: True si Oui
        """
        return messagebox.askyesno(title, message, parent=parent)
    
    @staticmethod
    def ask_ok_cancel(title: str, message: str, parent: tk.Widget = None) -> bool:
        """
        Affiche une question OK/Annuler.
        
        Args:
            title: Titre
            message: Message
            parent: Widget parent
            
        Returns:
            bool: True si OK
        """
        return messagebox.askokcancel(title, message, parent=parent)


class ConfirmDialog(tk.Toplevel):
    """
    Dialogue de confirmation personnalisé.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        message: str,
        confirm_text: str = "Confirmer",
        cancel_text: str = "Annuler",
        confirm_color: str = None,
        icon: str = "warning"
    ):
        """
        Initialise le dialogue.
        
        Args:
            parent: Widget parent
            title: Titre
            message: Message
            confirm_text: Texte du bouton de confirmation
            cancel_text: Texte du bouton d'annulation
            confirm_color: Couleur du bouton de confirmation
            icon: Type d'icône ('warning', 'error', 'info', 'question')
        """
        super().__init__(parent)
        
        self.title(title)
        self.result = False
        
        self._message = message
        self._confirm_text = confirm_text
        self._cancel_text = cancel_text
        self._confirm_color = confirm_color or UI_CONFIG['danger_color']
        self._icon = icon
        
        self._create_widgets()
        self._center_window()
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Attendre la fermeture
        self.wait_window()
    
    def _create_widgets(self) -> None:
        """Crée les widgets."""
        self.configure(padx=20, pady=20)
        
        # Frame contenu
        content_frame = ttk.Frame(self)
        content_frame.pack(fill='both', expand=True)
        
        # Icône + Message
        icon_text = {
            'warning': '⚠️',
            'error': '❌',
            'info': 'ℹ️',
            'question': '❓'
        }.get(self._icon, '❓')
        
        ttk.Label(
            content_frame,
            text=icon_text,
            font=('Segoe UI Emoji', 32)
        ).pack(pady=(0, 10))
        
        ttk.Label(
            content_frame,
            text=self._message,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            wraplength=300,
            justify='center'
        ).pack(pady=(0, 20))
        
        # Boutons
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack()
        
        cancel_btn = ttk.Button(
            btn_frame,
            text=self._cancel_text,
            command=self._on_cancel,
            width=12
        )
        cancel_btn.pack(side='left', padx=5)
        
        confirm_btn = tk.Button(
            btn_frame,
            text=self._confirm_text,
            command=self._on_confirm,
            width=12,
            bg=self._confirm_color,
            fg='white',
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            relief='flat',
            cursor='hand2'
        )
        confirm_btn.pack(side='left', padx=5)
        
        # Raccourcis clavier
        self.bind('<Return>', lambda e: self._on_confirm())
        self.bind('<Escape>', lambda e: self._on_cancel())
    
    def _center_window(self) -> None:
        """Centre la fenêtre."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width < 350:
            width = 350
        if height < 200:
            height = 200
        
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.resizable(False, False)
    
    def _on_confirm(self) -> None:
        """Action de confirmation."""
        self.result = True
        self.destroy()
    
    def _on_cancel(self) -> None:
        """Action d'annulation."""
        self.result = False
        self.destroy()


class InputDialog(tk.Toplevel):
    """
    Dialogue de saisie personnalisé.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        prompt: str,
        initial_value: str = "",
        input_type: str = "text",
        validate: Callable[[str], tuple] = None
    ):
        """
        Initialise le dialogue.
        
        Args:
            parent: Widget parent
            title: Titre
            prompt: Message/question
            initial_value: Valeur initiale
            input_type: Type ('text', 'password', 'number')
            validate: Fonction de validation (value) -> (bool, message)
        """
        super().__init__(parent)
        
        self.title(title)
        self.result: Optional[str] = None
        
        self._prompt = prompt
        self._initial_value = initial_value
        self._input_type = input_type
        self._validate = validate
        
        self._create_widgets()
        self._center_window()
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Focus
        self._entry.focus_set()
        self._entry.select_range(0, tk.END)
        
        # Attendre
        self.wait_window()
    
    def _create_widgets(self) -> None:
        """Crée les widgets."""
        self.configure(padx=20, pady=20)
        
        # Prompt
        ttk.Label(
            self,
            text=self._prompt,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(anchor='w', pady=(0, 5))
        
        # Entry
        self._var = tk.StringVar(value=self._initial_value)
        
        show = '*' if self._input_type == 'password' else ''
        
        self._entry = ttk.Entry(
            self,
            textvariable=self._var,
            width=40,
            show=show
        )
        self._entry.pack(fill='x', pady=(0, 5))
        
        # Message d'erreur
        self._error_var = tk.StringVar()
        ttk.Label(
            self,
            textvariable=self._error_var,
            foreground=UI_CONFIG['danger_color'],
            font=(UI_CONFIG['font_family'], 9)
        ).pack(anchor='w', pady=(0, 10))
        
        # Boutons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x')
        
        ttk.Button(
            btn_frame,
            text="Annuler",
            command=self._on_cancel,
            width=12
        ).pack(side='right', padx=(5, 0))
        
        ttk.Button(
            btn_frame,
            text="OK",
            command=self._on_ok,
            width=12
        ).pack(side='right')
        
        # Raccourcis
        self.bind('<Return>', lambda e: self._on_ok())
        self.bind('<Escape>', lambda e: self._on_cancel())
    
    def _center_window(self) -> None:
        """Centre la fenêtre."""
        self.update_idletasks()
        width = max(400, self.winfo_width())
        height = max(150, self.winfo_height())
        
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.resizable(False, False)
    
    def _on_ok(self) -> None:
        """Valide la saisie."""
        value = self._var.get().strip()
        
        # Validation de type
        if self._input_type == 'number':
            try:
                float(value)
            except ValueError:
                self._error_var.set("Veuillez entrer un nombre valide")
                return
        
        # Validation personnalisée
        if self._validate:
            is_valid, message = self._validate(value)
            if not is_valid:
                self._error_var.set(message)
                return
        
        self.result = value
        self.destroy()
    
    def _on_cancel(self) -> None:
        """Annule la saisie."""
        self.result = None
        self.destroy()