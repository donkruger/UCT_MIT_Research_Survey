# Trading Sheet Specifications

## Overview

This document defines the data structure and validation requirements for Unit Trust trading sheets processed through the EasyEquities Accounts Processor API.

---

## Data Structure Requirements

### Required Fields

All trading sheets must contain exactly these 8 columns with precise naming:

| Field Name | Data Type | Description | Validation Rules |
|------------|-----------|-------------|------------------|
| **ShareCode** | String | Fund share code identifier | - 3-10 characters<br>- Example: `NGWINT` |
| **ContractCode** | String | Full contract identifier | - Format: `UT.ZA.{ShareCode}`<br>- Example: `UT.ZA.NGWINT` |
| **InstrumentID** | Integer | Numeric instrument identifier | - Positive integer<br>- Example: `4257` |
| **Units** | Decimal | Number of units to trade | - Positive decimal<br>- Up to 8 decimal places<br>- Example: `123.12345679` |
| **Amount** | Decimal | Trade amount in ZAR | - Positive numbers only<br>- Max 2 decimal places<br>- Example: `1000.12` |
| **Direction** | String | Trade direction | - Valid values: `BUY`, `SELL` only<br>- Case sensitive |
| **UserID** | Integer | User identifier | - Positive integer<br>- Example: `807686` |
| **TrustAccount** | Integer | Trust account number | - Positive integer<br>- Example: `123456` |

### Optional Fields

Additional fields that can be included for enhanced processing:

| Field Name | Data Type | Description | Default Value |
|------------|-----------|-------------|---------------|
| **Reference** | String | Client reference number | Auto-generated |
| **Notes** | String | Trade notes/comments | Empty |
| **Priority** | String | Processing priority | `NORMAL` |

---

## File Format Specifications

### Excel Files (.xlsx, .xls)

**Requirements:**
- First row must contain column headers
- Data starts from row 2
- No merged cells
- No formulas in data cells
- Maximum 10,000 rows per file

**Example Structure:**
```
| ShareCode | ContractCode   | InstrumentID | Units        | Amount  | Direction | UserID | TrustAccount |
|-----------|----------------|--------------|--------------|---------|-----------|--------|--------------|
| NGWINT    | UT.ZA.NGWINT   | 4257         | 123.12345679 | 1000.12 | BUY       | 807686 | 123456       |
| NGWINT    | UT.ZA.NGWINT   | 4257         | 123.12345679 | 1000.12 | SELL      | 807686 | 123456       |
```

### CSV Files (.csv)

**Requirements:**
- UTF-8 encoding
- Comma-delimited
- Headers in first row
- No quotes unless containing commas
- Line endings: `\n` or `\r\n`

**Example Format:**
```csv
ShareCode,ContractCode,InstrumentID,Units,Amount,Direction,UserID,TrustAccount
NGWINT,UT.ZA.NGWINT,4257,123.12345679,1000.12,BUY,807686,123456
NGWINT,UT.ZA.NGWINT,4257,123.12345679,1000.12,SELL,807686,123456
```

---

## Validation Rules

### Business Rules

1. **ShareCode Validation**
   - Must match approved fund list
   - 3-10 characters alphanumeric
   - Example: NGWINT, STXNDQ

2. **ContractCode Validation**
   - Must follow format: UT.ZA.{ShareCode}
   - Must be consistent with ShareCode
   - Example: UT.ZA.NGWINT

3. **InstrumentID Validation**
   - Must be positive integer
   - Must match instrument in system
   - Range: 1-999999

4. **Units Validation**
   - Must be positive decimal
   - Up to 8 decimal places allowed
   - Minimum: 0.00000001

5. **Amount Validation**
   - Must be positive decimal
   - Max 2 decimal places
   - Range: 0.01 - 10,000,000.00

6. **Direction Rules**
   - Valid values: `BUY` or `SELL` only
   - Case sensitive
   - **BUY**: Requires available cash balance
   - **SELL**: Requires sufficient fund holdings

