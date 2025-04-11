@startuml

' Styling and Theme
skinparam class {
    BackgroundColor LightSkyBlue/White
    BorderColor DarkBlue
    ArrowColor Navy
    FontName Arial
    FontSize 12
    AttributeFontColor Black
    AttributeFontSize 11
    BackgroundColor<<Main>> LightGreen/White
    BorderColor<<Main>> DarkGreen
}

skinparam stereotypeCBackgroundColor YellowGreen
skinparam stereotypeCBorderColor SpringGreen

skinparam title {
    FontColor DarkBlue
    FontSize 20
    FontStyle bold
}

skinparam note {
    BackgroundColor LightYellow
    BorderColor Gold
    FontStyle italic
}

' Title
title Location de Voitures - Diagramme de Classes

' Packages styling
package "Gestion Utilisateurs" #LightBlue {
    class User {
        +username: String
        +email: EmailField
        +password: String
        +first_name: String
        +last_name: String
        +is_mail_verified: Boolean
        +is_active: Boolean
        +is_staff: Boolean
        +last_login: DateTime
        +date_joined: DateTime
        +get_full_name(): String
        +has_newsletter_subscription(): Boolean
        +verify_email(): void
    }


    class MailSubscription {
        +user: User
        +subscription_date: DateTime
        +is_active: Boolean
        +unsubscription_date: DateTime
        +promo_value: Float
        +is_promo_used: Boolean
    }
}

package "Gestion Localisation" #LightPink {
    class State {
        +name: String
        +order_key: Integer
        +position: PointField
        +get_delegations(): List
    }

    class Delegation {
        +name: String
        +order_key: Integer
        +position: PointField
        +state: State
        +get_cities(): List
    }

    class City {
        +name: String
        +zipcode: String
        +order_key: Integer
        +position: PointField
        +delegation: Delegation
    }
}

package "Gestion Voitures" #LightGreen {
    class Brand {
        +name: String
        +description: String
        +img_hash: String
        +img_extension: String
        +is_active: Boolean
        +order_key: Integer
    }

    class CarModel {
        +name: String
        +description: String
        +brand: Brand
        +img_hash: String
        +img_extension: String
        +is_active: Boolean
        +air_conditioner: String
        +category: String
        +cylinder: Float
        +horse_power: Float
        +doors_nbr: Integer
        +place_nbr: Integer
        +energy: String
        +consumption_data: JSON
        +gear_type: String
        +gear_nbr: Integer
        +transmission: String
        +dimensions: JSON
        +created: DateTime
        +updated: DateTime
        +order_key: Integer
        +get_full_specs(): Dict
    }

    class GearType {
        +name: String
        +is_active: Boolean
        +order_key: Integer
    }

    class AgencyCar {
        +agence: Agence
        +brand: Brand
        +car_model: CarModel
        +gear_type: GearType
        +image: ImageField
        +fuel_policy: String
        +security_deposit: Decimal
        +minimum_license_age: Integer
        +price_per_day: Decimal
        +is_active: Boolean
        +available: Boolean
        +created: DateTime
        +is_available(start_date: Date, end_date: Date): Boolean
        +calculate_price(days: Integer): Decimal
    }
}

package "Gestion Agences" #LightYellow {
    class Agence {
        +agency_name: String
        +commercial_name: String
        +ceo_name: String
        +ceo_phone_number: String
        +tax_number: String
        +address_agency: String
        +governorate: String
        +city: String
        +delegation: String
        +email: String
        +phone_number: String
        +creation_date: Date
        +update_date: Date
        +is_mail_verified: Boolean
        +is_active: Boolean
        +is_auto: Boolean
        +zipcode: String
        +logo: ImageField
        +location: PointField
        +creator: User
        +verify_email(): void
        +get_active_cars(): List
    }

    class AgencyPermission {
        +agency: Agence
        +user: User
        +permission: String
        +granted_by: User
        +granted_at: DateTime
        +is_valid(): Boolean
    }
}

package "Gestion Réservations" #LightGray {
    class CarReservation {
        +car: AgencyCar
        +user: User
        +start_date: Date
        +end_date: Date
        +notes: Text
        +total_price: Decimal
        +status: String
        +rejection_reason: Text
        +deposit_paid: Boolean
        +created_at: DateTime
        +updated_at: DateTime
        +calculate_total(): void
        +clean(): void
    }

    class CarUnavailability {
        +car: AgencyCar
        +start_date: Date
        +end_date: Date
        +clean(): void
        +is_period_valid(): Boolean
    }
}



' Relationships
State "1" --* "*" Delegation
Delegation "1" --* "*" City
Agence "1" -- "1" City : located in

User "1" --o "*" MailSubscription : has
User "1" --o "*" CarReservation : makes
User "1" --o "*" AgencyPermission : has
User "1" --o "*" Agence : manages

Brand "1" --* "*" CarModel
CarModel "1" --o "*" AgencyCar : based on
GearType "1" --o "*" AgencyCar : has

AgencyCar "1" --* "*" CarUnavailability
AgencyCar "1" --* "*" CarReservation
Agence "1" --o "*" AgencyCar : owns
Agence "1" --* "*" AgencyPermission : grants

@enduml
