# Telos — Themis Tech

O Telos busca decisões do Tribunal de Justiça de São Paulo (TJSP) em Direito Bancário e usa o Gemini para apontar possíveis relações com os casos do escritório. A ferramenta é um apoio à pesquisa: não substitui a leitura da decisão nem a avaliação de uma advogada ou advogado.

## O que você precisa

- Python 3.10 ou mais recente.
- Uma chave da Gemini API, criada gratuitamente no [Google AI Studio](https://aistudio.google.com/app/apikey).
- Internet para consultar o TJSP e enviar os textos à API do Gemini.

O nível gratuito da Gemini tem limites que podem mudar. O Google informa que, no nível gratuito, os dados enviados podem ser usados para melhorar os produtos. Não envie informações sigilosas, dados pessoais de clientes ou conteúdo protegido sem confirmar que isso é permitido pelo escritório. Mais informações: [preços e condições](https://ai.google.dev/gemini-api/docs/pricing) e [limites de uso](https://ai.google.dev/gemini-api/docs/rate-limits).

## 1. Instale o Python e prepare o Telos

Se ainda não tiver Python, baixe-o em [python.org/downloads](https://www.python.org/downloads/) e instale. Abra o Terminal (no Mac) ou Prompt de Comando/PowerShell (no Windows), entre na pasta do Telos e instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Em alguns computadores, o comando pode ser `python3` em vez de `python`. Nesse caso, troque `python` por `python3` nos comandos abaixo.

## 2. Crie sua chave gratuita e configure-a

1. Acesse [Google AI Studio — API keys](https://aistudio.google.com/app/apikey) com uma conta Google.
2. Crie uma chave de API para um projeto habilitado para o nível gratuito da Gemini API e copie a chave.
3. Na pasta principal do Telos, crie um arquivo chamado `.env` (o nome começa com ponto).
4. Dentro dele, escreva `GEMINI_API_KEY=` seguido da chave, sem aspas. Por exemplo: `GEMINI_API_KEY=sua_chave_aqui`.
5. Salve o arquivo. Não compartilhe nem publique a chave. O arquivo `.env` está excluído do Git.

O modelo padrão é `gemini-3.1-flash-lite`, escolhido por estar disponível no nível gratuito e aceitar respostas estruturadas. Se quiser usar outro modelo disponível para sua conta, acrescente uma linha `GEMINI_MODEL=nome-do-modelo` ao `.env`.

## 3. Configure a busca do TJSP

Ao iniciar, o Telos faz buscas automáticas usando os métodos estáveis do `juscraper` para o TJSP. A primeira versão consulta uma página por termo em cada tipo de busca, para limitar o volume de consultas:

- `cjpg`: decisões e sentenças de primeiro grau; o texto da decisão é analisado.
- `cjsg`: acórdãos de segundo grau; nesta versão, o Telos analisa somente a ementa, não baixa o acórdão completo. O aviso do resultado informa quando a análise usou apenas a ementa.

Os termos iniciais cobrem juros em empréstimos, dívidas de cartão e garantias em financiamentos, conforme os casos de exemplo. Para alterá-los, acrescente ao `.env` uma linha com termos separados por ponto e vírgula. Cada termo pode ter até 120 caracteres:

```text
TJSP_SEARCH_TERMS=juros de empréstimo;cartão de crédito negativação;garantia financiamento
```

Os resultados são salvos como arquivos `auto_*.txt` na pasta `decisoes/`, com o texto disponível e a referência oficial da consulta. Para sentenças de primeiro grau, o Telos monta o endereço da consulta de processo do e-SAJ com o código do processo e o número CNJ fornecidos pelo TJSP. Para acórdãos, monta o endereço oficial do e-SAJ a partir dos códigos do acórdão e do foro fornecidos pelo TJSP. Esses endereços são links para a consulta oficial do TJSP; o acesso pode depender das regras e da disponibilidade do próprio tribunal. Arquivos automáticos são locais e ficam fora do Git.

## 4. Adicione decisões manualmente, se necessário

Se a busca automática falhar ou você quiser incluir outra decisão, coloque o arquivo `.txt` ou PDF com texto selecionável em `decisoes/`. Inclua o link oficial do TJSP no próprio arquivo. O Telos aceita endereços HTTPS de `tjsp.jus.br` e seus subdomínios. PDFs digitalizados como imagem, sem camada de texto, não são analisados.

Se o arquivo manual trouxer apenas a ementa de um acórdão, identifique isso no começo do texto, em uma linha como `Tipo de conteúdo: ementa (ementa apenas; inteiro teor não incluído)`. O Telos então exibirá o aviso correspondente na análise.

Os arquivos de exemplo em `casos/` correspondem aos três casos descritos para esta primeira versão. Você pode editá-los ou substituí-los por arquivos `.txt` com descrições curtas.

## 5. Rode o programa

Com o Terminal aberto na pasta principal do Telos, execute:

```bash
python telos.py
```

O programa busca decisões primeiro e depois analisa os arquivos em `decisoes/`, sejam automáticos ou manuais. Cada rodada envia no máximo cinco decisões ao Gemini e espera seis segundos entre chamadas. As análises concluídas ficam registradas localmente para que a próxima execução continue com as decisões pendentes; uma decisão alterada é considerada nova. Se houver mais de cinco pendentes, rode o Telos novamente para iniciar outra rodada. Se a busca automática estiver indisponível, o Telos ainda tenta analisar os arquivos que já existem na pasta. Para analisar apenas os arquivos locais, sem consultar o TJSP, rode:

```bash
python telos.py --sem-busca
```

Para cada decisão, o Telos mostra os casos possivelmente afetados, um resumo simples, a justificativa, trechos encontrados no material e o link oficial. Também informa o resultado da decisão quando ele estiver expresso no texto e avalia se ele favorece ou desfavorece a posição descrita para o cliente, sempre com um trecho literal de apoio. Se não conseguir identificar o resultado, informa isso; quando a análise usar apenas a ementa, diz expressamente que o resultado não aparece na ementa disponível. Se a favorabilidade ou a relação for inconclusiva, o resultado dirá “não tenho certeza”.

## Como a análise funciona e seus limites

O Telos envia o texto da decisão ou a ementa e as descrições dos casos à Gemini API. A resposta é solicitada num formato JSON com campos e categorias definidos, e validada antes de ser exibida. Os trechos que sustentam a relação, o resultado e a favorabilidade precisam existir literalmente no material analisado; se não existir trecho para sustentar a favorabilidade, o Telos diz que não tem certeza. O modelo pode cometer erros ou deixar passar relações, e citações literais não garantem que a interpretação jurídica esteja correta. Confira a decisão oficial e peça revisão profissional antes de tomar qualquer providência.

Na análise de acórdãos, uma ementa pode não trazer todos os fatos ou fundamentos presentes no acórdão completo. Por isso, o Telos destaca quando analisou apenas a ementa e pode responder “não tenho certeza” se ela não der base suficiente. O download do inteiro teor de acórdãos não faz parte desta versão.
