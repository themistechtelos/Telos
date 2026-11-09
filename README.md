# Telos — Themis Tech

O Telos busca decisões do Tribunal de Justiça de São Paulo (TJSP) pelos termos configurados e compara o conteúdo com os casos cadastrados. A área acompanhada depende dos arquivos na pasta `casos/` e dos termos em `TJSP_SEARCH_TERMS` no `.env`; não é fixa no código. Direito Bancário é apenas o exemplo inicial, agora acompanhado por exemplos de Direito do Consumidor. A ferramenta é um apoio à pesquisa: não substitui a leitura da decisão nem a avaliação de uma advogada ou advogado.

## O que você precisa

- Python 3.10 ou mais recente.
- Uma chave gratuita do [Google AI Studio](https://aistudio.google.com/app/apikey) para usar o Gemini. A Groq continua disponível como alternativa, com uma chave da [GroqCloud](https://console.groq.com/keys).
- Internet para consultar o TJSP e enviar os textos ao provedor escolhido.

O Gemini é o provedor padrão porque, no teste feito pelo Telos, suas saídas foram idênticas nas duas rodadas das mesmas cinco decisões; com a Groq, houve diferenças em quatro de cinco. Esse resultado descreve apenas nosso teste e não garante que as respostas futuras serão sempre iguais.

## Usar a Groq como alternativa

O modelo Groq padrão é `openai/gpt-oss-120b`: ele está nos limites do plano gratuito, é multilíngue e teve 85,3% na avaliação MMMLU em português no nível alto de raciocínio. A Groq oferece JSON Schema estrito para esse modelo. O Telos usa temperatura zero e uma semente fixa para reduzir variações; a Groq ressalva que isso não garante repetibilidade. Se o modelo padrão rejeitar uma resposta por formato JSON incompatível, o Telos tenta uma vez com `openai/gpt-oss-20b` e identifica a troca no aviso. Confira os [modelos e limites da Groq](https://console.groq.com/docs/rate-limits), os [formatos estruturados compatíveis](https://console.groq.com/docs/structured-outputs) e os [parâmetros de consistência](https://console.groq.com/docs/prompting).

A Groq informa que não mantém por padrão os dados enviados para inferência, mas pode registrar temporariamente entradas e saídas para investigar problemas de confiabilidade ou abuso. Não envie informações sigilosas, dados pessoais de clientes ou conteúdo protegido sem confirmar que isso é permitido pelo escritório. Consulte [como a Groq trata os dados](https://console.groq.com/docs/your-data).

## 1. Instale o Python e prepare o Telos

Se ainda não tiver Python, baixe-o em [python.org/downloads](https://www.python.org/downloads/) e instale. Abra o Terminal (no Mac) ou Prompt de Comando/PowerShell (no Windows), entre na pasta do Telos e instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Em alguns computadores, o comando pode ser `python3` em vez de `python`. Nesse caso, troque `python` por `python3` nos comandos abaixo.

## 2. Configure o Gemini como provedor padrão

1. Crie uma chave no [Google AI Studio](https://aistudio.google.com/app/apikey) e copie-a.
2. Na pasta principal do Telos, crie `.env` copiando o arquivo `.env.example`, se ainda não existir.
3. Mantenha `AI_PROVIDER=gemini` e cole a chave depois de `GEMINI_API_KEY=`. Não coloque aspas.
4. Salve o arquivo. Não compartilhe nem publique a chave. O arquivo `.env` está excluído do Git.

O modelo Gemini padrão é `gemini-3.1-flash-lite`. Para escolher outro, altere `GEMINI_MODEL`.

### Configurar a Groq em vez do Gemini

1. Crie uma conta na [GroqCloud](https://console.groq.com/) e crie uma chave de API.
2. No `.env`, coloque-a depois de `GROQ_API_KEY=` e mude para `AI_PROVIDER=groq`.
3. O modelo padrão é `openai/gpt-oss-120b`. Para escolher outro compatível com saída estruturada, altere `GROQ_MODEL`.

## 3. Configure a busca do TJSP

Ao iniciar, o Telos faz buscas automáticas usando os métodos estáveis do `juscraper` para o TJSP. A primeira versão consulta uma página por termo em cada tipo de busca, para limitar o volume de consultas:

- `cjpg`: decisões e sentenças de primeiro grau; o texto da decisão é analisado.
- `cjsg`: acórdãos de segundo grau; nesta versão, o Telos analisa somente a ementa, não baixa o acórdão completo. O aviso do resultado informa quando a análise usou apenas a ementa.

O Telos não limita a busca a uma área do Direito. A área acompanhada depende das descrições em `casos/` e dos termos em `TJSP_SEARCH_TERMS` no `.env`: adicione os assuntos que quer acompanhar e cadastre os casos correspondentes. Direito Bancário é apenas o exemplo inicial. Se nenhum termo estiver configurado, a busca automática não é executada.

O `.env.example` traz termos de exemplo para empréstimos, cartão de crédito, garantias em financiamentos, cobertura de cirurgia por plano de saúde e cancelamento de voos. Você pode editar a linha do `.env` para incluir, remover ou substituir temas, mantendo os termos separados por ponto e vírgula. Cada termo pode ter até 120 caracteres:

```text
TJSP_SEARCH_TERMS=juros contrato empréstimo bancário;cartão de crédito dívida negativação pagamento;garantia contrato financiamento bancário;plano de saúde negativa cobertura cirurgia rol ANS;plano de saúde procedimento cirurgia rol ANS;cancelamento de voo companhia aérea danos morais;cancelamento de voo sem aviso reacomodação indenização
```

Os resultados são salvos como arquivos `auto_*.txt` na pasta `decisoes/`, com o texto disponível e a referência oficial da consulta. Para sentenças de primeiro grau, o Telos monta o endereço da consulta de processo do e-SAJ com o código do processo e o número CNJ fornecidos pelo TJSP. Para acórdãos, monta o endereço oficial do e-SAJ a partir dos códigos do acórdão e do foro fornecidos pelo TJSP. Esses endereços são links para a consulta oficial do TJSP; o acesso pode depender das regras e da disponibilidade do próprio tribunal. Arquivos automáticos são locais e ficam fora do Git.

## 4. Adicione decisões manualmente, se necessário

Se a busca automática falhar ou você quiser incluir outra decisão, coloque o arquivo `.txt` ou PDF com texto selecionável em `decisoes/`. Inclua o link oficial do TJSP no próprio arquivo. O Telos aceita endereços HTTPS de `tjsp.jus.br` e seus subdomínios. PDFs digitalizados como imagem, sem camada de texto, não são analisados.

Se o arquivo manual trouxer apenas a ementa de um acórdão, identifique isso no começo do texto, em uma linha como `Tipo de conteúdo: ementa (ementa apenas; inteiro teor não incluído)`. O Telos então exibirá o aviso correspondente na análise.

Os arquivos em `casos/` contêm cinco casos de exemplo: três bancários, um sobre cobertura de cirurgia por plano de saúde e um sobre cancelamento de voo. Você pode editar, remover ou substituir esses arquivos `.txt` por descrições curtas; as áreas acompanhadas mudam conforme esses casos e os termos de busca configurados.

## 5. Rode o programa

Com o Terminal aberto na pasta principal do Telos, execute:

```bash
python telos.py
```

O programa busca decisões primeiro e depois analisa os arquivos em `decisoes/`, sejam automáticos ou manuais. Cada rodada envia no máximo cinco decisões ao provedor escolhido. Cada decisão recebe duas análises separadas, com uma pausa de seis segundos entre as chamadas. Para caber no limite gratuito da Groq, documentos muito longos são enviados em trechos do início e do final; o aviso informa quando isso ocorrer e as citações continuam sendo conferidas contra o arquivo completo. Nesses casos, a parte não enviada pode conter informação relevante, então confira o texto integral. As análises concluídas ficam registradas localmente para que a próxima execução continue com as decisões pendentes; uma decisão alterada é considerada nova. Se houver mais de cinco pendentes, rode o Telos novamente para iniciar outra rodada. Se a busca automática estiver indisponível, o Telos ainda tenta analisar os arquivos que já existem na pasta. Para analisar apenas os arquivos locais, sem consultar o TJSP, rode:

```bash
python telos.py --sem-busca
```

Para cada decisão, o Telos faz duas análises independentes. Uma relação direta exige que a decisão resolva a mesma questão jurídica específica do caso; tratar apenas de tema parecido não basta. O aviso só é emitido se as duas análises concordarem que a relação é direta, no resultado da decisão e na favorabilidade para o cliente. Se divergirem sobre qualquer uma dessas classificações, a decisão vai para “Revisar à mão”, com as duas respostas completas. Relações indiretas que tenham consenso aparecem numa seção separada “Para conhecimento” e não são apresentadas como avisos. Os avisos de impacto trazem resumo, motivo, trechos do material e link oficial. Também informam o resultado da decisão quando ele estiver expresso no texto e se ele favorece ou desfavorece a posição descrita para o cliente, sempre com um trecho literal de apoio. Se não conseguirem identificar o resultado, as análises dizem isso; quando a fonte for apenas uma ementa, o Telos informa expressamente se o resultado não aparece nela. Se a favorabilidade ou a relação for inconclusiva, o resultado dirá “não tenho certeza”.

## Como a análise funciona e seus limites

O Telos envia duas vezes o texto da decisão ou a ementa e as descrições dos casos ao provedor selecionado em `AI_PROVIDER`. Cada resposta é solicitada num formato JSON Schema e validada antes da comparação. No Gemini, erros temporários de serviço ou de cota são repetidos automaticamente até cinco tentativas; a decisão só é marcada como analisada depois que os dois pareceres terminam. A relação direta requer que a decisão resolva a mesma questão jurídica específica do caso, não apenas que mencione assunto parecido. Uma divergência na relação, no resultado da decisão ou na favorabilidade impede a emissão de aviso e encaminha as duas respostas para “Revisar à mão”. Os trechos que sustentam a relação, o resultado e a favorabilidade precisam existir literalmente no material analisado. O modelo pode cometer erros ou deixar passar relações, e citações literais não garantem que a interpretação jurídica esteja correta. Confira a decisão oficial e peça revisão profissional antes de tomar qualquer providência.

Na análise de acórdãos, uma ementa pode não trazer todos os fatos ou fundamentos presentes no acórdão completo. Por isso, o Telos destaca quando analisou apenas a ementa e pode responder “não tenho certeza” se ela não der base suficiente. O download do inteiro teor de acórdãos não faz parte desta versão.
