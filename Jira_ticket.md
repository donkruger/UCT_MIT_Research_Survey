# JIRA Ticket - Trading Sheet Applet

## Project Information

**Project**: Trading Operations Platform  
**Epic**: Trade Allocations API Integration  
**Ticket Type**: Story/Epic  
**Priority**: High  
**Status**: Completed  
**Assignee**: Development Team  
**Reporter**: Trading Operations  
**Components**: Trading Systems, API Integration, Security  
**Labels**: `trading`, `unit-trusts`, `api-integration`, `security`, `devops-ready`

---

## Title

**Trading Sheet Applet - Unit Trust Trade Processing Application**

---

## Description

### Overview

Develop a professional trading operations application for processing Unit Trust (UT) trades through the EasyEquities Trade Allocations Monitor API. The application must implement a complete two-phase asynchronous trading workflow with comprehensive security, audit trail, and user authentication.

### Business Context

The trading desk requires a secure, user-friendly application to:
- Upload and validate Unit Trust trading sheets
- Submit trades to the Trade Allocations API with real-time monitoring
- Provide detailed execution feedback and failure analysis
- Maintain comprehensive audit trails for compliance
- Enforce UT-only trading restrictions for risk management
- Support multi-environment deployments (UAT, QA, Production)

### Technical Requirements

#### Core Functionality
1. **User Authentication System**
   - Password-based authentication with bcrypt hashing (MVP)
   - Session management (60-min timeout, 30-min inactivity)
   - Rate limiting (5 failed attempts = 15-minute lockout)
   - Audit logging for all authentication events
   - Future-ready for OAuth/SSO migration

2. **Two-Phase Trading Workflow**
   - **Phase 1**: Trade submission via `/createValueOrdersWithSystemIdentifier`
   - **Phase 2**: Real-time status monitoring via `/tradeGroupStatus/{groupID}`
   - Intelligent polling (5-second intervals, 5-minute maximum)
   - Enhanced failure feedback with individual trade-level results

3. **File Processing & Validation**
   - Support Excel (.xlsx, .xls) and CSV formats
   - Validate required columns: ShareCode, ContractCode, InstrumentID, Amount/Units, Direction, UserID, TrustAccount
   - Enforce business rules (BUY=amount-based, SELL=unit-based)
   - Data preview and validation summary

4. **Security Architecture**
   - UT-only protection (block non-UT ContractCode values)
   - Fail-safe defaults (protection enabled by default)
   - Input sanitization and injection protection
   - Environment-specific security hardening
   - Comprehensive validation and audit logging

5. **Audit Trail & Compliance**
   - Email notifications for ALL submissions (success, failure, error)
   - Capture WHO executed (authenticated user identity)
   - Capture WHAT was executed (complete trade details)
   - Capture WHEN (precise timestamps)
   - Capture OUTCOME (success/failure with reasons)
   - CSV and JSON attachments for evidence

6. **DevOps-Friendly Secrets Management**
   - HashiCorp Vault integration via environment variables
   - Template-based secrets rendering at container startup
   - Fail-fast validation with `STRICT_STARTUP=true`
   - Zero hardcoded credentials in repository
   - AWS ECS Fargate deployment ready

7. **Error Handling & Monitoring**
   - Distinguish system errors from business errors
   - Detailed failure feedback per trade:
     - Insufficient funds
     - Duplicate requests
     - Account restrictions
     - Invalid instruments
     - Market hours violations
   - Health check endpoint for container monitoring
   - CloudWatch logs integration

### Architecture

- **Frontend**: Streamlit (Python web framework)
- **Authentication**: bcrypt password hashing with provider pattern
- **API Integration**: Two-phase asynchronous workflow
- **Deployment**: Docker containers on AWS ECS Fargate
- **Secrets Management**: HashiCorp Vault → AWS Secrets Manager → ECS
- **Audit Trail**: SMTP email with CSV/JSON attachments

---

## Acceptance Criteria

### 1. User Authentication & Authorization

