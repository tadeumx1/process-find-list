# WSLazy verification

**Verdict**: PASS
**Profile**: light
**Diff range**: 257d712bbdbbb09c75c73131a16d767bebc85307..e88db7f0b4a6302423ba2f8b90edca51b0c845fa
**Round**: 2 - scoped
**Verifier**: independent sub-agent (author != verifier), `/root/verify_wslazy`

40/40 checks com evidência localizada, 44 testes passaram. Os seis checks com lacunas na rodada 1 agora têm provas adicionais. Nenhuma alteração na implementação foi necessária.

## Execution

Verified at `e88db7f0b4a6302423ba2f8b90edca51b0c845fa`, árvore inicialmente limpa, em 2026-10-05. Executado novamente o conjunto completo:

`PYTHONPATH=/tmp/wslazy-build-tools python3 -m unittest discover -v`

Resultado: exit 0, `Ran 44 tests in 7.115s`, `OK`. A saída mostrou individualmente `tests.test_acceptance.Acceptance.test_ac01` até `test_ac40`, todos `ok`, além de `test_bash_escaped_continuation`, `test_click_does_not_confirm_twice`, `test_slow_collector_keeps_ui_responsive` e `test_terminals_suspend_and_resume_mouse`, todos `ok`. As ferramentas em `/tmp/wslazy-build-tools` são somente dependências do build/teste, não do runtime.

Escopo da revisão: diff `af29c8de588d71827a18670882be34c6f936ce64..e88db7f0b4a6302423ba2f8b90edca51b0c845fa`, C15/C16/C30/C31/C32/C35 e helpers modificados. `tests/terminal.py` também serve C27; sua nova assinatura conserva os defaults, e C27 foi reavaliado e executado. Não houve mudança no setup compartilhado de Acceptance, na implementação ou nos claims/proofs. Os demais verdicts são carried from `af29c8de588d71827a18670882be34c6f936ce64`; todas as citações de `tests/test_acceptance.py` foram atualizadas para o HEAD atual mediante `rg -n -A 28 'def test_ac' tests/test_acceptance.py`.

## Checks

C15, C16, C27, C30, C31, C32 e C35: verified at `e88db7f0b4a6302423ba2f8b90edca51b0c845fa`. Demais conclusões: carried from `af29c8de588d71827a18670882be34c6f936ce64`, proofs reexecutados no novo HEAD. Em cada linha, `test_acNN` significa o método completo `tests.test_acceptance.Acceptance.test_acNN`, cujo resultado individual foi `ok`.

