@startuml
title Processus d'Ajout d'une Voiture par une Agence

actor "Agent d'Agence" as agent
participant "Interface Web" as ui
participant "Système" as system
participant "Base de données" as db
participant "Service Upload" as upload
participant "Service Email" as email

autonumber

' Authentification
agent -> ui : Se connecter à l'interface agence
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
    system -> db : Enregistrer voiture
    activate db
    db --> system : Confirmation enregistrement
    deactivate db
    
    ' Notification succès
    system -> email : Envoyer confirmation
    activate email
    email -> agent : Email confirmation
    deactivate email
    
    system --> ui : Succès enregistrement
    ui --> agent : Afficher confirmation
else données invalides
    system --> ui : Erreurs validation
    ui --> agent : Afficher erreurs
end
deactivate system
deactivate ui

' Activation automatique
alt activation auto activée
    system -> db : Activer voiture
    activate system
    activate db
    db --> system : Confirmation activation
    deactivate db
    system -> email : Notification disponibilité
    activate email
    email -> agent : Email activation
    deactivate email
    deactivate system
end

@enduml
