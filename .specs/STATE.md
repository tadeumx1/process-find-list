# WSLazy state

## Decisions

| ID | Status | Decision | Reason |
| --- | --- | --- | --- |
| AD-001 | active | Python >=3.10, curses, Linux /proc, comando wslazy; sem dependências externas de runtime | Porta 1 do plano aprovado; execução direta no WSL existente. |
| AD-002 | active | Perfil light da tlc-spec-lean | Padrão registrado no plano aprovado; verificador independente, sem injeção de falhas. |

## Handoff

**Feature**: wslazy
**Where**: concluída; C1–C40 comprovados na rodada 2 independente, HEAD de implementação/testes `e88db7f0b4a6302423ba2f8b90edca51b0c845fa`.
**Next step**: uso pelo usuário; nenhuma implementação pendente.
**Blockers**: nenhum.

Execução: `python3 -m wslazy` ou `.venv/bin/wslazy` (instalado localmente). Testes neste host: `PYTHONPATH=/tmp/wslazy-build-tools python3 -m unittest discover -v`; 44 testes passam. Ferramentas de build estão isoladas em /tmp, sem mudança no Python do sistema. Gate `validate_verification.py` com caminho absoluto do relatório retorna 0.

Limite de validação: perfil light, sem mutações; ações de serviço usam executor simulado; lazydocker é um substituto temporário porque o executável real não está instalado. Coleta de recursos foi executada no WSL real. Mouse, restauração e inicialização instalada foram exercitados em PTY real. UAT humano ainda não realizado.
