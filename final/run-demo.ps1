param(
    [int]$Port = 5173
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSCommandPath
$Url = "http://localhost:$Port/"

function Get-PythonCommand {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        return @($pyLauncher.Source, "-3")
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return @($python.Source)
    }

    $python3 = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3) {
        return @($python3.Source)
    }

    throw "Python was not found on PATH. Install Python or run: python -m http.server $Port"
}

$pythonCommand = @(Get-PythonCommand)
$pythonExe = $pythonCommand[0]
$pythonArgs = if ($pythonCommand.Count -gt 1) {
    $pythonCommand[1..($pythonCommand.Count - 1)]
} else {
    @()
}

Write-Host "Serving Rover Ready from $Root"
Write-Host "Opening $Url"
Start-Process $Url

Push-Location $Root
try {
    & $pythonExe @pythonArgs -m http.server $Port
}
finally {
    Pop-Location
}
