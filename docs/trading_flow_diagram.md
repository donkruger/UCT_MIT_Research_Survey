# Trading Sheet Upload System - Flow Diagrams

## System Overview

```mermaid
graph TD
    %% User Journey
    START[User Access] --> AUTH[Declaration & Acceptance]
    AUTH --> CHECK{Declaration<br/>Accepted?}
    CHECK -->|No| AUTH
    CHECK -->|Yes| UPLOAD[Trading Sheet Upload]
    
    UPLOAD --> VALIDATE{File<br/>Valid?}
    VALIDATE -->|No| ERROR1[Show Error]
    ERROR1 --> UPLOAD
    VALIDATE -->|Yes| PREVIEW[Preview Data]
    
    PREVIEW --> REVIEW[Review & Submit]
    REVIEW --> CONFIRM{Final<br/>Confirmation?}
    CONFIRM -->|No| UPLOAD
    CONFIRM -->|Yes| PROCESS[Process Trades]
    
    PROCESS --> API[Accounts Processor API]
    API --> RESPONSE{API<br/>Response}
    RESPONSE -->|Success| SUCCESS[Confirmation Email]
    RESPONSE -->|Failure| ERROR2[Error Notification]
    
    SUCCESS --> END[Transaction Complete]
    ERROR2 --> RETRY[Retry Options]
    
    %% Styling
    classDef userAction fill:#e1f5fe
    classDef validation fill:#f3e5f5
    classDef process fill:#e8f5e8
    classDef outcome fill:#fff3e0
    
    class START,AUTH,UPLOAD,PREVIEW,REVIEW userAction
    class CHECK,VALIDATE,CONFIRM,RESPONSE validation
    class PROCESS,API process
    class SUCCESS,ERROR1,ERROR2,RETRY,END outcome
```

## Data Processing Pipeline

```mermaid
graph LR
    %% File Processing
    FILE[Excel/CSV File] --> PARSE[File Parser]
    
    PARSE --> EXTRACT[Data Extraction<br/>- Account Numbers<br/>- Fund Codes<br/>- Trade Types<br/>- Amounts<br/>- Dates]
    
    EXTRACT --> VAL1[Format Validation<br/>- Column presence<br/>- Data types<br/>- Required fields]
    
    VAL1 --> VAL2[Business Validation<br/>- Account exists<br/>- Fund approved<br/>- Amount limits<br/>- Date rules]
    
    VAL2 --> TRANSFORM[Transform to API Format<br/>- JSON payload<br/>- Batch structure<br/>- Authentication]
    
    TRANSFORM --> BATCH[Batch Optimizer<br/>- Group trades<br/>- Order execution<br/>- Priority sorting]
    
    BATCH --> SUBMIT[API Submission<br/>- HTTPS POST<br/>- Retry logic<br/>- Error handling]
    
    SUBMIT --> RESULT[Process Response<br/>- Success codes<br/>- Error messages<br/>- Reference numbers]
    
    %% Styling
    classDef input fill:#e3f2fd
    classDef process fill:#f1f8e9
    classDef validation fill:#fff8e1
    classDef output fill:#fce4ec
    
    class FILE input
    class PARSE,EXTRACT,TRANSFORM,BATCH process
    class VAL1,VAL2 validation
    class SUBMIT,RESULT output
```

## Validation Architecture

```mermaid
graph TD
    INPUT[Trading Sheet Data] --> L1[Level 1: Structure]
    
    L1 --> CHK1[File Format Check]
    L1 --> CHK2[Column Headers]
    L1 --> CHK3[Data Presence]
    
    CHK1 --> L2[Level 2: Data Types]
    CHK2 --> L2
    CHK3 --> L2
    
    L2 --> TYPE1[Account: String]
    L2 --> TYPE2[Fund: String]
    L2 --> TYPE3[Type: Enum]
    L2 --> TYPE4[Amount: Decimal]
    L2 --> TYPE5[Date: DateTime]
    
    TYPE1 --> L3[Level 3: Business Rules]
    TYPE2 --> L3
    TYPE3 --> L3
    TYPE4 --> L3
    TYPE5 --> L3
    
    L3 --> BUS1[Account Validation<br/>- Exists in system<br/>- Is active<br/>- Has mandate]
    
    L3 --> BUS2[Fund Validation<br/>- On approved list<br/>- Currently tradeable<br/>- Accepts trade type]
    
    L3 --> BUS3[Amount Validation<br/>- Min: R100<br/>- Max: R10M<br/>- Fund minimums]
    
    L3 --> BUS4[Date Validation<br/>- Business day<br/>- Not future<br/>- Within limits]
    
    L3 --> BUS5[Trade Logic<br/>- BUY: Cash available<br/>- SELL: Holdings exist<br/>- SWITCH: Valid funds]
    
    BUS1 --> RESULT{All Valid?}
    BUS2 --> RESULT
    BUS3 --> RESULT
    BUS4 --> RESULT
    BUS5 --> RESULT
    
    RESULT -->|Yes| PROCEED[Proceed to API]
    RESULT -->|No| ERRORS[Return Errors<br/>with Line Numbers]
    
    %% Styling
    classDef level fill:#e8eaf6
    classDef check fill:#e1f5fe
    classDef business fill:#f3e5f5
    classDef result fill:#e8f5e8
    
    class L1,L2,L3 level
    class CHK1,CHK2,CHK3,TYPE1,TYPE2,TYPE3,TYPE4,TYPE5 check
    class BUS1,BUS2,BUS3,BUS4,BUS5 business
    class RESULT,PROCEED,ERRORS result
```

