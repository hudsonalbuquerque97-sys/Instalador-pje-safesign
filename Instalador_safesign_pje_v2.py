#!/usr/bin/env python3
# ================================================================
#  Script: Instala SafeSign (Token), cria atalhos do PJe
#  e adiciona atalho do TokenAdmin na Área de Trabalho do usuário real
# ================================================================
#  Uso: sudo python3 instala_safesign_pje_com_tokenadmin.py
#  criado por Hudson Albuquerque (hud.and@yandex.com)
# ================================================================

import os
import sys
import subprocess
import pwd
import grp
from pathlib import Path
import shutil

def executar_comando(cmd, shell=False, check=True):
    """Executa comando e retorna resultado"""
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, check=check, 
                                  capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar: {cmd}")
        print(f"Saída: {e.stderr}")
        raise

def verificar_root():
    """Verifica se está rodando como root"""
    if os.geteuid() != 0:
        print("Este script precisa ser executado como root (sudo)")
        sys.exit(1)

def obter_usuario_real():
    """Obtém o usuário real (não root)"""
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        return sudo_user
    return os.environ.get('USER', 'root')

def obter_home_usuario(username):
    """Obtém o diretório home do usuário"""
    try:
        return pwd.getpwnam(username).pw_dir
    except KeyError:
        print(f"Usuário {username} não encontrado")
        sys.exit(1)

def mostrar_dialogo_confirmacao():
    """Mostra diálogo de confirmação usando whiptail"""
    msg = """
Este script irá instalar:

  • SafeSign / TokenAdmin
  • Dependências de smartcard
  • PJe Office Pro
  • Atalhos na Área de Trabalho e Menu

Deseja prosseguir?
"""
    try:
        subprocess.run([
            'whiptail', '--title', 'Instalador SafeSign + PJe',
            '--yesno', msg, '20', '70'
        ], check=True)
        return True
    except subprocess.CalledProcessError:
        print("Instalação cancelada.")
        return False

def criar_grupo_se_necessario(grupo):
    """Cria grupo se não existir"""
    print(f"==> Criando grupo {grupo} (se não existir)...")
    try:
        grp.getgrnam(grupo)
        print(f"Grupo {grupo} já existe.")
    except KeyError:
        executar_comando(['addgroup', grupo])

def adicionar_usuario_ao_grupo(usuario, grupo):
    """Adiciona usuário ao grupo"""
    print(f"==> Adicionando usuário {usuario} ao grupo {grupo}...")
    executar_comando(['adduser', usuario, grupo])

def instalar_dependencias_gerais():
    """Instala dependências gerais do sistema"""
    print("==> Instalando dependências gerais...")
    executar_comando(['apt', 'update'])
    
    pacotes = [
        'libengine-pkcs11-openssl', 'libp11-3', 'libpcsc-perl', 
        'libccid', 'pcsc-tools', 'libasedrive-usb', 'opensc', 
        'openssl', 'pcscd', 'libc6', 'libgcc-s1', 'libgdbm-compat4',
        'libglib2.0-0', 'libpcsclite1', 'libssl3', 'libstdc++6'
    ]
    
    executar_comando(['apt', 'install', '-y'] + pacotes)

def baixar_pacotes_antigos():
    """Baixa e instala pacotes antigos necessários"""
    print("==> Baixando pacotes antigos...")
    temp_dir = Path('/tmp/token_debs')
    temp_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(temp_dir)
    
    urls = [
        'http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1-1ubuntu2.1~18.04.23_amd64.deb',
        'http://archive.ubuntu.com/ubuntu/pool/universe/w/wxwidgets3.0/libwxbase3.0-0v5_3.0.5.1+dfsg-4_amd64.deb',
        'http://archive.ubuntu.com/ubuntu/pool/main/g/gdk-pixbuf-xlib/libgdk-pixbuf-xlib-2.0-0_2.40.2-2build4_amd64.deb',
        'http://archive.ubuntu.com/ubuntu/pool/universe/g/gdk-pixbuf-xlib/libgdk-pixbuf2.0-0_2.40.2-2build4_amd64.deb',
        'http://archive.ubuntu.com/ubuntu/pool/main/t/tiff/libtiff5_4.3.0-6_amd64.deb',
        'http://archive.ubuntu.com/ubuntu/pool/universe/w/wxwidgets3.0/libwxgtk3.0-gtk3-0v5_3.0.5.1+dfsg-4_amd64.deb'
    ]
    
    for url in urls:
        executar_comando(['wget', '-c', url])
    
    print("==> Instalando pacotes antigos...")
    executar_comando('dpkg -i *.deb || apt -f install -y', shell=True, check=False)
    executar_comando(['apt', '-f', 'install', '-y'])

