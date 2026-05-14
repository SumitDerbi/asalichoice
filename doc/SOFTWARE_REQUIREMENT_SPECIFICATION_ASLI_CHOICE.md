MODULE 1 — MASTER MANAGEMENT
for AsliChoice

Purpose
Master Management is the foundation module of the entire application.
It acts as the:
Single Source of Truth
for:
products, 
pricing, 
branches, 
taxes, 
customers, 
vendors, 
and all reusable business configurations. 
All other modules depend on this module.

MAIN SUBMODULES
1. Product Master
Central product database.
Features
Product Name 
SKU/Product Code 
Barcode 
HSN Code 
Brand 
Description 
Product Images 
Active/Inactive status 
Online visibility 
POS enable/disable 
Product Types
Simple Product 
Variant Product 
Combo Product 
Service Product 

2. Category Management
Features
Multi-level categories 
Parent-child hierarchy 
Example
Ghee
 ├── A2 Ghee
 └── Gir Cow Ghee

3. Product Variants
Supports:
size, 
flavor, 
weight, 
packaging variations. 
Features
Separate SKU 
Separate barcode 
Separate inventory 
Separate pricing 

4. Unit Management
Examples
Kg 
Gram 
Liter 
Piece 
Bottle 
Features
Unit conversion support 
Example:
1 Box = 12 Bottles

5. Brand Management
Features
Brand Name 
Logo 
Description 
Status 

6. Tax Management (GST)
Features
CGST 
SGST 
IGST 
Inclusive/Exclusive pricing 
Product-wise tax configuration 

7. Price Management
Price Categories
MRP
Retail
Wholesale
Partner
Internal Consumption
Features
Product-wise pricing 
Branch-wise pricing (future-ready) 
Offer pricing 

8. Internal Consumption Pricing
Purpose
For:
owner use, 
product samples, 
office usage, 
internal product consumption. 
Rules Finalized
Access only to Super Admin 
No backdated entries 
Mandatory comments 
Inventory reduces immediately 
Separate from normal sales reporting 

9. Branch & Warehouse Management
Features
Multiple branches 
Warehouse management 
Branch-wise stock 
Fields
Branch Name 
Address 
GST Number 
Contact Details 

10. Customer Master
Basic Fields
Name 
Mobile 
Email 
Address 
GST (optional) 

11. Vendor Master
Basic Fields
Vendor Name 
Contact Details 
GST 
Payment Terms 

12. Payment Mode Master
Examples
Cash 
UPI 
Card 
Wallet 
Bank Transfer 

13. Offer/Coupon Master
Features
Percentage discount 
Flat discount 
Product-based offers 
Expiry dates 

IMPORTANT BUSINESS RULES
1. Structured SKU System
Example:
GHE-GIR-500

2. Barcode Ready
Barcode support from Day 1.

3. Soft Delete Only
Never permanently delete master data.
Use:
is_active = false

4. Multi-branch Ready
Even if initially single branch.

5. Audit Logs
Track:
product changes, 
price changes, 
inventory-affecting updates. 

INTERNAL CONSUMPTION FINALIZED FLOW
Super Admin
      ↓
Creates Internal Consumption Entry
      ↓
Mandatory Comments
      ↓
Inventory Reduced
      ↓
Separate Audit Entry Created

CORE DATABASE TABLES
products
product_variants
categories
brands
units
taxes
price_lists
branches
warehouses
customers
vendors
payment_modes
offers
internal_consumptions

FINAL OBJECTIVE OF MODULE 1
To create a:
Centralized, scalable, audit-safe business master engine
that powers:
Inventory 
Purchase 
POS 
Online Store 
CRM 
Referral System 
Analytics 
Accounting 
across the entire AsliChoice ecosystem.



MODULE 2 — USER & ROLE MANAGEMENT
for AsliChoice

Purpose
This module manages:
authentication, 
authorization, 
roles, 
permissions, 
branch access, 
security, 
sessions, 
audit logs, 
and user hierarchy. 
It acts as the:
Security Backbone
of the entire application.

CORE ARCHITECTURE
Unified User System
Single user table for:
customers, 
partners, 
staff, 
admins, 
vendors. 
Structure:
User
 ├── Roles
 ├── Permissions
 ├── Branch Access
 └── Profiles
One user can have multiple roles.
Example:
Customer + Partner
Staff + Customer
Admin + Partner

AUTHENTICATION SYSTEM
Supported Login Identifiers
Mobile Number
Email Address

Supported Authentication Methods
OTP Login
Password Login

Supported OTP Channels
SMS OTP
Email OTP

FINALIZED LOGIN FLOW
User enters:
Email OR Mobile Number
System automatically:
detects input type, 
finds user, 
checks enabled authentication methods, 
selects best available verified OTP channel. 

SMART OTP FALLBACK LOGIC (FINALIZED)
If user enters mobile but:
Mobile OTP = Disabled
Email OTP = Enabled
and verified email exists:
System sends:
OTP to registered email address
Similarly:
email input can fallback to mobile OTP. 

IMPORTANT RULE
User Input ≠ OTP Destination
The system intelligently decides:
best verified authentication channel, 
based on configuration and availability. 

SUPER ADMIN AUTH CONFIGURATION
Login Identifier Controls
Enable/Disable Mobile Login 
Enable/Disable Email Login 

Authentication Method Controls
Enable/Disable OTP Login 
Enable/Disable Password Login 

OTP Channel Controls
Enable/Disable SMS OTP 
Enable/Disable Email OTP 

OTP Settings
OTP length 
Expiry duration 
Resend cooldown 
Max attempts 

CONFIGURATION VALIDATION RULES
System prevents invalid setups.
Example invalid config:
Mobile Login ENABLED
Mobile OTP DISABLED
Password Login DISABLED
System blocks save.

ROLE MANAGEMENT
Finalized Roles
SUPER_ADMIN
ADMIN
MANAGER
STAFF
CASHIER
CUSTOMER
PARTNER
VENDOR

PERMISSION MANAGEMENT
Permission-Based Access
Permissions:
VIEW
CREATE
EDIT
DELETE
APPROVE
EXPORT
Example:
PRODUCT_VIEW
PRODUCT_CREATE

BRANCH ACCESS CONTROL
Users can have:
single branch access, 
multi-branch access, 
all-branch access. 

USER PROFILES
Common Fields
Name 
Mobile 
Email 
Address 
DOB 
Profile Photo 

Specialized Profiles
Staff Profile
Employee ID 
Department 
Partner Profile
Referral Code 
Wallet Status 
Vendor Profile
GST 
Company Information 

REFERRAL → PARTNER FLOW (FINALIZED)
Customer refers another customer
        ↓
Referral completes successful purchase
        ↓
Customer automatically becomes PARTNER

REFERRAL RULES
Single-level referral only 
No MLM 
Wallet-based rewards initially 

WALLET SYSTEM
Initially:
Commission → Internal Wallet
No payouts initially.
Future payout-ready structure maintained.

INTERNAL CONSUMPTION (FINALIZED)
Access
SUPER_ADMIN only

Rules
No backdated entries 
Mandatory comments 
Inventory reduces immediately 
Separate reporting 

SESSION & SECURITY FEATURES
Active sessions 
Device tracking 
Force logout 
Session expiry 
Login attempt limits 
OTP rate limiting 

AUDIT LOGS
Track:
logins, 
failed logins, 
edits, 
approvals, 
deletions, 
user activity. 

RECOMMENDED DATABASE TABLES
users
roles
permissions
user_roles
role_permissions
user_permissions
user_branches
sessions
audit_logs
partner_profiles
staff_profiles
vendor_profiles
customer_profiles

RECOMMENDED SECURITY ARCHITECTURE
Backend
JWT Authentication 
Refresh Tokens 
Role Middleware 
Permission Middleware 

Frontend
Route Guards 
Permission-based Menus 
Dynamic UI Visibility 

FINAL OBJECTIVE OF MODULE 2
To create a:
Secure, scalable, configurable user-access ecosystem
for the complete AsliChoice platform covering:
Inventory 
POS 
CRM 
Online Store 
Referral Engine 
Wallet 
Reporting 
Admin Controls 
Multi-branch Operations

MODULE 3 — VENDOR MANAGEMENT
for AsliChoice

Purpose
Vendor Management handles:
supplier onboarding, 
supplier relationships, 
procurement controls, 
vendor pricing, 
payment terms, 
and vendor analytics. 
This module becomes the:
Procurement Foundation
for the Purchase and Inventory ecosystem.

CORE PHILOSOPHY
Vendor ≠ Just Contact Record
A vendor should become:
A fully trackable procurement entity
with:
transaction history, 
pricing history, 
payment behavior, 
supply performance, 
and analytics. 

MAIN SUBMODULES

1. Vendor Master
Central vendor database.

Basic Vendor Fields
Business Information
Vendor Name 
Company Name 
Vendor Code 
GST Number 
PAN Number 
Vendor Category 
Business Type 

Contact Information
Mobile Number 
Email Address 
Alternate Contact 
Website (future) 

Address Information
Billing Address 
Pickup Address 
Warehouse Address 

Banking Information
Account Holder Name 
Bank Name 
Account Number 
IFSC Code 
UPI ID (future) 

Tax Information
GST Type 
GST State 
TDS Applicability (future) 

Important Recommendation
Vendor Code Auto Generation
Example:
VEN-0001
Avoid manual vendor codes.

2. Vendor Categories
Supports classification.

Example Categories
RAW_MATERIAL
PACKAGING
TRANSPORT
SERVICE_PROVIDER
DISTRIBUTOR
MANUFACTURER

Why Important?
Useful for:
analytics, 
filtering, 
purchase rules, 
reporting. 

3. Vendor Status Management

Recommended Statuses
ACTIVE
INACTIVE
BLACKLISTED
ON_HOLD

Important Rule
Blacklisted vendors should:
not appear in purchase creation, 
not allow transactions. 

4. Vendor Contact Persons
Supports multiple contacts per vendor.

Example
Accounts Person
Sales Representative
Dispatch Coordinator

Fields
Name 
Designation 
Mobile 
Email 

5. Vendor Payment Terms
Very important for procurement.

Examples
Advance Payment
Net 7 Days
Net 15 Days
Net 30 Days

Important Features
default payment terms, 
purchase-level override, 
credit tracking (future). 

6. Vendor Pricing Management
Supports:
vendor-specific pricing, 
negotiated procurement rates. 

Example
Vendor A → Ghee Jar = ₹25
Vendor B → Ghee Jar = ₹23

Important Recommendation
Maintain Price History
Track:
previous rates, 
effective dates, 
vendor pricing trends. 
Very useful later.

7. Vendor Product Mapping
Maps:
Vendor ↔ Products Supplied

Features
preferred vendor, 
multiple vendors per product, 
lead time tracking, 
minimum order quantity. 

Example
Product: Peanut Butter Jar
Preferred Vendor: XYZ Packaging
Lead Time: 5 Days
MOQ: 1000 Units

8. Vendor Performance Tracking
Important future-ready feature.

Metrics
Delivery Performance
on-time delivery, 
delayed delivery. 

Quality Performance
damaged supplies, 
rejection rate. 

Pricing Stability
price fluctuation tracking. 

Purchase Volume
total purchase amount, 
frequency. 

Future Analytics
Vendor scorecards.
Example:
Vendor Rating = 4.5/5

9. Vendor Documents
Supports:
GST certificate, 
agreements, 
quotations, 
licenses. 

Recommended Features
upload documents, 
expiry tracking, 
document verification status. 

10. Vendor Communication Log
Track:
calls, 
emails, 
meetings, 
negotiations. 

Why Important?
Useful for:
procurement follow-up, 
vendor dispute handling, 
accountability. 

11. Vendor Notes & Remarks
Supports internal notes.
Example:
Frequently delays dispatch during festivals.

Important Rule
Internal notes should NOT be vendor-visible.

12. Vendor Branch Mapping
Optional future-ready feature.
Supports:
Vendor accessible only to specific branches
Useful for:
local procurement, 
branch-specific vendors. 

13. Vendor Approval Workflow (Future)
For enterprise scaling.

Example Flow
Vendor Created
      ↓
Verification Pending
      ↓
Approval
      ↓
Vendor Activated

14. Vendor Ledger (Future Finance Integration)
Tracks:
total purchases, 
payments, 
outstanding balance, 
debit/credit notes. 

Important Recommendation
Keep:
Finance-ready schema from Day 1.

15. Vendor Portal (Future Expansion)
Future feature.
Vendor can:
view purchase orders, 
track payments, 
upload invoices, 
manage dispatch status. 

VENDOR SEARCH & FILTERING
Recommended filters:
category, 
status, 
city, 
GST state, 
product supplied. 

RECOMMENDED VALIDATIONS
GST Validation
Format validation mandatory.

Duplicate Detection
Prevent duplicate vendors based on:
GST number, 
mobile number, 
company name. 

Important Recommendation
Soft Delete Only
Never permanently delete vendors.
Use:
is_active = false

VENDOR REPORTS

Recommended Reports
Vendor List Report

Vendor-wise Purchase Report

Vendor Outstanding Report

Vendor Product Mapping Report

Vendor Performance Report

Purchase Trend Report

RECOMMENDED PERMISSIONS
VENDOR_VIEW
VENDOR_CREATE
VENDOR_EDIT
VENDOR_APPROVE
VENDOR_EXPORT

FINALIZED RULES
Rule 1
Vendor deletion not allowed.

Rule 2
Vendor pricing history must be preserved.

Rule 3
Blacklisted vendors cannot transact.

Rule 4
Vendor-product mapping should support multiple vendors.

Rule 5
Vendor notes remain internal only.

RECOMMENDED DATABASE TABLES
vendors
vendor_contacts
vendor_categories
vendor_products
vendor_price_history
vendor_documents
vendor_notes
vendor_payment_terms
vendor_communications
vendor_branch_mapping
vendor_ledgers

RECOMMENDED ARCHITECTURE
Backend
Procurement-ready vendor service 
Vendor analytics engine 
Price history management 

Frontend
Vendor profile dashboard 
Vendor analytics 
Vendor document management 
Product mapping UI 

FINAL OBJECTIVE OF MODULE 3
To create a:
Scalable, analytics-ready procurement vendor ecosystem
for the complete AsliChoice platform supporting:
Purchase Management 
Inventory Planning 
Procurement Optimization 
Vendor Analytics 
Multi-branch Procurement 
Future Finance Integration 

UPDATED MODULE 4 — PURCHASE MANAGEMENT
for AsliChoice

Purpose
Purchase Management handles:
centralized procurement, 
vendor purchasing, 
procurement approvals, 
branch-wise stock inwarding, 
invoice management, 
and procurement analytics. 
This module acts as the:
Controlled Procurement Engine
for the entire platform.

FINALIZED PROCUREMENT PHILOSOPHY
Centralized Procurement + Distributed Inventory
Procurement Control
Handled only by:
HEAD OFFICE (HO)
OR
MAIN BRANCH

Inventory Ownership
Belongs to:
Branch + Warehouse

IMPORTANT ARCHITECTURE
HO controls:
procurement, 
vendor negotiations, 
purchase approvals. 
BUT
Inventory can directly belong to:
any branch, 
any warehouse. 

FINALIZED PROCUREMENT FLOW
Scenario 1 — Central Warehouse Procurement
Vendor
   ↓
HO Purchase
   ↓
HO Warehouse GRN
   ↓
HO Inventory
   ↓
Branch Transfer

Scenario 2 — Direct Branch Procurement
HO Creates PO
      ↓
Vendor Delivers Directly to Branch
      ↓
Branch GRN
      ↓
Branch Inventory Updated

MAIN SUBMODULES

1. Purchase Requisition
Purpose
Internal procurement request.

Finalized Rule
Only:
HO / MAIN BRANCH
can create requisitions.

Requisition Fields
Header
Requisition Number 
Requesting Branch 
Destination Branch 
Destination Warehouse 
Requested By 
Priority 
Notes 

Item Details
Product 
Variant 
Quantity 
Required Date 
Remarks 

Priority Levels
LOW
MEDIUM
HIGH
URGENT

Requisition Status Flow
DRAFT
↓
SUBMITTED
↓
APPROVED
↓
PARTIALLY_PROCESSED
↓
COMPLETED
↓
REJECTED

Important Rules
Requisition does NOT affect inventory.

Multiple requisitions can merge into single PO.

Example
Pune Requirement + Mumbai Requirement
→ Single Vendor PO

2. Purchase Order (PO)
Purpose
Official procurement order sent to vendor.

FINALIZED PO STRUCTURE
Header Fields
PO Number 
Vendor 
Procurement Branch (HO/Main Branch) 
Destination Branch 
Destination Warehouse 
PO Date 
Expected Delivery Date 
Payment Terms 
Notes 

Item Fields
Product 
Variant 
Quantity 
Unit 
Purchase Rate 
Tax 
Discount 
Total Amount 

IMPORTANT NEW FIELDS
Destination Branch
Defines:
Who owns inventory

Destination Warehouse
Defines:
Where stock will inward

PO Statuses
DRAFT
PENDING_APPROVAL
APPROVED
PARTIALLY_RECEIVED
COMPLETED
CANCELLED