- [ ] ✅ Users must authenticate with email and password before accessing application
- [ ] ✅ Passwords stored as bcrypt hashes (never plain text)
- [ ] ✅ Session timeout enforced (60 minutes absolute, 30 minutes inactivity)
- [ ] ✅ Rate limiting prevents brute force attacks (5 attempts = 15-min lockout)
- [ ] ✅ User identity captured and included in audit trail
- [ ] ✅ Login attempts logged for security auditing
- [ ] ✅ Password visibility toggle available on login form
- [ ] ✅ Locked accounts display countdown timer

### 2. File Upload & Validation

- [ ] ✅ Application accepts Excel (.xlsx, .xls) and CSV files
- [ ] ✅ Validates presence of all required columns
- [ ] ✅ Enforces UT-only restriction (ContractCode must start with `UT.ZA`)
- [ ] ✅ Validates BUY orders have positive Amount
- [ ] ✅ Validates SELL orders have positive Units
- [ ] ✅ Displays data preview before submission
- [ ] ✅ Shows validation summary with error/warning counts
- [ ] ✅ Blocks submission if critical validation errors exist

### 3. Trade Submission (Phase 1)

- [ ] ✅ Submits trades to `/createValueOrdersWithSystemIdentifier` endpoint
- [ ] ✅ Uses Bearer token authentication
- [ ] ✅ Includes system identifier (ID: 27)
- [ ] ✅ Displays complete payload preview before submission
- [ ] ✅ Returns Group ID for tracking
- [ ] ✅ Handles API errors gracefully with user-friendly messages
- [ ] ✅ Retry logic for transient failures (max 3 attempts)

### 4. Execution Monitoring (Phase 2)

- [ ] ✅ Polls `/tradeGroupStatus/{groupID}` every 5 seconds
- [ ] ✅ Maximum polling duration: 5 minutes
- [ ] ✅ Displays real-time progress indicators
- [ ] ✅ Checks `groupStatusID` (0=incomplete, 1=success, 2=with errors)
- [ ] ✅ Automatically fetches detailed results from `/trade-monitor/allocation/all/{groupID}`
- [ ] ✅ Maps `allocationStatusId` (0=pending, 3=failed, 4=success)
- [ ] ✅ Displays individual trade failure reasons
- [ ] ✅ Shows success/failure/pending counts in real-time
- [ ] ✅ Provides complete execution summary

### 5. Enhanced Failure Feedback

- [ ] ✅ Retrieves detailed allocation data for all trades
- [ ] ✅ Parses and displays specific failure reasons:
  - [ ] ✅ Insufficient funds
  - [ ] ✅ Duplicate request detection (within 2 seconds)
  - [ ] ✅ Account restrictions
  - [ ] ✅ Invalid instruments
  - [ ] ✅ Market hours violations
- [ ] ✅ Shows User ID, Instrument ID, Amount, Trust Account for each failed trade
- [ ] ✅ Provides actionable error messages for self-service correction
- [ ] ✅ Debug panel shows raw API responses for troubleshooting

### 6. Security & Protection

- [ ] ✅ UT-only protection enabled by default (fail-safe)
- [ ] ✅ Blocks non-UT trades in strict mode
- [ ] ✅ Configuration supports multiple protection modes (strict, audit_warn)
- [ ] ✅ All validation attempts logged for audit
- [ ] ✅ Input sanitization prevents injection attacks
- [ ] ✅ Environment-specific security settings enforced
- [ ] ✅ Session management prevents unauthorized access
- [ ] ✅ HTTPS encryption for all API communications

### 7. Audit Trail & Compliance

- [ ] ✅ Email sent for EVERY submission (success, failure, error)
- [ ] ✅ Captures WHO: User name, email, role, login timestamp
- [ ] ✅ Captures WHAT: Complete trade details, file name, counts
- [ ] ✅ Captures WHEN: Precise timestamps for all actions
- [ ] ✅ Captures OUTCOME: Success/failure with detailed reasons
- [ ] ✅ Attaches original CSV file to email
- [ ] ✅ Includes JSON execution results
- [ ] ✅ Error details included for failed submissions
- [ ] ✅ Email sent to configured compliance recipient

