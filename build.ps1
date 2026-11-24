<#
.SYNOPSIS
    Script de automação para execução de testes e build do executável (.exe) standalone
    do Backup Utility CiD via PyInstaller.
#>

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Backup Utility CiD - PIPELINE DE TESTES E BUILD PYINSTALLER" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Executa a suíte de testes
Write-Host "`n[1/3] Executando bateria de testes automatizados com Pytest..." -ForegroundColor Yellow
python -m pytest tests -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERRO] Falha nos testes automatizados! O build foi cancelado." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Todos os testes passaram com sucesso!" -ForegroundColor Green

# 2. Limpeza de builds anteriores
Write-Host "`n[2/3] Limpando diretórios de build anteriores..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# 3. Empacotamento com PyInstaller usando .spec único
Write-Host "`n[3/3] Compilando executável standalone com PyInstaller..." -ForegroundColor Yellow
python -m PyInstaller --noconfirm Backup-Utility-CiD.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host " [SUCESSO] Executável gerado na pasta dist/Backup-Utility-CiD/" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
} else {
    Write-Host "`n[ERRO] Falha durante a compilação com PyInstaller." -ForegroundColor Red
    exit 1
}
