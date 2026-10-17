param(
    [int]$Port = 8005,
    [switch]$Reload
)

$ErrorActionPreference = 'Stop'
$url = "http://127.0.0.1:$Port"

# Reuse a healthy local instance instead of starting a second process on the
# same port (which produces Windows bind errors).
try {
    $health = Invoke-WebRequest -UseBasicParsing "$url/health" -TimeoutSec 2
    if ($health.StatusCode -eq 200) {
        Write-Host "SHUFFL API is already running at $url"
        Write-Host "Readiness: $((Invoke-WebRequest -UseBasicParsing "$url/v1/health/readiness" -TimeoutSec 3).Content)"
        exit 0
    }
} catch {
    # No healthy server on this port; start one below.
}

$arguments = @('-m', 'uvicorn', 'backend.app.main:app', '--host', '127.0.0.1', '--port', "$Port")
if ($Reload) { $arguments += '--reload' }
Write-Host "Starting SHUFFL API at $url ..."
& python @arguments