### 8. DevOps & Deployment

- [ ] ✅ Dockerfile created with proper base image (Python 3.10)
- [ ] ✅ Entrypoint script renders secrets from environment variables
- [ ] ✅ Secrets template file committed (no actual secrets)
- [ ] ✅ Environment variable validation with `STRICT_STARTUP=true`
- [ ] ✅ Health check endpoint: `/_stcore/health`
- [ ] ✅ Container uses tini for proper signal handling
- [ ] ✅ CloudWatch logs integration configured
- [ ] ✅ IAM roles documented for ECS Task Execution and Task Role
- [ ] ✅ Support for multiple environments (UAT, QA, Production)
- [ ] ✅ Complete DevOps deployment request documentation

### 9. Documentation

- [ ] ✅ Comprehensive README.md with quickstart guide
- [ ] ✅ API integration guide with endpoint details
- [ ] ✅ Authentication implementation summary
- [ ] ✅ DevOps-friendly secrets implementation guide (1100+ lines)
- [ ] ✅ Migration checklist for deployment validation
- [ ] ✅ Enhanced polling documentation with failure feedback
- [ ] ✅ UT-only protection architecture documentation
- [ ] ✅ Audit email system documentation
- [ ] ✅ Sample CSV templates for testing
- [ ] ✅ Postman collection for API testing
- [ ] ✅ DevOps deployment request document

### 10. User Experience

- [ ] ✅ Modern, professional UI with EasyEquities branding
- [ ] ✅ Progress tracker in sidebar
- [ ] ✅ Clear step-by-step workflow
- [ ] ✅ Real-time status updates during execution
- [ ] ✅ User-friendly error messages
- [ ] ✅ Downloadable execution reports
- [ ] ✅ Expandable debug information
- [ ] ✅ Responsive design

---

## Testing Criteria

### Unit Testing

#### 1. Authentication Module
- [ ] ✅ Test bcrypt password hashing and verification
- [ ] ✅ Test session creation and expiration
- [ ] ✅ Test rate limiting (5 failed attempts trigger lockout)
- [ ] ✅ Test lockout duration (15 minutes)
- [ ] ✅ Test session timeout (60-min absolute, 30-min inactivity)
- [ ] ✅ Test user lookup by email (case-insensitive)
- [ ] ✅ Test disabled user accounts cannot login
- [ ] ✅ Test authentication audit logging

#### 2. File Parser & Validator
- [ ] ✅ Test Excel file parsing (.xlsx, .xls)
- [ ] ✅ Test CSV file parsing
- [ ] ✅ Test column validation (all required columns present)
- [ ] ✅ Test UT-only protection (ContractCode validation)
- [ ] ✅ Test BUY order validation (Amount required)
- [ ] ✅ Test SELL order validation (Units required)
- [ ] ✅ Test data type validation (numeric fields)
- [ ] ✅ Test empty file handling
- [ ] ✅ Test malformed file handling

#### 3. Trade Mapper
- [ ] ✅ Test CSV to API payload conversion
- [ ] ✅ Test BUY order mapping (value-based)
- [ ] ✅ Test SELL order mapping (unit-based)
- [ ] ✅ Test decimal precision (Amount: 2 places, Units: 8 places)
- [ ] ✅ Test required field mapping
- [ ] ✅ Test system identifier inclusion

#### 4. API Client
- [ ] ✅ Test trade submission request formatting
- [ ] ✅ Test Bearer token authentication
- [ ] ✅ Test retry logic (max 3 attempts)
- [ ] ✅ Test timeout handling (30 seconds)
- [ ] ✅ Test polling mechanism (5-second intervals)
- [ ] ✅ Test max polling duration (5 minutes)
- [ ] ✅ Test status ID interpretation (0, 1, 2)
- [ ] ✅ Test allocation status mapping (0, 3, 4)
- [ ] ✅ Test detailed failure data retrieval

