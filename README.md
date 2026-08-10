# academySsoOidc
Single Sign On using OIDC 

## Running the IdP locally

**1. Create Config file**  - 'docker-compose.yml':
```yaml
services: 
  keycloak:
    image: quay.io/keycloak/keycloak:25.0
    command: start-dev
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: password
    ports: 
      - "8080:8080"
```

**2. Prerequisite** - [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/) installed and running.

**3. Start It:** 
``` bash 
docker compose up
```
**4. Log in** - Visit http://localhost:8080/admin and log in with the admin
credentials set in docker-compose.yml. This puts us in Keycloak's
`master` realm, which manages Keycloak itself — not yet the
`hart-academy` realm. 