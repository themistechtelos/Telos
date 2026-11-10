# Telos — Themis Tech

## 1. O que é o Telos

O Telos é um vigia de jurisprudência para escritórios de advocacia, criado pela Themis Tech. Ele busca decisões novas no Tribunal de Justiça de São Paulo (TJSP), compara essas decisões com os casos do escritório e avisa quais casos podem ter sido afetados. Os avisos informam o resultado da decisão e se ele favorece ou desfavorece a posição do cliente.

## 2. Como funciona

1. **Busca:** consulta decisões no TJSP com os termos configurados pelo escritório.
2. **Análise:** a inteligência artificial compara o texto encontrado com os casos cadastrados. Cada decisão recebe dois pareceres independentes.
3. **Aviso:** quando os pareceres concordam que há relação direta, o Telos mostra o resumo, o motivo, o resultado, trechos do documento e o link oficial.

## 3. Exemplo real de aviso

Este aviso foi produzido em uma rodada já realizada. Os nomes das partes foram omitidos:

> **Caso 4 — cobertura de cirurgia por plano de saúde**
>
> **Resumo:** a decisão reconheceu a cobertura de uma cirurgia que havia sido negada sob a justificativa de que o procedimento não constava no rol da ANS.
>
> **Resultado:** procedente. **Posição do cliente:** favorável.
>
> **Trecho da decisão:** “É abusiva a recusa de cobertura de custeio de cirurgia e materiais (prótese) essenciais à saúde do beneficiário, sob o argumento de não estarem previstos no rol de procedimentos da ANS”.
>
> **Consulta oficial do TJSP:** [abrir a decisão](https://esaj.tjsp.jus.br/cpopg/show.do?processo.codigo=GE000H9WU0000&processo.foro=590&processo.numero=1004083-13.2026.8.26.0590&gateway=true)

## 4. Proteções contra erros da IA

- **Citações conferidas:** o Telos verifica se cada trecho citado existe no texto da decisão. Citações que não aparecem no arquivo não são usadas como prova do aviso.
- **Link oficial controlado pelo programa:** nas buscas automáticas, o Telos monta o link de consulta com identificadores recebidos do TJSP. A IA não inventa nem escolhe o link. Para arquivos colocados manualmente, o Telos usa o link oficial informado no próprio arquivo.
- **Segundo parecer:** relação direta significa que a decisão resolve a mesma questão jurídica específica do caso, não apenas um tema parecido. Só há aviso quando as duas análises concordam sobre essa relação, o resultado e a favorabilidade. Se houver divergência, a decisão vai para **“Revisar à mão”**, junto com as duas respostas.
- **Incerteza explícita:** quando o material não permite uma conclusão segura, o Telos diz **“não tenho certeza”** em vez de afirmar que a decisão afeta o caso.

## 5. Como mudar a área vigiada

A área acompanhada depende dos casos cadastrados na pasta `casos/` e dos termos em `TJSP_SEARCH_TERMS` no arquivo `.env`. Para mudar o foco, edite as descrições dos casos e troque ou acrescente termos de busca, separados por ponto e vírgula. O programa não fica preso a uma área específica: Direito Bancário é apenas o exemplo inicial.

## 6. Limitações

- Por enquanto, as buscas automáticas são feitas somente no TJSP.
- A busca consulta uma página por termo em cada tipo de decisão.
- Para decisões de primeiro grau, o Telos analisa o texto disponível na busca. Para acórdãos, analisa somente a ementa; não baixa o acórdão completo.
- Cada rodada analisa até cinco decisões. O plano gratuito do provedor de IA também tem limites de uso.
- O Telos ajuda a localizar decisões que merecem atenção, mas não substitui a leitura da decisão nem a análise de uma advogada ou advogado.

## 7. Por que usamos o Gemini

Nas mesmas cinco decisões analisadas duas vezes, o Gemini produziu respostas idênticas nas duas rodadas. No teste equivalente com a Groq, as respostas foram diferentes em quatro das cinco decisões. Por esse resultado observado, o Gemini é o provedor padrão; a Groq continua disponível como alternativa. Esse teste é limitado e não garante que respostas futuras serão sempre iguais.

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

### Rodar o Telos

Com o Terminal ou PowerShell aberto na pasta principal, execute:

```bash
python telos.py
```

O Telos busca decisões no TJSP e analisa as decisões pendentes. Para analisar somente os arquivos que já estão em `decisoes/`, sem fazer uma nova busca, execute:

```bash
python telos.py --sem-busca
```

Cada termo de `TJSP_SEARCH_TERMS` pode ter até 120 caracteres. Se a busca automática falhar, também é possível colocar um arquivo `.txt` ou PDF com texto selecionável na pasta `decisoes/`; inclua nele o link oficial do TJSP. PDFs digitalizados como imagem não são lidos nesta versão.