Important Features
auto-generated PO numbers, 
branch-specific procurement, 
warehouse-specific inwarding, 
approval workflow support. 

3. Purchase Approval Workflow
Suggested Initial Logic
Small purchases:
Auto Approved
Large purchases:
Admin Approval Required

Future Workflow
Manager
→ Admin
→ Super Admin

4. Goods Receipt Note (GRN)
Most Critical Inventory Component

Purpose
Confirms:
Actual stock received

FINALIZED INVENTORY RULE
Inventory updates ONLY after GRN.
NOT after PO.

UPDATED GRN LOGIC
GRN updates:
Destination Branch Inventory
+
Destination Warehouse Inventory

GRN Fields
GRN Number 
Linked PO 
Destination Branch 
Destination Warehouse 
Received Quantity 
Damaged Quantity 
Receiver 
Notes 

Important Rule
Branch inventory ownership starts after GRN.

5. Partial Receipt Handling
Supports:
partial delivery, 
multiple inwarding. 

Example
PO = 100 Units
Delivery 1 = 60
Delivery 2 = 40

Status
PARTIALLY_RECEIVED

6. Purchase Invoice Management
Features
invoice upload, 
invoice number, 
GST details, 
tax breakup, 
PO linkage, 
GRN linkage, 
vendor linkage. 

Important Recommendation
Invoice should remain:
Finance-ready from Day 1.

7. Purchase Return Management
Handles:
damaged goods, 
wrong products, 
expired stock, 
rejected items. 

Return Reasons
DAMAGED
WRONG_PRODUCT
EXPIRED
QUALITY_ISSUE

Important Rule
Purchase return must affect:
branch inventory, 
warehouse stock, 
vendor ledger, 
procurement analytics. 

8. Vendor Credit & Payment Tracking
Tracks:
outstanding amount, 
due dates, 
advance payments, 
partial payments. 

Payment Modes
Cash
UPI
Bank Transfer
Cheque

9. Purchase Attachments
Supports:
invoices, 
quotations, 
transport receipts, 
delivery documents. 

10. Purchase Notes & Remarks
Internal procurement notes.
Example:
Vendor promised replacement in next shipment.

11. Inventory Integration
Finalized Inventory Movement Type
PURCHASE

Finalized Rule
Inventory updates:
only through GRN.

Inventory Ownership Logic
Inventory belongs to:
Destination Branch + Warehouse

12. Multi-branch Procurement
HO can:
purchase for HO, 
purchase for any branch, 
purchase for any warehouse. 

IMPORTANT RULE
Branches cannot directly purchase from vendors.

13. Purchase Analytics
Recommended Analytics
Branch-wise procurement 
Vendor-wise procurement 
Product purchase trends 
Purchase cost trends 
Delayed delivery tracking 
Purchase return analytics 

14. Purchase Reports
Recommended Reports
Purchase Register 
PO Report 
GRN Report 
Branch-wise Purchase Report 
Vendor-wise Purchase Report 
Pending PO Report 
Purchase Return Report 
Outstanding Vendor Report 

15. Barcode Integration
Supports:
inward barcode scanning, 
warehouse scanning, 
GRN verification. 

16. Offline Purchase Support (Future)
Queue-based sync support for:
warehouses, 
low internet branches. 

FINALIZED PURCHASE STATUS FLOW
DRAFT
↓
APPROVED
↓
PARTIALLY_RECEIVED
↓
COMPLETED

RECOMMENDED PERMISSIONS
PURCHASE_VIEW
PURCHASE_CREATE
PURCHASE_APPROVE
PURCHASE_GRN
PURCHASE_RETURN
PURCHASE_EXPORT
REQUISITION_CREATE
REQUISITION_APPROVE
REQUISITION_CONVERT_TO_PO

FINALIZED RULES
Rule 1
Only HO/Main Branch can create requisitions.

Rule 2
Branches cannot directly procure from vendors.

Rule 3
HO can purchase for any branch.

Rule 4
Inventory ownership belongs to destination branch.

Rule 5
Inventory updates only after GRN.

Rule 6
Purchase returns reverse branch inventory.

Rule 7
Partial receipts fully supported.

Rule 8
Vendor ledger integration mandatory.

RECOMMENDED DATABASE TABLES
purchase_requisitions
purchase_requisition_items
purchase_orders
purchase_order_items
goods_receipts
goods_receipt_items
purchase_invoices
purchase_returns
purchase_return_items
purchase_payments
vendor_ledgers
purchase_attachments
purchase_notes
purchase_status_logs

RECOMMENDED ARCHITECTURE
Backend
centralized procurement engine, 
branch-aware inventory inwarding, 
GRN inventory integration, 
vendor ledger service. 

Frontend
procurement dashboard, 
branch-wise inwarding screens, 
GRN verification UI, 
procurement analytics. 

FINAL OBJECTIVE OF MODULE 4
To create a:
Centralized procurement + distributed inventory purchase ecosystem
for the complete AsliChoice platform supporting:
HO-controlled procurement 
Branch inventory ownership 
Warehouse-wise inwarding 
Procurement governance 
Vendor tracking 
Purchase analytics 
Multi-branch operations 
Future finance integration

MODULE 5 — INVENTORY MANAGEMENT
for AsliChoice

Purpose
Inventory Management controls:
branch-wise stock,
warehouse-wise stock,
stock movement,
stock visibility,
inventory audits,
reservations,
transfers,
and inventory accountability.
This module becomes the:
Central Operational Engine
of the entire platform.

FINALIZED INVENTORY PHILOSOPHY
Centralized Inventory Engine
with
Distributed Branch Ownership
Meaning:
Single Inventory System
        +
Branch-wise Inventory Ownership

IMPORTANT INVENTORY PRINCIPLE
Inventory belongs to:
Branch + Warehouse
NOT globally.

FINALIZED PROCUREMENT & INVENTORY FLOW
Scenario 1 — HO Procurement
Vendor
   ↓
HO Purchase
   ↓
HO Warehouse GRN
   ↓
HO Inventory
   ↓
Branch Transfer

Scenario 2 — Direct Branch Procurement
HO Purchase
   ↓
Vendor Delivers Directly to Branch
   ↓
Branch GRN
   ↓
Branch Inventory Updated

IMPORTANT RULE
All channels use:
Same Central Inventory Engine
Used by:
Online Store
Retail POS
Internal Consumption
Future Wholesale
Returns

CORE INVENTORY STRUCTURE
System tracks:
Available Stock
Reserved Stock
Damaged Stock
Transit Stock
Blocked Stock

Definitions
Available Stock
Sellable stock.

Reserved Stock
Allocated for:
online orders,
draft invoices,
future bookings.

Damaged Stock
Unsellable inventory.

Transit Stock
Inventory moving between:
branches,
warehouses.

Blocked Stock
Restricted stock.
Example:
quality hold,
inspection.

MAIN SUBMODULES

1. Inventory Ledger System
Most Critical Component

FINALIZED RULE
No direct stock editing allowed.
Every stock movement creates:
Inventory Ledger Entry

Example Ledger Entries
+100 PURCHASE
-2 POS_SALE
-1 INTERNAL_CONSUMPTION
+5 SALES_RETURN
-20 TRANSFER_OUT
+20 TRANSFER_IN

Ledger Fields
Product
Variant
Branch
Warehouse
Movement Type
Quantity Change
Before Quantity
After Quantity
Reference Number
User
Timestamp

Important Rule
Inventory must always remain:
Ledger Driven

2. Branch-wise Inventory
Each branch maintains:
separate stock,
separate inventory visibility,
separate stock reports,
separate inventory analytics.

Example
Pune Branch → 120 Units
Mumbai Branch → 80 Units

Important Rule
Users only access:
authorized branch inventory.

3. Warehouse Management
Supports:
multiple warehouses,
stores,
godowns,
damage warehouses.

Recommended Warehouse Types
MAIN_WAREHOUSE
STORE_WAREHOUSE
DAMAGE_WAREHOUSE
TRANSIT_WAREHOUSE

Warehouse Features
warehouse-wise stock,
warehouse managers,
warehouse status,
warehouse mapping.

4. Stock Movement Types
Every inventory change must have movement classification.

Finalized Movement Types
PURCHASE
SALE
RETURN
TRANSFER_IN
TRANSFER_OUT
ADJUSTMENT
DAMAGE
INTERNAL_CONSUMPTION
OPENING_STOCK

Future Movement Types
MANUFACTURING
ASSEMBLY
BUNDLE
SUBSCRIPTION_RESERVE

5. Stock Transfer Management
Supports:
HO → Branch
Branch → Branch
Warehouse → Warehouse

Transfer Workflow
Source Warehouse
      ↓
Transfer Created
      ↓
Transit Stock
      ↓
Destination Receives
      ↓
Inventory Updated

Transfer Statuses
PENDING
IN_TRANSIT
RECEIVED
CANCELLED

Important Rules
Source inventory reduces immediately.

Destination inventory increases only after receiving confirmation.

6. Inventory Reservation System
Important for:
online orders,
draft invoices,
future order booking.

Example
Available = 50
Reserved = 10
Sellable = 40

Important Rule
Reservations auto-expire if:
order abandoned,
order cancelled.

7. Damaged Inventory Management
Tracks:
damaged stock,
expired stock,
leakage,
unusable stock.

Suggested Reasons
BROKEN
EXPIRED
LEAKAGE
QUALITY_ISSUE

Features
damage quantity,
damage warehouse,
damage reporting.

8. Inventory Adjustment
Used for:
stock mismatch,
audit correction,
setup correction.

Important Rule
Adjustments require:
permission,
reason,
audit logs.

Suggested Reasons
PHYSICAL_COUNT
SYSTEM_CORRECTION
MISPLACED
INITIAL_SETUP

Important Rule
Every adjustment creates:
inventory ledger entry.

9. Opening Stock Management
Supports:
migration,
initial inventory setup.

Finalized Rule
Opening stock:
creates ledger entry,
remains separately identifiable.

10. Batch & Expiry Management (Future Ready)
Useful for:
ghee,
oils,
FMCG products.

Features
batch number,
manufacturing date,
expiry date,
batch-wise stock,
FIFO support.

Important Recommendation
Keep schema ready from Day 1.

11. Barcode Management
Barcode-ready architecture from beginning.

Features
barcode generation,
barcode scanning,
inventory search,
POS barcode integration.

Future Features
QR support,
barcode label printing.

12. Inventory Audit System
Supports:
physical stock counting,
cycle counting,
stock verification.

Features
stock count sheets,
variance reports,
audit workflow (future).

13. Low Stock Alerts
Supports:
branch-wise low stock alerts,
warehouse-wise thresholds.

Example
Minimum Stock = 20
Current Stock = 5
→ Low Stock Alert

Future Notifications
Email
WhatsApp
Push Notifications

14. Inventory Visibility Logic
POS Inventory Visibility
POS should show:
Current Branch Inventory Only

Example
Pune POS
→ Pune Branch Inventory

Optional Feature
Cross-branch stock lookup:
Out of stock in Pune
Available in Mumbai
Permission-controlled.

IMPORTANT POS RULE
POS sales consume:
local branch inventory only.

15. Online Inventory Visibility
FINALIZED RULE
Online stock should be:
Location-Aware

Flow
Customer Location
      ↓
Nearest Fulfillment Branch
      ↓
Show Relevant Inventory

Example
Pune Customer
→ Pune Branch Inventory

Important Rule
Online stock visibility:
should NOT show global stock.

Online Fulfillment Logic
System checks:
Nearest Branch
↓
City Warehouse
↓
HO Warehouse

Important Recommendation
Maintain:
Online Sellable Quantity
Example:
Physical Stock = 100
Reserved Buffer = 20
Online Sellable = 80

Fulfillment-enabled Branches
Not every branch should fulfill online orders.

Branch Setting
Online Fulfillment Enabled = YES/NO

16. Inventory Reports
Recommended Reports
Stock Summary
Inventory Ledger
Branch-wise Inventory
Warehouse-wise Inventory
Low Stock Report
Damaged Stock Report
Fast-moving Stock
Slow-moving Stock
Dead Stock Report
Inventory Valuation Report
Expiry Report (future)
Online Fulfillment Report

17. Offline Inventory Sync
Important for:
POS,
unstable internet branches.

Finalized Principle
Offline inventory transactions:
queue locally,
sync later,
use conflict resolution.

Important Recommendation
Use:
Inventory Transaction Queue
instead of overwrite sync.

18. Inventory Valuation
Recommended Methods
FIFO
AVERAGE_COST
Avoid LIFO initially.

19. Inventory Permissions
Recommended Permissions
STOCK_VIEW
STOCK_TRANSFER
STOCK_ADJUST
STOCK_AUDIT
STOCK_EXPORT

FINALIZED INVENTORY RULES
Rule 1
Inventory is ledger-driven.

Rule 2
No direct quantity editing allowed.

Rule 3
Every movement creates audit trail.

Rule 4
Inventory belongs to:
Branch + Warehouse

Rule 5
POS visibility is branch-specific.

Rule 6
POS sales consume local branch inventory only.

Rule 7
Online inventory visibility is location-aware.

Rule 8
Inventory updates from purchase only after GRN.

Rule 9
Transfer destination inventory updates only after receiving confirmation.

Rule 10
Internal Consumption reduces inventory immediately.

RECOMMENDED DATABASE TABLES
inventory
inventory_ledger
inventory_movements
stock_transfers
stock_transfer_items
warehouses
warehouse_stocks
damaged_inventory
inventory_adjustments
inventory_reservations
batch_inventory
opening_stock
stock_audits

FINAL OBJECTIVE OF MODULE 5
To create a:
Centralized inventory engine with distributed branch ownership and location-aware visibility
for the complete AsliChoice platform supporting:
Purchase Management
Retail POS
Online Store
Branch Transfers
Internal Consumption
Inventory Audits
Inventory Analytics
Multi-branch Operations
Future Manufacturing & Distribution Expansion

MODULE 6 — ONLINE STORE
for AsliChoice

Purpose
Online Store handles:
ecommerce storefront,
customer shopping experience,
location-aware inventory visibility,
cart & checkout,
delivery & fulfillment,
online ordering,
referral integration,
wallet integration,
and omnichannel ecommerce operations.
This module becomes the:
Digital Commerce Channel
of the platform.

FINALIZED ECOMMERCE PHILOSOPHY
Online Store is NOT a separate system.
It uses the same:
inventory,
pricing,
customers,
orders,
wallet,
referral engine,
offers engine.

IMPORTANT PRINCIPLE
Ecommerce is a:
Sales Channel
inside the centralized commerce ecosystem.

MAIN SUBMODULES

1. Customer Storefront
Main ecommerce interface.

Features
homepage,
banners,
categories,
product listing,
offers,
search,
featured products.

Important Recommendation
Storefront should be:
Mobile-first

2. Product Catalog
Displays:
products,
variants,
pricing,
stock availability,
product details,
offers.

Product Information
product name,
images,
description,
nutrition facts,
pricing,
availability.

Product Visibility Control
Products can be:
ONLINE_VISIBLE = YES/NO

Important Rule
POS-only products remain hidden online.

3. Intelligent Location Selection System
FINALIZED RULE
System should:
Auto-suggest customer location
BUT:
customer confirmation is mandatory.

Returning Customer Flow
Customer Opens Store
       ↓
System Detects Previous Pincode
       ↓
Auto Suggest Location
       ↓
Customer Confirms/Changes
       ↓
Load Inventory & Delivery Rules

New Customer Flow
Open Store
    ↓
Detect/Suggest Location
    ↓
Customer Confirms

Auto-Detection Priority
1. Last Selected Pincode
2. Default Saved Address
3. GPS Detection (optional)
4. Manual Selection

Important Rule
Inventory loads:
Only after location confirmation.

4. Mandatory Pincode-Based Shopping
FINALIZED RULE
Shopping experience is:
Pincode-Aware
because:
inventory is branch-aware,
delivery is pincode-aware,
offers may vary by location,
fulfillment is branch-based.

5. Location-Aware Inventory Visibility
FINALIZED RULE
Online inventory visibility should be:
Location-Based

Flow
Customer Pincode
      ↓
Nearest Fulfillment Branch
      ↓
Show Relevant Inventory

Example
Pune Customer
→ Pune Branch Inventory

Important Rule
Customers should NOT see:
Global Stock Quantity

Fulfillment Priority
Nearest Branch
↓
City Warehouse
↓
HO Warehouse

Online Sellable Quantity
Maintain:
Online-specific sellable stock
Example:
Physical Stock = 100
Reserved Buffer = 20
Online Sellable = 80

Fulfillment-enabled Branches
Branch setting:
Online Fulfillment Enabled = YES/NO

6. Product Search & Filters
Supports:
keyword search,
category filters,
brand filters,
price filters,
availability filters.

Future Features
AI recommendations,
voice search,
smart search.

7. Shopping Cart
Supports:
add/remove products,
quantity updates,
coupon application,
referral code application.

Important Rule
Cart validates:
Live Inventory
before checkout.

