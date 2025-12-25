"""
Utilitaires pour le formatage d'affichage.

Auteur: Alsény Camara
Version: 1.0
"""

import re
from typing import Optional
from decimal import Decimal, ROUND_HALF_UP

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SALE_CONFIG


class FormatUtils:
    """
    Classe utilitaire pour le formatage des données d'affichage.
    
    Fournit des méthodes pour formater montants, pourcentages, etc.
    """
    
    @staticmethod
    def format_currency(amount: float, symbol: bool = True) -> str:
        """
        Formate un montant en devise.
        
        Args:
            amount: Montant à formater
            symbol: Inclure le symbole de devise
            
        Returns:
            str: Montant formaté (ex: "12.50 €")
        """
        if amount is None:
            amount = 0.0
        
        # Arrondir à 2 décimales
        formatted = f"{amount:,.2f}".replace(",", " ")
        
        if symbol:
            currency = SALE_CONFIG.get("currency_symbol", "€")
            return f"{formatted} {currency}"
        
        return formatted
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """
        Formate un pourcentage.
        
        Args:
            value: Valeur en pourcentage
            decimals: Nombre de décimales
            
        Returns:
            str: Pourcentage formaté (ex: "12.5%")
        """
        if value is None:
            value = 0.0
        
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_quantity(quantity: int, unit: str = "") -> str:
        """
        Formate une quantité.
        
        Args:
            quantity: Quantité
            unit: Unité (optionnel)
            
        Returns:
            str: Quantité formatée
        """
        if quantity is None:
            quantity = 0
        
        if unit:
            return f"{quantity} {unit}"
        
        return str(quantity)
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """
        Formate un numéro de téléphone.
        
        Args:
            phone: Numéro brut
            
        Returns:
            str: Numéro formaté
        """
        if not phone:
            return ""
        
        # Supprimer tous les caractères non numériques
        digits = re.sub(r'\D', '', phone)
        
        # Format français (10 chiffres): XX XX XX XX XX
        if len(digits) == 10:
            return ' '.join([digits[i:i+2] for i in range(0, 10, 2)])
        
        return phone
    
    @staticmethod
    def format_name(first_name: str, last_name: str) -> str:
        """
        Formate un nom complet.
        
        Args:
            first_name: Prénom
            last_name: Nom
            
        Returns:
            str: Nom formaté
        """
        first = (first_name or "").strip().title()
        last = (last_name or "").strip().upper()
        
        return f"{first} {last}".strip()
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Tronque un texte à une longueur maximale.
        
        Args:
            text: Texte à tronquer
            max_length: Longueur maximale
            suffix: Suffixe à ajouter si tronqué
            
        Returns:
            str: Texte tronqué
        """
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_code(prefix: str, number: int, width: int = 5) -> str:
        """
        Formate un code avec préfixe et numéro.
        
        Args:
            prefix: Préfixe (ex: "CLI", "MED")
            number: Numéro
            width: Largeur du numéro (padding zeros)
            
        Returns:
            str: Code formaté (ex: "CLI-00001")
        """
        return f"{prefix}-{number:0{width}d}"
    
    @staticmethod
    def round_currency(amount: float) -> float:
        """
        Arrondit un montant à 2 décimales (arrondi commercial).
        
        Args:
            amount: Montant à arrondir
            
        Returns:
            float: Montant arrondi
        """
        if amount is None:
            return 0.0
        
        decimal_amount = Decimal(str(amount))
        rounded = decimal_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return float(rounded)
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Nettoie une entrée utilisateur.
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            str: Texte nettoyé
        """
        if not text:
            return ""
        
        # Supprimer les espaces en début/fin
        text = text.strip()
        
        # Remplacer les espaces multiples par un seul
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Formate une taille de fichier.
        
        Args:
            size_bytes: Taille en octets
            
        Returns:
            str: Taille formatée (ex: "1.5 MB")
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    @staticmethod
    def pluralize(count: int, singular: str, plural: str = None) -> str:
        """
        Retourne le mot au singulier ou pluriel selon le compte.
        
        Args:
            count: Nombre d'éléments
            singular: Forme singulière
            plural: Forme plurielle (par défaut: singulier + 's')
            
        Returns:
            str: Chaîne formatée avec le nombre
        """
        if plural is None:
            plural = singular + 's'
        
        word = singular if count <= 1 else plural
        return f"{count} {word}"