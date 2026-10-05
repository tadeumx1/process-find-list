# WSLazy verification

**Verdict**: FAIL
**Profile**: light
**Diff range**: 257d712bbdbbb09c75c73131a16d767bebc85307..af29c8de588d71827a18670882be34c6f936ce64
**Round**: 1 - full
**Verifier**: independent sub-agent (author != verifier), `/root/verify_wslazy`

44 testes passaram, incluindo todos os 40 métodos nomeados nos proofs. Há evidência localizada para todos os checks; 34 recebem PASS no nível light e 6 têm lacunas específicas de prova. FAIL não significa que foi demonstrado um defeito na implementação: as lacunas abaixo impedem afirmar que todas as obrigações estão provadas.

## Execution

Executado no HEAD `af29c8de588d71827a18670882be34c6f936ce64`, árvore inicialmente limpa, em 2026-10-05:

`PYTHONPATH=/tmp/wslazy-build-tools python3 -m unittest discover -v`

Resultado: exit 0, `Ran 44 tests in 3.839s`, `OK`. A saída mostrou individualmente `tests.test_acceptance.Acceptance.test_ac01` até `test_ac40`, todos `ok`, além de `test_bash_escaped_continuation`, `test_click_does_not_confirm_twice`, `test_slow_collector_keeps_ui_responsive` e `test_terminals_suspend_and_resume_mouse`, todos `ok`. As ferramentas em `/tmp/wslazy-build-tools` são somente dependências do build/teste, não do runtime.

Os seletores foram localizados com `rg -n -A 28 'def test_ac' tests/test_acceptance.py`; as regressões com `rg -n -A 70 'def test_' tests/test_regressions.py`. Todos os arquivos de teste são novos no diff completo. O diff de checks preserva os claims e proofs: altera status e acrescenta o handoff.

## Checks

