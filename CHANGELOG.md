# Changelog

## [Latest] - 2025-01-05

### Added
- **Multi-step registration system** with `shouldUpdatePassword` flag
- **New User model fields**:
  - `should_update_password` - tracks registration completion status
  - `registration_completed_at` - timestamp of registration completion
- **New API endpoints**:
  - `POST /api/auth/complete-registration/` - Complete user registration (without password)
  - `POST /api/auth/set-password/` - Set password and complete registration
  - `POST /api/auth/reset-password/` - Initiate password reset
  - `POST /api/auth/set-new-password/` - Set new password after reset
- **Enhanced security features**:
  - Spam protection with `is_reset` flag
  - Rate limiting for SMS/Telegram requests
  - Phone number validation in E.164 format
- **Comprehensive Swagger documentation** for all new endpoints
- **Test script** for new registration flow

### Changed
- **Updated registration flow**:
  1. Send verification code (with spam protection)
  2. Complete registration (create user without password)
  3. Set password (complete registration)
- **Enhanced User model methods**:
  - `is_registration_complete()` - check if registration is complete
  - `can_use_service()` - check if user can use the service
  - `complete_registration()` - complete registration process
- **Updated serializers** with new fields and validation
- **Enhanced URL routing** with new endpoints

### Security
- **Spam protection**: Existing phone numbers require `is_reset=true` flag
- **Rate limiting**: Prevents abuse of SMS/Telegram services
- **Phone validation**: Strict E.164 format validation
- **Registration state tracking**: Users cannot access service until registration is complete

### Migration
- Database migration included for new User model fields
- Backward compatibility maintained for existing endpoints
- Old registration endpoints preserved for compatibility

## Registration Flow

### New User Registration
1. `POST /api/auth/send-code/` - Send verification code
2. `POST /api/auth/complete-registration/` - Create user (without password)
3. `POST /api/auth/set-password/` - Set password and complete registration

### Password Reset
1. `POST /api/auth/reset-password/` - Send reset code
2. `POST /api/auth/set-new-password/` - Set new password with code verification

### Security Features
- **Spam Protection**: Cannot register existing numbers without `is_reset=true`
- **State Tracking**: `should_update_password` flag prevents incomplete registrations
- **Rate Limiting**: Prevents abuse of SMS/Telegram services
- **Code Expiration**: Verification codes expire in 5 minutes
