"""
Composants de champs de formulaire réutilisables.

Auteur: Alsény Camara
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk
from datetime import date, datetime
from typing import Optional, List, Tuple, Callable, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import UI_CONFIG


class FormField(ttk.Frame):
    """
    Classe de base pour les champs de formulaire.
    
    Fournit un conteneur avec label et widget d'entrée.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        required: bool = False,
        **kwargs
    ):
        """
        Initialise le champ de formulaire.
        
        Args:
            parent: Widget parent
            label: Libellé du champ
            required: Champ obligatoire
        """
        super().__init__(parent)
        
        self._label_text = label
        self._required = required
        self._error_var = tk.StringVar()
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Crée les widgets du champ."""
        # Label
        label_text = self._label_text
        if self._required:
            label_text += " *"
        
        self._label = ttk.Label(
            self,
            text=label_text,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        )
        self._label.pack(anchor='w', pady=(0, 2))
        
        # Conteneur pour le widget d'entrée
        self._input_frame = ttk.Frame(self)
        self._input_frame.pack(fill='x')
        
        # Label d'erreur
        self._error_label = ttk.Label(
            self,
            textvariable=self._error_var,
            foreground=UI_CONFIG['danger_color'],
            font=(UI_CONFIG['font_family'], 8)
        )
        self._error_label.pack(anchor='w')
    
    def set_error(self, message: str) -> None:
        """Affiche un message d'erreur."""
        self._error_var.set(message)
    
    def clear_error(self) -> None:
        """Efface le message d'erreur."""
        self._error_var.set("")
    
    def get_value(self) -> Any:
        """Retourne la valeur du champ (à implémenter)."""
        raise NotImplementedError
    
    def set_value(self, value: Any) -> None:
        """Définit la valeur du champ (à implémenter)."""
        raise NotImplementedError
    
    def clear(self) -> None:
        """Efface le champ (à implémenter)."""
        raise NotImplementedError
    
    def set_enabled(self, enabled: bool) -> None:
        """Active/désactive le champ (à implémenter)."""
        raise NotImplementedError


class FormEntry(FormField):
    """Champ de saisie texte simple."""
    
    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        required: bool = False,
        show: str = None,
        width: int = 30,
        placeholder: str = "",
        validate_callback: Callable[[str], Tuple[bool, str]] = None,
        **kwargs
    ):
        """
        Initialise le champ de saisie.
        
        Args:
            parent: Widget parent
            label: Libellé
            required: Obligatoire
            show: Caractère de masquage (pour mots de passe)
            width: Largeur en caractères
            placeholder: Texte indicatif
            validate_callback: Fonction de validation
        """
        self._show = show
        self._width = width
        self._placeholder = placeholder
        self._validate_callback = validate_callback
        self._var = tk.StringVar()
        
        super().__init__(parent, label, required, **kwargs)
    
    def _create_widgets(self) -> None:
        """Crée les widgets."""
        super()._create_widgets()
        
        # Entry
        self._entry = ttk.Entry(
            self._input_frame,
            textvariable=self._var,
            width=self._width,
            show=self._show or ""
        )
        self._entry.pack(fill='x')
        
        # Placeholder
        if self._placeholder:
            self._setup_placeholder()
        
        # Validation en temps réel
        if self._validate_callback:
            self._var.trace_add('write', self._on_change)
    
    def _setup_placeholder(self) -> None:
        """Configure le placeholder."""
        def on_focus_in(event):
            if self._entry.get() == self._placeholder:
                self._entry.delete(0, tk.END)
                self._entry.configure(foreground='black')
        
        def on_focus_out(event):
            if not self._entry.get():
                self._entry.insert(0, self._placeholder)
                self._entry.configure(foreground='gray')
        
        # Afficher le placeholder initialement
        self._entry.insert(0, self._placeholder)
        self._entry.configure(foreground='gray')
        
        self._entry.bind('<FocusIn>', on_focus_in)
        self._entry.bind('<FocusOut>', on_focus_out)
    
    def _on_change(self, *args) -> None:
        """Appelé lors de la modification."""
        if self._validate_callback:
            value = self.get_value()
            is_valid, message = self._validate_callback(value)
            if not is_valid:
                self.set_error(message)
            else:
                self.clear_error()
    
    def get_value(self) -> str:
        """Retourne la valeur."""
        value = self._var.get()
        if value == self._placeholder:
            return ""
        return value.strip()
    
    def set_value(self, value: str) -> None:
        """Définit la valeur."""
        self._var.set(value or "")
    
    def clear(self) -> None:
        """Efface le champ."""
        self._var.set("")
        self.clear_error()
        if self._placeholder:
            self._entry.insert(0, self._placeholder)
            self._entry.configure(foreground='gray')
    
    def set_enabled(self, enabled: bool) -> None:
        """Active/désactive le champ."""
        state = 'normal' if enabled else 'disabled'
        self._entry.configure(state=state)
    
    def focus(self) -> None:
        """Donne le focus au champ."""
        self._entry.focus_set()
    
    def bind_enter(self, callback: Callable) -> None:
        """Lie la touche Entrée à un callback."""
        self._entry.bind('<Return>', lambda e: callback())


