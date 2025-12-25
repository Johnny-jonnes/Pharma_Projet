"""
Vue de gestion des utilisateurs.

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
from controllers.user_controller import UserController
from ui.components.data_table import DataTable
from ui.components.form_field import FormCombobox
from ui.components.alert_box import AlertBox, ConfirmDialog


class UserView(ttk.Frame):
    """
    Vue de gestion des utilisateurs (Admin uniquement).
    """
    
    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, **kwargs)
        
        self._controller = UserController()
        self._selected_id: Optional[int] = None
        self._is_editing = False
        self._is_new = False
        
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
            text="👤 Gestion des Utilisateurs",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_title'], 'bold')
        ).pack(side='left')
        
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side='right')
        
        ttk.Button(
            btn_frame,
            text="➕ Nouvel utilisateur",
            command=self._new_user
        ).pack(side='left', padx=2)
        
        ttk.Button(
            btn_frame,
            text="🔄 Actualiser",
            command=self.refresh
        ).pack(side='left', padx=2)
    
    def _create_list_section(self) -> None:
        """Crée la section liste."""
        list_frame = ttk.LabelFrame(self, text="Liste des utilisateurs", padding=10)
        list_frame.grid(row=1, column=0, sticky='nsew', padx=(20, 10), pady=(0, 20))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        columns = [
            {'key': 'username', 'label': 'Identifiant', 'width': 100},
            {'key': 'full_name', 'label': 'Nom complet', 'width': 150},
            {'key': 'role_display', 'label': 'Rôle', 'width': 100},
            {'key': 'status', 'label': 'Statut', 'width': 80, 'anchor': 'center'}
        ]
        
        self._table = DataTable(
            list_frame,
            columns=columns,
            on_select=self._on_select,
            on_double_click=self._on_double_click,
            height=15
        )
        self._table.grid(row=0, column=0, sticky='nsew')
    
    def _create_form_section(self) -> None:
        """Crée la section formulaire."""
        form_frame = ttk.LabelFrame(self, text="Détails de l'utilisateur", padding=10)
        form_frame.grid(row=1, column=1, sticky='nsew', padx=(10, 20), pady=(0, 20))
        
        # Conteneur pour le formulaire
        self._form_container = ttk.Frame(form_frame)
        self._form_container.pack(fill='both', expand=True)
        
        # Identifiant
        ttk.Label(
            self._form_container,
            text="Identifiant *",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(anchor='w', pady=(5, 2))
        
        self._username_var = tk.StringVar()
        self._username_entry = ttk.Entry(
            self._form_container,
            textvariable=self._username_var,
            width=30
        )
        self._username_entry.pack(fill='x', pady=(0, 10))
        
        # Nom complet
        ttk.Label(
            self._form_container,
            text="Nom complet *",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(anchor='w', pady=(0, 2))
        
        self._fullname_var = tk.StringVar()
        self._fullname_entry = ttk.Entry(
            self._form_container,
            textvariable=self._fullname_var,
            width=30
        )
        self._fullname_entry.pack(fill='x', pady=(0, 10))
        
        # Rôle
        ttk.Label(
            self._form_container,
            text="Rôle *",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(anchor='w', pady=(0, 2))
        
        self._role_var = tk.StringVar()
        self._role_combo = ttk.Combobox(
            self._form_container,
            textvariable=self._role_var,
            values=["Administrateur", "Pharmacien", "Vendeur"],
            state='readonly',
            width=28
        )
        self._role_combo.pack(fill='x', pady=(0, 10))
        
        # Mapping des rôles
        self._role_map = {
            "Administrateur": "admin",
            "Pharmacien": "pharmacien",
            "Vendeur": "vendeur"
        }
        self._role_map_reverse = {v: k for k, v in self._role_map.items()}
        
        # Statut
        self._active_var = tk.BooleanVar(value=True)
        self._active_check = ttk.Checkbutton(
            self._form_container,
            text="Compte actif",
            variable=self._active_var
        )
        self._active_check.pack(anchor='w', pady=10)
        
        # Section mot de passe (pour création uniquement)
        self._password_frame = ttk.LabelFrame(
            self._form_container, 
            text="Mot de passe", 
            padding=10
        )
        
        ttk.Label(
            self._password_frame,
            text="Mot de passe *",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(anchor='w', pady=(0, 2))
        
        self._password_var = tk.StringVar()
        self._password_entry = ttk.Entry(
            self._password_frame,
            textvariable=self._password_var,
            width=28,
            show='•'
        )
        self._password_entry.pack(fill='x', pady=(0, 10))
        
        ttk.Label(
            self._password_frame,
            text="Confirmer *",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(anchor='w', pady=(0, 2))
        
        self._confirm_var = tk.StringVar()
        self._confirm_entry = ttk.Entry(
            self._password_frame,
            textvariable=self._confirm_var,
            width=28,
            show='•'
        )
        self._confirm_entry.pack(fill='x')
        
        # Boutons de sauvegarde
        self._btn_frame = ttk.Frame(self._form_container)
        self._btn_frame.pack(fill='x', pady=15)
        
        self._save_btn = ttk.Button(
            self._btn_frame,
            text="💾 Enregistrer",
            command=self._save
        )
        self._save_btn.pack(side='left', padx=2)
        
        self._cancel_btn = ttk.Button(
            self._btn_frame,
            text="❌ Annuler",
            command=self._cancel
        )
        self._cancel_btn.pack(side='left', padx=2)
        
        # Actions (visible seulement en consultation)
        self._actions_frame = ttk.LabelFrame(
            self._form_container, 
            text="Actions", 
            padding=10
        )
        
        self._reset_pwd_btn = ttk.Button(
            self._actions_frame,
            text="🔑 Réinitialiser mot de passe",
            command=self._reset_password
        )
        self._reset_pwd_btn.pack(fill='x', pady=2)
        
        self._toggle_btn = ttk.Button(
            self._actions_frame,
            text="🔄 Activer/Désactiver",
            command=self._toggle_status
        )
        self._toggle_btn.pack(fill='x', pady=2)
        
        self._delete_btn = ttk.Button(
            self._actions_frame,
            text="🗑️ Supprimer définitivement",
            command=self._delete_user
        )
        self._delete_btn.pack(fill='x', pady=2)
        
        # État initial
        self._set_form_state(False)
    
    def _set_form_state(self, editing: bool, is_new: bool = False) -> None:
        """Configure l'état du formulaire."""
        self._is_editing = editing
        self._is_new = is_new
        
        # Champs de base
        state = 'normal' if editing else 'disabled'
        self._username_entry.configure(state=state)
        self._fullname_entry.configure(state=state)
        self._role_combo.configure(state='readonly' if editing else 'disabled')
        
        # Checkbox actif: seulement en édition (pas création)
        if editing and not is_new:
            self._active_check.configure(state='normal')
        else:
            self._active_check.configure(state='disabled')
        
        # Section mot de passe: afficher seulement pour création
        if is_new:
            self._password_frame.pack(fill='x', pady=10, before=self._btn_frame)
            self._password_entry.configure(state='normal')
            self._confirm_entry.configure(state='normal')
            self._actions_frame.pack_forget()
        else:
            self._password_frame.pack_forget()
            self._password_var.set("")
            self._confirm_var.set("")
            # Afficher les actions si en consultation avec sélection
            if not editing and self._selected_id:
                self._actions_frame.pack(fill='x', pady=10)
            else:
                self._actions_frame.pack_forget()
        
        # Boutons de sauvegarde
        btn_state = 'normal' if editing else 'disabled'
        self._save_btn.configure(state=btn_state)
        self._cancel_btn.configure(state=btn_state)
        
        # Boutons d'actions
        action_state = 'normal' if (not editing and self._selected_id) else 'disabled'
        self._reset_pwd_btn.configure(state=action_state)
        self._toggle_btn.configure(state=action_state)
        self._delete_btn.configure(state=action_state)
    
    def _clear_form(self) -> None:
        """Efface le formulaire."""
        self._username_var.set("")
        self._fullname_var.set("")
        self._role_var.set("")
        self._password_var.set("")
        self._confirm_var.set("")
        self._active_var.set(True)
        self._selected_id = None
    
    def _load_user(self, user_id: int) -> None:
        """Charge un utilisateur dans le formulaire."""
        success, message, user = self._controller.get_user(user_id)
        
        if not success or user is None:
            AlertBox.show_error("Erreur", message, self)
            return
        
        self._selected_id = user.id
        
        self._username_var.set(user.username)
        self._fullname_var.set(user.full_name)
        self._role_var.set(self._role_map_reverse.get(user.role, user.role))
        self._active_var.set(user.is_active)
        
        self._set_form_state(False)
    
    def _on_select(self, item: dict) -> None:
        """Gère la sélection."""
        if item and 'id' in item:
            self._load_user(item['id'])
    
    def _on_double_click(self, item: dict) -> None:
        """Gère le double-clic."""
        if item and 'id' in item:
            self._load_user(item['id'])
            self._set_form_state(True, is_new=False)
    
    def _new_user(self) -> None:
        """Prépare le formulaire pour un nouvel utilisateur."""
        self._clear_form()
        self._set_form_state(True, is_new=True)
        self._username_entry.focus_set()
    
    def _save(self) -> None:
        """Enregistre l'utilisateur."""
        username = self._username_var.get().strip()
        fullname = self._fullname_var.get().strip()
        role_display = self._role_var.get()
        role = self._role_map.get(role_display, "")
        
        if not username:
            AlertBox.show_error("Erreur", "L'identifiant est obligatoire", self)
            return
        
        if not fullname:
            AlertBox.show_error("Erreur", "Le nom complet est obligatoire", self)
            return
        
        if not role:
            AlertBox.show_error("Erreur", "Le rôle est obligatoire", self)
            return
        
        if self._is_new:
            # Création
            password = self._password_var.get()
            confirm = self._confirm_var.get()
            
            if not password:
                AlertBox.show_error("Erreur", "Le mot de passe est obligatoire", self)
                return
            
            if password != confirm:
                AlertBox.show_error("Erreur", "Les mots de passe ne correspondent pas", self)
                return
            
            success, message = self._controller.create_user(
                username=username,
                password=password,
                confirm_password=confirm,
                role=role,
                full_name=fullname
            )
        else:
            # Modification
            success, message = self._controller.update_user(
                user_id=self._selected_id,
                username=username,
                role=role,
                full_name=fullname,
                is_active=self._active_var.get()
            )
        
        if success:
            AlertBox.show_success("Succès", message, self)
            self._set_form_state(False)
            self.refresh()
        else:
            AlertBox.show_error("Erreur", message, self)
    
    def _cancel(self) -> None:
        """Annule l'édition."""
        if self._selected_id:
            self._load_user(self._selected_id)
        else:
            self._clear_form()
        self._set_form_state(False)
    
    def _reset_password(self) -> None:
        """Réinitialise le mot de passe."""
        if not self._selected_id:
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Réinitialiser le mot de passe")
        dialog.geometry("350x220")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 350) // 2
        y = (dialog.winfo_screenheight() - 220) // 2
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(
            main_frame,
            text="Nouveau mot de passe:",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(anchor='w', pady=(0, 5))
        
        pwd_var = tk.StringVar()
        pwd_entry = ttk.Entry(main_frame, textvariable=pwd_var, show='•', width=35)
        pwd_entry.pack(fill='x', pady=(0, 15))
        
        ttk.Label(
            main_frame,
            text="Confirmer:",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(anchor='w', pady=(0, 5))
        
        confirm_var = tk.StringVar()
        confirm_entry = ttk.Entry(main_frame, textvariable=confirm_var, show='•', width=35)
        confirm_entry.pack(fill='x', pady=(0, 15))
        
        def do_reset():
            if pwd_var.get() != confirm_var.get():
                AlertBox.show_error("Erreur", "Les mots de passe ne correspondent pas", dialog)
                return
            
            success, message = self._controller.reset_password(
                self._selected_id,
                pwd_var.get(),
                confirm_var.get()
            )
            
            if success:
                AlertBox.show_success("Succès", message, dialog)
                dialog.destroy()
            else:
                AlertBox.show_error("Erreur", message, dialog)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_frame, text="Réinitialiser", command=do_reset).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy).pack(side='left', padx=5)
        
        pwd_entry.focus_set()
        pwd_entry.bind('<Return>', lambda e: confirm_entry.focus_set())
        confirm_entry.bind('<Return>', lambda e: do_reset())
    
    def _toggle_status(self) -> None:
        """Active ou désactive l'utilisateur."""
        if not self._selected_id:
            return
        
        success, message, user = self._controller.get_user(self._selected_id)
        if not success or not user:
            return
        
        if user.is_active:
            # Désactiver
            dialog = ConfirmDialog(
                self,
                title="Désactiver",
                message=f"Désactiver le compte de {user.full_name} ?",
                confirm_text="Désactiver",
                icon="warning"
            )
            new_status = False
        else:
            # Réactiver
            dialog = ConfirmDialog(
                self,
                title="Réactiver",
                message=f"Réactiver le compte de {user.full_name} ?",
                confirm_text="Réactiver",
                confirm_color=UI_CONFIG['success_color'],
                icon="question"
            )
            new_status = True
        
        if dialog.result:
            success, msg = self._controller.update_user(
                user_id=self._selected_id,
                username=user.username,
                role=user.role,
                full_name=user.full_name,
                is_active=new_status
            )
            
            if success:
                action = "réactivé" if new_status else "désactivé"
                AlertBox.show_success("Succès", f"Compte {action} avec succès", self)
                self._clear_form()
                self.refresh()
            else:
                AlertBox.show_error("Erreur", msg, self)
    
    def _delete_user(self) -> None:
        """Supprime définitivement un utilisateur."""
        if not self._selected_id:
            return
        
        success, message, user = self._controller.get_user(self._selected_id)
        if not success or not user:
            return
        
        # Première confirmation
        dialog = ConfirmDialog(
            self,
            title="⚠️ Suppression définitive",
            message=f"ATTENTION!\n\nCette action est IRRÉVERSIBLE.\nToutes les données liées seront perdues.\n\nSupprimer {user.full_name} ?",
            confirm_text="Supprimer",
            icon="warning"
        )
        
        if dialog.result:
            # Deuxième confirmation par saisie
            from ui.components.alert_box import InputDialog
            confirm = InputDialog(
                self,
                title="Confirmation finale",
                prompt="Tapez 'SUPPRIMER' pour confirmer:"
            )
            
            if confirm.result and confirm.result.upper() == "SUPPRIMER":
                try:
                    from database.user_repository import UserRepository
                    repo = UserRepository()
                    
                    # Vérifier qu'on ne supprime pas son propre compte
                    from services.auth_service import AuthService
                    current = AuthService.get_current_user()
                    if current and current.id == self._selected_id:
                        AlertBox.show_error("Erreur", "Vous ne pouvez pas supprimer votre propre compte", self)
                        return
                    
                    # Suppression physique
                    query = "DELETE FROM users WHERE id = ?"
                    repo.db.execute(query, (self._selected_id,))
                    
                    AlertBox.show_success("Succès", "Utilisateur supprimé définitivement", self)
                    self._clear_form()
                    self.refresh()
                    
                except Exception as e:
                    AlertBox.show_error("Erreur", f"Impossible de supprimer: {e}", self)
            else:
                AlertBox.show_info("Annulé", "Suppression annulée", self)
    
    def refresh(self) -> None:
        """Rafraîchit les données."""
        success, message, users = self._controller.get_all_users()
        
        if not success:
            AlertBox.show_error("Erreur", message, self)
            return
        
        role_labels = {
            'admin': 'Administrateur',
            'pharmacien': 'Pharmacien',
            'vendeur': 'Vendeur'
        }
        
        data = [
            {
                'id': u.id,
                'username': u.username,
                'full_name': u.full_name,
                'role': u.role,
                'role_display': role_labels.get(u.role, u.role),
                'status': "✅ Actif" if u.is_active else "❌ Inactif",
                'is_active': u.is_active
            }
            for u in users
        ]
        
        self._table.load_data(data)