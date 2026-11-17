"""kb.py: a small help-centre knowledge base for the demo shop QuickCart.

Fictional data, made for this lesson. Each document has sections (## headings).
"""

DOCS = {
    "refunds": """# Refunds
## Refund timeline
After we receive your return, the refund starts within 24 hours.
UPI and wallet refunds arrive in 2 to 4 working days.
Card refunds take 5 to 7 working days, because the bank adds its own step.
## Refund method
Refunds go back to the original payment method.
Cash on delivery orders are refunded to your bank account by NEFT.""",
    "returns": """# Returns
## Return window
Most items can be returned within 10 days of delivery.
Phones and laptops have a 7 day replacement-only window.
## How to return
Open My Orders, pick the item and tap Return.
A courier picks it up within 2 days.""",
    "shipping": """# Shipping
## Delivery time
Metro cities get delivery in 1 to 2 days.
Other cities take 3 to 5 days.
## Warehouses
Electronics ship from the Pune warehouse.
Groceries ship from the nearest city store.
## Delivery fee
Orders above Rs 499 ship free. QuickCart Plus members always ship free.""",
    "plus": """# QuickCart Plus
## Benefits
QuickCart Plus is our membership plan.
It gives free delivery on every order and early access to sales.
## Price
Plus costs Rs 999 per year or Rs 129 per month.""",
    "payments": """# Payments
## Payment options
We accept UPI, cards, net banking, wallets and cash on delivery.
## EMI
No cost EMI is available on cards for orders above Rs 3000.
The QuickCart Plus yearly plan can also be paid by EMI in 3 parts.""",
    "warranty": """# Warranty
## Electronics warranty
All electronics come with a 1 year brand warranty.
Laptops shipped from the Pune warehouse get 1 extra year of QuickCart Care.
## Claims
Raise a claim in My Orders with the invoice and a photo.""",
    "errors": """# App error codes
## E-204
E-204 means the payment was taken but the order was not created.
The money is auto-reversed within 48 hours. Do not pay again.
## E-310
E-310 means the delivery pincode is not serviceable yet.""",
    "account": """# Account
## Login problems
If you forgot your password, tap Forgot Password on the login screen.
An OTP is sent to your registered mobile number.
## Delete account
Account deletion is final and takes 7 days.""",
}