#### 5. Email Audit System
- [ ] ✅ Test email generation for successful submissions
- [ ] ✅ Test email generation for failed submissions
- [ ] ✅ Test email generation for error conditions
- [ ] ✅ Test user identity capture in emails
- [ ] ✅ Test CSV attachment generation
- [ ] ✅ Test JSON report attachment
- [ ] ✅ Test SMTP authentication
- [ ] ✅ Test email delivery

#### 6. Security Protection
- [ ] ✅ Test UT-only validation in strict mode
- [ ] ✅ Test non-UT blocking
- [ ] ✅ Test audit_warn mode (allow with log)
- [ ] ✅ Test protection override configuration
- [ ] ✅ Test validation audit logging
- [ ] ✅ Test fail-safe defaults

### Integration Testing

#### 1. End-to-End Workflow (UAT Environment)
- [ ] ✅ **Test User Login**
  - Login with valid credentials
  - Verify session creation
  - Verify user identity captured
  
- [ ] ✅ **Test File Upload**
  - Upload valid UT trading sheet
  - Verify data preview displays correctly
  - Verify validation passes
  
- [ ] ✅ **Test Trade Submission**
  - Submit trades to UAT API
  - Verify Group ID returned
  - Verify API payload correct
  
- [ ] ✅ **Test Execution Monitoring**
  - Verify polling starts automatically
  - Verify status updates every 5 seconds
  - Verify final status captured (success/failure)
  
- [ ] ✅ **Test Detailed Results**
  - Verify allocation data retrieved
  - Verify individual trade statuses displayed
  - Verify failure reasons shown for failed trades
  
- [ ] ✅ **Test Audit Email**
  - Verify email sent to compliance recipient
  - Verify user identity in email
  - Verify CSV attached
  - Verify execution results included

#### 2. Error Handling Scenarios
- [ ] ✅ **Test Invalid Login**
  - Invalid credentials rejected
  - Failed attempt counter increments
  - Lockout triggered after 5 attempts
  
- [ ] ✅ **Test Session Timeout**
  - Session expires after 60 minutes (absolute)
  - Session expires after 30 minutes (inactivity)
  - User redirected to login
  
- [ ] ✅ **Test Invalid File Upload**
  - Non-UT trades blocked in strict mode
  - Missing columns detected
  - Invalid data types rejected
  
- [ ] ✅ **Test API Errors**
  - Network timeout handled gracefully
  - Authentication failures handled
  - Invalid responses handled
  - Retry logic executes properly
  
- [ ] ✅ **Test Business Errors**
  - Insufficient funds error displayed
  - Duplicate request error shown
  - Account restriction error explained
  - Individual trade failures mapped correctly

#### 3. Security Testing
- [ ] ✅ **Test UT-Only Protection**
  - Upload file with non-UT trades
  - Verify trades blocked in strict mode
  - Verify validation logged
  
- [ ] ✅ **Test Authentication Security**
  - Brute force protection works
  - Session tokens secure
  - Password hashes never exposed
  
- [ ] ✅ **Test Input Validation**
  - SQL injection attempts blocked
  - XSS attempts sanitized
  - File upload restrictions enforced

#### 4. Multi-Environment Testing
- [ ] ✅ **Test UAT Environment**
  - Connect to UAT API endpoints
  - Verify environment-specific configuration
  - Submit test trades
  
- [ ] ✅ **Test QA Environment**
  - Connect to QA API endpoints
  - Verify separate configuration
  
- [ ] ✅ **Test Production Configuration**
  - Verify production URLs configured
  - Verify strict security settings
  - Verify protection cannot be disabled

### Performance Testing

- [ ] ✅ File upload handles files up to 1000 rows
- [ ] ✅ Validation completes within 5 seconds
- [ ] ✅ Trade submission responds within 10 seconds
- [ ] ✅ Polling performs efficiently (minimal CPU/memory)
- [ ] ✅ Email generation completes within 3 seconds
- [ ] ✅ Application startup under 30 seconds (including secrets rendering)
- [ ] ✅ Health check responds within 2 seconds

