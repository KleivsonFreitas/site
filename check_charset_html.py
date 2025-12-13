"""
Verificador de Charset UTF-8 em arquivos HTML

- Procura <meta charset="UTF-8"> no <head>
- Valida posição correta
- Verifica arquivos HTML salvos fora de UTF-8

Execução:
    python check_charset_html.py
"""

from pathlib import Path
import re

# Regex para charset
REGEX_CHARSET = re.compile(r'<meta\s+charset=["\']?utf-8["\']?', re.IGNORECASE)

# Regex para HEAD
REGEX_HEAD = re.compile(r'<head.*?>.*?</head>', re.IGNORECASE | re.DOTALL)


def arquivo_em_utf8(caminho: Path) -> bool:
    try:
        caminho.read_text(encoding='utf-8')
        return True
    except UnicodeDecodeError:
        return False


def verificar_html(caminho: Path):
    problemas = []

    try:
        conteudo = caminho.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        problemas.append('Não foi possível ler o arquivo')
        return problemas

    # Verifica charset
    if not REGEX_CHARSET.search(conteudo):
        problemas.append('Falta <meta charset="UTF-8">')

    # Verifica se está dentro do <head>
    head_match = REGEX_HEAD.search(conteudo)
    if head_match:
        head = head_match.group()
        if not REGEX_CHARSET.search(head):
            problemas.append('Charset não está dentro do <head>')
    else:
        problemas.append('Tag <head> não encontrada')

    # Verifica encoding real do arquivo
    if not arquivo_em_utf8(caminho):
        problemas.append('Arquivo não está salvo em UTF-8')

    return problemas


def main():
    print('=' * 60)
    print('🔎 VERIFICAÇÃO DE CHARSET UTF-8 EM HTML')
    print('=' * 60)

    templates = Path('templates')
    if not templates.exists():
        print('❌ Diretório templates não encontrado')
        return

    arquivos = list(templates.rglob('*.html'))
    if not arquivos:
        print('ℹ️ Nenhum arquivo HTML encontrado')
        return

    total_problemas = 0

    for arquivo in arquivos:
        problemas = verificar_html(arquivo)
        if problemas:
            total_problemas += len(problemas)
            print(f'❌ {arquivo}')
            for p in problemas:
                print(f'   └─ {p}')
        else:
            print(f'✅ {arquivo}')

    print('=' * 60)
    if total_problemas == 0:
        print('🎉 Todos os arquivos HTML estão corretos (UTF-8)')
    else:
        print(f'⚠️ Total de problemas encontrados: {total_problemas}')
    print('=' * 60)


if __name__ == '__main__':
    main()
