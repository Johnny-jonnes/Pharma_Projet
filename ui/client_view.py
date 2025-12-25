"""
Vue de gestion des clients.

Auteur: Alsény Camara
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import UI_CONFIG
from controllers.client_controller import ClientController
from ui.components.data_table import DataTable
from ui.components.alert_box import AlertBox, ConfirmDialog


class ClientView(ttk.Frame):
    """
    Vue de gestion des clients.
    """
    
    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, **kwargs)
        
        self._controller = ClientController()
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
        """Crée l'en-tête."""
        header = ttk.Frame(self)
        header.grid(row=0, column=0, columnspan=2, sticky='ew', padx=20, pady=(20, 10))
        
        ttk.Label(
            header,
            text="👥 Gestion des Clients",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_title'], 'bold')
        ).pack(side='left')
        
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text="🔄 Actualiser", command=self.refresh).pack(side='left', padx=2)
    
    def _create_list_section(self) -> None:
        """Crée la section liste."""
        list_frame = ttk.LabelFrame(self, text="Liste des clients", padding=10)
        list_frame.grid(row=1, column=0, sticky='nsew', padx=(20, 10), pady=(0, 20))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        columns = [
            {'key': 'code', 'label': 'Code', 'width': 80},
            {'key': 'name', 'label': 'Nom complet', 'width': 150},
            {'key': 'phone', 'label': 'Téléphone', 'width': 100},
            {'key': 'loyalty_points', 'label': 'Points', 'width': 70, 'anchor': 'center'},
            {'key': 'tier', 'label': 'Niveau', 'width': 80, 'anchor': 'center'}
        ]
        
        self._table = DataTable(
            list_frame,
            columns=columns,
            on_select=self._on_select,
            on_double_click=self._on_double_click,
            height=18
        )
        self._table.grid(row=0, column=0, sticky='nsew')
    
    def _create_form_section(self) -> None:
        """Crée la section formulaire."""
        form_frame = ttk.LabelFrame(self, text="Détails du client", padding=10)
        form_frame.grid(row=1, column=1, sticky='nsew', padx=(10, 20), pady=(0, 20))
        
        # Code (lecture seule)
        self._code_var = tk.StringVar(value="Code: (nouveau)")
        ttk.Label(
            form_frame,
            textvariable=self._code_var,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'], 'bold')
        ).pack(anchor='w', pady=5)
        
        # Prénom
        ttk.Label(form_frame, text="Prénom *").pack(anchor='w', pady=(10, 2))
        self._first_name_var = tk.StringVar()
        self._first_name_entry = ttk.Entry(form_frame, textvariable=self._first_name_var, width=30)
        self._first_name_entry.pack(fill='x', pady=(0, 5))
        
        # Nom
        ttk.Label(form_frame, text="Nom de famille *").pack(anchor='w', pady=(5, 2))
        self._last_name_var = tk.StringVar()
        self._last_name_entry = ttk.Entry(form_frame, textvariable=self._last_name_var, width=30)
        self._last_name_entry.pack(fill='x', pady=(0, 5))
        
        # Téléphone
        ttk.Label(form_frame, text="Téléphone").pack(anchor='w', pady=(5, 2))
        self._phone_var = tk.StringVar()
        self._phone_entry = ttk.Entry(form_frame, textvariable=self._phone_var, width=30)
        self._phone_entry.pack(fill='x', pady=(0, 5))
        
        # Email
        ttk.Label(form_frame, text="Email").pack(anchor='w', pady=(5, 2))
        self._email_var = tk.StringVar()
        self._email_entry = ttk.Entry(form_frame, textvariable=self._email_var, width=30)
        self._email_entry.pack(fill='x', pady=(0, 5))
        
        # Adresse
        ttk.Label(form_frame, text="Adresse").pack(anchor='w', pady=(5, 2))
        self._address_var = tk.StringVar()
        self._address_entry = ttk.Entry(form_frame, textvariable=self._address_var, width=30)
        self._address_entry.pack(fill='x', pady=(0, 10))
        
        # Informations fidélité
        loyalty_frame = ttk.LabelFrame(form_frame, text="🎁 Fidélité", padding=10)
        loyalty_frame.pack(fill='x', pady=10)
        
        self._loyalty_points_var = tk.StringVar(value="0 points")
        ttk.Label(
            loyalty_frame,
            textvariable=self._loyalty_points_var,
            font=(UI_CONFIG['font_family'], 14, 'bold'),
            foreground=UI_CONFIG['success_color']
        ).pack(anchor='w')
        
        self._loyalty_tier_var = tk.StringVar(value="Niveau: Standard")
        ttk.Label(loyalty_frame, textvariable=self._loyalty_tier_var).pack(anchor='w')
        
        self._loyalty_discount_var = tk.StringVar(value="Remise: 0%")
        ttk.Label(loyalty_frame, textvariable=self._loyalty_discount_var).pack(anchor='w')
        
        self._total_spent_var = tk.StringVar(value="Total dépensé: 0 GNF")
        ttk.Label(loyalty_frame, textvariable=self._total_spent_var, foreground='gray').pack(anchor='w', pady=(10, 0))
        
        # Boutons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill='x', pady=20)
        
        self._save_btn = ttk.Button(btn_frame, text="💾 Enregistrer", command=self._save)
        self._save_btn.pack(side='left', padx=2)
        
        self._cancel_btn = ttk.Button(btn_frame, text="❌ Annuler", command=self._cancel)
        self._cancel_btn.pack(side='left', padx=2)
        
        self._delete_btn = ttk.Button(btn_frame, text="🗑️ Supprimer", command=self._delete)
        self._delete_btn.pack(side='right', padx=2)
        
        self._set_form_state(False)
    
    def _set_form_state(self, editing: bool) -> None:
        """Configure l'état du formulaire."""
        self._is_editing = editing
        
        state = 'normal' if editing else 'disabled'
        self._first_name_entry.configure(state=state)
        self._last_name_entry.configure(state=state)
        self._phone_entry.configure(state=state)
        self._email_entry.configure(state=state)
        self._address_entry.configure(state=state)
        
        self._save_btn.configure(state=state)
        self._cancel_btn.configure(state=state)
        
        delete_state = 'normal' if (not editing and self._selected_id) else 'disabled'
        self._delete_btn.configure(state=delete_state)
    
    def _clear_form(self) -> None:
        """Efface le formulaire."""
        self._code_var.set("Code: (nouveau)")
        self._first_name_var.set("")
        self._last_name_var.set("")
        self._phone_var.set("")
        self._email_var.set("")
        self._address_var.set("")
        
        self._loyalty_points_var.set("0 points")
        self._loyalty_tier_var.set("Niveau: Standard")
        self._loyalty_discount_var.set("Remise: 0%")
        self._total_spent_var.set("Total dépensé: 0 GNF")
        
        self._selected_id = None
    
    def _load_client(self, client_id: int) -> None:
        """Charge un client dans le formulaire."""
        client = self._controller.get_client(client_id)
        if client is None:
            return
        
        self._selected_id = client.id
        
        self._code_var.set(f"Code: {client.code}")
        self._first_name_var.set(client.first_name)
        self._last_name_var.set(client.last_name)
        self._phone_var.set(client.phone or "")
        self._email_var.set(client.email or "")
        self._address_var.set(client.address or "")
        
        # Fidélité
        loyalty_info = self._controller.get_client_loyalty_info(client_id)
        
        self._loyalty_points_var.set(f"{loyalty_info.get('current_points', 0)} points")
        self._loyalty_tier_var.set(f"Niveau: {loyalty_info.get('current_tier', 'Standard')}")
        self._loyalty_discount_var.set(f"Remise: {loyalty_info.get('current_discount', 0)}%")
        
        from utils.format_utils import FormatUtils
        total_spent = FormatUtils.format_currency(loyalty_info.get('total_spent', 0))
        self._total_spent_var.set(f"Total dépensé: {total_spent}")
        
        self._set_form_state(False)
    
    def _on_select(self, item: dict) -> None:
        """Gère la sélection."""
        if item and 'id' in item:
            self._load_client(item['id'])
    
    def _on_double_click(self, item: dict) -> None:
        """Gère le double-clic."""
        if item and 'id' in item:
            self._load_client(item['id'])
            self._set_form_state(True)
    
    def _new_client(self) -> None:
        """Nouveau client."""
        self._clear_form()
        self._set_form_state(True)
        self._first_name_entry.focus_set()
    
    def _save(self) -> None:
        """Enregistre le client."""
        first_name = self._first_name_var.get().strip()
        last_name = self._last_name_var.get().strip()
        phone = self._phone_var.get().strip()
        email = self._email_var.get().strip()
        address = self._address_var.get().strip()
        
        # DEBUG
        print("=" * 60)
        print("DEBUG CLIENT - Tentative d'enregistrement")
        print(f"  Prénom: '{first_name}'")
        print(f"  Nom: '{last_name}'")
        print(f"  Téléphone: '{phone}'")
        print(f"  Email: '{email}'")
        print(f"  Adresse: '{address}'")
        print(f"  ID sélectionné: {self._selected_id}")
        print(f"  Mode édition: {self._is_editing}")
        print("=" * 60)
        
        if not first_name:
            AlertBox.show_error("Erreur", "Le prénom est obligatoire", self)
            self._first_name_entry.focus_set()
            return
        
        if not last_name:
            AlertBox.show_error("Erreur", "Le nom est obligatoire", self)
            self._last_name_entry.focus_set()
            return
        
        try:
            if self._selected_id:
                # MODE MODIFICATION
                print(f"DEBUG - Mode MODIFICATION, ID: {self._selected_id}")
                success, message = self._controller.update_client(
                    client_id=self._selected_id,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    address=address
                )
                print(f"DEBUG - Résultat update: success={success}, message='{message}'")
            else:
                # MODE CRÉATION
                print("DEBUG - Mode CRÉATION")
                result = self._controller.create_client(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    address=address
                )
                print(f"DEBUG - Résultat brut: {result}")
                print(f"DEBUG - Type résultat: {type(result)}")
                
                if isinstance(result, tuple):
                    if len(result) == 3:
                        success, message, client = result
                        print(f"DEBUG - Tuple à 3 éléments: success={success}, message='{message}', client={client}")
                    elif len(result) == 2:
                        success, message = result
                        print(f"DEBUG - Tuple à 2 éléments: success={success}, message='{message}'")
                    else:
                        success = False
                        message = f"Format inattendu: {len(result)} éléments"
                        print(f"DEBUG - Format inattendu")
                else:
                    success = False
                    message = f"Type inattendu: {type(result)}"
                    print(f"DEBUG - Type inattendu: {type(result)}")
            
            print(f"DEBUG - Succès final: {success}")
            print(f"DEBUG - Message final: {message}")
            print("=" * 60)
            
            if success:
                AlertBox.show_success("Succès", message, self)
                self._set_form_state(False)
                self.refresh()
            else:
                AlertBox.show_error("Erreur", message, self)
        
        except Exception as e:
            print(f"DEBUG - EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            AlertBox.show_error("Erreur", f"Exception: {str(e)}", self)
    
    def _cancel(self) -> None:
        """Annule."""
        if self._selected_id:
            self._load_client(self._selected_id)
        else:
            self._clear_form()
        self._set_form_state(False)
    
    def _delete(self) -> None:
        """Supprime le client."""
        if not self._selected_id:
            return
        
        dialog = ConfirmDialog(
            self,
            title="Confirmation",
            message="Êtes-vous sûr de vouloir supprimer ce client ?",
            confirm_text="Supprimer",
            icon="warning"
        )
        
        if dialog.result:
            success, message = self._controller.delete_client(self._selected_id)
            
            if success:
                AlertBox.show_success("Succès", message, self)
                self._clear_form()
                self.refresh()
            else:
                AlertBox.show_error("Erreur", message, self)
    
    def refresh(self) -> None:
        """Rafraîchit les données."""
        print("DEBUG - Rafraîchissement de la liste clients")
        try:
            data = self._controller.get_clients_for_table()
            print(f"DEBUG - Nombre de clients: {len(data)}")
            self._table.load_data(data)
        except Exception as e:
            print(f"DEBUG - Erreur refresh: {e}")
            import traceback
            traceback.print_exc()