7. **UserID Validation**
   - Must be positive integer
   - Must exist in user system
   - Associated with valid permissions

8. **TrustAccount Validation**
   - Must be positive integer
   - Account must exist and be active
   - Must be linked to UserID

### Data Quality Checks

1. **Duplicate Detection**
   - No duplicate rows (all fields identical)
   - Warning for similar trades (same account, fund, amount on same day)

2. **Completeness**
   - All required fields must be populated
   - No null or empty values in mandatory columns

3. **Format Consistency**
   - Consistent date format throughout file
   - Consistent decimal notation
   - No special characters in account numbers

---

## Approved Fund List

### Satrix Funds
| Fund Code | Fund Name | Min Investment |
|-----------|-----------|----------------|
| STXNDQ | Satrix MSCI World | R500 |
| STXRAM | Satrix RAFI 40 | R500 |
| STXMOM | Satrix Momentum | R500 |
| STXQUA | Satrix Quality SA | R500 |
| STXDIV | Satrix DIVI Plus | R500 |
| STX40 | Satrix 40 | R500 |
| STXSWX | Satrix SWIX 40 | R500 |

### Other Unit Trusts
| Fund Code | Fund Name | Min Investment |
|-----------|-----------|----------------|
| ASHEQF | Ashburton Equity | R1000 |
| COROP | Coronation Optimum Growth | R1000 |
| ABSA200 | ABSA Top 40 | R500 |
| SYGNIA | Sygnia Equity | R500 |

---

## Error Codes

### Validation Errors

| Code | Description | Resolution |
|------|-------------|------------|
| `VAL001` | Invalid ShareCode format | Check ShareCode against approved list |
| `VAL002` | ContractCode mismatch | ContractCode must be UT.ZA.{ShareCode} |
| `VAL003` | Invalid Direction value | Use only: BUY or SELL |
| `VAL004` | Negative or zero Units/Amount | Units and Amount must be positive |
| `VAL005` | Invalid InstrumentID | InstrumentID must be valid integer |
| `VAL006` | Missing required column | Ensure all 8 columns are present |
| `VAL007` | Invalid UserID | UserID must be valid integer |
| `VAL008` | Invalid TrustAccount | TrustAccount must be valid integer |

### Business Rule Errors

| Code | Description | Resolution |
|------|-------------|------------|
| `BUS001` | TrustAccount not found | Verify TrustAccount exists in system |
| `BUS002` | TrustAccount suspended | Contact account administration |
| `BUS003` | Insufficient balance | Check available cash for BUY direction |
| `BUS004` | Insufficient holdings | Verify fund holdings for SELL direction |
| `BUS005` | UserID permission error | User not authorized for this TrustAccount |
| `BUS006` | InstrumentID mismatch | Instrument doesn't match ShareCode |
| `BUS007` | Units/Amount mismatch | Units and Amount values inconsistent |

### System Errors

| Code | Description | Resolution |
|------|-------------|------------|
| `SYS001` | File too large | Maximum file size is 10MB |
| `SYS002` | Unsupported format | Use .xlsx, .xls, or .csv only |
| `SYS003` | API timeout | Retry submission |
| `SYS004` | API unavailable | Contact support team |

---

## Processing Notes

### Execution Order
- Trades are processed in the order they appear in the file
- SELL trades are processed before BUY trades for same account
- SWITCH trades are processed last

### Cut-off Times
- Same-day processing: Before 14:00 SAST
- Next-day processing: After 14:00 SAST
- Weekend/holiday uploads: Processed next business day

### Confirmation
- Email confirmation sent upon successful upload
- Reference number provided for tracking
- Execution report available within 24 hours

---

## Support

For assistance with trading sheet formats or validation errors:

**Trading Operations Team**
- Email: trading@easyequities.co.za
- Phone: Available during market hours
- Include: Error codes, sample data, and timestamps
