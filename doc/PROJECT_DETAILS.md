# AsliChoice — Project Details

> Source: `SOFTWARE REQUIREMENT SPECIFICATION ASLI CHOICE.docx`
> This file is a structured, planning-ready summary of the SRS. Use it as the working reference for module design, schema planning, and phasing.

---

## 1. Platform Overview

**AsliChoice** is an omnichannel commerce + operations platform covering:

- Retail POS (offline-capable)
- Online Store (location-aware ecommerce)
- Inventory across branches & warehouses
- Procurement (centralized) and Vendor management
- CRM, Referral & Wallet
- Finance, Accounting & GST
- HR, Attendance & Payroll
- Reporting / BI
- Logistics & Fulfillment
- Returns / QC
- System configuration, Security, Audit
- Mobile apps + Offline sync + APIs

### Cross-cutting Architectural Principles

| Principle | Meaning |
|---|---|
| Centralized Inventory + Distributed Branch Ownership | One inventory engine; stock belongs to `Branch + Warehouse`. |
| Ledger-Driven | Inventory, wallet, and finance never allow direct edits — only ledger entries. |
| Branch-Aware | POS, fulfillment, payments, reports, security all scope by branch. |
| Pincode-Aware | Online inventory visibility, MOV, delivery, serviceability, fulfillment all depend on pincode. |
| Omnichannel Unified Engine | POS + Online + future Wholesale share inventory, customers, offers, wallet, referral, reporting. |
| Negative Stock — Strictly Prohibited | Hard-block, not warning. Inventory can hit 0, never below. |
| Configurable, Not Hardcoded | Global + branch-override settings; feature toggles. |
| API-First, Offline-Capable | Mobile apps, POS, attendance must work offline and sync later. |
| Audit-Everywhere | Every critical action creates an immutable audit log. |
| Non-MLM Referral | Single-level only; successful referrer auto-becomes Partner. |
| Soft Delete Only for masters | Never permanently delete masters; `is_active = false`. |

---

## 2. Module Index

| # | Module | Role |
|---|---|---|
| 1 | Master Management | Single source of truth (products, pricing, branches, taxes, customers, vendors) |
| 2 | User & Role Management | Auth, roles, permissions, sessions, audit |
| 3 | Vendor Management | Procurement-ready supplier ecosystem |
| 4 | Purchase Management | Centralized procurement + branch-aware GRN |
| 5 | Inventory Management | Ledger-driven, branch + warehouse stock |
| 6 | Online Store | Location-aware ecommerce |
| 7 | Retail POS | Branch-scoped, offline-capable billing |
| 8 | Sales & Order Management | Unified commerce transaction engine |
| 9 | CRM & Customer Management | Central customer intelligence |
| 10 | Referral, Partner & Wallet | Non-MLM growth & incentive engine |
| 11 | Notifications & Communication | OTP/SMS/Email/WhatsApp/Push |
| 12 | Finance, Accounts & Ledger | Branch-aware accounting & GST |
| 13 | Reports, Analytics & BI | Role-based dashboards & exports |
| 14 | Delivery, Logistics & Fulfillment | Pincode + branch-based fulfillment |
| 15 | Returns, Damages & QC | Inventory recovery & quality assurance |
| 16 | HR, Staff, Attendance & Payroll | Phase 1 includes payroll |
| 17 | Document, Media & File Management | Central digital asset engine |
| 18 | System Settings, Configuration & Automation | Global + branch configs, toggles, cron, workflows |
| 19 | Super Admin, Security & Audit | Enterprise governance |
| 20 | Mobile App, Offline Sync & API | Mobility + digital connectivity |

---

## MODULE 1 — Master Management

**Foundation. Single source of truth for products, pricing, branches, taxes, customers, vendors. All other modules depend on it.**

### Submodules
1. **Product Master** — Name, SKU, Barcode, HSN, Brand, Images, Active/Online/POS flags. Types: Simple, Variant, Combo, Service.
2. **Category Management** — Multi-level parent-child.
3. **Product Variants** — Separate SKU/barcode/inventory/price per variant (size, flavor, weight, packaging).
4. **Unit Management** — Kg, g, L, Piece, Bottle; supports conversions (1 Box = 12 Bottles).
5. **Brand Management** — Name, logo, description, status.
6. **Tax Management (GST)** — CGST/SGST/IGST, inclusive/exclusive, product-wise.
7. **Price Management** — Categories: MRP, Retail, Wholesale, Partner, Internal Consumption. Branch-wise ready.
8. **Internal Consumption Pricing** — Super Admin only; no backdated entries; mandatory comments; immediate inventory reduction; separate reporting.
9. **Branch & Warehouse Management** — Multiple branches/warehouses, branch-wise stock, GST/contact info.
10. **Customer Master** — Name, mobile, email, address, optional GST.
11. **Vendor Master** — Vendor name, contact, GST, payment terms.
12. **Payment Mode Master** — Cash, UPI, Card, Wallet, Bank Transfer.
13. **Offer/Coupon Master** — %/flat/product-based, expiry.

### Business Rules
- Structured SKU (e.g. `GHE-GIR-500`).
- Barcode-ready from Day 1.
- Soft delete only.
- Multi-branch ready even if launching single-branch.
- Audit logs for product/price/inventory-affecting changes.

### Core Tables
`products, product_variants, categories, brands, units, taxes, price_lists, branches, warehouses, customers, vendors, payment_modes, offers, internal_consumptions`

---

## MODULE 2 — User & Role Management

**Security backbone. Auth, authorization, roles, permissions, branch access, sessions, audit, user hierarchy.**

### Architecture
- **Single unified user table** for customers, partners, staff, admins, vendors.
- One user can have multiple roles (e.g. Customer + Partner).
- Structure: `User → Roles → Permissions → Branch Access → Profiles`.

### Authentication
- **Identifiers**: Mobile, Email.
- **Methods**: OTP login, Password login.
- **OTP Channels**: SMS, Email.
- **Smart OTP Fallback**: If user enters mobile but mobile OTP is disabled and email OTP is enabled with verified email → send to email. Reverse also supported. *User input ≠ OTP destination.*
- **Super Admin controls**: enable/disable each identifier, method, channel; OTP length, expiry, cooldown, max attempts.
- **Validation guard**: System blocks invalid combos (e.g. Mobile login on + Mobile OTP off + Password off).

### Roles
`SUPER_ADMIN, ADMIN, MANAGER, STAFF, CASHIER, CUSTOMER, PARTNER, VENDOR`

### Permissions
Granular `VIEW / CREATE / EDIT / DELETE / APPROVE / EXPORT` per resource (e.g. `PRODUCT_VIEW`, `PRODUCT_CREATE`).

### Branch Access
Single / Multi / All-branch.

### Profiles
Common (name, mobile, email, address, DOB, photo) + Specialized (Staff: empId/dept; Partner: referral code/wallet; Vendor: GST/company).

### Referral → Partner Flow
Customer refers → referred customer completes successful purchase → original customer **auto-becomes Partner**. Single-level only. No MLM.

### Wallet
Commission → Internal Wallet. No payouts initially; payout-ready schema preserved.

### Security
JWT + refresh tokens, role + permission middleware, route guards, permission-based menus, session tracking, force logout, OTP rate limiting.

### Tables
`users, roles, permissions, user_roles, role_permissions, user_permissions, user_branches, sessions, audit_logs, partner_profiles, staff_profiles, vendor_profiles, customer_profiles`

---

## MODULE 3 — Vendor Management

**Procurement foundation. Vendor ≠ contact record — a fully trackable procurement entity with transaction, pricing, payment, supply, and analytics history.**

