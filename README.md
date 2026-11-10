# Telos — Themis Tech

## 1. O que é o Telos

O Telos é um vigia de jurisprudência para escritórios de advocacia, criado pela Themis Tech. Ele busca decisões novas no Tribunal de Justiça de São Paulo (TJSP), compara essas decisões com os casos do escritório e avisa quais casos podem ter sido afetados. Os avisos informam o resultado da decisão e se ele favorece ou desfavorece a posição do cliente.

## 2. Como funciona

1. **Busca:** consulta decisões no TJSP com os termos configurados pelo escritório.
2. **Análise:** a inteligência artificial compara o texto encontrado com os casos cadastrados. Cada decisão recebe dois pareceres independentes.
3. **Aviso:** quando os pareceres concordam que há relação direta, o Telos mostra o resumo, o motivo, o resultado, trechos do documento e o link oficial.

## 3. Exemplo de aviso

A prévia [email_exemplo.html](email_exemplo.html) foi gerada com os avisos da rodada atual, já configurada para Direito Imobiliário e Direito Empresarial. Ela mostra como o resumo da decisão, os casos afetados, os trechos conferidos e o link oficial aparecem no e-mail.

## 4. Proteções contra erros da IA

- **Citações conferidas:** o Telos verifica se cada trecho citado existe no texto da decisão. Citações que não aparecem no arquivo não são usadas como prova do aviso.
- **Link oficial controlado pelo programa:** nas buscas automáticas, o Telos monta o link de consulta com identificadores recebidos do TJSP. A IA não inventa nem escolhe o link. Para arquivos colocados manualmente, o Telos usa o link oficial informado no próprio arquivo.
- **Segundo parecer:** relação direta significa que a decisão resolve a mesma questão jurídica específica do caso, não apenas um tema parecido. Só há aviso quando as duas análises concordam sobre essa relação, o resultado e a favorabilidade. Se houver divergência, a decisão vai para **“Revisar à mão”**, junto com as duas respostas.
- **Incerteza explícita:** quando o material não permite uma conclusão segura, o Telos diz **“não tenho certeza”** em vez de afirmar que a decisão afeta o caso.

## 5. Como mudar a área vigiada

Nesta configuração, o Telos acompanha Direito Imobiliário e Direito Empresarial. A área depende dos casos cadastrados na pasta `casos/` e dos termos em `TJSP_SEARCH_TERMS` no arquivo `.env`. Para mudar o foco, edite as descrições dos casos e troque ou acrescente termos de busca, separados por ponto e vírgula. O Caso 13 (horas extras) é um caso de controle e não tem termo de busca.

## 6. Limitações

- Por enquanto, as buscas automáticas são feitas somente no TJSP.
- A busca consulta uma página por termo em cada tipo de decisão.
- Para decisões de primeiro grau, o Telos analisa o texto disponível na busca. Para acórdãos, analisa somente a ementa; não baixa o acórdão completo.
- Cada rodada analisa até cinco decisões. O plano gratuito do provedor de IA também tem limites de uso.
- O Telos ajuda a localizar decisões que merecem atenção, mas não substitui a leitura da decisão nem a análise de uma advogada ou advogado.

## 7. Por que usamos o Gemini

No teste anterior, feito com os casos e as decisões das áreas então acompanhadas (bancário, saúde e aviação), o Gemini produziu respostas idênticas nas duas rodadas para as mesmas cinco decisões. No teste equivalente com a Groq, as respostas foram diferentes em quatro das cinco decisões. Por esse resultado observado, o Gemini é o provedor padrão; a Groq continua disponível como alternativa. Esse registro se refere aos casos antigos, não aos atuais de Direito Imobiliário e Empresarial, e não garante que respostas futuras serão sempre iguais.

## Do pitch ao produto

