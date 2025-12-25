"""
Utilitaires de hashage pour la sécurité des mots de passe.

Auteur: Alsény Camara
Version: 1.0
"""

import hashlib
import secrets
import string
from typing import Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AUTH_CONFIG


class HashUtils:
    """
    Classe utilitaire pour le hashage sécurisé des mots de passe.
    
    Utilise SHA-256 pour le hashage.
    Fournit des méthodes pour générer et vérifier les hash.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash un mot de passe avec SHA-256.
        
        Args:
            password: Mot de passe en clair
            
        Returns:
            str: Hash hexadécimal du mot de passe
            
        Raises:
            ValueError: Si le mot de passe est vide
        """
        if not password:
            raise ValueError("Le mot de passe ne peut pas être vide")
        
        # Encodage en bytes et hashage
        password_bytes = password.encode('utf-8')
        hash_object = hashlib.sha256(password_bytes)
        
        return hash_object.hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Vérifie si un mot de passe correspond à un hash.
        
        Args:
            password: Mot de passe en clair à vérifier
            password_hash: Hash stocké
            
        Returns:
            bool: True si le mot de passe correspond
        """
        if not password or not password_hash:
            return False
        
        computed_hash = HashUtils.hash_password(password)
        
        # Comparaison sécurisée (timing-safe)
        return secrets.compare_digest(computed_hash, password_hash)
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """
        Génère un mot de passe aléatoire sécurisé.
        
        Args:
            length: Longueur du mot de passe (min: 8)
            
        Returns:
            str: Mot de passe généré
        """
        if length < 8:
            length = 8
        
        # Caractères autorisés
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        
        # Assurer au moins un caractère de chaque type
        password = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
            secrets.choice("!@#$%^&*")
        ]
        
        # Compléter avec des caractères aléatoires
        password += [secrets.choice(alphabet) for _ in range(length - 4)]
        
        # Mélanger les caractères
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Valide la force d'un mot de passe.
        
        Args:
            password: Mot de passe à valider
            
        Returns:
            Tuple[bool, str]: (est_valide, message)
        """
        min_length = AUTH_CONFIG.get("password_min_length", 6)
        
        if not password:
            return False, "Le mot de passe est obligatoire"
        
        if len(password) < min_length:
            return False, f"Le mot de passe doit contenir au moins {min_length} caractères"
        
        # Vérifications optionnelles pour plus de sécurité
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "Le mot de passe doit contenir majuscules, minuscules et chiffres"
        
        return True, "Mot de passe valide"
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Génère un token aléatoire sécurisé.
        
        Args:
            length: Longueur du token
            
        Returns:
            str: Token hexadécimal
        """
        return secrets.token_hex(length // 2)