# main.py
# SISTEMA DE GESTÃO COLABORATIVA - PIM II
# Versão Sem Classes - Todos os relatórios em Python

import json                                     # armazenamento das informações pós finalizar sistema
import os                                       # limpar terminal/verifica existencia de json
import datetime                                 # manter registros em tempo real
import random                                   # redefinir senha quando selecionar a opção "recupera senha"
import string                                   # auxilia na complexidade da senha aleatoria, e outros fatores
import subprocess

# =============================================
# VARIÁVEIS GLOBAIS DO SISTEMA
# =============================================

usuarios = []          # Todos os usuários do sistema
produtos = []          # Produtos em estoque
solicitacoes = []      # Solicitações de produtos (saídas)
movimentacoes = []     # Histórico de entradas/saídas APROVADAS
pendencias = []        # Movimentações pendentes de aprovação

usuario_logado = None  # Usuário atualmente logado

# =============================================
# FUNÇÕES DE INICIALIZAÇÃO E PERSISTÊNCIA
# =============================================

def inicializar_dados():
    """INICIALIZA DADOS DO SISTEMA"""
    global usuarios, produtos, solicitacoes, movimentacoes, pendencias  #atribui a variaveis globais
    
    dados_iniciais = {                          #dados inicias ao rodar pela primeira vez
        'usuarios.json': [
            {
                'id': 1,
                'nome': 'Administrador',
                'email': 'admin@sistema.com',
                'senha': '123456',
                'perfil': 'Administrador',
                'cpf': '12345678901',
                'telefone': '(11) 99999-0001',
                'data_cadastro': '01/01/2024 00:00'
            }
        ],
        'produtos.json': [],
        'solicitacoes.json': [],
        'movimentacoes.json': [],
        'pendencias.json': []
    }
    
    for arquivo, dados in dados_iniciais.items():     #para cada chave,valor nos itens do dicionario "dados_iniciais"
        if not os.path.exists(arquivo):                 #se json com nome chave não existir
            with open(arquivo, 'w', encoding='utf-8') as f:     #cria json sendo chave o nome 
                json.dump(dados, f, indent=2, ensure_ascii=False)      #adiciona dados inicias ao json criado
            print(f"📁 Arquivo {arquivo} criado com dados iniciais")    #informa no terminal
        else:                                                   #senão = ja existem json's
            print(f"📁 Arquivo {arquivo} já existe - mantendo dados")   #informa no terminal

def carregar_dados():
    """CARREGA DADOS DOS ARQUIVOS JSON"""
    global usuarios, produtos, solicitacoes, movimentacoes, pendencias
    
    arquivos = ['usuarios.json', 'produtos.json', 'solicitacoes.json', 'movimentacoes.json', 'pendencias.json']
#                                             lista dos arquivos json 👆👆👆
    for arquivo in arquivos:    #para cada arquivo
        if os.path.exists(arquivo):     #se arquivo existir
            with open(arquivo, 'r', encoding='utf-8') as f: #abrir arquivo como leitura
                if arquivo == 'usuarios.json':          #se arquivo = tal json
                    usuarios = json.load(f)             #carrega json para lista tal para utilizar no sistema
                elif arquivo == 'produtos.json':           #mesma logica nos "elif's"
                    produtos = json.load(f)
                elif arquivo == 'solicitacoes.json':
                    solicitacoes = json.load(f)
                elif arquivo == 'movimentacoes.json':
                    movimentacoes = json.load(f)
                elif arquivo == 'pendencias.json':
                    pendencias = json.load(f)

def salvar_dados():
    """SALVA DADOS NOS ARQUIVOS JSON"""
    arquivos = {                #dicionario = lista nome json:nome listas correspodentes
        'usuarios.json': usuarios,
        'produtos.json': produtos,
        'solicitacoes.json': solicitacoes,
        'movimentacoes.json': movimentacoes,
        'pendencias.json': pendencias
    }
    
    for arquivo, dados_salvar in arquivos.items():  #para cada chave e valor
        with open(arquivo, 'w', encoding='utf-8') as f: #abre json da chave atual
            json.dump(dados_salvar, f, indent=2, ensure_ascii=False)    #salva lista de dicionarios atual no json atual

# =============================================
# FUNÇÕES DE INTERFACE DO USUÁRIO
# =============================================

def limpar_tela():
    """LIMPA A TELA DO TERMINAL"""
    os.system('cls' if os.name == 'nt' else 'clear')    #limpa tela de windows e outros O.S

def exibir_cabecalho(titulo: str):
    """EXIBE CABEÇALHO FORMATADO"""
    limpar_tela()
    print("=" * 60)                 #Exibe cabeçalho padronizado
    print(f"🏢 S.O.S GERENCIMENTO DE ESTOQUE - {titulo}")  
    print("=" * 60)
    print()

def pausar():
    """PAUSA A EXECUÇÃO"""
    input("\n📝 Pressione ENTER para continuar...")  #pausa execução para leitura

# =============================================
# FUNÇÕES DE AUTENTICAÇÃO
# =============================================

def autenticar_usuario(email: str, senha: str): #verifica se usuário existe no sistema
    """AUTENTICA USUÁRIO NO SISTEMA"""
    for usuario in usuarios: #para cada usuario na lista
        if usuario['email'] == email and usuario['senha'] == senha: # se email e senha correspondem a lista
            return usuario  #retorna usuário
    return None # se não encontrar, não retorna valor

def login():
    """REALIZA O LOGIN DO USUÁRIO"""
    global usuario_logado
    
    while True:
        exibir_cabecalho("LOGIN")
        print("🔐 Faça login no sistema")
        print("-" * 40)
        
        email = input("📧 E-mail: ").strip()    #pede credencias ao usuário
        senha = input("🔒 Senha: ").strip()
        
        usuario = autenticar_usuario(email, senha)  #verifica se usuario existe
        
        if usuario: #se existir
            usuario_logado = usuario    #registra que está logado
            print(f"\n✅ Login realizado com sucesso!")
            print(f"👋 Bem-vindo(a), {usuario['nome']}!")
            pausar()
            return True #retorna a função
        else:
            print("\n❌ E-mail ou senha incorretos!")
            opcao = input("\nDeseja tentar novamente? (s/n): ").lower() 
            if opcao == 'n':
                return False #retorna a função

def limpar_telefone(telefone):
    """LIMPA FORMATAÇÃO DO TELEFONE"""
    if not telefone:
        return ""
    return ''.join(filter(str.isdigit, telefone)) #filtra apenas caracteres digitos

def formatando_cpf(cpf: str) -> str:
    """FORMATA CPF PARA PADRÃO BRASILEIRO"""
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    if len(cpf_limpo) != 11:
        return cpf
    
    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

def gerar_senha_temporaria(tamanho = 8):
    """GERA SENHA TEMPORÁRIA ALEATÓRIA"""
    caracteres = string.ascii_letters + string.digits   #caracteres disponiveis pra se utilizar na senha
    caracteres = caracteres.replace('0', '').replace('O', '').replace('1', '').replace('l', '').replace('I', '')