Na primeira fase, apresentamos o Telos em um site (https://themistech.netlify.app) com a visão completa do produto. Nesta segunda fase, construímos uma versão real e reduzida. Esta seção mostra, com honestidade, o que foi entregue, o que foi simplificado e o que fica para uma próxima versão.

O que foi entregue. O Telos busca sozinho decisões novas no Tribunal de Justiça de São Paulo, compara cada uma com os casos do escritório e avisa quais casos foram afetados, com o que mudou e o link oficial para conferir, como prometido no site. Também mantivemos a promessa central de nunca entregar informação sem fonte oficial: o link é montado pelo programa a partir dos dados do tribunal, e cada trecho citado pela inteligência artificial é conferido no texto da decisão. O produto pode ser configurado para qualquer área do Direito, porque a área vigiada depende dos casos cadastrados e dos termos de busca.

O que entregamos além do prometido. Cada aviso informa o resultado da decisão e se ela é favorável ou desfavorável ao cliente. Criamos ainda um "segundo parecer": cada decisão é analisada duas vezes, e só vira aviso quando as duas análises concordam. Quando discordam, a decisão vai para "Revisar à mão". Fizemos isso depois de medir que um dos modelos testados dava respostas diferentes para a mesma decisão.

O que foi simplificado, e por quê. O site prometia vigiar leis, o Supremo Tribunal Federal, o Superior Tribunal de Justiça, o Banco Central, o Cade e a Receita. Esta versão vigia só o Tribunal de Justiça de São Paulo, porque a biblioteca pública que usamos para buscar decisões não cobre o Superior Tribunal de Justiça, e cada nova fonte exige um buscador próprio. O site prometia avisos na hora, por e-mail ou WhatsApp. Esta versão envia por e-mail ao final de cada execução. O WhatsApp exige um acesso oficial pago, e a execução automática diária depende de um computador ou servidor ligado. O site mostrava a escolha do que vigiar escrevendo em linguagem natural. Aqui, isso é feito editando os termos de busca no arquivo de configuração. O site mostrava contratos completos. Aqui, cada caso é uma descrição curta. Os acórdãos de segundo grau são analisados apenas pela ementa, e cada execução analisa cinco decisões, por causa dos limites do plano gratuito.

Sigilo. O site prometia criptografia do início ao fim. Uma criptografia completa não é possível quando uma inteligência artificial precisa ler o texto para analisá-lo. Nesta versão, usamos apenas casos inventados e decisões públicas, e o plano gratuito do Gemini pode usar os textos enviados para melhorar os produtos do Google. Em uso real, o caminho seria um plano pago, que não usa os dados para treinamento, e manter o nome do cliente apenas no computador do escritório, enviando à inteligência artificial só um código e a descrição do caso.

Próximos passos. Novas fontes, começando pelo Superior Tribunal de Justiça e pelos diários oficiais; execução automática diária em servidor; leitura do acórdão completo; cadastro de contratos inteiros; e envio de cada aviso apenas ao advogado responsável pelo caso.

## 8. Instalação e uso

### Instalar

Instale o Python 3.10 ou mais recente. Abra o Terminal (Mac/Linux) ou o PowerShell (Windows), entre na pasta do Telos e instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Se `python` não funcionar, tente `python3`.

### Configurar a chave do Gemini

1. Crie uma chave no [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Na pasta principal do Telos, crie o arquivo `.env` a partir do `.env.example`:

   ```bash
   cp .env.example .env
   ```

   No Windows PowerShell, use `Copy-Item .env.example .env`.

3. Abra `.env`, mantenha `AI_PROVIDER=gemini` e cole a chave depois de `GEMINI_API_KEY=`. O modelo padrão é `gemini-3.1-flash-lite`.
4. Salve o arquivo. Não compartilhe a chave: `.env` fica fora do Git.

### Usar a Groq como alternativa

Crie uma chave na [GroqCloud](https://console.groq.com/keys), cole-a depois de `GROQ_API_KEY=` no `.env` e altere `AI_PROVIDER=groq`. O modelo padrão é `openai/gpt-oss-120b`. Se ele rejeitar uma resposta por formato incompatível, o Telos tenta uma vez com `openai/gpt-oss-20b` e informa a troca. O Telos usa o SDK oficial `groq` para Python.

### Receber os avisos pelo Gmail

O envio é opcional. Se `GMAIL_SENDER`, `GMAIL_APP_PASSWORD` e `GMAIL_RECIPIENT` estiverem vazios, o Telos funciona como antes e não tenta enviar e-mail. Quando os três estiverem preenchidos, cada rodada envia um resumo: os avisos diretos ficam em cartões separados e os itens de “Revisar à mão”, com os pareceres em frases simples lado a lado, ficam em uma seção lilás própria. Cada aviso mostra um título curto para o caso e, quando constam no material, o número do processo, o foro, a vara e a data da decisão. Campos ausentes são identificados como não informados. O resumo descreve o que o tribunal decidiu. O assunto ajusta singular e plural. O visual usa o azul-marinho e a lavanda do site de apresentação da Themis Tech. A mensagem inclui uma versão HTML compatível com o Gmail e uma alternativa em texto simples.

Você pode abrir [email_exemplo.html](email_exemplo.html) no navegador para ver uma prévia. O arquivo usa resultados de uma rodada anterior, sem nomes das partes do processo.

Para criar a senha de app do Gmail:

1. Ative a [Verificação em duas etapas](https://support.google.com/accounts/answer/185839?hl=pt-BR) na sua Conta Google.
2. Abra a página de [senhas de app](https://myaccount.google.com/apppasswords), entre na conta que enviará os avisos e crie uma senha para o Telos. O Google mostra a senha uma única vez; guarde-a para o próximo passo.
3. No `.env`, preencha os três campos. Use o endereço Gmail que criou a senha em `GMAIL_SENDER`, a senha gerada em `GMAIL_APP_PASSWORD` e informe em `GMAIL_RECIPIENT` o endereço ou a lista de endereços que receberá as mensagens. Separe vários endereços por vírgula. Todos recebem a mensagem em cópia oculta, sem ver o endereço dos demais:

   ```text
   GMAIL_SENDER=seu-endereco@gmail.com
   GMAIL_APP_PASSWORD=senha-de-app-do-google
   GMAIL_RECIPIENT=destino1@exemplo.com,destino2@exemplo.com
   ```

   O Telos envia pelo servidor seguro do Gmail (`smtp.gmail.com`, TLS na porta 587). A senha de app requer Verificação em duas etapas; algumas contas de trabalho/escola, contas com Proteção Avançada ou contas que usam somente chaves de segurança podem não oferecer essa opção. Veja a [ajuda oficial do Google sobre senhas de app](https://support.google.com/accounts/answer/185833?hl=pt-BR) e os [parâmetros SMTP do Gmail](https://support.google.com/mail/answer/7104828?hl=pt-BR).

### Rodar o Telos

Com o Terminal ou PowerShell aberto na pasta principal, execute:

```bash
python telos.py
```

O Telos busca decisões no TJSP e analisa as decisões pendentes. Ao fim da rodada, envia o e-mail se os três campos do Gmail estiverem configurados. Para analisar somente os arquivos que já estão em `decisoes/`, sem fazer uma nova busca, execute:

```bash
python telos.py --sem-busca
```

Cada termo de `TJSP_SEARCH_TERMS` pode ter até 120 caracteres. Se a busca automática falhar, também é possível colocar um arquivo `.txt` ou PDF com texto selecionável na pasta `decisoes/`; inclua nele o link oficial do TJSP. PDFs digitalizados como imagem não são lidos nesta versão.
