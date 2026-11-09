# Telos — Themis Tech

O Telos analisa decisões do Superior Tribunal de Justiça (STJ) e aponta, com apoio de inteligência artificial, possíveis relações com casos do escritório. A ferramenta é um apoio à pesquisa: não substitui a leitura da decisão nem a avaliação de uma advogada ou advogado.

## O que você precisa

- Python 3.10 ou mais recente.
- Uma chave da Gemini API, criada gratuitamente no [Google AI Studio](https://aistudio.google.com/app/apikey).
- Internet para enviar os textos à API do Gemini.

O nível gratuito tem limites que podem mudar. No nível gratuito, o Google informa que os dados enviados podem ser usados para melhorar os produtos. Não envie informações sigilosas, dados pessoais de clientes ou conteúdo protegido sem antes confirmar que isso é permitido pelo escritório e adequado às obrigações de confidencialidade. Mais informações: [preços e condições](https://ai.google.dev/gemini-api/docs/pricing) e [limites de uso](https://ai.google.dev/gemini-api/docs/rate-limits).

## 1. Instale o Python e prepare o Telos

Se ainda não tiver Python, baixe-o em [python.org/downloads](https://www.python.org/downloads/) e instale. Abra o Terminal (no Mac) ou Prompt de Comando/PowerShell (no Windows), entre na pasta do Telos e instale a dependência usada para ler PDFs:

```bash
python -m pip install -r requirements.txt
```

Em alguns computadores, o comando pode ser `python3` em vez de `python`. Nesse caso, troque `python` por `python3` nos comandos abaixo.

## 2. Crie sua chave gratuita e configure-a

1. Acesse [Google AI Studio — API keys](https://aistudio.google.com/app/apikey) com uma conta Google.
2. Crie uma chave de API para um projeto habilitado para o nível gratuito da Gemini API e copie a chave.
3. Na pasta principal do Telos, crie um arquivo chamado `.env` (o nome começa com ponto).
4. Dentro dele, escreva `GEMINI_API_KEY=` seguido da chave, sem aspas. Por exemplo: `GEMINI_API_KEY=sua_chave_aqui`.
5. Salve o arquivo. Não compartilhe nem publique a chave. O arquivo `.env` está excluído do Git para evitar que seja enviado ao GitHub.

O modelo padrão é `gemini-2.5-flash`. Se quiser configurar outro modelo disponível para sua conta, acrescente ao `.env` uma linha `GEMINI_MODEL=nome-do-modelo`. A disponibilidade e as cotas dependem do projeto e podem mudar.

## 3. Adicione os arquivos

- Coloque cada decisão em `decisoes/`, como arquivo `.txt` ou PDF com texto selecionável. Inclua no próprio arquivo o endereço oficial da decisão do STJ. Para PDF, o endereço precisa estar no texto extraível do documento; se estiver apenas escrito à mão ou como imagem, o Telos não o encontrará.
- Coloque cada caso como arquivo `.txt` em `casos/`. Já existem três exemplos correspondentes aos casos descritos para esta primeira versão; edite-os ou substitua-os conforme necessário.

O Telos não busca decisões na internet. Ele analisa somente os arquivos que você colocou nessas pastas. PDFs digitalizados como imagem, sem camada de texto, não são analisados.

## 4. Rode o programa

Com o Terminal aberto na pasta principal do Telos, execute:

```bash
python telos.py
```

O resultado aparece no próprio Terminal. Para cada decisão, o Telos mostra os casos que a IA considera afetados, um resumo simples, a justificativa, trechos copiados da decisão e o link que encontrou no arquivo. Se não houver relação confirmada, informa isso; se a análise for inconclusiva ou os trechos não puderem ser confirmados no arquivo, mostra “não tenho certeza”.

## Como a análise funciona e seus limites

O Telos envia o texto da decisão e as descrições dos casos à Gemini API para análise. O modelo pode interpretar contexto jurídico melhor que uma busca por palavras, mas pode cometer erros ou deixar passar relações. O programa exige trechos que apareçam literalmente no documento para sustentar uma relação indicada como confirmada; ainda assim, esses trechos não garantem que a interpretação esteja correta. Confira sempre a decisão oficial e peça revisão profissional antes de tomar qualquer providência jurídica.

O programa não inventa links: só exibe um endereço encontrado no arquivo da decisão. Se a chave estiver ausente, o documento não puder ser lido ou a resposta não trouxer evidência verificável, o Telos explica o problema ou indica incerteza.