8. Checkout System
Supports:
address selection,
delivery validation,
payment selection,
order summary.

Important Recommendation
Checkout should remain:
Fast & Minimal

9. Customer Registration & Access Control
FINALIZED RULE
Only:
Registered Customers
can place orders.

Guest Users Can
browse products,
view offers,
check delivery availability,
explore store.

Optional
Guest cart allowed.
BUT:
Login/Register mandatory before checkout.

10. Intelligent Registration Approval System
FINALIZED RULE
Customer registration depends on:
Pincode Serviceability

Flow
Customer Registers
       ↓
Check Pincode
       ↓
Serviceable?
   ↓ YES             ↓ NO
Auto Approve      Generate Admin Request

Serviceable Pincode
Customer:
Auto Approved
after OTP verification.

Non-Serviceable Pincode
Instead of rejection:
Generate Admin Serviceability Request
Admin can:
contact customer,
explain service limitation,
evaluate future expansion.

Important Rule
Non-serviceable customers remain:
Stored in CRM

11. Pincode Serviceability Engine
FINALIZED DELIVERY ZONES
Supports:
STANDARD
EXTENDED
PREMIUM_SPECIAL
NON_SERVICEABLE

STANDARD Zone
Normal delivery area.

EXTENDED Zone
Supports:
extra delivery charges,
higher MOV.

PREMIUM_SPECIAL Zone
Supports:
manual approval,
premium delivery,
exceptional servicing.

NON_SERVICEABLE Zone
Ordering blocked,
admin request generated.

12. Delivery Charge Engine
FINALIZED RULE
Delivery charges should be:
Pincode-Based

Each Pincode Can Define
delivery fee,
extra delivery fee,
free delivery threshold,
delivery ETA,
COD availability,
assigned branch.

Example
Standard Zone
Delivery = ₹40
Free Above ₹999

Extended Zone
Delivery = ₹120
Higher MOV Required

13. Minimum Order Value (MOV) Engine
FINALIZED RULE
MOV varies:
By Pincode / Delivery Zone

Example
Standard Zone
Minimum Order = ₹299

Extended Zone
Minimum Order = ₹999

Checkout Validation
System validates:
serviceability,
delivery fee,
MOV eligibility,
inventory availability.

14. Delivery & Fulfillment Logic
FINALIZED FLOW
Customer Location
      ↓
Fulfillment Branch Selection
      ↓
Inventory Reservation
      ↓
Order Confirmation
      ↓
Branch Dispatch

Delivery Models (Future)
STANDARD_DELIVERY
SAME_DAY_DELIVERY
STORE_PICKUP

15. Inventory Reservation
Inventory reserves:
During Order Placement

Example
Available = 20
Reserved = 5
Sellable = 15

Important Rule
Reservations auto-expire if:
payment fails,
order cancelled,
cart abandoned.

16. Order Management
Handles:
order lifecycle,
customer tracking,
fulfillment tracking.

Order Status Flow
PENDING
↓
CONFIRMED
↓
PACKED
↓
SHIPPED
↓
DELIVERED
↓
COMPLETED

Additional Statuses
CANCELLED
RETURNED
REFUNDED

Important Rule
All order events create:
Audit Trail

17. Payment Gateway Integration
Supports:
UPI,
cards,
net banking,
COD,
wallet payments.

Future Integrations
Razorpay
PhonePe
Paytm

Payment Modes
ONLINE_PAYMENT
COD
WALLET

Important Rule
Payment success triggers:
Order Confirmation

18. Offers & Coupon Engine
FINALIZED RULE
Offers can be:
Online-only,
POS-only,
Shared across both.

Offer Channel Types
ONLINE
POS
BOTH

Features
coupon codes,
flat discounts,
percentage discounts,
category offers,
referral offers.

19. Referral Integration
Integrated with:
Referral & Partner Engine

Finalized Logic
Successful Referral
      ↓
Wallet Commission Credited

Important Rule
Referral rewards trigger only after:
Successful Order Completion

20. Wallet Integration
Supports:
wallet redemption,
referral rewards,
future cashback.

Important Rule
Wallet maintains:
Transaction Ledger

21. Customer Account Panel
Customer can manage:
profile,
addresses,
orders,
wallet,
referrals,
saved products.

Features
reorder,
invoice download,
order tracking.

22. Wishlist System
Supports:
save products,
future purchase planning.

Future Features
stock alerts,
price drop alerts.

23. Notifications
Supports:
order confirmation,
payment confirmation,
shipping updates,
delivery updates.

Future Channels
SMS
Email
WhatsApp
Push Notifications

24. SEO & Marketing Features
Supports:
SEO URLs,
meta tags,
sitemap generation.

Future Marketing Features
abandoned cart recovery,
recommendation engine,
automation campaigns.

25. Online Reports & Analytics
Recommended Reports
online sales report,
pincode-wise sales,
branch fulfillment report,
delivery profitability,
cart abandonment,
offer usage analytics,
location-wise demand analytics.

26. Security Features
Supports:
secure checkout,
payment validation,
fraud prevention,
audit logging.

Important Rule
Sensitive payment data:
must never be stored directly.

RECOMMENDED DATABASE TABLES
online_orders
online_order_items
customer_addresses
shopping_carts
cart_items
wishlists
wishlist_items
online_payments
coupons
coupon_usages
serviceable_pincodes
online_fulfillment_logs
order_status_logs
customer_serviceability_requests

FINALIZED ONLINE STORE RULES
Rule 1
Location confirmation mandatory before inventory loading.

Rule 2
System may auto-suggest customer location.

Rule 3
Inventory visibility is pincode/location-aware.

Rule 4
Only registered customers can place orders.

Rule 5
Serviceable pincodes auto-approve customers.

Rule 6
Non-serviceable pincodes generate admin requests.

Rule 7
Offers can be:
ONLINE
POS
BOTH

Rule 8
Delivery charges are pincode-aware.

Rule 9
MOV is pincode/zone-aware.

Rule 10
Checkout validates:
inventory,
serviceability,
delivery charges,
MOV eligibility.

FINAL OBJECTIVE OF MODULE 6
To create a:
Location-aware omnichannel ecommerce ecosystem
for the complete AsliChoice platform supporting:
Online Sales
Branch-based Fulfillment
Hyperlocal Delivery
Referral Commerce
Wallet Integration
Pincode-based Logistics
Multi-branch Ecommerce Operations
Future Regional Expansion

MODULE 7 — RETAIL POS
for AsliChoice

Purpose
Retail POS handles:
retail billing,
cashier operations,
branch-wise sales,
stock-aware billing,
barcode/manual product selection,
payment collection,
retail offers,
customer tagging,
wallet redemption,
and offline retail operations.
This module becomes the:
Physical Retail Sales Channel
of the platform.

FINALIZED POS PHILOSOPHY
POS is NOT a separate inventory system.
It uses the same:
inventory engine,
pricing engine,
offers engine,
customer database,
wallet system,
commerce engine.

IMPORTANT PRINCIPLE
POS is:
Branch-Specific
Each POS works using:
Current Branch Inventory Only

MAIN SUBMODULES

1. POS Billing Interface
Main billing screen for cashier operations.

Recommended UI Layout
Left Side:
- Search
- Categories
- Product List

Right Side:
- Current Bill
- Totals
- Payment

Important Recommendation
POS UI should remain:
Fast & Minimal
for high-speed billing.

2. Product Selection Methods
FINALIZED RULE
POS supports BOTH:
barcode billing,
manual product selection.

Supported Selection Methods

Barcode Billing
If barcode exists:
Scan Barcode
      ↓
Load Product
      ↓
Add to Bill

Important Rule
Barcode support should:
improve speed
NOT become mandatory.

Manual Product Selection
Cashier can:
search products,
select variants,
browse categories.

Search Supports
product name,
SKU,
category,
partial typing.

Example
Search: Ghee
→ Show Available Ghee Products

Important Rule
POS shows:
Current Branch Inventory Only

3. Strict Stock-aware Billing
FINALIZED RULE
POS validates:
Real-time stock availability
before billing.

Important Policy
Negative stock is:
STRICTLY NOT ALLOWED

Example
Available Stock = 5
Cashier Adds = 6
→ Billing Blocked

Allowed Scenario
Available Stock = 5
Billing Quantity = 5
→ Allowed
Stock becomes 0

Important Rule
Inventory may become:
ZERO
BUT:
Never below zero.

POS Validation Rule
POS must:
hard-block overselling
NOT only warning.

4. Category-Based Quick Billing
Useful for:
grocery stores,
touch-screen POS,
fast-moving counters.

Example Categories
Honey
Ghee
Peanut Butter
Oils

Flow
Category
   ↓
Product
   ↓
Add to Bill

5. Frequently Sold / Recent Products
Supports:
frequent products,
recent items,
favorite items.

Purpose
Improves:
Billing Speed

6. Variant-aware Billing
Supports:
product variants,
size selection,
pack selection.

Example
Cow Ghee
→ 500ml
→ 1L
→ 5L

7. Customer Management in POS
Supports:
existing customer selection,
mobile search,
member lookup,
new customer creation.

Important Rule
Customer tagging remains:
Optional
for walk-in billing.

Suggested Customer Types
WALK_IN
REGISTERED
PARTNER

8. POS Offers & Discounts
FINALIZED RULE
Offers can be:
POS-only,
Online-only,
shared across both.

Offer Channel Types
ONLINE
POS
BOTH

Supported Discounts
flat discounts,
percentage discounts,
bill-level discounts,
product-level discounts.

Important Rule
Offer validation must include:
POS Channel

9. Payment Collection
Supports:
cash,
UPI,
cards,
mixed payments,
wallet redemption.

Payment Modes
CASH
UPI
CARD
WALLET
MIXED

Important Recommendation
Support:
Multi-payment Billing
Example:
₹500 Cash
₹300 UPI

10. Wallet Integration
Supports:
wallet redemption,
loyalty rewards,
referral wallet usage.

Important Rule
Wallet maintains:
Transaction Ledger

11. Invoice & Receipt Printing
Supports:
thermal printing,
A4 invoices,
digital receipts.

Receipt Content
branch details,
GST details,
products,
payment summary,
savings/offers.

Future Features
WhatsApp receipt,
email receipt,
QR invoice.

12. Sales Returns & Exchanges
Supports:
full return,
partial return,
product exchange.

Important Rule
Returns should:
Restore Branch Inventory

Return Reasons
DAMAGED
WRONG_PRODUCT
CUSTOMER_RETURN

13. Offline POS Support
Most Critical Feature
POS should work:
Without Internet

FINALIZED OFFLINE FLOW
Offline Billing
      ↓
Store Local Queue
      ↓
Sync Later

Important Rules
Offline POS remains:
Branch-scoped

Offline stock must remain:
locally consistent

Example
Local Stock = 5
Offline Sale = 5
→ Local Available = 0
Next Billing Blocked

Offline Requirements
local inventory cache,
local product cache,
offline invoice numbering,
sync conflict handling.

14. POS Inventory Consumption
FINALIZED RULE
POS sales consume:
Current Branch Inventory Only

Important Rule
POS should NEVER:
use global inventory.

Optional Feature
Cross-branch stock lookup.
Example:
Out of stock in Pune
Available in Mumbai
Permission-controlled.

15. Cashier & Shift Management
Supports:
cashier login,
shift opening,
shift closing,
cash reconciliation.

Features
opening balance,
closing balance,
cash mismatch tracking.

16. POS Reports
Recommended Reports
daily sales report,
cashier-wise sales,
branch-wise sales,
payment-mode report,
return report,
discount report,
item-wise sales.

17. POS Notifications (Future)
Supports:
low stock alerts,
shift alerts,
billing alerts.

18. Security & Audit
Supports:
bill audit logs,
cashier tracking,
refund approval tracking.

Important Rule
All billing actions create:
Audit Trail

19. POS Performance Optimization
Important for:
high-speed billing,
touch-screen systems,
offline retail operations.

Recommended Optimizations
local caching,
lightweight UI,
fast product search,
keyboard shortcuts.

RECOMMENDED PERMISSIONS
POS_BILLING
POS_RETURN
POS_DISCOUNT
POS_CASHIER_CLOSE
POS_REPORT_VIEW
POS_REFUND_APPROVE

RECOMMENDED DATABASE TABLES
pos_sales
pos_sale_items
pos_payments
pos_returns
pos_return_items
cashier_shifts
cashier_sessions
pos_devices
offline_sync_queue

FINALIZED POS RULES
Rule 1
POS is branch-specific.

Rule 2
POS consumes local branch inventory only.

Rule 3
Barcode billing is optional.

Rule 4
Manual product selection fully supported.

Rule 5
POS validates stock availability before billing.

Rule 6
Negative stock strictly prohibited.

Rule 7
Billing allowed only until stock reaches zero.

Rule 8
POS hard-blocks overselling.

Rule 9
Offers can be:
ONLINE
POS
BOTH

Rule 10
POS supports offline billing.

Rule 11
Offline POS remains branch-scoped.

Rule 12
Offline inventory must remain locally consistent.

Rule 13
Returns restore branch inventory.

Rule 14
All billing actions create audit trail.

FINAL OBJECTIVE OF MODULE 7
To create a:
Fast, branch-aware, offline-capable, strictly stock-controlled omnichannel retail POS ecosystem
for the complete AsliChoice platform supporting:
Retail Billing
Branch Inventory Consumption
Offline Retail Operations
Omnichannel Offers
Wallet Redemption
Customer Tagging
Sales Returns
Strict Inventory Control
High-speed Retail Operations

MODULE 8 — SALES & ORDER MANAGEMENT
for AsliChoice

Purpose
Sales & Order Management handles:
online orders,
POS sales,
future wholesale sales,
sales lifecycle,
order tracking,
invoicing,
payments,
returns,
customer sales history,
and omnichannel commerce workflows.
This module becomes the:
Central Commerce Transaction Engine
of the platform.

FINALIZED SALES PHILOSOPHY
All sales channels should use:
One Unified Commerce Engine

Supported Sales Channels
ONLINE
POS
WHOLESALE (future)
DIRECT_SALES (future)

IMPORTANT PRINCIPLE
All channels should share:
inventory,
customer database,
offers,
wallet,
referral logic,
reporting.

MAIN SUBMODULES

1. Unified Sales Engine
FINALIZED RULE
All sales transactions flow into:
One Central Sales System

Example
POS Sale
Online Order
Future Wholesale Order
All become:
commerce transactions
inside same sales engine.

Benefits
unified reporting,
customer history,
inventory consistency,
centralized analytics.

2. Sales Channels
Each sale tracks:
Sales Source

Recommended Channel Types
ONLINE
POS
WHOLESALE
MANUAL

Important Rule
Channel affects:
offers,
workflows,
invoice flow,
reporting.

3. Sales Order Management
Handles:
order creation,
order processing,
fulfillment tracking,
order completion.

FINALIZED ORDER FLOW
Order Created
      ↓
Inventory Reserved
      ↓
Payment Validated
      ↓
Processing
      ↓
Dispatch
      ↓
Delivery
      ↓
Completion

Important Rule
Every order event creates:
Audit Trail

4. Order Status Management
FINALIZED STATUS FLOW
PENDING
↓
CONFIRMED
↓
PROCESSING
↓
PACKED
↓
SHIPPED
↓
DELIVERED
↓
COMPLETED

Additional Statuses
CANCELLED
RETURNED
REFUNDED
FAILED

Important Rule
Statuses remain:
configurable & extendable.

5. Inventory Integration
FINALIZED RULE
Inventory integrates directly with:
sales workflows.

Inventory Logic
Online Orders
Reserve Inventory
↓
Confirm Order
↓
Deduct During Fulfillment

POS Billing
Instant Inventory Deduction

Important Rule
Negative stock:
strictly prohibited.

Billing Policy
Inventory may become:
ZERO
BUT:
never below zero.

Important Rule
Overselling should:
hard-block billing/order confirmation.

6. Branch-wise Sales Management
Each sale belongs to:
Branch + Warehouse

Example
Pune POS Sale
Mumbai Online Fulfillment

Important Rule
Sales analytics remain:
branch-aware.

7. Customer Sales History
Tracks:
online orders,
POS purchases,
returns,
wallet usage,
referrals.

Important Benefit
Creates:
Unified Customer Commerce Profile

Example
Customer:
- bought online
- visited POS
- used wallet
- referred customers

8. Sales Invoice Management
Supports:
GST invoices,
retail invoices,
tax summaries,
downloadable invoices.

Invoice Features
invoice numbering,
branch-wise invoice series,
digital invoice generation,
printable invoices.

Future Features
e-invoicing,
e-way bill integration.

9. Payment Management
Supports:
online payments,
COD,
POS payments,
split payments,
wallet redemption.

Payment Modes
CASH
UPI
CARD
BANK_TRANSFER
COD
WALLET
MIXED

FINALIZED PAYMENT PHILOSOPHY
Payment methods should be:
Branch-configurable

Payment Availability Depends On
Branch
Channel
Fulfillment Logic

Example
Pune Branch
CASH
UPI
CARD
WALLET

Small Branch
CASH
UPI

Online Fulfillment Branch
ONLINE_PAYMENT
COD
WALLET

