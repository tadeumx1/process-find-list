# WSLazy — gerenciador de processos para o terminal

## Problem

Quem desenvolve no WSL precisa alternar entre comandos diferentes para descobrir quais aplicativos estão rodando, quem ocupa uma porta e quais serviços estão ativos. Encerrar uma execução e recuperar um comando recente exige procurar e relacionar essas informações manualmente. O pedido não informa medidas de frequência ou tempo perdido.

O resultado será uma aplicação de terminal inspirada na navegação do lazydocker, com cinco visões: Processos, Aplicativos, Portas, Serviços e Histórico. A interface será em português, operada pelo teclado e pelo mouse, com lista pesquisável e detalhes da seleção. Um botão `Lazydocker` abrirá a ferramenta no mesmo terminal e permitirá voltar ao WSLazy ao encerrá-la.

## Flow

A aplicação reutiliza `/proc`, `ss`, `systemctl` e os arquivos de histórico do shell existentes no Linux; não mantém um inventário paralelo nem modifica esses históricos.

`single module - WSLazy` (door 1).

1. A abertura de `wslazy` entra na interface local e inicia a coleta da distribuição WSL atual; a saída são as cinco visões navegáveis (AC 1–12, 27–29).
2. A seleção e a pesquisa percorrem o retrato coletado e apresentam detalhes do processo, aplicativo, porta, serviço ou comando (AC 2–12, 23).
3. Uma ação sobre processo ou serviço passa por confirmação, valida o alvo e invoca a operação local; seu resultado aparece na interface e uma nova coleta atualiza a lista (AC 13–21).
4. Um comando escolhido no histórico passa por revisão e confirmação; o shell assume o terminal, executa no diretório indicado e devolve o controle à interface com o código de saída (AC 22–26).
5. Cliques nos controles visíveis e atalhos de teclado acionam as mesmas operações e confirmações; a roda do mouse percorre listas e detalhes (AC 33–36).
6. O botão de acesso ao lazydocker ou seu atalho entrega temporariamente o terminal ao executável externo instalado; quando ele termina, a interface restaura sua visão, seleção e pesquisa (AC 37–40).

## Impact

| Front | What changes |
| --- | --- |
| domain | Novo termo: aplicativo significa o agrupamento dos processos pelo nome do executável e UID; não é um catálogo de programas instalados. |
| domain | Serviço significa uma unidade `.service` carregada no systemd, no escopo de sistema ou do usuário, identificado na lista. |
| stored data | Nenhuma migração e nenhum banco novo; os históricos existentes são somente leitura. |
| ambiente | A instalação disponibiliza o comando `wslazy`; apenas ações confirmadas na aplicação enviam sinais, alteram serviços ou executam comandos. |
| ambiente | O botão `Lazydocker` inicia uma ferramenta externa opcional pelo PATH; não instala pacotes nem inicia o Docker automaticamente. |

## Relations

None - nenhuma alteração no formato de dados persistidos. Processos, agrupamentos, portas, serviços e entradas de histórico são retratos em memória.

## Surface

None - não há rotas HTTP ou API. A superfície pública é uma CLI, cujos códigos são códigos de saída de processo:

- `wslazy`: sem argumentos, abre a interface em um terminal Linux; retorna `0` ao sair normalmente ou `1` se o ambiente não permitir iniciar.
- `wslazy --help`: imprime instruções textuais sem iniciar a interface; retorna `0`.
- `wslazy --version`: imprime a versão instalada; retorna `0`.
- `wslazy <argumento desconhecido>`: imprime erro de uso em stderr; retorna `2`.

## Landing

| One-way door | Literal shape | Alternative rejected |
| --- | --- | --- |
| 1 — runtime e distribuição inicial | Aplicação `WSLazy`, comando público `wslazy`, Python `>=3.10`, biblioteca padrão com `curses`, Linux com `/proc`; execução a partir do checkout via `python3 -m wslazy` e instalação local via `pip install .` | Textual exigiria dependências de runtime externas; Go exigiria instalar uma cadeia de compilação que não é necessária para o runtime Python disponível. |

