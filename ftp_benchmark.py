# ============ Verificação de Dependências ============
try:
    import questionary
    import matplotlib
    import dotenv
    from rich import print
    import logging
    import sys
except ImportError as e:
    print(
        f"[red]❌ Dependência faltante: {e}. Execute 'pip install -r requirements.txt'[/red]"
    )
    sys.exit(1)

# ============ Imports ============
import os
import time
import csv
import subprocess
import argparse
from datetime import datetime
from ftplib import FTP
import matplotlib.pyplot as plt
from rich.progress import (
    Progress,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from dotenv import load_dotenv

# ============ Setup Inicial ============
load_dotenv()

# ============ Configuração de Logging ============
logging.basicConfig(
    filename="ftp_teste.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("🚀 Script de Teste FTP iniciado.")

# ============ Funções auxiliares ============


def criar_arquivo(nome, tamanho_mb):
    if not os.path.exists(nome):
        print(f'[yellow]Criando arquivo "{nome}" de {tamanho_mb} MB...[/yellow]')
        with open(nome, "wb") as f:
            f.write(b"\0" * (tamanho_mb * 1024 * 1024))
        print("[green]✔ Arquivo criado com sucesso![/green]\n")
    else:
        print(f'[cyan]ℹ Arquivo "{nome}" já existe. Pulando criação.[/cyan]\n')


def upload_arquivo(ftp, nome, buffer_size):
    print("[bold blue]🚀 Iniciando upload com barra de progresso...[/bold blue]")
    filesize = os.path.getsize(nome)
    start = time.time()

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TransferSpeedColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("Upload", total=filesize)
        with open(nome, "rb") as file:
            ftp.voidcmd("TYPE I")
            with ftp.transfercmd(f"STOR {nome}") as conn:
                while True:
                    data = file.read(buffer_size)
                    if not data:
                        break
                    conn.sendall(data)
                    progress.update(task, advance=len(data))
            ftp.voidresp()

    end = time.time()
    tempo = end - start
    velocidade_mbps = (filesize * 8) / (tempo * 1024 * 1024)
    velocidade_mbs = filesize / (tempo * 1024 * 1024)
    mins, secs = divmod(int(tempo), 60)
    tempo_formatado = f"{mins}m {secs}s" if mins else f"{secs}s"

    print(
        f"[green]✔ Upload concluído em {tempo_formatado} ➔ {velocidade_mbps:.2f} Mbps / {velocidade_mbs:.2f} MB/s[/green]\n"
    )
    return tempo_formatado, velocidade_mbps, velocidade_mbs


def download_arquivo(ftp, nome, nome_download, buffer_size):
    print("[bold blue]🚀 Iniciando download com barra de progresso...[/bold blue]")
    filesize = ftp.size(nome)
    start = time.time()

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TransferSpeedColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("Download", total=filesize)
        with open(nome_download, "wb") as file:
            ftp.voidcmd("TYPE I")
            with ftp.transfercmd(f"RETR {nome}") as conn:
                while True:
                    data = conn.recv(buffer_size)
                    if not data:
                        break
                    file.write(data)
                    progress.update(task, advance=len(data))
            ftp.voidresp()

    end = time.time()
    tempo = end - start
    velocidade_mbps = (filesize * 8) / (tempo * 1024 * 1024)
    velocidade_mbs = filesize / (tempo * 1024 * 1024)
    mins, secs = divmod(int(tempo), 60)
    tempo_formatado = f"{mins}m {secs}s" if mins else f"{secs}s"

    print(
        f"[green]✔ Download concluído em {tempo_formatado} ➔ {velocidade_mbps:.2f} Mbps / {velocidade_mbs:.2f} MB/s[/green]\n"
    )
    return tempo_formatado, velocidade_mbps, velocidade_mbs


def apagar_arquivo_local(nome):
    if os.path.exists(nome):
        os.remove(nome)
        print(f"[red]🗑️ Arquivo local '{nome}' apagado.[/red]")


def apagar_arquivo_ftp(ftp, nome):
    try:
        ftp.delete(nome)
        print(f"[red]🗑️ Arquivo no FTP '{nome}' apagado.[/red]")
    except Exception as e:
        print(f"[yellow]⚠ Não foi possível apagar '{nome}' no FTP: {e}[/yellow]")


def testar_ping(host):
    print(f"\n[cyan]📡 Testando latência para {host}...[/cyan]")
    try:
        resultado = subprocess.run(
            ["ping", "-n", "4", host], capture_output=True, text=True
        )
        print("[bold white]" + resultado.stdout + "[/bold white]")
    except Exception as e:
        print(f"[yellow]⚠ Erro ao testar ping: {e}[/yellow]")


def salvar_relatorio_txt(nome_teste, resultados, inicio, fim, uploads, downloads):
    os.makedirs("relatorios", exist_ok=True)
    timestamp = fim.strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = os.path.join("relatorios", f"relatorio_{timestamp}.txt")

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(f"=== {nome_teste} ===\n")
        f.write(f"Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Fim: {fim.strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Tempo total: {int((fim - inicio).total_seconds())} segundos\n")
        f.write(f"Arquivos testados: {len(uploads)}\n")
        if uploads:
            f.write(f"Velocidade média Upload: {sum(uploads)/len(uploads):.2f} Mbps\n")
        if downloads:
            f.write(
                f"Velocidade média Download: {sum(downloads)/len(downloads):.2f} Mbps\n"
            )
        f.write("=" * 40 + "\n\n")
        for linha in resultados:
            if linha.strip() == "":
                f.write("\n")
            elif linha.startswith("Arquivo:"):
                f.write(f"{linha}\n")
            else:
                f.write(f"    {linha}\n")
    print(f"[bold cyan]📄 Relatório .txt salvo em: {nome_arquivo}[/bold cyan]")


def salvar_relatorio_markdown(nome_teste, resultados, inicio, fim, uploads, downloads):
    os.makedirs("relatorios", exist_ok=True)
    timestamp = fim.strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = os.path.join("relatorios", f"relatorio_{timestamp}.md")

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(f"# 📄 {nome_teste}\n\n")
        f.write(f"**Início:** {inicio.strftime('%d/%m/%Y %H:%M:%S')}  \n")
        f.write(f"**Fim:** {fim.strftime('%d/%m/%Y %H:%M:%S')}  \n")
        f.write(f"**Tempo total:** {int((fim - inicio).total_seconds())} segundos  \n")
        f.write(f"**Arquivos testados:** {len(uploads)}  \n")
        if uploads:
            f.write(
                f"**Velocidade média Upload:** {sum(uploads)/len(uploads):.2f} Mbps  \n"
            )
        if downloads:
            f.write(
                f"**Velocidade média Download:** {sum(downloads)/len(downloads):.2f} Mbps  \n"
            )
        f.write("\n---\n\n")
        for linha in resultados:
            if linha.strip() == "":
                f.write("\n")
            elif linha.startswith("Arquivo:"):
                f.write(f"## {linha}\n")
            else:
                f.write(f"- {linha.strip()}\n")
    print(
        f"[bold cyan]📄 Relatório Markdown (.md) salvo em: {nome_arquivo}[/bold cyan]"
    )


def salvar_relatorio_csv(nome_teste, resultados, inicio, fim, uploads, downloads):
    os.makedirs("relatorios", exist_ok=True)
    timestamp = fim.strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = os.path.join("relatorios", f"relatorio_{timestamp}.csv")

    with open(nome_arquivo, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Arquivo", "Upload (Mbps)", "Download (Mbps)", "Integridade"])
        for res, up, down in zip(resultados, uploads, downloads):
            if res.startswith("Arquivo:"):
                arquivo = res.split(":")[1].strip()
                integridade = "OK" if "OK" in res else "FALHA"
                writer.writerow([arquivo, up, down, integridade])

    print(f"[bold cyan]📄 Relatório CSV salvo em: {nome_arquivo}[/bold cyan]")


def live_plot(tamanhos, uploads, downloads):
    plt.clf()
    plt.plot(tamanhos, uploads, marker="o", label="Upload (Mbps)")
    plt.plot(tamanhos, downloads, marker="s", label="Download (Mbps)")
    plt.xlabel("Tamanho do Arquivo (MB)")
    plt.ylabel("Velocidade (Mbps)")
    plt.title("Resultados de Upload e Download (Live)")
    plt.grid(True)
    plt.legend()
    plt.pause(0.1)


# ============ Credenciais e Configurações ============
endereco_ftp = os.getenv("FTP_ENDERECO", "192.168.0.1")
usuario = os.getenv("FTP_USUARIO", "admin")
senha = os.getenv("FTP_SENHA", "password")
diretorio_remoto = os.getenv("FTP_DIRETORIO", "C")

# ============ Início do Script ============
print("[bold cyan]\n=== Teste de Velocidade FTP ===[/bold cyan]\n")

nome_teste = (
    questionary.text("📝 Nome do teste (padrão: Teste FTP):").ask() or "Teste FTP"
)
inicio_teste = datetime.now()

# Teste de Ping
testar_ping(endereco_ftp)

# Escolha de Ações
acoes = questionary.checkbox(
    "🛠️ Escolha o(s) teste(s):",
    choices=[
        questionary.Choice("Upload", checked=True),
        questionary.Choice("Download", checked=True),
    ],
).ask()

# ============ CLI - Argumentos ============

parser = argparse.ArgumentParser(description="Script de Teste FTP")
args = parser.parse_args()

# Interface amigável para seleção de tamanhos de arquivo
tamanhos_escolhidos = questionary.checkbox(
    "📦 Selecione os tamanhos de arquivo para testar:",
    choices=[
        questionary.Choice(title="📁 Pequeno (100 MB)", value="100", checked=True),
        questionary.Choice(title="📁 Médio (512 MB)", value="512", checked=True),
        questionary.Choice(title="📁 Grande (1 GB)", value="1024", checked=True),
    ],
).ask()

args.tamanho = list(map(int, tamanhos_escolhidos or ["100", "512", "1024"]))

# Interface amigável para seleção de buffer
buffer_escolhido = questionary.select(
    "📐 Escolha o tamanho do buffer para upload/download:",
    choices=[
        questionary.Choice("32 KB", value=32768),
        questionary.Choice("64 KB (padrão)", value=65536, checked=True),
        questionary.Choice("128 KB", value=131072),
        questionary.Choice("256 KB", value=262144),
    ],
).ask()

args.buffer = buffer_escolhido or 65536

# Aviso para arquivos grandes
if max(args.tamanho) > 1024:
    confirm = questionary.confirm(
        "⚠️ Tamanhos grandes detectados (>1GB). Continuar?"
    ).ask()
    if not confirm:
        print("[yellow]🚫 Teste cancelado pelo usuário.[/yellow]")
        exit(0)

resultados = []
upload_speeds = []
download_speeds = []

plt.ion()
fig = plt.figure(figsize=(10, 6))

# ============ Loop Principal ============

for tamanho_mb in args.tamanho:
    try:
        print(
            f"\n[bold magenta]🚀 Testando arquivo de {tamanho_mb} MB...[/bold magenta]"
        )
        nome_arquivo = f"arquivo_teste_{tamanho_mb}mb.bin"
        nome_arquivo_download = f"download_{nome_arquivo}"

        criar_arquivo(nome_arquivo, tamanho_mb)

        ftp = FTP(endereco_ftp, timeout=10)
        ftp.login(usuario, senha)
        ftp.cwd(diretorio_remoto)

        upload_info = download_info = None

        if "Upload" in acoes:
            upload_info = upload_arquivo(ftp, nome_arquivo, args.buffer)

        if "Download" in acoes:
            if upload_info is None:
                try:
                    ftp.size(nome_arquivo)
                except Exception as e:
                    print(f"[red]❌ Erro: {e}[/red]")
                    resultados.append(f"Arquivo: {nome_arquivo} ({tamanho_mb} MB)")
                    resultados.append(
                        "  ❌ Download não realizado: arquivo não encontrado no FTP."
                    )
                    resultados.append("")
                    download_speeds.append(0)
                    ftp.quit()
                    continue
            download_info = download_arquivo(
                ftp, nome_arquivo, nome_arquivo_download, args.buffer
            )

        integridade_ok = None
        if upload_info and download_info:
            integridade_ok = os.path.getsize(nome_arquivo) == os.path.getsize(
                nome_arquivo_download
            )

        resultados.append(f"Arquivo: {nome_arquivo} ({tamanho_mb} MB)")
        if upload_info:
            resultados.append(
                f"  Upload: {upload_info[0]} ➔ {upload_info[1]:.2f} Mbps / {upload_info[2]:.2f} MB/s"
            )
            upload_speeds.append(upload_info[1])
        else:
            upload_speeds.append(0)

        if download_info:
            resultados.append(
                f"  Download: {download_info[0]} ➔ {download_info[1]:.2f} Mbps / {download_info[2]:.2f} MB/s"
            )
            download_speeds.append(download_info[1])
        else:
            download_speeds.append(0)

        if integridade_ok is not None:
            resultados.append(f"  Integridade: {'OK' if integridade_ok else 'FALHA'}")
        resultados.append("")

        ftp.quit()
        live_plot(args.tamanho[: len(upload_speeds)], upload_speeds, download_speeds)

    except Exception as e:
        logging.error(f"Erro ao processar {tamanho_mb} MB: {e}")
        print(f"[red]❌ Erro ao testar arquivo de {tamanho_mb} MB: {e}[/red]")

# ============ Finalizando ============
fim_teste = datetime.now()

salvar_relatorio_txt(
    nome_teste, resultados, inicio_teste, fim_teste, upload_speeds, download_speeds
)
salvar_relatorio_markdown(
    nome_teste, resultados, inicio_teste, fim_teste, upload_speeds, download_speeds
)
salvar_relatorio_csv(
    nome_teste, resultados, inicio_teste, fim_teste, upload_speeds, download_speeds
)

plt.ioff()
plt.savefig("grafico_resultados.png")
plt.show()

print("\n[bold green]✅ Testes finalizados com sucesso![/bold green]\n")

# ============ Limpeza Automática ============
try:
    ftp = FTP(endereco_ftp)
    ftp.login(usuario, senha)
    ftp.cwd(diretorio_remoto)

    for tamanho_mb in args.tamanho:
        nome_arquivo = f"arquivo_teste_{tamanho_mb}mb.bin"
        nome_arquivo_download = f"download_{nome_arquivo}"

        apagar_arquivo_local(nome_arquivo)
        apagar_arquivo_local(nome_arquivo_download)
        apagar_arquivo_ftp(ftp, nome_arquivo)

    ftp.quit()
    print("[bold green]\n🧹 Limpeza automática concluída![/bold green]")
except Exception as e:
    logging.warning(f"Erro durante a limpeza: {e}")
    print(f"[yellow]⚠ Erro durante a limpeza: {e}[/yellow]")
    try:
        ftp.quit()
    except:
        pass

print("[bold cyan]\n📂 Relatórios salvos na pasta 'relatorios/'\n[/bold cyan]")
