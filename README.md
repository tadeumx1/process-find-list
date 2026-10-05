# WSLazy

Gerenciador de processos do WSL no terminal, inspirado no lazydocker. Navegue com **teclado ou mouse** entre processos, aplicativos, portas, serviços e comandos recentes. O botão **Lazydocker [D]** abre a ferramenta no mesmo terminal e retorna ao WSLazy quando ela termina.

```text
 WSLazy     seu WSL, em um só lugar         Lazydocker [D]  Ajuda [?]

 Processos [1]  Aplicativos [2]  Portas [3]  Serviços [4]  Histórico [5]

 / Pesquisar: python

 PID     USUÁRIO   CPU     MEMÓRIA     COMANDO   │ Detalhes
 1420    você     12.4%    48.0 MiB    python …  │ PID: 1420
                                              │ Comando:
                                              │ python app.py

 Encerrar [x]  Forçar [K]  Atualizar [F5]                  Sair [q]
```

## Começar

Requer **Linux/WSL e Python 3.10+ com curses**. Não há dependências Python de runtime de terceiros.

Da pasta do projeto, execute:

```bash
python3 -m wslazy
```

Para instalar o comando `wslazy` num ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
wslazy
```

No Ubuntu/WSL, se `venv` ou `pip` estiverem ausentes, instale as ferramentas de empacotamento da distribuição:

```bash
sudo apt install python3-venv python3-pip
```

Também é possível expor o comando instalado fora do ambiente virtual, adicionando `$(pwd)/.venv/bin` ao seu `PATH`. Para remover, exclua o ambiente virtual e essa entrada do PATH. A execução direta com `python3 -m wslazy` funciona sem `pip`.

- **Portas:** usa `ss`, fornecido pelo pacote `iproute2`.
- **Serviços:** usa systemd; lista os escopos de sistema e usuário. A ausência de um escopo aparece na interface sem bloquear as outras telas.
- **Lazydocker:** opcional; o executável `lazydocker` deve estar no `PATH`. A aplicação não o instala nem inicia o Docker. Consulte o [projeto oficial](https://github.com/jesseduffield/lazydocker) para instalação. Enquanto ele está aberto, os controles são os da própria ferramenta.
- Terminal recomendado: **80×24 ou maior**, com cores e eventos de mouse, como Windows Terminal. Sem eventos de mouse, todos os controles continuam acessíveis pelo teclado.

## Controles

| Ação | Teclado | Mouse |
| --- | --- | --- |
| Trocar tela | `Tab`, `Shift+Tab`, `1`–`5` | Clique na aba |
| Selecionar item | `↑` / `↓`, `j` / `k`, `PgUp` / `PgDn` | Clique ou roda na lista |
| Rolar detalhes | `[` / `]` | Roda sobre os detalhes |
| Pesquisar | `/`, digitar, `Enter` para terminar | Clique em Pesquisar e digite |
| Limpar pesquisa | `Ctrl+U` no campo ou `Esc` fora dele | Clique no campo e use `Ctrl+U` |
| Abrir detalhes completos | `Enter` | Leia o painel, rolando o texto |
| Encerrar processo | `x` → `Tab` → `Enter` | Encerrar → Confirmar |
| Forçar encerramento | `K` → `Tab` → `Enter` | Forçar → Confirmar |
| Iniciar / parar / reiniciar serviço | `s` / `t` / `r` → `Tab` → `Enter` | Botão da ação → Confirmar |
| Revisar comando recente | `Enter` na tela Histórico | Executar |
| Abrir lazydocker | `D` | Lazydocker |
| Atualizar agora | `F5` | Atualizar |
| Ajuda | `?` | Ajuda |
| Sair | `q` | Sair |

A confirmação de processo mostra **PID, comando e sinal**. `Esc` ou **Cancelar** abandona a ação. Em aplicativos ou portas com vários processos, escolha primeiro um único PID. Encerrar usa `SIGTERM`; Forçar usa `SIGKILL`. O programa confere a identidade do processo e usa `pidfd` para que um PID reutilizado não direcione o sinal a outro processo. Em um kernel sem esse suporte, a ação é recusada.

As operações usam suas permissões atuais e não elevam privilégios automaticamente. Sinal enviado ou operação aceita não significa que o processo ou serviço já terminou: a lista é consultada novamente. O encerramento de um processo supervisionado pode causar seu reinício pelo supervisor.

## Histórico de comandos

Lê as últimas 2.000 entradas de cada arquivo disponível entre `$HISTFILE`, `~/.bash_history` e `~/.zsh_history`. Caminhos repetidos são lidos uma vez; comandos repetidos em cada origem mostram a ocorrência mais recente. A posição no arquivo define a ordem, não uma cronologia global entre shells. Metadados Bash/Zsh são removidos da apresentação.

Somente comandos **já gravados em disco** ficam disponíveis. Se necessário, grave o histórico do shell antes de abrir o WSLazy: `history -a` no Bash ou `fc -AI` no Zsh. Para um caminho customizado, exporte `HISTFILE` para que o processo filho o receba. Bash sem timestamps nem escapes não contém informação suficiente para reconstruir todos os comandos multilinha.

Antes de executar, a revisão mostra o texto completo, o shell e o **diretório atual**. Edite com as setas, `Home`, `End`, `Backspace`, `Delete` e `Ctrl+U`; `Ctrl+N` insere uma linha. `Enter` no editor ou **Confirmar** executa o texto revisado. `Tab` alterna editor e botões; `Esc` cancela.

O comando usa `bash -c` ou `zsh -c`, sem reconstruir diretório, variáveis, aliases ou funções da sessão original. Após a execução, o código de saída é mostrado; pressione Enter para retornar à interface. O WSLazy não adiciona nem reescreve entradas nos arquivos de histórico. Comandos executados têm os mesmos efeitos que teriam no seu shell.

## O que cada tela mostra

- **Processos:** processos legíveis em `/proc` da distribuição atual, com PID, usuário, CPU, memória e comando; estado e início estão nos detalhes.
- **Aplicativos:** agrupamentos por nome do executável e UID, com consumo somado e os PIDs integrantes.
- **Portas:** TCP em escuta e UDP vinculados, incluindo IPv4/IPv6. A porta continua visível quando o proprietário não pode ser identificado.
- **Serviços:** unidades `.service` carregadas no systemd, de sistema e usuário, inclusive inativas.
- **Histórico:** comandos recentes de Bash e Zsh, com origem e revisão antes de executar.

A coleta das telas de recursos se repete dois segundos após a coleta anterior. Na primeira amostra, CPU aparece como `—`; depois, o uso é calculado entre amostras e pode ultrapassar 100% em processos que usam vários núcleos. Processos Windows e de outras distribuições não são incluídos. Erros de coleta aparecem na tela correspondente.

## Desenvolvimento e validação

```bash
python3 -m unittest tests.test_acceptance -v
```

O teste de instalação precisa de `pip`, `setuptools` e `wheel` no Python que executa os testes. Instale essas ferramentas em seu ambiente de desenvolvimento com `python -m pip install setuptools wheel`. Elas não são dependências de runtime do WSLazy. O teste cria e remove seu próprio ambiente isolado e instala um wheel local sem acesso à rede.

Os testes exercitam processos descartáveis, históricos temporários, um pseudoterminal real e um substituto temporário do lazydocker. Operações de serviço são testadas com executor simulado, sem alterar serviços reais.

O [plano](.specs/features/wslazy/plan.md) e os [checks](.specs/features/wslazy/checks.md) documentam os critérios de aceitação. A implementação usa o perfil de verificação `light` da skill `tlc-spec-lean`.
