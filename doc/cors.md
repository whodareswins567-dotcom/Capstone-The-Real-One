# CORS

The backend uses FastAPI/Starlette CORSMiddleware and is configured environment-driven.

## Origin allowlist

- Env var: `IMS_CORS_ALLOW_ORIGINS`
- Format: comma-separated list of origins
- Safe default: if unset or empty, no origins are allowed (deny by default)

## Credentialed CORS

- Env var: `IMS_CORS_ALLOW_CREDENTIALS`
 - Values: `true`/ `1`/ `yes`/ `on` (case-insensitive)
- Safe default: if unset/empty/unrecognized, `False` (credentials disallowed)

 Enabling credentials broadens the cross-origin attack surface and should only be used when you intentionally use cookie/session based auth from a different origin.
