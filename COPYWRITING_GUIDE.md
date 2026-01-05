# Campaign Copywriting Consistency Guide

This guide documents the copywriting standards for all campaign configurations to ensure consistency across the user experience.

## Core Principles

1. **Brand-Consistent**: Use official product names (e.g., "scan & pay" not "QR payment")
2. **Action-Oriented**: Tell users what to do, not just what they'll get
3. **Context-Specific**: Match terminology to where the user sees it
4. **Concise**: Keep copy short and punchy

## Terminology Standards

### SCAN_HOMEPAGE_CONFIG (Scan & Pay Home Screen)

**Context**: User is on the Scan & Pay home screen, about to scan QR codes at merchants.

**Initial State (_0):**
- Format: `"assured cashback of ₹{total} on next {count} payments"`
- Example: `"assured cashback of ₹30 on next 3 payments"`
- Reasoning: Generic intro, doesn't need to be specific yet
- Applies to: All campaign types (SNP, UPI, P2P)

**In-Progress State (_1_X):**
- **SNP campaigns**: `"assured ₹{per_txn} cashback on next scan & pay"`
  - Example: `"assured ₹10 cashback on next scan & pay"`
  - Reasoning: Brand-consistent, specific to scan & pay action
- **UPI campaigns**: `"assured ₹{per_txn} cashback on next UPI payment"`
  - Example: `"assured ₹10 cashback on next UPI payment"`
  - Reasoning: UPI covers both scan & pay AND P2P, so use generic "UPI payment"
- **P2P campaigns**: `"assured ₹{per_txn} cashback on next UPI payment"`
  - Example: `"assured ₹10 cashback on next UPI payment"`
  - Reasoning: Generic, covers all payment types

**Single Transaction:**
- Same logic as in-progress state
- SNP → "scan & pay"
- UPI/P2P → "UPI payment"

### PTP_STREAK_CONFIG (P2P Home Screen)

**Context**: User is on the P2P (peer-to-peer) home screen, about to pay contacts.

**Initial State (_0):**
- Format: `"assured ₹{total} cashback on {count} UPI payments"`
- Example: `"assured ₹30 cashback on 5 UPI payments"`
- Reasoning: Generic, includes payment type for clarity

**In-Progress State (_1_X):**
- Format: `"assured ₹{per_txn} cashback on next UPI payment"`
- Example: `"assured ₹10 cashback on next UPI payment"`
- Reasoning: Consistent with scan & pay pattern, uses "UPI payment" for P2P context

## Why These Choices?

### Campaign-Type Aware Copy

**SCAN_HOMEPAGE_CONFIG:**
- **SNP**: "scan & pay" - Specific, brand-consistent
- **UPI**: "UPI payment" - Generic, covers both scan & P2P flows
- **P2P**: "UPI payment" - Generic, appropriate for P2P context

**PTP_STREAK_CONFIG:**
- Always "UPI payment" - Appropriate for P2P/contact payment context
- "scan & pay" would NOT make sense here

### Why "scan & pay" for SNP only?
- ✅ SNP campaigns are exclusively for scanning QR codes
- ✅ Matches your official product name
- ✅ More specific than generic "UPI payment"
- ✅ Clear action for the user

### Why "UPI payment" for UPI campaigns?
- ✅ UPI campaigns include BOTH scan & pay AND P2P transactions
- ✅ "scan & pay" would be too restrictive (user might do P2P)
- ✅ Generic enough to cover all eligible payment types
- ✅ Consistent across both home screens

### Initial State = Generic, In-Progress = Specific
- **Initial**: User just enrolled, show big picture ("3 payments")
- **In-Progress**: User already started, drive next action ("next scan & pay")

## Pattern Summary

| Config | Campaign Type | State | Pattern |
|--------|---------------|-------|---------|
| SCAN_HOMEPAGE_CONFIG | SNP | Initial (_0) | "₹{total} on next {count} payments" |
| SCAN_HOMEPAGE_CONFIG | SNP | In-Progress (_1_X) | "₹{per_txn} on next **scan & pay**" |
| SCAN_HOMEPAGE_CONFIG | SNP | Single | "₹{amount} on next **scan & pay**" |
| SCAN_HOMEPAGE_CONFIG | UPI | Initial (_0) | "₹{total} on next {count} payments" |
| SCAN_HOMEPAGE_CONFIG | UPI | In-Progress (_1_X) | "₹{per_txn} on next **UPI payment**" |
| SCAN_HOMEPAGE_CONFIG | UPI | Single | "₹{amount} on next **UPI payment**" |
| SCAN_HOMEPAGE_CONFIG | P2P | Initial (_0) | "₹{total} on next {count} payments" |
| SCAN_HOMEPAGE_CONFIG | P2P | In-Progress (_1_X) | "₹{per_txn} on next **UPI payment**" |
| SCAN_HOMEPAGE_CONFIG | P2P | Single | "₹{amount} on next **UPI payment**" |
| PTP_STREAK_CONFIG | UPI | Initial (_0) | "₹{total} on {count} **UPI payments**" |
| PTP_STREAK_CONFIG | UPI | In-Progress (_1_X) | "₹{per_txn} on next **UPI payment**" |
| PTP_STREAK_CONFIG | P2P | Initial (_0) | "₹{total} on {count} **UPI payments**" |
| PTP_STREAK_CONFIG | P2P | In-Progress (_1_X) | "₹{per_txn} on next **UPI payment**" |

## Implementation

These patterns are implemented in:
- `/scripts/process_scan_homepage_config.py` (lines 138, 177, 210, 244)
  - Uses campaign_type to determine: SNP → "scan & pay", UPI/P2P → "UPI payment"
- `/scripts/process_ptp_streak_config.py` (lines 155, 222)
  - Always uses "UPI payment" (appropriate for P2P context)

## Future Campaigns

When creating new campaign templates or modifying existing ones:
1. SCAN_HOMEPAGE_CONFIG: Use "scan & pay" ONLY for SNP campaigns
2. SCAN_HOMEPAGE_CONFIG: Use "UPI payment" for UPI and P2P campaigns
3. PTP_STREAK_CONFIG: Always use "UPI payment"
4. Keep initial state generic, in-progress state specific
5. Update this guide if new patterns are needed

## Revision History

- 2026-01-03: Created guide
- 2026-01-03: Made copywriting campaign-type aware (SNP uses "scan & pay", UPI/P2P use "UPI payment")
