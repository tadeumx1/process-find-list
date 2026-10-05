# WSLazy checks

Profile: light
Plan: `.specs/features/wslazy/plan.md`

40 checks em 5 slices · 1 porta de arquitetura · 0 perguntas abertas.

## Checks

### S1

**C1** - WHEN a aplicação abre em um terminal Linux THEN o sistema SHALL disponibilizar as visões `Processos`, `Aplicativos`, `Portas`, `Serviços` e `Histórico`, com lista e detalhes do item selecionado. (AC 1)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac01 -v`
Status: pending

**C2** - WHEN a visão Processos coleta `/proc` THEN o sistema SHALL listar os PIDs legíveis com usuário, estado, uso de CPU, memória residente e linha de comando, exibindo `—` para campos indisponíveis. (AC 2)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac02 -v`
Status: pending

**C3** - WHILE uma visão de recursos está aberta THEN o sistema SHALL iniciar uma nova coleta a cada dois segundos após a coleta anterior e conservar a seleção pela identidade do item quando ele continuar presente. (AC 3)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac03 -v`
Status: pending

**C4** - WHEN a visão Aplicativos é selecionada THEN o sistema SHALL agrupar processos por nome do executável e UID, exibindo quantidade, CPU total, memória total e os PIDs integrantes nos detalhes. (AC 4)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac04 -v`
Status: pending

**C5** - WHEN a visão Portas é selecionada THEN o sistema SHALL listar sockets TCP em escuta e UDP vinculados, com protocolo, endereço local, porta e todos os pares processo/PID informados por `ss`. (AC 5)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac05 -v`
Status: pending

**C6** - IF a coleta de portas não informa um proprietário THEN o sistema SHALL mostrar `proprietário indisponível` sem remover a porta da lista. (AC 6)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac06 -v`
Status: pending

**C7** - WHEN a visão Serviços é selecionada THEN o sistema SHALL listar unidades `.service` carregadas no systemd, com nome, escopo `sistema` ou `usuário`, estado e descrição. (AC 7)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac07 -v`
Status: pending

**C8** - IF uma fonte está ausente, retorna erro ou excede cinco segundos de coleta THEN o sistema SHALL apresentar a fonte e o motivo da indisponibilidade na visão afetada, mantendo as outras visões acessíveis. (AC 8)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac08 -v`
Status: pending

**C9** - WHEN o usuário digita uma pesquisa THEN o sistema SHALL filtrar a visão atual por trecho textual sem distinguir maiúsculas e minúsculas, incluindo PIDs, nomes, comandos e portas nos campos aplicáveis. (AC 9)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac09 -v`
Status: pending

**C10** - IF uma visão não contém itens ou a pesquisa não encontra correspondências THEN o sistema SHALL exibir `Nenhum resultado` na área da lista. (AC 10)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac10 -v`
Status: pending

**C11** - WHILE a primeira coleta de uma visão está pendente THEN o sistema SHALL exibir `Carregando…` e aceitar navegação e saída. (AC 11)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac11 -v`
Status: pending

**C12** - WHEN o usuário navega pelas listas THEN o sistema SHALL ordenar processos e aplicativos por CPU decrescente, portas por número crescente, serviços por escopo e nome e histórico pela posição mais recente no arquivo de origem; empates entre processos usam PID crescente e entre arquivos de histórico usam nome da origem. (AC 12)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac12 -v`
Status: pending

### S2

**C13** - WHEN o usuário solicita encerrar ou forçar o encerramento de um processo THEN o sistema SHALL apresentar uma confirmação com PID, comando e sinal `SIGTERM` ou `SIGKILL` antes de enviar o sinal. (AC 13)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac13 -v`
Status: pending

**C14** - WHEN o usuário cancela uma confirmação THEN o sistema SHALL voltar à visão anterior sem iniciar a ação pendente. (AC 14)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac14 -v`
Status: pending

**C15** - WHEN o usuário confirma um sinal e a identidade PID/início ainda corresponde ao processo selecionado THEN o sistema SHALL enviar somente o sinal escolhido para aquele processo, sem sinalizar o grupo inteiro. (AC 15)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac15 -v`
Status: pending

**C16** - IF o processo terminou ou o PID foi reutilizado após a seleção THEN o sistema SHALL recusar a ação com `Processo não está mais disponível` e atualizar a lista, sem sinalizar a nova identidade. (AC 16)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac16 -v`
Status: pending

**C17** - IF uma ação recebe erro de permissão THEN o sistema SHALL mostrar `Permissão negada` e permanecer aberto, sem tentar elevação automática de privilégios. (AC 17)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac17 -v`
Status: pending

**C18** - WHEN o usuário solicita encerrar a partir de um aplicativo ou porta com vários PIDs THEN o sistema SHALL exigir a escolha de um único PID antes de apresentar a confirmação. (AC 18)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac18 -v`
Status: pending

