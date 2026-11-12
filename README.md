# Telos — Themis Tech

## 1. O que é o Telos

O Telos é um vigia de jurisprudência para escritórios de advocacia, criado pela Themis Tech. Ele busca decisões e temas repetitivos no Superior Tribunal de Justiça (STJ), compara esse material com os casos do escritório e avisa quais casos podem ter sido afetados. Os avisos informam o resultado e se ele favorece ou desfavorece a posição do cliente.

## 2. Como funciona

1. **Busca:** consulta no portal de dados abertos do STJ as decisões disponíveis e os temas repetitivos ligados aos termos configurados.
2. **Análise:** a inteligência artificial compara o texto encontrado com os casos cadastrados. Cada decisão recebe dois pareceres independentes.
3. **Aviso:** quando os pareceres concordam que há relação direta, o Telos mostra o resumo, o motivo, o resultado, trechos do documento e o link oficial.

## 3. Exemplo de aviso

A prévia [email_exemplo.html](email_exemplo.html) foi gerada com avisos da demonstração. Ela mostra como o resumo da decisão, os casos afetados, os trechos conferidos e o link oficial aparecem no e-mail.

## 4. Proteções contra erros da IA

- **Citações conferidas:** o Telos verifica se cada trecho citado existe no texto da decisão. Citações que não aparecem no arquivo não são usadas como prova do aviso.
- **Link oficial controlado pelo programa:** para decisões do STJ, o Telos monta o link do inteiro teor usando os dados do catálogo oficial; para temas repetitivos, usa a consulta oficial do tema. A IA não inventa nem escolhe o link. Para arquivos colocados manualmente, usa o link oficial informado no próprio arquivo.
- **Segundo parecer:** uma decisão de outro processo tem relação direta quando resolve a mesma questão jurídica discutida no caso do escritório e pode servir de precedente. Por exemplo, uma decisão que concede lucros cessantes por atraso na entrega de imóvel é direta para um caso que também pede lucros cessantes pelo atraso. Se tratar de tema parecido, mas resolver outra questão, a relação é indireta. Os dois pareceres precisam concordar que a relação é direta e comprová-la com trechos encontrados no arquivo. Se concordarem sobre a relação, mas divergirem apenas sobre o resultado ou a favorabilidade, o aviso é enviado com o selo **“Favorabilidade a confirmar”**. Divergências sobre a própria relação vão para **“Revisar à mão”**, junto com os dois pareceres.
- **Incerteza explícita:** quando o material não permite uma conclusão segura, o Telos diz **“não tenho certeza”** em vez de afirmar que a decisão afeta o caso.

## 5. Como mudar a área vigiada

O Telos acompanha Direito Bancário, Imobiliário e Empresarial. A área depende dos casos cadastrados em `casos/` e dos termos `STJ_SEARCH_TERMS_BANCARIO`, `STJ_SEARCH_TERMS_IMOBILIARIO` e `STJ_SEARCH_TERMS_EMPRESARIAL` no `.env`. Cada campo aceita vários termos separados por ponto e vírgula. Os termos são enviados ao catálogo do STJ para localizar decisões; a análise da relação com os casos é feita pela IA. Os casos de bancário recuperados do histórico são os Casos 14 a 16. O Caso 13 continua como caso de controle sem termo de busca.

## 6. Limitações

- A única fonte de jurisprudência nesta versão é o STJ.
- No STJ, a janela de três semanas só pode cobrir datas para as quais o portal já publicou os arquivos diários de metadados e textos. O portal pode atualizar com atraso.
- O STJ disponibiliza decisões e acórdãos em arquivos estruturados com atraso variável; temas repetitivos são consultados na lista oficial de precedentes qualificados.
- Cada rodada analisa até seis itens. O custo depende do provedor configurado; a OpenAI cobra pelos tokens usados.
- O Telos ajuda a localizar decisões que merecem atenção, mas não substitui a leitura da decisão nem a análise de uma advogada ou advogado.

## 7. Provedor de IA