Important Rule
POS should show:
only branch-enabled payment methods.

Online Checkout Logic
Customer Pincode
      ↓
Fulfillment Branch
      ↓
Load Allowed Payment Methods

Future Features
COD restrictions,
zone-wise payment rules,
prepaid-only zones.

Important Rule
All payments create:
Payment Ledger Entries

10. Returns & Refund Management
Supports:
online returns,
POS returns,
exchanges,
refunds.

Return Flow
Return Request
      ↓
Approval/Validation
      ↓
Inventory Restoration
      ↓
Refund/Exchange

Return Reasons
DAMAGED
WRONG_PRODUCT
CUSTOMER_RETURN
QUALITY_ISSUE

Important Rule
Returns restore:
correct branch inventory.

11. Exchange Management
Supports:
product replacement,
variant exchange,
amount adjustment.

Example
500ml Ghee
↓
Exchange
↓
1L Ghee

12. Wallet Integration
Supports:
wallet redemption,
cashback,
referral commissions,
future loyalty rewards.

Important Rule
Wallet maintains:
full transaction ledger.

13. Referral & Partner Integration
Integrated with:
Referral Engine

Finalized Logic
Successful Sale
      ↓
Referral Validation
      ↓
Wallet Commission Credit

Important Rule
Commission triggers only after:
successful order completion.

14. Delivery & Fulfillment Tracking
Supports:
order dispatch,
delivery tracking,
branch fulfillment visibility.

Important Rule
Fulfillment remains:
branch-aware.

Future Features
delivery partner integration,
live tracking,
route optimization.

15. Omnichannel Offers Engine
FINALIZED RULE
Offers can apply to:
Online,
POS,
Both.

Offer Channel Types
ONLINE
POS
BOTH

Offer Types
product offers,
cart discounts,
referral discounts,
branch offers,
festival offers.

16. Sales Notifications
Supports:
order confirmation,
payment confirmation,
dispatch updates,
delivery updates,
refund updates.

Future Channels
SMS
Email
WhatsApp
Push Notifications

17. Sales Analytics & Reports
Recommended Reports
sales summary,
channel-wise sales,
branch-wise sales,
product-wise sales,
payment-wise sales,
return analytics,
refund analytics,
wallet usage,
referral performance.

Important Analytics
Omnichannel Customer Analytics
Tracks:
online + POS behavior,
repeat purchases,
order frequency,
customer lifetime value.

18. Offline Sales Sync
Important for:
offline POS,
unstable internet branches.

FINALIZED RULE
Offline transactions:
queue locally and sync later.

Important Rule
Offline sync preserves:
inventory integrity,
branch mapping,
invoice consistency.

19. Security & Audit
Supports:
sales audit logs,
refund approvals,
invoice audit tracking,
order history logs.

Important Rule
All commerce actions create:
Audit Trail

20. Future Wholesale Support
Architecture remains ready for:
dealer sales,
distributor orders,
bulk pricing,
B2B workflows.

RECOMMENDED PERMISSIONS
SALES_VIEW
SALES_CREATE
SALES_RETURN
SALES_REFUND
SALES_EXPORT
ORDER_MANAGE
DELIVERY_MANAGE

RECOMMENDED DATABASE TABLES
sales_orders
sales_order_items
sales_payments
sales_returns
sales_return_items
sales_refunds
sales_exchanges
sales_invoices
sales_channels
sales_status_logs
delivery_tracking
customer_sales_history
branch_payment_methods
payment_channel_configurations

FINALIZED SALES RULES
Rule 1
All sales channels use one commerce engine.

Rule 2
Inventory integrates directly with sales workflows.

Rule 3
Negative stock strictly prohibited.

Rule 4
POS deducts stock instantly.

Rule 5
Online orders reserve inventory before fulfillment.

Rule 6
Sales remain branch-aware.

Rule 7
Returns restore correct branch inventory.

Rule 8
Referral commission triggers only after successful completion.

Rule 9
Offers can apply to:
ONLINE
POS
BOTH

Rule 10
Payment methods are branch-configurable.

Rule 11
POS shows only branch-enabled payment methods.

Rule 12
Online checkout loads payment methods based on fulfillment branch.

Rule 13
All commerce actions create audit trail.

FINAL OBJECTIVE OF MODULE 8
To create a:
Unified omnichannel sales & commerce transaction ecosystem
for the complete AsliChoice platform supporting:
Online Orders
Retail POS
Future Wholesale
Branch Fulfillment
Wallet Transactions
Referral Commerce
Returns & Refunds
Branch-configurable Payments
Omnichannel Analytics
Future Distribution Expansion

MODULE 9 — CRM & CUSTOMER MANAGEMENT
for AsliChoice

Purpose
CRM & Customer Management handles:
centralized customer database,
customer onboarding,
customer lifecycle,
address management,
referral relationships,
wallet history,
communication tracking,
customer segmentation,
and omnichannel customer analytics.
This module becomes the:
Central Customer Intelligence Engine
of the platform.

FINALIZED CRM PHILOSOPHY
One Unified Customer System
All channels should use:
One Central Customer Database

Supported Customer Sources
ONLINE
POS
REFERRAL
MANUAL
WHOLESALE (future)

IMPORTANT PRINCIPLE
Customer data should remain:
centralized and omnichannel.

MAIN SUBMODULES

1. Central Customer Database
FINALIZED RULE
Each customer should have:
One Unified Customer Profile

Example
Customer:
- ordered online
- visited POS
- earned wallet rewards
- referred customers
All linked to:
single CRM profile.

Customer Profile Fields
customer ID,
name,
mobile,
email,
DOB (optional),
gender (optional),
profile image (future),
registration source.

Important Rule
Mobile number should remain:
primary unique identifier.

2. Customer Registration & Onboarding
Supports:
online registration,
POS customer creation,
admin-created customers,
referral onboarding.

FINALIZED REGISTRATION LOGIC
Registration depends on:
Pincode Serviceability

Flow
Customer Registers
       ↓
Check Pincode
       ↓
Serviceable?
   ↓ YES             ↓ NO
Auto Approve      Admin Review Request

Important Rule
Non-serviceable customers:
remain stored in CRM.

Customer Statuses
PENDING_SERVICEABILITY
ACTIVE
BLOCKED
INACTIVE

3. Address Management
Supports:
multiple addresses,
delivery addresses,
address history.

Address Fields
name,
mobile,
address line,
landmark,
city,
state,
pincode.

Important Rule
Pincode determines:
serviceability,
fulfillment branch,
delivery rules.

Future Features
GPS coordinates,
map integration.

4. Customer Segmentation
Supports:
customer grouping,
marketing targeting,
analytics segmentation.

Suggested Segments
RETAIL
PREMIUM
PARTNER
WHOLESALE
FREQUENT_BUYER

Important Benefit
Enables:
targeted offers,
loyalty campaigns,
analytics.

5. Referral Relationship Management
Integrated with:
Referral Engine

FINALIZED RULE
When customer refers successfully:
Customer
   ↓
Automatically becomes:
PARTNER

Tracks
referred customers,
referral hierarchy (non-MLM),
referral earnings,
wallet commissions.

Important Rule
Referral rewards trigger only after:
successful order completion.

6. Wallet Management
Supports:
referral earnings,
cashback,
wallet redemption,
future loyalty rewards.

Important Rule
Wallet maintains:
Full Ledger System

Wallet Transaction Types
REFERRAL_CREDIT
CASHBACK
ORDER_REDEMPTION
MANUAL_ADJUSTMENT

Important Rule
Wallet balance should:
never be directly editable.
Use:
ledger entries only.

7. Customer Communication History
Tracks:
SMS,
Email,
WhatsApp (future),
support interactions.

Important Benefit
Provides:
customer communication timeline.

Future Features
automated reminders,
marketing campaigns,
customer follow-ups.

8. Customer Notes & Internal Remarks
Supports:
internal comments,
special handling notes,
delivery notes.

Example
Preferred evening delivery customer.

Important Rule
Internal notes remain:
admin-only.

9. Customer Purchase History
Tracks:
online orders,
POS purchases,
returns,
exchanges,
wallet usage.

Important Benefit
Creates:
360° Customer View

Example
Customer:
- spends ₹5000/month
- buys ghee frequently
- prefers online ordering

10. Customer Loyalty Readiness
Architecture should remain ready for:
loyalty points,
membership tiers,
rewards programs.

Future Loyalty Types
SILVER
GOLD
PLATINUM

Important Recommendation
Keep:
loyalty schema future-ready from Day 1.

11. Customer Support Integration (Future)
Supports:
complaint tracking,
issue resolution,
return assistance.

Future Features
ticket system,
support chat,
escalation workflows.

12. Customer Notifications
Supports:
registration confirmation,
order updates,
wallet updates,
referral rewards,
promotional campaigns.

Future Channels
SMS
Email
WhatsApp
Push Notifications

13. Customer Analytics
Recommended Analytics
customer acquisition,
repeat customer rate,
top customers,
referral performance,
customer lifetime value,
average order value,
customer retention.

Important Analytics
Omnichannel Behavior Analytics
Tracks:
online vs POS behavior,
preferred branch,
preferred products,
buying frequency.

14. Customer Search & Lookup
Supports:
mobile search,
email search,
name search,
referral lookup.

Important Recommendation
Search should remain:
extremely fast
for POS/customer service operations.

15. Customer Verification
Supports:
mobile OTP,
email OTP,
admin approval (special cases).

Important Rule
Verification method depends on:
system configuration.

16. Customer Privacy & Security
Supports:
audit logging,
access control,
customer data protection.

Important Rule
Sensitive customer data access should remain:
permission-controlled.

17. Customer Activity Timeline
Tracks:
registrations,
orders,
wallet activity,
referrals,
returns,
communications.

Important Benefit
Provides:
complete customer activity history.

18. Future Wholesale CRM Readiness
Architecture should support:
dealers,
distributors,
B2B accounts,
business pricing.

RECOMMENDED PERMISSIONS
CUSTOMER_VIEW
CUSTOMER_CREATE
CUSTOMER_EDIT
CUSTOMER_EXPORT
WALLET_ADJUST
CUSTOMER_COMMUNICATION

RECOMMENDED DATABASE TABLES
customers
customer_addresses
customer_segments
customer_wallets
wallet_ledger
customer_referrals
customer_notes
customer_communications
customer_status_logs
customer_activity_logs
customer_serviceability_requests

FINALIZED CRM RULES
Rule 1
All channels use one centralized customer database.

Rule 2
Mobile number remains primary customer identifier.

Rule 3
Customers can have multiple addresses.

Rule 4
Pincode determines serviceability and fulfillment logic.

Rule 5
Successful referral automatically converts customer into partner.

Rule 6
Referral commission triggers only after successful order completion.

Rule 7
Wallet remains ledger-driven.

Rule 8
Wallet balance should never be directly editable.

Rule 9
Non-serviceable customers remain stored in CRM.

Rule 10
Customer communication history remains trackable.

Rule 11
Sensitive customer data remains permission-controlled.

FINAL OBJECTIVE OF MODULE 9
To create a:
Unified omnichannel customer intelligence & relationship ecosystem
for the complete AsliChoice platform supporting:
Customer Lifecycle Management
Omnichannel Customer Profiles
Referral Commerce
Wallet Management
Customer Analytics
Serviceability Intelligence
Future Loyalty Programs
Future B2B Customer Expansion

MODULE 10 — REFERRAL, PARTNER & WALLET MANAGEMENT
for AsliChoice

Purpose
Referral, Partner & Wallet Management handles:
customer referrals,
automatic partner creation,
commission calculation,
wallet credits,
partner incentives,
referral tracking,
payout readiness,
and growth analytics.
This module becomes the:
Growth & Incentive Engine
of the platform.

FINALIZED REFERRAL PHILOSOPHY
Referral System is:
NON-MLM
Meaning:
no binary structure,
no levels,
no chain income,
no forced hierarchy.

FINALIZED PARTNER PHILOSOPHY
Any successful referring customer can become:
PARTNER
Automatically.

FINALIZED REFERRAL FLOW
Customer Refers User
        ↓
Referred User Registers
        ↓
Referred User Purchases
        ↓
Order Successfully Completed
        ↓
Commission Credited
        ↓
Referrer Becomes Partner

IMPORTANT PRINCIPLE
Commission triggers ONLY after:
successful order completion.

MAIN SUBMODULES

1. Referral Engine
Tracks:
referral source,
referred customers,
successful referrals,
commission eligibility.

Referral Sources
CUSTOMER
PARTNER
ADMIN
CAMPAIGN

Important Rule
Each customer should support:
unique referral code/link.

Referral Methods
Supports:
referral code,
referral link,
mobile referral,
manual tagging (admin).

Important Rule
Referral relationship should remain:
permanent and auditable.

2. Automatic Partner Conversion
FINALIZED RULE
Once referral succeeds:
customer automatically becomes partner.

Success Definition
Referred Customer
      ↓
Places Successful Completed Order

Important Rule
No manual partner activation required initially.

Suggested Partner Statuses
PENDING
ACTIVE
BLOCKED
INACTIVE

3. Partner Profile Management
Partner profile includes:
partner ID,
referral code,
referred customers,
wallet balance,
earnings history.

Important Rule
Partner remains:
linked to original customer profile.

4. Commission Engine
FINALIZED RULE
Commission should remain:
configurable
by admin.

Supported Commission Types
FIXED
PERCENTAGE

Commission Scope
Can apply to:
product,
category,
order value,
campaign.

Example
5% on Ghee Orders
₹100 fixed on first referral order

Important Rule
Commission calculation should remain:
rule-driven.

5. Commission Trigger Logic
FINALIZED RULE
Commission should trigger ONLY after:
successful order completion.

Example Flow
Order Delivered
      ↓
Return Window Passed (optional future)
      ↓
Commission Approved
      ↓
Wallet Credit

Important Benefit
Prevents:
fake referrals,
cancelled-order abuse,
payout fraud.

6. Wallet Management
FINALIZED RULE
All commissions first go to:
Wallet

Wallet Uses
Supports:
future payouts,
order redemption,
cashback,
referral earnings.

Wallet Transaction Types
REFERRAL_COMMISSION
CASHBACK
ORDER_REDEMPTION
MANUAL_ADJUSTMENT
PAYOUT_DEDUCTION

Important Rule
Wallet must remain:
Ledger Driven

Important Rule
Wallet balance should:
never be directly editable.

7. Wallet Ledger System
Tracks:
credits,
debits,
adjustments,
payout deductions.

Ledger Fields
transaction type,
reference ID,
amount,
before balance,
after balance,
timestamp,
remarks.

Important Rule
Every wallet change creates:
audit trail.

8. Wallet Redemption
Supports:
online wallet usage,
POS wallet usage,
partial redemption.

Example
Wallet Balance = ₹500
Order = ₹1200
Wallet Used = ₹300

Important Rule
Wallet usage rules remain:
configurable.

Possible Configurations
Minimum Order Required
Max Wallet Usage %

9. Future Payout System Readiness
FINALIZED DECISION
Initially:
commissions remain in wallet.

Future Support
Add:
bank payouts,
UPI payouts,
payout requests,
approval workflows.

Suggested Future Payout Statuses
PENDING
APPROVED
PAID
FAILED

Important Recommendation
Keep payout schema ready from Day 1.

10. Referral Analytics
Tracks:
top referrers,
referral conversions,
commission liabilities,
referral sales.

Recommended Analytics
referral performance,
conversion rate,
partner earnings,
referral ROI.

11. Campaign-based Referral Support
Future support for:
special campaigns,
festive referral bonuses,
category-based referral offers.

Example
Diwali Campaign
→ Double Referral Rewards

12. Referral Validation Rules
Supports:
duplicate prevention,
self-referral prevention,
fraud detection.

Important Rules
Same mobile number:
cannot self-refer.

Duplicate referral mapping:
not allowed.

13. Referral Relationship Visibility
Admin can view:
who referred whom,
referral performance,
wallet liabilities.

Important Rule
Structure remains:
simple non-MLM referral mapping.

Example
Customer A
   ↓
Customer B
NOT:
Multi-level chain income

14. Notifications
Supports:
referral success,
wallet credit,
payout updates (future),
campaign alerts.

Future Channels
SMS
Email
WhatsApp
Push Notifications

15. Security & Audit
Supports:
commission audit,
wallet audit,
payout audit,
fraud tracking.

Important Rule
All commission & wallet actions create:
audit trail.

16. Future Loyalty Integration
Architecture should remain compatible with:
loyalty points,
memberships,
rewards systems.

RECOMMENDED PERMISSIONS
REFERRAL_VIEW
REFERRAL_CONFIGURE
WALLET_VIEW
WALLET_ADJUST
PAYOUT_APPROVE
PARTNER_MANAGE

RECOMMENDED DATABASE TABLES
partners
partner_referrals
referral_rules
wallets
wallet_ledger
commission_transactions
partner_status_logs
referral_campaigns
future_payout_requests

FINALIZED REFERRAL & WALLET RULES
Rule 1
Referral system remains strictly non-MLM.

Rule 2
Successful referrer automatically becomes partner.

