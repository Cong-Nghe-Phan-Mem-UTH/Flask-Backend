# Domain constants

class Role:
    Owner = "Owner"
    Employee = "Employee"
    Guest = "Guest"

class TokenType:
    ForgotPasswordToken = "ForgotPasswordToken"
    AccessToken = "AccessToken"
    RefreshToken = "RefreshToken"
    TableToken = "TableToken"

class DishStatus:
    Available = "Available"
    Unavailable = "Unavailable"
    Hidden = "Hidden"

class TableStatus:
    Available = "Available"
    Hidden = "Hidden"
    Reserved = "Reserved"

class OrderStatus:
    Pending = "Pending"
    Processing = "Processing"
    Rejected = "Rejected"
    Delivered = "Delivered"
    Paid = "Paid"

# Manager room for Socket.IO
ManagerRoom = "manager"