Em cada linha, `test_acNN` significa o método completo `tests.test_acceptance.Acceptance.test_acNN`, executado na invocação batched acima com resultado `ok`. As assertions abaixo reproduzem as expressões relevantes; limitações transversais constam após a tabela.

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
| C15 | Sinal escolhido apenas no processo selecionado | `test_ac15` exit 0 | `tests/test_acceptance.py:206` — `self.assertEqual(child.wait(timeout=2),-sig)`, para SIGTERM/SIGKILL. Nenhuma assertion observa um segundo processo do mesmo grupo após a ação; falta a exclusividade prometida. G1. | FAIL |
| C16 | Identidade obsoleta recusada e lista atualizada | `test_ac16` exit 0 | `tests/test_acceptance.py:214` — `self.assertRaisesRegex(core.SourceError,'Processo não está mais disponível')`; `:216` — `self.assertIsNone(child.poll())`. Exercita o core; nenhuma assertion verifica atualização da UI nessa falha. G2. | FAIL |
| C17 | Permissão negada mantém aplicação aberta | `test_ac17` exit 0 | `tests/test_acceptance.py:227` — `self.assertIn('Permissão negada',self.app.message)`; `:228` — `self.assertTrue(self.app.running)` | PASS |
| C18 | Múltiplos PIDs exigem escolha única | `test_ac18` exit 0 | `tests/test_acceptance.py:233` — `self.assertEqual(self.app.dialog.kind,'choose')`; `:236` — `self.assertIn('PID: 2',self.screen.text())`; porta também exige escolha em `:242` | PASS |
| C19 | Três ações de serviço confirmadas com unidade/escopo | `test_ac19` exit 0 | `tests/test_acceptance.py:246` percorre `('iniciar','parar','reiniciar')`; `:248` — `for value in ('demo.service','usuário',action): self.assertIn(value,self.screen.text())`; `:249` — `self.assertEqual(self.backend.operations,[])` | PASS |
| C20 | Operação no escopo, timeout 10s e sem repetição | `test_ac20` exit 0 | `tests/test_acceptance.py:260` — `self.assertEqual('--user' in argv,scope=='usuário')`; `:261` — `self.assertEqual(run.call_args.kwargs['timeout'],10)`; `:265` — `self.assertEqual(run.call_count,1)` | PASS |
| C21 | Ações recolhem dados sem afirmar término | `test_ac21` exit 0 | `tests/test_acceptance.py:271` — `self.assertIn(0,self.backend.calls)`; `:273` — `self.assertNotIn('encerrado',self.app.message)`; `:276` — `self.assertIn(3,self.backend.calls)` | PASS |
| C22 | Últimas 2.000 entradas/caminhos únicos | `test_ac22` exit 0 | `tests/test_acceptance.py:283` — `self.assertEqual(len(b),2000)`; `:284` — `self.assertEqual({e.command for e in b},{f'echo {i}' for i in range(3,2003)})`; `:285` — `self.assertEqual(len(entries),2001)` | PASS |
| C23 | Bash/Zsh, metadados, continuação e deduplicação | `test_ac23` exit 0 + regressão Bash | `tests/test_acceptance.py:293` — `self.assertEqual(b,['echo a','printf "a\nb"'])`; `:294` — `self.assertEqual(z,['echo z','echo first\necho second'])` | PASS |
| C24 | Revisão editável mostra contexto antes da execução | `test_ac24` exit 0 | `tests/test_acceptance.py:302` — `for value in ('echo old','bash',os.getcwd()): self.assertIn(value,self.screen.text())`; `:304` — `self.assertEqual(self.app.dialog.text,'echo old!')`; `:305` — `self.assertFalse(run.called)` | PASS |
| C25 | Texto revisado/cwd/código de saída | `test_ac25` exit 0 | `tests/test_acceptance.py:310` — `self.assertEqual(code,7)`; `:311` — `self.assertEqual(output.read_text().strip(),str(self.home))`; `:316` — `self.assertEqual(calls[0][0][-2:],['-c','echo revised'])`; `:318` — `self.assertIn('7',self.app.message)` | PASS |
| C26 | Shell ausente/falha de execução são informados | `test_ac26` exit 0 | `tests/test_acceptance.py:323` — `self.assertRaisesRegex(core.SourceError,'Shell.*não encontrado')`; `:327` — `self.assertIn('cannot start',self.app.message); self.assertTrue(self.app.running)` | PASS |
| C27 | Teclado e terminal restaurado | `test_ac27` exit 0 | `tests/test_acceptance.py:331` a `:341` verificam seleções, visões, busca, ajuda e saída; `:344` — `self.assertEqual(result['exit'],0)`; `:345` — `self.assertTrue(result['restored'])` em PTY real | PASS |
| C28 | Tamanho mínimo e retorno após ampliar | `test_ac28` exit 0 | `tests/test_acceptance.py:350` — `self.assertIn('80',self.screen.text()); self.assertIn('24',self.screen.text())`; `:352` — `self.assertIn('Processos',self.screen.text())`; `:353` — `self.assertFalse(self.app.running)` | PASS |
| C29 | Processo inacessível não interrompe demais | `test_ac29` exit 0 | `tests/test_acceptance.py:358` e `:364` — `self.assertEqual([p.pid for p in core.ProcessSampler(root).sample()],[123])`, com stat inválido e PermissionError | PASS |
| C30 | CLI e canais de saída definidos | `test_ac30` exit 0 | `tests/test_acceptance.py:369` — `self.assertEqual(r.returncode,code)`; `:370` — `self.assertIn(text,r.stdout+r.stderr)`. A concatenação não distingue stderr, exigido para não-TTY e argumento desconhecido. G5. | FAIL |
| C31 | Início no checkout/venv e runtime stdlib | `test_ac31` exit 0 | `tests/test_acceptance.py:375` — `self.assertEqual(result['version'],'WSLazy 0.1.0')`; `:377` — `self.assertEqual(result['requires'],[])`. `--version` sai antes de importar a TUI; instalação não é iniciada interativamente. G4. | FAIL |
| C32 | Histórico não alterado ao executar | `test_ac32` exit 0 | `tests/test_acceptance.py:388` — `self.assertEqual(p.read_bytes(),before)`, mas a execução usa `runner=lambda argv, cwd: 0` (`:59`), sem shell real. G3. | FAIL |
| C33 | Cliques nas visões/linhas/campos/controles | `test_ac33` exit 0 + C37 | `tests/test_acceptance.py:392` — `self.assertEqual(self.app.view,index)`; `:394` — `self.assertEqual(self.app.current().payload.pid,2)`; `:401` — `self.assertEqual(self.app.dialog.text,'echo hi!')`; clique Lazydocker em `:442` — `self.assertEqual(len(calls),1)` | PASS |
| C34 | Roda na lista/detalhes e seleção preservada | `test_ac34` exit 0 | `tests/test_acceptance.py:407` — `self.assertGreater(self.app.selected[0],0)`; `:412` — `self.assertGreater(self.app.detail_scroll,0)`; `:413` — `self.assertEqual(self.app.selected[0],0)` | PASS |
| C35 | Confirmação por mouse/teclado mantém validações | `test_ac35` exit 0 | `tests/test_acceptance.py:419` — `self.assertEqual(self.backend.operations,[('signal',123,signal.SIGTERM)])`; `:422` — `self.assertEqual(self.app.dialog.target.pid,2)`. Não comprova alvo obsoleto/permissão via ambas as entradas; confirmação positiva de teclado é invocada diretamente por `confirm()` em outros testes. G2. | FAIL |
| C36 | Ajuda de atalhos e teclado sem mouse | `test_ac36` exit 0 | `tests/test_acceptance.py:427` — `for key in ('Tab','j/k','/','D','x','K','s','t','r','Enter','q'): self.assertIn(key,text)`; `:430` — `self.assertEqual(self.app.view,1)` após erro de mousemask | PASS |
| C37 | Lazydocker por clique/D, mesmo terminal/cwd | `test_ac37` exit 0 + PTY externo | `tests/test_acceptance.py:443` — `self.assertEqual(calls[0][0],[str(exe)])`; `:444` — `self.assertEqual((self.home/'marker').read_text(),str(self.home))`; `tests/test_regressions.py:86` — `self.assertEqual(marker.read_text(),'True')` comprova ICANON no filho lançado pelo clique real | PASS |
| C38 | Restaura visão/pesquisa/seleção e entradas | `test_ac38` exit 0 + PTY externo | `tests/test_acceptance.py:455` — `self.assertEqual((self.app.view,self.app.selected[0],self.app.queries[0]),(0,1,'python'))`; `tests/test_regressions.py:88` — `read_until(b'Atalhos e ajuda')` após clique real no retorno; `:92` — `self.assertEqual(termios.tcgetattr(slave),before)` | PASS |
| C39 | Lazydocker ausente mantém UI aberta | `test_ac39` exit 0 | `tests/test_acceptance.py:462` — `self.assertIn('Lazydocker não encontrado no PATH',self.app.message)`; `:463` — `self.assertTrue(self.app.running)` | PASS |
| C40 | Falha de lançamento informa motivo/aceita entradas | `test_ac40` exit 0 | `tests/test_acceptance.py:468` — `self.assertIn('launch failed',self.app.message)`; `:470` — `self.assertEqual(self.app.view,1)` por teclado; `:471` — `self.assertEqual(self.app.view,0)` por clique | PASS |

