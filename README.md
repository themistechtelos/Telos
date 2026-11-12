# Telos — Themis Tech

## 1. O que é o Telos

O Telos é um vigia de jurisprudência para escritórios de advocacia, criado pela Themis Tech: busca decisões e temas repetitivos do Superior Tribunal de Justiça (STJ), compara o material com os casos do escritório e mostra quais casos podem ter sido afetados, o resultado e se ele favorece ou desfavorece a posição do cliente. Acesse o [site de apresentação](https://themistech.netlify.app), experimente o [Telos no ar](https://telos-zoor.onrender.com) ou consulte [este repositório no GitHub](https://github.com/themistechtelos/Telos).

## 2. Como testar em um minuto pelo site

1. Abra o [Telos no ar](https://telos-zoor.onrender.com). Se o serviço estiver dormindo, aguarde a página carregar.
2. Deixe a quantidade em **Todos** e escolha **Todas as áreas** ou uma área específica.
3. Deixe o campo de e-mail vazio para não enviar mensagem e clique em **Vigiar agora**. O Telos mostra o andamento e, em cerca de 20 segundos, reapresenta a rodada de demonstração com os avisos e a seção **Revisar à mão**.

## 3. Como funciona

1. **Fontes do STJ:** na busca ao vivo, o Telos procura decisões nos arquivos diários de texto e metadados do [Portal de Dados Abertos do STJ](https://dadosabertos.web.stj.jus.br/). Também consulta os temas repetitivos e suas teses na base oficial de precedentes qualificados. Arquivos de decisão em texto ou PDF com texto selecionável podem ser colocados manualmente em `decisoes/`, com o link oficial do STJ dentro do arquivo.
2. **Dois pareceres da IA:** o modelo analisa cada decisão duas vezes e compara cada parecer com as descrições dos casos. Só considera direta a relação em que a decisão resolve a mesma questão jurídica do caso; uma semelhança de assunto, por si só, não basta.
3. **Aviso com fonte:** os resultados aparecem na página. Ao fim da rodada, o Telos também envia um e-mail se houver destinatário configurado. O aviso traz o resumo, o motivo, o resultado, a favorabilidade, os trechos e o link oficial. Se os pareceres discordarem sobre a relação direta, o item fica em **Revisar à mão**. O e-mail pode ser reenviado pelo botão da página.

## 4. Exemplo real de aviso da demonstração

Este exemplo usa o [Tema 970 do STJ](https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?cod_tema_inicial=970&cod_tema_final=970&novaConsulta=true&tipo_pesquisa=T). O tema e a tese são reais; os casos do escritório abaixo são fictícios.

> O STJ decidiu que, em regra, a cláusula penal moratória equivalente ao valor locatício afasta sua cumulação com lucros cessantes. **3 casos do escritório são afetados.**
>
> Casos: Apartamento entregue com atraso; Multa e lucros cessantes; Multa moratória e aluguel.
>
> Favorabilidade: **a confirmar**.
>
> Trecho: “em regra, estabelecida em valor equivalente ao locativo, afasta-se sua cumulação com lucros cessantes”.
>
> [Conferir o Tema 970 no site oficial do STJ](https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?cod_tema_inicial=970&cod_tema_final=970&novaConsulta=true&tipo_pesquisa=T)

Uma [prévia do e-mail](email_exemplo.html) mostra a apresentação visual dos avisos e dos itens para revisão.

## 5. Proteções contra erros da IA

- **Trechos conferidos:** antes de usar uma citação como prova, o programa verifica se ela aparece no texto do arquivo analisado.
- **Link controlado pelo programa:** o modelo não cria nem escolhe links. Para temas, o Telos monta a consulta oficial com o número do tema; para decisões do portal, usa os dados e endereços oficiais do catálogo. Em arquivos manuais, valida o link informado no próprio arquivo.
- **Segundo parecer:** as duas análises precisam confirmar a relação direta e apresentar evidências encontradas no texto. Se divergirem sobre essa relação, o item vai para **Revisar à mão**. Se concordarem sobre a relação, mas não sobre o resultado ou a favorabilidade, o aviso sai com **“Favorabilidade a confirmar”**.
- **Incerteza explícita:** quando o texto não permite uma conclusão segura, o Telos informa que não tem certeza em vez de afirmar um resultado. Um aviso não substitui a conferência da fonte oficial.

## 6. Sigilo no cadastro de casos

No uso local, o nome do cliente fica no arquivo `.telos_clientes.json`, no computador do escritório; esse arquivo é ignorado pelo Git. A descrição é gravada junto a um código do caso. Para a análise ao vivo, o provedor de IA recebe o código e a descrição, não o nome. Depois da resposta, o programa associa o código ao nome no próprio computador para exibir avisos e preparar e-mails. A descrição do caso e o texto da decisão são enviados ao provedor de IA escolhido; não inclua nesses textos dados que não queira compartilhar com esse serviço.

Na hospedagem, o cadastro é uma simulação: o nome e a descrição digitados são enviados ao site hospedado para selecionar uma decisão de demonstração parecida. O exemplo é calculado sem IA e os dados do formulário não são gravados. Se a pessoa informar um e-mail, o exemplo enviado por e-mail inclui o nome digitado. Essa simulação não cria um caso para rodadas futuras.

## 7. Modo de demonstração

O modo de demonstração vem ligado por padrão. A página reapresenta uma rodada fixa que já foi analisada, com seis temas repetitivos do STJ: cinco com avisos diretos e um em **Revisar à mão**. O andamento é simulado; essa rodada não faz uma nova busca no STJ nem chama a IA. A área e a quantidade escolhidas filtram os itens da rodada. **Todos** mostra todos os itens da área selecionada; **Todas as áreas** mostra a rodada completa.

O modo é controlado por `TELOS_DEMO_MODE` no `.env`. No computador, `TELOS_DEMO_MODE=false` habilita a busca e a análise ao vivo. Na hospedagem, `TELOS_HOSPEDADO=true` mantém a demonstração ligada mesmo se outra configuração pedir busca ao vivo.

## 8. Limitações

- A única fonte de jurisprudência implementada é o STJ.
- A busca ao vivo cobre os últimos 21 dias para os quais o portal já disponibilizou os arquivos diários correspondentes. O portal pode publicar os arquivos com atraso.
- Cada rodada ao vivo analisa no máximo seis itens. A rodada fixa de demonstração também contém seis.
- Os resultados dependem do texto disponível e das respostas do modelo. Dois pareceres e citações verificadas reduzem riscos, mas não garantem uma conclusão correta.
- O Telos compara descrições curtas; não analisa contratos completos nem substitui a leitura da fonte oficial ou o trabalho de uma advogada ou advogado.
- O serviço gratuito do Render pode dormir após 15 minutos sem acesso e apaga arquivos locais quando dorme, reinicia ou recebe uma nova publicação. A rodada de demonstração está no repositório, mas a última rodada salva e o contador local de envios podem ser reiniciados. Por isso, o limite de e-mails da hospedagem — um envio por minuto e 20 por dia — pode ser reiniciado junto com esses arquivos. Consulte as [limitações oficiais do Render](https://render.com/docs/free).

## 9. Por que escolhemos a OpenAI

A OpenAI é o provedor padrão, com o modelo `gpt-6-luna`. O fluxo pede respostas estruturadas para conferir campos, citações e a concordância entre os dois pareceres. A OpenAI foi escolhida para esta versão por essa compatibilidade com o formato e por ser o provedor pago selecionado para o projeto; isso não significa que as respostas sejam sempre iguais.

Nos testes anteriores com cinco decisões e o conjunto de casos disponível à época, a Groq deu respostas diferentes em quatro decisões, enquanto o Gemini repetiu as mesmas respostas nas duas rodadas. Em um teste posterior, as respostas finais da OpenAI também não foram idênticas ao repetir oito decisões. Os testes usaram conjuntos anteriores ao atual e não provam que um provedor será sempre mais consistente. Por isso, o Telos mantém o segundo parecer e a possibilidade de revisão manual. Gemini e Groq continuam disponíveis como alternativas.

## 10. Parte técnica

### Rodar no computador

É necessário ter Python 3.10 ou mais recente. Abra o Terminal (Mac ou Linux) ou o PowerShell (Windows), entre na pasta do projeto e instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Copie `.env.example` para `.env`:

```bash
cp .env.example .env
```

No Windows PowerShell, use `Copy-Item .env.example .env`. Abra `.env`, mantenha `TELOS_DEMO_MODE=true` para usar a demonstração ou mude para `false` para busca ao vivo. Para a análise ao vivo, escolha o provedor em `AI_PROVIDER` e preencha a chave correspondente. A OpenAI é a opção padrão; as chaves são `OPENAI_API_KEY`, `GEMINI_API_KEY` e `GROQ_API_KEY`. Os nomes dos modelos podem ser ajustados em `OPENAI_MODEL`, `GEMINI_MODEL` e `GROQ_MODEL`.

Os termos de busca são configurados em `STJ_SEARCH_TERMS_BANCARIO`, `STJ_SEARCH_TERMS_IMOBILIARIO` e `STJ_SEARCH_TERMS_EMPRESARIAL`. Separe vários termos com ponto e vírgula. Se uma variável de área estiver vazia, o Telos pode usar o campo geral `STJ_SEARCH_TERMS`. As áreas e termos são configuráveis; os exemplos atuais estão no `.env.example`.

Para abrir a página, execute:

```bash
python webapp.py
```

Depois, abra [http://127.0.0.1:5000](http://127.0.0.1:5000) no navegador. Se definir a variável `PORT`, o programa usa essa porta; sem ela, usa `5000`. Não abra `templates/index.html` como arquivo: ele precisa do servidor Python para montar a página.

Para busca ao vivo, `TELOS_DEMO_MODE=false`, chave de IA e termos de busca válidos são necessários. Para enviar e-mail localmente, preencha `GMAIL_SENDER`, `GMAIL_APP_PASSWORD` e `GMAIL_RECIPIENT`. A senha de app do Gmail é criada na [página de senhas de app da Conta Google](https://myaccount.google.com/apppasswords); o Google exige a Verificação em duas etapas. Em `GMAIL_RECIPIENT`, pode haver vários endereços separados por vírgula; o Telos os envia em cópia oculta.

O `.env` contém segredos e não deve ser enviado ao GitHub. O `.gitignore` já exclui esse arquivo e os dados locais de cadastro.

### Hospedar no Render

O arquivo `render.yaml` configura um serviço web gratuito. No Render, crie um **Blueprint** conectado a este repositório. O serviço usa `requirements-hosting.txt`, inicia o `webapp.py` com Gunicorn e recebe a porta da variável `PORT`, definida pelo Render. A configuração mantém `TELOS_HOSPEDADO=true` e `TELOS_DEMO_MODE=true`; assim, a busca ao vivo e as chaves de IA não são necessárias.

No painel do Render, cadastre apenas `GMAIL_SENDER` e `BREVO_API_KEY` se quiser enviar e-mails. O endereço usado em `GMAIL_SENDER` deve estar autorizado como remetente na conta Brevo. Na hospedagem, o e-mail de cada rodada só é enviado se a pessoa preencher o campo da página; esse endereço é o único destinatário, e `GMAIL_RECIPIENT` é ignorado. Não cadastre chaves de IA, senha de app do Gmail nem termos de busca no Render para esta demonstração. Coloque valores secretos no painel do Render, nunca no código ou no GitHub.

### Licença

O Telos é distribuído sob a [licença MIT](LICENSE), em nome de Themis Tech, ano 2026.
