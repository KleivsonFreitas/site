"""
Corretor Automático de Encoding UTF-8
Sistema de Gestão Financeira - Simplifica Finanças

Corrige problemas comuns de mojibake (UTF-8 lido como Latin-1/CP1252)
Execução: python fix_encoding.py
"""

import os
from pathlib import Path
from datetime import datetime

# ==========================
# Mapa de correções (SEM chaves duplicadas e SEM strings quebradas)
# ==========================
CORRECOES = {
    # Letras minúsculas
    'ç': 'ç', 'ã': 'ã', 'á': 'á', 'é': 'é', 'í': 'í', 'ó': 'ó', 'ú': 'ú',
    'â': 'â', 'ê': 'ê', 'ô': 'ô', 'à': 'à',

    # Letras maiúsculas
    'Ç': 'Ç', 'Ã': 'Ã', 'Á': 'Á', 'É': 'É', 'Í': 'Í', 'Ó': 'Ó', 'Ú': 'Ú',
    '': '', 'Ê': 'Ê', 'Ô': 'Ô',

    # Aspas e pontuação
    '"': '"', '"': '"', ''': "'", ''': "'",
    '—': '—', '–': '–',

    # Símbolos invisíveis / inválidos
    '': '', '': '',
}

# ==========================
# Emojis (tratados de forma segura)
# ==========================
EMOJIS = {
    '💰': '💰', '💵': '💵', '💸': '💸', '💳': '💳',
    '📊': '📊', '📈': '📈', '📉': '📉', '🔒': '🔒',
    '🎯': '🎯', '🚀': '🚀', '✅': '✅', '❌': '❌', '⚠️': '⚠️',
    '🔧': '🔧', '📝': '📝', '📅': '📅', '📋': '📋',
    '🏠': '🏠', '🚗': '🚗', '🍽️': '🍽️', '💊': '💊',
    '📚': '📚', '🎮': '🎮', '👔': '👔', '📦': '📦',
    '💼': '💼', '🛒': '🛒', '✈️': '✈️', '📱': '📱',
    '🖥️': '🖥️', '💡': '💡', '🎉': '🎉', '🏆': '🏆',
    '📌': '📌', '🎁': '🎁',
}

class EncodingFixer:
    def __init__(self):
        self.arquivos_corrigidos = []
        self.arquivos_com_erro = []
        self.total_substituicoes = 0

    def corrigir_texto(self, texto: str):
        substituicoes = 0
        for errado, correto in {**CORRECOES, **EMOJIS}.items():
            if errado in texto:
                qtd = texto.count(errado)
                texto = texto.replace(errado, correto)
                substituicoes += qtd
        self.total_substituicoes += substituicoes
        return texto, substituicoes

    def ler_arquivo(self, caminho: str):
        for encoding in ('utf-8', 'cp1252', 'latin-1', 'iso-8859-1'):
            try:
                with open(caminho, 'r', encoding=encoding) as f:
                    return f.read(), encoding
            except UnicodeDecodeError:
                continue
        return None, None

    def corrigir_arquivo(self, caminho: str):
        try:
            conteudo, encoding = self.ler_arquivo(caminho)
            if conteudo is None:
                self.arquivos_com_erro.append(caminho)
                return False

            corrigido, subs = self.corrigir_texto(conteudo)
            if subs == 0:
                return True

            # Backup
            backup = caminho + '.backup'
            if not os.path.exists(backup):
                with open(backup, 'w', encoding='utf-8') as f:
                    f.write(conteudo)

            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(corrigido)

            self.arquivos_corrigidos.append({
                'path': caminho,
                'subs': subs,
                'encoding_original': encoding
            })
            return True

        except Exception:
            self.arquivos_com_erro.append(caminho)
            return False

    def corrigir_diretorio(self, diretorio: str, extensoes=None):
        extensoes = extensoes or ('.html', '.py', '.txt', '.md')
        arquivos = []
        for ext in extensoes:
            arquivos.extend(Path(diretorio).rglob(f'*{ext}'))

        print(f"📁 {len(arquivos)} arquivos encontrados em {diretorio}")
        for arq in arquivos:
            ok = self.corrigir_arquivo(str(arq))
            print(f" {'✅' if ok else '❌'} {arq}")

    def gerar_relatorio(self):
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE CORREÇÕES")
        print("=" * 60)
        print(f"⏰ {datetime.now():%d/%m/%Y %H:%M:%S}\n")

        if self.arquivos_corrigidos:
            print(f"✅ {len(self.arquivos_corrigidos)} arquivo(s) corrigido(s):")
            for info in self.arquivos_corrigidos:
                print(f"  • {Path(info['path']).name} | {info['subs']} substituições | {info['encoding_original']}")
        else:
            print("ℹ️ Nenhuma correção necessária.")

        if self.arquivos_com_erro:
            print("\n❌ Arquivos com erro:")
            for a in self.arquivos_com_erro:
                print(f"  • {a}")

        print(f"\n📈 Total de substituições: {self.total_substituicoes}")
        print("=" * 60)


def main():
    print("=" * 60)
    print("🔧 CORRETOR AUTOMÁTICO DE ENCODING UTF-8")
    print("=" * 60)

    diretorios = []
    if Path('templates').exists():
        diretorios.append('templates')
    if Path('app.py').exists():
        diretorios.append('.')

    if not diretorios:
        print("❌ Execute o script na raiz do projeto")
        return

    print(f"📂 Diretórios: {', '.join(diretorios)}")
    if input("Deseja prosseguir? (s/n): ").lower() != 's':
        print("Operação cancelada.")
        return

    fixer = EncodingFixer()
    for d in diretorios:
        fixer.corrigir_diretorio(d)

    fixer.gerar_relatorio()
    print("🎉 Concluído! Teste a aplicação e depois remova os .backup")


if __name__ == '__main__':
    main()