## Ranked gaps

1. **G1 — C15, exclusividade do sinal (alta):** a saída do alvo prova que ele recebeu o sinal, mas não que outro membro do grupo permaneceu vivo. Adicionar prova com alvo e sentinela descartáveis no mesmo grupo isolado; verificar ambos os sinais, alvo encerrado e sentinela viva. Evidência atual: `tests/test_acceptance.py:206`.
2. **G2 — C16/C35, falha e equivalência de entrada (alta):** ligar os erros já cobertos no core à ação real da UI e provar recolha após alvo obsoleto. Exercitar confirmação/cancelamento por eventos de teclado e clique; permissão negada e identidade alterada devem chegar às mesmas validações e manter a interface aberta. Evidência parcial: `tests/test_acceptance.py:214`, `:227`, `:419`. A implementação compartilha `confirm`, mas isso não substitui uma assertion da obrigação.
3. **G3 — C32, preservação durante execução (média):** a comparação de bytes ocorre após execução simulada. Executar entrada inofensiva com shell real e histórico temporário, afirmar um efeito que demonstre a execução e comparar bytes depois. Evidência: `tests/test_acceptance.py:388`; runner simulado em `:59`.
4. **G4 — C31, início instalado (média):** o teste da distribuição executa apenas `--version`, caminho que não importa `curses`/UI. Falta iniciar o comando instalado em PTY, fora do checkout e sem PYTHONPATH de desenvolvimento, e sair normalmente. O build atual usa wheel via `setup.py bdist_wheel`, não o `pip install .` do README; registrar essa diferença ou testar também o comando documentado. Evidência: `tests/install.py:15`, `:20`; import tardio da UI em `wslazy/__main__.py:23`.
5. **G5 — C30, stderr (baixa):** `stdout+stderr` torna invisível o canal requerido. Asserir a mensagem diretamente em stderr e a ausência de saída indevida em stdout. Evidência: `tests/test_acceptance.py:370`.