## API Integration Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as Application
    participant V as Validator
    participant API as Accounts API
    participant E as Email Service
    
    U->>A: Upload Trading Sheet
    A->>V: Validate Data
    
    alt Validation Failed
        V-->>A: Return Errors
        A-->>U: Display Errors
    else Validation Success
        V-->>A: Data Valid
        A->>API: POST /api/v1/trades/batch
        Note over API: Process Trades
        
        alt API Success
            API-->>A: 200 OK + Reference
            A->>E: Send Confirmation
            E-->>U: Email with Reference
            A-->>U: Success Message
        else API Error
            API-->>A: Error Response
            A-->>U: Show Error
            Note over A: Log for Retry
        end
    end
```

## State Management

```mermaid
graph TD
    INIT[Initial State] --> DECLARE[Declaration State<br/>- consent_given: false<br/>- consent_name: null<br/>- consent_date: null]
    
    DECLARE --> ACCEPTED{User<br/>Accepts?}
    ACCEPTED -->|Yes| UPLOAD_READY[Upload Ready<br/>- consent_given: true<br/>- consent_name: string<br/>- consent_date: datetime]
    ACCEPTED -->|No| DECLARE
    
    UPLOAD_READY --> FILE_UPLOAD[File Uploaded<br/>- file_uploaded: true<br/>- uploaded_file_name: string<br/>- uploaded_file_size: int<br/>- upload_timestamp: datetime]
    
    FILE_UPLOAD --> VALIDATED[Validated State<br/>- validation_passed: true<br/>- trade_count: int<br/>- total_value: decimal]
    
    VALIDATED --> REVIEW_STATE[Review State<br/>- ready_to_submit: true<br/>- final_declaration: false]
    
    REVIEW_STATE --> FINAL{Final<br/>Declaration?}
    FINAL -->|Yes| SUBMITTED[Submitted State<br/>- submission_time: datetime<br/>- reference_number: string<br/>- status: processing]
    FINAL -->|No| REVIEW_STATE
    
    SUBMITTED --> COMPLETE[Complete State<br/>- status: completed<br/>- confirmation_sent: true]
    
    %% Styling
    classDef state fill:#e3f2fd
    classDef decision fill:#fff3e0
    classDef final fill:#e8f5e8
    
    class INIT,DECLARE,UPLOAD_READY,FILE_UPLOAD,VALIDATED,REVIEW_STATE,SUBMITTED,COMPLETE state
    class ACCEPTED,FINAL decision
```

## Error Handling Strategy

```mermaid
graph LR
    ERROR[Error Detected] --> CLASSIFY[Error Classification]
    
    CLASSIFY --> USER[User Errors<br/>- Invalid data<br/>- Missing fields<br/>- Format issues]
    
    CLASSIFY --> SYSTEM[System Errors<br/>- API timeout<br/>- Network issues<br/>- Server errors]
    
    CLASSIFY --> BUSINESS[Business Errors<br/>- Insufficient funds<br/>- Invalid account<br/>- Trade limits]
    
    USER --> DISPLAY1[Display Clear Message<br/>- Field location<br/>- Correction guidance<br/>- Examples]
    
    SYSTEM --> RETRY[Automatic Retry<br/>- Exponential backoff<br/>- Max 3 attempts<br/>- Queue for manual]
    
    BUSINESS --> NOTIFY[Notify Operations<br/>- Error details<br/>- Account info<br/>- Manual review]
    
    DISPLAY1 --> LOG[Log All Errors<br/>- Timestamp<br/>- User info<br/>- Stack trace]
    RETRY --> LOG
    NOTIFY --> LOG
    
    LOG --> ANALYTICS[Analytics<br/>- Error patterns<br/>- Common issues<br/>- System health]
    
    %% Styling
    classDef error fill:#ffebee
    classDef handler fill:#f3e5f5
    classDef action fill:#e8f5e8
    
    class ERROR,USER,SYSTEM,BUSINESS error
    class CLASSIFY,DISPLAY1,RETRY,NOTIFY handler
    class LOG,ANALYTICS action
```

## Security Architecture

```mermaid
graph TD
    USER[User Access] --> AUTH[Authentication<br/>- User credentials<br/>- Session management]
    
    AUTH --> DECLARE[Declaration<br/>- Digital signature<br/>- Timestamp<br/>- IP logging]
    
    DECLARE --> UPLOAD[File Upload<br/>- Virus scanning<br/>- Size limits<br/>- Type validation]
    
    UPLOAD --> ENCRYPT[Data Encryption<br/>- TLS 1.3<br/>- At-rest encryption<br/>- Key management]
    
    ENCRYPT --> API_AUTH[API Authentication<br/>- API key<br/>- Request signing<br/>- Rate limiting]
    
    API_AUTH --> AUDIT[Audit Trail<br/>- All actions logged<br/>- Immutable records<br/>- Compliance ready]
    
    AUDIT --> MONITOR[Monitoring<br/>- Real-time alerts<br/>- Anomaly detection<br/>- Performance metrics]
    
    %% Styling
    classDef security fill:#e3f2fd
    classDef process fill:#f1f8e9
    
    class USER,AUTH,DECLARE,UPLOAD,ENCRYPT,API_AUTH,AUDIT,MONITOR security
```

## Key Architecture Benefits

### 🎯 **Streamlined Workflow**
- Linear progression with clear checkpoints
- Validation at each step prevents downstream errors
- User-friendly error messages guide corrections

### 🔒 **Security First**
- Declaration provides legal accountability
- Encrypted data transmission
- Complete audit trail for compliance

### ⚡ **Performance Optimized**
- Batch processing reduces API calls
- Client-side validation reduces server load
- Async processing for large files

### 📊 **Operational Excellence**
- Comprehensive error handling
- Automated retry mechanisms
- Detailed logging for troubleshooting

This architecture ensures reliable, secure, and efficient processing of Unit Trust trades through the EasyEquities Accounts Processor API.
