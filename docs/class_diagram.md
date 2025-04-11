@startuml

' Style and Theme Configuration
skinparam packageStyle rectangle
skinparam class {
    BackgroundColor White
    ArrowColor #2688d4
    BorderColor #2688d4
}
skinparam stereotypeCBackgroundColor #95DEF0

' Package Definition
package "Authentication" {
    class User {
        +is_mail_verified: BooleanField
        +email: EmailField
        +has_newsletter_subscription(): Boolean
        +get_full_name(): String
        +get_agency_permissions(): List
        +email_verification_token: String
        +reset_password_token: String
        +last_login: DateTime
        +register(): void
        +verify_email(): void
        +reset_password(): void
    }
}

package "Agency Management" {
    class Agences {
        +agency_name: CharField
        +commercial_name: CharField
        +ceo_name: CharField
        +ceo_phone_number: CharField
        +tax_number: CharField
        +adress_agency: CharField
        +governorate: CharField
        +city: CharField
        +delegation: CharField
        +email: EmailField
        +phone_number: CharField
        +creation_date: DateField
        +update_date: DateField
        +is_mail_verified: BooleanField
        +is_active: BooleanField
        +is_auto: BooleanField
        +zipcode: CharField
        +logo: ImageField
        +location: PointField
        +__str__(): String
        +get_active_cars(): QuerySet
        +verify_email(): void
        +get_location_data(): Dict
        +has_user_permission(user: User, permission: String): Boolean
    }
    class AgencyPermission {
        +permission: CharField
        +granted_at: DateTimeField
        +__str__(): String
        +is_valid(): Boolean
    }
    class RightsAccess
}

package "Car Management" {
    class Brand {
        +name: CharField
        +description: CharField
        +img_hash: CharField
        +img_extension: CharField
        +is_active: BooleanField
        +order_key: IntegerField
        +__str__(): String
    }
    class CarModel {
        +name: CharField
        +description: CharField
        +img_hash: CharField
        +img_extension: CharField
        +is_active: BooleanField
        +air_conditioner: CharField
        +category: CharField
        +cylinder: FloatField
        +horse_power: FloatField
        +doors_nbr: IntegerField
        +place_nbr: IntegerField
        +energy: CharField
        +extra_urban_consumption: FloatField
        +urban_consumption: FloatField
        +mixte_consumption: FloatField
        +gear_type: CharField
        +gear_nbr: IntegerField
        +transmission: CharField
        +max_speed: IntegerField
        +length: FloatField
        +width: FloatField
        +height: FloatField
        +trunk_volume: IntegerField
        +created: DateTimeField
        +updated: DateTimeField
        +order_key: IntegerField
        +__str__(): String
        +get_full_specs(): Dict
        +get_consumption_data(): Dict
        +get_dimensions(): Dict
    }
    class GearType {
        +name: CharField
        +is_active: BooleanField
        +order_key: IntegerField
        +__str__(): String
    }
    class Transmission {
        +name: CharField
        +is_active: BooleanField
        +order_key: IntegerField
        +__str__(): String
    }
    class AgencyCar {
        +image: ImageField
        +fuel_policy: CharField
        +security_deposit: DecimalField
        +minimum_license_age: IntegerField
        +price_per_day: DecimalField
        +is_active: BooleanField
        +available: BooleanField
        +created: DateTimeField
        +is_available(start_date: Date, end_date: Date): Boolean
        +calculate_total_price(start_date: Date, end_date: Date): Decimal
        +get_current_availability(): Boolean
        +__str__(): String
        +save(): void
    }
    class CarUnavailability {
        +start_date: DateField
        +end_date: DateField
        +clean(): void
        +save(): void
        +__str__(): String
        +is_period_valid(): Boolean
    }
}

package "Booking System" {
    class CarReservation {
        +start_date: DateField
        +end_date: DateField
        +notes: TextField
        +total_price: DecimalField
        +status: CharField
        +rejection_reason: TextField
        +deposit_paid: BooleanField
        +created_at: DateTimeField
        +updated_at: DateTimeField
        +clean(): void
        +save(): void
        +__str__(): String
        +calculate_total_price(): void
        +approve(): void
        +reject(reason: String): void
        +cancel(): void
        +payment_status: String
        +payment_method: String
        +invoice_number: String
        +generate_invoice(): void
        +process_payment(): void
        +send_confirmation_email(): void
    }
    class CarModelRequest {
        +brand_name: CharField
        +model_name: CharField
        +description: TextField
        +status: CharField
        +created_at: DateTimeField
        +updated_at: DateTimeField
    }
}

package "Location Services" {
    class State {
        +name: String
        +code: String
        +position: PointField
        +get_delegations(): List
    }
    class Delegation {
        +name: String
        +state: ForeignKey
        +position: PointField
        +get_cities(): List
    }
    class City {
        +name: String
        +zipcode: String
        +delegation: ForeignKey
        +position: PointField
    }
}

' Additional Classes
class PaymentTransaction {
    +reservation: ForeignKey
    +amount: DecimalField
    +status: String
    +payment_method: String
    +transaction_id: String
    +created_at: DateTime
    +process(): void
    +verify(): void
    +refund(): void
}

class Review {
    +user: ForeignKey
    +car: ForeignKey
    +rating: IntegerField
    +comment: TextField
    +created_at: DateTime
    +validate(): void
}

class Notification {
    +user: ForeignKey
    +title: String
    +message: Text
    +type: String
    +read: Boolean
    +created_at: DateTime
    +mark_as_read(): void
}

' Relationships
User "1" -- "*" Review : writes >
AgencyCar "1" -- "*" Review : receives >
CarReservation "1" -- "1" PaymentTransaction : has >
User "1" -- "*" Notification : receives >
State "1" -- "*" Delegation : contains >
Delegation "1" -- "*" City : contains >
Agences "1" -- "1" City : located in >

' Existing relationships with improved notation
Brand "1" --o "*" CarModel : has >
CarModel "1" --o "*" AgencyCar : based on >
Agences "1" --o "*" AgencyCar : owns >
GearType "1" --o "*" AgencyCar : has >
Transmission "1" --o "*" CarModel : has >
AgencyCar "1" --* "*" CarUnavailability : contains >
AgencyCar "1" --* "*" CarReservation : has >
User "1" --o "*" CarReservation : makes >
User "1" --o "*" CarModelRequest : submits >
User "1" --o "*" AgencyPermission : has >
Agences "1" --* "*" AgencyPermission : grants >
User "1" --o "*" Agences : manages >

' Notes
note right of PaymentTransaction
  Handles all payment processing
  and transaction management
end note

note right of Review
  Allows users to rate and
  comment on their car rentals
end note

note bottom of Notification
  System notifications for
  users and agencies
end note

@enduml