class FormCombobox(FormField):
    """Liste déroulante."""
    
    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        values: List[Tuple[Any, str]],
        required: bool = False,
        width: int = 28,
        on_change: Callable[[Any], None] = None,
        **kwargs
    ):
        """
        Initialise la liste déroulante.
        
        Args:
            parent: Widget parent
            label: Libellé
            values: Liste de tuples (valeur, libellé)
            required: Obligatoire
            width: Largeur
            on_change: Callback lors du changement
        """
        self._values = values
        self._width = width
        self._on_change = on_change
        self._var = tk.StringVar()
        
        super().__init__(parent, label, required, **kwargs)
    
    def _create_widgets(self) -> None:
        """Crée les widgets."""
        super()._create_widgets()
        
        # Extraire les libellés
        display_values = [v[1] for v in self._values]
        
        self._combo = ttk.Combobox(
            self._input_frame,
            textvariable=self._var,
            values=display_values,
            width=self._width,
            state='readonly'
        )
        self._combo.pack(fill='x')
        
        if self._on_change:
            self._combo.bind('<<ComboboxSelected>>', self._handle_change)
    
    def _handle_change(self, event) -> None:
        """Gère le changement de sélection."""
        if self._on_change:
            self._on_change(self.get_value())
    
    def get_value(self) -> Any:
        """Retourne la valeur sélectionnée."""
        display = self._var.get()
        for value, label in self._values:
            if label == display:
                return value
        return None
    
    def set_value(self, value: Any) -> None:
        """Définit la valeur sélectionnée."""
        for val, label in self._values:
            if val == value:
                self._var.set(label)
                return
        self._var.set("")
    
    def clear(self) -> None:
        """Efface la sélection."""
        self._var.set("")
        self.clear_error()
    
    def set_enabled(self, enabled: bool) -> None:
        """Active/désactive."""
        state = 'readonly' if enabled else 'disabled'
        self._combo.configure(state=state)
    
    def update_values(self, values: List[Tuple[Any, str]]) -> None:
        """Met à jour les valeurs disponibles."""
        self._values = values
        display_values = [v[1] for v in self._values]
        self._combo.configure(values=display_values)


