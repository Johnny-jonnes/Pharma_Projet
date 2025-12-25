"""
Contrôleur de gestion des clients.

Gère les opérations CRUD sur les clients et la fidélité.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, Tuple, List
from models.client import Client
from database.client_repository import ClientRepository
from services.loyalty_service import LoyaltyService
from services.auth_service import AuthService


class ClientController:
    """
    Contrôleur pour la gestion des clients.
    
    Responsabilités:
    - CRUD des clients
    - Recherche de clients
    - Gestion de la fidélité
    """
    
    def __init__(self):
        """Initialise le contrôleur."""
        self._client_repo = ClientRepository()
        self._loyalty_service = LoyaltyService()
    
    def _check_permission(self) -> Tuple[bool, str]:
        """Vérifie les permissions de gestion des clients."""
        current = AuthService.get_current_user()
        
        if current is None:
            return False, "Utilisateur non connecté"
        
        # Admin et Pharmacien peuvent tout faire
        # Vendeur peut seulement ajouter des clients
        return True, ""
    
    def _check_edit_permission(self) -> Tuple[bool, str]:
        """Vérifie les permissions d'édition des clients."""
        current = AuthService.get_current_user()
        
        if current is None:
            return False, "Utilisateur non connecté"
        
        if current.role == 'vendeur':
            return False, "Permission refusée"
        
        return True, ""
    
    def get_all_clients(self) -> List[Client]:
        """
        Récupère tous les clients.
        
        Returns:
            List[Client]: Liste des clients
        """
        return self._client_repo.get_all()
    
    def get_client(self, client_id: int) -> Optional[Client]:
        """
        Récupère un client par son ID.
        
        Args:
            client_id: ID du client
            
        Returns:
            Optional[Client]: Client trouvé ou None
        """
        return self._client_repo.get_by_id(client_id)
    
    def search_clients(self, keyword: str) -> List[Client]:
        """
        Recherche des clients.
        
        Args:
            keyword: Mot-clé de recherche
            
        Returns:
            List[Client]: Clients correspondants
        """
        if not keyword or not keyword.strip():
            return self.get_all_clients()
        
        return self._client_repo.search(keyword.strip())
    
    def create_client(
        self,
        first_name: str,
        last_name: str,
        phone: str = "",
        email: str = "",
        address: str = ""
    ) -> Tuple[bool, str, Optional[Client]]:
        """
        Crée un nouveau client.
        
        Args:
            first_name: Prénom
            last_name: Nom
            phone: Téléphone
            email: Email
            address: Adresse
            
        Returns:
            Tuple[bool, str, Optional[Client]]: (succès, message, client)
        """
        allowed, message = self._check_permission()
        if not allowed:
            return False, message, None
        
        # Validation
        if not first_name or not first_name.strip():
            return False, "Le prénom est obligatoire", None
        
        if not last_name or not last_name.strip():
            return False, "Le nom est obligatoire", None
        
        # Vérifier unicité du téléphone
        phone_clean = phone.strip() if phone else None
        if phone_clean:
            if self._client_repo.phone_exists(phone_clean):
                return False, "Ce numéro de téléphone existe déjà", None
        
        # Générer le code client
        code = self._client_repo.generate_code()
        
        try:
            client = Client(
                code=code,
                first_name=first_name.strip().title(),
                last_name=last_name.strip().upper(),
                phone=phone_clean,
                email=email.strip().lower() if email else None,
                address=address.strip() if address else None
            )
            
            created = self._client_repo.create(client)
            return True, f"Client {created.get_full_name()} créé avec succès", created
            
        except Exception as e:
            return False, f"Erreur lors de la création: {str(e)}", None
    
    def update_client(
        self,
        client_id: int,
        first_name: str,
        last_name: str,
        phone: str = "",
        email: str = "",
        address: str = ""
    ) -> Tuple[bool, str]:
        """
        Met à jour un client.
        
        Args:
            client_id: ID du client
            first_name: Prénom
            last_name: Nom
            phone: Téléphone
            email: Email
            address: Adresse
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        allowed, message = self._check_edit_permission()
        if not allowed:
            return False, message
        
        client = self._client_repo.get_by_id(client_id)
        if client is None:
            return False, "Client non trouvé"
        
        # Validation
        if not first_name or not first_name.strip():
            return False, "Le prénom est obligatoire"
        
        if not last_name or not last_name.strip():
            return False, "Le nom est obligatoire"
        
        # Vérifier unicité du téléphone
        phone_clean = phone.strip() if phone else None
        if phone_clean and phone_clean != client.phone:
            if self._client_repo.phone_exists(phone_clean, exclude_id=client_id):
                return False, "Ce numéro de téléphone existe déjà"
        
        # Mettre à jour
        client.first_name = first_name.strip().title()
        client.last_name = last_name.strip().upper()
        client.phone = phone_clean
        client.email = email.strip().lower() if email else None
        client.address = address.strip() if address else None
        
        success = self._client_repo.update(client)
        
        if success:
            return True, "Client mis à jour avec succès"
        else:
            return False, "Erreur lors de la mise à jour"
    
    def delete_client(self, client_id: int) -> Tuple[bool, str]:
        """
        Supprime un client (désactivation).
        
        Args:
            client_id: ID du client
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        allowed, message = self._check_edit_permission()
        if not allowed:
            return False, message
        
        success = self._client_repo.delete(client_id)
        
        if success:
            return True, "Client supprimé avec succès"
        else:
            return False, "Erreur lors de la suppression"
    
    def get_client_loyalty_info(self, client_id: int) -> dict:
        """
        Récupère les informations de fidélité d'un client.
        
        Args:
            client_id: ID du client
            
        Returns:
            dict: Informations de fidélité
        """
        return self._loyalty_service.get_client_loyalty_info(client_id)
    
    def get_clients_for_table(self) -> List[dict]:
        """
        Prépare les données des clients pour affichage tableau.
        
        Returns:
            List[dict]: Données formatées
        """
        clients = self.get_all_clients()
        
        result = []
        for client in clients:
            tier_info = self._loyalty_service.get_client_tier(client)
            
            result.append({
                'id': client.id,
                'code': client.code,
                'name': client.get_full_name(),
                'phone': client.phone or "-",
                'email': client.email or "-",
                'loyalty_points': client.loyalty_points,
                'tier': tier_info.name if tier_info else "Standard",
                'total_spent': client.total_spent
            })
        
        return result
    
    def get_clients_for_combobox(self) -> List[Tuple[int, str]]:
        """
        Prépare les clients pour une liste déroulante.
        
        Returns:
            List[Tuple[int, str]]: Liste (id, libellé)
        """
        clients = self.get_all_clients()
        return [(c.id, f"{c.code} - {c.get_full_name()}") for c in clients]