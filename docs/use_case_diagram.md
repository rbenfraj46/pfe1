@startuml Use Case Diagram - Car Rental System

left to right direction
skinparam packageStyle rectangle

actor "Client" as client
actor "Agency Owner" as owner
actor "Agency Staff" as staff
actor "Admin" as admin

rectangle "Car Rental System" {
    ' Client Use Cases
    usecase "Register Account" as UC1
    usecase "Search Cars" as UC2
    usecase "Book Car" as UC3
    usecase "Manage Reservations" as UC4
    usecase "View Car Details" as UC5
    usecase "Submit Car Model Request" as UC6
    usecase "Subscribe to Newsletter" as UC7

    ' Agency Owner Use Cases
    usecase "Register Agency" as UC8
    usecase "Manage Agency Profile" as UC9
    usecase "Manage Cars" as UC10
    usecase "Handle Reservations" as UC11
    usecase "Manage Staff" as UC12
    usecase "View Analytics" as UC13
    usecase "Set Car Availability" as UC14

    ' Agency Staff Use Cases
    usecase "Handle Customer Requests" as UC15
    usecase "Manage Car Status" as UC16
    usecase "Process Reservations" as UC17

    ' Admin Use Cases
    usecase "Manage Brands" as UC18
    usecase "Approve Agencies" as UC19
    usecase "Manage Car Models" as UC20
    usecase "System Configuration" as UC21
    usecase "Monitor Activities" as UC22
}

' Client Relationships
client --> UC1
client --> UC2
client --> UC3
client --> UC4
client --> UC5
client --> UC6
client --> UC7

' Agency Owner Relationships
owner --> UC8
owner --> UC9
owner --> UC10
owner --> UC11
owner --> UC12
owner --> UC13
owner --> UC14

' Agency Staff Relationships
staff --> UC15
staff --> UC16
staff --> UC17

' Admin Relationships
admin --> UC18
admin --> UC19
admin --> UC20
admin --> UC21
admin --> UC22

' Include/Extend Relationships
UC3 .> UC2 : <<include>>
UC3 .> UC5 : <<include>>
UC10 .> UC14 : <<include>>
UC11 .> UC17 : <<include>>
UC19 .> UC22 : <<include>>

' Inheritance
owner --|> staff

note "All users must be authenticated\nexcept for Search Cars and View Car Details" as N1

@enduml