class FormDatePicker(FormField):
    """Sélecteur de date simplifié."""
    
    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        required: bool = False,
        min_date: date = None,
        max_date: date = None,
        years_range: Tuple[int, int] = (-2, 10),
        **kwargs
    ):
        """
        Initialise le sélecteur de date.
        
        Args:
            parent: Widget parent
            label: Libellé
            required: Obligatoire
            min_date: Date minimum
            max_date: Date maximum
            years_range: Tuple (années avant, années après) par rapport à l'année courante
        """
        self._min_date = min_date
        self._max_date = max_date
        self._years_range = years_range
        self._date_var = tk.StringVar()
        
        super().__init__(parent, label, required, **kwargs)
    
    def _create_widgets(self) -> None:
        """Crée les widgets."""
        super()._create_widgets()
        
        # Frame pour jour/mois/année
        date_frame = ttk.Frame(self._input_frame)
        date_frame.pack(fill='x')
        
        # Jour
        self._day_var = tk.StringVar()
        self._day_combo = ttk.Combobox(
            date_frame,
            textvariable=self._day_var,
            values=[""] + [f"{i:02d}" for i in range(1, 32)],
            width=4,
            state='readonly'
        )
        self._day_combo.pack(side='left', padx=(0, 2))
        
        ttk.Label(date_frame, text="/").pack(side='left')
        
        # Mois
        self._month_var = tk.StringVar()
        self._month_combo = ttk.Combobox(
            date_frame,
            textvariable=self._month_var,
            values=[""] + [f"{i:02d}" for i in range(1, 13)],
            width=4,
            state='readonly'
        )
        self._month_combo.pack(side='left', padx=2)
        
        ttk.Label(date_frame, text="/").pack(side='left')
        
        # Année - plage étendue
        current_year = date.today().year
        start_year = current_year + self._years_range[0]
        end_year = current_year + self._years_range[1]
        years = [""] + [str(y) for y in range(start_year, end_year + 1)]
        
        self._year_var = tk.StringVar()
        self._year_combo = ttk.Combobox(
            date_frame,
            textvariable=self._year_var,
            values=years,
            width=6,
            state='readonly'
        )
        self._year_combo.pack(side='left', padx=(2, 0))
    
    def get_value(self) -> Optional[date]:
        """Retourne la date sélectionnée."""
        day = self._day_var.get()
        month = self._month_var.get()
        year = self._year_var.get()
        
        if not all([day, month, year]):
            return None
        
        try:
            return date(int(year), int(month), int(day))
        except ValueError:
            return None
    
    def set_value(self, value) -> None:
        """
        Définit la date.
        
        Args:
            value: date, datetime, string (YYYY-MM-DD ou DD/MM/YYYY), ou None
        """
        if value is None:
            self.clear()
            return
        
        try:
            # Convertir en objet date si nécessaire
            if isinstance(value, str):
                if '-' in value:
                    # Format YYYY-MM-DD
                    parts = value.split('-')
                    if len(parts) == 3:
                        value = date(int(parts[0]), int(parts[1]), int(parts[2]))
                elif '/' in value:
                    # Format DD/MM/YYYY
                    parts = value.split('/')
                    if len(parts) == 3:
                        value = date(int(parts[2]), int(parts[1]), int(parts[0]))
            elif isinstance(value, datetime):
                value = value.date()
            
            if isinstance(value, date):
                self._day_var.set(f"{value.day:02d}")
                self._month_var.set(f"{value.month:02d}")
                self._year_var.set(str(value.year))
            else:
                self.clear()
        except (ValueError, TypeError, AttributeError):
            self.clear()
    
    def clear(self) -> None:
        """Efface la sélection."""
        self._day_var.set("")
        self._month_var.set("")
        self._year_var.set("")
        self.clear_error()
    
    def set_enabled(self, enabled: bool) -> None:
        """Active/désactive."""
        state = 'readonly' if enabled else 'disabled'
        self._day_combo.configure(state=state)
        self._month_combo.configure(state=state)
        self._year_combo.configure(state=state)


class FormTextArea(FormField):
    """Zone de texte multi-lignes."""
    
    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        required: bool = False,
        width: int = 40,
        height: int = 4,
        **kwargs
    ):
        """
        Initialise la zone de texte.
        
        Args:
            parent: Widget parent
            label: Libellé
            required: Obligatoire
            width: Largeur en caractères
            height: Hauteur en lignes
        """
        self._width = width
        self._height = height
        
        super().__init__(parent, label, required, **kwargs)
    
    def _create_widgets(self) -> None:
        """Crée les widgets."""
        super()._create_widgets()
        
        # Frame avec scrollbar
        text_frame = ttk.Frame(self._input_frame)
        text_frame.pack(fill='both', expand=True)
        
        self._text = tk.Text(
            text_frame,
            width=self._width,
            height=self._height,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            wrap='word'
        )
        self._text.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=self._text.yview)
        scrollbar.pack(side='right', fill='y')
        self._text.configure(yscrollcommand=scrollbar.set)
    
    def get_value(self) -> str:
        """Retourne le contenu."""
        return self._text.get('1.0', 'end-1c').strip()
    
    def set_value(self, value: str) -> None:
        """Définit le contenu."""
        self._text.delete('1.0', tk.END)
        if value:
            self._text.insert('1.0', value)
    
    def clear(self) -> None:
        """Efface le contenu."""
        self._text.delete('1.0', tk.END)
        self.clear_error()
    
    def set_enabled(self, enabled: bool) -> None:
        """Active/désactive."""
        state = 'normal' if enabled else 'disabled'
        self._text.configure(state=state)