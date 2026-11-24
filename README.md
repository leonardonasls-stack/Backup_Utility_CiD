# Backup Utility CiD

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/UI-Flet%201.0-4527a0.svg)](https://flet.dev/)
[![Control iD](https://img.shields.io/badge/Hardware-Control%20iD%20iDFace-00b4d8.svg)](https://www.controlid.com.br/)
[![MySQL](https://img.shields.io/badge/Database-MySQL%205.7%20%2F%208.0-orange.svg)](https://www.mysql.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-success.svg)](https://docs.pytest.org/)

Aplicação desktop para técnicos de campo e administradores de controle de acesso. O **Backup Utility CiD** automatiza a descoberta na rede local, a extração somente leitura de bancos de contingência de leitores faciais **Control iD (iDFace)**, a consolidação com deduplicação de biometrias faciais em SQLite e a restauração completa no servidor **iDSecure** (via injeção direta em MySQL, SQL Dump ou sincronização via Web API).

---

## Principais Funcionalidades

- **Descoberta e Extração de Terminais:**
  - Varredura paralela na rede local (IP único, faixa, lista ou CIDR `/24`) para localizar equipamentos Control iD.
  - Autenticação via API `.fcgi` (`/login.fcgi`) com reautenticação reativa em HTTP `401`/`403` e extração de `users`, `cards`, `groups`, `user_groups`, `access_rules`, `time_zones`, `time_spans` e `devices`.
  - Download em lote de biometrias faciais (`/user_get_image.fcgi`) com semáforo por dispositivo (`MAX_CONCURRENT_IMAGES_PER_DEVICE = 3`), *retries* e gravação não-bloqueante (`asyncio.to_thread`).
- **Consolidação e Deduplicação em SQLite:**
  - Banco local `backup_controlid.sqlite` com `PRAGMA journal_mode = WAL`, índices dedicados e *checkpoints* para pausa e retomada sem downloads duplicados.
  - Resolução de conflitos entre múltiplos terminais com regra *Best-Record Wins* baseada em timestamp.
- **Restauração no iDSecure:**
  - **Injeção Direta no MySQL (porta 3306):** Compatível com MySQL 5.7 e 8.0 em modo estrito (`STRICT_TRANS_TABLES`, `ONLY_FULL_GROUP_BY`) via introspecção dinâmica de `INFORMATION_SCHEMA.COLUMNS`.
  - **Sincronização de Fotos via Web API (porta 30443):** Envio paralelo (`asyncio.Semaphore(5)`) de fotos faciais em Base64 com `canUseFacial = True`.
  - **Exportação Offline:** Geração de `dump_idsecure_mysql.sql` e pacote `importacao_idsecure.zip` (`usuarios.csv` em UTF-8 BOM + `/fotos`).

> [!IMPORTANT]
> Durante a extração, o sistema opera estritamente em modo **Somente Leitura (Read-Only)** nos terminais iDFace para não impactar o reconhecimento facial ao vivo.

---

## Estrutura do Projeto

```text
Backup_Utility_CiD/
├── backend/
│   ├── core/
│   │   ├── detector.py              # Detecção de equipamentos Control iD na rede
│   │   ├── extractor.py             # Orquestração assíncrona de extração e checkpoints
│   │   ├── idface_client.py         # Cliente HTTPX assíncrono para API .fcgi
│   │   ├── logger.py                # Logger rotativo centralizado (logs/bot_backup.log)
│   │   ├── merger.py                # Consolidação Best-Record Wins e detecção de conflitos
│   │   ├── network_utils.py         # Parse de IPs, faixas e sub-redes CIDR
│   │   └── scanner.py               # Varredura paralela de rede
│   ├── models/
│   │   ├── backup_models.py         # Modelos de progresso, auditoria e configurações
│   │   └── device.py                # Modelo ControlIdDevice e estatísticas
│   └── services/
│       ├── exporter_service.py      # Exportação JSON (backup_full.json / audit_report.json)
│       ├── idsecure_api_restorer.py # Sync de fotos via Web API e gerador de ZIP
│       ├── mysql_idsecure_service.py# Injeção PyMySQL e gerador de dump_idsecure_mysql.sql
│       └── sqlite_storage.py        # Persistência SQLite (WAL, índices e checkpoints)
├── frontend/
│   ├── assets/                      # Assets visuais (logo do rodapé)
│   ├── components/                  # Painéis Flet (header, connection, device_selector, progress, audit, restore, footer)
│   ├── styles/theme.py              # Tema Dark Mode corporativo
│   └── app.py                       # Controlador principal da UI Flet
├── tests/                           # Suíte Pytest (unitários, tradutor MySQL, ZIP BOM e E2E com mock)
├── build.ps1                        # Pipeline local de testes + build PyInstaller
├── main.py                          # Entrypoint da aplicação desktop
├── pyproject.toml                   # Configuração de pytest, ruff e mypy
└── requirements.txt                 # Dependências Python
```

---

## Pré-requisitos

- **Sistema Operacional:** Windows 10 ou Windows 11 (64-bit)
- **Python:** 3.10 ou superior
- **Rede:** Acesso na mesma rede local dos terminais Control iD e do servidor iDSecure

---

## Instalação

1. Clone o repositório e acesse a pasta do projeto:
   ```powershell
   git clone <url-do-repositorio>
   cd Backup_Utility_CiD
   ```

2. Crie e ative um ambiente virtual:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```

---

## Executando os Testes

A suíte automatizada cobre cliente `.fcgi`, persistência/deduplicação SQLite, tradução MySQL, geração de ZIP sem BOM duplo e pipeline E2E com servidor mock:

```powershell
python -m pytest tests -v
```

---

## Como Usar

Inicie a aplicação desktop:

```powershell
python main.py
```

### Aba 1: Extração iDFace
1. Informe o IP, faixa (`192.168.1.100-110`) ou CIDR (`/24`) e clique em **Buscar**.
2. Preencha as credenciais do terminal (padrão de fábrica: `admin` / `admin`).
3. Selecione a pasta de destino e inicie o backup. O progresso de objetos e fotos é exibido em tempo real com suporte a pausa/retomada.

### Aba 2: Restauração MySQL / iDSecure
1. Selecione a pasta do backup contendo `backup_controlid.sqlite`.
2. Configure o acesso ao **MySQL** (`localhost:3306`, banco `idsecure`) e/ou à **API iDSecure** (`https://localhost:30443`) e teste a conexão.
3. Execute a injeção direta no MySQL, sincronize as fotos via API ou gere `dump_idsecure_mysql.sql` e `importacao_idsecure.zip`.

---

## Compilando Executável Standalone (.exe)

Para gerar o executável portátil no Windows (executa os testes antes de empacotar):

```powershell
.\build.ps1
```

O binário será gerado em `dist/Backup-Utility-CiD/Backup-Utility-CiD.exe`.

> [!TIP]
> Para detalhes de arquitetura e requisitos, consulte [PRD.md](PRD.md) e [TRD.md](TRD.md).