| Check | Claim | Proof run | Evidence | Result |
| --- | --- | --- | --- | --- |
| C1 | Cinco visões, lista e detalhes | `test_ac01` exit 0 | `tests/test_acceptance.py:80` — `self.assertEqual(VIEWS, ('Processos','Aplicativos','Portas','Serviços','Histórico'))`; `tests/test_acceptance.py:84` — `self.assertIn('Detalhes', text)` | PASS |
| C2 | Campos dos processos e indisponibilidade | `test_ac02` exit 0 | `tests/test_acceptance.py:90` — `self.assertEqual((p.pid,p.uid,p.name,p.command,p.state,p.memory,p.start), (123,1000,'python','python app.py','S',2*os.sysconf('SC_PAGE_SIZE'),100))`; `tests/test_acceptance.py:97` — `self.assertIn('—', core.make_snapshot(0, [dataclasses.replace(p,cpu=None)]).items[0].cells)` | PASS |
| C3 | Atualização em 2s, identidade preservada | `test_ac03` exit 0 | `tests/test_acceptance.py:103` — `self.assertEqual(self.app.current().payload.pid,456)`; `tests/test_acceptance.py:106` e `:109` — `self.assertEqual(self.backend.calls,[])` antes de 12 e `self.assertEqual(self.backend.calls,[0])` em 12 | PASS |
| C4 | Agrupamento por executável/UID e totais | `test_ac04` exit 0 | `tests/test_acceptance.py:113` — `self.assertEqual(len(groups),2)`; `tests/test_acceptance.py:115` — `self.assertEqual((g.name,g.cpu,g.memory,[p.pid for p in g.processes]),('python',15,5120,[1,2]))` | PASS |
| C5 | TCP/UDP e todos os proprietários retornados | `test_ac05` exit 0 | `tests/test_acceptance.py:124` — `self.assertEqual([(p.protocol,p.address,p.port) for p in ports],[('udp','127.0.0.1',53),('tcp','[::]',8000)])`; `:125` — `self.assertEqual(ports[1].owners,[('python',12),('worker',13)])` | PASS |
| C6 | Porta sem proprietário permanece | `test_ac06` exit 0 | `tests/test_acceptance.py:130` — `self.assertEqual(len(s.items),1)`; `:131` — `self.assertIn('proprietário indisponível',s.items[0].details)` | PASS |
| C7 | Serviços nos dois escopos com estado/descrição | `test_ac07` exit 0 | `tests/test_acceptance.py:137` — `self.assertEqual([(s.scope,s.name,s.state,s.description) for s in services], [('sistema','db.service','active/running','Database'),('sistema','idle.service','inactive/dead','Idle'), ('usuário','db.service','active/running','Database'),('usuário','idle.service','inactive/dead','Idle')])` | PASS |
| C8 | Erros/prazo da fonte não bloqueiam navegação | `test_ac08` exit 0 + regressão lenta | `tests/test_acceptance.py:145` — `self.assertIn('ss',s.error)`; `tests/test_regressions.py:34` — `self.assertIn('5 segundos',app.snapshots[0].error)` e `:35` — `self.assertEqual(app.view,1)` | PASS |
| C9 | Pesquisa textual sem distinguir caixa | `test_ac09` exit 0 | `tests/test_acceptance.py:158` define `('PYTHON',123),('123',123),('NODE',456)`; `:160` — `self.assertEqual([i.payload.pid for i in self.app.filtered()],[expected])`; `:163` — `self.assertEqual(len(self.app.filtered()),1)` para porta 8123 | PASS |
| C10 | Estado vazio | `test_ac10` exit 0 | `tests/test_acceptance.py:167` e `:169` — `self.assertIn('Nenhum resultado',self.screen.text())`, sem itens e sem correspondência | PASS |
| C11 | Carregamento com navegação/saída | `test_ac11` exit 0 | `tests/test_acceptance.py:173` — `self.assertIn('Carregando',self.screen.text())`; `:175` — `self.assertFalse(self.app.running)` | PASS |
| C12 | Ordenações definidas | `test_ac12` exit 0 | `tests/test_acceptance.py:178` — `self.assertEqual([i.payload.pid for i in core.make_snapshot(0,[process(5,cpu=1),process(3,cpu=8),process(2,cpu=8)]).items],[2,3,5])`; `:185` — `self.assertEqual([i.payload.command for i in core.make_snapshot(4,es).items],['new','other','old'])`; aplicativos/portas/serviços em `:180`, `:181`, `:183` | PASS |
| C13 | Confirmação mostra PID/comando/sinal antes de agir | `test_ac13` exit 0 | `tests/test_acceptance.py:191` — `self.assertIn('123',self.screen.text()); self.assertIn('python app.py',self.screen.text())`; `:192` — `self.assertIn(sig,self.screen.text()); self.assertEqual(self.backend.operations,[])`, para ambos os sinais | PASS |
| C14 | Cancelar não executa e retorna | `test_ac14` exit 0 | `tests/test_acceptance.py:197` — `self.assertIsNone(self.app.dialog); self.assertEqual(self.backend.operations,[])`; `:198` — `self.assertEqual(self.app.view,0)` | PASS |
| C15 | Sinal escolhido apenas no processo selecionado | `test_ac15` exit 0 | `tests/test_acceptance.py:202` e `:203` criam alvo e controle no mesmo grupo isolado; `:207` — `self.assertEqual(child.wait(timeout=2),-sig)`; `:208` — `self.assertIsNone(control.poll(), 'signal must not reach another PID in the same group')`, para SIGTERM/SIGKILL | PASS |
| C16 | Identidade obsoleta recusada e lista atualizada | `test_ac16` exit 0 | `tests/test_acceptance.py:223` — `self.assertIn('Processo não está mais disponível',self.app.message)`; `:224` — `self.assertIn(0,self.backend.calls)`; `:225` — `self.assertEqual(self.app.filtered(),[])`; `:226` — `self.assertIsNone(child.poll())`, após confirmação pela UI com identidade alterada | PASS |
| C17 | Permissão negada mantém aplicação aberta | `test_ac17` exit 0 | `tests/test_acceptance.py:237` — `self.assertIn('Permissão negada',self.app.message)`; `:238` — `self.assertTrue(self.app.running)` | PASS |
| C18 | Múltiplos PIDs exigem escolha única | `test_ac18` exit 0 | `tests/test_acceptance.py:243` — `self.assertEqual(self.app.dialog.kind,'choose')`; `:246` — `self.assertIn('PID: 2',self.screen.text())`; porta também exige escolha em `:252` | PASS |
| C19 | Três ações de serviço confirmadas com unidade/escopo | `test_ac19` exit 0 | `tests/test_acceptance.py:256` percorre `('iniciar','parar','reiniciar')`; `:258` — `for value in ('demo.service','usuário',action): self.assertIn(value,self.screen.text())`; `:259` — `self.assertEqual(self.backend.operations,[])` | PASS |
| C20 | Operação no escopo, timeout 10s e sem repetição | `test_ac20` exit 0 | `tests/test_acceptance.py:270` — `self.assertEqual('--user' in argv,scope=='usuário')`; `:271` — `self.assertEqual(run.call_args.kwargs['timeout'],10)`; `:275` — `self.assertEqual(run.call_count,1)` | PASS |
| C21 | Ações recolhem dados sem afirmar término | `test_ac21` exit 0 | `tests/test_acceptance.py:281` — `self.assertIn(0,self.backend.calls)`; `:283` — `self.assertNotIn('encerrado',self.app.message)`; `:286` — `self.assertIn(3,self.backend.calls)` | PASS |
| C22 | Últimas 2.000 entradas/caminhos únicos | `test_ac22` exit 0 | `tests/test_acceptance.py:293` — `self.assertEqual(len(b),2000)`; `:294` — `self.assertEqual({e.command for e in b},{f'echo {i}' for i in range(3,2003)})`; `:295` — `self.assertEqual(len(entries),2001)` | PASS |
| C23 | Bash/Zsh, metadados, continuação e deduplicação | `test_ac23` exit 0 + regressão Bash | `tests/test_acceptance.py:303` — `self.assertEqual(b,['echo a','printf "a\nb"'])`; `:304` — `self.assertEqual(z,['echo z','echo first\necho second'])` | PASS |
| C24 | Revisão editável mostra contexto antes da execução | `test_ac24` exit 0 | `tests/test_acceptance.py:312` — `for value in ('echo old','bash',os.getcwd()): self.assertIn(value,self.screen.text())`; `:314` — `self.assertEqual(self.app.dialog.text,'echo old!')`; `:315` — `self.assertFalse(run.called)` | PASS |
| C25 | Texto revisado/cwd/código de saída | `test_ac25` exit 0 | `tests/test_acceptance.py:320` — `self.assertEqual(code,7)`; `:321` — `self.assertEqual(output.read_text().strip(),str(self.home))`; `:326` — `self.assertEqual(calls[0][0][-2:],['-c','echo revised'])`; `:328` — `self.assertIn('7',self.app.message)` | PASS |
| C26 | Shell ausente/falha de execução são informados | `test_ac26` exit 0 | `tests/test_acceptance.py:333` — `self.assertRaisesRegex(core.SourceError,'Shell.*não encontrado')`; `:337` — `self.assertIn('cannot start',self.app.message); self.assertTrue(self.app.running)` | PASS |
| C27 | Teclado e terminal restaurado | `test_ac27` exit 0 | `tests/test_acceptance.py:341` a `:351` verificam seleções, visões, busca, ajuda e saída; `:354` — `self.assertEqual(result['exit'],0)`; `:355` — `self.assertTrue(result['restored'])` em PTY real | PASS |
| C28 | Tamanho mínimo e retorno após ampliar | `test_ac28` exit 0 | `tests/test_acceptance.py:360` — `self.assertIn('80',self.screen.text()); self.assertIn('24',self.screen.text())`; `:362` — `self.assertIn('Processos',self.screen.text())`; `:363` — `self.assertFalse(self.app.running)` | PASS |
| C29 | Processo inacessível não interrompe demais | `test_ac29` exit 0 | `tests/test_acceptance.py:368` e `:374` — `self.assertEqual([p.pid for p in core.ProcessSampler(root).sample()],[123])`, com stat inválido e PermissionError | PASS |
| C30 | CLI e canais de saída definidos | `test_ac30` exit 0 | `tests/test_acceptance.py:379` — `self.assertEqual(r.returncode,code)`; `:382` — `self.assertIn(text,r.stderr)`; `:383` — `self.assertEqual(r.stdout,'')` nos erros; `:385` — `self.assertIn(text,r.stdout)` e `:386` — `self.assertEqual(r.stderr,'')` em help/version | PASS |
| C31 | Início no checkout/venv e runtime stdlib | `test_ac31` exit 0 | `tests/test_acceptance.py:393` — `self.assertEqual(result['requires'],[])`; `:394` — `self.assertEqual(result['interactive']['exit'],0)`; `:395` — `self.assertTrue(result['interactive']['restored'])`; `:397` — `self.assertIn('Processos',result['interactive']['text'])`. Instalação por fonte em `tests/install.py:26`, ambiente limpo em `:29` e PTY instalado em `:35` | PASS |
| C32 | Histórico não alterado ao executar | `test_ac32` exit 0 | `tests/test_acceptance.py:422` — `self.assertEqual(p.read_bytes(),original[p])`; `:423` — `self.assertEqual(zsh.read_bytes(),original[zsh])`; `:424` — `self.assertEqual(ran,[('bash','harmless',0),('zsh','harmless',0)])`, após shells reais | PASS |
| C33 | Cliques nas visões/linhas/campos/controles | `test_ac33` exit 0 + C37 | `tests/test_acceptance.py:428` — `self.assertEqual(self.app.view,index)`; `:430` — `self.assertEqual(self.app.current().payload.pid,2)`; `:437` — `self.assertEqual(self.app.dialog.text,'echo hi!')`; clique Lazydocker em `:495` — `self.assertEqual(len(calls),1)` | PASS |
| C34 | Roda na lista/detalhes e seleção preservada | `test_ac34` exit 0 | `tests/test_acceptance.py:443` — `self.assertGreater(self.app.selected[0],0)`; `:448` — `self.assertGreater(self.app.detail_scroll,0)`; `:449` — `self.assertEqual(self.app.selected[0],0)` | PASS |
| C35 | Confirmação por mouse/teclado mantém validações | `test_ac35` exit 0 | `tests/test_acceptance.py:455` — `self.assertEqual(self.backend.operations,[('signal',123,signal.SIGTERM)])`; `:458` — `self.assertEqual(self.app.dialog.target.pid,2)`; `:472` — `self.assertIn(message,self.app.message)`; `:473` — `self.assertEqual(self.backend.operations,before)`; `:474` — `self.assertTrue(self.app.running)`, para ambos os erros e entradas definidos em `:460`–`:470` | PASS |
| C36 | Ajuda de atalhos e teclado sem mouse | `test_ac36` exit 0 | `tests/test_acceptance.py:480` — `for key in ('Tab','j/k','/','D','x','K','s','t','r','Enter','q'): self.assertIn(key,text)`; `:483` — `self.assertEqual(self.app.view,1)` após erro de mousemask | PASS |
| C37 | Lazydocker por clique/D, mesmo terminal/cwd | `test_ac37` exit 0 + PTY externo | `tests/test_acceptance.py:496` — `self.assertEqual(calls[0][0],[str(exe)])`; `:497` — `self.assertEqual((self.home/'marker').read_text(),str(self.home))`; `tests/test_regressions.py:86` — `self.assertEqual(marker.read_text(),'True')` comprova ICANON no filho lançado pelo clique real | PASS |
| C38 | Restaura visão/pesquisa/seleção e entradas | `test_ac38` exit 0 + PTY externo | `tests/test_acceptance.py:508` — `self.assertEqual((self.app.view,self.app.selected[0],self.app.queries[0]),(0,1,'python'))`; `tests/test_regressions.py:88` — `read_until(b'Atalhos e ajuda')` após clique real no retorno; `:92` — `self.assertEqual(termios.tcgetattr(slave),before)` | PASS |
| C39 | Lazydocker ausente mantém UI aberta | `test_ac39` exit 0 | `tests/test_acceptance.py:515` — `self.assertIn('Lazydocker não encontrado no PATH',self.app.message)`; `:516` — `self.assertTrue(self.app.running)` | PASS |
| C40 | Falha de lançamento informa motivo/aceita entradas | `test_ac40` exit 0 | `tests/test_acceptance.py:521` — `self.assertIn('launch failed',self.app.message)`; `:523` — `self.assertEqual(self.app.view,1)` por teclado; `:524` — `self.assertEqual(self.app.view,0)` por clique | PASS |