Rule 3
Commission triggers only after successful order completion.

Rule 4
All commissions first credit to wallet.

Rule 5
Wallet remains ledger-driven.

Rule 6
Wallet balance should never be directly editable.

Rule 7
Referral relationships remain permanent and auditable.

Rule 8
Duplicate/self referrals should be blocked.

Rule 9
Payout system remains future-ready.

Rule 10
All wallet & commission actions create audit trail.

FINAL OBJECTIVE OF MODULE 10
To create a:
Scalable non-MLM referral, partner & wallet incentive ecosystem
for the complete AsliChoice platform supporting:
Referral Commerce
Automatic Partner Creation
Wallet-based Incentives
Future Payouts
Referral Analytics
Incentive Tracking
Omnichannel Wallet Usage
Future Loyalty Expansion

MODULE 11 — NOTIFICATIONS & COMMUNICATION MANAGEMENT
for AsliChoice

Purpose
Notifications & Communication Management handles:
OTP delivery,
SMS notifications,
email notifications,
WhatsApp notifications,
push notifications,
transactional alerts,
campaign messaging,
communication templates,
and customer communication tracking.
This module becomes the:
Central Communication Engine
of the platform.

FINALIZED COMMUNICATION PHILOSOPHY
All communications should use:
One Centralized Notification Engine

Supported Channels
SMS
EMAIL
WHATSAPP
PUSH_NOTIFICATION
IN_APP

IMPORTANT PRINCIPLE
Communication should remain:
event-driven and template-based.

MAIN SUBMODULES

1. Central Notification Engine
FINALIZED RULE
All modules should trigger notifications through:
One Unified Communication System

Example Triggers
Order Placed
Payment Success
OTP Verification
Wallet Credit
Referral Success
Low Stock Alert

Important Benefit
Provides:
centralized control,
audit tracking,
template management,
retry handling.

2. OTP Management System
Supports:
mobile OTP,
email OTP,
login verification,
registration verification.

FINALIZED LOGIN RULE
OTP channel depends on:
system configuration.

Supported OTP Methods
MOBILE_OTP
EMAIL_OTP

Intelligent OTP Logic
If:
both mobile & email exist,
and admin configured email OTP,
then:
System automatically sends email OTP

Important Rule
OTP delivery method should remain:
configurable from super admin.

OTP Features
expiry time,
resend control,
retry limit,
rate limiting.

Important Rule
OTP logs should remain:
auditable.

3. SMS Notification System
Supports:
transactional SMS,
OTP SMS,
delivery updates,
order confirmations.

Example SMS Events
Order Confirmed
Order Delivered
Wallet Credited
OTP Sent

Future Features
promotional SMS,
campaign SMS.

Important Recommendation
Separate:
Transactional vs Promotional SMS

4. Email Notification System
Supports:
OTP emails,
invoices,
order notifications,
wallet statements,
reports.

Example Email Events
Invoice Email
Welcome Email
Password Reset
Order Confirmation

Future Features
newsletter campaigns,
automated email journeys.

5. WhatsApp Notification System (Future Ready)
Supports:
order updates,
OTP,
wallet updates,
delivery notifications.

Important Recommendation
Keep architecture ready for:
WhatsApp Business API

Example WhatsApp Events
Order Shipped
Order Delivered
Wallet Credited

6. Push Notification System (Future)
Supports:
mobile app alerts,
offer notifications,
reminders.

Example Push Events
New Offer
Cart Reminder
Referral Reward

7. In-App Notifications
Supports:
dashboard alerts,
admin notifications,
internal reminders.

Example In-App Alerts
Low Stock
Pending Approval
New Referral
New Order

Important Benefit
Reduces dependency on:
external communication channels.

8. Communication Templates
FINALIZED RULE
All communications should use:
Template System

Supported Template Types
SMS_TEMPLATE
EMAIL_TEMPLATE
WHATSAPP_TEMPLATE
PUSH_TEMPLATE

Template Features
dynamic variables,
multi-language readiness,
template versioning,
activation/deactivation.

Example Variables
{CUSTOMER_NAME}
{ORDER_ID}
{OTP}
{WALLET_AMOUNT}

Important Rule
Templates should remain:
editable from admin panel.

9. Event-driven Notification Triggers
Notifications should trigger from:
business events.

Example Triggers

Important Rule
Notification logic should remain:
decoupled from business logic.

10. Communication Logs
Tracks:
sent notifications,
delivery status,
failures,
retries.

Important Rule
Every communication should create:
communication log entry.

Suggested Log Fields
recipient,
channel,
template used,
status,
sent time,
delivery status.

11. Retry & Failure Handling
Supports:
retry failed messages,
queue processing,
provider failover (future).

Example
SMS Failed
↓
Retry Queue

Important Recommendation
Use:
Queue-based notification processing
for scalability.

12. Campaign Messaging (Future Ready)
Supports:
promotional campaigns,
festive campaigns,
referral campaigns.

Example Campaigns
Diwali Offers
Referral Bonus Campaign
New Product Launch

Important Rule
Promotional messaging should support:
opt-in/opt-out controls.

13. Customer Communication Preferences
Supports:
SMS enabled/disabled,
email enabled/disabled,
WhatsApp enabled/disabled.

Important Benefit
Supports:
customer communication consent management.

14. Internal Admin Notifications
Supports:
pending approvals,
stock alerts,
serviceability requests,
payout approvals,
failed sync alerts.

Example Admin Alerts
Low Stock Alert
Pending Refund Approval
Non-serviceable Registration Request

15. Notification Scheduling (Future)
Supports:
scheduled campaigns,
reminder notifications,
future automation.

Example
Send Festival Campaign Tomorrow 9AM

16. Multi-language Readiness
Architecture should remain ready for:
English,
Hindi,
Marathi,
regional languages.

Important Recommendation
Keep templates:
localization-ready.

17. Security & Compliance
Supports:
OTP security,
audit logging,
communication history,
consent tracking.

Important Rule
Sensitive communications should remain:
secure and auditable.

18. Notification Analytics
Tracks:
delivery rate,
open rate,
click rate (future),
campaign performance.

Important Analytics
OTP success rate,
SMS delivery success,
campaign conversion.

RECOMMENDED PERMISSIONS
NOTIFICATION_VIEW
NOTIFICATION_SEND
TEMPLATE_MANAGE
CAMPAIGN_MANAGE
OTP_CONFIGURATION
COMMUNICATION_REPORTS

RECOMMENDED DATABASE TABLES
notification_templates
notification_logs
otp_logs
communication_preferences
notification_queues
campaigns
campaign_recipients
admin_notifications

FINALIZED COMMUNICATION RULES
Rule 1
All communications use centralized notification engine.

Rule 2
OTP method depends on admin configuration.

Rule 3
Templates remain admin-configurable.

Rule 4
All notifications create communication logs.

Rule 5
Notification processing should remain queue-based.

Rule 6
Promotional communications should support opt-in/opt-out.

Rule 7
Notification triggers remain event-driven.

Rule 8
Sensitive communications remain secure & auditable.

Rule 9
System remains multi-language ready.

FINAL OBJECTIVE OF MODULE 11
To create a:
Centralized omnichannel communication & notification ecosystem
for the complete AsliChoice platform supporting:
OTP Verification
Transactional Notifications
Omnichannel Messaging
Communication Tracking
Campaign Messaging
Customer Communication Preferences
Future Marketing Automation
Multi-language Communication Expansion

MODULE 12 — FINANCE, ACCOUNTS & LEDGER MANAGEMENT
for AsliChoice

Purpose
Finance, Accounts & Ledger Management handles:
accounting structure,
customer/vendor ledgers,
branch accounting,
payment accounting,
expense tracking,
wallet accounting,
tax calculations,
profit analysis,
and future GST/accounting integrations.
This module becomes the:
Financial Control & Accounting Engine
of the platform.

FINALIZED FINANCE PHILOSOPHY
Finance should remain:
Ledger-driven & Transaction-linked
Meaning:
every financial transaction creates ledger impact,
accounting should follow actual business operations,
no manual financial inconsistencies.

IMPORTANT PRINCIPLE
Finance integrates directly with:
purchases,
inventory,
sales,
wallet,
payments,
returns,
referrals,
expenses.

MAIN SUBMODULES

1. Chart of Accounts (COA)
FINALIZED RULE
System should maintain:
Centralized Chart of Accounts

Recommended Account Types
ASSET
LIABILITY
INCOME
EXPENSE
EQUITY

Example Accounts
Cash Account
Bank Account
Sales Account
Purchase Account
Wallet Liability
Referral Expense
GST Payable

Important Recommendation
Keep COA:
configurable & expandable.

2. Ledger Management
FINALIZED RULE
Every financial transaction creates:
Ledger Entries

Ledger Entry Structure
debit account,
credit account,
amount,
branch,
transaction reference,
timestamp,
narration.

Important Rule
Ledger must remain:
immutable & auditable.

Example
POS Sale
Cash/UPI Account → Debit
Sales Account → Credit

3. Customer Ledger
Tracks:
purchases,
refunds,
wallet usage,
outstanding balances (future B2B).

Important Benefit
Creates:
customer financial history.

Future Features
credit customers,
customer outstanding tracking.

4. Vendor Ledger
Tracks:
purchases,
vendor payments,
outstanding dues,
purchase returns.

Example
Purchase Created
↓
Vendor Outstanding Increased

Payment Example
Vendor Payment
↓
Outstanding Reduced

Important Rule
Vendor ledger integrates directly with:
purchase module.

5. Branch-wise Accounting
FINALIZED RULE
Accounting should remain:
Branch-aware

Tracks
branch sales,
branch expenses,
branch profitability,
branch collections.

Important Benefit
Enables:
branch profitability analysis.

Example
Pune Branch Profit
Mumbai Branch Expenses

6. Payment Accounting
Supports:
cash,
UPI,
cards,
COD,
wallet payments.

FINALIZED RULE
Payment methods are:
branch-configurable

Important Rule
Every payment creates:
accounting ledger impact.

Example
Online Payment
Payment Gateway Account → Debit
Sales Account → Credit

7. Wallet Accounting
FINALIZED RULE
Wallet remains:
ledger-driven

Important Accounting Principle
Wallet balance is:
company liability
until redeemed/payout.

Example
Referral Credit
Referral Expense → Debit
Wallet Liability → Credit

Wallet Redemption Example
Wallet Liability → Debit
Sales Adjustment → Credit

Important Rule
Wallet balance should:
never be directly editable.

8. Expense Management
Supports:
branch expenses,
operational expenses,
logistics expenses,
miscellaneous expenses.

Suggested Expense Categories
RENT
SALARY
DELIVERY
MARKETING
UTILITY
MISCELLANEOUS

Expense Features
expense entry,
receipt upload,
approval workflow (future),
branch tagging.

Important Rule
Expenses remain:
branch-mapped.

9. Tax & GST Management
Supports:
GST calculations,
GST breakup,
tax reports,
invoice tax summaries.

Important Recommendation
Keep architecture ready for:
Indian GST compliance.

Future Features
e-invoicing,
GST return export,
HSN codes,
e-way bills.

10. Profitability Analysis
Supports:
branch profitability,
product profitability,
category profitability,
delivery profitability.

Important Benefit
Provides:
business intelligence.

Example Analytics
Top Profitable Product
Most Profitable Branch
High Expense Zone

11. Cash & Bank Management
Tracks:
cash balances,
bank balances,
deposits,
withdrawals,
transfers.

Important Rule
Cash flow should remain:
traceable & auditable.

Future Features
bank reconciliation,
auto statement import.

12. Refund & Return Accounting
Supports:
customer refunds,
sales returns,
wallet reversals.

Example
Sales Return
↓
Sales Reversal
↓
Inventory Restoration
↓
Refund Entry

Important Rule
Returns affect:
inventory,
sales,
accounting,
tax.

13. Referral & Commission Accounting
Supports:
commission liabilities,
wallet credits,
payout accounting (future).

Example
Referral Commission
↓
Expense Entry
↓
Wallet Liability

14. Financial Reports
Recommended Reports
Profit & Loss
Balance Sheet
Cash Flow
Trial Balance
Sales Register
Purchase Register
GST Reports
Expense Reports
Branch Profitability
Wallet Liability Report

Important Reports
Omnichannel Revenue Analytics
Tracks:
online revenue,
POS revenue,
future wholesale revenue.

15. Financial Audit & Logs
Supports:
accounting audit logs,
ledger tracking,
adjustment history.

Important Rule
Financial records should remain:
immutable & auditable.

16. Financial Adjustments
Supports:
correction entries,
journal entries,
reversals.

Important Rule
Adjustments require:
permissions,
remarks,
audit logs.

17. Future Accounting Integration
Architecture should support:
Tally integration,
Zoho Books integration,
ERP exports,
CA reporting.

Important Recommendation
Keep:
export-ready financial architecture.

18. Future Credit System Readiness
Supports future:
customer credit,
vendor credit,
dealer credit limits.

Important Recommendation
Keep:
receivable/payable schema future-ready.

RECOMMENDED PERMISSIONS
FINANCE_VIEW
LEDGER_VIEW
EXPENSE_MANAGE
PAYMENT_VIEW
PAYMENT_ADJUST
FINANCIAL_REPORTS
JOURNAL_ENTRY

RECOMMENDED DATABASE TABLES
chart_of_accounts
ledger_entries
customer_ledgers
vendor_ledgers
wallet_ledgers
branch_accounts
expenses
expense_categories
tax_configurations
financial_adjustments
bank_accounts
cash_accounts
financial_reports

FINALIZED FINANCE RULES
Rule 1
All financial transactions create ledger entries.

Rule 2
Finance remains branch-aware.

Rule 3
Wallet remains ledger-driven.

Rule 4
Wallet balance is company liability until redeemed.

Rule 5
Payment methods remain branch-configurable.

Rule 6
Financial records remain immutable & auditable.

Rule 7
Returns affect:
inventory,
sales,
accounting,
tax.

Rule 8
Expenses remain branch-mapped.

Rule 9
Financial adjustments require audit tracking.

Rule 10
Architecture remains GST & accounting integration ready.

FINAL OBJECTIVE OF MODULE 12
To create a:
Ledger-driven omnichannel financial control & accounting ecosystem
for the complete AsliChoice platform supporting:
Branch Accounting
Omnichannel Revenue Tracking
Vendor & Customer Ledgers
Wallet Accounting
Referral Accounting
Expense Management
GST-ready Accounting
Financial Analytics
Future Accounting Integrations

MODULE 13 — REPORTS, ANALYTICS & BUSINESS INTELLIGENCE
for AsliChoice

Purpose
Reports, Analytics & Business Intelligence handles:
operational reports,
sales analytics,
inventory analytics,
customer analytics,
financial analytics,
referral analytics,
KPI dashboards,
and strategic business insights.
This module becomes the:
Business Intelligence & Decision Engine
of the platform.

FINALIZED ANALYTICS PHILOSOPHY
Reports should be:
Real-time + Actionable + Branch-aware

IMPORTANT PRINCIPLE
Analytics should integrate across:
sales,
inventory,
finance,
CRM,
referrals,
fulfillment,
procurement,
and operations.

MAIN SUBMODULES

1. Central Dashboard System
FINALIZED RULE
Each user role should have:
Role-based Dashboards

Example Dashboards

Dashboard Features
KPI cards,
charts,
quick summaries,
alerts,
pending actions.

Recommended KPIs
Today's Sales
Orders Pending
Low Stock
Wallet Liability
Branch Revenue

2. Sales Analytics
Tracks:
online sales,
POS sales,
branch sales,
payment-wise sales,
product-wise sales.

Recommended Reports
Daily Sales
Monthly Sales
Channel-wise Sales
Branch-wise Sales
Top Selling Products

Important Analytics
Omnichannel Revenue Analysis
Tracks:
online vs POS revenue,
branch contribution,
category performance.

3. Inventory Analytics
Tracks:
stock levels,
stock movement,
dead stock,
fast-moving items,
low stock alerts.

Recommended Reports
Current Stock Report
Stock Aging
Low Stock Report
Inventory Valuation
Branch Inventory Summary

Important Benefit
Supports:
smarter procurement planning.

4. Purchase Analytics
Tracks:
vendor performance,
purchase trends,
procurement costs,
purchase returns.

Recommended Reports
Vendor-wise Purchases
Purchase Trends
Vendor Outstanding
Purchase Return Report

Important Analytics
Procurement Efficiency Analysis
Tracks:
vendor reliability,
purchase frequency,
pricing trends.

5. Financial Analytics
Tracks:
revenue,
expenses,
profitability,
wallet liabilities,
branch profitability.

Recommended Reports
Profit & Loss
Expense Report
Cash Flow
Branch Profitability
Wallet Liability Report

Important Benefit
Provides:
business financial visibility.

6. CRM & Customer Analytics
Tracks:
customer acquisition,
repeat customers,
customer lifetime value,
customer retention.

Recommended Reports
Top Customers
Repeat Purchase Report
Customer Retention
Average Order Value

Important Analytics
Omnichannel Customer Behavior
Tracks:
online vs POS buying,
preferred branches,
preferred products,
order frequency.