Nenhuma outra decisão exige migração de dados ou cria contrato externo persistido. A organização interna de arquivos será decidida na implementação.

## Criteria

### S1: Encontrar o que está rodando (P1)

**Acceptance Criteria**

1. WHEN a aplicação abre em um terminal Linux THEN o sistema SHALL disponibilizar as visões `Processos`, `Aplicativos`, `Portas`, `Serviços` e `Histórico`, com lista e detalhes do item selecionado.
2. WHEN a visão Processos coleta `/proc` THEN o sistema SHALL listar os PIDs legíveis com usuário, estado, uso de CPU, memória residente e linha de comando, exibindo `—` para campos indisponíveis.
3. WHILE uma visão de recursos está aberta THEN o sistema SHALL iniciar uma nova coleta a cada dois segundos após a coleta anterior e conservar a seleção pela identidade do item quando ele continuar presente.
4. WHEN a visão Aplicativos é selecionada THEN o sistema SHALL agrupar processos por nome do executável e UID, exibindo quantidade, CPU total, memória total e os PIDs integrantes nos detalhes.
5. WHEN a visão Portas é selecionada THEN o sistema SHALL listar sockets TCP em escuta e UDP vinculados, com protocolo, endereço local, porta e todos os pares processo/PID informados por `ss`.
6. IF a coleta de portas não informa um proprietário THEN o sistema SHALL mostrar `proprietário indisponível` sem remover a porta da lista.
7. WHEN a visão Serviços é selecionada THEN o sistema SHALL listar unidades `.service` carregadas no systemd, com nome, escopo `sistema` ou `usuário`, estado e descrição.
8. IF uma fonte está ausente, retorna erro ou excede cinco segundos de coleta THEN o sistema SHALL apresentar a fonte e o motivo da indisponibilidade na visão afetada, mantendo as outras visões acessíveis.
9. WHEN o usuário digita uma pesquisa THEN o sistema SHALL filtrar a visão atual por trecho textual sem distinguir maiúsculas e minúsculas, incluindo PIDs, nomes, comandos e portas nos campos aplicáveis.
10. IF uma visão não contém itens ou a pesquisa não encontra correspondências THEN o sistema SHALL exibir `Nenhum resultado` na área da lista.
11. WHILE a primeira coleta de uma visão está pendente THEN o sistema SHALL exibir `Carregando…` e aceitar navegação e saída.
12. WHEN o usuário navega pelas listas THEN o sistema SHALL ordenar processos e aplicativos por CPU decrescente, portas por número crescente, serviços por escopo e nome e histórico pela posição mais recente no arquivo de origem; empates entre processos usam PID crescente e entre arquivos de histórico usam nome da origem.

**Independent test:** abrir a aplicação com um processo de teste que mantenha uma porta local, localizá-lo pelo PID, conferir o agrupamento e alternar para Serviços.

### S2: Encerrar processos e controlar serviços (P1)

**Acceptance Criteria**