## Resolved gaps

Verified at `e88db7f0b4a6302423ba2f8b90edca51b0c845fa`. Não restam findings abertos da rodada 1.

- **G1/C15:** alvo e processo-controle compartilham grupo isolado. Ambos os sinais encerram somente o alvo; a assertion observa o controle vivo (`tests/test_acceptance.py:208`).
- **G2/C16/C35:** identidade obsoleta percorre UI → core real → erro → nova coleta; o processo continua vivo (`tests/test_acceptance.py:223`). Os caminhos de clique e teclas `x`, Tab, Enter recebem os mesmos erros de permissão/identidade e verificam mensagem, ausência de operação e UI aberta (`tests/test_acceptance.py:460`).
- **G3/C32:** Bash e Zsh reais produzem `harmless` com saída zero, enquanto os dois arquivos temporários permanecem idênticos (`tests/test_acceptance.py:422`). A comparação com `original` remete aos bytes capturados no mesmo método em `:410`.
- **G4/C31:** instalação por wheel e por fonte via `pip install . --no-index --no-build-isolation --force-reinstall`, seguida de PTY real do executável instalado fora do checkout, sem PYTHONPATH/PYTHONHOME. A interface abre, mostra Processos, sai com 0 e restaura termios (`tests/test_acceptance.py:394`; `tests/install.py:26`; `tests/install.py:35`). As flags extras tornam o teste offline usando build tools preparadas; não alteram as dependências de runtime.
- **G5/C30:** mensagens verificadas separadamente em stderr/stdout, com o outro canal vazio (`tests/test_acceptance.py:382`).