7. Referral & Partner Analytics
Tracks:
referral performance,
top partners,
conversion rates,
wallet commissions.

Recommended Reports
Top Referrers
Referral Conversion
Commission Summary
Partner Earnings

Important Rule
Referral analytics remain:
non-MLM structured.

8. Delivery & Fulfillment Analytics
Tracks:
pincode-wise orders,
delivery profitability,
fulfillment efficiency,
branch fulfillment load.

Recommended Reports
Delivery Zone Report
Pincode-wise Sales
Delivery Cost Analysis
Branch Fulfillment Report

Important Benefit
Supports:
logistics optimization.

9. Wallet & Incentive Analytics
Tracks:
wallet credits,
wallet redemption,
pending liabilities,
payout readiness.

Recommended Reports
Wallet Balance Summary
Commission Liability
Wallet Usage Analytics

Important Rule
Wallet remains:
ledger-driven.

10. Operational Alerts & Insights
Supports:
low stock alerts,
pending approvals,
failed sync alerts,
unusual activity detection.

Example Alerts
Low Inventory
High Return Rate
Failed Payment Spike

Important Recommendation
Dashboards should provide:
actionable insights
NOT only raw reports.

11. Branch-wise Analytics
FINALIZED RULE
All major analytics should remain:
branch-aware

Tracks
branch sales,
branch inventory,
branch profitability,
branch expenses.

Important Benefit
Supports:
multi-branch operational control.

12. Export & Download System
Supports:
Excel export,
PDF export,
CSV export.

Important Recommendation
Reports should support:
filters + exports.

Suggested Filters
date range,
branch,
category,
customer,
payment mode,
sales channel.

13. Scheduled Reports (Future)
Supports:
daily summaries,
weekly reports,
monthly reports,
email delivery.

Example
Daily Sales Report
→ Email to Admin Every Morning

14. Predictive Analytics Readiness (Future)
Architecture should remain ready for:
demand forecasting,
stock prediction,
sales prediction,
customer behavior prediction.

Future AI Features
Demand Forecasting
Smart Reordering
Customer Recommendations

15. KPI Tracking System
Supports:
operational KPIs,
financial KPIs,
sales KPIs,
branch KPIs.

Example KPIs
Revenue Growth
Inventory Turnover
Average Order Value
Customer Retention

16. Audit & Data Integrity Reporting
Tracks:
stock mismatches,
failed syncs,
unusual refunds,
manual adjustments.

Important Rule
Critical analytics should remain:
audit-aware.

17. Real-time Analytics Readiness
Important for:
live dashboards,
POS monitoring,
operational visibility.

Important Recommendation
Use:
optimized reporting architecture
for scalability.

18. Mobile Dashboard Readiness
Dashboards should remain:
mobile-friendly
for management usage.

19. Multi-channel Analytics
Tracks:
Online,
POS,
future wholesale,
future distributor sales.

Important Rule
All analytics should support:
omnichannel visibility.

RECOMMENDED PERMISSIONS
REPORTS_VIEW
ANALYTICS_VIEW
FINANCIAL_REPORTS
EXPORT_REPORTS
DASHBOARD_MANAGE
KPI_VIEW

RECOMMENDED DATABASE TABLES
dashboard_configurations
analytics_snapshots
scheduled_reports
report_exports
kpi_definitions
branch_kpis
analytics_alerts

FINALIZED ANALYTICS RULES
Rule 1
All analytics remain branch-aware.

Rule 2
Reports should remain role-based.

Rule 3
Analytics integrate across all business modules.

Rule 4
Dashboards should provide actionable insights.

Rule 5
Wallet analytics remain ledger-driven.

Rule 6
Referral analytics remain non-MLM.

Rule 7
Reports support filtering & export.

Rule 8
Architecture remains predictive-analytics ready.

Rule 9
Critical reports remain audit-aware.

FINAL OBJECTIVE OF MODULE 13
To create a:
Real-time omnichannel business intelligence & analytics ecosystem
for the complete AsliChoice platform supporting:
Operational Reporting
Omnichannel Analytics
Branch Profitability
Customer Intelligence
Inventory Intelligence
Referral Analytics
Financial Visibility
KPI Tracking
Future Predictive Analytics

MODULE 14 — DELIVERY, LOGISTICS & FULFILLMENT MANAGEMENT
for AsliChoice

Purpose
Delivery, Logistics & Fulfillment Management handles:
order fulfillment,
packing workflows,
dispatch management,
delivery routing,
pincode-based logistics,
delivery tracking,
branch dispatch operations,
logistics costing,
and future hyperlocal delivery integrations.
This module becomes the:
Fulfillment & Logistics Control Engine
of the platform.

FINALIZED FULFILLMENT PHILOSOPHY
Fulfillment should remain:
Branch-aware + Pincode-aware

IMPORTANT PRINCIPLE
Fulfillment logic depends on:
customer pincode,
branch inventory,
delivery zones,
serviceability,
logistics configuration.

MAIN SUBMODULES

1. Fulfillment Engine
FINALIZED RULE
Every online order should go through:
Fulfillment Workflow

FINALIZED FLOW
Order Created
      ↓
Fulfillment Branch Selection
      ↓
Inventory Reservation
      ↓
Picking
      ↓
Packing
      ↓
Dispatch
      ↓
Delivery

Important Rule
Fulfillment remains:
branch-scoped.

2. Intelligent Fulfillment Branch Selection
FINALIZED RULE
System selects fulfillment branch based on:
pincode,
inventory availability,
delivery configuration.

Selection Priority
Nearest Branch
↓
Mapped Fulfillment Branch
↓
Warehouse
↓
HO

Important Rule
Only:
fulfillment-enabled branches
can process online orders.

Branch Setting
Online Fulfillment Enabled = YES/NO

3. Pincode-based Delivery Routing
FINALIZED RULE
Delivery logic remains:
Pincode-aware

Supported Zone Types
STANDARD
EXTENDED
PREMIUM_SPECIAL
NON_SERVICEABLE

Important Rule
Pincode controls:
fulfillment branch,
delivery fee,
MOV,
delivery ETA,
payment methods.

4. Picking Workflow
Supports:
picklist generation,
inventory validation,
picking status tracking.

Picking Flow
Order Confirmed
      ↓
Generate Picklist
      ↓
Items Picked
      ↓
Packing Queue

Important Rule
Picking validates:
branch inventory availability.

5. Packing Workflow
Supports:
packing verification,
packaging status,
package weight (future),
packaging notes.

Packing Statuses
PENDING
PACKING
PACKED
FAILED

Important Rule
Packing completion required before:
dispatch.

6. Dispatch Management
Supports:
dispatch creation,
dispatch assignment,
delivery scheduling.

Dispatch Flow
Packed Order
      ↓
Assign Delivery
      ↓
Dispatch
      ↓
Out For Delivery

Important Rule
Dispatch remains:
branch-linked.

7. Delivery Status Tracking
FINALIZED DELIVERY FLOW
PENDING
↓
PACKED
↓
DISPATCHED
↓
OUT_FOR_DELIVERY
↓
DELIVERED

Additional Statuses
FAILED
RETURNED
CANCELLED

Important Rule
All delivery events create:
audit trail.

8. Delivery Charges Management
FINALIZED RULE
Delivery charges remain:
Pincode-based

Charges Can Depend On
zone type,
branch,
order value,
delivery type.

Example
Standard Zone
₹40 Delivery
Free Above ₹999

Extended Zone
₹120 Delivery
Higher MOV

9. Delivery Partner Management (Future Ready)
Supports future integration with:
Dunzo,
Porter,
Shiprocket,
local delivery partners.

Important Recommendation
Keep:
logistics integration-ready architecture.

Future Features
API integration,
automatic shipping assignment,
live tracking.

10. Hyperlocal Delivery Readiness
Architecture supports:
same-day delivery,
local branch dispatch,
hyperlocal routing.

Future Delivery Types
STANDARD
SAME_DAY
EXPRESS
STORE_PICKUP

11. Delivery Personnel Management (Future)
Supports:
delivery assignment,
delivery tracking,
delivery performance.

Future Features
delivery agent app,
OTP delivery confirmation,
GPS tracking.

12. Store Pickup / Click & Collect
Future support for:
Store Pickup

Example Flow
Order Placed
↓
Branch Prepares Order
↓
Customer Picks Up

Important Benefit
Reduces:
delivery costs,
logistics dependency.

13. Failed Delivery Handling
Supports:
failed delivery reasons,
rescheduling,
customer contact attempts.

Suggested Reasons
CUSTOMER_UNAVAILABLE
WRONG_ADDRESS
PAYMENT_ISSUE

Important Rule
Failed deliveries should remain:
trackable & auditable.

14. Return-to-Origin (RTO) Readiness
Future support for:
undelivered returns,
reverse logistics.

Example
Delivery Failed
↓
Return To Branch
↓
Inventory Reconciliation

15. Logistics Cost Tracking
Tracks:
delivery costs,
branch dispatch cost,
logistics profitability.

Important Analytics
Cost Per Delivery
Pincode Profitability
Branch Logistics Expense

16. Fulfillment Notifications
Supports:
packing updates,
dispatch alerts,
delivery notifications.

Example Notifications
Order Packed
Out for Delivery
Delivered Successfully

17. Fulfillment Analytics
Tracks:
fulfillment speed,
packing efficiency,
branch dispatch load,
delivery success rate.

Recommended Reports
Delivery Performance
Branch Fulfillment Load
Delivery Success Rate
Average Delivery Time

18. Offline Fulfillment Readiness
Supports:
temporary internet failure,
sync queue operations.

Important Rule
Fulfillment integrity must remain:
inventory-safe.

19. Security & Audit
Supports:
fulfillment audit logs,
dispatch tracking,
delivery audit history.

Important Rule
All logistics events create:
audit trail.

RECOMMENDED PERMISSIONS
FULFILLMENT_VIEW
FULFILLMENT_PROCESS
DISPATCH_MANAGE
DELIVERY_TRACK
PICKLIST_MANAGE
DELIVERY_REPORTS

RECOMMENDED DATABASE TABLES
fulfillment_orders
picklists
packing_logs
dispatches
delivery_tracking
delivery_zones
delivery_charges
delivery_failures
delivery_agents
logistics_costs

FINALIZED FULFILLMENT RULES
Rule 1
Fulfillment remains branch-aware.

Rule 2
Delivery logic remains pincode-aware.

Rule 3
Only fulfillment-enabled branches process online orders.

Rule 4
Inventory must reserve before fulfillment.

Rule 5
Packing completion required before dispatch.

Rule 6
Delivery charges remain pincode-based.

Rule 7
MOV validation remains delivery-zone aware.

Rule 8
All fulfillment & delivery actions create audit trail.

Rule 9
Architecture remains hyperlocal delivery ready.

Rule 10
Future logistics integrations remain supported.

FINAL OBJECTIVE OF MODULE 14
To create a:
Branch-aware omnichannel fulfillment & logistics ecosystem
for the complete AsliChoice platform supporting:
Pincode-based Fulfillment
Hyperlocal Delivery
Branch Dispatch Operations
Delivery Tracking
Logistics Analytics
Same-day Delivery Readiness
Future Delivery Partner Integrations
Omnichannel Order Fulfillment

MODULE 15 — RETURNS, DAMAGES & QUALITY CONTROL MANAGEMENT
for AsliChoice

Purpose
Returns, Damages & Quality Control Management handles:
sales returns,
purchase returns,
damaged stock,
expiry tracking,
quality inspection,
inventory quarantine,
reverse logistics,
replacement workflows,
and inventory recovery controls.
This module becomes the:
Inventory Recovery & Quality Assurance Engine
of the platform.

FINALIZED QUALITY PHILOSOPHY
Returned or damaged inventory should NEVER:
directly merge into sellable stock
without validation.

IMPORTANT PRINCIPLE
Every return/damage workflow should support:
inventory traceability,
branch tracking,
audit history,
quality inspection.

MAIN SUBMODULES

1. Sales Return Management
Supports:
online returns,
POS returns,
partial returns,
full returns.

FINALIZED RETURN FLOW
Customer Return Request
        ↓
Validation
        ↓
Return Approval
        ↓
Stock Inspection
        ↓
Inventory Decision
        ↓
Refund/Replacement

Important Rule
Returns should remain:
branch-aware.

Supported Return Types
REFUND
REPLACEMENT
EXCHANGE

Important Rule
Returns affect:
inventory,
sales,
finance,
wallet,
analytics.

2. Purchase Return Management
Supports:
vendor returns,
damaged purchase returns,
rejected stock return.

Example Flow
Purchase Received
↓
QC Failed
↓
Vendor Return

Important Rule
Purchase returns should link to:
original purchase transaction.

3. Damaged Stock Management
Tracks:
damaged inventory,
broken products,
leakage,
unusable stock.

Important Rule
Damaged stock should move to:
Separate Damage Inventory

Damage Sources
PURCHASE_DAMAGE
WAREHOUSE_DAMAGE
DELIVERY_DAMAGE
CUSTOMER_RETURN_DAMAGE

Important Rule
Damaged stock should NEVER:
appear in sellable inventory.

4. Expiry Management
Important for:
food products,
oils,
FMCG inventory.

FINALIZED RULE
System should support:
batch & expiry tracking
where applicable.

Tracks
batch number,
manufacturing date,
expiry date.

Important Alerts
Near Expiry Alert
Expired Stock Alert

Important Rule
Expired stock should:
auto-block selling.

5. Quality Control (QC) Workflow
Supports:
incoming QC,
return QC,
random inspections.

QC Statuses
PENDING_QC
PASSED
FAILED
QUARANTINED

Example Flow
Returned Product
↓
QC Inspection
↓
Decision

QC Outcomes
RESTOCK
DAMAGE
RETURN_TO_VENDOR
DISPOSE

Important Rule
Only:
QC-approved inventory
returns to sellable stock.

6. Inventory Quarantine
Supports:
suspected damaged stock,
QC pending stock,
expired products.

Important Rule
Quarantined inventory should:
remain isolated from sellable inventory.

Quarantine Reasons
QC_PENDING
DAMAGED
EXPIRED
SUSPECTED_DEFECT

7. Reverse Logistics Management
Supports:
customer pickup returns,
branch return handling,
vendor returns.

Example
Customer Return
↓
Branch Receives
↓
QC
↓
Restock/Damage

Future Features
delivery partner reverse pickup,
RTO logistics.

8. Replacement Workflow
Supports:
product replacement,
variant replacement,
replacement approval.

Example
Damaged Ghee Jar
↓
Replacement Approved
↓
New Dispatch

Important Rule
Replacement should create:
linked transaction history.

9. Inventory Adjustment Controls
Supports:
stock correction,
damage adjustment,
expiry adjustment.

Important Rule
Inventory adjustments require:
permissions,
remarks,
audit trail.

Important Rule
Negative stock remains:
strictly prohibited.

10. Refund Integration
Integrated with:
finance,
wallet,
payment system.

Refund Methods
ORIGINAL_PAYMENT
WALLET
STORE_CREDIT

Important Rule
Refunds should remain:
traceable & auditable.

11. Branch-wise Return Handling
FINALIZED RULE
Returns remain:
branch-aware

Example
Pune Sale
→ Pune Return

Important Rule
Inventory restoration should affect:
correct branch inventory.

12. Damage & Loss Analytics
Tracks:
damage percentage,
return trends,
expiry losses,
branch damage rates.

Recommended Reports
Damage Report
Expiry Loss Report
Return Trend Report
QC Failure Report

Important Benefit
Supports:
operational improvement.

13. Expiry & Batch Analytics
Tracks:
near-expiry inventory,
batch performance,
expiry losses.

Important Recommendation
Expiry management should remain:
batch-aware.

14. QC Audit & Traceability
Supports:
QC logs,
inspection history,
operator tracking.

Important Rule
Every QC action creates:
audit trail.

15. Disposal Management
Supports:
expired stock disposal,
damaged stock disposal,
inventory write-offs.

Important Rule
Disposed inventory should:
remain financially traceable.

Disposal Reasons
EXPIRED
DAMAGED
LEAKAGE
UNSELLABLE

16. Future Recall Management Readiness
Architecture should support:
product recalls,
batch recalls,
safety recalls.

Example
Batch Recall
↓
Block Sales
↓
Notify Customers

17. Notifications & Alerts
Supports:
expiry alerts,
QC pending alerts,
return approval alerts,
damage alerts.

Example Alerts
Batch Expiring in 7 Days
High Return Rate Alert

18. Security & Audit
Supports:
inventory audit logs,
QC audit history,
adjustment tracking.

Important Rule
All return & damage actions create:
audit trail.

RECOMMENDED PERMISSIONS
RETURN_APPROVE
QC_MANAGE
DAMAGE_MANAGE
EXPIRY_MANAGE
INVENTORY_ADJUST
DISPOSAL_APPROVE

RECOMMENDED DATABASE TABLES
sales_returns
purchase_returns
damage_inventory
inventory_quarantine
batch_tracking
expiry_tracking
qc_inspections
replacement_orders
inventory_adjustments
disposal_logs