**C19** - WHEN o usuário solicita uma ação em Serviços THEN o sistema SHALL oferecer `iniciar`, `parar` e `reiniciar`, com confirmação que identifica unidade, escopo e ação. (AC 19)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac19 -v`
Status: pending

**C20** - WHEN uma ação de serviço é confirmada THEN o sistema SHALL executar a operação no escopo selecionado e apresentar o sucesso, o erro retornado ou o limite de dez segundos de espera, sem repetição automática. (AC 20)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac20 -v`
Status: pending

**C21** - WHEN uma ação de processo ou serviço conclui THEN o sistema SHALL iniciar uma nova coleta da visão afetada; uma operação aceita não será apresentada como prova de que o recurso já mudou de estado. (AC 21)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac21 -v`
Status: pending

### S3

**C22** - WHEN a visão Histórico é aberta THEN o sistema SHALL ler até as últimas 2.000 entradas de cada arquivo disponível entre `$HISTFILE`, `~/.bash_history` e `~/.zsh_history`, sem ler duas vezes o mesmo caminho. (AC 22)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac22 -v`
Status: pending

**C23** - WHEN o histórico contém entradas Bash ou Zsh estendido THEN o sistema SHALL apresentar os comandos com sua origem, removendo metadados de timestamp e preservando comandos com continuação; comandos duplicados na mesma origem aparecem uma vez, na ocorrência mais recente. (AC 23)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac23 -v`
Status: pending

**C24** - WHEN o usuário escolhe executar um comando do histórico THEN o sistema SHALL abrir uma revisão editável que mostra o comando integral, o shell e o diretório atual, exigindo confirmação explícita antes da execução. (AC 24)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac24 -v`
Status: pending

**C25** - WHEN a execução revisada é confirmada THEN o sistema SHALL executar exatamente o texto revisado no shell de origem disponível, usando o diretório exibido, e devolver o controle à interface com o código de saída ao terminar. (AC 25)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac25 -v`
Status: pending

**C26** - IF o shell necessário não existe ou o comando não pode iniciar THEN o sistema SHALL informar a falha e retornar à interface, sem tentar outro interpretador silenciosamente. (AC 26)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac26 -v`
Status: pending

### S4

**C27** - WHEN o usuário pressiona `Tab`/`Shift+Tab`, setas ou `j`/`k`, `/`, `Esc`, `?` e `q` fora de um campo de texto THEN o sistema SHALL, respectivamente, alternar visões, navegar, iniciar pesquisa, fechar a interação atual, abrir ajuda e sair, restaurando o terminal. (AC 27)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac27 -v`
Status: pending

**C28** - IF o terminal tem menos de 80 colunas ou 24 linhas THEN o sistema SHALL exibir uma solicitação para ampliar a janela, continuar aceitando `q` e redesenhar a interface quando houver espaço suficiente. (AC 28)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac28 -v`
Status: pending

**C29** - IF um processo desaparece ou seus arquivos ficam inacessíveis durante a coleta THEN o sistema SHALL descartar apenas os dados inacessíveis daquele processo e concluir a coleta dos demais. (AC 29)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac29 -v`
Status: pending

**C30** - WHEN o usuário executa as formas públicas da CLI THEN o sistema SHALL respeitar as saídas e os códigos definidos em Surface; iniciar sem TTY informa `Terminal interativo necessário` em stderr e retorna `1`. (AC 30)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac30 -v`
Status: pending

**C31** - WHEN o usuário segue o README THEN o sistema SHALL poder ser iniciado via `python3 -m wslazy` no checkout e como `wslazy` após instalação em ambiente virtual, sem dependências de runtime de terceiros. (AC 31)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac31 -v`
Status: pending

**C32** - The sistema SHALL manter os arquivos de histórico de origem inalterados ao listar, pesquisar e executar entradas pela aplicação. (AC 32)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac32 -v`
Status: pending

### S5

**C33** - WHERE o terminal entrega eventos de mouse THEN o sistema SHALL permitir, com clique esquerdo, alternar as cinco visões, selecionar itens, focar a pesquisa e o editor de comando e acionar os controles visíveis de ações, ajuda, saída e lazydocker. (AC 33)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac33 -v`
Status: pending

**C34** - WHERE o terminal entrega eventos de mouse THEN o sistema SHALL permitir percorrer a lista ou os detalhes sob o ponteiro com a roda do mouse, sem alterar a seleção por rolar apenas os detalhes. (AC 34)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac34 -v`
Status: pending