13. WHEN o usuário solicita encerrar ou forçar o encerramento de um processo THEN o sistema SHALL apresentar uma confirmação com PID, comando e sinal `SIGTERM` ou `SIGKILL` antes de enviar o sinal.
14. WHEN o usuário cancela uma confirmação THEN o sistema SHALL voltar à visão anterior sem iniciar a ação pendente.
15. WHEN o usuário confirma um sinal e a identidade PID/início ainda corresponde ao processo selecionado THEN o sistema SHALL enviar somente o sinal escolhido para aquele processo, sem sinalizar o grupo inteiro.
16. IF o processo terminou ou o PID foi reutilizado após a seleção THEN o sistema SHALL recusar a ação com `Processo não está mais disponível` e atualizar a lista, sem sinalizar a nova identidade.
17. IF uma ação recebe erro de permissão THEN o sistema SHALL mostrar `Permissão negada` e permanecer aberto, sem tentar elevação automática de privilégios.
18. WHEN o usuário solicita encerrar a partir de um aplicativo ou porta com vários PIDs THEN o sistema SHALL exigir a escolha de um único PID antes de apresentar a confirmação.
19. WHEN o usuário solicita uma ação em Serviços THEN o sistema SHALL oferecer `iniciar`, `parar` e `reiniciar`, com confirmação que identifica unidade, escopo e ação.
20. WHEN uma ação de serviço é confirmada THEN o sistema SHALL executar a operação no escopo selecionado e apresentar o sucesso, o erro retornado ou o limite de dez segundos de espera, sem repetição automática.
21. WHEN uma ação de processo ou serviço conclui THEN o sistema SHALL iniciar uma nova coleta da visão afetada; uma operação aceita não será apresentada como prova de que o recurso já mudou de estado.

**Independent test:** iniciar um processo descartável, cancelar uma confirmação e comprovar que continua vivo; confirmar SIGTERM e comprovar sua saída. Exercitar ações de serviço com um executor de teste, sem alterar serviços reais durante a validação automatizada.

### S3: Recuperar e executar comandos recentes (P1)

**Acceptance Criteria**

22. WHEN a visão Histórico é aberta THEN o sistema SHALL ler até as últimas 2.000 entradas de cada arquivo disponível entre `$HISTFILE`, `~/.bash_history` e `~/.zsh_history`, sem ler duas vezes o mesmo caminho.
23. WHEN o histórico contém entradas Bash ou Zsh estendido THEN o sistema SHALL apresentar os comandos com sua origem, removendo metadados de timestamp e preservando comandos com continuação; comandos duplicados na mesma origem aparecem uma vez, na ocorrência mais recente.
24. WHEN o usuário escolhe executar um comando do histórico THEN o sistema SHALL abrir uma revisão editável que mostra o comando integral, o shell e o diretório atual, exigindo confirmação explícita antes da execução.
25. WHEN a execução revisada é confirmada THEN o sistema SHALL executar exatamente o texto revisado no shell de origem disponível, usando o diretório exibido, e devolver o controle à interface com o código de saída ao terminar.
26. IF o shell necessário não existe ou o comando não pode iniciar THEN o sistema SHALL informar a falha e retornar à interface, sem tentar outro interpretador silenciosamente.

**Independent test:** usar históricos temporários de Bash e Zsh com duplicatas e comandos multilinha, pesquisar uma entrada e executar um comando inofensivo que imprime o diretório e termina com um código conhecido.

### S4: Usar e instalar pelo terminal (P1)

**Acceptance Criteria**

27. WHEN o usuário pressiona `Tab`/`Shift+Tab`, setas ou `j`/`k`, `/`, `Esc`, `?` e `q` fora de um campo de texto THEN o sistema SHALL, respectivamente, alternar visões, navegar, iniciar pesquisa, fechar a interação atual, abrir ajuda e sair, restaurando o terminal.
28. IF o terminal tem menos de 80 colunas ou 24 linhas THEN o sistema SHALL exibir uma solicitação para ampliar a janela, continuar aceitando `q` e redesenhar a interface quando houver espaço suficiente.
29. IF um processo desaparece ou seus arquivos ficam inacessíveis durante a coleta THEN o sistema SHALL descartar apenas os dados inacessíveis daquele processo e concluir a coleta dos demais.
30. WHEN o usuário executa as formas públicas da CLI THEN o sistema SHALL respeitar as saídas e os códigos definidos em Surface; iniciar sem TTY informa `Terminal interativo necessário` em stderr e retorna `1`.
31. WHEN o usuário segue o README THEN o sistema SHALL poder ser iniciado via `python3 -m wslazy` no checkout e como `wslazy` após instalação em ambiente virtual, sem dependências de runtime de terceiros.
32. The sistema SHALL manter os arquivos de histórico de origem inalterados ao listar, pesquisar e executar entradas pela aplicação.

