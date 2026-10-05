# WSLazy state

## Decisions

| ID | Status | Decision | Reason |
| --- | --- | --- | --- |
| AD-001 | active | Python >=3.10, curses, Linux /proc, comando wslazy; sem dependências externas de runtime | Porta 1 do plano aprovado; execução direta no WSL existente. |
| AD-002 | active | Perfil light da tlc-spec-lean | Padrão registrado no plano aprovado; verificador independente, sem injeção de falhas. |

## Handoff

Plano aprovado em 2026-10-05. Implementação e 44 testes passaram. Próxima etapa: verificação independente C1–C40 sobre `257d712bbdbbb09c75c73131a16d767bebc85307..HEAD`.

Execução: `python3 -m wslazy`. Testes neste host: `PYTHONPATH=/tmp/wslazy-build-tools python3 -m unittest discover -v`. O Python do sistema não tem pip/ensurepip; ferramentas de build estão isoladas em /tmp. Instalação e execução em venv limpo verificadas, sem rede no teste.

Limite de validação: serviços são exercitados por executor simulado e a integração lazydocker por executável temporário, pois o lazydocker não está instalado. Coleta de processos, portas e serviços foi executada no WSL real. Mouse e restauração do terminal foram exercitados em pseudoterminal real.