FINALIZED RETURNS & QC RULES
Rule 1
Returned inventory should never directly enter sellable stock.

Rule 2
QC-approved inventory only returns to sellable stock.

Rule 3
Damaged inventory remains isolated.

Rule 4
Expired stock automatically becomes non-sellable.

Rule 5
Returns remain branch-aware.

Rule 6
Inventory adjustments require audit tracking.

Rule 7
Negative stock remains strictly prohibited.

Rule 8
Refunds remain financially traceable.

Rule 9
Quarantined inventory remains isolated from active inventory.

Rule 10
Architecture remains recall-management ready.

FINAL OBJECTIVE OF MODULE 15
To create a:
Branch-aware inventory recovery, returns & quality assurance ecosystem
for the complete AsliChoice platform supporting:
Sales Returns
Purchase Returns
Damage Tracking
Batch & Expiry Management
QC Workflows
Reverse Logistics
Inventory Recovery
Financially Traceable Adjustments
Future Product Recall Operations

MODULE 16 — HR, STAFF, ATTENDANCE & PAYROLL MANAGEMENT
for AsliChoice

Purpose
HR, Staff, Attendance & Payroll Management handles:
employee management,
branch staff allocation,
attendance tracking,
biometric/application attendance,
shift management,
leave management,
payroll processing,
payslip generation,
salary accounting,
and workforce analytics.
This module becomes the:
Workforce, Attendance & Payroll Control Engine
of the platform.

FINALIZED HR PHILOSOPHY
Workforce operations should remain:
Role-based + Branch-aware + Attendance-linked + Permission-controlled

IMPORTANT PRINCIPLE
HR integrates directly with:
user roles,
attendance,
payroll,
finance,
POS shifts,
branch operations,
audit systems.

MAIN SUBMODULES

1. Employee Management
FINALIZED RULE
Every staff member should have:
Centralized Employee Profile

Employee Profile Includes
employee ID,
full name,
mobile,
email,
branch assignment,
designation,
department,
reporting manager,
joining date,
employee status.

Suggested Employee Statuses
ACTIVE
INACTIVE
ON_LEAVE
TERMINATED

Important Rule
Employee profile remains:
linked with user account.

2. Branch-wise Staff Allocation
FINALIZED RULE
Employees remain:
branch-mapped

Example
Pune Cashier
Mumbai Warehouse Staff

Important Benefit
Supports:
branch accountability,
staffing analytics,
operational visibility.

3. Attendance Management
Supports:
daily attendance,
punch-in/punch-out,
shift attendance,
biometric attendance,
application attendance,
GPS attendance (future),
manual corrections.

FINALIZED ATTENDANCE METHODS
APPLICATION_PUNCH
BIOMETRIC
GPS_MOBILE
MANUAL_ADMIN
HYBRID

FINALIZED LOGIN FLOW
Employee Login
      ↓
Attendance Exists?
   ↓ YES            ↓ NO
Continue        Show Punch-In Prompt

Important Rule
If employee has not punched in:
system prompts attendance punch immediately.

Recommended Attendance Popup
You have not marked attendance today.

[ Punch In Now ]
[ Remind Later ]

Important Rule
Attendance methods remain:
configurable from super admin panel.

Branch-wise Attendance Support
Different branches can use:
biometric,
application punch,
hybrid attendance.

Example
Pune → Biometric
Warehouse → Application Punch
Delivery Staff → GPS Punch

Important Rule
Biometric architecture remains:
vendor-independent.

Supported Future Vendors
ZKTeco
eSSL
API-based biometric systems

4. Shift Management
Supports:
shift allocation,
shift timing,
cashier shifts,
branch shifts.

Suggested Shift Types
MORNING
EVENING
FULL_DAY
CUSTOM

POS Shift Integration
Punch In
↓
Cashier Shift Open
↓
Billing Enabled

Important Rule
POS operations can optionally require:
attendance punch-in first.

5. Leave Management
Supports:
leave requests,
approvals,
leave balance tracking.

Suggested Leave Types
CASUAL
SICK
PAID
UNPAID

Leave Workflow
Employee Requests Leave
       ↓
Manager Approval
       ↓
Leave Applied

Important Rule
Leave approvals remain:
permission-controlled.

6. Department & Role Mapping
Integrated with:
User & Role Management

Suggested Departments
SALES
PURCHASE
WAREHOUSE
FINANCE
OPERATIONS
ADMIN

Important Rule
Permissions depend on:
role,
branch,
department.

7. Employee Activity Tracking
Tracks:
login history,
approvals,
inventory actions,
billing activities,
payroll actions.

Important Rule
Critical actions create:
audit trail.

8. Payroll Management
FINALIZED DECISION
Payroll included in:
Phase 1 itself.

Payroll Supports
salary structures,
attendance-linked salary,
incentives,
deductions,
payroll processing,
payroll approvals,
payslip generation.

Suggested Salary Components
BASIC
HRA
ALLOWANCE
INCENTIVE
BONUS
DEDUCTION

Important Rule
Salary structures remain:
employee-specific.

9. Attendance-linked Payroll
FINALIZED RULE
Payroll integrates directly with:
attendance,
leave,
shifts.

Example
30 Days
2 Unpaid Leaves
↓
Salary Deduction Applied

Important Rule
Attendance remains:
payroll-integrated.

10. Payroll Processing Workflow
Attendance Finalized
      ↓
Payroll Generated
      ↓
Review
      ↓
Approval
      ↓
Payslip Generated

Suggested Payroll Statuses
DRAFT
PROCESSING
APPROVED
PAID

11. Payslip Generation
FINALIZED RULE
System should generate:
downloadable payslips.

Payslip Includes
employee details,
attendance summary,
salary breakup,
incentives,
deductions,
net payable.

Supported Formats
PDF
Print
Email

Important Rule
Payslips remain:
employee-accessible.

12. Incentive & Bonus Management
Supports:
sales incentives,
performance bonus,
attendance bonus,
future referral incentives.

Example
Branch Target Achieved
↓
Bonus Added

13. Salary Deductions
Supports:
unpaid leave deduction,
advance recovery,
penalties.

Suggested Deduction Types
UNPAID_LEAVE
ADVANCE
PENALTY
OTHER

Important Rule
All deductions require:
remarks,
audit tracking.

14. Payroll Accounting Integration
Integrated with:
Finance & Ledger Module

Example Ledger Entry
Salary Expense → Debit
Salary Payable → Credit

Salary Payment Example
Salary Payable → Debit
Bank Account → Credit

Important Rule
Payroll creates:
automatic accounting entries.

15. Employee Payroll Dashboard
Employee can view:
attendance,
salary history,
payslips,
deductions.

Future Features
reimbursement claims,
tax declarations.

16. HR Reports & Analytics
Recommended Reports
Attendance Report
Payroll Summary
Leave Report
Branch Staff Report
Shift Performance

Important Analytics
Tracks:
attendance trends,
overtime,
workforce productivity,
payroll expenses.

17. Security & Audit
Supports:
attendance audit,
payroll audit,
salary revision logs,
approval tracking.

Important Rule
Salary & HR data remain:
highly permission-controlled.

18. Future Readiness
Architecture remains ready for:
PF,
ESIC,
TDS,
GPS attendance,
field staff operations,
payroll compliance.

RECOMMENDED PERMISSIONS
EMPLOYEE_VIEW
EMPLOYEE_MANAGE
ATTENDANCE_MANAGE
SHIFT_MANAGE
LEAVE_APPROVE
PAYROLL_VIEW
PAYROLL_PROCESS
PAYROLL_APPROVE
PAYSLIP_GENERATE
HR_REPORTS

RECOMMENDED DATABASE TABLES
employees
employee_branches
attendance_logs
attendance_configurations
attendance_devices
biometric_sync_logs
shift_assignments
leave_requests
salary_structures
payroll_cycles
employee_payroll
payroll_items
payslips
employee_activity_logs

FINALIZED HR RULES
Rule 1
Employees remain branch-aware.

Rule 2
Attendance methods remain configurable from super admin panel.

Rule 3
Attendance supports:
APPLICATION
BIOMETRIC
GPS
MANUAL
HYBRID

Rule 4
First login of the day validates attendance punch status.

Rule 5
Biometric integrations remain vendor-independent.

Rule 6
POS operations can optionally require attendance punch-in.

Rule 7
Payroll included in Phase 1 itself.

Rule 8
Payroll remains attendance-linked.

Rule 9
Payroll remains branch-aware.

Rule 10
Payslips should be system-generated.

Rule 11
Payroll integrates automatically with finance ledger.

Rule 12
Critical HR & payroll actions create audit trail.

FINAL OBJECTIVE OF MODULE 16
To create a:
Branch-aware workforce, attendance & payroll ecosystem
for the complete AsliChoice platform supporting:
Employee Management
Biometric/Application Attendance
Shift Management
Leave Management
Payroll Processing
Payslip Generation
Attendance-linked Salary
Payroll Accounting
Workforce Analytics
Future Compliance Expansion

MODULE 17 — DOCUMENT, MEDIA & FILE MANAGEMENT
for AsliChoice

Purpose
Document, Media & File Management handles:
product images,
invoices,
employee documents,
vendor/customer attachments,
report exports,
media storage,
and centralized file management.
This module becomes the:
Central Digital Asset & Document Management Engine
of the platform.

FINALIZED DOCUMENT MANAGEMENT PHILOSOPHY
All files should remain:
Centralized + Secure + Linked + Auditable

IMPORTANT PRINCIPLE
Files should always be linked to:
modules,
records,
entities,
transactions.

MAIN SUBMODULES

1. Central File Storage Engine
FINALIZED RULE
All uploaded files should use:
Centralized File Management System

Supported File Types
IMAGE
PDF
EXCEL
CSV
DOCUMENT
ZIP

Important Rule
Files should NEVER remain:
unlinked/orphaned.

File Linking Examples
Product → Product Images
Invoice → PDF Invoice
Employee → Documents
Vendor → Agreements

2. Product Media Management
Supports:
product images,
gallery images,
thumbnails,
future videos.

Important Features
multiple product images,
variant-wise images,
image sorting,
default image selection.

Recommended Image Types
THUMBNAIL
GALLERY
BANNER
VARIANT_IMAGE

Important Rule
Product media should remain:
optimized for web & mobile.

3. Invoice & Document Storage
Supports:
sales invoices,
purchase invoices,
return documents,
payslips,
reports.

Important Rule
Generated documents should remain:
permanently linked to transactions.

Example
Sales Order
↓
Invoice PDF
↓
Stored & Downloadable

4. Employee Document Management
Supports:
ID proofs,
agreements,
joining documents,
certifications.

Important Rule
Employee documents remain:
access-controlled.

Future Features
document expiry reminders,
renewal alerts.

5. Vendor & Customer Attachments
Supports:
agreements,
GST documents,
KYC documents,
contracts,
supporting files.

Important Rule
Attachments remain:
entity-linked & permission-controlled.

6. Report Export Management
Supports:
PDF reports,
Excel exports,
CSV exports.

Important Rule
Exports should remain:
downloadable & traceable.

Example Exports
Sales Report
Inventory Report
Payroll Report

7. Media Optimization Engine
Supports:
image compression,
thumbnail generation,
responsive media handling.

Important Recommendation
Media uploads should remain:
optimized automatically.

Important Benefit
Improves:
application speed,
storage efficiency,
mobile performance.

8. File Access Control
FINALIZED RULE
Document visibility depends on:
role,
permissions,
ownership,
branch.

Example
HR Documents
→ HR/Admin Only

Finance Reports
→ Finance/Admin Only

Important Rule
Sensitive files remain:
highly permission-controlled.

9. File Versioning (Future Ready)
Architecture should support:
version history,
updated documents,
rollback capability.

Example
Vendor Agreement v1
Vendor Agreement v2

10. File Audit & Tracking
Tracks:
uploaded by,
modified by,
download history,
access history.

Important Rule
Critical document actions create:
audit trail.

11. Storage Structure Management
FINALIZED RULE
Files should remain:
module-organized

Example Structure
products/
employees/
vendors/
sales/
reports/
payroll/

Important Recommendation
Use:
logical folder architecture.

12. Cloud Storage Readiness
Architecture should support:
AWS S3,
Google Cloud Storage,
Azure Storage,
local storage.

Important Recommendation
Keep:
storage-provider-independent architecture.

13. Image & Media Security
Supports:
secure URLs,
protected downloads,
signed URLs (future).

Important Rule
Sensitive files should NEVER become:
publicly accessible.

14. Bulk Upload Management
Supports:
bulk image uploads,
bulk document imports,
Excel imports.

Example
Bulk Product Images Upload

Future Features
drag & drop upload,
zip extraction.

15. Generated File Automation
Supports:
auto-generated invoices,
auto-generated payslips,
export reports.

Important Rule
Generated files should:
auto-link to source transactions.

16. Media Analytics (Future)
Tracks:
storage usage,
upload activity,
download analytics.

Example Analytics
Top Storage Consumers
Monthly Upload Volume

17. Backup & Recovery Readiness
Architecture should support:
automated backups,
disaster recovery,
storage redundancy.

Important Recommendation
Critical business documents should remain:
backup-protected.

18. Future OCR & AI Readiness
Architecture should support:
invoice OCR,
document scanning,
automated document extraction.

Example Future Features
Invoice OCR
Auto GST Extraction
Document AI Classification

19. Notifications & Alerts
Supports:
document expiry alerts,
upload failure alerts,
storage warnings.

Example Alerts
Employee Document Expiring
Storage Usage High

20. Security & Compliance
Supports:
secure file access,
audit tracking,
compliance-ready document handling.

Important Rule
Document management remains:
secure & auditable.

RECOMMENDED PERMISSIONS
FILE_UPLOAD
FILE_DOWNLOAD
FILE_DELETE
MEDIA_MANAGE
DOCUMENT_VIEW
REPORT_EXPORT

RECOMMENDED DATABASE TABLES
files
file_categories
file_versions
file_access_logs
media_assets
document_links
generated_reports
storage_configurations

FINALIZED DOCUMENT MANAGEMENT RULES
Rule 1
All files remain centrally managed.

Rule 2
Files must remain linked to entities or transactions.

Rule 3
Sensitive files remain permission-controlled.

Rule 4
Generated documents auto-link to source records.

Rule 5
Media uploads remain optimized automatically.

Rule 6
Storage architecture remains cloud-independent.

Rule 7
Critical file actions create audit trail.

Rule 8
Architecture remains OCR & AI ready.

Rule 9
Critical business documents remain backup-protected.

FINAL OBJECTIVE OF MODULE 17
To create a:
Secure centralized digital asset & document management ecosystem
for the complete AsliChoice platform supporting:
Product Media Management
Invoice Storage
Employee Documents
Vendor & Customer Attachments
Report Exports
Secure File Access
Media Optimization
Cloud Storage Readiness
Future OCR & AI Document Processing

MODULE 18 — SYSTEM SETTINGS, CONFIGURATION & AUTOMATION MANAGEMENT
for AsliChoice

Purpose
System Settings, Configuration & Automation Management handles:
global settings,
branch configurations,
feature toggles,
automation rules,
scheduler jobs,
approval workflows,
operational controls,
and centralized system behavior management.
This module becomes the:
Central System Control & Automation Engine
of the platform.

FINALIZED CONFIGURATION PHILOSOPHY
System behavior should remain:
Configurable NOT Hardcoded

IMPORTANT PRINCIPLE
Configurations should support:
global defaults,
branch overrides,
role-based control,
future scalability.

MAIN SUBMODULES

1. Global System Settings
FINALIZED RULE
Super Admin should control:
Global Platform Behavior

Example Global Settings
Company Name
Currency
Timezone
Tax Settings
Invoice Prefix
Default Language

Important Rule
Global settings should support:
branch-level override where applicable.

2. Branch-wise Configuration
FINALIZED RULE
Each branch can maintain:
independent operational settings

Branch Configurations Include
payment methods,
fulfillment enablement,
attendance methods,
pricing policies,
POS configurations,
invoice series.

Example
Pune Branch
→ Biometric Attendance

Mumbai Branch
→ Application Attendance

3. Feature Toggle System
Supports:
enabling/disabling modules,
beta features,
operational controls.

Example Toggles
Wallet Enabled
Referral Enabled
Online Ordering Enabled
Payroll Enabled

Important Benefit
Supports:
phased rollout & controlled deployment.

4. Payment Configuration Management
FINALIZED RULE
Payment methods remain:
branch-configurable

Supports
UPI,
cash,
COD,
wallet,
cards,
online payment gateways.

Example
Branch A → COD Enabled
Branch B → COD Disabled

Important Rule
Payment visibility depends on:
branch + channel + configuration.

5. Attendance Configuration Management
Supports:
biometric attendance,
application punch,
GPS attendance,
hybrid attendance.

FINALIZED RULE
Attendance method remains:
configurable from super admin panel.

Supported Attendance Methods
APPLICATION
BIOMETRIC
GPS
HYBRID

Important Rule
Configurations may vary:
branch-wise.

6. Automation Rules Engine
FINALIZED RULE
Operational workflows should support:
rule-based automation.