### Deployment Testing (DevOps)

#### 1. Container Build & Startup
- [ ] ✅ Docker image builds successfully
- [ ] ✅ Container starts with all required environment variables
- [ ] ✅ Entrypoint script renders secrets.toml correctly
- [ ] ✅ Startup validation passes with `STRICT_STARTUP=true`
- [ ] ✅ Missing secrets cause container to exit (fail-fast)
- [ ] ✅ Health check endpoint responds
- [ ] ✅ CloudWatch logs show successful startup

#### 2. Secrets Management
- [ ] ✅ Secrets loaded from AWS Secrets Manager
- [ ] ✅ Environment variables injected correctly
- [ ] ✅ User credentials parsed from pipe-delimited format
- [ ] ✅ Bcrypt hashes handled correctly
- [ ] ✅ No secrets hardcoded in repository
- [ ] ✅ Secrets template committed (placeholders only)

#### 3. ECS Deployment
- [ ] ✅ Task definition includes all required environment variables
- [ ] ✅ Task definition references correct Secrets Manager ARNs
- [ ] ✅ IAM roles configured correctly
- [ ] ✅ ECS service starts tasks successfully
- [ ] ✅ Health checks pass
- [ ] ✅ ALB routes traffic correctly
- [ ] ✅ Container logs visible in CloudWatch

### User Acceptance Testing (UAT)

- [ ] ✅ Trading desk can login successfully
- [ ] ✅ Trading desk can upload CSV files
- [ ] ✅ Trading desk can preview data before submission
- [ ] ✅ Trading desk can submit trades
- [ ] ✅ Trading desk receives real-time status updates
- [ ] ✅ Trading desk can view detailed failure reasons
- [ ] ✅ Trading desk receives audit emails
- [ ] ✅ Trading desk confirms UI is intuitive and professional
- [ ] ✅ Trading desk confirms error messages are clear and actionable

### Regression Testing

- [ ] ✅ All existing authentication features work after updates
- [ ] ✅ All existing file validation rules work after updates
- [ ] ✅ All existing API integration works after updates
- [ ] ✅ All existing email notifications work after updates
- [ ] ✅ All existing security features work after updates
- [ ] ✅ No performance degradation introduced

---

## Definition of Done

- [x] All acceptance criteria met
- [x] All testing criteria passed
- [x] Code reviewed and approved
- [x] Documentation complete and accurate
- [x] Security review completed
- [x] DevOps deployment guide created
- [x] UAT testing completed successfully
- [x] Production deployment artifacts ready
- [x] Audit trail and compliance requirements met
- [x] Handover to operations team completed

---

## Technical Debt & Future Enhancements

### Identified for Future Iterations

1. **Authentication Enhancements**
   - OAuth/SSO integration (Google, Microsoft)
   - Multi-factor authentication (MFA)
   - LDAP/Active Directory integration
   - API key authentication for automated systems

2. **User Management**
   - Database-backed user storage
   - Self-service user registration
   - Password reset workflow
   - User activity dashboard

3. **Trading Features**
   - Support for additional trade types beyond UT
   - Bulk CSV download of historical executions
   - Trade scheduling and recurring trades
   - Advanced filtering and search

4. **Monitoring & Analytics**
   - Grafana dashboards for metrics
   - Trade success rate analytics
   - Performance monitoring
   - Usage analytics

5. **Infrastructure**
   - Multi-region deployment
   - Blue-green deployment strategy
   - Automated rollback procedures
   - Container auto-scaling

---

## Dependencies

### External Systems
- EasyEquities Trade Allocations API (UAT, QA, Production)
- EasyEquities Trade Allocations Monitor API
- Gmail SMTP server (for audit emails)
- HashiCorp Vault (secrets management)
- AWS Secrets Manager
- AWS ECS Fargate
- AWS ECR (Docker registry)
- AWS Application Load Balancer