#                                   Evita utilizar caracteres semelhantes 👆👆
    senha = [   #lista de caracteres da senha
        random.choice(string.ascii_uppercase),  # Garante que a senha tenha pelo menos: 1 maiúscula;
        random.choice(string.ascii_lowercase),  #1 minúscula;
        random.choice(string.digits)            #1 número.
    ]
    
    senha.extend(random.choice(caracteres) for _ in range(tamanho - 3)) #completa senha com caracteres aleatorios
    random.shuffle(senha)   #embaralha a senha
    
    return ''.join(senha)   #coverte lista para string

def recuperar_senha():
    """RECUPERAÇÃO DE SENHA - Versão Unificada"""
    exibir_cabecalho("RECUPERAÇÃO DE SENHA")
    
    print("🔐 Recuperação de Senha - Verificação de Identidade")
    print("📋 Por favor, informe os dados abaixo para verificação:")
    print("-" * 50)
    
    email = input("📧 E-mail cadastrado: ").strip().lower()
    cpf = input("📄 CPF (apenas números): ").strip()
    telefone = input("📞 Telefone com DDD: ").strip()
    nome_completo = input("👤 Nome completo: ").strip().title()
    
    usuario = next((u for u in usuarios if u['email'].lower() == email), None)#encontra usuario com email
    
    if not usuario: #verifica se usuario não existe no sistema
        print(f"\n❌ E-mail não encontrado no sistema.")
        pausar()
        return

    # Verificação de identidade
    verificacao_ok = True
    mensagens_erro = []
    
    if usuario['nome'].title() != nome_completo: #checa nomes
        verificacao_ok = False
        mensagens_erro.append("❌ Nome completo não confere")
    
    cpf_input = formatando_cpf(cpf) #limpa cpf da entrada atual
    
    if usuario.get('cpf', '')  != cpf_input:    #checa cpf
        verificacao_ok = False
        mensagens_erro.append("❌ CPF não confere")
    
    telefone_limpo = limpar_telefone(telefone)  #limpa telefone da entrada atual
    
    if usuario.get('telefone', '') != telefone_limpo:
        verificacao_ok = False
        mensagens_erro.append("❌ Telefone não confere")
    
    if verificacao_ok:  #se informações corretas
        senha_temporaria = gerar_senha_temporaria()     #gera nova senha
        usuario_original = next((u for u in usuarios if u['id'] == usuario['id']), None) 
        # encontra usuario pelo id ou retorna "None" se não encontar 👆👆

        if usuario_original:        #se encontarr ussuario
            usuario_original['senha'] = senha_temporaria  #reseta senha
            salvar_dados()      #salva alteração

            
            print(f"\n✅ Identidade verificada com sucesso!")
            print(f"🔑 Sua senha temporária: {senha_temporaria}")
            print(f"\n📝 Instruções:")
            print("   1. Faça login com esta senha temporária")
            print("   2. Vá em 'Meu Perfil' para redefinir sua senha")
            print("   3. Escolha uma senha segura e fácil de lembrar")
            print(f"\n⚠️  Esta senha é válida por 24 horas")
            
        else:
            print(f"\n❌ Erro interno ao atualizar senha.")
    
    else:       #se infrmação não forem coincidentes com armazenadas
        print(f"\n❌ Falha na verificação de identidade.")
        print("   Erros encontrados:")
        for erro in mensagens_erro: #informa erros 
            print(f"   - {erro}")
        print(f"\nVerifique os dados informados e tente novamente.")
    
    pausar()

def alterar_senha():
        """REDEFINE SENHA DO USUÁRIO LOGADO"""
        exibir_cabecalho("REDEFINIR SENHA")
        
        print("🔐 Redefinição de Senha")
        print("-" * 30)
        #   Pede senha ao usuario
        senha_atual = input("🔒 Senha atual: ").strip()
        
        #Verifica se senha está incorreta
        if senha_atual != usuario_logado['senha']:
            print("\n❌ Senha atual incorreta!")
            pausar()
            return
        
        #pede ao usuario para redefinir senha
        nova_senha = input("🆕 Nova senha: ").strip()
        confirmar_senha = input("✅ Confirmar nova senha: ").strip()
        
        #se senha não se coincidirem
        if nova_senha != confirmar_senha:
            print("\n❌ As senhas não coincidem!")
            pausar()
            return
        
        #se senha não atender requisito de tamanho
        if len(nova_senha) < 6:
            print("\n❌ A senha deve ter pelo menos 6 caracteres!")
            pausar()
            return
        
        #usuario tem sua senha alterada na variavel logado
        usuario_logado['senha'] = nova_senha
        
        #usuario tem sua senha alterada na lista em memoria
        for usuario in usuarios:
            if usuario['id'] == usuario_logado['id']:
                usuario['senha'] = nova_senha
                break
        
        salvar_dados() # salva lista em memoria para .json
        print(f"\n✅ Senha redefinida com sucesso!")
        pausar()

# =============================================
# MÓDULO DE GERENCIAMENTO DE USUÁRIOS
# =============================================

