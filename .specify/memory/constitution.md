# Backup Utility CiD Constitution

## Core Principles

### I. Segurança Operacional (Read-Only nos Terminais)
Durante a etapa de extração, o sistema deve operar estritamente em modo **Somente Leitura (Read-Only)** nos equipamentos Control iD (iDFace). Requisições devem respeitar controle de concorrência por dispositivo (`MAX_CONCURRENT_IMAGES_PER_DEVICE = 3`), *throttling* e *retries* com *backoff* para não degradar o reconhecimento facial ao vivo.

### II. Arquitetura Dual-Database em 2 Estágios
- **Estágio 1 (Extração & Consolidação Local):** Persistência transacional em SQLite (`backup_controlid.sqlite`) com deduplicação pré-download de fotos e resolução de conflitos *Best-Record Wins* baseada em timestamp.
- **Estágio 2 (Tradução & Restauração iDSecure):** Injeção direta em MySQL 5.7/8.0 (modo estrito) via introspecção dinâmica de `INFORMATION_SCHEMA.COLUMNS`, geração de SQL Dump (`dump_idsecure_mysql.sql`) e sincronização de fotos faciais via Web API do iDSecure (porta `30443`).

### III. Resiliência e Checkpoints
Operações longas de extração e download de biometrias faciais devem registrar *checkpoints* no SQLite, permitindo pausar, retomar e reexecutar sem perda de progresso ou downloads redundantes.

### IV. Testes Automatizados e Qualidade
Toda alteração de código deve preservar a integridade dos testes automatizados (`python -m pytest tests -v`), cobrindo cliente API iDFace, persistência/deduplicação SQLite, tradutor MySQL e fluxo E2E com servidor mock (`tests/mock_idface_server.py`). O build via `build.ps1` é bloqueado se houver falhas nos testes.

### V. Simplicidade e Consistência de Stack
- **Linguagem & UI:** Python 3.10+ com interface desktop Flet em Dark Mode corporativo.
- **Rede & Dados:** `httpx` assíncrono para comunicação `.fcgi`, `sqlite3` para storage local e `pymysql` para restauração no iDSecure.

## Restrições Técnicas e Segurança
- Preservar `id` e `idDevice` na tabela `Users` do MySQL do iDSecure para manter sincronia com os terminais físicos.
- Compatibilidade obrigatória com MySQL 5.7 e 8.0 em `STRICT_TRANS_TABLES` e `ONLY_FULL_GROUP_BY`.
- Logs centralizados com rotação em `logs/bot_backup.log` via logger `BackupUtilityCiD`.

## Workflow de Desenvolvimento e Build
1. Especificar e planejar alterações alinhadas ao `PRD.md` e `TRD.md`.
2. Validar com `python -m pytest tests -v`.
3. Empacotar executável standalone Windows (`dist/Backup-Utility-CiD/`) via `build.ps1` (PyInstaller).

## Governance
Esta constituição reflete as diretrizes do `PRD.md` e `TRD.md` do **Backup Utility CiD**. Alterações arquiteturais devem ser documentadas nos respectivos documentos e validadas pela suíte de testes.

**Version**: 1.0.0 | **Ratified**: 2026-11-24 | **Last Amended**: 2026-11-24
