"""
Utilitaires de validation des données.

Auteur: Alsény Camara
Version: 1.0
"""

import re
from typing import Optional, Tuple
from datetime import date


class Validators:
    """
    Classe utilitaire pour la validation des données.
    """
    
    @staticmethod
    def validate_required(value: str, field_name: str) -> Tuple[bool, str]:
        """
        Valide qu'un champ n'est pas vide.
        
        Args:
            value: Valeur à valider
            field_name: Nom du champ pour le message
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        if not value or not str(value).strip():
            return False, f"Le champ '{field_name}' est obligatoire"
        return True, ""
    
    @staticmethod
    def validate_min_length(
        value: str, 
        min_length: int, 
        field_name: str
    ) -> Tuple[bool, str]:
        """
        Valide la longueur minimale d'une chaîne.
        
        Args:
            value: Valeur à valider
            min_length: Longueur minimale
            field_name: Nom du champ
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        if not value or len(value) < min_length:
            return False, f"Le champ '{field_name}' doit contenir au moins {min_length} caractères"
        return True, ""
    
    @staticmethod
    def validate_max_length(
        value: str, 
        max_length: int, 
        field_name: str
    ) -> Tuple[bool, str]:
        """
        Valide la longueur maximale d'une chaîne.
        
        Args:
            value: Valeur à valider
            max_length: Longueur maximale
            field_name: Nom du champ
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        if value and len(value) > max_length:
            return False, f"Le champ '{field_name}' ne doit pas dépasser {max_length} caractères"
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Valide un format d'email.
        
        Args:
            email: Email à valider
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        if not email:
            return True, ""  # Email optionnel
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Format d'email invalide"
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Valide un format de téléphone.
        
        Args:
            phone: Téléphone à valider
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        if not phone:
            return True, ""  # Téléphone optionnel
        
        # Nettoyer et vérifier
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 8 or len(digits) > 15:
            return False, "Format de téléphone invalide"
        return True, ""
    
    @staticmethod
    def validate_positive_number(
        value: float, 
        field_name: str,
        allow_zero: bool = True
    ) -> Tuple[bool, str]:
        """
        Valide qu'un nombre est positif.
        
        Args:
            value: Valeur à valider
            field_name: Nom du champ
            allow_zero: Autoriser zéro
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        try:
            num = float(value)
            if allow_zero:
                if num < 0:
                    return False, f"Le champ '{field_name}' ne peut pas être négatif"
            else:
                if num <= 0:
                    return False, f"Le champ '{field_name}' doit être supérieur à zéro"
            return True, ""
        except (ValueError, TypeError):
            return False, f"Le champ '{field_name}' doit être un nombre valide"
    
    @staticmethod
    def validate_integer(
        value: str, 
        field_name: str
    ) -> Tuple[bool, str]:
        """
        Valide qu'une valeur est un entier.
        
        Args:
            value: Valeur à valider
            field_name: Nom du champ
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        try:
            int(value)
            return True, ""
        except (ValueError, TypeError):
            return False, f"Le champ '{field_name}' doit être un nombre entier"
    
    @staticmethod
    def validate_date_not_past(
        d: date, 
        field_name: str
    ) -> Tuple[bool, str]:
        """
        Valide qu'une date n'est pas dans le passé.
        
        Args:
            d: Date à valider
            field_name: Nom du champ
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        if d and d < date.today():
            return False, f"Le champ '{field_name}' ne peut pas être dans le passé"
        return True, ""
    
    @staticmethod
    def validate_date_range(
        start_date: date, 
        end_date: date
    ) -> Tuple[bool, str]:
        """
        Valide que la date de début est avant la date de fin.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        if start_date and end_date and start_date > end_date:
            return False, "La date de début doit être antérieure à la date de fin"
        return True, ""
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Valide la force d'un mot de passe.
        
        Args:
            password: Mot de passe à valider
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        if len(password) < 6:
            return False, "Le mot de passe doit contenir au moins 6 caractères"
        
        # Optionnel: vérifications supplémentaires
        # if not re.search(r'[A-Z]', password):
        #     return False, "Le mot de passe doit contenir au moins une majuscule"
        # if not re.search(r'[0-9]', password):
        #     return False, "Le mot de passe doit contenir au moins un chiffre"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Valide un nom d'utilisateur.
        
        Args:
            username: Nom d'utilisateur à valider
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        if not username:
            return False, "Le nom d'utilisateur est obligatoire"
        
        if len(username) < 3:
            return False, "Le nom d'utilisateur doit contenir au moins 3 caractères"
        
        if len(username) > 50:
            return False, "Le nom d'utilisateur ne doit pas dépasser 50 caractères"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Le nom d'utilisateur ne peut contenir que des lettres, chiffres et underscores"
        
        return True, ""
    
    @staticmethod
    def validate_code(code: str, prefix: str = None) -> Tuple[bool, str]:
        """
        Valide un code (médicament, client, etc.).
        
        Args:
            code: Code à valider
            prefix: Préfixe attendu (optionnel)
            
        Returns:
            Tuple[bool, str]: (valide, message d'erreur)
        """
        if not code:
            return False, "Le code est obligatoire"
        
        if len(code) > 50:
            return False, "Le code ne doit pas dépasser 50 caractères"
        
        if prefix and not code.startswith(prefix):
            return False, f"Le code doit commencer par '{prefix}'"
        
        return True, ""