# Windows equivalent of `make test`. Only the dedicated test database is reset.
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pgBin = 'C:\Program Files\PostgreSQL\16\bin'
$psql = if (Get-Command psql -ErrorAction SilentlyContinue) { (Get-Command psql).Source } else { Join-Path $pgBin 'psql.exe' }
$createdb = if (Get-Command createdb -ErrorAction SilentlyContinue) { (Get-Command createdb).Source } else { Join-Path $pgBin 'createdb.exe' }
$python = Join-Path $root 'api\.venv\Scripts\python.exe'
if (!(Test-Path $psql) -or !(Test-Path $createdb) -or !(Test-Path $python)) {
    throw 'PostgreSQL 16 tools and api/.venv are required to run backend tests.'
}
if (!$env:PGPASSWORD) { $env:PGPASSWORD = 'concierge' }
$existing = & $psql -h localhost -U concierge -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='concierge_test'"
if ($LASTEXITCODE -ne 0) { throw 'Could not inspect PostgreSQL databases.' }
if ("$existing".Trim() -ne '1') {
    & $createdb -h localhost -U concierge concierge_test
    if ($LASTEXITCODE -ne 0) { throw 'Could not create concierge_test.' }
}
& $psql -v ON_ERROR_STOP=1 -h localhost -U concierge -d concierge_test -q -c 'DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;'
if ($LASTEXITCODE -ne 0) { throw 'Could not reset concierge_test.' }
foreach ($file in @('db\schema.sql', 'db\seed.sql')) {
    & $psql -v ON_ERROR_STOP=1 -h localhost -U concierge -d concierge_test -q -f (Join-Path $root $file)
    if ($LASTEXITCODE -ne 0) { throw "Could not apply $file." }
}
foreach ($file in (Get-ChildItem (Join-Path $root 'db\migrations\*.sql') | Sort-Object Name)) {
    & $psql -v ON_ERROR_STOP=1 -h localhost -U concierge -d concierge_test -q -f $file.FullName
    if ($LASTEXITCODE -ne 0) { throw "Could not apply $($file.Name)." }
}
$env:DATABASE_URL = 'postgresql://concierge:concierge@localhost:5432/concierge_test'
$env:TESTING = 'true'
$env:GEMINI_API_KEY = ''
$env:OPENAI_API_KEY = ''
$env:OPENROUTER_API_KEY = ''
$env:XKIRO_API_KEY = ''
$env:GROQ_API_KEY = ''
Push-Location (Join-Path $root 'api')
try { & $python -m pytest tests -q; exit $LASTEXITCODE }
finally { Pop-Location }
