# 📈 FTP Benchmark

**FTP Benchmark** é um script Python interativo para testar a performance de **upload e download** via FTP. Ele mede velocidades, verifica integridade dos arquivos e gera relatórios em vários formatos, além de um gráfico visual de desempenho.

## GitAds Sponsored
[![Sponsored by GitAds](https://gitads.dev/v1/ad-serve?source=gabireze/ftp-benchmark@github)](https://gitads.dev/v1/ad-track?source=gabireze/ftp-benchmark@github)

---

## ✅ Requisitos

- Python **3.8+**
- Bibliotecas:
  - [`questionary`](https://github.com/tmbo/questionary)
  - [`matplotlib`](https://matplotlib.org/)
  - [`rich`](https://rich.readthedocs.io/)
  - [`python-dotenv`](https://github.com/theskumar/python-dotenv)

Instale todas as dependências com:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração

Crie um arquivo `.env` com as credenciais do seu servidor FTP:

```env
FTP_ENDERECO=ftp.seu_servidor.com
FTP_USUARIO=seu_usuario
FTP_SENHA=sua_senha
FTP_DIRETORIO=diretorio_remoto
```

Use o `.env.example` como modelo.

---

## 🚀 Como usar

Execute o script principal:

```bash
python ftp_benchmark.py
```

Durante a execução você poderá:

- Definir o nome do teste
- Escolher os tamanhos dos arquivos (100MB, 512MB, 1GB)
- Selecionar Upload, Download ou ambos
- Escolher o tamanho do buffer (32KB, 64KB, 128KB, 256KB)
- Visualizar a latência com `ping`

---

## 🧾 Relatórios Gerados

- `relatorios/*.txt` — Relatório em texto simples
- `relatorios/*.md` — Relatório em Markdown
- `relatorios/*.csv` — Relatório tabular em CSV
- `grafico_resultados.png` — Gráfico de performance (Upload/Download)

---

## 🛠️ Funcionalidades

- Teste de latência via `ping`
- Upload e download com barra de progresso interativa
- Cálculo de velocidade em **Mbps** e **MB/s**
- Verificação de integridade do arquivo (comparação de tamanho)
- Relatórios automáticos em `.txt`, `.md`, `.csv`
- Gráfico dinâmico com `matplotlib`
- Limpeza automática de arquivos locais e remotos após os testes

---

## 📁 Estrutura do Projeto

```bash
.
├── .env
├── .env.example
├── ftp_benchmark.py
├── requirements.txt
├── relatorios/
│   └── (relatórios gerados)
```

---

## ⚠️ Avisos

- **Não** versionar o `.env` com credenciais reais
- Os arquivos de teste podem ser grandes — ajuste conforme seu ambiente
- Os testes usam modo binário (`TYPE I`) para garantir integridade nos dados

<!-- GitAds-Verify: K1EYRYQBCVXDP1D5V39E59VYVE1MNLG1 -->
