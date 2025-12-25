"""
Composant tableau de données réutilisable.

Auteur: Alsény Camara
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Callable, Optional, Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import UI_CONFIG


class DataTable(ttk.Frame):
    """
    Tableau de données basé sur Treeview.
    
    Fonctionnalités:
    - Colonnes configurables
    - Tri par colonne
    - Sélection simple/multiple
    - Recherche intégrée
    - Pagination optionnelle
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        columns: List[Dict[str, Any]],
        show_search: bool = True,
        show_scrollbar: bool = True,
        select_mode: str = 'browse',
        on_select: Callable[[Dict], None] = None,
        on_double_click: Callable[[Dict], None] = None,
        row_colors: Dict[str, str] = None,
        height: int = 15,
        **kwargs
    ):
        """
        Initialise le tableau.
        
        Args:
            parent: Widget parent
            columns: Configuration des colonnes
                [{'key': 'id', 'label': 'ID', 'width': 50, 'anchor': 'center'}, ...]
            show_search: Afficher la barre de recherche
            show_scrollbar: Afficher les scrollbars
            select_mode: Mode de sélection ('browse', 'extended')
            on_select: Callback lors de la sélection
            on_double_click: Callback lors du double-clic
            row_colors: Couleurs conditionnelles {'condition': 'color'}
            height: Nombre de lignes visibles
        """
        super().__init__(parent, **kwargs)
        
        self._columns = columns
        self._show_search = show_search
        self._show_scrollbar = show_scrollbar
        self._select_mode = select_mode
        self._on_select = on_select
        self._on_double_click = on_double_click
        self._row_colors = row_colors or {}
        self._height = height
        
        self._data: List[Dict] = []
        self._filtered_data: List[Dict] = []
        self._sort_column: Optional[str] = None
        self._sort_reverse: bool = False
        
        self._create_widgets()
        self._setup_styles()
    
    def _create_widgets(self) -> None:
        """Crée les widgets du tableau."""
        # Barre de recherche
        if self._show_search:
            search_frame = ttk.Frame(self)
            search_frame.pack(fill='x', pady=(0, 5))
            
            ttk.Label(
                search_frame,
                text="🔍 Rechercher:",
                font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
            ).pack(side='left', padx=(0, 5))
            
            self._search_var = tk.StringVar()
            self._search_var.trace_add('write', self._on_search)
            
            self._search_entry = ttk.Entry(
                search_frame,
                textvariable=self._search_var,
                width=30
            )
            self._search_entry.pack(side='left', fill='x', expand=True)
            
            ttk.Button(
                search_frame,
                text="Effacer",
                command=self._clear_search,
                width=8
            ).pack(side='left', padx=(5, 0))
        
        # Conteneur du tableau
        table_frame = ttk.Frame(self)
        table_frame.pack(fill='both', expand=True)
        
        # Configuration des colonnes
        column_ids = [col['key'] for col in self._columns]
        
        self._tree = ttk.Treeview(
            table_frame,
            columns=column_ids,
            show='headings',
            selectmode=self._select_mode,
            height=self._height
        )
        
        # Configurer chaque colonne
        for col in self._columns:
            self._tree.heading(
                col['key'],
                text=col['label'],
                command=lambda c=col['key']: self._sort_by_column(c)
            )
            self._tree.column(
                col['key'],
                width=col.get('width', 100),
                anchor=col.get('anchor', 'w'),
                minwidth=col.get('min_width', 50)
            )
        
        # Scrollbars
        if self._show_scrollbar:
            v_scroll = ttk.Scrollbar(
                table_frame,
                orient='vertical',
                command=self._tree.yview
            )
            v_scroll.pack(side='right', fill='y')
            
            h_scroll = ttk.Scrollbar(
                table_frame,
                orient='horizontal',
                command=self._tree.xview
            )
            h_scroll.pack(side='bottom', fill='x')
            
            self._tree.configure(
                yscrollcommand=v_scroll.set,
                xscrollcommand=h_scroll.set
            )
        
        self._tree.pack(fill='both', expand=True)
        
        # Événements
        self._tree.bind('<<TreeviewSelect>>', self._handle_select)
        self._tree.bind('<Double-1>', self._handle_double_click)
        
        # Compteur
        self._count_var = tk.StringVar(value="0 élément(s)")
        ttk.Label(
            self,
            textvariable=self._count_var,
            font=(UI_CONFIG['font_family'], 9)
        ).pack(anchor='e', pady=(5, 0))
    
    def _setup_styles(self) -> None:
        """Configure les styles du tableau."""
        style = ttk.Style()
        
        # Style des lignes
        style.configure(
            'Treeview',
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            rowheight=25
        )
        
        # Style des en-têtes
        style.configure(
            'Treeview.Heading',
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'], 'bold')
        )
        
        # Tags pour couleurs conditionnelles
        self._tree.tag_configure('low_stock', background='#FADBD8')
        self._tree.tag_configure('expiring', background='#FCF3CF')
        self._tree.tag_configure('expired', background='#E74C3C', foreground='white')
        self._tree.tag_configure('inactive', foreground='gray')
        self._tree.tag_configure('cancelled', foreground='gray', background='#F5F5F5')
        self._tree.tag_configure('selected', background=UI_CONFIG['secondary_color'])
    
    def load_data(self, data: List[Dict]) -> None:
        """
        Charge les données dans le tableau.
        
        Args:
            data: Liste de dictionnaires
        """
        self._data = data
        self._filtered_data = data.copy()
        self._refresh_table()
    
    def _refresh_table(self) -> None:
        """Rafraîchit l'affichage du tableau."""
        # Effacer le tableau
        for item in self._tree.get_children():
            self._tree.delete(item)
        
        # Insérer les données
        for row in self._filtered_data:
            values = [row.get(col['key'], '') for col in self._columns]
            
            # Déterminer le tag
            tags = self._get_row_tags(row)
            
            self._tree.insert('', 'end', values=values, tags=tags)
        
        # Mettre à jour le compteur
        count = len(self._filtered_data)
        total = len(self._data)
        
        if count == total:
            self._count_var.set(f"{count} élément(s)")
        else:
            self._count_var.set(f"{count} / {total} élément(s)")
    
    def _get_row_tags(self, row: Dict) -> Tuple[str, ...]:
        """Détermine les tags pour une ligne."""
        tags = []
        
        if row.get('is_low_stock'):
            tags.append('low_stock')
        if row.get('is_expiring'):
            tags.append('expiring')
        if row.get('is_expired'):
            tags.append('expired')
        if row.get('is_active') == False:
            tags.append('inactive')
        if row.get('status') == 'cancelled':
            tags.append('cancelled')
        
        return tuple(tags)
    
    def _on_search(self, *args) -> None:
        """Filtre les données selon la recherche."""
        search_text = self._search_var.get().lower()
        
        if not search_text:
            self._filtered_data = self._data.copy()
        else:
            self._filtered_data = [
                row for row in self._data
                if any(
                    search_text in str(row.get(col['key'], '')).lower()
                    for col in self._columns
                )
            ]
        
        self._refresh_table()
    
    def _clear_search(self) -> None:
        """Efface la recherche."""
        self._search_var.set("")
    
    def _sort_by_column(self, column: str) -> None:
        """Trie par une colonne."""
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False
        
        try:
            self._filtered_data.sort(
                key=lambda x: x.get(column, ''),
                reverse=self._sort_reverse
            )
        except TypeError:
            # Comparaison de types différents
            self._filtered_data.sort(
                key=lambda x: str(x.get(column, '')),
                reverse=self._sort_reverse
            )
        
        self._refresh_table()
    
    def _handle_select(self, event) -> None:
        """Gère la sélection."""
        if self._on_select:
            selected = self.get_selected()
            if selected:
                self._on_select(selected)
    
    def _handle_double_click(self, event) -> None:
        """Gère le double-clic."""
        if self._on_double_click:
            selected = self.get_selected()
            if selected:
                self._on_double_click(selected)
    
    def get_selected(self) -> Optional[Dict]:
        """
        Retourne l'élément sélectionné.
        
        Returns:
            Optional[Dict]: Données de la ligne sélectionnée
        """
        selection = self._tree.selection()
        if not selection:
            return None
        
        item = self._tree.item(selection[0])
        values = item['values']
        
        # Reconstruire le dictionnaire
        row = {}
        for i, col in enumerate(self._columns):
            row[col['key']] = values[i] if i < len(values) else None
        
        # Retrouver les données originales
        for data_row in self._data:
            match = True
            for col in self._columns:
                if str(data_row.get(col['key'], '')) != str(row.get(col['key'], '')):
                    match = False
                    break
            if match:
                return data_row
        
        return row
    
    def get_all_selected(self) -> List[Dict]:
        """Retourne tous les éléments sélectionnés."""
        results = []
        for item_id in self._tree.selection():
            item = self._tree.item(item_id)
            values = item['values']
            
            row = {}
            for i, col in enumerate(self._columns):
                row[col['key']] = values[i] if i < len(values) else None
            
            results.append(row)
        
        return results
    
    def clear_selection(self) -> None:
        """Efface la sélection."""
        self._tree.selection_remove(*self._tree.selection())
    
    def refresh(self) -> None:
        """Rafraîchit le tableau avec les données actuelles."""
        self._refresh_table()
    
    def get_data(self) -> List[Dict]:
        """Retourne les données chargées."""
        return self._data.copy()
    
    def select_by_id(self, id_value: Any, id_column: str = 'id') -> None:
        """Sélectionne une ligne par ID."""
        for item in self._tree.get_children():
            values = self._tree.item(item)['values']
            col_index = next(
                (i for i, col in enumerate(self._columns) if col['key'] == id_column),
                None
            )
            if col_index is not None and values[col_index] == id_value:
                self._tree.selection_set(item)
                self._tree.see(item)
                break