def cadastrar_usuario():
    """CADASTRAR NOVO USUÁRIO - Para administradores"""
    exibir_cabecalho("CADASTRAR NOVO USUÁRIO")
    
    print("📝 Preencha os dados do usuário:")
    print("-" * 40)
    
    # Coleta dados básicos
    nome = input("👤 Nome completo: ").strip().title()
    email = input("📧 E-mail: ").strip().lower()
    cpf = input("📄 CPF (apenas números): ").strip()
    telefone = input("📞 Telefone com DDD: ").strip()
    
    #verifica entrada entradas vazias
    for info in [nome, email, cpf, telefone]:
        if  not info:
            print("❌ Por favor, preencha todos os campos!")
            return

    # Menu de seleção de perfil por número
    print("\n🎭 Selecione o perfil do usuário:")
    print("   1. 👑 Administrador")
    print("   2. 🎁 Doador") 
    print("   3. 📦 Solicitante")
    print("-" * 30)
    
    perfil_opcao = input("📋 Digite o número do perfil (1-3): ").strip()
    
    # Mapeia a opção numérica para o perfil
    perfis = {
        '1': 'Administrador',
        '2': 'Doador', 
        '3': 'Solicitante'
    }
    #define perfil escolhido ao sistema
    perfil = perfis.get(perfil_opcao)
    
    if not perfil:  #se escolha fora de 1,2,3
        print("❌ Opção de perfil inválida!")
        pausar()
        return
    
    # Cria o usuário
    usuario = {
        'id': len(usuarios) + 1,
        'nome': nome,
        'email': email,
        'senha': "123456",
        'perfil': perfil,
        'cpf': cpf,
        'telefone': telefone,
        'data_cadastro': datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    '''administrador informa pessoalmente a senha padrão de acesso ao
    novo usuario e orienta a alteração da senha'''

    usuarios.append(usuario)   #adiciona novo usuario a lista em memoria
    salvar_dados()      #atualiza dados com nova alteração
    
    print(f"\n✅ Usuário '{usuario['nome']}' cadastrado com sucesso!")
    print(f"🔑 Senha inicial: 123456")
    print(f"🎭 Perfil: {perfil}")
    pausar()

def listar_usuarios():
    """LISTA TODOS OS USUÁRIOS DO SISTEMA - Para administradores"""
    exibir_cabecalho("LISTA DE USUÁRIOS")
    
    if not usuarios:    #se nenhum Usuario cadastrado
        print("📭 Nenhum usuário cadastrado no sistema.")
        return
    
    print(f"{'ID':<4} {'NOME':<40} {'EMAIL':<32} {'PERFIL':<15} {'TELEFONE':<15}")
    print("-" * 90) #cabeçalho da tabela com alinhamento 👆👆
    
    for usuario in usuarios:    #gera lista "usuario nome email perfil telefone"
        print(f"{usuario['id']:<4} {usuario['nome'][:30]:<40} {usuario['email'][:30]:<32} "
              f"{usuario['perfil']:<15} {usuario.get('telefone', 'N/D')[:13]:<15}")

def menu_gerenciar_usuarios():
    """GERENCIAR USUÁRIOS - Apenas para administradores"""
    #Menu simples
    while True:
        exibir_cabecalho("GERENCIAR USUÁRIOS")
        
        print("1. 👤 Cadastrar Novo Usuário")
        print("2. 📋 Listar Todos os Usuários")
        print("3. 🏠 Voltar")
        
        opcao = input("\n📋 Escolha uma opção: ")
            
        if opcao == '1':
            cadastrar_usuario()
        elif opcao == '2':
            listar_usuarios()
        elif opcao == '3':
            break
        else:
            print("❌ Opção inválida!")
        pausar()

def exibir_meus_dados():
    """EXIBE DADOS DO USUÁRIO LOGADO"""
    exibir_cabecalho("MEUS DADOS")
    
    usuario = usuario_logado
    print("📋 SEUS DADOS CADASTRAIS:")
    print("-" * 40)
    print(f"👤 Nome: {usuario['nome']}")
    print(f"📧 E-mail: {usuario['email']}")
    print(f"🎭 Perfil: {usuario['perfil']}")    
    cpf_formatado = formatando_cpf(usuario['cpf'])
    print(f"📄 CPF: {cpf_formatado}")
    print(f"📞 Telefone: {usuario['telefone']}")
    print(f"📅 Data de Cadastro: {usuario['data_cadastro']}")

    decisao = input("deseja atualizar seus dados?(s/n): ").lower()

    if decisao == 's':
        atualizar_dados()
    else:
        return

def atualizar_dados():
    """ATUALIZA OS DADOS DO USUÁRIO LOGADO"""
    exibir_cabecalho("ATUALIZAR MEUS DADOS")
    
    print("📝 Atualize seus dados (deixe em branco para manter o valor atual):")
    print("-" * 50)
    
    usuario = usuario_logado
    
    # Exibe dados atuais
    print(f"📋 Dados atuais:")
    print(f"👤 Nome atual: {usuario['nome']}")
    print(f"📧 E-mail atual: {usuario['email']}")
    print(f"📞 Telefone atual: {usuario['telefone']}")
    print("-" * 50)
    
    # Coleta novos dados
    novo_nome = input(f"👤 Novo nome completo [{usuario['nome']}]: ").strip().title()
    novo_email = input(f"📧 Novo e-mail [{usuario['email']}]: ").strip().lower()
    novo_telefone = input(f"📞 Novo telefone [{usuario['telefone']}]: ").strip()
    
    # Verifica se houve alterações
    alteracoes = False
    
    # Atualiza nome se fornecido
    if novo_nome and novo_nome != usuario['nome']:
        # Verifica se o nome tem pelo menos 2 partes (nome e sobrenome)
        partes_nome = novo_nome.split()
        if len(partes_nome) < 2:
            print("❌ Por favor, digite seu nome COMPLETO")
            pausar()
            return
        
        # Verifica se cada parte do nome tem pelo menos 2 caracteres
        for parte in partes_nome:
            if len(parte) < 2:
                print("❌ Cada parte do nome deve ter pelo menos 2 caracteres!")
                pausar()
                return
        
        usuario['nome'] = novo_nome
        alteracoes = True
        print("✅ Nome atualizado!")
    
    # Atualiza e-mail se fornecido
    if novo_email and novo_email != usuario['email']:
        # Verifica se o e-mail já existe em outro usuário
        email_existente = next((u for u in usuarios if u['email'] == novo_email and u['id'] != usuario['id']), None)
        if email_existente:
            print("❌ Este e-mail já está em uso por outro usuário!")
            pausar()
            return
        
        # Verifica formato básico do e-mail
        if '@' not in novo_email or '.' not in novo_email:
            print("❌ Por favor, digite um e-mail válido!")
            pausar()
            return
            
        usuario['email'] = novo_email
        alteracoes = True
        print("✅ E-mail atualizado!")
    
    # Atualiza telefone se fornecido
    if novo_telefone and novo_telefone != usuario['telefone']:
        # Limpa o telefone
        telefone_limpo = limpar_telefone(novo_telefone)
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            print("❌ Telefone deve conter DDD (2 dígitos) + número (8 ou 9 dígitos)!")
            pausar()
            return
        
        # Formata o telefone para padrão brasileiro
        if len(telefone_limpo) == 10:
            telefone_formatado = f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
        else:
            telefone_formatado = f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
        
        usuario['telefone'] = telefone_formatado
        alteracoes = True
        print("✅ Telefone atualizado!")
    
    # Se houve alterações, salva no sistema
    if alteracoes:      
        salvar_dados()

        print(f"\n🎉 Todas as alterações foram salvas com sucesso!")
        print(f"📅 Última atualização: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    else:
        print(f"\nℹ️  Nenhuma alteração foi realizada.")
    
    pausar()

def menu_meu_perfil():
    """MENU MEU PERFIL"""
    while True:
        exibir_cabecalho("MEU PERFIL")
        print(f"👤 Usuário: {usuario_logado['nome']}")
        print(f"📧 E-mail: {usuario_logado['email']}")
        print(f"🎭 Perfil: {usuario_logado['perfil']}")
        print("-" * 40)
        
        print("1. 🔐 Redefinir Senha")
        print("2. 📋 Meus Dados")
        print("3. 🏠 Voltar ao Menu Principal")

        opcao = input("\n📋 Escolha uma opção: ")
        
        if opcao == '1':
            alterar_senha()
        elif opcao == '2':
            exibir_meus_dados()
        elif opcao == '3':
            break
        else:
            print("❌ Opção inválida!")
        pausar()

def trocar_usuario():
    """TROCA PARA OUTRO USUÁRIO SEM SAIR DO SISTEMA"""
    global usuario_logado
    
    exibir_cabecalho("TROCAR USUÁRIO")
    print("🎭 Trocar de Usuário")
    print("-" * 30)
    print("Você será redirecionado para a tela de login.")
    print("Seus dados atuais serão mantidos no sistema.")
    
    confirmar = input("\n📋 Deseja continuar? (s/n): ").lower()
    
    if confirmar == 's':
        usuario_logado = None  # Remove o usuário logado atual
        print("\n👋 Até logo! Redirecionando para login...")
        pausar()
        return True  # Indica que deve retornar ao login
    else:
        print("\n✅ Operação cancelada. Continuando no usuário atual.")
        pausar()
        return False  # Indica que deve continuar no menu atual
# =============================================
# MÓDULO PARA DOADORES
# =============================================

def registrar_doacao_pendente():
    """
    REGISTRAR DOAÇÃO PENDENTE - Para doadores
    Cria uma pendência de entrada que precisa ser aprovada
    """
    exibir_cabecalho("REGISTRAR DOAÇÃO")
    
    print(f"🎁 Registrar Nova Doação - {usuario_logado['nome']}")
    print("📝 Esta doação ficará pendente até avaliação do administrador")
    print("-" * 50)
    
    # Coleta dados do produto
    nome = input("📦 Nome do produto: ").strip()
    descricao = input("📄 Descrição (opcionnal): ").strip()
    categoria = input("🏷️  Categoria (Alimento, Medicamento etc): ").strip()
    
    try: # try corrige valores não numericos
        peso = float(input("⚖️  Peso (kg): "))
        quantidade = int(input("📊 Quantidade: "))
        data_validade = input("📅 Data de validade (DD/MM/AAAA): ").strip()
    except ValueError:
        print("❌ Por favor, digite valores numéricos válidos!")
        pausar()
        return

    #verifica entrada entradas vazias
    for info in [nome, descricao, peso, quantidade, data_validade]:
        if  not info:
            print("❌ Por favor, preencha todos os campos!")
            pausar()
            return


    # Cria pendência de entrada
    pendencia = {
        'id': len(pendencias) + 1,
        'tipo': 'ENTRADA',
        'produto_nome': nome,
        'produto_descricao': descricao,
        'produto_categoria': categoria,
        'produto_peso': peso,
        'produto_validade': data_validade,
        'quantidade': quantidade,
        'usuario_id': usuario_logado['id'],
        'usuario_nome': usuario_logado['nome'],
        'data_solicitacao': datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        'status': 'Pendente'
    }
    
    pendencias.append(pendencia)    #adiciona a lista em memoria
    salvar_dados()      #atualiza json com nova informação
    
    print(f"\n✅ Doação registrada com sucesso! (ID: {pendencia['id']})")
    print(f"📦 {quantidade} unidades de '{nome}'")
    print("⏳ Aguardando aprovação do administrador...")
    pausar()

def minhas_doacoes_pendentes():
    """MINHAS DOAÇÕES PENDENTES - Para doadores"""
    exibir_cabecalho("MINHAS DOAÇÕES PENDENTES")
    
    minhas_pendencias = [p for p in pendencias if p['usuario_id'] == usuario_logado['id'] and p['tipo'] == 'ENTRADA']
    #                   Gera lista de Pendencias 👆👆
    if not minhas_pendencias:# verifica se não existem pendencias
        print("📭 Você não tem doações pendentes.")
        return
    
    #cabeçalho da tebela
    print(f"🎁 Suas Doações Pendentes ({len(minhas_pendencias)}):")
    print("-" * 80)
    print(f"{'ID':<4} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA':<16} {'STATUS':<12}")
    print("-" * 80)
    
    for pend in minhas_pendencias:  #exibe todas as pendencias
        print(f"{pend['id']:<4} {pend['produto_nome'][:18]:<20} "
              f"{pend['quantidade']:<12} {pend['data_solicitacao']:<16} {pend['status']:<12}")
    pausar()

def meu_historico_doacoes():
    """MEU HISTÓRICO DE DOAÇÕES - Para doadores (apenas aprovadas)"""
    exibir_cabecalho("MEU HISTÓRICO DE DOAÇÕES")
    
    # Busca apenas movimentações de entrada aprovadas deste doador
    doacoes_aprovadas = [m for m in movimentacoes 
                        if m['tipo'] == 'ENTRADA' 
                        and m.get('doador_id') == usuario_logado['id']]
    
    if not doacoes_aprovadas: # verifica se não existem doações aprovadas
        print("📭 Nenhuma doação aprovada no histórico.")
        pausar()
        return
    
    total_doacoes = sum(d['quantidade'] for d in doacoes_aprovadas) #soma doações armazena total
    total_itens = len(doacoes_aprovadas)    # quantidades de aprovadas
    
    #informações + cabeçalho da tabela
    print(f"📊 Seu Histórico de Doações Aprovadas ({total_itens} registros):")
    print(f"📦 Total doado: {total_doacoes} unidades")
    print("-" * 80)
    print(f"{'DATA':<16} {'PRODUTO':<20} {'QUANTIDADE':<12} {'STATUS':<10}")
    print("-" * 80)
    
    for doacao in doacoes_aprovadas:    #exibe toda a tabela
        status = doacao.get('status', 'Aprovada')
        print(f"{doacao['data']:<16} {doacao['produto_nome'][:18]:<20} {doacao['quantidade']:<12} {status:<10}")
    
    pausar()

# =============================================
# MÓDULO PARA SOLICITANTES
# =============================================

def visualizar_produtos_disponiveis():
    """VISUALIZAR PRODUTOS DISPONÍVEIS - Para solicitantes"""
    exibir_cabecalho("PRODUTOS DISPONÍVEIS")
    
    produtos_disponiveis = [p for p in produtos if p['quantidade'] > 0 and p['ativo']]
    # list comprehension para gerar produtos_disponiveis 👆👆
    if not produtos_disponiveis:  # senão tiver produtos
        print("📭 Nenhum produto disponível no momento.")
        return
    
    #informações + cabeçalho da tabela
    print(f"📦 Produtos Disponíveis ({len(produtos_disponiveis)} itens):")
    print("-" * 80)
    print(f"{'ID':<4} {'NOME':<20} {'CATEGORIA':<15} {'QUANTIDADE':<12} {'DOADOR':<15}")
    print("-" * 80)
    
    for produto in produtos_disponiveis:    #exibe tabela
        doador = produto.get('doador_nome', 'Sistema')[:13]
        print(f"{produto['id']:<4} {produto['nome'][:18]:<20} {produto['categoria'][:13]:<15} "
              f"{produto['quantidade']:<12} {doador:<15}")
    pausar()

def nova_solicitacao_pendente():
    """
    NOVA SOLICITAÇÃO PENDENTE - Para solicitantes
    Cria uma pendência de saída que precisa ser aprovada
    """
    exibir_cabecalho("NOVA SOLICITAÇÃO")
    
    # Mostra produtos disponíveis
    visualizar_produtos_disponiveis()
    print()
    
    try:    #tenta receber informações, se não conseguir exibe erro
        produto_id = int(input("📦 ID do produto desejado: "))
        quantidade = int(input("📊 Quantidade desejada: ")) 
        produto = next((p for p in produtos if p['id'] == produto_id and p['quantidade'] > 0), None)
        #                   procura produto 👆👆
        if produto: #se encontrar produto
            if produto['quantidade'] >= quantidade: #verifica se quantidade estoque > quantidade  solicitada
                # Cria pendência de saída
                pendencia = {
                    'id': len(pendencias) + 1,
                    'tipo': 'SAIDA',
                    'produto_id': produto_id,
                    'produto_nome': produto['nome'],
                    'quantidade': quantidade,
                    'usuario_id': usuario_logado['id'],
                    'usuario_nome': usuario_logado['nome'],
                    'data_solicitacao': datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'status': 'Pendente'
                }
                
                pendencias.append(pendencia)    #adiciona a lista em memoria
                salvar_dados()      #salva novas informações no json
                
                print(f"\n✅ Solicitação registrada com sucesso! (ID: {pendencia['id']})")
                print(f"📦 {quantidade} unidades de '{produto['nome']}'")
                print("⏳ Aguardando Avaliação do administrador...")
            else:
                print("❌ Quantidade solicitada maior que o estoque disponível!")
        else:
            print("❌ Produto não encontrado ou indisponível!")
            
    except ValueError:
        print("❌ Por favor, digite valores numéricos válidos!")
    pausar()

def minhas_solicitacoes_pendentes():
    """MINHAS SOLICITAÇÕES PENDENTES - Para solicitantes"""
    exibir_cabecalho("MINHAS SOLICITAÇÕES PENDENTES")
    
    minhas_pendencias = [p for p in pendencias if p['usuario_id'] == usuario_logado['id'] and p['tipo'] == 'SAIDA']
    #                   List comprehension para gerar lista de pendencias  👆👆
    if not minhas_pendencias:   #verifica existencia de pendencias
        print("📭 Você não tem solicitações pendentes.")
        return
    
    #exibe cabeçalho da tabela
    print(f"📋 Suas Solicitações Pendentes ({len(minhas_pendencias)}):")
    print("-" * 80)
    print(f"{'ID':<4} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA':<16} {'STATUS':<12}")
    print("-" * 80)
    
    for pend in minhas_pendencias:  #exibe todas as pendencias
        print(f"{pend['id']:<4} {pend['produto_nome'][:18]:<20} "
              f"{pend['quantidade']:<12} {pend['data_solicitacao']:<16} {pend['status']:<12}")
    pausar()

# =============================================
# MÓDULO PARA ADMINISTRADORES
# =============================================

def listar_todas_pendencias():
    """LISTA TODAS AS PENDÊNCIAS - Para administradores"""
    exibir_cabecalho("TODAS AS PENDÊNCIAS")
    #List comprehension para gerar lista de pendencias a serem avaliadas 
    pendencias_pendentes = [p for p in pendencias if p['status'] == 'Pendente']
    
    if not pendencias_pendentes:    #verifica se não existe pendencia
        print("✅ Nenhuma pendência no momento.")
        return
    
    #cabeçalho da tabela
    print(f"{'ID':<4} {'TIPO':<8} {'USUÁRIO':<20} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA':<16}")
    print("-" * 90)
    
    for pend in pendencias_pendentes:   #Exibe tabela de pendencias a ser avaliadas
        tipo = "🎁 ENTRADA" if pend['tipo'] == 'ENTRADA' else "📦 SAÍDA"
        print(f"{pend['id']:<4} {tipo:<8} {pend['usuario_nome'][:18]:<20} {pend['produto_nome'][:18]:<20} "
              f"{pend['quantidade']:<12} {pend['data_solicitacao']:<16}")

def aprovar_entrada(pendencia):
    """APROVA UMA ENTRADA (DOAÇÃO)"""
    # Cria o produto no estoque
    produto = {
        'id': len(produtos) + 1,
        'nome': pendencia['produto_nome'],
        'descricao': pendencia.get('produto_descricao', ''),
        'categoria': pendencia.get('produto_categoria', 'Outros'),
        'peso': pendencia.get('produto_peso', 0),
        'data_validade': pendencia.get('produto_validade', '01/01/2099'),
        'quantidade': pendencia['quantidade'],
        'quantidade_minima': 5,
        'doador_id': pendencia['usuario_id'],
        'doador_nome': pendencia['usuario_nome'],
        'data_cadastro': datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        'status': 'Disponível',
        'ativo': True
    }
    
    produtos.append(produto) #adiciona a lista em memoria
    
    # Registra movimentação aprovada
    movimentacao = {
        'id': len(movimentacoes) + 1,
        'tipo': 'ENTRADA',
        'produto_id': produto['id'],
        'produto_nome': produto['nome'],
        'quantidade': pendencia['quantidade'],
        'doador_id': pendencia['usuario_id'],
        'doador_nome': pendencia['usuario_nome'],
        'data': datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        'usuario': usuario_logado['nome'],
        'status': 'Aprovada'
    }
    
    movimentacoes.append(movimentacao) #adiciona movimentaçãoem memoria
    
    # Atualiza status da pendência
    pendencia['status'] = 'Aprovada'
    pendencia['data_processamento'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pendencia['processado_por'] = usuario_logado['nome']
    
    salvar_dados()  #passa alterações em memorai para .json
    
    print(f"\n✅ Entrada aprovada com sucesso!")
    print(f"📦 {pendencia['quantidade']} unidades de '{pendencia['produto_nome']}'")
    print(f"🎁 Doação de: {pendencia['usuario_nome']}")

def aprovar_saida(pendencia):
    """APROVA UMA SAÍDA (SOLICITAÇÃO)"""
    produto = next((p for p in produtos if p['id'] == pendencia['produto_id']), None)
    #       procura produto 👆👆
    if not produto: #verifica se não existe produto
        print("❌ Produto não encontrado no estoque!")
        return
    
    if produto['quantidade'] < pendencia['quantidade']: # verifica se quantidade estoque < quantidade solicitação
        print("❌ Estoque insuficiente para aprovar esta solicitação!")
        return
    
    # Atualiza estoque (produto quantidade = produto quantidade - pendencia quantidade)
    produto['quantidade'] -= pendencia['quantidade']
    
    # Registra movimentação aprovada
    movimentacao = {
        'id': len(movimentacoes) + 1,
        'tipo': 'SAIDA',
        'produto_id': pendencia['produto_id'],
        'produto_nome': pendencia['produto_nome'],
        'quantidade': pendencia['quantidade'],
        'solicitante_id': pendencia['usuario_id'],
        'solicitante_nome': pendencia['usuario_nome'],
        'data': datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        'usuario': usuario_logado['nome'],
        'status': 'Aprovada'
    }
    
    movimentacoes.append(movimentacao) #adiciona na lista lista em memoria
    
    # Atualiza status da pendência
    pendencia['status'] = 'Aprovada'
    pendencia['data_processamento'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pendencia['processado_por'] = usuario_logado['nome']
    
    salvar_dados() #salva lista memoriapara .json
    
    print(f"\n✅ Saída aprovada com sucesso!")
    print(f"📦 {pendencia['quantidade']} unidades de '{pendencia['produto_nome']}'")
    print(f"🤝 Solicitante: {pendencia['usuario_nome']}")

def processar_reprovacao(pendencia):
    """PROCESSA REPROVAÇÃO DE UMA PENDÊNCIA"""
    pendencia['status'] = 'Reprovada'
    pendencia['data_processamento'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pendencia['processado_por'] = usuario_logado['nome']
    
    salvar_dados() #atualiza dados no .json
    
    print(f"\n❌ Pendência reprovada!")
    print(f"📋 ID: {pendencia['id']}")
    print(f"👤 Usuário: {pendencia['usuario_nome']}")

def processar_aprovacao(pendencia):
    """PROCESSA APROVAÇÃO DE UMA PENDÊNCIA"""

    #faz a aprovação conforme entrada/saida
    if pendencia['tipo'] == 'ENTRADA':
        aprovar_entrada(pendencia)
    else:
        aprovar_saida(pendencia)

def aprovar_reprovar_pendencias():
    """APROVA/REPROVA PENDÊNCIAS - Função principal dos administradores"""
    exibir_cabecalho("APROVAR/REPROVAR PENDÊNCIAS")
    
    pendencias_pendentes = [p for p in pendencias if p['status'] == 'Pendente']
    #       List comprehension para gerar pendencias a ser  avaliadas👆👆
    if not pendencias_pendentes:    #Verifica se não tem  pendencias
        print("✅ Nenhuma pendência para aprovar no momento.")
        pausar()
        return
    
    #cabeçalho da tabela
    print("📋 Pendências Pendentes:")
    print("-" * 90)
    print(f"{'ID':<4} {'TIPO':<8} {'USUÁRIO':<20} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA':<16}")
    print("-" * 90)

    # Lista pendências
    for pend in pendencias_pendentes:
        tipo = "🎁 ENTRADA" if pend['tipo'] == 'ENTRADA' else "📦 SAÍDA"
        print(f"{pend['id']:<4} {tipo:<8} {pend['usuario_nome'][:18]:<20} {pend['produto_nome'][:18]:<20} "
              f"{pend['quantidade']:<12} {pend['data_solicitacao']:<16}")
    
    try:    #tenta pegar informações,se não conseguir exibe erro
        pendencia_id = int(input("\n📋 ID da pendência a aprovar/reprovar: "))
        acao = input("✅ Aprovar (a) ou ❌ Reprovar (r)? ").lower()
        
        pendencia = next((p for p in pendencias if p['id'] == pendencia_id and p['status'] == 'Pendente'), None)
        #           Procura pendecia pelo ID 👆👆
        if pendencia:   #se encontrar pendencia
            if acao == 'a':
                processar_aprovacao(pendencia)
            elif acao == 'r':
                processar_reprovacao(pendencia)
            else:
                print("❌ Ação inválida!")
                pausar()
        else:       #se não encontrar pendencia
            print("❌ Pendência não encontrada ou já processada!")
            pausar()
            
    except ValueError:
        print("❌ Por favor, digite um ID válido!")
        pausar()

def menu_aprovar_pendencias():
    """MENU APROVAR PENDÊNCIAS - Principal função dos administradores"""
    while True:
        exibir_cabecalho("APROVAR PENDÊNCIAS")
        
        # Contadores de totais entradas/saidas
        pendencias_entrada = len([p for p in pendencias if p['tipo'] == 'ENTRADA' and p['status'] == 'Pendente'])
        pendencias_saida = len([p for p in pendencias if p['tipo'] == 'SAIDA' and p['status'] == 'Pendente'])
        
        print(f"📊 Pendências para Aprovação:")
        print(f"   🎁 Entradas (Doações): {pendencias_entrada}")
        print(f"   📦 Saídas (Solicitações): {pendencias_saida}")
        print("-" * 40)
        
        print("1. ✅ Aprovar/Reprovar Pendências")
        print("2. 📋 Listar Todas as Pendências")
        print("3. 🏠 Voltar")
        
        opcao = input("\n📋 Escolha uma opção: ")
        
        if opcao == '1':
            aprovar_reprovar_pendencias()
        elif opcao == '2':
            listar_todas_pendencias()
        elif opcao == '3':
            break
        else:
            print("❌ Opção inválida!")
        pausar()

def verificar_produtos_proximos_vencimento():
    """VERIFICA PRODUTOS PRÓXIMOS DO VENCIMENTO"""
    produtos_proximos = []
    hoje = datetime.datetime.now()
    
    for produto in produtos:
        try:
            #converte string para datetime e faz operações
            data_validade = datetime.datetime.strptime(produto['data_validade'], "%d/%m/%Y")
            dias_para_vencer = (data_validade - hoje).days
            if 0 <= dias_para_vencer <= 30: #verifica produtos com vencimento em até 30 dias
                produtos_proximos.append(produto)   #adiciona a lista a de "perto de vencer"
        except: #Se houver erro na conversão da data, pula para o próximo produto
            continue
    
    return produtos_proximos  #retorna lista de produtos perto do vencimento

def visualizar_estoque():
    """VISUALIZAR ESTOQUE - Para administradores"""
    exibir_cabecalho("ESTOQUE ATUAL")
    
    if not produtos: #verifica se não tem produtos em estoque
        print("📭 Nenhum produto no estoque.")
        pausar()
        return
    
    # Alertas
    produtos_baixo_estoque = [p for p in produtos if p['quantidade'] <= p['quantidade_minima']]
    produtos_proximos_vencer = verificar_produtos_proximos_vencimento()
    
    if produtos_baixo_estoque:  #se existir produtos abaixo do estoque minimo
        print("⚠️  ALERTAS DE ESTOQUE BAIXO:")
        for produto in produtos_baixo_estoque:# lista produtos com estoque baixo
            print(f"   📦 {produto['nome']} - apenas {produto['quantidade']} unidades")
        print()
    
    if produtos_proximos_vencer:     #se existir produtos perto de vencer
        print("⚠️  PRODUTOS PRÓXIMOS DO VENCIMENTO:")
        for produto in produtos_proximos_vencer:    #lista de produtos perto de vencer
            print(f"   ⏰ {produto['nome']} - vence em {produto['data_validade']}")
        print()
    
    #cabeçalho da tabela
    print(f"{'ID':<4} {'NOME':<20} {'CATEGORIA':<15} {'QUANTIDADE':<12} {'ESTOQUE':<10} {'VALIDADE':<12}")
    print("-" * 90)
    
    for produto in produtos:    #lista produtos
        estoque_status = "🟢 OK" if produto['quantidade'] > produto['quantidade_minima'] else "🔴 BAIXO"
        print(f"{produto['id']:<4} {produto['nome'][:18]:<20} {produto['categoria'][:13]:<15} "
              f"{produto['quantidade']:<12} {estoque_status:<10} {produto['data_validade']:<12}")
    
    pausar()

def gerar_relatorio_estoque():
    subprocess.run(["./Relatorio_de_Estoque.exe"])
    '''"""GERA RELATÓRIO DE ESTOQUE EM PYTHON"""
    exibir_cabecalho("RELATÓRIO DE ESTOQUE")
    
    if not produtos:    #se não existir produto
        print("📭 Nenhum produto no estoque para relatório.")
        pausar()
        return
    
    # Estatísticas
    total_produtos = len(produtos)
    total_unidades = sum(p['quantidade'] for p in produtos)
    produtos_baixo_estoque = [p for p in produtos if p['quantidade'] <= p['quantidade_minima']]
    produtos_proximos_vencer = verificar_produtos_proximos_vencimento()
    
    print("📊 RESUMO DO ESTOQUE:")
    print(f"   📦 Total de produtos: {total_produtos}")
    print(f"   🔢 Total de unidades: {total_unidades}")
    print(f"   ⚠️  Produtos com estoque baixo: {len(produtos_baixo_estoque)}")
    print(f"   ⏰ Produtos próximos do vencimento: {len(produtos_proximos_vencer)}")
    print("-" * 80)
    
    #contagem de produtos por categoria
    categorias = {}
    for produto in produtos:
        cat = produto['categoria']
        if cat in categorias:
            categorias[cat] += 1
        else:
            categorias[cat] = 1
    
    print("\n🏷️  PRODUTOS POR CATEGORIA:")
    for categoria, quantidade in categorias.items(): # exibição das contagens
        print(f"   {categoria}: {quantidade} produtos")
    
    # Produtos com estoque baixo
    if produtos_baixo_estoque:
        print("\n🔴 PRODUTOS COM ESTOQUE BAIXO:")
        for produto in produtos_baixo_estoque:  #exibição de estoques baixos
            print(f"   📦 {produto['nome']} - {produto['quantidade']} unidades "
                  f"(mínimo: {produto['quantidade_minima']})")
    
    # Produtos próximos do vencimento
    if produtos_proximos_vencer:
        print("\n⏰ PRODUTOS PRÓXIMOS DO VENCIMENTO:")
        for produto in produtos_proximos_vencer:    #exibição de proximos do vencimento
            print(f"   📦 {produto['nome']} - vence em {produto['data_validade']}")
    '''
    pausar()

def gerar_relatorio_movimentacoes():
    """GERA RELATÓRIO DE MOVIMENTAÇÕES EM PYTHON"""
    exibir_cabecalho("RELATÓRIO DE MOVIMENTAÇÕES")
    
    if not movimentacoes:   #se não tem movimentações
        print("📭 Nenhuma movimentação registrada.")
        pausar()
        return
    
    # Filtros de periodos
    print("📅 Filtrar por período:")
    print("1. 📊 Últimos 7 dias")
    print("2. 📈 Últimos 30 dias")
    print("3. 📋 Todo o histórico")
    
    try: #verifica se input 'filtro' é valido
        filtro = int(input("\n📋 Escolha o período: "))
        
        hoje = datetime.datetime.now()
        movimentacoes_filtradas = []
        
        for mov in movimentacoes: # Percorre todas as movimentações para aplicar o filtro
            try:
                #coverte string para datetime
                data_mov = datetime.datetime.strptime(mov['data'], "%d/%m/%Y %H:%M")
                
                #aplicação do filtro conforme input "filtro" anteriormente
                if filtro == 1 and (hoje - data_mov).days <= 7:
                    movimentacoes_filtradas.append(mov)
                elif filtro == 2 and (hoje - data_mov).days <= 30:
                    movimentacoes_filtradas.append(mov)
                elif filtro == 3:
                    movimentacoes_filtradas.append(mov)
                    
            except: # Se houver erro na conversão de data, pula para a próxima movimentação
                continue
        
        if not movimentacoes_filtradas: #se nenhuma movimentação no periodo selecionado
            print("📭 Nenhuma movimentação no período selecionado.")
            pausar()
            return
        
        # Estatísticas
        # List comprehension: filtra apenas movimentações do tipo ENTRADA
        entradas = [m for m in movimentacoes_filtradas if m['tipo'] == 'ENTRADA']
        saidas = [m for m in movimentacoes_filtradas if m['tipo'] == 'SAIDA']
        # List comprehension: filtra apenas movimentações do tipo SAIDA 👆

        #armazena quantidade totais de cada tipo
        total_entradas = sum(e['quantidade'] for e in entradas)
        total_saidas = sum(s['quantidade'] for s in saidas)
        
        print(f"\n📊 RESUMO DO PERÍODO:")
        print(f"   🎁 Entradas (doações): {len(entradas)} registros, {total_entradas} unidades")
        print(f"   📦 Saídas (solicitações): {len(saidas)} registros, {total_saidas} unidades")
        print(f"   📈 Saldo líquido: {total_entradas - total_saidas} unidades")
        print("-" * 90)
        
        # Exibe o cabeçalho
        print(f"\n📋 DETALHES DAS MOVIMENTAÇÕES:")
        print(f"{'DATA':<16} {'TIPO':<8} {'PRODUTO':<20} {'QUANTIDADE':<12} {'USUÁRIO':<20}")
        print("-" * 90)
        
        for mov in movimentacoes_filtradas: #lista movimentações
            tipo = "🎁 ENTRADA" if mov['tipo'] == 'ENTRADA' else "📦 SAÍDA"
            usuario = mov.get('doador_nome', mov.get('solicitante_nome', 'Sistema'))[:18]
            print(f"{mov['data']:<16} {tipo:<8} {mov['produto_nome'][:18]:<20} {mov['quantidade']:<12} {usuario:<20}")
        
    except ValueError:
        print("❌ Opção inválida!")
        pausar()

def gerar_relatorio_pendencias():
    """GERA RELATÓRIO DE PENDÊNCIAS EM PYTHON"""
    exibir_cabecalho("RELATÓRIO DE PENDÊNCIAS")
    
    if not pendencias:  #se não tiver pendencias
        print("📭 Nenhuma pendência registrada.")
        pausar()
        return
    
    # Estatísticas
    #list comprehension: para filtrar tipos de pendencias em listas separadas
    pendencias_pendentes = [p for p in pendencias if p['status'] == 'Pendente']
    pendencias_aprovadas = [p for p in pendencias if p['status'] == 'Aprovada']
    pendencias_reprovadas = [p for p in pendencias if p['status'] == 'Reprovada']
    
    print("📊 RESUMO DE PENDÊNCIAS:")
    print(f"   ⏳ Pendentes: {len(pendencias_pendentes)}")
    print(f"   ✅ Aprovadas: {len(pendencias_aprovadas)}")
    print(f"   ❌ Reprovadas: {len(pendencias_reprovadas)}")
    print(f"   📋 Total: {len(pendencias)}")
    print("-" * 90)
    
    # List comprehension: filtrar entre listas entradas e saidas
    entradas_pendentes = [p for p in pendencias_pendentes if p['tipo'] == 'ENTRADA']
    saidas_pendentes = [p for p in pendencias_pendentes if p['tipo'] == 'SAIDA']
    
    print("\n📋 PENDÊNCIAS PENDENTES:")
    print(f"   🎁 Entradas (doações): {len(entradas_pendentes)}")
    print(f"   📦 Saídas (solicitações): {len(saidas_pendentes)}")
    
    if pendencias_pendentes:    #se exitem pendencias a ser avaliadas
        print(f"\n📋 DETALHES DAS PENDÊNCIAS PENDENTES:") #gera cabeçalho
        print(f"{'ID':<4} {'TIPO':<8} {'USUÁRIO':<20} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA':<16}")
        print("-" * 90)
        
        for pend in pendencias_pendentes: # lista as pendencias a serem avaliadas
            tipo = "🎁 ENTRADA" if pend['tipo'] == 'ENTRADA' else "📦 SAÍDA"
            print(f"{pend['id']:<4} {tipo:<8} {pend['usuario_nome'][:18]:<20} {pend['produto_nome'][:18]:<20} "
                  f"{pend['quantidade']:<12} {pend['data_solicitacao']:<16}")
    
    pausar()

def menu_relatorios():
    """MENU DE RELATÓRIOS EM PYTHON"""
    while True:
        exibir_cabecalho("RELATÓRIOS")
        # menu simples para escolha
        print("1. 📊 Relatório de Estoque")
        print("2. 📈 Relatório de Movimentações")
        print("3. 📋 Relatório de Pendências")
        print("4. 🏠 Voltar")
        
        opcao = input("\n📋 Escolha uma opção: ")
        
        if opcao == '1':
            gerar_relatorio_estoque()
        elif opcao == '2':
            gerar_relatorio_movimentacoes()
        elif opcao == '3':
            gerar_relatorio_pendencias()
        elif opcao == '4':
            break
        else:
            print("❌ Opção inválida!")
            pausar()

# =============================================
# MENUS POR PERFIL
# =============================================

def menu_doador():
    """MENU PRINCIPAL PARA DOADORES"""
    while True:
        exibir_cabecalho("MENU PRINCIPAL")
        print(f"👤 Usuário: {usuario_logado['nome']} | Perfil: {usuario_logado['perfil']}")
        print("-" * 40)
        #menu simples para escolha
        print("1. 🎁 Registrar Nova Doação")
        print("2. 📦 Minhas Doações Pendentes")
        print("3. 📊 Meu Histórico de Doações")
        print("4. 👤 Meu Perfil")
        print("5. 🎭 Trocar de Usuario")
        print("6. 🚪 Sair")
        

        opcao = input("\n📋 Escolha uma opção: ")
        
        if opcao == '1':
            registrar_doacao_pendente()
        elif opcao == '2':
            minhas_doacoes_pendentes()
        elif opcao == '3':
            meu_historico_doacoes()
        elif opcao == '4':
            menu_meu_perfil()
        elif opcao == '5':
            if trocar_usuario():
                return True
        elif opcao == '6':
            limpar_tela()
            print("\n👋 Até logo!")
            return False
        else:
            print("❌ Opção inválida!")

def menu_solicitante():
    """MENU PRINCIPAL PARA SOLICITANTES"""
    while True:
        exibir_cabecalho("MENU PRINCIPAL")
        print(f"👤 Usuário: {usuario_logado['nome']} | Perfil: {usuario_logado['perfil']}")
        print("-" * 40)

        #   menu simples para escolha
        print("1. 📦 Visualizar Produtos Disponíveis")
        print("2. 📋 Nova Solicitação")
        print("3. 📊 Minhas Solicitações Pendentes")
        print("4. 👤 Meu Perfil")
        print("5. 🎭 Trocar de Usuario")
        print("6. 🚪 Sair")
        
        opcao = input("\n📋 Escolha uma opção: ")
        
        if opcao == '1':
            visualizar_produtos_disponiveis()
        elif opcao == '2':
            nova_solicitacao_pendente()
        elif opcao == '3':
            minhas_solicitacoes_pendentes()
        elif opcao == '4':
            menu_meu_perfil()
        elif opcao == '5':
            if trocar_usuario():
                return True
        elif opcao == '6':
            limpar_tela()
            print("\n👋 Até logo!")
            return False
        else:
            print("❌ Opção inválida!")
            pausar()

def menu_administrador():
    """MENU PRINCIPAL PARA ADMINISTRADORES"""
    while True:
        exibir_cabecalho("MENU PRINCIPAL")
        print(f"👤 Usuário: {usuario_logado['nome']} | Perfil: {usuario_logado['perfil']}")
        print("-" * 40)
        #   menu simples para escolha
        print("1. ✅ Aprovar/Reprovar Pendências")
        print("2. 📦 Visualizar Estoque")
        print("3. 📊 Relatórios")
        print("4. 👥 Gerenciar Usuários")
        print("5. 👤 Meu Perfil")
        print("6. 🎭 Trocar de Usuario")    
        print("7. 🚪 Sair")
        
        opcao = input("\n📋 Escolha uma opção: ")
        
        if opcao == '1':
            menu_aprovar_pendencias()
        elif opcao == '2':
            visualizar_estoque()
        elif opcao == '3':
            menu_relatorios()
        elif opcao == '4':
            menu_gerenciar_usuarios()
        elif opcao == '5':
            menu_meu_perfil()
        elif opcao == '6':
            if trocar_usuario():
                return True
        elif opcao == '7':
            limpar_tela()
            print("\n👋 Até logo!")
            return False            
        else:
            print("❌ Opção inválida!")
            pausar()

def menu_principal():
    """MENU PRINCIPAL APÓS LOGIN"""
    #   indetifica perfil do usuario e redireciona para seu menu
    perfil = usuario_logado['perfil']

    if perfil == 'Administrador':
       manter_sistema = menu_administrador()
    elif perfil == 'Doador':
        manter_sistema = menu_doador()
    elif perfil == 'Solicitante':
        manter_sistema = menu_solicitante()

    #se "True" há troca de Usuário, se "False" Finaliza o sistema
    return manter_sistema if manter_sistema is not None else True

# =============================================
# FUNÇÃO PRINCIPAL
# =============================================

def main():
    """FUNÇÃO PRINCIPAL DO SISTEMA"""
    limpar_tela()
    print("🚀 Inicializando Sistema de Gestão Estoque da S.O.S Sorocaba...")
    
    # Inicialização
    inicializar_dados()
    carregar_dados()
    
    print("📁 Dados carregados dos arquivos JSON")
    print("✅ Sistema inicializado com sucesso!")
    pausar()
    
    # Loop principal
    while True:
        exibir_cabecalho("TELA INICIAL")
        #   menu simples para escolha
        print("1. 🔐 Login")
        print("2. 🔓 Recuperar Senha")
        print("3. 🚪 Sair do Sistema")
        

        opcao = input("\n📋 Escolha uma opção: ")
        
        if opcao == '1':
            if login(): # Retorna "True" se login bem sucedido
                # Chama menu_principal e verifica se quer continuar no sistema
                continuar = menu_principal()
                if not continuar:
                    break  # Sai do loop principal e finaliza o sistema
        elif opcao == '2':
            recuperar_senha()
        elif opcao == '3':
            print("\n👋 Obrigado por usar nosso sistema! Até logo!")
            break
        else:
            print("❌ Opção inválida!")
            pausar()

# =============================================
# EXECUÇÃO DO PROGRAMA
# =============================================

if __name__ == "__main__":
    main()