def instalar_safesign():
    """Baixa e instala o SafeSign"""
    print("==> Baixando e instalando SafeSign...")
    os.chdir('/tmp')
    
    url = 'https://safesign.gdamericadosul.com.br/content/SafeSign_IC_Standard_Linux_ub2204_3.8.0.0_AET.000.zip'
    executar_comando(['wget', '-c', url, '-O', 'safesign.zip'])
    executar_comando(['unzip', '-o', 'safesign.zip', '-d', 'safesign_pkg'])
    
    os.chdir('safesign_pkg')
    debs = list(Path('.').glob('*.deb'))
    
    if debs:
        safe_deb = debs[0]
        executar_comando(['dpkg', '-i', str(safe_deb)], check=False)
    else:
        print("!! Nenhum .deb encontrado no zip")
    
    executar_comando(['apt', '-f', 'install', '-y'])

def habilitar_servico_pcscd():
    """Habilita e inicia o serviço pcscd"""
    print("==> Habilitando serviço pcscd...")
    executar_comando(['systemctl', 'enable', 'pcscd'])
    executar_comando(['systemctl', 'start', 'pcscd'])

def executar_como_usuario(usuario, comando):
    """Executa comando como usuário específico"""
    cmd = ['sudo', '-u', usuario] + comando
    return executar_comando(cmd)

def instalar_pje_office(usuario, home_usuario):
    """Instala o PJe Office Pro"""
    print("==> Instalando PJe Office Pro...")
    
    pje_url = 'https://pje-office.pje.jus.br/pro/pjeoffice-pro-v2.5.16u-linux_x64.zip'
    dest_dir = Path(home_usuario) / '.local/share/pjeoffice-pro'
    
    # Criar diretório
    executar_como_usuario(usuario, ['mkdir', '-p', str(dest_dir)])
    
    # Baixar PJe
    print("==> Baixando PJe Office Pro...")
    executar_comando(['wget', '-c', pje_url, '-O', '/tmp/pjeoffice-pro.zip'])
    
    # Extrair
    executar_como_usuario(usuario, [
        'unzip', '-o', '/tmp/pjeoffice-pro.zip', '-d', str(dest_dir)
    ])
    
    # Encontrar e dar permissão ao script
    pje_sh = None
    for arquivo in dest_dir.rglob('pjeoffice-pro.sh'):
        pje_sh = arquivo
        break
    
    if pje_sh:
        os.chmod(pje_sh, 0o755)
    else:
        print("Aviso: pjeoffice-pro.sh não encontrado")
        pje_sh = dest_dir / 'pjeoffice-pro.sh'
    
    # Baixar ícone
    icon_url = 'https://raw.githubusercontent.com/hudsonalbuquerque97-sys/Instalador-pje-safesign/refs/heads/main/pjeoffice-pro-black.png'
    icon_file = dest_dir / 'pje-office.png'
    executar_como_usuario(usuario, ['wget', '-c', icon_url, '-O', str(icon_file)])
    
    return pje_sh, icon_file

def criar_atalho_pje(usuario, home_usuario, pje_sh, icon_file):
    """Cria atalhos do PJe Office"""
    print("==> Criando atalhos do PJe Office...")
    
    # Obter diretório Desktop
    try:
        result = executar_como_usuario(usuario, ['xdg-user-dir', 'DESKTOP'])
        desktop_dir = Path(result.stdout.strip())
    except:
        desktop_dir = Path(home_usuario) / 'Desktop'
    
    executar_como_usuario(usuario, ['mkdir', '-p', str(desktop_dir)])
    
    desktop_file = desktop_dir / 'pjeoffice-pro.desktop'
    
    conteudo = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=PJe Office Pro
Comment=Carregador de Certificados
Exec={pje_sh}
Icon={icon_file}
Categories=Office;
StartupNotify=false
Terminal=false
"""
    
    # Escrever arquivo
    with open(desktop_file, 'w') as f:
        f.write(conteudo)
    
    # Ajustar permissões
    uid = pwd.getpwnam(usuario).pw_uid
    gid = pwd.getpwnam(usuario).pw_gid
    os.chown(desktop_file, uid, gid)
    os.chmod(desktop_file, 0o755)
    
    # Copiar para menu
    menu_dir = Path(home_usuario) / '.local/share/applications'
    executar_como_usuario(usuario, ['mkdir', '-p', str(menu_dir)])
    shutil.copy(desktop_file, menu_dir / 'pjeoffice-pro.desktop')
    
    # Atualizar banco de dados
    if shutil.which('update-desktop-database'):
        executar_comando(['update-desktop-database', str(menu_dir)], check=False)
    
    return desktop_dir

def criar_atalho_tokenadmin(usuario, desktop_dir):
    """Cria atalho do TokenAdmin com ícone personalizado"""
    print("==> Baixando ícone personalizado do TokenAdmin...")
    
    # *** SUBSTITUA O LINK ABAIXO PELO SEU LINK DO GITHUB ***
    icon_url = 'https://raw.githubusercontent.com/hudsonalbuquerque97-sys/Instalador-pje-safesign/refs/heads/main/tokenadmin-black.png'
    
    # Baixar ícone para temporário
    temp_icon = '/tmp/token2.png'
    executar_comando(['wget', '-c', icon_url, '-O', temp_icon])
    
    # Copiar ícone para as pastas padrão do sistema
    print("==> Copiando ícone para as pastas do sistema...")
    icon_dirs = [
        '/usr/share/icons/hicolor/48x48/apps',
        '/usr/share/icons/hicolor/64x64/apps',
        '/usr/share/icons/hicolor/128x128/apps',
        '/usr/share/icons/hicolor/256x256/apps',
        '/usr/share/pixmaps'
    ]
    
    for icon_dir in icon_dirs:
        try:
            # Criar diretório se não existir
            Path(icon_dir).mkdir(parents=True, exist_ok=True)
            # Copiar ícone
            dest_icon = Path(icon_dir) / 'token2.png'
            shutil.copy(temp_icon, dest_icon)
            os.chmod(dest_icon, 0o644)
            print(f"   Ícone copiado para: {dest_icon}")
        except Exception as e:
            print(f"   Aviso: Não foi possível copiar para {icon_dir}: {e}")
    
    # Atualizar cache de ícones
    print("==> Atualizando cache de ícones...")
    if shutil.which('gtk-update-icon-cache'):
        executar_comando(['gtk-update-icon-cache', '/usr/share/icons/hicolor'], check=False)
    
    print("==> Criando atalho do TokenAdmin...")
    
    token_desktop = desktop_dir / 'TokenAdmin.desktop'
    
    # Usar o ícone personalizado
    conteudo = """[Desktop Entry]
