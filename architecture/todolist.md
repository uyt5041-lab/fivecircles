# Identity & Admin Services Implementation Plan

## Overview
Phase 1 Foundation for: Auth, User, Admin services.

## Service: Auth Service (Port: 8081)
- [x] Project Setup
- [x] Implement Domain Entity (RefreshToken)
- [ ] Implement Feign Client (UserServiceClient)
- [ ] Implement Service (Login with Feign)
- [ ] Implement Controller (AuthController)

## Service: User Service (Port: 8082)
- [x] Project Setup
- [x] Domain Entity (User) & DB Schema
- [ ] Implement Repository/Mapper
- [ ] Internal API (Validate User by Email)
- [ ] CRUD API (Signup, Update Profile)

## Service: Admin Service (Port: 8087)
- [x] Project Setup
- [ ] Admin Dashboard Data API
- [ ] User Management API (Block/Unblock)