O provedor padrão agora é a OpenAI, com o modelo **GPT-6 Luna**. A OpenAI o descreve como eficiente para tarefas focadas e de alto volume; ele aceita respostas estruturadas e faz parte da geração atual com recursos multilíngues. Isso combina com o Telos, que compara decisões e precisa receber campos em um formato verificável. Ainda não fizemos uma avaliação comparativa específica de qualidade em português no Telos. O preço publicado é de US$ 0,10 por milhão de tokens de entrada e US$ 0,50 por milhão de tokens de saída; cada decisão recebe dois pareceres, e o custo real depende do tamanho do texto e da resposta. Consulte a [página do modelo](https://developers.openai.com/api/docs/models/gpt-6-luna), o [catálogo de modelos](https://developers.openai.com/api/docs/models) e os [preços atuais da API](https://developers.openai.com/api/docs/pricing), que podem mudar.

Gemini e Groq continuam disponíveis como alternativas configuráveis no `.env`. Um teste anterior comparou os dois provedores usando os casos antigos de Direito Bancário, Saúde e Aviação: o Gemini deu respostas idênticas nas duas rodadas para as mesmas cinco decisões, enquanto a Groq variou em quatro de cinco. Esse resultado histórico não é um teste do GPT-6 Luna nem dos casos atuais de Direito Imobiliário e Empresarial, e não garante que respostas futuras serão sempre iguais.

## Do pitch ao produto

Na primeira fase, apresentamos o Telos em um site (https://themistech.netlify.app) com a visão completa do produto. Nesta segunda fase, construímos uma versão real e reduzida. Esta seção mostra, com honestidade, o que foi entregue, o que foi simplificado e o que fica para uma próxima versão.

O que foi entregue. O Telos busca decisões no Superior Tribunal de Justiça, compara cada uma com os casos do escritório e avisa quais casos foram afetados, com o que mudou e o link oficial para conferir, como prometido no site. Também mantivemos a promessa central de nunca entregar informação sem fonte oficial: o link é montado pelo programa a partir dos dados do tribunal, e cada trecho citado pela inteligência artificial é conferido no texto da decisão. O produto pode ser configurado para qualquer área do Direito, porque a área vigiada depende dos casos cadastrados e dos termos de busca.

O que entregamos além do prometido. Cada aviso informa o resultado da decisão e se ela é favorável ou desfavorável ao cliente. Criamos ainda um "segundo parecer": cada decisão é analisada duas vezes e só vira aviso quando as duas análises concordam que a relação com o caso é direta. Se os pareceres divergirem apenas sobre o resultado ou a favorabilidade, o aviso sai marcado "Favorabilidade a confirmar". Se discordarem sobre a relação direta, a decisão vai para "Revisar à mão". Fizemos isso depois de medir que um dos modelos testados dava respostas diferentes para a mesma decisão.

O que foi simplificado, e por quê. O site prometia vigiar leis, o Supremo Tribunal Federal, o Banco Central, o Cade e a Receita. Esta versão consulta apenas o Superior Tribunal de Justiça. O site prometia avisos na hora, por e-mail ou WhatsApp. Esta versão envia avisos por e-mail ao fim da rodada quando há destinatário configurado; o botão permite reenviar. O WhatsApp exige um acesso oficial pago, e a execução automática diária depende de um computador ou servidor ligado. O site mostrava a escolha do que vigiar escrevendo em linguagem natural. Aqui, isso é feito editando os termos de busca no arquivo de configuração. O site mostrava contratos completos. Aqui, cada caso é uma descrição curta. Cada execução limita a seis itens.

Sigilo. O site prometia criptografia do início ao fim. Uma criptografia completa não é possível quando uma inteligência artificial precisa ler o texto para analisá-lo. Nesta versão, usamos casos inventados e decisões públicas. Os textos são enviados ao provedor escolhido; as regras de retenção e uso dos dados variam conforme o provedor e as configurações da conta. Em uso real, mantenha o nome do cliente no computador do escritório e envie à inteligência artificial apenas um código e a descrição do caso.

Próximos passos. Acrescentar outras fontes, como os diários oficiais; execução automática diária em servidor; ampliar a leitura de documentos do STJ; cadastro de contratos inteiros; e envio de cada aviso apenas ao advogado responsável pelo caso.

## 8. Interface web

O modo de demonstração da página continua usando a rodada fixa já verificada. A busca ao vivo no STJ fica disponível no computador quando `TELOS_DEMO_MODE=false`; na hospedagem ela permanece desativada.

A interface permite informar um e-mail para receber os avisos. Ao terminar a rodada, o Telos mostra os resultados na página e envia o e-mail automaticamente quando há destinatário configurado. No computador, o envio vai para os destinatários do `.env` e também para o endereço digitado; na hospedagem, vai somente para o endereço digitado. Se nenhum endereço for digitado na hospedagem, nenhum e-mail é enviado. Depois de um envio bem-sucedido, o botão **Enviar avisos por e-mail** fica disponível para reenviar aquela rodada. A página confirma o envio. As chaves e senhas não são enviadas à página.

O modo de demonstração é controlado pela variável `TELOS_DEMO_MODE` no `.env` e vem ligado (`true`). Nesse modo, o botão reapresenta uma rodada fixa já verificada, com andamento simulado, sem consultar o STJ nem chamar a IA. A escolha da área e da quantidade vale também para essa rodada: “Todos” (a opção padrão) mostra todos os itens da área escolhida; as opções de 1 a 6 mostram até essa quantidade. “Todas as áreas” reúne a rodada completa. A página não exibe um aviso de que está nesse modo. No computador, para fazer buscas e análises reais, mude `TELOS_DEMO_MODE=false`; o Telos consulta os arquivos diários do STJ disponíveis para os últimos 21 dias e acrescenta arquivos novos sem apagar os anteriores. Na busca ao vivo, “Todos” respeita o limite atual de seis decisões por rodada.

Em hospedagem, `TELOS_HOSPEDADO=true` força o modo de demonstração, mesmo se `TELOS_DEMO_MODE` estiver desligado, e impede buscas ao vivo no STJ. O envio usa a API transacional do Brevo com `BREVO_API_KEY` e o remetente informado em `GMAIL_SENDER`; esse endereço precisa estar cadastrado e autorizado na conta Brevo. Cada envio hospedado aceita somente o endereço digitado na página e ignora completamente `GMAIL_RECIPIENT`; não há outros destinatários que possam ver esse endereço. Há limite de um envio iniciado por minuto e 20 por dia. Para uso no computador, deixe `TELOS_HOSPEDADO=false` (ou vazio): o modo e os destinatários continuam seguindo as configurações locais de hoje, e o Gmail continua sendo usado. O arquivo local que registra o limite pode ser apagado quando o serviço gratuito reinicia; por isso, esses limites são uma proteção operacional para uma instância hospedada, não um mecanismo contra abuso distribuído.

Os casos fictícios de demonstração ficam em `casos/demonstracao/`, numerados de 17 a 37. Os Casos 28 a 37 foram criados para representar questões jurídicas específicas dos temas repetitivos analisados.

A rodada fixa atual usa cinco temas repetitivos do STJ com relação direta confirmada pelos dois pareceres. Cada cartão afeta pelo menos dois casos. Há também um item em **Revisar à mão**: o [Tema 577](https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?cod_tema_inicial=577&cod_tema_final=577&novaConsulta=true&tipo_pesquisa=T) define quando os valores do distrato devem ser devolvidos. Os Casos 3 e 20 discutem principalmente quanto pode ser retido; os dois pareceres classificaram a relação como indireta, então nenhum aviso direto foi confirmado.

| Tema oficial do STJ | Área | Casos com relação direta confirmada |
| --- | --- | ---: |
| [Tema 27 — revisão de juros remuneratórios](https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?cod_tema_inicial=27&cod_tema_final=27&novaConsulta=true&tipo_pesquisa=T) | Bancário | 2 (Casos 28 e 29) |
| [Tema 929 — devolução em dobro por cobrança indevida contrária à boa-fé](https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?cod_tema_inicial=929&cod_tema_final=929&novaConsulta=true&tipo_pesquisa=T) | Bancário | 2 (Casos 36 e 37) |
| [Tema 1061 — autenticidade de assinatura bancária](https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?cod_tema_inicial=1061&cod_tema_final=1061&novaConsulta=true&tipo_pesquisa=T) | Bancário | 2 (Casos 26 e 27) |
| [Tema 970 — multa contratual e lucros cessantes por atraso](https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?cod_tema_inicial=970&cod_tema_final=970&novaConsulta=true&tipo_pesquisa=T) | Imobiliário | 3 (Casos 1, 32 e 33) |
| [Tema 1051 — data do crédito na recuperação judicial](https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?cod_tema_inicial=1051&cod_tema_final=1051&novaConsulta=true&tipo_pesquisa=T) | Empresarial | 2 (Casos 34 e 35) |

Os temas foram conferidos na lista oficial de precedentes qualificados do STJ, e cada trecho usado nos avisos foi localizado no arquivo da tese. A rodada é formada por precedentes qualificados já publicados; não se apresenta como decisões novas das últimas três semanas.

Na página **Casos do escritório**, o cadastro local grava o caso e a relação entre nome e código em `.telos_clientes.json` (ignorado pelo Git). A IA recebe somente o código e a descrição do caso. O programa acrescenta o nome aos avisos e e-mails. O novo cadastro passa a participar da próxima rodada. Na hospedagem, o formulário funciona em modo de demonstração: compara a descrição com os avisos fixos, mostra um exemplo da decisão mais parecida e não grava os dados do formulário. Se for informado um e-mail, o exemplo também é enviado, sujeito aos limites de envio.

Em um teste anterior, ainda sem análises paralelas, três decisões imobiliárias levaram cerca de 2 min 29 s e 3 min 51 s; os avisos diferiram, nenhum aviso direto foi confirmado e uma decisão ficou em “Revisar à mão”. Uma medição posterior de menos de dois segundos não registrou respostas novas da API e podia estar mostrando a última rodada já salva; por isso, ela não é usada como medida de desempenho.

Na validação seguinte, limpamos o estado de decisões processadas antes de cada repetição, desligamos o envio de e-mail e contamos as respostas da API OpenAI. As mesmas oito decisões marcadas para demonstração foram analisadas duas vezes em paralelo. Cada rodada gerou 16 respostas da API, todas com identificador único, e terminou em 24,93 s e 25,74 s. Os avisos não foram iguais. A tabela mostra quantos casos receberam aviso direto em cada decisão; itens para revisão manual não contam como casos afetados confirmados.

| Decisão da demonstração | Rodada 1 | Rodada 2 |
| --- | ---: | ---: |
| Atraso na entrega do imóvel | 3 | 3 |
| Desistência da compra na planta | 0 | 3 |
| Defeitos no apartamento | 2 | 2 |
| Despejo por falta de pagamento | 0 | 0 |
| Saída de sócio | 2 | 2 |
| Crédito na recuperação judicial | 0 | 0 |
| Duplicata protestada | 2 | 2 |
| Rescisão de franquia | 0 | 2 |

Nas rodadas, respectivamente, cinco e duas decisões também apareceram em “Revisar à mão”. Nenhum e-mail foi enviado.

Para abrir no seu computador:

1. Instale as dependências conforme a seção seguinte e configure as chaves no `.env`.
2. No Terminal, entre na pasta do Telos e execute:

   ```bash
   python webapp.py
   ```

   Se necessário, use `python3 webapp.py`. O programa usa a porta indicada por `PORT`; no computador, sem essa variável, usa a porta 5000.
3. Abra `http://127.0.0.1:5000` no navegador. Não abra `templates/index.html` diretamente: esse arquivo é um modelo usado pelo servidor, e aberto como arquivo local ele mostra instruções internas em vez da página pronta.

O andamento aparece na própria tela enquanto o trabalho continua em segundo plano. Uma nova rodada não pode começar enquanto outra estiver ativa. A página inicial também mostra a última rodada salva; no computador, ela fica em `.telos_web_data/` e continua disponível mesmo depois de fechar e abrir o programa. A página **Casos do escritório** lista os casos que estão na pasta `casos/`.

### Hospedar gratuitamente

O projeto inclui `render.yaml` para criar um serviço web gratuito no Render. Envie o repositório ao GitHub e, no Render, crie um **Blueprint** conectado a esse repositório. Escolha o plano gratuito. O arquivo configura `TELOS_HOSPEDADO=true`, que mantém a demonstração ativa e desativa buscas reais no STJ. Para a página e os casos, não é preciso cadastrar chaves de IA nem termos de busca. Para habilitar o envio automático de e-mail, informe apenas `GMAIL_SENDER` e `BREVO_API_KEY`; cadastre e autorize `GMAIL_SENDER` como remetente na conta Brevo. O endereço digitado na página é o único destinatário. Não configure `GMAIL_RECIPIENT`, senha de app do Gmail nem chaves de IA para a hospedagem. `TELOS_HOSPEDADO` e `TELOS_DEMO_MODE` já são definidos pelo `render.yaml`; o Render fornece `PORT` automaticamente. Os campos secretos ficam no painel do serviço; não coloque esses valores no código nem envie o `.env` ao GitHub. A instalação da hospedagem usa apenas as dependências do site, em `requirements-hosting.txt`; as dependências de coleta e análise ao vivo continuam em `requirements.txt` para uso no computador.

Depois que o serviço for criado, copie o endereço `*.onrender.com` e acrescente ao site de apresentação um botão que aponte para esse endereço. Na hospedagem, o cadastro de caso funciona como uma simulação: mostra um aviso baseado na decisão de demonstração mais parecida e não grava os dados. No uso local, o cadastro é guardado para as rodadas seguintes.

Há uma limitação importante do plano gratuito do Render para esta demonstração: ele apaga arquivos locais quando o serviço para, reinicia ou é publicado novamente, então a cópia da última rodada e o contador de envios podem reiniciar. O e-mail hospedado usa a API do Brevo por HTTPS. Veja as [limitações oficiais do plano gratuito](https://render.com/docs/free) e o [guia oficial de Flask no Render](https://render.com/docs/deploy-flask).

## 9. Instalação e uso

### Instalar

Instale o Python 3.10 ou mais recente. Abra o Terminal (Mac/Linux) ou o PowerShell (Windows), entre na pasta do Telos e instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Se `python` não funcionar, tente `python3`.

### Buscar no STJ sem chamar a inteligência artificial

Com `TELOS_DEMO_MODE=false`, a interface do computador busca as íntegras disponíveis nos arquivos diários do portal do STJ. Para baixar apenas as decisões do STJ das últimas três semanas e atualizar as fichas dos temas repetitivos, sem chamar IA nem enviar e-mail, execute:

```bash
python telos.py --baixar-stj
```

As decisões completas ficam em `decisoes/auto_stj_*.txt`. Os CSVs oficiais e as fichas dos precedentes ficam em `decisoes/stj_precedentes/`, subpasta que o Telos não envia para análise como se fosse uma decisão recente. O portal pode publicar os arquivos diários com atraso; se não houver o par JSON/ZIP na janela, o comando informa a última data completa encontrada e baixa os precedentes qualificados disponíveis.

### Configurar a OpenAI (provedor padrão)

1. Crie uma chave na [página de chaves da API OpenAI](https://platform.openai.com/api-keys). A API é paga por uso; confira os preços atuais antes de rodar análises.
2. Na pasta principal do Telos, crie o arquivo `.env` a partir do `.env.example`:

   ```bash
   cp .env.example .env
   ```

   No Windows PowerShell, use `Copy-Item .env.example .env`.

3. Abra `.env`, mantenha `AI_PROVIDER=openai` e cole sua chave depois de `OPENAI_API_KEY=`. O modelo padrão é `gpt-6-luna`.
4. Salve o arquivo. Não compartilhe a chave: `.env` fica fora do Git.

### Usar o Gemini como alternativa

Crie uma chave no [Google AI Studio](https://aistudio.google.com/app/apikey), cole-a depois de `GEMINI_API_KEY=` no `.env` e mude `AI_PROVIDER=openai` para `AI_PROVIDER=gemini`. O modelo padrão é `gemini-3.1-flash-lite`.

### Usar a Groq como alternativa

Crie uma chave na [GroqCloud](https://console.groq.com/keys), cole-a depois de `GROQ_API_KEY=` no `.env` e altere `AI_PROVIDER=groq`. O modelo padrão é `openai/gpt-oss-120b`. Se ele rejeitar uma resposta por formato incompatível, o Telos tenta uma vez com `openai/gpt-oss-20b` e informa a troca. O Telos usa o SDK oficial `groq` para Python.

### Receber os avisos pelo Gmail

O envio é automático ao fim da rodada quando há destinatário configurado. No computador, configure `GMAIL_SENDER` e `GMAIL_APP_PASSWORD`, mais pelo menos um destinatário em `GMAIL_RECIPIENT` ou no campo de e-mail da interface. Na hospedagem, configure `GMAIL_SENDER` autorizado no Brevo e `BREVO_API_KEY`; sem e-mail digitado na página, nada é enviado. O botão **Enviar avisos por e-mail** serve apenas para reenviar uma rodada que já foi enviada. O Telos prepara um resumo: os avisos diretos ficam em cartões separados e os itens de “Revisar à mão”, com os pareceres em frases simples lado a lado, ficam em uma seção lilás própria. Cada aviso mostra um título curto para o caso e, quando constam no material, o número do processo, o foro, a vara e a data da decisão. Campos ausentes são identificados como não informados. O resumo descreve o que o tribunal decidiu. O assunto ajusta singular e plural. O visual usa o azul-marinho e a lavanda do site de apresentação da Themis Tech. A mensagem inclui uma versão HTML compatível com o Gmail e uma alternativa em texto simples.

Você pode abrir [email_exemplo.html](email_exemplo.html) no navegador para ver uma prévia. O arquivo usa resultados de uma rodada anterior, sem nomes das partes do processo.

No computador, o envio continua pelo Gmail. Na hospedagem, o Telos usa a [API transacional do Brevo](https://developers.brevo.com/reference/send-transac-email), que envia por HTTPS sem depender da porta SMTP bloqueada pelo Render. Crie uma chave de API no painel do Brevo e configure `BREVO_API_KEY`; o endereço de `GMAIL_SENDER` deve estar cadastrado e autorizado como remetente na conta. O HTML e o texto simples do e-mail são mantidos. Cada envio hospedado leva um único destinatário, então nenhum outro destinatário recebe ou vê o endereço informado.

Para criar a senha de app do Gmail:

1. Ative a [Verificação em duas etapas](https://support.google.com/accounts/answer/185839?hl=pt-BR) na sua Conta Google.
2. Abra a página de [senhas de app](https://myaccount.google.com/apppasswords), entre na conta que enviará os avisos e crie uma senha para o Telos. O Google mostra a senha uma única vez; guarde-a para o próximo passo.
3. No `.env`, preencha os três campos. Use o endereço Gmail que criou a senha em `GMAIL_SENDER`, a senha gerada em `GMAIL_APP_PASSWORD` e informe em `GMAIL_RECIPIENT` o endereço ou a lista de endereços que receberá as mensagens. Separe vários endereços por vírgula. Todos recebem a mensagem em cópia oculta, sem ver o endereço dos demais. Esse fluxo é usado no computador; na hospedagem, o envio usa o Brevo:

   ```text
   GMAIL_SENDER=seu-endereco@gmail.com
   GMAIL_APP_PASSWORD=senha-de-app-do-google
   GMAIL_RECIPIENT=destino1@exemplo.com,destino2@exemplo.com
   ```

   Ao fim da rodada, o Telos envia pelo servidor seguro do Gmail (`smtp.gmail.com`, TLS na porta 587). O botão da interface permite reenviar a rodada. A senha de app requer Verificação em duas etapas; algumas contas de trabalho/escola, contas com Proteção Avançada ou contas que usam somente chaves de segurança podem não oferecer essa opção. Veja a [ajuda oficial do Google sobre senhas de app](https://support.google.com/accounts/answer/185833?hl=pt-BR) e os [parâmetros SMTP do Gmail](https://support.google.com/mail/answer/7104828?hl=pt-BR).

### Rodar o Telos

Com o Terminal ou PowerShell aberto na pasta principal, execute:

```bash
python telos.py
```

O Telos busca as íntegras disponíveis do STJ e analisa os arquivos pendentes. O envio automático de avisos fica na interface web. Para analisar somente os arquivos que já estão em `decisoes/`, sem fazer uma nova busca, execute:

```bash
python telos.py --sem-busca
```

Cada termo de busca do STJ pode ter até 120 caracteres. Se a busca automática falhar, também é possível colocar um arquivo `.txt` ou PDF com texto selecionável na pasta `decisoes/`; inclua nele o link oficial do STJ. PDFs digitalizados como imagem não são lidos nesta versão.
