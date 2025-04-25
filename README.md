
# FTP Benchmark

**FTP Benchmark** é um script em Python que realiza testes de velocidade de Upload e Download via FTP, gerando relatórios de performance automaticamente.

---

## Requisitos

- Python 3.8+
- Bibliotecas:
  - `questionary`
  - `matplotlib`
  - `rich`
  - `python-dotenv`

Instale todas as dependências com:

```bash
pip install -r requirements.txt
```

---

## Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
FTP_ENDERECO=ftp.seu_servidor.com
FTP_USUARIO=seu_usuario
FTP_SENHA=sua_senha
FTP_DIRETORIO=seu_diretorio
```

Use o `.env.example` como referência.

---

## Como usar

Execute o script principal:

```bash
python ftp_benchmark.py
```

Durante a execução, você poderá:
- Definir o nome do teste
- Escolher os tamanhos dos arquivos para teste
- Selecionar Upload, Download ou ambos
- Visualizar barras de progresso para cada operação

Relatórios gerados:
- `relatorios/*.txt` (texto simples)
- `relatorios/*.md` (Markdown)
- `relatorios/*.csv` (dados tabulares)
- `grafico_resultados.png` (gráfico de performance)

---

## Features

- Teste de latência via Ping antes dos testes.
- Upload e download com barra de progresso (Rich).
- Cálculo de velocidades em Mbps e MB/s.
- Verificação de integridade (comparando tamanhos dos arquivos).
- Relatórios automáticos em `.txt`, `.md` e `.csv`.
- Geração de gráfico dinâmico com `matplotlib`.
- Limpeza automática de arquivos locais e remotos após o teste.

---

## Estrutura do Projeto

```bash
.
├── .env
├── .env.example
├── ftp_benchmark.py
├── requirements.txt
├── relatorios/
│   └── (arquivos de relatórios gerados)
```

---

## Avisos

- **Não** versionar o arquivo `.env` contendo credenciais reais.
- Ajuste os tamanhos de teste conforme o seu ambiente (pode gerar arquivos grandes).
- Testes de Upload e Download são feitos utilizando o modo binário (`TYPE I`) para evitar corrupção de dados.
