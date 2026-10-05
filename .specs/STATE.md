# WSLazy state

## Decisions

| ID | Status | Decision | Reason |
| --- | --- | --- | --- |
| AD-001 | active | Python >=3.10, curses, Linux /proc, comando wslazy; sem dependências externas de runtime | Porta 1 do plano aprovado; execução direta no WSL existente. |
| AD-002 | active | Perfil light da tlc-spec-lean | Padrão registrado no plano aprovado; verificador independente, sem injeção de falhas. |

## Handoff

**Feature**: wslazy
**Where**: C1–C40 implementados; rodada 1 independente encontrou seis lacunas de prova, corrigidas com assertions adicionais sem modificar a implementação.
**Next step**: rodada 2 do verificador sobre o novo HEAD, com todos os proofs novamente e revisão focada em C15, C16, C30, C31, C32 e C35.
**Blockers**: nenhum.

Execução: `python3 -m wslazy` ou `.venv/bin/wslazy` (instalado localmente). Testes neste host: `PYTHONPATH=/tmp/wslazy-build-tools python3 -m unittest discover -v`; 44 testes passam. Ferramentas de build estão isoladas em /tmp, sem mudança no Python do sistema.

Limite de validação: ações de serviço usam executor simulado; lazydocker é um substituto temporário porque o executável real não está instalado. Coleta de recursos foi executada no WSL real. Mouse, restauração e inicialização instalada foram exercitados em PTY real. UAT humano ainda não realizado.
