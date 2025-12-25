"""
Repository de base - Classe abstraite pour tous les repositories.

Auteur: Alsény Camara
Version: 1.0
"""

from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar, Generic
from database.database_manager import DatabaseManager

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Classe abstraite définissant l'interface commune des repositories.
    
    Implémente le pattern Repository pour abstraire l'accès aux données.
    Chaque repository concret doit implémenter les méthodes CRUD.
    """
    
    def __init__(self):
        """Initialise le repository avec la connexion DB."""
        self._db = DatabaseManager()
    
    @property
    def db(self) -> DatabaseManager:
        """Retourne l'instance du gestionnaire de base de données."""
        return self._db
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """
        Crée une nouvelle entité en base de données.
        
        Args:
            entity: Entité à créer
            
        Returns:
            T: Entité créée avec son ID
        """
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Récupère une entité par son ID.
        
        Args:
            entity_id: Identifiant de l'entité
            
        Returns:
            Optional[T]: Entité trouvée ou None
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Récupère toutes les entités.
        
        Returns:
            List[T]: Liste de toutes les entités
        """
        pass
    
    @abstractmethod
    def update(self, entity: T) -> bool:
        """
        Met à jour une entité existante.
        
        Args:
            entity: Entité à mettre à jour
            
        Returns:
            bool: True si mise à jour réussie
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """
        Supprime une entité (logique ou physique).
        
        Args:
            entity_id: ID de l'entité à supprimer
            
        Returns:
            bool: True si suppression réussie
        """
        pass