Version=1.0
Name=TokenAdmin
Comment=Gerenciador SafeSign
Exec=tokenadmin
Icon=token2
Terminal=false
Type=Application
Categories=Utility;System;
"""
    
    with open(token_desktop, 'w') as f:
        f.write(conteudo)
    
    # Ajustar permissões
    uid = pwd.getpwnam(usuario).pw_uid
    gid = pwd.getpwnam(usuario).pw_gid
    os.chown(token_desktop, uid, gid)
    os.chmod(token_desktop, 0o755)
    
    # Também criar no menu de aplicativos
    menu_dir = Path(pwd.getpwnam(usuario).pw_dir) / '.local/share/applications'
    executar_como_usuario(usuario, ['mkdir', '-p', str(menu_dir)])
    menu_desktop = menu_dir / 'TokenAdmin.desktop'
    shutil.copy(token_desktop, menu_desktop)
    os.chown(menu_desktop, uid, gid)
    os.chmod(menu_desktop, 0o755)
    
    # Limpar ícone temporário
    if os.path.exists(temp_icon):
        os.remove(temp_icon)
    
    print("   Atalho do TokenAdmin criado com sucesso!")

def limpar_temporarios():
    """Remove arquivos temporários"""
    print("==> Limpando arquivos temporários...")
    diretorios = [
        '/tmp/token_debs',
        '/tmp/safesign_pkg',
    ]
    arquivos = [
        '/tmp/safesign.zip',
        '/tmp/pjeoffice-pro.zip'
    ]
    
    for diretorio in diretorios:
        if os.path.exists(diretorio):
            shutil.rmtree(diretorio)
    
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            os.remove(arquivo)

def main():
    """Função principal"""
    verificar_root()
    
    if not mostrar_dialogo_confirmacao():
        sys.exit(0)
    
    print("Prosseguindo com a instalação...")
    
    # Obter informações do usuário
    usuario = obter_usuario_real()
    home_usuario = obter_home_usuario(usuario)
    
    print(f"Executando como root, mas instalando atalhos para: {usuario} ({home_usuario})")
    print()
    
    # ---- BLOCO 1: Instalação do SafeSign ----
    grupo = "scard"
    criar_grupo_se_necessario(grupo)
    adicionar_usuario_ao_grupo(usuario, grupo)
    instalar_dependencias_gerais()
    baixar_pacotes_antigos()
    instalar_safesign()
    habilitar_servico_pcscd()
    
    print("==== Instalação do SafeSign concluída ====")
    input("Pressione Enter para instalar o PJe e criar atalhos...")
    
    # ---- BLOCO 2: PJe Office Pro ----
    pje_sh, icon_file = instalar_pje_office(usuario, home_usuario)
    
    print(f"==== PJe instalado para {usuario} ====")
    input("Pressione Enter para criar o atalho do TokenAdmin...")
    
    # ---- BLOCO 3: Atalho TokenAdmin ----
    desktop_dir = criar_atalho_pje(usuario, home_usuario, pje_sh, icon_file)
    criar_atalho_tokenadmin(usuario, desktop_dir)
    
    # Limpar arquivos temporários
    limpar_temporarios()
    
    print("==== Instalação concluída ====")
    print(f"- PJe Office Pro e TokenAdmin disponíveis em {home_usuario}/Desktop e no menu de aplicativos.")
    print(f"- Faça logout/login para ativar o grupo {grupo}.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstalação interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nErro durante a instalação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