Example Automations
Low Stock Alert
Auto Wallet Credit
Order Status Notifications
Attendance Reminders

Important Benefit
Reduces:
manual work,
operational dependency,
errors.

7. Scheduler & Cron Management
Supports:
scheduled jobs,
automated tasks,
report scheduling.

Example Jobs
Night Inventory Sync
Daily Sales Report
Payroll Processing Reminder

Important Recommendation
All scheduled tasks should remain:
centrally manageable.

8. Approval Workflow Configuration
Supports:
leave approvals,
payroll approvals,
refund approvals,
inventory adjustments.

FINALIZED RULE
Approval workflows should remain:
configurable.

Example
Refund > ₹5000
↓
Manager Approval Required

9. Notification Configuration
Supports:
SMS providers,
email providers,
WhatsApp configuration,
OTP settings.

Example
OTP Expiry = 5 Minutes
SMS Retry = 3

Important Rule
Notification behavior remains:
centrally configurable.

10. Inventory Configuration
Supports:
negative stock rules,
reorder alerts,
stock reservation,
branch transfer policies.

FINALIZED RULE
Negative stock remains:
permanently disabled.

Example Settings
Auto Reorder Alert = YES
Stock Reservation = ENABLED

11. POS Configuration
Supports:
barcode enablement,
offline mode,
invoice printing,
cashier restrictions.

Example
Manual Product Selection = ENABLED
Barcode = OPTIONAL

Important Rule
POS settings may remain:
branch-specific.

12. Online Store Configuration
Supports:
delivery rules,
pincode settings,
minimum order value,
serviceability rules.

Example
Extended Zone MOV = ₹1500

Important Rule
Online behavior remains:
pincode-aware + configurable.

13. Referral & Wallet Configuration
Supports:
commission rules,
wallet limits,
payout policies,
referral campaigns.

Example
Referral Reward = 5%
Wallet Usage Limit = 20%

Important Rule
Referral system remains:
non-MLM.

14. Finance & Accounting Configuration
Supports:
ledger settings,
tax rules,
invoice sequences,
branch accounting rules.

Example
GST Enabled = YES
Invoice Auto-numbering = YES

15. Security & Session Configuration
Supports:
password policies,
session timeout,
login restrictions,
device restrictions.

Example
Session Timeout = 30 Minutes

Important Rule
Security settings remain:
centrally managed.

16. Audit & System Logs
Tracks:
configuration changes,
automation execution,
admin actions,
failed jobs.

Important Rule
Critical configuration changes create:
audit trail.

17. Multi-language & Localization Settings
Supports:
language preferences,
regional settings,
future localization.

Supported Future Languages
English
Hindi
Marathi

18. Backup & Recovery Configuration
Supports:
automated backups,
backup schedules,
recovery settings.

Important Recommendation
Critical business data should remain:
backup-protected.

19. API & Integration Configuration
Supports future:
payment gateway APIs,
delivery APIs,
biometric APIs,
accounting integrations.

Important Recommendation
Keep:
integration-ready configuration architecture.

20. Future AI & Smart Automation Readiness
Architecture should support:
AI alerts,
predictive automation,
smart reorder rules,
AI analytics.

Example Future Features
AI Low Stock Prediction
Auto Procurement Suggestion

RECOMMENDED PERMISSIONS
SYSTEM_SETTINGS_MANAGE
AUTOMATION_MANAGE
BRANCH_CONFIGURATION
PAYMENT_CONFIGURATION
SECURITY_CONFIGURATION
FEATURE_TOGGLE_MANAGE

RECOMMENDED DATABASE TABLES
system_settings
branch_configurations
feature_toggles
automation_rules
scheduler_jobs
approval_workflows
payment_configurations
attendance_configurations
notification_configurations
security_configurations
audit_logs

FINALIZED CONFIGURATION RULES
Rule 1
System behavior remains configurable, not hardcoded.

Rule 2
Configurations support global defaults + branch overrides.

Rule 3
Payment methods remain branch-configurable.

Rule 4
Attendance methods remain configurable from super admin panel.

Rule 5
Negative stock remains permanently disabled.

Rule 6
Automation workflows remain rule-driven.

Rule 7
Approval workflows remain configurable.

Rule 8
Critical configuration changes create audit trail.

Rule 9
Security settings remain centrally managed.

Rule 10
Architecture remains AI & automation ready.

FINAL OBJECTIVE OF MODULE 18
To create a:
Centralized configurable automation & operational control ecosystem
for the complete AsliChoice platform supporting:
Global System Configuration
Branch Operational Controls
Automation Rules
Attendance Configuration
Payment Configuration
Security Management
Workflow Automation
Feature Toggles
Future AI-driven Operations

MODULE 19 — SUPER ADMIN, SECURITY & AUDIT CONTROL MANAGEMENT
for AsliChoice

Purpose
Super Admin, Security & Audit Control Management handles:
super admin governance,
platform-wide control,
audit tracking,
security policies,
access monitoring,
fraud prevention,
session management,
device restrictions,
and operational governance.
This module becomes the:
Enterprise Governance, Security & Control Engine
of the platform.

FINALIZED SECURITY PHILOSOPHY
Every critical action should remain:
Permission-controlled + Auditable + Traceable

IMPORTANT PRINCIPLE
Security should integrate across:
users,
finance,
inventory,
payroll,
POS,
CRM,
approvals,
and automation.

MAIN SUBMODULES

1. Super Admin Control Panel
FINALIZED RULE
Super Admin should have:
centralized enterprise control
over the complete platform.

Super Admin Controls
Supports:
global configurations,
branch management,
feature toggles,
security controls,
audit access,
operational overrides.

Important Rule
Super Admin actions should remain:
fully auditable.

2. Role-based Access Control (RBAC)
FINALIZED RULE
Every user action should depend on:
permissions
NOT only role names.

Example Permissions
INVENTORY_VIEW
PAYROLL_APPROVE
REFUND_APPROVE
SYSTEM_SETTINGS_MANAGE

Important Rule
Permissions remain:
granular & scalable.

3. Permission Audit System
Tracks:
permission changes,
role assignments,
access escalations.

Example
User X
→ Payroll Approval Access Granted

Important Rule
Permission changes create:
audit logs.

4. Audit Logging System
FINALIZED RULE
Critical business actions create:
immutable audit logs

Audit Scope Includes
inventory adjustments,
refunds,
payroll approvals,
wallet adjustments,
system setting changes,
login activity.

Suggested Audit Fields
User
Action
Timestamp
IP Address
Branch
Device
Remarks

Important Rule
Audit logs should remain:
tamper-resistant.

5. Login & Session Security
Supports:
session timeout,
device tracking,
concurrent session control,
suspicious login detection.

Example Settings
Session Timeout = 30 Minutes
Max Concurrent Login = 1

Important Rule
Security policies remain:
centrally configurable.

6. Device Management & Restrictions
Supports:
authorized devices,
branch device mapping,
POS terminal restrictions.

Example
POS Billing
→ Allowed only from registered POS devices

Important Benefit
Prevents:
unauthorized operations,
remote misuse.

7. Branch-wise Security Controls
Supports:
branch-specific access,
branch-level restrictions,
branch device policies.

Example
Pune Manager
→ Pune Data Only

Important Rule
Data visibility remains:
branch-aware.

8. Financial Security Controls
Supports:
refund approval hierarchy,
wallet adjustment restrictions,
payroll approval controls.

Example
Refund > ₹5000
↓
Manager Approval Mandatory

Important Rule
Sensitive financial actions require:
multi-level authorization.

9. Inventory Security Controls
Supports:
stock adjustment approvals,
transfer approvals,
inventory audit monitoring.

Important Rule
Inventory modifications remain:
audit-traceable.

10. HR & Payroll Security
Supports:
salary access control,
payroll approval restrictions,
attendance audit tracking.

Important Rule
Payroll & HR data remain:
highly restricted.

11. POS Security Controls
Supports:
cashier shift validation,
refund restrictions,
offline sync audit.

Example
Cashier cannot:
→ approve high refunds

Important Rule
POS operations remain:
operator-traceable.

12. Fraud Prevention & Risk Monitoring
Supports:
suspicious activity alerts,
unusual refund monitoring,
duplicate transaction detection.

Example Alerts
High Refund Activity
Multiple Failed OTP Attempts

Important Recommendation
Use:
risk-based monitoring architecture.

13. OTP & Verification Security
Supports:
OTP retry limits,
brute-force prevention,
verification throttling.

Example
Max OTP Retry = 5

Important Rule
Authentication systems remain:
rate-limited & secure.

14. API & Integration Security
Supports:
API authentication,
token management,
webhook validation.

Important Recommendation
All integrations should remain:
authenticated & logged.

15. Data Access Governance
Supports:
restricted exports,
sensitive data masking,
download permissions.

Example
Employee Salary
→ HR/Admin Only

Important Rule
Sensitive data exports require:
permissions.

16. Operational Monitoring Dashboard
Supports:
active sessions,
failed logins,
audit alerts,
system health.

Example Monitoring
Online Users
Failed Login Attempts
Pending Critical Approvals

17. Backup & Disaster Recovery Governance
Supports:
backup monitoring,
recovery verification,
disaster readiness.

Important Rule
Critical operational data should remain:
recoverable.

18. Compliance & Governance Readiness
Architecture should support:
GST audit readiness,
HR audit readiness,
financial audit readiness.

Important Benefit
Supports:
enterprise compliance operations.

19. Future Multi-factor Authentication (MFA)
Architecture should support:
OTP MFA,
authenticator apps,
biometric login.

Future Features
2FA Login
Biometric Login
Trusted Device Verification

20. Security Analytics
Tracks:
failed logins,
suspicious access,
approval anomalies,
security incidents.

Recommended Reports
Audit Report
Security Incident Report
Permission Change Report

RECOMMENDED PERMISSIONS
SUPER_ADMIN
AUDIT_VIEW
SECURITY_MANAGE
SESSION_MONITOR
PERMISSION_MANAGE
DEVICE_MANAGE

RECOMMENDED DATABASE TABLES
audit_logs
user_sessions
device_registrations
permission_audits
security_events
failed_login_attempts
otp_security_logs
system_health_logs
approval_audit_logs

FINALIZED SECURITY RULES
Rule 1
All critical actions remain permission-controlled.

Rule 2
Critical business operations create immutable audit logs.

Rule 3
Security remains branch-aware.

Rule 4
Sensitive financial actions require approval hierarchy.

Rule 5
Device access remains controllable.

Rule 6
POS operations remain operator-traceable.

Rule 7
Sensitive HR & payroll data remain restricted.

Rule 8
Authentication systems remain rate-limited & secure.

Rule 9
Audit logs remain tamper-resistant.

Rule 10
Architecture remains MFA & enterprise security ready.

FINAL OBJECTIVE OF MODULE 19
To create a:
Secure enterprise governance, audit & operational control ecosystem
for the complete AsliChoice platform supporting:
Super Admin Governance
Enterprise Security
Audit Logging
Fraud Prevention
Session Monitoring
Permission Governance
Device Security
Financial Approval Controls
Enterprise Compliance Readiness
MODULE 20 — MOBILE APP, OFFLINE SYNC & API INTEGRATION MANAGEMENT
for AsliChoice

Purpose
Mobile App, Offline Sync & API Integration Management handles:
mobile application architecture,
offline-first operations,
sync engine,
API ecosystem,
third-party integrations,
device synchronization,
and future digital ecosystem connectivity.
This module becomes the:
Digital Connectivity & Mobility Engine
of the platform.

FINALIZED DIGITAL PHILOSOPHY
System should remain:
Mobile-ready + Offline-capable + API-driven

IMPORTANT PRINCIPLE
The platform should work reliably even during:
unstable internet,
branch connectivity issues,
mobile network interruptions.

MAIN SUBMODULES

1. Mobile App Architecture
FINALIZED RULE
Platform should support:
Multi-app ecosystem

Suggested Apps
Customer App
POS App
Delivery App (future)
Partner App (future)
Admin App (future)

Important Recommendation
Use:
API-first architecture
for all applications.

2. Offline-first Architecture
FINALIZED RULE
Critical operations should support:
Offline Mode

Supported Offline Operations
POS Billing
Attendance Punch
Inventory Lookup
Customer Lookup

Important Rule
Offline mode should maintain:
inventory integrity.

3. Central Sync Engine
FINALIZED RULE
Offline transactions should:
queue locally and sync later.

Sync Flow
Offline Action
      ↓
Local Queue
      ↓
Internet Available
      ↓
Background Sync

Important Rule
Sync engine should remain:
conflict-aware.

4. Offline Inventory Consistency
FINALIZED RULE
Offline inventory should remain:
locally controlled
to prevent overselling.

Example
Local Stock = 5
Offline Sale = 5
↓
Next Billing Blocked

Important Rule
Negative stock remains:
strictly prohibited.

5. Offline POS Support
Supports:
offline billing,
local invoice generation,
sync queue management.

Important Features
local product cache,
local inventory cache,
offline customer cache.

Important Rule
POS should remain:
operational during internet failure.

6. Offline Attendance Support
Supports:
offline punch-in,
offline shift tracking.

Sync Flow
Offline Attendance
↓
Local Save
↓
Sync Later

7. API Gateway Architecture
FINALIZED RULE
All applications should communicate through:
Central API Layer

API Scope
Supports:
web app,
mobile app,
POS app,
third-party integrations.

Important Benefit
Provides:
scalability,
integration readiness,
app consistency.

8. Authentication & API Security
Supports:
token authentication,
session validation,
device authorization.

Important Rule
All APIs should remain:
authenticated & rate-limited.

Future Features
OAuth
API Keys
Webhook Security

9. Third-party Integration Readiness
Architecture should support:
payment gateways,
delivery partners,
biometric systems,
accounting systems,
SMS/email providers.

Example Integrations
Razorpay
Shiprocket
ZKTeco
Tally

Important Recommendation
Use:
modular integration architecture.

10. Push Notification Integration
Supports:
mobile push notifications,
app alerts,
operational reminders.

Example Notifications
Order Delivered
Wallet Credited
Attendance Reminder

11. Device Management
Supports:
device registration,
trusted device management,
branch device mapping.

Example
POS Device
→ Branch Linked

Important Rule
Critical operations may remain:
device-restricted.

12. Local Data Caching
Supports:
product cache,
inventory cache,
customer cache,
settings cache.

Important Benefit
Improves:
performance,
offline usability,
response speed.

13. Sync Conflict Resolution
FINALIZED RULE
Sync engine should support:
conflict detection & resolution

Example Conflicts
Offline Inventory Change
Online Inventory Change

Important Recommendation
Use:
timestamp + transaction priority logic.

14. Background Sync Processing
Supports:
automatic sync,
retry queue,
failed sync recovery.

Important Rule
Sync operations should remain:
resilient & recoverable.

15. API Monitoring & Analytics
Tracks:
API usage,
failed requests,
sync failures,
mobile performance.

Recommended Metrics
API Response Time
Sync Failure Rate
Offline Queue Size

16. Mobile Performance Optimization
Supports:
lightweight APIs,
optimized media,
cached requests.

Important Recommendation
Mobile apps should remain:
low-bandwidth optimized.

17. Future PWA (Progressive Web App) Readiness
Architecture should support:
web app behaving like mobile app.

Future Features
Installable Web App
Offline Browser Support
Push Notifications

18. Future IoT & Smart Device Readiness
Architecture should support:
smart weighing scales,
barcode scanners,
IoT inventory devices.

Example Future Features
Smart Inventory Sensors
Auto Weight Integration

19. Backup & Recovery for Offline Devices
Supports:
local backup,
recovery sync,
queue restoration.

Important Rule
Offline operations should remain:
recoverable after failure.

20. Security & Audit
Supports:
sync audit logs,
API audit tracking,
device activity logs.

Important Rule
All offline & API operations create:
audit trail.

RECOMMENDED PERMISSIONS
API_MANAGE
DEVICE_MANAGE
SYNC_MONITOR
OFFLINE_OVERRIDE
MOBILE_APP_MANAGE

RECOMMENDED DATABASE TABLES
api_tokens
device_registrations
offline_sync_queue
sync_logs
mobile_sessions
api_request_logs
integration_configurations
offline_cache_metadata

FINALIZED MOBILE & SYNC RULES
Rule 1
Platform remains API-first.

Rule 2
Critical operations support offline mode.

Rule 3
Offline transactions queue locally and sync later.

Rule 4
Offline inventory remains locally controlled.

Rule 5
Negative stock remains strictly prohibited.

Rule 6
All APIs remain authenticated & rate-limited.

Rule 7
Sync engine remains conflict-aware.

Rule 8
Critical operations may remain device-restricted.

Rule 9
Offline operations remain recoverable.

Rule 10
All sync & API operations create audit trail.

FINAL OBJECTIVE OF MODULE 20
To create a:
Offline-capable omnichannel mobility & digital integration ecosystem
for the complete AsliChoice platform supporting:
Mobile Applications
Offline-first Operations
Sync Engine
API Ecosystem
Third-party Integrations
Device Management
Push Notifications
Future PWA Support
Future IoT Expansion