**Independent test:** instalar em ambiente virtual limpo, verificar CLI e uso sem TTY e percorrer as cinco visões em um pseudoterminal, incluindo redimensionamento e saída.

### S5: Usar o mouse e acessar o lazydocker (P1)

**Acceptance Criteria**

33. WHERE o terminal entrega eventos de mouse THEN o sistema SHALL permitir, com clique esquerdo, alternar as cinco visões, selecionar itens, focar a pesquisa e o editor de comando e acionar os controles visíveis de ações, ajuda, saída e lazydocker.
34. WHERE o terminal entrega eventos de mouse THEN o sistema SHALL permitir percorrer a lista ou os detalhes sob o ponteiro com a roda do mouse, sem alterar a seleção por rolar apenas os detalhes.
35. WHEN uma confirmação ou escolha de PID está aberta THEN o sistema SHALL aceitar tanto navegação e ativação por teclado quanto cliques nas opções e nos botões `Confirmar` e `Cancelar`, mantendo as mesmas validações de alvo e permissão para ambas as entradas.
36. The sistema SHALL disponibilizar um caminho por teclado para toda ação clicável do WSLazy, exibir seus atalhos na ajuda e manter a navegação por teclado utilizável quando o terminal não entregar eventos de mouse.
37. WHEN o usuário clica no botão global `Lazydocker` ou pressiona `D` fora de campos de texto e diálogos THEN o sistema SHALL iniciar uma única instância do executável `lazydocker` encontrado no PATH, em primeiro plano no mesmo terminal e diretório atual, suspendendo a interface do WSLazy durante a execução.
38. WHEN o lazydocker termina THEN o sistema SHALL restaurar a visão, a pesquisa e a seleção anterior do WSLazy quando o item ainda existir, reativar teclado e mouse e apresentar o código de saída da ferramenta.
39. IF o executável `lazydocker` não é encontrado no PATH THEN o sistema SHALL exibir `Lazydocker não encontrado no PATH` e permanecer utilizável, sem instalar a ferramenta automaticamente.
40. IF o lazydocker não pode iniciar THEN o sistema SHALL apresentar o motivo da falha e restaurar a interface com teclado e mouse utilizáveis.

**Independent test:** enviar eventos de clique e rolagem em pseudoterminal, alternar as cinco visões e cancelar uma ação usando o mouse. Usar um executável de teste chamado `lazydocker` em PATH temporário para comprovar entrega e restauração do terminal, diretório, código de saída e tratamento de ausência/falha, sem operar contêineres reais.

## Out of scope

| Excluded | Why |
| --- | --- |
| Processos Windows e outras distribuições WSL | A coleta usa o namespace Linux onde a aplicação é iniciada. |
| Gerenciador próprio de contêineres e conexão SSH | As operações Docker ficam na ferramenta lazydocker aberta pelo botão; não serão reimplementadas dentro do WSLazy. |
| Instalação e configuração automática do lazydocker ou Docker | A integração abre o executável existente no PATH e informa sua ausência. |
| Alterar os controles internos do lazydocker | Enquanto a ferramenta externa ocupa o terminal, seus próprios atalhos e suporte a mouse regem a interação. |
| Encerramento em massa de aplicativos e árvores de processos | A primeira versão seleciona um alvo explícito por ação. |
| Recuperar histórico ainda não gravado pelo shell | Uma aplicação separada não recebe automaticamente o histórico em memória de outros terminais. |
| Recriar diretório, variáveis, aliases e funções da sessão original | Arquivos de histórico não preservam esse contexto; a revisão exibe o contexto atual de execução. |
| Shells diferentes de Bash/Zsh, histórico de Fish e PowerShell | Formatos adicionais ficam para uma extensão posterior. |
| Logs de serviços, gráficos históricos e métricas persistidas | O foco inicial é localizar recursos e agir sobre a seleção atual. |