### Infrastructure Requirements
- AWS Account with ECS access
- HashiCorp Vault instance
- Jenkins CI/CD pipeline
- CloudWatch Logs access
- IAM roles and policies

### Team Dependencies
- DevOps team (for pipeline creation and deployment)
- Security team (for secrets configuration)
- Trading operations (for UAT testing)
- Compliance team (for audit trail validation)

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation | Status |
|------|--------|-------------|------------|--------|
| API downtime during production trades | High | Low | Retry logic, timeout handling, clear error messages | ✅ Mitigated |
| Secrets exposure in repository | Critical | Low | Template-based system, .gitignore, code review | ✅ Mitigated |
| Unauthorized access to trading | High | Medium | Authentication, session management, rate limiting | ✅ Mitigated |
| Non-UT trades submitted | High | Medium | UT-only protection with fail-safe defaults | ✅ Mitigated |
| Missing audit trail | High | Low | Email sent for every submission, comprehensive logging | ✅ Mitigated |
| Container startup failures | Medium | Low | Fail-fast validation, health checks, CloudWatch logs | ✅ Mitigated |

---

## Release Notes

### Version 1.0.0 - Initial Production Release

**Release Date**: TBD  
**Status**: Ready for Deployment

#### Features Delivered

✅ **Core Trading Functionality**
- Two-phase asynchronous trade workflow
- Excel and CSV file upload support
- Real-time execution monitoring with 5-second polling
- Enhanced failure feedback with individual trade-level results
- Complete execution summary with success/failure breakdown

✅ **Security & Compliance**
- Password-based authentication with bcrypt hashing
- Session management (60-min timeout, 30-min inactivity)
- Rate limiting (5 failed attempts = 15-minute lockout)
- UT-only protection with fail-safe defaults
- Comprehensive audit trail via email
- Input sanitization and injection protection

✅ **DevOps & Deployment**
- HashiCorp Vault integration
- AWS ECS Fargate ready
- Docker containerization with health checks
- Fail-fast validation with STRICT_STARTUP mode
- Multi-environment support (UAT, QA, Production)
- Complete deployment documentation

✅ **User Experience**
- Modern UI with EasyEquities branding
- Intuitive step-by-step workflow
- Real-time progress indicators
- Clear error messages with actionable guidance
- Debug panel for troubleshooting

✅ **Documentation**
- Comprehensive README (570+ lines)
- DevOps-friendly secrets guide (1100+ lines)
- Authentication implementation summary
- API integration guide
- Enhanced polling documentation
- Deployment request document
- Migration checklist

#### Known Limitations

- Authentication is password-based (OAuth/SSO planned for future)
- Single region deployment (multi-region planned for future)
- Manual user management (self-service registration planned for future)

#### Deployment Requirements

- AWS ECS cluster configured
- HashiCorp Vault secrets configured
- Jenkins pipeline created
- IAM roles provisioned
- CloudWatch Logs group created
- ALB configured with target group

---

## Sign-Off

**Development Team**: ✅ Complete  
**Security Review**: ✅ Approved  
**DevOps Review**: Pending Pipeline Creation  
**UAT Testing**: ✅ Passed  
**Product Owner**: Pending Final Approval  

---

## Related Documentation

- **Repository**: https://github.com/Purple-Group/trading-sheet/tree/feature/ProjectInception
- **README**: `/README.md`
- **DevOps Deployment Request**: `/docs/DEVOPS_DEPLOYMENT_REQUEST.md`
- **DevOps Secrets Guide**: `/docs/devops_friendly_secrets.md`
- **Authentication Summary**: `/docs/AUTHENTICATION_IMPLEMENTATION_SUMMARY.md`
- **API Integration Guide**: `/docs/API_Integration_Guide.md`

---

**Ticket Created**: October 16, 2025  
**Last Updated**: October 16, 2025  
**Ticket ID**: [To be assigned by Jira]

