"""
Vue de gestion des médicaments.

Auteur: Alsény Camara
Version: 1.3
"""

import tkinter as tk
from tkinter import ttk
from datetime import date, datetime
from typing import Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import UI_CONFIG
from controllers.medicament_controller import MedicamentController
from ui.components.data_table import DataTable
from ui.components.form_field import FormEntry, FormDatePicker, FormTextArea
from ui.components.alert_box import AlertBox, ConfirmDialog, InputDialog


class MedicamentView(ttk.Frame):
    """
    Vue de gestion des médicaments.
    
    Fonctionnalités:
    - Liste des médicaments avec recherche
    - Formulaire d'ajout/modification
    - Gestion du stock
    - Visualisation des alertes
    """
    
    def __init__(self, parent: tk.Widget, **kwargs):
        """
        Initialise la vue.
        
        Args:
            parent: Widget parent
        """
        super().__init__(parent, **kwargs)
        
        self._controller = MedicamentController()
        self._selected_id: Optional[int] = None
        self._is_editing = False
        
        self._create_widgets()
        self.refresh()
    
    def _create_widgets(self) -> None:
        """Crée les widgets de la vue."""
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_list_section()
        self._create_form_section()
    
    def _create_header(self) -> None:
        """Crée l'en-tête de la vue."""
        header = ttk.Frame(self)
        header.grid(row=0, column=0, columnspan=2, sticky='ew', padx=20, pady=(20, 10))
        
        ttk.Label(
            header,
            text="💊 Gestion des Médicaments",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_title'], 'bold')
        ).pack(side='left')
        
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side='right')
        
        ttk.Button(
            btn_frame,
            text="➕ Nouveau",
            command=self._new_medicament
        ).pack(side='left', padx=2)
        
        ttk.Button(
            btn_frame,
            text="🔄 Actualiser",
            command=self.refresh
        ).pack(side='left', padx=2)
    
    def _create_list_section(self) -> None:
        """Crée la section de liste des médicaments."""
        list_frame = ttk.LabelFrame(self, text="Liste des médicaments", padding=10)
        list_frame.grid(row=1, column=0, sticky='nsew', padx=(20, 10), pady=(0, 20))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Filtres
        filter_frame = ttk.Frame(list_frame)
        filter_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Catégorie:").pack(side='left', padx=(0, 5))
        
        self._filter_category_var = tk.StringVar(value="Toutes")
        self._filter_category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self._filter_category_var,
            values=["Toutes"],
            state='readonly',
            width=20
        )
        self._filter_category_combo.pack(side='left', padx=(0, 15))
        self._filter_category_combo.bind('<<ComboboxSelected>>', lambda e: self._filter_data())
        
        self._in_stock_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_frame,
            text="En stock uniquement",
            variable=self._in_stock_var,
            command=self._filter_data
        ).pack(side='left')
        
        # Tableau
        columns = [
            {'key': 'code', 'label': 'Code', 'width': 80},
            {'key': 'name', 'label': 'Nom', 'width': 150},
            {'key': 'category', 'label': 'Catégorie', 'width': 100},
            {'key': 'selling_price', 'label': 'Prix vente', 'width': 80, 'anchor': 'e'},
            {'key': 'quantity', 'label': 'Stock', 'width': 60, 'anchor': 'center'},
            {'key': 'expiration', 'label': 'Péremption', 'width': 90, 'anchor': 'center'}
        ]
        
        self._table = DataTable(
            list_frame,
            columns=columns,
            on_select=self._on_select,
            on_double_click=self._on_double_click,
            height=18
        )
        self._table.grid(row=1, column=0, sticky='nsew')
    
    def _create_form_section(self) -> None:
        """Crée la section formulaire."""
        form_frame = ttk.LabelFrame(self, text="Détails du médicament", padding=10)
        form_frame.grid(row=1, column=1, sticky='nsew', padx=(10, 20), pady=(0, 20))
        
        # Conteneur scrollable pour le formulaire
        canvas = tk.Canvas(form_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_frame, orient='vertical', command=canvas.yview)
        self._form_container = ttk.Frame(canvas)
        
        self._form_container.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self._form_container, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Champs du formulaire
        self._create_form_fields()
        
        # Boutons d'action
        self._create_form_buttons()
    
    def _create_form_fields(self) -> None:
        """Crée les champs du formulaire."""
        # Code
        self._code_field = FormEntry(
            self._form_container,
            label="Code",
            required=True,
            width=25
        )
        self._code_field.pack(fill='x', pady=5)
        
        # Nom
        self._name_field = FormEntry(
            self._form_container,
            label="Nom du médicament",
            required=True,
            width=25
        )
        self._name_field.pack(fill='x', pady=5)
        
        # Catégorie - Combobox éditable
        cat_frame = ttk.Frame(self._form_container)
        cat_frame.pack(fill='x', pady=5)
        
        ttk.Label(cat_frame, text="Catégorie").pack(anchor='w')
        
        self._category_var = tk.StringVar()
        self._category_entry = ttk.Combobox(
            cat_frame,
            textvariable=self._category_var,
            width=23
        )
        self._category_entry.pack(fill='x', pady=(2, 0))
        self._update_category_suggestions()
        
        # Prix d'achat
        self._purchase_price_field = FormEntry(
            self._form_container,
            label="Prix d'achat (GNF)",
            required=True,
            width=25
        )
        self._purchase_price_field.pack(fill='x', pady=5)
        
        # Prix de vente
        self._selling_price_field = FormEntry(
            self._form_container,
            label="Prix de vente (GNF)",
            required=True,
            width=25
        )
        self._selling_price_field.pack(fill='x', pady=5)
        
        # Quantité initiale (seulement pour création)
        self._quantity_field = FormEntry(
            self._form_container,
            label="Quantité initiale",
            width=25
        )
        self._quantity_field.pack(fill='x', pady=5)
        
        # Seuil d'alerte
        self._threshold_field = FormEntry(
            self._form_container,
            label="Seuil d'alerte stock",
            width=25
        )
        self._threshold_field.pack(fill='x', pady=5)
        
        # Date de péremption - FormDatePicker
        self._expiration_field = FormDatePicker(
            self._form_container,
            label="Date de péremption",
            years_range=(-1, 10)  # De l'année dernière à +10 ans
        )
        self._expiration_field.pack(fill='x', pady=5)
        
        # Fabricant
        self._manufacturer_field = FormEntry(
            self._form_container,
            label="Fabricant",
            width=25
        )
        self._manufacturer_field.pack(fill='x', pady=5)
        
        # Description
        self._description_field = FormTextArea(
            self._form_container,
            label="Description",
            width=25,
            height=3
        )
        self._description_field.pack(fill='x', pady=5)
    
    def _update_category_suggestions(self) -> None:
        """Met à jour les suggestions de catégories."""
        try:
            categories = self._controller.get_categories()
            self._category_entry['values'] = categories if categories else []
        except Exception:
            self._category_entry['values'] = []
    
    def _create_form_buttons(self) -> None:
        """Crée les boutons du formulaire."""
        btn_frame = ttk.Frame(self._form_container)
        btn_frame.pack(fill='x', pady=20)
        
        self._save_btn = ttk.Button(
            btn_frame,
            text="💾 Enregistrer",
            command=self._save
        )
        self._save_btn.pack(side='left', padx=2)
        
        self._cancel_btn = ttk.Button(
            btn_frame,
            text="❌ Annuler",
            command=self._cancel
        )
        self._cancel_btn.pack(side='left', padx=2)
        
        # Boutons de gestion du stock
        stock_frame = ttk.LabelFrame(self._form_container, text="Gestion du stock", padding=10)
        stock_frame.pack(fill='x', pady=10)
        
        self._add_stock_btn = ttk.Button(
            stock_frame,
            text="➕ Ajouter stock",
            command=self._add_stock
        )
        self._add_stock_btn.pack(side='left', padx=2)
        
        self._adjust_stock_btn = ttk.Button(
            stock_frame,
            text="🔧 Ajuster stock",
            command=self._adjust_stock
        )
        self._adjust_stock_btn.pack(side='left', padx=2)
        
        # Bouton supprimer
        self._delete_btn = ttk.Button(
            self._form_container,
            text="🗑️ Supprimer",
            command=self._delete
        )
        self._delete_btn.pack(anchor='e', pady=10)
        
        # État initial
        self._set_form_state(False)
    
    def _set_form_state(self, editing: bool, is_new: bool = False) -> None:
        """Configure l'état du formulaire."""
        self._is_editing = editing
        
        state = 'normal' if editing else 'disabled'
        
        self._code_field.set_enabled(editing)
        self._name_field.set_enabled(editing)
        self._category_entry.configure(state=state)
        self._purchase_price_field.set_enabled(editing)
        self._selling_price_field.set_enabled(editing)
        self._quantity_field.set_enabled(editing and is_new)
        self._threshold_field.set_enabled(editing)
        self._expiration_field.set_enabled(editing)
        self._manufacturer_field.set_enabled(editing)
        self._description_field.set_enabled(editing)
        
        self._save_btn.configure(state=state)
        self._cancel_btn.configure(state=state)
        
        # Boutons de stock: actifs uniquement en consultation
        stock_state = 'normal' if (not editing and self._selected_id) else 'disabled'
        self._add_stock_btn.configure(state=stock_state)
        self._adjust_stock_btn.configure(state=stock_state)
        
        # Supprimer: actif uniquement en consultation avec sélection
        delete_state = 'normal' if (not editing and self._selected_id) else 'disabled'
        self._delete_btn.configure(state=delete_state)
    
    def _clear_form(self) -> None:
        """Efface le formulaire."""
        self._code_field.clear()
        self._name_field.clear()
        self._category_var.set("")
        self._purchase_price_field.clear()
        self._selling_price_field.clear()
        self._quantity_field.clear()
        self._threshold_field.clear()
        self._expiration_field.clear()
        self._manufacturer_field.clear()
        self._description_field.clear()
        
        self._selected_id = None
    
    def _load_medicament(self, medicament_id: int) -> None:
        """Charge un médicament dans le formulaire."""
        med = self._controller.get_medicament(medicament_id)
        if med is None:
            return
        
        self._selected_id = med.id
        
        self._code_field.set_value(med.code)
        self._name_field.set_value(med.name)
        self._category_var.set(med.category or "")
        self._purchase_price_field.set_value(str(med.purchase_price))
        self._selling_price_field.set_value(str(med.selling_price))
        self._quantity_field.set_value(str(med.quantity_in_stock))
        self._threshold_field.set_value(str(med.stock_threshold))
        self._expiration_field.set_value(med.expiration_date)
        self._manufacturer_field.set_value(med.manufacturer or "")
        self._description_field.set_value(med.description or "")
        
        self._set_form_state(False)
    
    def _on_select(self, item: dict) -> None:
        """Gère la sélection d'un médicament."""
        if item and 'id' in item:
            self._load_medicament(item['id'])
    
    def _on_double_click(self, item: dict) -> None:
        """Gère le double-clic (édition)."""
        if item and 'id' in item:
            self._load_medicament(item['id'])
            self._set_form_state(True, is_new=False)
    
    def _new_medicament(self) -> None:
        """Prépare le formulaire pour un nouveau médicament."""
        self._clear_form()
        self._set_form_state(True, is_new=True)
        self._code_field.focus()
    
    def _save(self) -> None:
        """Enregistre le médicament."""
        # Récupérer la catégorie
        category = self._category_var.get().strip()
        
        # Récupérer la date de péremption
        expiration_date = self._expiration_field.get_value()
        
        if self._selected_id:
            # Modification
            success, message = self._controller.update_medicament(
                medicament_id=self._selected_id,
                code=self._code_field.get_value(),
                name=self._name_field.get_value(),
                purchase_price=self._purchase_price_field.get_value(),
                selling_price=self._selling_price_field.get_value(),
                description=self._description_field.get_value(),
                category=category,
                threshold=self._threshold_field.get_value(),
                expiration_date=expiration_date,
                manufacturer=self._manufacturer_field.get_value()
            )
        else:
            # Création
            success, message = self._controller.create_medicament(
                code=self._code_field.get_value(),
                name=self._name_field.get_value(),
                purchase_price=self._purchase_price_field.get_value(),
                selling_price=self._selling_price_field.get_value(),
                description=self._description_field.get_value(),
                category=category,
                quantity=self._quantity_field.get_value() or "0",
                threshold=self._threshold_field.get_value(),
                expiration_date=expiration_date,
                manufacturer=self._manufacturer_field.get_value()
            )
        
        if success:
            AlertBox.show_success("Succès", message, self)
            self._set_form_state(False)
            self._update_category_suggestions()
            self.refresh()
        else:
            AlertBox.show_error("Erreur", message, self)
    
    def _cancel(self) -> None:
        """Annule l'édition."""
        if self._selected_id:
            self._load_medicament(self._selected_id)
        else:
            self._clear_form()
        self._set_form_state(False)
    
    def _delete(self) -> None:
        """Supprime le médicament sélectionné."""
        if not self._selected_id:
            return
        
        dialog = ConfirmDialog(
            self,
            title="Confirmation",
            message="Êtes-vous sûr de vouloir supprimer ce médicament ?",
            confirm_text="Supprimer",
            icon="warning"
        )
        
        if dialog.result:
            success, message = self._controller.delete_medicament(self._selected_id)
            
            if success:
                AlertBox.show_success("Succès", message, self)
                self._clear_form()
                self.refresh()
            else:
                AlertBox.show_error("Erreur", message, self)
    
    def _add_stock(self) -> None:
        """Ajoute du stock au médicament."""
        if not self._selected_id:
            return
        
        dialog = InputDialog(
            self,
            title="Ajouter du stock",
            prompt="Quantité à ajouter:",
            input_type="number"
        )
        
        if dialog.result:
            success, message = self._controller.add_stock(
                self._selected_id,
                dialog.result,
                "Réapprovisionnement"
            )
            
            if success:
                AlertBox.show_success("Succès", message, self)
                self._load_medicament(self._selected_id)
                self.refresh()
            else:
                AlertBox.show_error("Erreur", message, self)
    
    def _adjust_stock(self) -> None:
        """Ajuste le stock du médicament."""
        if not self._selected_id:
            return
        
        med = self._controller.get_medicament(self._selected_id)
        if not med:
            return
        
        dialog = InputDialog(
            self,
            title="Ajuster le stock",
            prompt=f"Nouvelle quantité (actuel: {med.quantity_in_stock}):",
            initial_value=str(med.quantity_in_stock),
            input_type="number"
        )
        
        if dialog.result:
            success, message = self._controller.adjust_stock(
                self._selected_id,
                dialog.result,
                "Ajustement inventaire"
            )
            
            if success:
                AlertBox.show_success("Succès", message, self)
                self._load_medicament(self._selected_id)
                self.refresh()
            else:
                AlertBox.show_error("Erreur", message, self)
    
    def _filter_data(self) -> None:
        """Filtre les données selon les critères."""
        category = self._filter_category_var.get()
        if category == "Toutes":
            category = ""
        
        in_stock_only = self._in_stock_var.get()
        
        data = self._controller.get_medicaments_for_table()
        
        # Filtrer les données
        if category:
            data = [d for d in data if d.get('category') == category]
        if in_stock_only:
            data = [d for d in data if d.get('quantity', 0) > 0]
        
        self._table.load_data(data)
    
    def refresh(self) -> None:
        """Rafraîchit les données."""
        # Mettre à jour les catégories pour le filtre
        categories = ["Toutes"] + self._controller.get_categories()
        self._filter_category_combo.configure(values=categories)
        
        # Mettre à jour les suggestions de catégorie dans le formulaire
        self._update_category_suggestions()
        
        # Charger les données
        data = self._controller.get_medicaments_for_table()
        self._table.load_data(data)