$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $cvmCommand = Get-Command pdflatex -ErrorAction SilentlyContinue
    $cvmCompiler = if ($cvmCommand) { $cvmCommand.Source } else { Join-Path $env:LOCALAPPDATA 'Programs/MiKTeX/miktex/bin/x64/pdflatex.exe' }
    if (-not (Test-Path -LiteralPath $cvmCompiler)) { throw 'Install a standard TeX Live or MiKTeX distribution with pdfLaTeX.' }
    for ($cvmPass = 1; $cvmPass -le 3; $cvmPass++) {
        & $cvmCompiler -interaction=nonstopmode -halt-on-error -file-line-error -no-shell-escape main.tex
        if ($LASTEXITCODE -ne 0) { throw "pdfLaTeX failed on pass $cvmPass; inspect main.log." }
    }
    Copy-Item -LiteralPath 'main.pdf' -Destination 'MANUSCRIPT_CVM.pdf' -Force
} finally {
    Pop-Location
}
