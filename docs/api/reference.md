# API Reference

Live OpenAPI schema rendered via Swagger UI. The schema is fetched at build time from the backend (`/api/v1/schema/?format=json`) and stored at `docs/api/openapi.json`.

To refresh against a running backend:

```powershell
python docs/scripts/fetch-openapi.py
```

<swagger-ui src="./openapi.json"/>