Busca adicional antes de declarar ausência: `rg -n 'stderr|stdout|poll\(|killpg|start_new_session|read_bytes|Permission|Processo não|runner|exercise_install|pip|termios|ICANON' tests`. Encontrou as comparações parciais citadas e as duas provas de PTY; não encontrou sentinela de grupo, comparação de stderr isolado, UI instalada em PTY ou comparação de histórico após shell real. Não houve injeção de falhas.

## Level and sampling

- Coletores `/proc` usam arquivos controlados; sinalização usa processo descartável real e pidfd. `ss` e `systemctl` são simulados. Nenhum serviço real foi alterado. O plano aceita executor simulado para serviços.
- A maior parte da UI é exercitada com tela simulada e chamadas ao controlador. Há PTY real para entrada/saída e para clique de lançamento do executável externo, retorno, novo clique e termios. Não houve ensaio de todas as visões/populações em Windows Terminal/WSL real.
- C1/C3/C10/C11 amostram conteúdo/seleção principalmente em Processos. C8 amostra erros de `ss` e atraso de `/proc`. C9 amostra processos e porta, C22 limite de 2.000 entradas em Bash com Zsh curto, C29 stat inválido e PermissionError. C36 comprova ajuda e navegação sem mouse, sem percorrer exaustivamente cada atalho. Estas são limitações de amostragem do perfil light, não uma recomputação do Coverage.
- C25 executa Bash real e confere a entrega do texto revisado ao runner em teste separado; não executa Zsh real. C40 exercita falha de runner na UI simulada; restauração real de termios é provada no sucesso do executável substituto, não numa falha de exec.
- Não foi demonstrado defeito de produto durante este passe; os seis FAILs delimitam cláusulas concretas sem prova no nível adequado. A existência de código plausível não foi usada para converter ausência de prova em PASS.

## Binding sources

Lidos integralmente `plan.md`, `checks.md` e os três pedidos do usuário reproduzidos em `plan.md` → `Sources`: TUI tipo lazydocker para recursos WSL e histórico; uso da skill lean; botão lazydocker e controle por teclado e mouse. Não há mockup externo nem contrato remoto indicado. Não há contradição identificada entre esses pedidos reproduzidos e os claims. Auditoria exaustiva de composição por tela não faz parte do perfil light.

## Coverage and policy

Coverage lido, não recomputado — perfil light. Não há seção `Test policy` nos checks. `Swept` relido: nenhuma linha delega obrigação a `existing`; todas referenciam checks novos. Os `n/a` são escolhas de escopo aprovadas. Sem injeção de falhas, conforme perfil light.

## Human judgment

UAT humano não realizado. Permanecem sem avaliação humana a legibilidade/densidade dos painéis, conforto da navegação e adequação visual à referência lazydocker. Esta verificação não declara aprovação humana; não foi solicitada interação adicional durante o passe.

## Gate

Suite: 44 passed, 0 failed, exit 0. Executado `python3 /home/matheus/.codex/skills/tlc-spec-lean/scripts/validate_verification.py /home/matheus/process-find-list/.specs/features/wslazy`: exit 1, `1 error(s), 0 warning(s)`, exclusivamente porque o verdict é FAIL. Nenhuma implementação, teste ou check foi editado pelo Verifier. O autor iniciou alterações não commitadas nos helpers de testes após a execução das provas; este relatório e as citações descrevem o HEAD indicado, anterior a essas correções.