### Submodules
1. **Vendor Master** — Business (Name, Company, Code, GST, PAN, Category, Business Type), Contact, Addresses (Billing/Pickup/Warehouse), Banking, Tax (GST type/state, future TDS). Vendor Code auto-generated (e.g. `VEN-0001`).
2. **Vendor Categories** — `RAW_MATERIAL, PACKAGING, TRANSPORT, SERVICE_PROVIDER, DISTRIBUTOR, MANUFACTURER`.
3. **Status** — `ACTIVE, INACTIVE, BLACKLISTED, ON_HOLD`. Blacklisted cannot transact.
4. **Contact Persons** — Multiple per vendor (Accounts, Sales, Dispatch).
5. **Payment Terms** — Advance, Net 7/15/30; default + PO-level override.
6. **Pricing** — Vendor-specific rates; **price history with effective dates**.
7. **Vendor-Product Mapping** — Multiple vendors per product, preferred vendor, lead time, MOQ.
8. **Performance Tracking** — Delivery on-time, quality/rejection, pricing stability, volume; vendor scorecards (future).
9. **Documents** — GST cert, agreements, quotations, licenses; upload + expiry tracking.
10. **Communication Log** — Calls, emails, meetings, negotiations.
11. **Notes & Remarks** — Internal only, not vendor-visible.
12. **Vendor-Branch Mapping** — Optional, for local procurement.
13. **Approval Workflow** (future) — Created → Verification → Approval → Activated.
14. **Ledger** (future finance) — Total purchases, payments, outstanding, debit/credit notes. Finance-ready schema from Day 1.
15. **Vendor Portal** (future).

### Validations
- GST format validation mandatory.
- Duplicate detection on GST / mobile / company.
- Soft delete only.

### Permissions
`VENDOR_VIEW, VENDOR_CREATE, VENDOR_EDIT, VENDOR_APPROVE, VENDOR_EXPORT`

### Tables
`vendors, vendor_contacts, vendor_categories, vendor_products, vendor_price_history, vendor_documents, vendor_notes, vendor_payment_terms, vendor_communications, vendor_branch_mapping, vendor_ledgers`

---

## MODULE 4 — Purchase Management

**Centralized procurement + distributed inventory. Procurement controlled by HO/Main Branch; inventory belongs to branch + warehouse.**

### Procurement Scenarios
- **Scenario 1 — Central Warehouse**: Vendor → HO Purchase → HO Warehouse GRN → HO Inventory → Branch Transfer.
- **Scenario 2 — Direct Branch**: HO PO → Vendor delivers to Branch → Branch GRN → Branch Inventory.

