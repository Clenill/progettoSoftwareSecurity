# Test Rate Limiting

## Requisiti
pip install pytest pytest-asyncio httpx

## Esecuzione
pytest tests/test_rate_limit.py -v
pytest tests/test_autenticazione.py -v
pytest tests/test_sql_injection.py -v

## Test disponibili
- **sotto_soglia**: verifica che le richieste normali non vengano bloccate
- **alla_soglia**: verifica che la richiesta N+1 venga bloccata con 429
- **retry_after**: verifica che la risposta 429 contenga l'header Retry-After
- **admin_soglia_doppia**: verifica che gli admin abbiano il doppio del limite
- **reset_dopo_intervallo**: verifica che il limite si azzeri dopo la finestra temporale
- **ip_diversi**: verifica che IP diversi abbiano contatori indipendenti