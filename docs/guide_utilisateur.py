"""
Générateur du Guide Utilisateur PDF.

Auteur: Alsény Camara
Version: 1.0
"""

import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm, mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, ListFlowable, ListItem
    )
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Installez reportlab: pip install reportlab")


class GuideUtilisateurGenerator:
    """Génère le guide utilisateur en PDF."""
    
    def __init__(self, output_path: str = "Guide_Utilisateur_PharmacieManager.pdf"):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configure les styles personnalisés."""
        # Titre principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#1976D2')
        ))
        
        # Titre de chapitre
        self.styles.add(ParagraphStyle(
            name='ChapterTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceBefore=20,
            spaceAfter=15,
            textColor=colors.HexColor('#1976D2'),
            borderWidth=1,
            borderColor=colors.HexColor('#1976D2'),
            borderPadding=10,
            backColor=colors.HexColor('#E3F2FD')
        ))
        
        # Titre de section
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#1976D2')
        ))
        
        # Sous-titre
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=8,
            textColor=colors.HexColor('#424242')
        ))
        
        # Texte normal
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14
        ))
        
        # Note importante
        self.styles.add(ParagraphStyle(
            name='ImportantNote',
            parent=self.styles['Normal'],
            fontSize=10,
            backColor=colors.HexColor('#FFF3E0'),
            borderWidth=1,
            borderColor=colors.HexColor('#FF9800'),
            borderPadding=10,
            spaceAfter=10
        ))
        
        # Astuce
        self.styles.add(ParagraphStyle(
            name='Tip',
            parent=self.styles['Normal'],
            fontSize=10,
            backColor=colors.HexColor('#E8F5E9'),
            borderWidth=1,
            borderColor=colors.HexColor('#4CAF50'),
            borderPadding=10,
            spaceAfter=10
        ))
    
    def generate(self):
        """Génère le document PDF complet."""
        if not REPORTLAB_AVAILABLE:
            print("ReportLab non disponible")
            return
        
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        
        # Page de garde
        elements.extend(self._create_cover_page())
        elements.append(PageBreak())
        
        # Table des matières
        elements.extend(self._create_table_of_contents())
        elements.append(PageBreak())
        
        # Chapitre 1: Introduction
        elements.extend(self._create_chapter_introduction())
        elements.append(PageBreak())
        
        # Chapitre 2: Connexion
        elements.extend(self._create_chapter_connexion())
        elements.append(PageBreak())
        
        # Chapitre 3: Tableau de bord
        elements.extend(self._create_chapter_dashboard())
        elements.append(PageBreak())
        
        # Chapitre 4: Gestion des médicaments
        elements.extend(self._create_chapter_medicaments())
        elements.append(PageBreak())
        
        # Chapitre 5: Point de vente
        elements.extend(self._create_chapter_pos())
        elements.append(PageBreak())
        
        # Chapitre 6: Gestion des clients
        elements.extend(self._create_chapter_clients())
        elements.append(PageBreak())
        
        # Chapitre 7: Rapports
        elements.extend(self._create_chapter_reports())
        elements.append(PageBreak())
        
        # Chapitre 8: Administration
        elements.extend(self._create_chapter_admin())
        elements.append(PageBreak())
        
        # Chapitre 9: FAQ
        elements.extend(self._create_chapter_faq())
        
        # Générer le PDF
        doc.build(elements)
        print(f"Guide généré : {self.output_path}")
    
    def _create_cover_page(self):
        """Crée la page de garde."""
        elements = []
        
        elements.append(Spacer(1, 3*cm))
        
        elements.append(Paragraph(
            "PHARMACIE MANAGER",
            self.styles['MainTitle']
        ))
        
        elements.append(Spacer(1, 1*cm))
        
        elements.append(Paragraph(
            "Guide Utilisateur Complet",
            ParagraphStyle(
                'Subtitle',
                parent=self.styles['Heading2'],
                fontSize=16,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#757575')
            )
        ))
        
        elements.append(Spacer(1, 2*cm))
        
        elements.append(Paragraph(
            "Version 1.0",
            ParagraphStyle('Version', alignment=TA_CENTER, fontSize=12)
        ))
        
        elements.append(Spacer(1, 5*cm))
        
        # Informations
        info_data = [
            ['Application', 'PharmacieManager v1.0'],
            ['Type', 'Système de Gestion de Pharmacie'],
            ['Plateforme', 'Windows 10/11'],
            ['Auteur', 'Alsény Camara'],
            ['Date', datetime.now().strftime('%d/%m/%Y')]
        ]
        
        info_table = Table(info_data, colWidths=[5*cm, 8*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDBDBD')),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(info_table)
        
        return elements
    
    def _create_table_of_contents(self):
        """Crée la table des matières."""
        elements = []
        
        elements.append(Paragraph("TABLE DES MATIÈRES", self.styles['ChapterTitle']))
        elements.append(Spacer(1, 1*cm))
        
        toc_items = [
            ("1. Introduction", "3"),
            ("   1.1 Présentation de l'application", "3"),
            ("   1.2 Configuration requise", "3"),
            ("   1.3 Rôles utilisateurs", "4"),
            ("2. Connexion et Authentification", "5"),
            ("   2.1 Écran de connexion", "5"),
            ("   2.2 Gestion du mot de passe", "5"),
            ("3. Tableau de Bord", "6"),
            ("   3.1 Vue d'ensemble", "6"),
            ("   3.2 Indicateurs clés", "6"),
            ("   3.3 Alertes", "7"),
            ("4. Gestion des Médicaments", "8"),
            ("   4.1 Liste des médicaments", "8"),
            ("   4.2 Ajouter un médicament", "9"),
            ("   4.3 Modifier un médicament", "10"),
            ("   4.4 Gestion du stock", "11"),
            ("5. Point de Vente (POS)", "12"),
            ("   5.1 Interface de vente", "12"),
            ("   5.2 Processus de vente", "13"),
            ("   5.3 Gestion du panier", "14"),
            ("   5.4 Validation et ticket", "15"),
            ("6. Gestion des Clients", "16"),
            ("   6.1 Fichier clients", "16"),
            ("   6.2 Programme de fidélité", "17"),
            ("7. Rapports et Statistiques", "18"),
            ("   7.1 Ventes par vendeur", "18"),
            ("   7.2 État du stock", "19"),
            ("   7.3 Top produits", "20"),
            ("   7.4 Export des données", "20"),
            ("8. Administration", "21"),
            ("   8.1 Gestion des utilisateurs", "21"),
            ("   8.2 Paramètres", "22"),
            ("9. FAQ et Dépannage", "23"),
        ]
        
        for item, page in toc_items:
            row = Table(
                [[item, page]],
                colWidths=[14*cm, 2*cm]
            )
            row.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(row)
        
        return elements
    
    def _create_chapter_introduction(self):
        """Chapitre 1: Introduction."""
        elements = []
        
        elements.append(Paragraph("1. INTRODUCTION", self.styles['ChapterTitle']))
        
        # 1.1 Présentation
        elements.append(Paragraph("1.1 Présentation de l'application", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """PharmacieManager est une application de bureau professionnelle conçue pour 
            la gestion complète d'une pharmacie. Elle permet de gérer les médicaments, 
            les ventes, les clients, le stock et de générer des rapports détaillés.""",
            self.styles['NormalText']
        ))
        
        elements.append(Paragraph("Fonctionnalités principales :", self.styles['SubTitle']))
        
        features = [
            "✓ Gestion complète du catalogue de médicaments",
            "✓ Point de vente (POS) intuitif et rapide",
            "✓ Suivi des stocks avec alertes automatiques",
            "✓ Gestion des clients et programme de fidélité",
            "✓ Rapports et statistiques détaillés",
            "✓ Génération de tickets de caisse PDF",
            "✓ Multi-utilisateurs avec gestion des rôles",
            "✓ Fonctionne hors ligne (pas besoin d'internet)"
        ]
        
        for feature in features:
            elements.append(Paragraph(feature, self.styles['NormalText']))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 1.2 Configuration requise
        elements.append(Paragraph("1.2 Configuration requise", self.styles['SectionTitle']))
        
        config_data = [
            ['Composant', 'Minimum', 'Recommandé'],
            ['Système d\'exploitation', 'Windows 10', 'Windows 11'],
            ['Processeur', 'Intel Core i3', 'Intel Core i5'],
            ['Mémoire RAM', '4 Go', '8 Go'],
            ['Espace disque', '500 Mo', '1 Go'],
            ['Écran', '1366x768', '1920x1080']
        ]
        
        config_table = Table(config_data, colWidths=[5*cm, 4*cm, 4*cm])
        config_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
        ]))
        elements.append(config_table)
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 1.3 Rôles utilisateurs
        elements.append(Paragraph("1.3 Rôles utilisateurs", self.styles['SectionTitle']))
        
        roles_data = [
            ['Rôle', 'Description', 'Permissions'],
            ['Administrateur', 'Gestionnaire principal', 'Accès complet à tous les modules'],
            ['Pharmacien', 'Professionnel de santé', 'Médicaments, ventes, clients, rapports'],
            ['Vendeur', 'Personnel de comptoir', 'Ventes uniquement']
        ]
        
        roles_table = Table(roles_data, colWidths=[3*cm, 4*cm, 6*cm])
        roles_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(roles_table)
        
        return elements
    
    def _create_chapter_connexion(self):
        """Chapitre 2: Connexion."""
        elements = []
        
        elements.append(Paragraph("2. CONNEXION ET AUTHENTIFICATION", self.styles['ChapterTitle']))
        
        # 2.1 Écran de connexion
        elements.append(Paragraph("2.1 Écran de connexion", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """Au lancement de l'application, l'écran de connexion s'affiche. 
            Vous devez saisir votre identifiant et votre mot de passe pour accéder au système.""",
            self.styles['NormalText']
        ))
        
        elements.append(Paragraph(
            "⚠️ IMPORTANT : Lors de la première connexion, utilisez les identifiants par défaut :\n"
            "• Identifiant : admin\n"
            "• Mot de passe : admin123\n\n"
            "Changez immédiatement ce mot de passe après la première connexion !",
            self.styles['ImportantNote']
        ))
        
        elements.append(Paragraph("Étapes de connexion :", self.styles['SubTitle']))
        steps = [
            "1. Lancez l'application PharmacieManager",
            "2. Saisissez votre identifiant dans le champ 'Nom d'utilisateur'",
            "3. Saisissez votre mot de passe dans le champ 'Mot de passe'",
            "4. Cliquez sur le bouton 'Se connecter' ou appuyez sur Entrée",
            "5. En cas d'erreur, vérifiez vos identifiants et réessayez"
        ]
        for step in steps:
            elements.append(Paragraph(step, self.styles['NormalText']))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 2.2 Gestion du mot de passe
        elements.append(Paragraph("2.2 Sécurité du mot de passe", self.styles['SectionTitle']))
        elements.append(Paragraph(
            "💡 ASTUCE : Choisissez un mot de passe sécurisé :\n"
            "• Au moins 8 caractères\n"
            "• Mélange de lettres majuscules et minuscules\n"
            "• Au moins un chiffre\n"
            "• Évitez les mots du dictionnaire",
            self.styles['Tip']
        ))
        
        return elements
    
    def _create_chapter_dashboard(self):
        """Chapitre 3: Tableau de bord."""
        elements = []
        
        elements.append(Paragraph("3. TABLEAU DE BORD", self.styles['ChapterTitle']))
        
        elements.append(Paragraph("3.1 Vue d'ensemble", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """Le tableau de bord est la page d'accueil après connexion. Il offre une vue 
            synthétique de l'activité de la pharmacie et des alertes importantes.""",
            self.styles['NormalText']
        ))
        
        elements.append(Paragraph("3.2 Indicateurs clés (KPI)", self.styles['SectionTitle']))
        
        kpi_data = [
            ['Indicateur', 'Description'],
            ['Chiffre d\'affaires du jour', 'Total des ventes validées aujourd\'hui'],
            ['Nombre de ventes', 'Nombre de transactions du jour'],
            ['Produits en stock', 'Nombre total de références en stock'],
            ['Alertes stock faible', 'Produits sous le seuil d\'alerte'],
            ['Alertes péremption', 'Produits expirant dans les 30 jours']
        ]
        
        kpi_table = Table(kpi_data, colWidths=[5*cm, 8*cm])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(kpi_table)
        
        elements.append(Spacer(1, 0.5*cm))
        
        elements.append(Paragraph("3.3 Alertes", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """Les alertes vous informent des situations nécessitant votre attention :""",
            self.styles['NormalText']
        ))
        
        alerts = [
            "🔴 Stock faible : Produits dont la quantité est inférieure au seuil défini",
            "🟠 Péremption proche : Produits expirant dans les 30 prochains jours",
            "⚫ Rupture de stock : Produits avec une quantité de 0"
        ]
        for alert in alerts:
            elements.append(Paragraph(alert, self.styles['NormalText']))
        
        return elements
    
    def _create_chapter_medicaments(self):
        """Chapitre 4: Gestion des médicaments."""
        elements = []
        
        elements.append(Paragraph("4. GESTION DES MÉDICAMENTS", self.styles['ChapterTitle']))
        
        # 4.1 Liste des médicaments
        elements.append(Paragraph("4.1 Liste des médicaments", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """La liste affiche tous les médicaments enregistrés dans le système. 
            Vous pouvez rechercher, filtrer et sélectionner un médicament pour voir ses détails.""",
            self.styles['NormalText']
        ))
        
        elements.append(Paragraph("Fonctionnalités de la liste :", self.styles['SubTitle']))
        list_features = [
            "• Barre de recherche : Recherchez par code, nom ou catégorie",
            "• Filtre par catégorie : Affichez uniquement une catégorie",
            "• Filtre 'En stock' : Masquez les produits en rupture",
            "• Tri : Cliquez sur un en-tête de colonne pour trier"
        ]
        for feature in list_features:
            elements.append(Paragraph(feature, self.styles['NormalText']))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 4.2 Ajouter un médicament
        elements.append(Paragraph("4.2 Ajouter un médicament", self.styles['SectionTitle']))
        elements.append(Paragraph("Pour ajouter un nouveau médicament :", self.styles['SubTitle']))
        
        add_steps = [
            "1. Cliquez sur le bouton '➕ Nouveau'",
            "2. Remplissez les champs obligatoires (*) :",
            "   • Code : Code barre ou référence unique",
            "   • Nom : Nom complet du médicament",
            "   • Prix d'achat : Prix d'achat HT",
            "   • Prix de vente : Prix de vente TTC",
            "3. Complétez les champs optionnels :",
            "   • Catégorie : Type de médicament",
            "   • Quantité initiale : Stock de départ",
            "   • Seuil d'alerte : Quantité minimale avant alerte",
            "   • Date de péremption : Date d'expiration",
            "   • Fabricant : Laboratoire pharmaceutique",
            "   • Description : Informations complémentaires",
            "4. Cliquez sur '💾 Enregistrer'"
        ]
        for step in add_steps:
            elements.append(Paragraph(step, self.styles['NormalText']))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 4.3 Modifier un médicament
        elements.append(Paragraph("4.3 Modifier un médicament", self.styles['SectionTitle']))
        mod_steps = [
            "1. Sélectionnez le médicament dans la liste (simple clic)",
            "2. Double-cliquez pour passer en mode édition",
            "3. Modifiez les champs souhaités",
            "4. Cliquez sur '💾 Enregistrer' pour valider",
            "5. Ou cliquez sur '❌ Annuler' pour annuler les modifications"
        ]
        for step in mod_steps:
            elements.append(Paragraph(step, self.styles['NormalText']))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 4.4 Gestion du stock
        elements.append(Paragraph("4.4 Gestion du stock", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """Après avoir sélectionné un médicament, vous pouvez gérer son stock :""",
            self.styles['NormalText']
        ))
        
        stock_actions = [
            "• '➕ Ajouter stock' : Pour un réapprovisionnement (entrée de stock)",
            "• '🔧 Ajuster stock' : Pour corriger la quantité (inventaire)"
        ]
        for action in stock_actions:
            elements.append(Paragraph(action, self.styles['NormalText']))
        
        elements.append(Paragraph(
            "💡 ASTUCE : Chaque mouvement de stock est enregistré dans l'historique "
            "pour assurer la traçabilité complète.",
            self.styles['Tip']
        ))
        
        return elements
    
    def _create_chapter_pos(self):
        """Chapitre 5: Point de vente."""
        elements = []
        
        elements.append(Paragraph("5. POINT DE VENTE (POS)", self.styles['ChapterTitle']))
        
        # 5.1 Interface de vente
        elements.append(Paragraph("5.1 Interface de vente", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """L'interface de vente est divisée en deux parties :
            
            • Partie gauche : Panier avec les produits ajoutés
            • Partie droite : Informations client et totaux""",
            self.styles['NormalText']
        ))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 5.2 Processus de vente
        elements.append(Paragraph("5.2 Processus de vente complet", self.styles['SectionTitle']))
        
        sale_steps = [
            "1. AJOUTER DES PRODUITS AU PANIER",
            "   • Saisissez le code ou le nom du produit",
            "   • Indiquez la quantité souhaitée",
            "   • Cliquez sur '➕ Ajouter' ou appuyez sur Entrée",
            "   • Utilisez '🔍 Rechercher' pour trouver un produit",
            "",
            "2. ASSOCIER UN CLIENT (optionnel)",
            "   • Cliquez sur '🔍 Sélectionner' pour choisir un client existant",
            "   • Ou cliquez sur '➕ Nouveau' pour créer un client rapidement",
            "   • Le client bénéficiera de sa remise fidélité automatiquement",
            "",
            "3. VÉRIFIER LE PANIER",
            "   • Vérifiez les quantités et les prix",
            "   • Modifiez si nécessaire avec '🔄 Modifier qté'",
            "   • Supprimez un produit avec '🗑️ Retirer'",
            "",
            "4. VALIDER LA VENTE",
            "   • Vérifiez le total affiché",
            "   • Cliquez sur '✅ VALIDER LA VENTE'",
            "   • Confirmez la validation",
            "",
            "5. IMPRIMER LE TICKET",
            "   • Après validation, choisissez d'imprimer le ticket",
            "   • Le ticket PDF est généré et peut être imprimé"
        ]
        for step in sale_steps:
            elements.append(Paragraph(step, self.styles['NormalText']))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 5.3 Gestion du panier
        elements.append(Paragraph("5.3 Gestion du panier", self.styles['SectionTitle']))
        
        panier_data = [
            ['Action', 'Description'],
            ['➕ Ajouter', 'Ajoute un produit au panier'],
            ['🔄 Modifier qté', 'Change la quantité d\'un produit'],
            ['🗑️ Retirer', 'Supprime un produit du panier'],
            ['🗑️ Vider panier', 'Supprime tous les produits'],
            ['🆕 Nouvelle vente', 'Annule et recommence une nouvelle vente']
        ]
        
        panier_table = Table(panier_data, colWidths=[4*cm, 9*cm])
        panier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(panier_table)
        
        elements.append(Paragraph(
            "⚠️ IMPORTANT : Vérifiez toujours le stock disponible avant de valider. "
            "Le système vous alertera si la quantité demandée dépasse le stock.",
            self.styles['ImportantNote']
        ))
        
        return elements
    
    def _create_chapter_clients(self):
        """Chapitre 6: Gestion des clients."""
        elements = []
        
        elements.append(Paragraph("6. GESTION DES CLIENTS", self.styles['ChapterTitle']))
        
        # 6.1 Fichier clients
        elements.append(Paragraph("6.1 Fichier clients", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """Le module de gestion des clients permet de maintenir un fichier client 
            complet avec historique des achats et gestion de la fidélité.""",
            self.styles['NormalText']
        ))
        
        elements.append(Paragraph("Informations client :", self.styles['SubTitle']))
        client_fields = [
            "• Code client : Généré automatiquement (CLI-XXXXX)",
            "• Prénom et Nom : Identité du client",
            "• Téléphone : Pour contact et recherche rapide",
            "• Email : Communication électronique",
            "• Adresse : Adresse postale"
        ]
        for field in client_fields:
            elements.append(Paragraph(field, self.styles['NormalText']))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 6.2 Programme de fidélité
        elements.append(Paragraph("6.2 Programme de fidélité", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """Le programme de fidélité récompense automatiquement les clients réguliers :""",
            self.styles['NormalText']
        ))
        
        fidelity_data = [
            ['Palier', 'Points requis', 'Remise'],
            ['Standard', '0', '0%'],
            ['Bronze', '100', '2%'],
            ['Argent', '250', '5%'],
            ['Or', '500', '8%'],
            ['Platine', '1000', '10%']
        ]
        
        fidelity_table = Table(fidelity_data, colWidths=[4*cm, 4*cm, 4*cm])
        fidelity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFC107')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(fidelity_table)
        
        elements.append(Spacer(1, 0.3*cm))
        
        elements.append(Paragraph(
            "💡 Les points sont calculés automatiquement : 1 point pour chaque 10 GNF dépensés. "
            "La remise est appliquée automatiquement lors des ventes.",
            self.styles['Tip']
        ))
        
        return elements
    
    def _create_chapter_reports(self):
        """Chapitre 7: Rapports."""
        elements = []
        
        elements.append(Paragraph("7. RAPPORTS ET STATISTIQUES", self.styles['ChapterTitle']))
        
        # 7.1 Ventes par vendeur
        elements.append(Paragraph("7.1 Ventes par vendeur", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """Ce rapport affiche la performance de chaque vendeur sur une période donnée.""",
            self.styles['NormalText']
        ))
        
        elements.append(Paragraph("Utilisation :", self.styles['SubTitle']))
        report_steps = [
            "1. Sélectionnez la période (dates de début et fin)",
            "2. Cliquez sur '🔍 Générer le rapport'",
            "3. La liste des vendeurs s'affiche à gauche",
            "4. Cliquez sur un vendeur pour voir le détail de ses ventes",
            "5. Exportez le rapport complet en CSV si nécessaire"
        ]
        for step in report_steps:
            elements.append(Paragraph(step, self.styles['NormalText']))
        
        elements.append(Paragraph("Informations affichées :", self.styles['SubTitle']))
        info_displayed = [
            "• Nom du vendeur",
            "• Nombre total de ventes",
            "• Chiffre d'affaires généré",
            "• Panier moyen",
            "• Détail de chaque vente (produit, client, montant)"
        ]
        for info in info_displayed:
            elements.append(Paragraph(info, self.styles['NormalText']))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 7.2 État du stock
        elements.append(Paragraph("7.2 État du stock", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """Ce rapport donne une vue complète de l'état actuel du stock.""",
            self.styles['NormalText']
        ))
        
        stock_info = [
            "• Nombre total de produits",
            "• Nombre de produits en stock faible",
            "• Nombre de produits proches de la péremption",
            "• Valeur totale du stock",
            "• Liste détaillée de tous les produits"
        ]
        for info in stock_info:
            elements.append(Paragraph(info, self.styles['NormalText']))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 7.3 Top produits
        elements.append(Paragraph("7.3 Top produits", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """Ce rapport identifie les produits les plus vendus sur une période.""",
            self.styles['NormalText']
        ))
        
        # 7.4 Export
        elements.append(Paragraph("7.4 Export des données", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """Tous les rapports peuvent être exportés en format CSV pour analyse 
            dans Excel ou autre tableur.""",
            self.styles['NormalText']
        ))
        
        elements.append(Paragraph(
            "💡 ASTUCE : Les fichiers CSV exportés utilisent le point-virgule (;) comme "
            "séparateur pour une meilleure compatibilité avec Excel en français.",
            self.styles['Tip']
        ))
        
        return elements
    
    def _create_chapter_admin(self):
        """Chapitre 8: Administration."""
        elements = []
        
        elements.append(Paragraph("8. ADMINISTRATION", self.styles['ChapterTitle']))
        
        # 8.1 Gestion des utilisateurs
        elements.append(Paragraph("8.1 Gestion des utilisateurs", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """Seul l'administrateur peut gérer les comptes utilisateurs.""",
            self.styles['NormalText']
        ))
        
        elements.append(Paragraph("Créer un utilisateur :", self.styles['SubTitle']))
        create_user_steps = [
            "1. Accédez au module 'Utilisateurs'",
            "2. Cliquez sur '➕ Nouveau'",
            "3. Remplissez les informations :",
            "   • Nom d'utilisateur (identifiant de connexion)",
            "   • Mot de passe",
            "   • Nom complet",
            "   • Rôle (Admin, Pharmacien, Vendeur)",
            "4. Cliquez sur '💾 Enregistrer'"
        ]
        for step in create_user_steps:
            elements.append(Paragraph(step, self.styles['NormalText']))
        
        elements.append(Paragraph(
            "⚠️ IMPORTANT : Chaque utilisateur doit avoir son propre compte. "
            "Ne partagez jamais les identifiants de connexion.",
            self.styles['ImportantNote']
        ))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # 8.2 Sauvegarde
        elements.append(Paragraph("8.2 Sauvegarde des données", self.styles['SectionTitle']))
        elements.append(Paragraph(
            """La sauvegarde régulière de vos données est essentielle.""",
            self.styles['NormalText']
        ))
        
        backup_steps = [
            "• Sauvegarde manuelle : Exécutez le script 'backup.bat'",
            "• Sauvegarde automatique : Configurée dans le planificateur Windows",
            "• Emplacement : Dossier 'backups' dans l'application",
            "• Fréquence recommandée : Quotidienne"
        ]
        for step in backup_steps:
            elements.append(Paragraph(step, self.styles['NormalText']))
        
        return elements
    
    def _create_chapter_faq(self):
        """Chapitre 9: FAQ."""
        elements = []
        
        elements.append(Paragraph("9. FAQ ET DÉPANNAGE", self.styles['ChapterTitle']))
        
        faqs = [
            {
                'q': "L'application ne démarre pas",
                'a': "Vérifiez que vous avez les droits d'exécution. "
                     "Essayez de lancer en tant qu'administrateur. "
                     "Vérifiez que l'antivirus ne bloque pas l'application."
            },
            {
                'q': "J'ai oublié mon mot de passe",
                'a': "Contactez l'administrateur qui peut réinitialiser votre mot de passe "
                     "depuis le module de gestion des utilisateurs."
            },
            {
                'q': "Le ticket ne s'imprime pas",
                'a': "Vérifiez que votre imprimante est bien configurée comme imprimante par défaut. "
                     "Le ticket est généré en PDF dans le dossier 'receipts'."
            },
            {
                'q': "Comment annuler une vente ?",
                'a': "Seuls l'administrateur et le pharmacien peuvent annuler une vente. "
                     "Accédez à l'historique des ventes et utilisez la fonction d'annulation."
            },
            {
                'q': "Les données sont-elles sécurisées ?",
                'a': "Oui, les mots de passe sont cryptés et la base de données est locale. "
                     "Effectuez des sauvegardes régulières pour éviter toute perte."
            },
            {
                'q': "Comment mettre à jour l'application ?",
                'a': "Faites une sauvegarde, fermez l'application, remplacez l'exécutable "
                     "par la nouvelle version, puis relancez."
            }
        ]
        
        for faq in faqs:
            elements.append(Paragraph(f"❓ {faq['q']}", self.styles['SectionTitle']))
            elements.append(Paragraph(faq['a'], self.styles['NormalText']))
            elements.append(Spacer(1, 0.3*cm))
        
        elements.append(Spacer(1, 1*cm))
        
        # Contact support
        elements.append(Paragraph("SUPPORT TECHNIQUE", self.styles['SectionTitle']))
        
        support_info = [
            "📞 Téléphone : +224 627 171 397",
            "📧 Email : support@votre-entreprise.com",
            "💬 WhatsApp : +224 627 171 397",
            "🕐 Horaires : Lundi - Vendredi, 8h00 - 18h00"
        ]
        for info in support_info:
            elements.append(Paragraph(info, self.styles['NormalText']))
        
        return elements


# Exécution
if __name__ == "__main__":
    generator = GuideUtilisateurGenerator()
    generator.generate()