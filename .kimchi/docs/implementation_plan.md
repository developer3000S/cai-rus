# Implementation Plan: CAI Edition System & RBAC

## 1. Objective
Implement a formal distinction between **Community Edition (Research & Learning)** and **Professional Edition (Enterprise & Production)**, including a Role-Based Access Control (RBAC) system with an administrative user.

## 2. Edition Definitions

### Community Edition (Research & Learning)
- **Target**: Researchers, students, open-source contributors.
- **Access**: Free, activated via `CAI_LICENSE_OFF=1` or absence of valid license.
- **Constraints**:
    - Limited access to high-end models (e.g., `alias1` gated).
    - Limited parallel execution capabilities.
    - Access to standard tools and agents.
    - Open-source updates (public PyPI).

### Professional Edition (Enterprise & Production)
- **Target**: Enterprises, professional security teams.
- **Access**: Paid license via `ALIAS_API_KEY`.
- **Capabilities**:
    - Full access to `alias1` and other professional models.
    - Unlimited/High-performance parallel execution.
    - Advanced tools and professional support.
    - Private package updates.

## 3. RBAC & Admin User

### Roles
- `USER`: Standard access based on the active edition.
- `ADMIN`: Full override access. Can manage users, change license settings, and access all Professional features regardless of the current global license state.

### Administrative User
- A special root account (created during setup or via environment variable).
- Full access to Professional Edition Enterprise features.

## 4. Implementation Steps

### Phase 1: Core Infrastructure
- [ ] Define `Edition` and `Role` enums in `src/cai/config.py` or a new `src/cai/auth_types.py`.
- [ ] Update `UserRecord` in `src/cai/api/auth.py` to include `role: Role`.
- [ ] Extend `AuthManager` to handle role-based session creation and validation.
- [ ] Implement a `get_current_edition()` utility that checks `ALIAS_API_KEY` and `CAI_LICENSE_OFF`.

### Phase 2: Feature Gating Mechanism
- [ ] Create a `@require_edition(Edition.PROFESSIONAL)` decorator for functions/methods.
- [ ] Implement an `EditionGuard` class to check access in the CLI and API.
- [ ] Integrate the guard into `src/cai/cli.py` and `src/cai/api/app.py`.

### Phase 3: Applying Constraints
- [ ] **Models**: Gate `alias1` model selection in the agent runner.
- [ ] **Tools**: Gate advanced tools (identify specific enterprise tools in `src/cai/tools/`).
- [ ] **Capabilities**: Gate `parallel` execution and `continuous_ops` for Community users.

### Phase 4: Admin User Implementation
- [ ] Add `CAI_ADMIN_PASSWORD` to `.env.example` and `CAIConfig`.
- [ ] Implement logic in `AuthManager` to ensure at least one admin user exists.
- [ ] Update RBAC checks to grant `ADMIN` full access.

### Phase 5: Verification
- [ ] Test Community access (verify limits).
- [ ] Test Professional access with valid key.
- [ ] Test Admin access (verify override).
- [ ] Verify API endpoint protection.