**C35** - WHEN uma confirmação ou escolha de PID está aberta THEN o sistema SHALL aceitar tanto navegação e ativação por teclado quanto cliques nas opções e nos botões `Confirmar` e `Cancelar`, mantendo as mesmas validações de alvo e permissão para ambas as entradas. (AC 35)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac35 -v`
Status: pending

**C36** - The sistema SHALL disponibilizar um caminho por teclado para toda ação clicável do WSLazy, exibir seus atalhos na ajuda e manter a navegação por teclado utilizável quando o terminal não entregar eventos de mouse. (AC 36)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac36 -v`
Status: pending

**C37** - WHEN o usuário clica no botão global `Lazydocker` ou pressiona `D` fora de campos de texto e diálogos THEN o sistema SHALL iniciar uma única instância do executável `lazydocker` encontrado no PATH, em primeiro plano no mesmo terminal e diretório atual, suspendendo a interface do WSLazy durante a execução. (AC 37)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac37 -v`
Status: pending

**C38** - WHEN o lazydocker termina THEN o sistema SHALL restaurar a visão, a pesquisa e a seleção anterior do WSLazy quando o item ainda existir, reativar teclado e mouse e apresentar o código de saída da ferramenta. (AC 38)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac38 -v`
Status: pending

**C39** - IF o executável `lazydocker` não é encontrado no PATH THEN o sistema SHALL exibir `Lazydocker não encontrado no PATH` e permanecer utilizável, sem instalar a ferramenta automaticamente. (AC 39)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac39 -v`
Status: pending

**C40** - IF o lazydocker não pode iniciar THEN o sistema SHALL apresentar o motivo da falha e restaurar a interface com teclado e mouse utilizáveis. (AC 40)
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac40 -v`
Status: pending

## Coverage

| Set (size) | Member -> proof | Unproven |
| --- | --- | --- |
| Visões (5) | Processos C1 · Aplicativos C1 · Portas C1 · Serviços C1 · Histórico C1 | - |
| Fontes (4) | /proc C2 · ss C5 · systemctl C7 · histórico C22 | - |
| Estados da visão (4) | dados C1 · vazio C10 · carregando C11 · erro C8 | - |
| Sinais (2) | SIGTERM C15 · SIGKILL C15 | - |
| Ações de serviço (3) | iniciar C20 · parar C20 · reiniciar C20 | - |
| Escopos de serviço (2) | sistema C7 · usuário C7 | - |
| Histórico (3) | HISTFILE C22 · Bash C23 · Zsh C23 | - |
| CLI e saídas (5) | interativo-0 C27 · sem-TTY-1 C30 · help-0 C30 · version-0 C30 · argumento-2 C30 | - |
| Entrada (2) | teclado C27 · mouse C33 | - |
| Mouse (4) | clique C33 · rolagem-lista C34 · rolagem-detalhes C34 · confirmação C35 | - |
| Lazydocker (4) | início C37 · retorno C38 · ausente C39 · falha C40 | - |
| Porta de runtime (3) | python-module C31 · comando-instalado C31 · sem-runtime-externo C31 | - |

## Swept

- validation: C9, C13, C18, C24, C28, C30
- failure modes: C8, C16, C17, C20, C26, C29, C39, C40
- idempotency: C14, C20, C23, C37 — cancelar não executa, sem repetição automática, deduplicação de histórico e execução modal única
- authorization: C6, C17 — permissões do usuário Linux, sem elevação automática; rate limits n/a - interface local
- concurrency: C3, C11, C16, C29 — coleta em segundo plano, seleção por identidade e pidfd para impedir sinal em PID reutilizado
- data lifecycle: C22, C32 — retratos em memória e arquivos de origem somente leitura
- dependency failure: C8, C26, C39, C40
- state transitions: C14, C15, C20, C21, C25, C38
- observability: C8, C17, C20, C25, C38 — resultados e erros na interface; métricas persistidas n/a - fora do escopo

## Handoff

- Base: projeto vazio; `wc -c plan.md` = 19.118 bytes / 4 ≈ 4.780 tokens de entrada. Não há código prévio, manifesto ou runner a reaproveitar; os proofs usam o runner `unittest` da biblioteca padrão Python e seletores específicos que serão criados antes da implementação.
- Estimativa de novos arquivos e testes: S1 20 KB, S2 12 KB, S3 12 KB, S4 16 KB, S5 16 KB; total 76 KB / 4 ≈ 19k tokens, mais plano e checks ≈ 8k; leitura e iterações estimadas em 54k, abaixo do orçamento padrão de 150k.
- Mechanism: one builder; verificação independente após o último commit. Perfil light: proofs e evidência localizada; não inclui injeção de falhas.