Nenhuma assertion anterior foi removida ou enfraquecida no diff. O autor registrou as lições da primeira rodada em `.specs/lessons.json`; este Verifier alterou somente este relatório.

## Level and sampling

Carried from `af29c8de588d71827a18670882be34c6f936ce64`, atualizado para as provas adicionais verified at `e88db7f0b4a6302423ba2f8b90edca51b0c845fa`:

- Coletores `/proc` usam arquivos controlados; sinalização usa processos descartáveis reais e pidfd. `ss` e `systemctl` são simulados. Nenhum serviço real foi alterado. O plano aceita executor simulado para serviços.
- A maior parte da UI é exercitada com tela simulada e chamadas ao controlador. Há PTY real para o checkout e instalação, além do clique de lançamento do executável externo, retorno, novo clique e restauração de termios. Não houve ensaio de todas as visões/populações em Windows Terminal/WSL real.
- C1/C3/C10/C11 amostram conteúdo/seleção principalmente em Processos. C8 amostra erros de `ss` e atraso de `/proc`. C9 amostra processos e porta, C22 limite de 2.000 entradas em Bash com Zsh curto, C29 stat inválido e PermissionError. C36 comprova ajuda e navegação sem mouse, sem percorrer exaustivamente cada atalho. São limitações de amostragem do perfil light, não uma recomputação do Coverage.
- C25 executa Bash real e confere a entrega do texto revisado ao runner em teste separado; C32 acrescenta execução real de Bash e Zsh para preservação dos históricos. C40 exercita falha de runner na UI simulada; restauração real de termios é provada no sucesso do executável substituto, não numa falha de exec.
- As novas assertions eliminam as seis lacunas concretas da rodada 1. O perfil light não inclui mutações e não demonstra que toda regressão plausível faria a suíte falhar.

