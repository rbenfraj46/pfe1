@startuml
title Processus d'Ajout d'une Voiture par une Agence

actor "Agent d'Agence" as agent
participant "Interface Web" as ui
participant "Système" as system
participant "Base de données" as db
participant "Service Upload" as upload
actor "Admin" as admin

autonumber

' Authentification
agent -> ui : Se connecter à l'interface 
activate ui
ui -> system : Vérifier permissions
activate system
system -> db : Vérifier droits d'accès
activate db
db --> system : Confirmation permissions
deactivate db
system --> ui : Accès autorisé
deactivate system
ui --> agent : Afficher dashboard agence
deactivate ui

' Accès au formulaire
agent -> ui : Cliquer "Ajouter voiture"
activate ui
ui -> system : Charger données initiales
activate system
system -> db : Requête marques/modèles
activate db
db --> system : Liste marques/modèles
deactivate db
system --> ui : Données formulaire
deactivate system
ui --> agent : Afficher formulaire
deactivate ui

' Remplissage formulaire
agent -> ui : Saisir détails voiture
activate ui
agent -> ui : Télécharger images
ui -> upload : Traiter images
activate upload
upload -> system : Stocker images
activate system
system --> ui : Confirmation upload
deactivate system
deactivate upload
ui --> agent : Aperçu images
deactivate ui

' Soumission formulaire
agent -> ui : Soumettre formulaire
activate ui
ui -> system : Valider données
activate system
system -> system : Vérifier format données
system -> db : Vérifier doublons
activate db
db --> system : Résultat vérification
deactivate db

alt données valides
    system -> db : Vérifier statut agence (is_auto)
    activate db
    db --> system : Statut agence
    deactivate db

    alt agence.is_auto == true
        system -> db : Enregistrer voiture (is_active=true)
        activate db
        db --> system : Voiture activée et enregistrée
        deactivate db
        system --> ui : Succès enregistrement\n(Voiture disponible immédiatement)
        ui --> agent : Afficher confirmation\n(Voiture active)
    else agence.is_auto == false
        system -> db : Enregistrer voiture (is_active=false)
        activate db
        db --> system : Voiture en attente
        deactivate db
        system --> ui : Succès enregistrement\n(En attente d'activation)
        ui --> agent : Afficher confirmation\n(En attente d'approbation)
        
        ' Processus d'activation manuel par l'admin
        admin -> ui : Accéder interface admin
        activate ui
        ui -> system : Liste des voitures en attente
        activate system
        system -> db : Récupérer voitures (is_active=false)
        activate db
        db --> system : Liste voitures inactives
        deactivate db
        system --> ui : Afficher liste
        admin -> ui : Activer voiture
        ui -> system : Demande activation
        system -> db : Mettre à jour (is_active=true)
        activate db
        db --> system : Confirmation activation
        deactivate db
        system --> ui : Confirmation
        ui --> admin : Notification succès
        deactivate system
        deactivate ui
    end

else données invalides
    system --> ui : Erreurs validation
    ui --> agent : Afficher erreurs
end
deactivate system
deactivate ui

@enduml