### Submodules
1. **Purchase Requisition** — Internal request. Only HO/Main Branch creates. Multiple requisitions can merge into one PO. Doesn't affect inventory. Priorities: `LOW/MEDIUM/HIGH/URGENT`. Status flow: `DRAFT → SUBMITTED → APPROVED → PARTIALLY_PROCESSED → COMPLETED → REJECTED`.
2. **Purchase Order** — Header (PO#, Vendor, Procurement Branch, **Destination Branch**, **Destination Warehouse**, dates, terms) + Items (product/variant/qty/unit/rate/tax/discount). Statuses: `DRAFT → PENDING_APPROVAL → APPROVED → PARTIALLY_RECEIVED → COMPLETED / CANCELLED`. Auto-generated PO numbers.
3. **Approval Workflow** — Small auto-approve, large needs admin. Future: Manager → Admin → Super Admin.
4. **GRN (Most Critical)** — **Inventory updates ONLY after GRN**, never after PO. GRN updates Destination Branch + Warehouse inventory. Fields: GRN#, linked PO, dest branch/warehouse, received qty, damaged qty, receiver, notes.
5. **Partial Receipt** — Multiple inwarding under one PO.
6. **Purchase Invoice** — Invoice upload, GST, tax breakup, PO + GRN + vendor linkage. Finance-ready.
7. **Purchase Returns** — Reasons: `DAMAGED, WRONG_PRODUCT, EXPIRED, QUALITY_ISSUE`. Affects branch inventory, warehouse stock, vendor ledger, analytics.
8. **Vendor Credit & Payment** — Outstanding, due dates, advance, partial payments. Modes: Cash, UPI, Bank, Cheque.
9. **Attachments** — Invoices, quotations, transport receipts.
10. **Notes & Remarks** — Internal.
11. **Inventory Integration** — Movement type `PURCHASE`. Inventory belongs to Dest Branch + Warehouse.
12. **Multi-branch Procurement** — HO can purchase for any branch. **Branches cannot directly purchase from vendors.**
13. **Analytics** — Branch/vendor/product purchase trends, cost trends, delayed delivery, returns.
14. **Reports** — Purchase Register, PO, GRN, Branch/Vendor-wise, Pending PO, Returns, Outstanding Vendor.
15. **Barcode Integration** — Inward scanning, GRN verification.
16. **Offline Support** (future).

### Permissions
`PURCHASE_VIEW, PURCHASE_CREATE, PURCHASE_APPROVE, PURCHASE_GRN, PURCHASE_RETURN, PURCHASE_EXPORT, REQUISITION_CREATE/APPROVE/CONVERT_TO_PO`

### Tables
`purchase_requisitions(_items), purchase_orders(_items), goods_receipts(_items), purchase_invoices, purchase_returns(_items), purchase_payments, vendor_ledgers, purchase_attachments, purchase_notes, purchase_status_logs`

---

## MODULE 5 — Inventory Management

**Central operational engine. Centralized inventory engine + distributed branch ownership. Inventory belongs to `Branch + Warehouse`, never globally.**

### Stock Buckets
`Available, Reserved, Damaged, Transit, Blocked`.

### Submodules
1. **Inventory Ledger (Most Critical)** — No direct stock editing. Every movement creates a ledger entry with: product, variant, branch, warehouse, movement type, qty change, before/after qty, reference#, user, timestamp.
2. **Branch-wise Inventory** — Separate stock/visibility/reports per branch. Users only access authorized branches.
3. **Warehouse Management** — Types: `MAIN_WAREHOUSE, STORE_WAREHOUSE, DAMAGE_WAREHOUSE, TRANSIT_WAREHOUSE`.
4. **Movement Types** — `PURCHASE, SALE, RETURN, TRANSFER_IN, TRANSFER_OUT, ADJUSTMENT, DAMAGE, INTERNAL_CONSUMPTION, OPENING_STOCK` (+ future: MANUFACTURING, ASSEMBLY, BUNDLE, SUBSCRIPTION_RESERVE).
5. **Stock Transfers** — HO↔Branch, Branch↔Branch, Warehouse↔Warehouse. Statuses: `PENDING → IN_TRANSIT → RECEIVED / CANCELLED`. Source reduces immediately; destination increases only after receiving confirmation.
6. **Reservations** — For online orders, draft invoices, future bookings. Auto-expire on cancel/abandon.
7. **Damaged Inventory** — Reasons: `BROKEN, EXPIRED, LEAKAGE, QUALITY_ISSUE`. Moves to damage warehouse.
8. **Adjustments** — Permission + reason + audit. Reasons: `PHYSICAL_COUNT, SYSTEM_CORRECTION, MISPLACED, INITIAL_SETUP`. Creates ledger entry.
9. **Opening Stock** — Creates ledger entry, separately identifiable.
10. **Batch & Expiry** (future-ready Day 1 schema) — Batch#, mfg date, expiry, FIFO.
11. **Barcode** — Generation, scanning, search, POS integration; future QR + label printing.
12. **Audits** — Stock count sheets, variance reports.
13. **Low Stock Alerts** — Branch-wise thresholds; future email/WhatsApp/push.
14. **POS Visibility** — Current branch only. POS sales consume local branch inventory only. Optional permissioned cross-branch lookup.
15. **Online Visibility (Location-Aware)** — Customer pincode → nearest fulfillment branch → relevant inventory. **Never show global stock.** Maintain `online sellable quantity = physical − reserved buffer`. Per-branch `online_fulfillment_enabled = YES/NO`. Fulfillment priority: Nearest Branch → City Warehouse → HO Warehouse.
16. **Reports** — Stock Summary, Ledger, Branch/Warehouse-wise, Low Stock, Damaged, Fast/Slow/Dead Stock, Valuation, Expiry, Online Fulfillment.
17. **Offline Inventory Sync** — Queue-based, conflict-resolving.
18. **Valuation** — FIFO, AVERAGE_COST (avoid LIFO initially).

### Permissions
`STOCK_VIEW, STOCK_TRANSFER, STOCK_ADJUST, STOCK_AUDIT, STOCK_EXPORT`

### Tables
`inventory, inventory_ledger, inventory_movements, stock_transfers(_items), warehouses, warehouse_stocks, damaged_inventory, inventory_adjustments, inventory_reservations, batch_inventory, opening_stock, stock_audits`

---

## MODULE 6 — Online Store

**Digital commerce channel. Same inventory/pricing/customers/orders/wallet/referral/offers as the rest of the platform — ecommerce is a sales channel, not a separate system.**

### Submodules
1. **Customer Storefront** — Homepage, banners, categories, listings, offers, search, featured. Mobile-first.
2. **Product Catalog** — Products/variants/pricing/stock/details/offers; `ONLINE_VISIBLE` flag hides POS-only products.
3. **Intelligent Location Selection** — Auto-suggest from last pincode → saved address → GPS → manual. **Customer confirmation mandatory.** Inventory loads only after location confirmation.
4. **Mandatory Pincode-Based Shopping** — Inventory, delivery, offers, fulfillment all pincode-aware.
5. **Location-Aware Inventory Visibility** — Customer pincode → nearest fulfillment branch. Never show global stock.
6. **Search & Filters** — Keyword/category/brand/price/availability; future: AI recommendations, voice.
7. **Shopping Cart** — Validates live inventory before checkout.
8. **Checkout** — Address, delivery validation, payment, summary. Fast & minimal.
9. **Customer Registration & Access** — Only registered customers can place orders. Guests can browse & explore.
10. **Intelligent Registration Approval** — Serviceable pincode → auto-approve after OTP. Non-serviceable → store in CRM + generate Admin Serviceability Request (not rejection).
11. **Pincode Serviceability Engine** — Zones: `STANDARD, EXTENDED, PREMIUM_SPECIAL, NON_SERVICEABLE`.
12. **Delivery Charge Engine** — Per pincode: delivery fee, extra fee, free threshold, ETA, COD availability, assigned branch.
13. **Minimum Order Value (MOV)** — Varies by pincode/zone.
14. **Delivery & Fulfillment** — Customer location → fulfillment branch → reservation → confirm → dispatch. Future models: `STANDARD_DELIVERY, SAME_DAY_DELIVERY, STORE_PICKUP`.
15. **Inventory Reservation** — During order placement; auto-expires.
16. **Order Management** — `PENDING → CONFIRMED → PACKED → SHIPPED → DELIVERED → COMPLETED` (+ CANCELLED/RETURNED/REFUNDED). Audit trail on each event.
17. **Payment Gateway** — UPI, cards, net banking, COD, wallet; future: Razorpay/PhonePe/Paytm. Modes: `ONLINE_PAYMENT, COD, WALLET`.
18. **Offers & Coupons** — Channel types: `ONLINE, POS, BOTH`.
19. **Referral Integration** — Reward triggers only after successful completion.
20. **Wallet Integration** — Redemption, referral rewards, future cashback.
21. **Customer Account Panel** — Profile, addresses, orders, wallet, referrals, saved, reorder, invoice download, tracking.
22. **Wishlist** — Future: stock & price-drop alerts.
23. **Notifications** — Order/payment/shipping/delivery. Future: SMS/Email/WhatsApp/Push.
24. **SEO & Marketing** — SEO URLs, meta, sitemap; future: abandoned cart, recommendations, campaigns.
25. **Reports** — Online sales, pincode-wise, branch fulfillment, delivery profitability, cart abandonment, offer usage, location-wise demand.
26. **Security** — Secure checkout, payment validation, fraud prevention, audit logs. Never store sensitive payment data directly.

### Tables
`online_orders(_items), customer_addresses, shopping_carts, cart_items, wishlists(_items), online_payments, coupons, coupon_usages, serviceable_pincodes, online_fulfillment_logs, order_status_logs, customer_serviceability_requests`

---

## MODULE 7 — Retail POS

**Physical retail sales channel. Branch-specific. Uses same inventory/pricing/offers/customer/wallet engines.**

### Submodules
1. **Billing Interface** — Left: search/categories/products; Right: bill/totals/payment. Fast, minimal.
2. **Product Selection** — Barcode scan, manual search (name/SKU/category/partial), category selection, frequent products. **Barcode is optional, never mandatory.** Manual selection fully supported.
3. **Strict Stock-Aware Billing** — Real-time validation. **Negative stock strictly not allowed.** Stock may reach 0 but never below. Hard-block, not warning.
4. **Category-Based Quick Billing** — For touch-screen / fast counters.
5. **Frequent / Recent / Favorite Products** — Improves billing speed.
6. **Variant-Aware Billing** — Size/pack selection per product.
7. **Customer Management** — Existing lookup by mobile, new customer creation, optional tagging. Types: `WALK_IN, REGISTERED, PARTNER`.
8. **Offers & Discounts** — Channels `ONLINE / POS / BOTH`. Flat, %, bill-level, product-level. Validation includes POS channel.
9. **Payment Collection** — `CASH, UPI, CARD, WALLET, MIXED`. Supports multi-payment billing (e.g. ₹500 Cash + ₹300 UPI).
10. **Wallet Integration** — Redemption, loyalty, referral usage; ledger-driven.
11. **Invoices** — Thermal, A4, digital. Branch + GST + items + payment + savings. Future: WhatsApp/email/QR receipts.
12. **Returns & Exchanges** — Full/partial/exchange. Reasons: `DAMAGED, WRONG_PRODUCT, CUSTOMER_RETURN`. Restores branch inventory.
13. **Offline POS Support (Most Critical)** — Must work without internet. Offline billing → local queue → sync later. Offline POS is branch-scoped; offline inventory remains locally consistent (blocks once local stock = 0). Requires: local inventory + product cache, offline invoice numbering, sync conflict handling.
14. **Inventory Consumption** — Current branch only; never global. Optional permissioned cross-branch lookup.
15. **Cashier & Shift Management** — Login, shift open/close, opening/closing balance, cash mismatch tracking.
16. **Reports** — Daily sales, cashier-wise, branch-wise, payment-mode, returns, discount, item-wise.
17. **Notifications** (future) — Low stock, shift, billing alerts.
18. **Security & Audit** — All billing creates audit trail; cashier tracking, refund approvals.
19. **Performance** — Local caching, lightweight UI, fast search, keyboard shortcuts.

### Permissions
`POS_BILLING, POS_RETURN, POS_DISCOUNT, POS_CASHIER_CLOSE, POS_REPORT_VIEW, POS_REFUND_APPROVE`

### Tables
`pos_sales(_items), pos_payments, pos_returns(_items), cashier_shifts, cashier_sessions, pos_devices, offline_sync_queue`

---

## MODULE 8 — Sales & Order Management

**Central commerce transaction engine. All channels (Online, POS, future Wholesale, future Direct) share inventory, customers, offers, wallet, referral, reporting.**

### Submodules
1. **Unified Sales Engine** — All sales flow into one central system.
2. **Channels** — `ONLINE, POS, WHOLESALE, MANUAL`. Affects offers, workflows, invoice flow, reporting.
3. **Sales Order Flow** — Created → Inventory Reserved → Payment Validated → Processing → Dispatch → Delivery → Completion.
4. **Status Flow** — `PENDING → CONFIRMED → PROCESSING → PACKED → SHIPPED → DELIVERED → COMPLETED` (+ CANCELLED/RETURNED/REFUNDED/FAILED). Configurable.
5. **Inventory Integration** — Online: reserve → confirm → deduct on fulfillment. POS: instant deduction. Overselling hard-blocks order/billing.
6. **Branch-wise Sales** — Every sale tagged with Branch + Warehouse. Branch-aware analytics.
7. **Customer Sales History** — Unified omnichannel profile.
8. **Invoice Management** — GST/retail invoices, branch-wise series, digital + printable. Future: e-invoicing, e-way bill.
9. **Payment Management** — `CASH, UPI, CARD, BANK_TRANSFER, COD, WALLET, MIXED`. **Payment methods are branch-configurable.** POS shows only branch-enabled methods. Online checkout loads methods based on fulfillment branch. All payments create payment ledger entries.
10. **Returns & Refunds** — Online + POS + Exchanges. Reasons: `DAMAGED, WRONG_PRODUCT, CUSTOMER_RETURN, QUALITY_ISSUE`. Restores correct branch inventory.
11. **Exchange Management** — Product/variant replacement with amount adjustment.
12. **Wallet Integration** — Redemption, cashback, referral commission, future loyalty.
13. **Referral & Partner Integration** — Commission only after successful order completion.
14. **Delivery & Fulfillment Tracking** — Branch-aware. Future: delivery partner integration, live tracking, route optimization.
15. **Omnichannel Offers** — Channels: `ONLINE, POS, BOTH`. Product/cart/referral/branch/festival offers.
16. **Notifications** — Order, payment, dispatch, delivery, refund.
17. **Analytics & Reports** — Sales summary, channel/branch/product/payment-wise, returns/refunds, wallet, referral; omnichannel customer behavior, repeat purchase, LTV.
18. **Offline Sync** — Queue locally, preserve inventory integrity, branch mapping, invoice consistency.
19. **Security & Audit** — All commerce actions create audit trail.
20. **Future Wholesale** — Architecture ready for B2B/dealers/distributors/bulk pricing.

### Permissions
`SALES_VIEW, SALES_CREATE, SALES_RETURN, SALES_REFUND, SALES_EXPORT, ORDER_MANAGE, DELIVERY_MANAGE`

### Tables
`sales_orders(_items), sales_payments, sales_returns(_items), sales_refunds, sales_exchanges, sales_invoices, sales_channels, sales_status_logs, delivery_tracking, customer_sales_history, branch_payment_methods, payment_channel_configurations`

---

## MODULE 9 — CRM & Customer Management

**Central customer intelligence. One unified customer system across Online, POS, Referral, Manual, future Wholesale.**

### Submodules
1. **Central Customer Database** — One unified profile linking all sales channels. Mobile = primary unique identifier.
2. **Registration & Onboarding** — Serviceable pincode → auto-approve; non-serviceable → CRM + admin review. Statuses: `PENDING_SERVICEABILITY, ACTIVE, BLOCKED, INACTIVE`.
3. **Address Management** — Multiple addresses, history. Pincode drives serviceability/fulfillment/delivery rules. Future: GPS/map.
4. **Customer Segmentation** — `RETAIL, PREMIUM, PARTNER, WHOLESALE, FREQUENT_BUYER`. Enables targeted offers, loyalty, analytics.
5. **Referral Relationships** — Successful referrer auto-becomes Partner. Tracks referred customers, hierarchy (non-MLM), earnings, wallet commissions.
6. **Wallet Management** — Types: `REFERRAL_CREDIT, CASHBACK, ORDER_REDEMPTION, MANUAL_ADJUSTMENT`. Ledger-driven, never directly editable.
7. **Communication History** — SMS, Email, future WhatsApp, support.
8. **Notes & Internal Remarks** — Admin-only.
9. **Purchase History** — Online + POS + Returns + Exchanges + Wallet → 360° view.
10. **Loyalty Readiness** — Future `SILVER/GOLD/PLATINUM`. Schema future-ready Day 1.
11. **Customer Support** (future) — Tickets, chat, escalations.
12. **Notifications** — Registration, orders, wallet, referrals, campaigns.
13. **Analytics** — Acquisition, repeat rate, top customers, referral performance, LTV, AOV, retention; omnichannel behavior.
14. **Search & Lookup** — Fast by mobile/email/name/referral.
15. **Verification** — Mobile OTP, Email OTP, admin approval (special).
16. **Privacy & Security** — Audit logs, access control, data protection; permission-controlled.
17. **Activity Timeline** — Complete customer history.
18. **Future Wholesale CRM** — Dealers, distributors, B2B accounts, business pricing.

### Permissions
`CUSTOMER_VIEW, CUSTOMER_CREATE, CUSTOMER_EDIT, CUSTOMER_EXPORT, WALLET_ADJUST, CUSTOMER_COMMUNICATION`

### Tables
`customers, customer_addresses, customer_segments, customer_wallets, wallet_ledger, customer_referrals, customer_notes, customer_communications, customer_status_logs, customer_activity_logs, customer_serviceability_requests`

---

## MODULE 10 — Referral, Partner & Wallet Management

**Growth & incentive engine. Strictly Non-MLM: no binary structure, no levels, no chain income, no forced hierarchy. Any successful referring customer automatically becomes a Partner.**

### Flow
Customer Refers → Referred User Registers → Referred User Purchases → Order Completed Successfully → Commission Credited → Referrer becomes Partner.

### Submodules
1. **Referral Engine** — Sources: `CUSTOMER, PARTNER, ADMIN, CAMPAIGN`. Methods: code, link, mobile, admin tagging. Each customer gets unique referral code/link. Relationship permanent & auditable.
2. **Automatic Partner Conversion** — Once referral succeeds (referred customer completes order). Statuses: `PENDING, ACTIVE, BLOCKED, INACTIVE`. No manual activation needed initially.
3. **Partner Profile** — Partner ID, referral code, referred customers, wallet balance, earnings history. Linked to customer profile.
4. **Commission Engine** — Configurable. Types: `FIXED, PERCENTAGE`. Scope: product, category, order value, campaign. Examples: 5% on Ghee orders; ₹100 on first referral. Rule-driven.
5. **Commission Trigger** — Only after successful order completion (future: after return window). Prevents fake referrals and cancelled-order abuse.
6. **Wallet** — All commissions first credit to wallet. Uses: future payouts, order redemption, cashback, referral earnings. Types: `REFERRAL_COMMISSION, CASHBACK, ORDER_REDEMPTION, MANUAL_ADJUSTMENT, PAYOUT_DEDUCTION`. **Ledger-driven; never directly editable.**
7. **Wallet Ledger** — Type, ref ID, amount, before/after balance, timestamp, remarks. Audit trail on every change.
8. **Wallet Redemption** — Online/POS/partial. Configurable: minimum order required, max wallet usage %.
9. **Future Payouts** — Initially commissions stay in wallet. Future: bank/UPI payouts, requests, approval workflows. Statuses: `PENDING, APPROVED, PAID, FAILED`.
10. **Referral Analytics** — Top referrers, conversion, liabilities, sales, ROI.
11. **Campaign-Based Referrals** — Festive bonuses (e.g. Diwali → Double rewards), category-based.
12. **Validation Rules** — Self-referral blocked, duplicate prevention, fraud detection.
13. **Visibility** — Admin views referrer→referred mapping, performance, liabilities.
14. **Notifications** — Referral success, wallet credit, payouts, campaigns.
15. **Security & Audit** — Commission, wallet, payout, fraud tracking.
16. **Future Loyalty Integration**.

### Permissions
`REFERRAL_VIEW, REFERRAL_CONFIGURE, WALLET_VIEW, WALLET_ADJUST, PAYOUT_APPROVE, PARTNER_MANAGE`

### Tables
`partners, partner_referrals, referral_rules, wallets, wallet_ledger, commission_transactions, partner_status_logs, referral_campaigns, future_payout_requests`

---

## MODULE 11 — Notifications & Communication Management

**Central communication engine. All modules trigger notifications through one unified, event-driven, template-based system.**

### Channels
`SMS, EMAIL, WHATSAPP, PUSH_NOTIFICATION, IN_APP`

### Submodules
1. **Central Engine** — Triggers from order placed, payment success, OTP, wallet credit, referral success, low stock, etc.
2. **OTP Management** — Mobile/Email OTP. Channel configurable from Super Admin. Smart: if both mobile & email exist and admin configured email OTP → use email. Expiry, resend, retry limit, rate limit. Auditable.
3. **SMS** — Transactional + OTP (separate from promotional). Future: campaigns.
4. **Email** — OTP, invoices, orders, wallet, reports. Future: newsletters, journeys.
5. **WhatsApp** (future-ready) — Order updates, OTP, wallet, delivery. Plan for WhatsApp Business API.
6. **Push** (future) — App alerts, offers, reminders.
7. **In-App** — Dashboard alerts (low stock, pending approval, new referral, new order).
8. **Templates** — Types: SMS/Email/WhatsApp/Push. Dynamic vars (`{CUSTOMER_NAME}, {ORDER_ID}, {OTP}, {WALLET_AMOUNT}`). Multi-language ready, versioned, activatable. Admin-editable.
9. **Event-Driven Triggers** — Decoupled from business logic.
10. **Communication Logs** — Recipient, channel, template, status, sent time, delivery status.
11. **Retry & Failure** — Queue-based, retry queue, future provider failover.
12. **Campaign Messaging** (future) — Festive, referral, launches. Opt-in/opt-out required.
13. **Customer Preferences** — Channel-wise consent.
14. **Internal Admin Notifications** — Low stock, refund approvals, non-serviceable requests, payout approvals, failed sync.
15. **Scheduling** (future).
16. **Multi-language** — English, Hindi, Marathi.
17. **Security & Compliance** — Sensitive comms secure & auditable.
18. **Analytics** — Delivery, open, click rate (future), campaign performance, OTP success.

### Permissions
`NOTIFICATION_VIEW, NOTIFICATION_SEND, TEMPLATE_MANAGE, CAMPAIGN_MANAGE, OTP_CONFIGURATION, COMMUNICATION_REPORTS`

### Tables
`notification_templates, notification_logs, otp_logs, communication_preferences, notification_queues, campaigns, campaign_recipients, admin_notifications`

---

## MODULE 12 — Finance, Accounts & Ledger Management

**Financial control & accounting engine. Ledger-driven; every financial transaction creates a ledger impact. Integrates with purchases, inventory, sales, wallet, payments, returns, referrals, expenses.**

### Submodules
1. **Chart of Accounts** — Types: `ASSET, LIABILITY, INCOME, EXPENSE, EQUITY`. Configurable.
2. **Ledger Management** — Every transaction creates ledger entries (debit/credit accounts, amount, branch, ref, timestamp, narration). Immutable & auditable.
3. **Customer Ledger** — Purchases, refunds, wallet usage; future outstanding for credit/B2B.
4. **Vendor Ledger** — Purchases, payments, outstanding, returns. Integrates with purchase module.
5. **Branch-wise Accounting** — Branch sales/expenses/profitability/collections.
6. **Payment Accounting** — Cash/UPI/Cards/COD/Wallet. Branch-configurable. Every payment hits ledger.
7. **Wallet Accounting** — Wallet is **company liability** until redeemed/paid out. Examples: Referral Credit → Dr Referral Expense / Cr Wallet Liability. Never directly editable.
8. **Expense Management** — Categories: `RENT, SALARY, DELIVERY, MARKETING, UTILITY, MISCELLANEOUS`. Receipt upload, future approval workflow, branch-tagged.
9. **Tax & GST** — Calculations, breakup, summaries. Future: e-invoicing, GST returns, HSN codes, e-way bills.
10. **Profitability** — Branch/product/category/delivery profitability. Top products, most profitable branch, high expense zones.
11. **Cash & Bank** — Balances, deposits, withdrawals, transfers; future reconciliation & auto statement import.
12. **Refund & Return Accounting** — Affects inventory + sales + accounting + tax.
13. **Referral Accounting** — Commission liabilities, wallet credits, future payout accounting.
14. **Financial Reports** — P&L, Balance Sheet, Cash Flow, Trial Balance, Sales Register, Purchase Register, GST, Expenses, Branch Profitability, Wallet Liability; omnichannel revenue analytics.
15. **Audit & Logs** — Immutable, auditable.
16. **Adjustments** — Correction entries, journal entries, reversals; require permissions, remarks, audit logs.
17. **Future Accounting Integration** — Tally, Zoho Books, ERP exports, CA reporting.
18. **Future Credit System** — Customer/vendor/dealer credit limits; receivable/payable schema ready.

### Permissions
`FINANCE_VIEW, LEDGER_VIEW, EXPENSE_MANAGE, PAYMENT_VIEW, PAYMENT_ADJUST, FINANCIAL_REPORTS, JOURNAL_ENTRY`

### Tables
`chart_of_accounts, ledger_entries, customer_ledgers, vendor_ledgers, wallet_ledgers, branch_accounts, expenses, expense_categories, tax_configurations, financial_adjustments, bank_accounts, cash_accounts, financial_reports`

---

## MODULE 13 — Reports, Analytics & Business Intelligence

**Real-time, actionable, branch-aware. Integrates across sales, inventory, finance, CRM, referrals, fulfillment, procurement, operations.**

### Submodules
1. **Role-based Dashboards** — Super Admin (Global), Branch Manager (Branch Ops), Purchase Team (Procurement), Finance (Financial), POS Cashier (Daily Sales), Partner (Referral Earnings). KPI cards, charts, alerts, pending actions.
2. **Sales Analytics** — Daily/monthly/channel/branch/product; omnichannel revenue analysis.
3. **Inventory Analytics** — Current stock, aging, low stock, valuation, branch summary; smarter procurement planning.
4. **Purchase Analytics** — Vendor-wise, trends, outstanding, returns; procurement efficiency.
5. **Financial Analytics** — P&L, expenses, cash flow, branch profitability, wallet liability.
6. **CRM/Customer Analytics** — Top customers, repeat, retention, AOV; omnichannel behavior.
7. **Referral & Partner Analytics** — Top referrers, conversion, commissions, partner earnings. Non-MLM structured.
8. **Delivery & Fulfillment Analytics** — Pincode-wise, delivery cost, fulfillment efficiency, branch load.
9. **Wallet & Incentive Analytics** — Balance summary, commission liability, usage.
10. **Operational Alerts & Insights** — Low stock, pending approvals, failed sync, unusual activity.
11. **Branch-wise Analytics** — All major analytics remain branch-aware.
12. **Export & Download** — Excel, PDF, CSV with filters (date, branch, category, customer, payment mode, channel).
13. **Scheduled Reports** (future) — Daily/weekly/monthly emailed summaries.
14. **Predictive Analytics** (future) — Demand forecasting, stock prediction, smart reordering, recommendations.
15. **KPI Tracking** — Revenue growth, inventory turnover, AOV, retention.
16. **Audit & Data Integrity** — Stock mismatches, failed syncs, unusual refunds, manual adjustments.
17. **Real-time Readiness** — Live dashboards, POS monitoring.
18. **Mobile Dashboard Readiness**.
19. **Multi-channel Analytics** — Online, POS, future wholesale/distributor.

### Permissions
`REPORTS_VIEW, ANALYTICS_VIEW, FINANCIAL_REPORTS, EXPORT_REPORTS, DASHBOARD_MANAGE, KPI_VIEW`

### Tables
`dashboard_configurations, analytics_snapshots, scheduled_reports, report_exports, kpi_definitions, branch_kpis, analytics_alerts`

---

## MODULE 14 — Delivery, Logistics & Fulfillment Management

**Fulfillment & logistics control engine. Branch-aware + pincode-aware.**

### Submodules
1. **Fulfillment Engine** — Flow: Order → Fulfillment Branch Selection → Reservation → Picking → Packing → Dispatch → Delivery. Branch-scoped.
2. **Intelligent Branch Selection** — Priority: Nearest Branch → Mapped Fulfillment Branch → Warehouse → HO. Per-branch `online_fulfillment_enabled` flag.
3. **Pincode-based Routing** — Zones: `STANDARD, EXTENDED, PREMIUM_SPECIAL, NON_SERVICEABLE`. Pincode controls fulfillment branch, delivery fee, MOV, ETA, payment methods.
4. **Picking** — Picklist gen, inventory validation, status tracking.
5. **Packing** — `PENDING → PACKING → PACKED → FAILED`. Required before dispatch.
6. **Dispatch** — Creation, assignment, scheduling. Branch-linked.
7. **Delivery Status** — `PENDING → PACKED → DISPATCHED → OUT_FOR_DELIVERY → DELIVERED` (+ FAILED/RETURNED/CANCELLED). Audit trail.
8. **Delivery Charges** — Pincode-based; depends on zone/branch/order value/delivery type.
9. **Delivery Partner Integration** (future) — Dunzo, Porter, Shiprocket, local partners.
10. **Hyperlocal Delivery** — Same-day, local branch dispatch, hyperlocal routing. Types: `STANDARD, SAME_DAY, EXPRESS, STORE_PICKUP`.
11. **Delivery Personnel** (future) — Assignment, tracking, performance, delivery agent app, OTP confirmation, GPS.
12. **Store Pickup / Click & Collect** (future) — Reduces delivery costs.
13. **Failed Delivery Handling** — Reasons: `CUSTOMER_UNAVAILABLE, WRONG_ADDRESS, PAYMENT_ISSUE`. Trackable, auditable.
14. **Return-to-Origin (RTO)** (future).
15. **Logistics Cost Tracking** — Cost per delivery, pincode profitability, branch logistics expense.
16. **Fulfillment Notifications** — Packing, dispatch, delivery.
17. **Fulfillment Analytics** — Speed, packing efficiency, branch dispatch load, success rate, avg delivery time.
18. **Offline Fulfillment Readiness**.
19. **Security & Audit**.

### Permissions
`FULFILLMENT_VIEW, FULFILLMENT_PROCESS, DISPATCH_MANAGE, DELIVERY_TRACK, PICKLIST_MANAGE, DELIVERY_REPORTS`

### Tables
`fulfillment_orders, picklists, packing_logs, dispatches, delivery_tracking, delivery_zones, delivery_charges, delivery_failures, delivery_agents, logistics_costs`

---

## MODULE 15 — Returns, Damages & Quality Control Management

**Inventory recovery & quality assurance. Returned/damaged inventory NEVER directly merges into sellable stock without validation.**

### Submodules
1. **Sales Return** — Online, POS, partial, full. Flow: Request → Validation → Approval → Inspection → Inventory Decision → Refund/Replacement. Types: `REFUND, REPLACEMENT, EXCHANGE`. Branch-aware.
2. **Purchase Return** — Vendor returns, damaged, rejected; linked to original purchase transaction.
3. **Damaged Stock** — Sources: `PURCHASE_DAMAGE, WAREHOUSE_DAMAGE, DELIVERY_DAMAGE, CUSTOMER_RETURN_DAMAGE`. Moves to separate damage inventory; never sellable.
4. **Expiry Management** — Batch & expiry tracking; near-expiry & expired alerts; expired auto-blocks selling.
5. **QC Workflow** — Statuses: `PENDING_QC, PASSED, FAILED, QUARANTINED`. Outcomes: `RESTOCK, DAMAGE, RETURN_TO_VENDOR, DISPOSE`. Only QC-approved returns to sellable.
6. **Inventory Quarantine** — Reasons: `QC_PENDING, DAMAGED, EXPIRED, SUSPECTED_DEFECT`. Isolated.
7. **Reverse Logistics** — Customer pickup returns, branch handling, vendor returns; future delivery partner reverse pickup, RTO.
8. **Replacement Workflow** — Linked transaction history.
9. **Inventory Adjustments** — Stock correction, damage, expiry. Permission + remarks + audit. Negative stock strictly prohibited.
10. **Refund Integration** — Methods: `ORIGINAL_PAYMENT, WALLET, STORE_CREDIT`. Traceable & auditable.
11. **Branch-wise Return Handling** — Restores correct branch inventory.
12. **Damage & Loss Analytics** — Damage %, return trends, expiry losses, branch damage rates.
13. **Expiry & Batch Analytics** — Near-expiry, batch performance, expiry losses.
14. **QC Audit & Traceability**.
15. **Disposal Management** — Reasons: `EXPIRED, DAMAGED, LEAKAGE, UNSELLABLE`. Financially traceable.
16. **Recall Management Readiness** (future) — Product/batch/safety recalls.
17. **Notifications** — Expiry, QC pending, return approval, damage.
18. **Security & Audit**.

### Permissions
`RETURN_APPROVE, QC_MANAGE, DAMAGE_MANAGE, EXPIRY_MANAGE, INVENTORY_ADJUST, DISPOSAL_APPROVE`

### Tables
`sales_returns, purchase_returns, damage_inventory, inventory_quarantine, batch_tracking, expiry_tracking, qc_inspections, replacement_orders, inventory_adjustments, disposal_logs`

---

## MODULE 16 — HR, Staff, Attendance & Payroll Management

**Workforce, attendance & payroll engine. Role-based + branch-aware + attendance-linked + permission-controlled. Payroll is included in Phase 1.**

### Submodules
1. **Employee Management** — Centralized profile (empId, name, mobile, email, branch, designation, dept, reporting manager, joining date, status). Statuses: `ACTIVE, INACTIVE, ON_LEAVE, TERMINATED`. Linked to user account.
2. **Branch-wise Staff Allocation** — Employees mapped to branches.
3. **Attendance Management** — Methods: `APPLICATION_PUNCH, BIOMETRIC, GPS_MOBILE, MANUAL_ADMIN, HYBRID`. Configurable from Super Admin. Branch-wise method allowed (e.g. Pune Biometric / Warehouse App / Delivery GPS). Biometric vendor-independent (ZKTeco, eSSL, API-based).
   - **Login attendance check**: If employee hasn't punched in → system shows popup with `[Punch In Now]` / `[Remind Later]`.
4. **Shift Management** — Types: `MORNING, EVENING, FULL_DAY, CUSTOM`. POS integration: Punch In → Cashier Shift Open → Billing Enabled. Optionally require attendance before POS billing.
5. **Leave Management** — Types: `CASUAL, SICK, PAID, UNPAID`. Workflow: Request → Manager Approval → Applied. Permission-controlled.
6. **Department & Role Mapping** — `SALES, PURCHASE, WAREHOUSE, FINANCE, OPERATIONS, ADMIN`.
7. **Employee Activity Tracking** — Login, approvals, inventory, billing, payroll. Critical actions create audit trail.
8. **Payroll Management (Phase 1)** — Salary structures, attendance-linked, incentives, deductions, processing, approvals, payslip generation. Components: `BASIC, HRA, ALLOWANCE, INCENTIVE, BONUS, DEDUCTION`. Structures employee-specific.
9. **Attendance-linked Payroll** — Integrates attendance, leave, shifts (e.g. 2 unpaid leaves → deduction).
10. **Payroll Processing** — Flow: Attendance Finalized → Payroll Generated → Review → Approval → Payslip Generated. Statuses: `DRAFT, PROCESSING, APPROVED, PAID`.
11. **Payslip Generation** — PDF/Print/Email. Employee details, attendance summary, salary breakup, incentives, deductions, net payable. Employee-accessible.
12. **Incentives & Bonus** — Sales, performance, attendance, future referral.
13. **Salary Deductions** — Types: `UNPAID_LEAVE, ADVANCE, PENALTY, OTHER`. Remarks + audit.
14. **Payroll Accounting Integration** — Salary Expense Dr / Salary Payable Cr; on payment: Salary Payable Dr / Bank Cr. Auto-entries.
15. **Employee Dashboard** — Attendance, salary history, payslips, deductions; future reimbursements, tax declarations.
16. **HR Reports** — Attendance, payroll summary, leave, branch staff, shift performance; trends, overtime, productivity, payroll expenses.
17. **Security & Audit** — Salary & HR data highly permission-controlled.
18. **Future Readiness** — PF, ESIC, TDS, GPS attendance, field staff, compliance.

### Permissions
`EMPLOYEE_VIEW/MANAGE, ATTENDANCE_MANAGE, SHIFT_MANAGE, LEAVE_APPROVE, PAYROLL_VIEW/PROCESS/APPROVE, PAYSLIP_GENERATE, HR_REPORTS`

### Tables
`employees, employee_branches, attendance_logs, attendance_configurations, attendance_devices, biometric_sync_logs, shift_assignments, leave_requests, salary_structures, payroll_cycles, employee_payroll, payroll_items, payslips, employee_activity_logs`

---

## MODULE 17 — Document, Media & File Management

**Central digital asset & document engine. All files centralized, secure, linked to entities/transactions, auditable.**

### Submodules
1. **Central Storage** — Types: `IMAGE, PDF, EXCEL, CSV, DOCUMENT, ZIP`. Files never orphaned; always linked (Product→Images, Invoice→PDF, Employee→Documents, Vendor→Agreements).
2. **Product Media** — Multiple images, variant-wise, sorting, default. Types: `THUMBNAIL, GALLERY, BANNER, VARIANT_IMAGE`. Web & mobile optimized.
3. **Invoice & Document Storage** — Sales/purchase invoices, return docs, payslips, reports. Permanently linked to transactions.
4. **Employee Documents** — ID proofs, agreements, joining docs, certifications. Access-controlled. Future: expiry/renewal alerts.
5. **Vendor & Customer Attachments** — Agreements, GST, KYC, contracts; entity-linked, permission-controlled.
6. **Report Export** — PDF, Excel, CSV; downloadable & traceable.
7. **Media Optimization** — Auto compression, thumbnails, responsive.
8. **File Access Control** — Role/permission/ownership/branch-based (HR docs → HR/Admin only).
9. **File Versioning** (future) — History, rollback (e.g. Agreement v1 / v2).
10. **File Audit & Tracking** — Uploaded/modified by, download/access history.
11. **Storage Structure** — Module-organized folders (`products/, employees/, vendors/, sales/, reports/, payroll/`).
12. **Cloud Readiness** — AWS S3, GCS, Azure, local. Storage-provider-independent.
13. **Media Security** — Secure URLs, protected downloads, future signed URLs.
14. **Bulk Upload** — Product images, document imports, Excel imports; future drag-and-drop, zip extraction.
15. **Generated File Automation** — Auto invoices/payslips/exports, auto-linked to source.
16. **Media Analytics** (future) — Storage usage, upload activity, downloads.
17. **Backup & Recovery** — Automated backups, disaster recovery, redundancy.
18. **OCR & AI Readiness** (future) — Invoice OCR, auto GST extraction, AI classification.
19. **Notifications** — Expiry, upload failure, storage warnings.
20. **Security & Compliance**.

### Permissions
`FILE_UPLOAD, FILE_DOWNLOAD, FILE_DELETE, MEDIA_MANAGE, DOCUMENT_VIEW, REPORT_EXPORT`

### Tables
`files, file_categories, file_versions, file_access_logs, media_assets, document_links, generated_reports, storage_configurations`

---

## MODULE 18 — System Settings, Configuration & Automation Management

**Central control engine. Configurable, not hardcoded. Global defaults + branch overrides + role-based control.**

### Submodules
1. **Global Settings** — Company, currency, timezone, tax, invoice prefix, default language.
2. **Branch-wise Configuration** — Payment methods, fulfillment enablement, attendance methods, pricing policies, POS config, invoice series. Independent per branch.
3. **Feature Toggles** — Wallet, Referral, Online Ordering, Payroll enable/disable; beta features.
4. **Payment Configuration** — Branch-configurable methods; visibility depends on branch + channel + config.
5. **Attendance Configuration** — App/Biometric/GPS/Hybrid; configurable from Super Admin; may vary by branch.
6. **Automation Rules Engine** — Low stock alerts, auto wallet credit, order status notifications, attendance reminders. Rule-driven.
7. **Scheduler & Cron** — Night inventory sync, daily sales reports, payroll reminders. Centrally managed.
8. **Approval Workflow Configuration** — Leave, payroll, refunds (>₹5000 → Manager Approval), inventory adjustments.
9. **Notification Configuration** — Providers (SMS/Email/WhatsApp), OTP expiry, retries.
10. **Inventory Configuration** — Negative stock permanently disabled; reorder alerts, reservation, branch transfer policies.
11. **POS Configuration** — Barcode enablement (optional), offline mode, invoice printing, cashier restrictions. May be branch-specific.
12. **Online Store Configuration** — Delivery rules, pincode settings, MOV (e.g. Extended zone ₹1500), serviceability rules.
13. **Referral & Wallet Configuration** — Commission rules, wallet limits, payout policies, campaigns. Non-MLM.
14. **Finance & Accounting Configuration** — Ledger, tax, invoice sequences, branch rules.
15. **Security & Session Configuration** — Password policies, session timeout (e.g. 30 min), login & device restrictions.
16. **Audit & System Logs** — Critical config changes audit-tracked.
17. **Multi-language & Localization** — English, Hindi, Marathi.
18. **Backup & Recovery Configuration** — Automated backups & schedules.
19. **API & Integration Configuration** — Payment gateways, delivery APIs, biometric APIs, accounting integrations.
20. **Future AI & Smart Automation** — AI alerts, predictive automation, smart reorder, AI analytics.

### Permissions
`SYSTEM_SETTINGS_MANAGE, AUTOMATION_MANAGE, BRANCH_CONFIGURATION, PAYMENT_CONFIGURATION, SECURITY_CONFIGURATION, FEATURE_TOGGLE_MANAGE`

### Tables
`system_settings, branch_configurations, feature_toggles, automation_rules, scheduler_jobs, approval_workflows, payment_configurations, attendance_configurations, notification_configurations, security_configurations, audit_logs`

---

## MODULE 19 — Super Admin, Security & Audit Control Management

**Enterprise governance & security engine. Every critical action is permission-controlled + auditable + traceable.**

### Submodules
1. **Super Admin Panel** — Centralized enterprise control: global config, branch management, feature toggles, security, audit, operational overrides. All Super Admin actions fully auditable.
2. **RBAC** — Permission-based, not just role-name (e.g. `INVENTORY_VIEW, PAYROLL_APPROVE, REFUND_APPROVE, SYSTEM_SETTINGS_MANAGE`). Granular & scalable.
3. **Permission Audit** — Tracks permission changes, role assignments, access escalations.
4. **Audit Logging** — Immutable logs for inventory adjustments, refunds, payroll approvals, wallet adjustments, system settings, logins. Fields: user, action, timestamp, IP, branch, device, remarks. Tamper-resistant.
5. **Login & Session Security** — Timeout (e.g. 30 min), device tracking, concurrent session control (e.g. max 1), suspicious login detection.
6. **Device Management** — Authorized devices, branch device mapping, POS terminal restrictions (e.g. POS billing only from registered devices).
7. **Branch-wise Security** — Branch-specific access, restrictions, device policies. Data visibility branch-aware.
8. **Financial Security** — Refund approval hierarchy (e.g. >₹5000 → Manager mandatory), wallet adjustment restrictions, payroll approval controls.
9. **Inventory Security** — Stock adjustment approvals, transfer approvals, audit monitoring.
10. **HR & Payroll Security** — Salary access control, payroll approval restrictions, attendance audit.
11. **POS Security** — Cashier shift validation, refund restrictions, offline sync audit; operator-traceable.
12. **Fraud Prevention** — Suspicious activity alerts, unusual refund monitoring, duplicate transaction detection.
13. **OTP & Verification Security** — Retry limits (e.g. max 5), brute-force prevention, throttling.
14. **API & Integration Security** — Auth, token management, webhook validation.
15. **Data Access Governance** — Restricted exports, sensitive data masking, download permissions.
16. **Operational Monitoring Dashboard** — Active sessions, failed logins, audit alerts, system health.
17. **Backup & Disaster Recovery Governance**.
18. **Compliance Readiness** — GST, HR, financial audit-ready.
19. **MFA Readiness** (future) — OTP MFA, authenticator apps, biometric, trusted device verification.
20. **Security Analytics** — Failed logins, suspicious access, approval anomalies, incidents.

### Permissions
`SUPER_ADMIN, AUDIT_VIEW, SECURITY_MANAGE, SESSION_MONITOR, PERMISSION_MANAGE, DEVICE_MANAGE`

### Tables
`audit_logs, user_sessions, device_registrations, permission_audits, security_events, failed_login_attempts, otp_security_logs, system_health_logs, approval_audit_logs`

---

## MODULE 20 — Mobile App, Offline Sync & API Integration Management

**Digital connectivity & mobility engine. Mobile-ready + offline-capable + API-driven. System must work during unstable internet, branch connectivity issues, mobile interruptions.**

### Submodules
1. **Mobile App Architecture** — Multi-app ecosystem: Customer App, POS App, future Delivery/Partner/Admin apps. API-first.
2. **Offline-first Architecture** — Critical operations support offline: POS Billing, Attendance Punch, Inventory Lookup, Customer Lookup.
3. **Central Sync Engine** — Offline Action → Local Queue → Internet → Background Sync. Conflict-aware.
4. **Offline Inventory Consistency** — Locally controlled to prevent overselling (Local Stock 5 + Offline Sale 5 → Next billing blocked). Negative stock strictly prohibited.
5. **Offline POS Support** — Local invoice generation, sync queue, local product/inventory/customer caches.
6. **Offline Attendance** — Local punch, sync later.
7. **API Gateway** — Central API layer for web/mobile/POS/third-party.
8. **Auth & API Security** — Token auth, session validation, device authorization, rate limiting. Future: OAuth, API keys, webhook security.
9. **Third-party Integrations** — Razorpay, Shiprocket, ZKTeco, Tally, payment gateways, delivery partners, biometric, accounting, SMS/email providers. Modular.
10. **Push Notifications** — Order delivered, wallet credited, attendance reminders.
11. **Device Management** — Registration, trusted devices, branch mapping (POS device → branch linked). Critical ops device-restricted.
12. **Local Caching** — Product, inventory, customer, settings caches.
13. **Sync Conflict Resolution** — Timestamp + transaction priority logic.
14. **Background Sync Processing** — Auto sync, retry queue, failed sync recovery. Resilient & recoverable.
15. **API Monitoring** — Response time, sync failure rate, offline queue size.
16. **Mobile Performance Optimization** — Lightweight APIs, optimized media, cached requests. Low-bandwidth optimized.
17. **PWA Readiness** (future) — Installable web app, offline browser, push.
18. **IoT & Smart Device Readiness** (future) — Smart weighing scales, barcode scanners, IoT sensors.
19. **Backup & Recovery for Offline Devices** — Local backup, recovery sync, queue restoration.
20. **Security & Audit**.

### Permissions
`API_MANAGE, DEVICE_MANAGE, SYNC_MONITOR, OFFLINE_OVERRIDE, MOBILE_APP_MANAGE`

### Tables
`api_tokens, device_registrations, offline_sync_queue, sync_logs, mobile_sessions, api_request_logs, integration_configurations, offline_cache_metadata`

---

## Appendix A — Consolidated Status Flows

| Domain | Flow |
|---|---|
| Purchase Requisition | `DRAFT → SUBMITTED → APPROVED → PARTIALLY_PROCESSED → COMPLETED / REJECTED` |
| Purchase Order | `DRAFT → PENDING_APPROVAL → APPROVED → PARTIALLY_RECEIVED → COMPLETED / CANCELLED` |
| Stock Transfer | `PENDING → IN_TRANSIT → RECEIVED / CANCELLED` |
| Online Order | `PENDING → CONFIRMED → PACKED → SHIPPED → DELIVERED → COMPLETED` (+ CANCELLED/RETURNED/REFUNDED) |
| Sales Order (unified) | `PENDING → CONFIRMED → PROCESSING → PACKED → SHIPPED → DELIVERED → COMPLETED` (+ CANCELLED/RETURNED/REFUNDED/FAILED) |
| Delivery | `PENDING → PACKED → DISPATCHED → OUT_FOR_DELIVERY → DELIVERED` (+ FAILED/RETURNED/CANCELLED) |
| Packing | `PENDING → PACKING → PACKED / FAILED` |
| QC | `PENDING_QC → PASSED / FAILED / QUARANTINED` |
| Payroll | `DRAFT → PROCESSING → APPROVED → PAID` |
| Future Payout | `PENDING → APPROVED → PAID / FAILED` |
| Customer (CRM) | `PENDING_SERVICEABILITY → ACTIVE / BLOCKED / INACTIVE` |
| Vendor | `ACTIVE / INACTIVE / BLACKLISTED / ON_HOLD` |
| Partner | `PENDING → ACTIVE / BLOCKED / INACTIVE` |
| Employee | `ACTIVE / INACTIVE / ON_LEAVE / TERMINATED` |

---

## Appendix B — Inventory Movement Types

`PURCHASE, SALE, RETURN, TRANSFER_IN, TRANSFER_OUT, ADJUSTMENT, DAMAGE, INTERNAL_CONSUMPTION, OPENING_STOCK`
Future: `MANUFACTURING, ASSEMBLY, BUNDLE, SUBSCRIPTION_RESERVE`

---

## Appendix C — Channels & Offer Scope

- **Sales Channels**: `ONLINE, POS, WHOLESALE (future), MANUAL`
- **Offer Channels**: `ONLINE, POS, BOTH`
- **Payment Modes**: `CASH, UPI, CARD, BANK_TRANSFER, COD, WALLET, MIXED`
- **Communication Channels**: `SMS, EMAIL, WHATSAPP, PUSH_NOTIFICATION, IN_APP`
- **Attendance Methods**: `APPLICATION_PUNCH, BIOMETRIC, GPS_MOBILE, MANUAL_ADMIN, HYBRID`
- **Delivery Zones**: `STANDARD, EXTENDED, PREMIUM_SPECIAL, NON_SERVICEABLE`

---

## Appendix D — Phase 1 Inclusions (Explicit per SRS)

- Payroll is in Phase 1 (Module 16).
- Wallet is included; future payouts deferred (Module 10).
- Batch & Expiry: schema future-ready Day 1 (Module 5/15).
- Loyalty: schema future-ready Day 1 (Module 9).
- Branch-wise pricing: schema future-ready (Module 1).
- Multi-language: templates localization-ready Day 1 (Module 11).
- Cloud storage independence: Day 1 (Module 17).
- Finance-ready vendor ledger / receivable-payable schema: Day 1 (Modules 3, 12).
- Offline POS & attendance: Day 1 (Modules 7, 16, 20).

---

## Appendix E — Architectural Decisions to Carry into Implementation

1. Use a **single user table** with multi-role mapping.
2. Use a **ledger table per domain** (inventory, wallet, vendor, customer, accounting) — never mutate balances directly.
3. **Inventory updates only on GRN** for purchases; only on confirmed receipt for transfers.
4. **POS: hard-block** when local stock would go negative — including offline mode.
5. **Online inventory loads only after customer confirms location** (pincode).
6. **Branch-aware everything**: payments, fulfillment, pricing, reports, security, attendance, payroll.
7. **OTP destination is computed by the system**, not by the user input field.
8. **Soft delete** for all master records.
9. **Audit log table** with tamper-resistant entries for all critical actions.
10. **API-first** so mobile apps, POS, and integrations all consume the same contracts.