## Binding sources

Carried from `af29c8de588d71827a18670882be34c6f936ce64`: lidos integralmente `plan.md`, `checks.md` e os três pedidos do usuário reproduzidos em `plan.md` → `Sources`: TUI tipo lazydocker para recursos WSL e histórico; uso da skill lean; botão lazydocker e controle por teclado e mouse. Não há mockup externo nem contrato remoto indicado. Não há contradição identificada entre esses pedidos reproduzidos e os claims. Auditoria exaustiva de composição por tela não faz parte do perfil light. O diff desta rodada não muda a interface nem os critérios.

## Coverage and policy

Carried from `af29c8de588d71827a18670882be34c6f936ce64`: Coverage lido, não recomputado — perfil light. Não há seção `Test policy` nos checks. `Swept` relido: nenhuma linha delega obrigação a `existing`; todas referenciam checks novos. Os `n/a` são escolhas de escopo aprovadas. Sem injeção de falhas, conforme perfil light. O diff desta rodada não altera essas decisões.

## Human judgment

Carried from `af29c8de588d71827a18670882be34c6f936ce64`: UAT humano não realizado. Permanecem sem avaliação humana a legibilidade/densidade dos painéis, conforto da navegação e adequação visual à referência lazydocker. Este PASS corresponde à verificação automatizada no perfil light, sem declarar aprovação humana.

## Gate

Verified at `e88db7f0b4a6302423ba2f8b90edca51b0c845fa`. Suite: 44 passed, 0 failed, exit 0. Executado `python3 /home/matheus/.codex/skills/tlc-spec-lean/scripts/validate_verification.py /home/matheus/process-find-list/.specs/features/wslazy`: exit 0, `0 error(s), 0 warning(s) across [wslazy]`. O caminho absoluto da pasta da feature evita a colisão com o módulo `wslazy` e segue o formato aceito pelo script.
