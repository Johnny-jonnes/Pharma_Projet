"""
Vue du point de vente (POS).

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
from controllers.sale_controller import SaleController
from controllers.client_controller import ClientController
from controllers.medicament_controller import MedicamentController
from ui.components.data_table import DataTable
from ui.components.alert_box import AlertBox, ConfirmDialog
from utils.format_utils import FormatUtils


class SaleView(ttk.Frame):
    """
    Vue du point de vente.
    """
    
    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, **kwargs)
        
        self._sale_controller = SaleController()
        self._client_controller = ClientController()
        self._med_controller = MedicamentController()
        
        self._create_widgets()
        self._new_sale()
    
    def _create_widgets(self) -> None:
        """Crée les widgets."""
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_cart_section()
        self._create_checkout_section()
    
    def _create_header(self) -> None:
        """Crée l'en-tête."""
        header = ttk.Frame(self)
        header.grid(row=0, column=0, columnspan=2, sticky='ew', padx=20, pady=(20, 10))
        
        ttk.Label(
            header,
            text="🛒 Point de Vente",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_title'], 'bold')
        ).pack(side='left')
        
        ttk.Button(
            header,
            text="🆕 Nouvelle vente",
            command=self._new_sale
        ).pack(side='right')
    
    def _create_cart_section(self) -> None:
        """Crée la section panier."""
        cart_frame = ttk.Frame(self)
        cart_frame.grid(row=1, column=0, sticky='nsew', padx=(20, 10), pady=(0, 20))
        cart_frame.columnconfigure(0, weight=1)
        cart_frame.rowconfigure(1, weight=1)
        
        # Barre d'ajout de produit
        add_frame = ttk.LabelFrame(cart_frame, text="Ajouter un produit", padding=10)
        add_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(add_frame, text="Code ou nom:").pack(side='left', padx=(0, 5))
        
        self._product_var = tk.StringVar()
        self._product_entry = ttk.Entry(
            add_frame,
            textvariable=self._product_var,
            width=25,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        )
        self._product_entry.pack(side='left', padx=(0, 10))
        self._product_entry.bind('<Return>', lambda e: self._add_product())
        
        ttk.Label(add_frame, text="Qté:").pack(side='left', padx=(0, 5))
        
        self._qty_var = tk.StringVar(value="1")
        self._qty_entry = ttk.Entry(add_frame, textvariable=self._qty_var, width=5)
        self._qty_entry.pack(side='left', padx=(0, 10))
        
        ttk.Button(add_frame, text="➕ Ajouter", command=self._add_product).pack(side='left')
        ttk.Button(add_frame, text="🔍 Rechercher", command=self._search_products).pack(side='left', padx=(10, 0))
        
        # Tableau du panier
        cart_list_frame = ttk.LabelFrame(cart_frame, text="Panier", padding=10)
        cart_list_frame.grid(row=1, column=0, sticky='nsew')
        cart_list_frame.columnconfigure(0, weight=1)
        cart_list_frame.rowconfigure(0, weight=1)
        
        columns = [
            {'key': 'code', 'label': 'Code', 'width': 80},
            {'key': 'name', 'label': 'Produit', 'width': 200},
            {'key': 'quantity', 'label': 'Qté', 'width': 50, 'anchor': 'center'},
            {'key': 'unit_price_display', 'label': 'Prix unit.', 'width': 100, 'anchor': 'e'},
            {'key': 'line_total_display', 'label': 'Total', 'width': 100, 'anchor': 'e'}
        ]
        
        self._cart_table = DataTable(
            cart_list_frame,
            columns=columns,
            show_search=False,
            on_select=self._on_cart_select,
            height=12
        )
        self._cart_table.grid(row=0, column=0, sticky='nsew')
        
        # Boutons panier
        cart_btn_frame = ttk.Frame(cart_list_frame)
        cart_btn_frame.grid(row=1, column=0, sticky='ew', pady=(10, 0))
        
        self._remove_btn = ttk.Button(
            cart_btn_frame,
            text="🗑️ Retirer",
            command=self._remove_from_cart,
            state='disabled'
        )
        self._remove_btn.pack(side='left', padx=2)
        
        ttk.Button(
            cart_btn_frame,
            text="🔄 Modifier qté",
            command=self._modify_quantity
        ).pack(side='left', padx=2)
        
        ttk.Button(
            cart_btn_frame,
            text="🗑️ Vider panier",
            command=self._clear_cart
        ).pack(side='right', padx=2)
    
    def _create_checkout_section(self) -> None:
        """Crée la section de validation."""
        checkout_frame = ttk.Frame(self)
        checkout_frame.grid(row=1, column=1, sticky='nsew', padx=(10, 20), pady=(0, 20))
        checkout_frame.columnconfigure(0, weight=1)
        
        # Client
        client_frame = ttk.LabelFrame(checkout_frame, text="👤 Client", padding=10)
        client_frame.pack(fill='x', pady=(0, 10))
        
        self._client_var = tk.StringVar(value="Aucun client")
        ttk.Label(
            client_frame,
            textvariable=self._client_var,
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal'])
        ).pack(anchor='w')
        
        client_btn_frame = ttk.Frame(client_frame)
        client_btn_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(client_btn_frame, text="🔍 Sélectionner", command=self._select_client).pack(side='left', padx=2)
        ttk.Button(client_btn_frame, text="➕ Nouveau", command=self._new_client).pack(side='left', padx=2)
        
        self._remove_client_btn = ttk.Button(
            client_btn_frame,
            text="❌",
            command=self._remove_client,
            width=3,
            state='disabled'
        )
        self._remove_client_btn.pack(side='right')
        
        # Totaux
        totals_frame = ttk.LabelFrame(checkout_frame, text="💰 Totaux", padding=15)
        totals_frame.pack(fill='x', pady=(0, 10))
        
        # Sous-total
        row1 = ttk.Frame(totals_frame)
        row1.pack(fill='x', pady=2)
        ttk.Label(row1, text="Sous-total:").pack(side='left')
        self._subtotal_var = tk.StringVar(value="0 GNF")
        ttk.Label(row1, textvariable=self._subtotal_var).pack(side='right')
        
        # Remise
        row2 = ttk.Frame(totals_frame)
        row2.pack(fill='x', pady=2)
        ttk.Label(row2, text="Remise fidélité:").pack(side='left')
        self._discount_var = tk.StringVar(value="- 0 GNF (0%)")
        ttk.Label(row2, textvariable=self._discount_var, foreground=UI_CONFIG['success_color']).pack(side='right')
        
        ttk.Separator(totals_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Total
        row3 = ttk.Frame(totals_frame)
        row3.pack(fill='x', pady=2)
        ttk.Label(row3, text="TOTAL:", font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_large'], 'bold')).pack(side='left')
        self._total_var = tk.StringVar(value="0 GNF")
        ttk.Label(
            row3,
            textvariable=self._total_var,
            font=(UI_CONFIG['font_family'], 24, 'bold'),
            foreground=UI_CONFIG['primary_color']
        ).pack(side='right')
        
        # Points et articles
        row4 = ttk.Frame(totals_frame)
        row4.pack(fill='x', pady=(10, 0))
        ttk.Label(row4, text="Points gagnés:").pack(side='left')
        self._points_var = tk.StringVar(value="+0 points")
        ttk.Label(row4, textvariable=self._points_var, foreground=UI_CONFIG['success_color']).pack(side='right')
        
        row5 = ttk.Frame(totals_frame)
        row5.pack(fill='x', pady=2)
        ttk.Label(row5, text="Articles:", foreground='gray').pack(side='left')
        self._items_count_var = tk.StringVar(value="0")
        ttk.Label(row5, textvariable=self._items_count_var, foreground='gray').pack(side='right')
        
        # Bouton de validation
        self._validate_btn = tk.Button(
            checkout_frame,
            text="✅ VALIDER LA VENTE",
            command=self._validate_sale,
            bg=UI_CONFIG['success_color'],
            fg='white',
            font=(UI_CONFIG['font_family'], 14, 'bold'),
            relief='flat',
            cursor='hand2',
            pady=15
        )
        self._validate_btn.pack(fill='x', pady=10)
        
        # Historique rapide
        history_frame = ttk.LabelFrame(checkout_frame, text="📜 Dernières ventes", padding=10)
        history_frame.pack(fill='both', expand=True)
        
        self._history_list = tk.Listbox(history_frame, font=(UI_CONFIG['font_family'], 9), height=6)
        self._history_list.pack(fill='both', expand=True)
    
    def _new_sale(self) -> None:
        """Démarre une nouvelle vente."""
        self._sale_controller.new_sale()
        self._client_var.set("Aucun client")
        self._remove_client_btn.configure(state='disabled')
        self._refresh_cart()
        self._product_entry.focus_set()
        self._update_history()
    
    def _add_product(self) -> None:
        """Ajoute un produit au panier."""
        code = self._product_var.get().strip()
        qty = self._qty_var.get().strip()
        
        if not code:
            AlertBox.show_warning("Attention", "Veuillez entrer un code ou nom de produit", self)
            return
        
        # Essayer par code exact
        success, message = self._sale_controller.add_product_by_code(code, qty)
        
        if not success:
            # Rechercher
            meds = self._med_controller.search_medicaments(keyword=code, in_stock_only=True)
            
            if len(meds) == 1:
                success, message = self._sale_controller.add_product(meds[0].id, qty)
            elif len(meds) > 1:
                self._show_product_selection(meds)
                return
            else:
                AlertBox.show_error("Erreur", f"Produit '{code}' non trouvé", self)
                return
        
        if success:
            self._product_var.set("")
            self._qty_var.set("1")
            self._refresh_cart()
            self._product_entry.focus_set()
        else:
            AlertBox.show_error("Erreur", message, self)
    
    def _show_product_selection(self, products: list) -> None:
        """Affiche une fenêtre de sélection de produit."""
        dialog = tk.Toplevel(self)
        dialog.title("Sélectionner un produit")
        dialog.geometry("500x350")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 500) // 2
        y = (dialog.winfo_screenheight() - 350) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(
            dialog,
            text="Plusieurs produits correspondent. Sélectionnez:",
            font=(UI_CONFIG['font_family'], UI_CONFIG['font_size_normal']),
            padding=10
        ).pack()
        
        # Frame pour listbox + scrollbar
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        listbox = tk.Listbox(
            list_frame,
            font=(UI_CONFIG['font_family'], 10),
            yscrollcommand=scrollbar.set,
            selectmode='single'
        )
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=listbox.yview)
        
        for med in products:
            listbox.insert(tk.END, f"{med.code} - {med.name} (Stock: {med.quantity_in_stock}, Prix: {med.selling_price:.0f})")
        
        # Sélectionner le premier par défaut
        if products:
            listbox.selection_set(0)
        
        def select():
            selection = listbox.curselection()
            if selection:
                med = products[selection[0]]
                success, message = self._sale_controller.add_product(med.id, self._qty_var.get())
                if success:
                    self._product_var.set("")
                    self._qty_var.set("1")
                    self._refresh_cart()
                    dialog.destroy()
                else:
                    AlertBox.show_error("Erreur", message, dialog)
            else:
                AlertBox.show_warning("Attention", "Veuillez sélectionner un produit", dialog)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="✅ Ajouter au panier", command=select).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Annuler", command=dialog.destroy).pack(side='left', padx=5)
        
        listbox.bind('<Double-1>', lambda e: select())
        dialog.bind('<Return>', lambda e: select())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def _search_products(self) -> None:
        """Ouvre la recherche de produits."""
        dialog = tk.Toplevel(self)
        dialog.title("Rechercher un produit")
        dialog.geometry("650x450")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 650) // 2
        y = (dialog.winfo_screenheight() - 450) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Barre de recherche
        search_frame = ttk.Frame(dialog, padding=10)
        search_frame.pack(fill='x')
        
        ttk.Label(search_frame, text="Rechercher:").pack(side='left', padx=(0, 5))
        
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side='left', padx=(0, 10))
        
        # Frame pour tableau
        table_frame = ttk.Frame(dialog)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview pour les résultats
        columns = ('code', 'name', 'price', 'stock')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        tree.heading('code', text='Code')
        tree.heading('name', text='Nom')
        tree.heading('price', text='Prix')
        tree.heading('stock', text='Stock')
        
        tree.column('code', width=80)
        tree.column('name', width=280)
        tree.column('price', width=100, anchor='e')
        tree.column('stock', width=80, anchor='center')
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Stocker les médicaments pour la sélection
        med_dict = {}
        
        def search(*args):
            # Effacer les résultats précédents
            for item in tree.get_children():
                tree.delete(item)
            med_dict.clear()
            
            keyword = search_var.get()
            meds = self._med_controller.search_medicaments(keyword=keyword, in_stock_only=True)
            
            for med in meds:
                item_id = tree.insert('', 'end', values=(
                    med.code,
                    med.name,
                    f"{med.selling_price:,.0f} GNF",
                    med.quantity_in_stock
                ))
                med_dict[item_id] = med
        
        search_var.trace_add('write', search)
        
        def add_selected():
            selection = tree.selection()
            if selection:
                med = med_dict.get(selection[0])
                if med:
                    success, message = self._sale_controller.add_product(med.id, "1")
                    if success:
                        self._refresh_cart()
                        dialog.destroy()
                    else:
                        AlertBox.show_error("Erreur", message, dialog)
            else:
                AlertBox.show_warning("Attention", "Veuillez sélectionner un produit", dialog)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="✅ Ajouter au panier", command=add_selected).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Fermer", command=dialog.destroy).pack(side='left', padx=5)
        
        tree.bind('<Double-1>', lambda e: add_selected())
        dialog.bind('<Return>', lambda e: add_selected())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Charger tous les produits initialement
        search()
        search_entry.focus_set()
    
    def _on_cart_select(self, item: dict) -> None:
        """Gère la sélection dans le panier."""
        if item:
            self._remove_btn.configure(state='normal')
        else:
            self._remove_btn.configure(state='disabled')
    
    def _remove_from_cart(self) -> None:
        """Retire le produit sélectionné."""
        selected = self._cart_table.get_selected()
        if selected:
            self._sale_controller.remove_product(selected['id'])
            self._refresh_cart()
    
    def _modify_quantity(self) -> None:
        """Modifie la quantité d'un produit."""
        selected = self._cart_table.get_selected()
        if not selected:
            AlertBox.show_warning("Attention", "Sélectionnez un produit", self)
            return
        
        from ui.components.alert_box import InputDialog
        dialog = InputDialog(
            self,
            title="Modifier la quantité",
            prompt=f"Nouvelle quantité pour {selected['name']}:",
            initial_value=str(selected['quantity']),
            input_type="number"
        )
        
        if dialog.result:
            success, message = self._sale_controller.update_quantity(selected['id'], dialog.result)
            if success:
                self._refresh_cart()
            else:
                AlertBox.show_error("Erreur", message, self)
    
    def _clear_cart(self) -> None:
        """Vide le panier."""
        if self._sale_controller.get_cart().is_empty():
            return
        
        dialog = ConfirmDialog(
            self,
            title="Confirmation",
            message="Vider le panier ?",
            confirm_text="Vider",
            icon="question"
        )
        
        if dialog.result:
            self._new_sale()
    
    def _select_client(self) -> None:
        """Sélectionne un client."""
        dialog = tk.Toplevel(self)
        dialog.title("Sélectionner un client")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 500) // 2
        y = (dialog.winfo_screenheight() - 400) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Recherche
        search_frame = ttk.Frame(dialog, padding=10)
        search_frame.pack(fill='x')
        
        ttk.Label(search_frame, text="Rechercher:").pack(side='left', padx=(0, 5))
        
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side='left')
        
        # Liste
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        listbox = tk.Listbox(
            list_frame,
            font=(UI_CONFIG['font_family'], 10),
            yscrollcommand=scrollbar.set
        )
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=listbox.yview)
        
        clients = self._client_controller.get_all_clients()
        filtered_clients = []
        
        def filter_clients(*args):
            nonlocal filtered_clients
            keyword = search_var.get().lower()
            listbox.delete(0, tk.END)
            filtered_clients = []
            
            for c in clients:
                name = c.get_full_name().lower()
                if keyword in name or keyword in (c.phone or "").lower() or keyword in c.code.lower():
                    listbox.insert(tk.END, f"{c.code} - {c.get_full_name()} ({c.loyalty_points} pts)")
                    filtered_clients.append(c)
            
            if filtered_clients:
                listbox.selection_set(0)
        
        search_var.trace_add('write', filter_clients)
        filter_clients()
        
        def select():
            selection = listbox.curselection()
            if selection and filtered_clients:
                client = filtered_clients[selection[0]]
                success, message = self._sale_controller.set_client(client.id)
                if success:
                    self._client_var.set(f"{client.code} - {client.get_full_name()}")
                    self._remove_client_btn.configure(state='normal')
                    self._refresh_cart()
                dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="✅ Sélectionner", command=select).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Annuler", command=dialog.destroy).pack(side='left', padx=5)
        
        listbox.bind('<Double-1>', lambda e: select())
        dialog.bind('<Return>', lambda e: select())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        search_entry.focus_set()
    
    def _new_client(self) -> None:
        """Crée un nouveau client rapidement."""
        from ui.components.alert_box import InputDialog
        
        # Prénom
        first = InputDialog(self, "Nouveau client", "Prénom:")
        if not first.result:
            return
        
        # Nom
        last = InputDialog(self, "Nouveau client", "Nom de famille:")
        if not last.result:
            return
        
        # Téléphone
        phone = InputDialog(self, "Nouveau client", "Téléphone (optionnel):")
        
        success, message, client = self._client_controller.create_client(
            first_name=first.result,
            last_name=last.result,
            phone=phone.result or ""
        )
        
        if success and client:
            self._sale_controller.set_client(client.id)
            self._client_var.set(f"{client.code} - {client.get_full_name()}")
            self._remove_client_btn.configure(state='normal')
            self._refresh_cart()
            AlertBox.show_success("Succès", f"Client {client.get_full_name()} créé", self)
        else:
            AlertBox.show_error("Erreur", message, self)
    
    def _remove_client(self) -> None:
        """Retire le client de la vente."""
        self._sale_controller.remove_client()
        self._client_var.set("Aucun client")
        self._remove_client_btn.configure(state='disabled')
        self._refresh_cart()
    
    def _refresh_cart(self) -> None:
        """Rafraîchit l'affichage du panier."""
        items = self._sale_controller.get_cart_items_for_table()
        self._cart_table.load_data(items)
        
        totals = self._sale_controller.get_totals()
        
        self._subtotal_var.set(totals['subtotal_display'])
        self._discount_var.set(f"- {totals['discount_amount_display']} ({totals['discount_display']})")
        self._total_var.set(totals['total_display'])
        self._points_var.set(f"+{totals['points_earned']} points")
        self._items_count_var.set(str(totals['items_count']))
        
        if self._sale_controller.get_cart().is_empty():
            self._validate_btn.configure(state='disabled')
        else:
            self._validate_btn.configure(state='normal')
    
    def _validate_sale(self) -> None:
        """Valide la vente."""
        if self._sale_controller.get_cart().is_empty():
            AlertBox.show_warning("Attention", "Le panier est vide", self)
            return
        
        totals = self._sale_controller.get_totals()
        
        dialog = ConfirmDialog(
            self,
            title="Confirmer la vente",
            message=f"Valider la vente ?\n\nTotal: {totals['total_display']}",
            confirm_text="Valider",
            confirm_color=UI_CONFIG['success_color'],
            icon="question"
        )
        
        if dialog.result:
            success, message, sale = self._sale_controller.validate_sale()
            
            if success:
                AlertBox.show_success("Succès", message, self)
                
                if AlertBox.ask_yes_no("Ticket", "Imprimer le ticket ?", self):
                    self._print_receipt(sale.id)
                
                self._new_sale()
            else:
                AlertBox.show_error("Erreur", message, self)
    
    def _print_receipt(self, sale_id: int) -> None:
        """Génère et affiche le ticket."""
        try:
            from utils.pdf_generator import PDFGenerator
            
            receipt_data = self._sale_controller.get_sale_for_receipt(sale_id)
            
            # Utiliser la bonne méthode
            filepath = PDFGenerator.generate_receipt(receipt_data)
            
            # Ouvrir le fichier
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', filepath])
            else:
                subprocess.call(['xdg-open', filepath])
                
            AlertBox.show_info("Ticket", f"Ticket généré: {filepath}", self)
                
        except Exception as e:
            AlertBox.show_error("Erreur", f"Impossible de générer le ticket: {e}", self)
    
    def _update_history(self) -> None:
        """Met à jour l'historique des ventes."""
        self._history_list.delete(0, tk.END)
        
        sales = self._sale_controller.get_today_sales()[:10]
        
        for sale in sales:
            status = "✅" if sale.status == 'completed' else "❌"
            total = FormatUtils.format_currency(sale.total)
            time_str = sale.sale_date.strftime("%H:%M")
            seller = sale.seller_name or "?"
            self._history_list.insert(tk.END, f"{status} {sale.sale_number} - {total} ({time_str}) - {seller}")
    
    def refresh(self) -> None:
        """Rafraîchit la vue."""
        self._refresh_cart()
        self._update_history()