## Assumptions

| Assumption | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Identidade visual | Painéis compactos em português, cores discretas e atalhos visíveis, inspirados na organização do lazydocker | A referência dada é uma interface de terminal com navegação rápida. | n |
| Histórico entre shells | Não inferir uma cronologia global entre arquivos sem timestamps; usar posições em cada origem conforme AC 12 | Bash pode persistir comandos sem data. | n |
| CPU | Percentual por processo medido entre coletas; primeira amostra exibe `—`; soma pode ultrapassar 100% em máquinas com vários núcleos | Torna a leitura dos processos ativos comparável entre amostras sem fabricar uma medição inicial. | n |
| Local de instalação | Ambiente virtual do usuário, com instruções para expor o executável no PATH | Não exige alterar Python do sistema. | n |
| Entrada de texto | O mouse foca campos; digitação e edição do conteúdo usam o teclado | É o comportamento habitual dos campos em uma aplicação de terminal. | n |

**Open questions:** none - escolhas pendentes de preferência têm valores propostos acima. Plano aprovado pelo usuário em 2026-10-05, incluindo mouse e lazydocker. Perfil de verificação: `light`, padrão da skill; nenhuma declaração de projeto substitui esse padrão.

## Observable

| Surface | Decision | Landing |
| --- | --- | --- |
| Cinco visões | Lista e detalhes | AC 1 |
| Processos e Aplicativos | Campos e agrupamento | AC 2, 4 |
| Portas | Protocolos e proprietário ausente | AC 5, 6 |
| Serviços | Escopos e estados | AC 7 |
| Cinco visões | Vazio | AC 10 |
| Cinco visões | Carregamento | AC 11 |
| Cinco visões | Erro de fonte e prazo | AC 8 |
| Processos, Portas e Serviços | Sem autorização | AC 6, 17, 29 |
| Cinco visões | Densidade e ordenação | AC 1, 12, 28 |
| Cinco visões | Pesquisa e teclado | AC 9, 27 |
| Cinco visões | Clique, foco e rolagem | AC 33, 34 |
| Diálogos e escolha de PID | Mouse e teclado com confirmação equivalente | AC 35 |
| Controles clicáveis e ajuda | Atalhos equivalentes e terminal sem eventos de mouse | AC 36 |
| Botão global `Lazydocker` | Lançamento e retorno à interface | AC 37, 38 |
| Botão global `Lazydocker` | Executável ausente ou falha ao iniciar | AC 39, 40 |
| Processos, Aplicativos e Portas | Confirmação destrutiva e alvo | AC 13–18 |
| Serviços | Confirmação e resultado de operação | AC 19–21 |
| Histórico | Origem, duplicatas e exceções de formato | AC 22, 23 |
| Histórico | Revisão e execução | AC 24–26 |
| CLI `wslazy` | Formato, flags, defaults e códigos de saída | AC 30; Surface |
| CLI `wslazy` | Falha parcial durante o uso | AC 8, 17, 20, 26, 29 |
| README | Estrutura e próxima ação | AC 31; instalação, execução, atalhos e limites em português |
| Interface e CLI | Versionamento de API e limite de requisições | n/a - aplicação local sem API ou clientes remotos |

## Sources

- Pedido do usuário nesta conversa: “uma aplicacao no terminal tipo lazydocker” para listar processos, aplicativos, serviços e portas no WSL, encerrar execuções e recuperar comandos recentes — define a finalidade e a referência de navegação.
- Orientação do usuário nesta conversa: “Usa a skill tlc-spec-lean ao inves da tlc-spec-driven” — define o fluxo de trabalho; o plano é apresentado antes dos checks e da implementação.
- Complemento do usuário nesta conversa: “um botao pra acessar o lazydocker” e “controlar a interface pelo teclado e tambem clicando pelo mouse” — torna obrigatórios o lançador da ferramenta e a interação por ambas as entradas no WSLazy.
