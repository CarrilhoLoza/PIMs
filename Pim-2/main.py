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
    """Limpa formatação do telefone, mantendo apenas dígitos"""
    if not telefone:
        return ""
    
    # Remove todos os caracteres não numéricos
    telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))
    
    return telefone_limpo

def estruturar_telefone(telefone_limpo):
    """Estrutura o telefone no formato brasileiro"""
    if len(telefone_limpo) == 11:  # Celular com 9 dígitos
        return f"({telefone_limpo[0:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
    elif len(telefone_limpo) == 10:  # Telefone fixo com 8 dígitos
        return f"({telefone_limpo[0:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
    else:
        return telefone_limpo  # Retorna como está se não for formato esperado

def validar_formatar_cpf(cpf: str):
    """
    Valida CPF (com dígitos verificadores) e retorna formatado.
    Retorna:
        (cpf_formatado, True)  -> se válido
        (mensagem_erro, False) -> se inválido
    """
    # Remove pontuação
    cpf_limpo = cpf.strip().replace(".", "").replace("-", "")

    # Checagens básicas
    if not cpf_limpo.isdigit() or len(cpf_limpo) != 11:
        return ("❌ CPF deve conter exatamente 11 números.", False)
    if cpf_limpo == cpf_limpo[0] * 11:
        return ("❌ CPF inválido: todos os dígitos iguais.", False)

    ## para conseguir utilizar cpf ficticio para exemplo o codigo de validação abaixo está "desativado"
    '''
    # Cálculo do 1º dígito verificador
    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10

    # Cálculo do 2º dígito verificador
    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10

    if cpf_limpo[-2:] != f"{digito1}{digito2}":
        return ("❌ CPF inválido! Dígitos verificadores não conferem.", False)'''

    # Formata CPF no padrão XXX.XXX.XXX-XX
    cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return (cpf_formatado, True)

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
    
    usuario = next((u for u in usuarios if u['email'] == email), None)#encontra usuario com email
    
    if not usuario: #verifica se usuario não existe no sistema
        print(f"\n❌ E-mail não encontrado no sistema.")
        pausar()
        return

    # Verificação de identidade
    verificacao_ok = True
    mensagens_erro = []
    
    if usuario['nome'] != nome_completo: #checa nomes
        verificacao_ok = False
        mensagens_erro.append("❌ Nome completo não confere")
    
    resultado, valido = validar_formatar_cpf(cpf)

    if valido:
        cpf = resultado  # aqui sim pegamos o CPF formatado
    else:
        print(resultado)  # mostra mensagem de erro
        pausar()
        return  #pede para digitar novamente
    
    if usuario['cpf']  != cpf:    #checa cpf
        verificacao_ok = False
        mensagens_erro.append("❌ CPF não confere")
    
    telefone_input = limpar_telefone(telefone)  #limpa telefone da entrada atual
    telefone_armazenado = limpar_telefone(usuario['telefone'])  #limpa telefone armazenado

    if telefone_armazenado != telefone_input:
        verificacao_ok = False
        mensagens_erro.append("❌ Telefone não confere")
    
    if verificacao_ok:  #se informações corretas
        senha_temporaria = gerar_senha_temporaria()     #gera nova senha
        usuario_original = next((u for u in usuarios if u['id'] == usuario['id']), None) 
        # encontra usuario pelo id ou retorna "None" se não encontar 👆👆

        if usuario_original:        #se encontar ussuario
            usuario_original['senha'] = senha_temporaria  #reseta senha
            salvar_dados()      #salva alteração

            
            print(f"\n✅ Identidade verificada com sucesso!")
            print(f"🔑 Sua senha temporária: {senha_temporaria}")
            print(f"\n📝 Instruções:")
            print("   1. Faça login com esta senha temporária")
            print("   2. Vá em 'Meu Perfil' para redefinir sua senha")
            print("   3. Escolha uma senha segura e fácil de lembrar")
            
        else:
            print(f"\n❌ Erro interno ao atualizar senha.")
        pausar() 
    else:       #se infrmação não forem coincidentes com armazenadas
        print(f"\n❌ Falha na verificação de identidade.")
        print("   Erros encontrados:")
        for erro in mensagens_erro: #informa erros 
            print(f"   - {erro}")
        print(f"\nVerifique os dados informados e tente novamente.")
        pausar()
    pausar()

def alterar_senha():
    """REDEFINE SENHA DO USUÁRIO LOGADO"""
    exibir_cabecalho("REDEFINIR SENHA")
    
    print("🔐 Redefinição de Senha")
    print("-" * 30)
    
    # Pede senha atual ao usuario
    senha_atual = input("🔒 Senha atual: ").strip()
    
    # Verifica se senha está incorreta
    if senha_atual != usuario_logado['senha']:
        print("\n❌ Senha atual incorreta!")
        pausar()
        return
    
    # Solicita e valida a nova senha
    print("\n🔐 Nova Senha - Requisitos:")
    print("   • Mínimo 8 caracteres")
    print("   • Pelo menos 1 letra maiúscula")
    print("   • Pelo menos 1 letra minúscula") 
    print("   • Pelo menos 1 número")
    print("   • Pelo menos 1 caractere especial (!@#$%&*)")
    print("-" * 50)
    
    while True:
        nova_senha = input("🆕 Nova senha: ").strip()
        confirmar_senha = input("✅ Confirmar nova senha: ").strip()
        
        if nova_senha != confirmar_senha:
            print("❌ As senhas não coincidem! Tente novamente.\n")
            continue
        
        # Validação da senha integrada
        senha_valida = True
        erros = []
        
        if len(nova_senha) < 8:
            senha_valida = False
            erros.append("❌ A senha deve ter pelo menos 8 caracteres")
        
        # Verifica requisitos de complexidade
        tem_maiuscula = any(char.isupper() for char in nova_senha)
        tem_minuscula = any(char.islower() for char in nova_senha)
        tem_numero = any(char.isdigit() for char in nova_senha)
        tem_especial = any(not char.isalnum() for char in nova_senha)

        if not tem_maiuscula:
            senha_valida = False
            erros.append("❌ A senha deve conter pelo menos 1 letra maiúscula")
        if not tem_minuscula:
            senha_valida = False
            erros.append("❌ A senha deve conter pelo menos 1 letra minúscula")
        if not tem_numero:
            senha_valida = False
            erros.append("❌ A senha deve conter pelo menos 1 número")
        if not tem_especial:
            senha_valida = False
            erros.append("❌ A senha deve conter pelo menos 1 caractere especial (!@#$%&*)")
        
        if not senha_valida:
            print("\n")
            for e in erros:
                print(e)
            print("\n") 
            continue
        break  # Senha válida, sai do loop
    
    # Atualiza a senha
    usuario_logado['senha'] = nova_senha
    
    # Atualiza a senha na lista em memoria
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
    
    #verifica entradas vazias
    for info in [nome, email, cpf, telefone]:
        if  not info:
            print("❌ Por favor, preencha todos os campos!")
            return
        

    #verifica se email tem estrutura valida
    if email.count("@") != 1:   #verifica existencia necessaria de @
        print("❌ O e-mail deve conter apenas um '@'.")
        return
    if " " in email:    #verifica se email tem espaços
        print("❌ O e-mail não pode conter espaços.")
        return
    
    nome, dominio = email.split("@", 1)# divide nome do dominio para analisar em partes

    if not nome: #verifica se email tem nome
        print("❌ O e-mail precisa ter algo antes do '@'")
        return 
    if not dominio: #verifica se email tem dominio
        print("❌ O e-mail precisa ter algo depois do '@'")
        return 
    if "." not in dominio: #verifica se email contem "." no dominio
        print("❌ O domínio deve conter pelo menos um ponto")
        return 
    if dominio.startswith("."): #verifica se dominio começa com "."
        print("❌ O domínio não pode começar com um ponto")
        return 
    if dominio.endswith("."): #verifica se dominio termina com "."
        print("❌ O domínio não pode terminar com um ponto")
        return 

    # Verifica se CPF é valido e já formata
    resultado, valido = validar_formatar_cpf(cpf)
    # resultado ou é o cpf ou é uma mensagem erro
    if valido:
        cpf = resultado  # aqui sim pegamos o CPF formatado
    else:
        print(resultado)  # mostra mensagem de erro
        return  #pede para digitar novamente
    
    # 1. Verifica se email já existe no sistema
    email_existente = next((u for u in usuarios if u['email'] == email), None)
    if email_existente:
        print("❌ Este e-mail já está em uso por outro usuário!")
        pausar()
        return

    # 2. Verifica se CPF já existe no sistema
    cpf_existente = next((u for u in usuarios if u['cpf'] == cpf), None)
    if cpf_existente:
        print("❌ Este CPF já está cadastrado no sistema!")
        pausar()
        return
    
    #formatação telefone
    telefone_limpo = limpar_telefone(telefone)

    # Validação do telefone
    if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
        print("❌ Telefone deve conter DDD (2 dígitos) + número (8 ou 9 dígitos)!")
        pausar()
        return

    # Estrutura o telefone no formato brasileiro
    telefone = estruturar_telefone(telefone_limpo)
    

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
    print(f"📄 CPF: {usuario['cpf']}")
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
        
            #verifica se email tem estrutura valida
        if novo_email.count("@") != 1:   #verifica existencia necessaria de @
            print("❌ O e-mail deve conter apenas um '@'.")
            return
        if " " in novo_email:    #verifica se email tem espaços
            print("❌ O e-mail não pode conter espaços.")
            return
        
        nome, dominio = novo_email.split("@", 1)# divide nome do dominio para analisar em partes

        if not nome: #verifica se email tem nome
            print("❌ O e-mail precisa ter algo antes do '@'")
            pausar()
            return 
        if not dominio: #verifica se email tem dominio
            print("❌ O e-mail precisa ter algo depois do '@'")
            pausar()
            return 
        if "." not in dominio: #verifica se email contem "." no dominio
            print("❌ O domínio deve conter pelo menos um ponto")
            pausar()
            return 
        if dominio.startswith("."): #verifica se dominio começa com "."
            print("❌ O domínio não pode começar com um ponto")
            pausar()
            return 
        if dominio.endswith("."): #verifica se dominio termina com "."
            print("❌ O domínio não pode terminar com um ponto")
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
    descricao = input("📄 Descrição (opcional): ").strip()
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
    for info in [nome, peso, quantidade, data_validade]:
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
    """
    MINHAS DOAÇÕES PENDENTES - Para doadores (apenas ATIVAS)
    
    🔍 FILTRO IMPORTANTE: 
    - usuario_id: Apenas do usuário logado
    - tipo: Apenas ENTRADA (doações)
    - status: Apenas 'Pendente' (ativas)
    """
    exibir_cabecalho("MINHAS DOAÇÕES PENDENTES")
    
    # 🔍 FILTRO CORRIGIDO: Apenas pendências ATIVAS do usuário
    # adicionado 'p['status'] == 'Pendente'' ao filtro
    # Isso garante que apenas pendências ATIVAS serão mostradas
    minhas_pendencias = [p for p in pendencias 
                        if p['usuario_id'] == usuario_logado['id']  # 👈 Do usuário logado
                        and p['tipo'] == 'ENTRADA'                   # 👈 Apenas doações
                        and p['status'] == 'Pendente']               # 👈 APENAS ATIVAS!
    
    # 📭 VERIFICA SE NÃO HÁ PENDÊNCIAS
    if not minhas_pendencias:
        print("📭 Você não tem doações pendentes.")
        pausar()
        return
    
    # 📊 EXIBE A LISTA DE PENDÊNCIAS ATIVAS
    print(f"🎁 Suas Doações Pendentes ({len(minhas_pendencias)}):")
    print("-" * 80)
    print(f"{'ID':<4} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA':<16} {'STATUS':<12}")
    print("-" * 80)
    
    # 📋 PERCORRE E EXIBE CADA PENDÊNCIA ATIVA
    for pend in minhas_pendencias:
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
    """
    MINHAS SOLICITAÇÕES PENDENTES - Para solicitantes (apenas ATIVAS)
    
    🎯 CONCEITO: Consistência de Filtros
    - Mesma lógica para doações e solicitações
    - Usuário só vê o que está realmente ativo
    - Experiência limpa e intuitiva
    """
    exibir_cabecalho("MINHAS SOLICITAÇÕES PENDENTES")
    
    # 🔍 FILTRO CORRIGIDO: Apenas pendências ATIVAS do usuário
    # Mesmo filtro, mas para SAIDA (solicitações) em vez de ENTRADA
    minhas_pendencias = [p for p in pendencias 
                        if p['usuario_id'] == usuario_logado['id']  # 👈 Do usuário logado
                        and p['tipo'] == 'SAIDA'                    # 👈 Apenas solicitações
                        and p['status'] == 'Pendente']              # 👈 APENAS ATIVAS!
    
    # 📭 VERIFICA SE NÃO HÁ PENDÊNCIAS
    if not minhas_pendencias:
        print("📭 Você não tem solicitações pendentes.")
        pausar()
        return
    
    # 📊 EXIBE A LISTA DE SOLICITAÇÕES ATIVAS
    print(f"📋 Suas Solicitações Pendentes ({len(minhas_pendencias)}):")
    print("-" * 80)
    print(f"{'ID':<4} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA':<16} {'STATUS':<12}")
    print("-" * 80)
    
    # 📋 PERCORRE E EXIBE CADA SOLICITAÇÃO ATIVA
    for pend in minhas_pendencias:
        print(f"{pend['id']:<4} {pend['produto_nome'][:18]:<20} "
              f"{pend['quantidade']:<12} {pend['data_solicitacao']:<16} {pend['status']:<12}")
    
    pausar()


# =============================================
# MÓDULO PARA ADMINISTRADORES
# =============================================

def listar_todas_pendencias():
    """
    LISTA TODAS AS PENDÊNCIAS - Para administradores (apenas ATIVAS)
    
    🎯 CONCEITO: Foco na Ação
    - Admin só vê pendências que precisam ser aprovadas/reprovadas
    - Pendências "excluídas" não aparecem (já foram resolvidas pelo usuário)
    - Interface mais limpa e eficiente
    """
    exibir_cabecalho("TODAS AS PENDÊNCIAS")
    
    # 🔍 FILTRO CORRIGIDO: Apenas pendências ATIVAS
    #Admin também só vê as ATIVAS para aprovação
    pendencias_pendentes = [p for p in pendencias if p['status'] == 'Pendente']
    
    # 📭 VERIFICA SE NÃO HÁ PENDÊNCIAS ATIVAS
    if not pendencias_pendentes:
        print("✅ Nenhuma pendência ativa no momento.")
        pausar()
        return
    
    # 📊 EXIBE A LISTA DE PENDÊNCIAS ATIVAS
    print(f"{'ID':<4} {'TIPO':<8} {'USUÁRIO':<20} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA':<16}")
    print("-" * 90)
    
    # 📋 PERCORRE E EXIBE CADA PENDÊNCIA ATIVA
    for pend in pendencias_pendentes:
        # 🎭 DEFINE EMOJI E TEXTO PARA O TIPO
        tipo = "🎁 ENTRADA" if pend['tipo'] == 'ENTRADA' else "📦 SAÍDA"
        
        # 🖨️ EXIBE A LINHA DA PENDÊNCIA
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
    """
    APROVAR/REPROVAR PENDÊNCIAS - Função principal dos administradores
    
    🔧 FLUXO CORRIGIDO:
    1. Mostra apenas pendências ATIVAS
    2. Permite aprovar/reprovar apenas ATIVAS
    3. Busca por ID apenas entre as ATIVAS
    """
    exibir_cabecalho("APROVAR/REPROVAR PENDÊNCIAS")
    
    # 🔍 FILTRO CORRIGIDO: Apenas pendências ATIVAS
    pendencias_pendentes = [p for p in pendencias if p['status'] == 'Pendente']
    
    # 📭 VERIFICA SE NÃO HÁ PENDÊNCIAS PARA APROVAR
    if not pendencias_pendentes:
        print("✅ Nenhuma pendência para aprovar no momento.")
        pausar()
        return
    
    # 📊 EXIBE A LISTA DE PENDÊNCIAS PARA APROVAÇÃO
    print("📋 Pendências Pendentes:")
    print("-" * 90)
    print(f"{'ID':<4} {'TIPO':<8} {'USUÁRIO':<20} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA':<16}")
    print("-" * 90)

    # 📋 LISTA PENDÊNCIAS ATIVAS (apenas as que podem ser aprovadas)
    for pend in pendencias_pendentes:
        tipo = "🎁 ENTRADA" if pend['tipo'] == 'ENTRADA' else "📦 SAÍDA"
        print(f"{pend['id']:<4} {tipo:<8} {pend['usuario_nome'][:18]:<20} {pend['produto_nome'][:18]:<20} "
              f"{pend['quantidade']:<12} {pend['data_solicitacao']:<16}")
    
    try:
        # 🎯 CAPTURA O ID DA PENDÊNCIA PARA PROCESSAR
        pendencia_id = int(input("\n📋 ID da pendência a aprovar/reprovar: "))
        acao = input("✅ Aprovar (a) ou ❌ Reprovar (r)? ").lower()
        
        # 🔍 BUSCA A PENDÊNCIA APENAS ENTRE AS ATIVAS
        #é buscado apenas entre pendências com status 'Pendente'
        # Isso evita que admin tente processar pendências "excluídas"
        pendencia = next((p for p in pendencias if p['id'] == pendencia_id and p['status'] == 'Pendente'), None)
        
        if pendencia:
            # 🎪 EXECUTA A AÇÃO SOLICITADA
            if acao == 'a':
                processar_aprovacao(pendencia)
            elif acao == 'r':
                processar_reprovacao(pendencia)
            else:
                print("❌ Ação inválida!")
                pausar()
        else:
            print("❌ Pendência não encontrada ou já processada!")
            pausar()
            
    except ValueError:
        # 🚨 TRATAMENTO DE ERRO PARA ENTRADA INVÁLIDA
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

def visualizar_estoque():
    """
    VISUALIZAR ESTOQUE ATUAL - Mostra apenas produtos ATIVOS
    """
    exibir_cabecalho("ESTOQUE ATUAL")
    
    # 🔍 FILTRO: Apenas produtos ATIVOS
    produtos_ativos = [p for p in produtos if p['ativo'] == True]
    
    if not produtos_ativos:
        print("📭 Nenhum produto no estoque.")
        pausar()
        return
    
    # 🚨 ALERTAS (apenas para produtos ATIVOS)
    produtos_baixo_estoque = [p for p in produtos_ativos if p['quantidade'] <= p['quantidade_minima']]
    produtos_proximos_vencer = [p for p in produtos_ativos if verificar_proximo_vencimento(p['data_validade'])]
    produtos_vencidos_ativos = [p for p in produtos_ativos if verificar_se_vencido(p['data_validade'])]
    
    # ⚠️ ALERTA DE PRODUTOS VENCIDOS AINDA ATIVOS
    if produtos_vencidos_ativos:
        print("🚨 PRODUTOS VENCIDOS NO ESTOQUE:")
        for produto in produtos_vencidos_ativos:
            print(f"   💀 {produto['nome']} - venceu em {produto['data_validade']} | Estoque: {produto['quantidade']} unidades")
        print()
    
    if produtos_baixo_estoque:
        print("⚠️  ALERTAS DE ESTOQUE BAIXO:")
        for produto in produtos_baixo_estoque:
            print(f"   📦 {produto['nome']} - apenas {produto['quantidade']} unidades")
        print()
    
    if produtos_proximos_vencer:
        print("⚠️  PRODUTOS PRÓXIMOS DO VENCIMENTO:")
        for produto in produtos_proximos_vencer:
            print(f"   ⏰ {produto['nome']} - vence em {produto['data_validade']}")
        print()
    
    # 📊 TABELA DE ESTOQUE ATIVO
    print(f"{'ID':<4} {'NOME':<20} {'CATEGORIA':<15} {'QUANTIDADE':<12} {'ESTOQUE':<10} {'VALIDADE':<12}")
    print("-" * 90)
    
    for produto in produtos_ativos:
        # 🎭 DEFINE STATUS DO ESTOQUE
        estoque_status = "🟢 OK" if produto['quantidade'] > produto['quantidade_minima'] else "🔴 BAIXO"
        
        # 🔍 VERIFICA SE ESTÁ VENCIDO (para destacar)
        if verificar_se_vencido(produto['data_validade']):
            estoque_status = "💀 VENCIDO"
            
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
    
    while True:  # Loop principal para permitir múltiplos acessos
        # Filtros de periodos
        print("📅 Filtrar por período:")
        print("1. 📊 Últimos 7 dias")
        print("2. 📈 Últimos 30 dias")
        print("3. 📋 Todo o histórico")
        print("4. 🏠 Voltar ao menu anterior")
        
        try: #verifica se input 'filtro' é valido
            filtro = int(input("\n📋 Escolha o período: "))
            limpar_tela()
            if filtro == 4:  # Opção para sair
                return
            
            hoje = datetime.datetime.now()
            movimentacoes_filtradas = []
            
            for mov in movimentacoes: # Percorre todas as movimentações para aplicar o filtro
                try:
                    #converte string para datetime
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
                continue  # Volta para o início do loop
            
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
            
            print("\n1. 🔄 Gerar outro relatório")
            print("2. 🔙 Voltar ao menu anterior")
            
            opcao = input("\n📋 Escolha uma opção: ")
            limpar_tela()
            if opcao == "2":
                return
            # Se escolher 1 ou qualquer outra coisa, continua no loop

        except ValueError:
            print("❌ Opção inválida!")
            pausar()

def gerar_relatorio_pendencias():
    """GERA RELATÓRIO DE PENDÊNCIAS EM PYTHON - Começa com relatório geral e permite filtrar"""
    exibir_cabecalho("RELATÓRIO DE PENDÊNCIAS")
    
    # Verifica se existem pendências no sistema
    if not pendencias:  # se não tiver pendencias
        print("📭 Nenhuma pendência registrada.")
        pausar()
        return
    
    # Loop principal para permitir que o administrador gere vários relatórios
    while True:
        # SEMPRE COMEÇA EXIBINDO O RELATÓRIO COMPLETO
        exibir_cabecalho("RELATÓRIO COMPLETO DE PENDÊNCIAS")
        
        # ESTATÍSTICAS GERAIS DO SISTEMA
        pendencias_pendentes = [p for p in pendencias if p['status'] == 'Pendente']
        pendencias_aprovadas = [p for p in pendencias if p['status'] == 'Aprovada']
        pendencias_reprovadas = [p for p in pendencias if p['status'] == 'Reprovada']
        
        # EXIBE O RESUMO ESTATÍSTICO COMPLETO
        print("📊 RESUMO GERAL DO SISTEMA:")
        print(f"   📋 Total de Pendências: {len(pendencias)}")
        print(f"   ⏳ Pendentes: {len(pendencias_pendentes)}")
        print(f"   ✅ Aprovadas: {len(pendencias_aprovadas)}")
        print(f"   ❌ Reprovadas: {len(pendencias_reprovadas)}")
        print("-" * 110)
        
        # EXIBE A TABELA COMPLETA COM TODAS AS PENDÊNCIAS
        print("📋 TODAS AS PENDÊNCIAS DO SISTEMA:")
        # Cabeçalho melhor alinhado
        print(f"{'ID':<3} {'STATUS':<12} {'TIPO':<9} {'USUÁRIO':<22} {'PRODUTO':<20} {'QTD':<5} {'DATA SOLIC.':<16} {'DATA PROC.':<12}")
        print("-" * 110)
        
        # PERCORRE E EXIBE TODAS AS PENDÊNCIAS
        for pend in pendencias:
            # Define o emoji e texto para o tipo de movimentação
            tipo = "🎁 ENTRADA" if pend['tipo'] == 'ENTRADA' else "📦 SAÍDA"
            
            # Define o emoji e texto para o status - usando abreviações para melhor alinhamento
            if pend['status'] == 'Pendente':
                status_text = "⏳ Pendente"
            elif pend['status'] == 'Aprovada':
                status_text = "✅ Aprovada"
            else:  # Reprovada
                status_text = "❌ Reprovada"
            
            # Obtém a data de processamento (se existir)
            data_processamento = pend.get('data_processamento', 'N/A')
            
            # Formata as datas para tamanho consistente
            data_solicitacao = pend['data_solicitacao'][:16]  # Mantém apenas DD/MM/AAAA HH:MM
            if data_processamento != 'N/A':
                data_processamento = data_processamento[:16]  # Mantém apenas DD/MM/AAAA HH:MM
            
            # Limita o tamanho dos textos para caber na tabela
            usuario_nome = pend['usuario_nome'][:20]  # Máximo 20 caracteres
            produto_nome = pend['produto_nome'][:18]  # Máximo 18 caracteres
            
            # Exibe a linha da tabela formatada com alinhamento melhorado
            print(f"{pend['id']:<3} {status_text:<12} {tipo:<9} {usuario_nome:<22} {produto_nome:<20} "
                  f"{pend['quantidade']:<5} {data_solicitacao:<16} {data_processamento:<12}")
        
        # MENU DE FILTROS
        print("\n" + "=" * 50)
        print("🎛️  FILTROS DISPONÍVEIS:")
        print("=" * 50)
        print("1. 🔍 Filtrar apenas Pendências Pendentes")
        print("2. ✅ Filtrar apenas Pendências Aprovadas")
        print("3. ❌ Filtrar apenas Pendências Reprovadas")
        print("4. 🏠 Voltar ao Menu de Relatórios")
        print("-" * 50)
        
        try:
            # Solicita a opção de filtro do usuário
            opcao_filtro = input("\n📋 Escolha um filtro ou opção: ").strip()
            
            # OPÇÃO 4: VOLTAR AO MENU ANTERIOR
            if opcao_filtro == '4':
                break
            
            # APLICA OS FILTROS CONFORME A OPÇÃO ESCOLHIDA
            elif opcao_filtro == '1':
                pendencias_filtradas = [p for p in pendencias if p['status'] == 'Pendente']
                titulo_filtro = "PENDÊNCIAS PENDENTES"
                
            elif opcao_filtro == '2':
                pendencias_filtradas = [p for p in pendencias if p['status'] == 'Aprovada']
                titulo_filtro = "PENDÊNCIAS APROVADAS"
                
            elif opcao_filtro == '3':
                pendencias_filtradas = [p for p in pendencias if p['status'] == 'Reprovada']
                titulo_filtro = "PENDÊNCIAS REPROVADAS"
                
            else:
                print("❌ Opção de filtro inválida!")
                pausar()
                continue
            
            # VERIFICA SE HÁ DADOS PARA O FILTRO APLICADO
            if not pendencias_filtradas:
                print(f"📭 Nenhuma pendência encontrada para o filtro '{titulo_filtro}'.")
                pausar()
                continue
            
            # EXIBE O RELATÓRIO FILTRADO
            exibir_cabecalho(f"RELATÓRIO FILTRADO - {titulo_filtro}")
            
            # ESTATÍSTICAS DO RELATÓRIO FILTRADO
            total_filtrado = len(pendencias_filtradas)
            entradas_filtradas = [p for p in pendencias_filtradas if p['tipo'] == 'ENTRADA']
            saidas_filtradas = [p for p in pendencias_filtradas if p['tipo'] == 'SAIDA']
            
            print(f"📊 RESUMO DO FILTRO:")
            print(f"   📋 Total: {total_filtrado} pendências")
            print(f"   🎁 Entradas: {len(entradas_filtradas)}")
            print(f"   📦 Saídas: {len(saidas_filtradas)}")
            print("-" * 110)
            
            # EXIBE A TABELA FILTRADA
            print(f"{'ID':<3} {'STATUS':<12} {'TIPO':<9} {'USUÁRIO':<22} {'PRODUTO':<20} {'QTD':<5} {'DATA SOLIC.':<16} {'DATA PROC.':<12}")
            print("-" * 110)
            
            for pend in pendencias_filtradas:
                tipo = "🎁 ENTRADA" if pend['tipo'] == 'ENTRADA' else "📦 SAÍDA"
                
                if pend['status'] == 'Pendente':
                    status_text = "⏳ Pendente"
                elif pend['status'] == 'Aprovada':
                    status_text = "✅ Aprovada"
                else:
                    status_text = "❌ Reprovada"
                
                data_processamento = pend.get('data_processamento', 'N/A')
                data_solicitacao = pend['data_solicitacao'][:16]
                if data_processamento != 'N/A':
                    data_processamento = data_processamento[:16]
                
                usuario_nome = pend['usuario_nome'][:20]
                produto_nome = pend['produto_nome'][:18]
                
                print(f"{pend['id']:<3} {status_text:<12} {tipo:<9} {usuario_nome:<22} {produto_nome:<20} "
                      f"{pend['quantidade']:<5} {data_solicitacao:<16} {data_processamento:<12}")
            
            # OPÇÕES DE CONTINUAÇÃO
            print("\n1. 🔄 Voltar ao Relatório Completo")
            print("2. 🏠 Voltar ao Menu de Relatórios")
            
            opcao_continuar = input("\n📋 Escolha uma opção: ").strip()
            
            if opcao_continuar == '2':
                break
            
        except Exception as e:
            print(f"❌ Erro ao processar filtro: {e}")
            pausar()

def gerar_relatorio_ranking_solicitacoes():
    """GERA RELATÓRIO DE RANKING DOS PRODUTOS MAIS SOLICITADOS - Apenas para administradores"""
    exibir_cabecalho("RANKING - PRODUTOS MAIS SOLICITADOS")
    
    # Verifica se existem movimentações de saída (solicitações aprovadas)
    solicitacoes_aprovadas = [m for m in movimentacoes if m['tipo'] == 'SAIDA']
    
    if not solicitacoes_aprovadas:
        print("📭 Nenhuma solicitação aprovada encontrada no sistema.")
        pausar()
        return
    
    # Dicionário para armazenar estatísticas por produto
    ranking_produtos = {}
    
    # Processa todas as solicitações aprovadas
    for solicitacao in solicitacoes_aprovadas:
        produto_id = solicitacao['produto_id']
        produto_nome = solicitacao['produto_nome']
        quantidade = solicitacao['quantidade']
        
        if produto_id in ranking_produtos:
            # Atualiza produto existente
            ranking_produtos[produto_id]['total_solicitado'] += quantidade
            ranking_produtos[produto_id]['quantidade_solicitacoes'] += 1
        else:
            # Adiciona novo produto ao ranking
            ranking_produtos[produto_id] = {
                'nome': produto_nome,
                'total_solicitado': quantidade,
                'quantidade_solicitacoes': 1
            }
    
    # Converte o dicionário para lista e ordena por total solicitado (decrescente)
    ranking_lista = list(ranking_produtos.values())
    ranking_lista.sort(key=lambda x: x['total_solicitado'], reverse=True)
    
    # Exibe o ranking
    print("-" * 80)
    print("🏆 RANKING DOS PRODUTOS MAIS SOLICITADOS:")
    print(f"{'POS':<4} {'PRODUTO':<30} {'TOTAL SOLICITADO':<16} {'QTD SOLICITAÇÕES':<18} {'MÉDIA POR PEDIDO':<16}")
    print("-" * 90)
    
    for i, produto in enumerate(ranking_lista[:15], 1):  # Top 15 produtos
        # Calcula a média por solicitação
        media_por_pedido = produto['total_solicitado'] / produto['quantidade_solicitacoes']
        
        # Define emoji para as primeiras posições
        if i == 1:
            posicao_emoji = "🥇"
        elif i == 2:
            posicao_emoji = "🥈" 
        elif i == 3:
            posicao_emoji = "🥉"
        else:
            posicao_emoji = f"{i}."
        
        print(f"{posicao_emoji:<4} {produto['nome'][:28]:<30} "
              f"{produto['total_solicitado']:<16} {produto['quantidade_solicitacoes']:<18} "
              f"{media_por_pedido:.1f}")
    
    # Se houver mais de 15 produtos, mostra quantos ficaram de fora
    if len(ranking_lista) > 15:
        print(f"\n📋 ... e mais {len(ranking_lista) - 15} produtos no ranking completo")
    
    # Análise adicional - produtos com maior frequência de solicitação
    print(f"\n📈 ANÁLISE ADICIONAL:")
    
    # Produto com maior quantidade total solicitada
    if ranking_lista:
        produto_mais_solicitado = ranking_lista[0]
        print(f"   🏅 Produto mais solicitado: {produto_mais_solicitado['nome']}")
        print(f"      Total: {produto_mais_solicitado['total_solicitado']} unidades")
    
    # Produto com maior média por pedido
    ranking_media = sorted(ranking_lista, key=lambda x: x['total_solicitado'] / x['quantidade_solicitacoes'], reverse=True)
    if ranking_media:
        produto_maior_media = ranking_media[0]
        media = produto_maior_media['total_solicitado'] / produto_maior_media['quantidade_solicitacoes']
        print(f"   📊 Produto com maior média por pedido: {produto_maior_media['nome']}")
        print(f"      Média: {media:.1f} unidades por solicitação")
    
    # Produto mais frequente (mais solicitações)
    ranking_frequencia = sorted(ranking_lista, key=lambda x: x['quantidade_solicitacoes'], reverse=True)
    if ranking_frequencia:
        produto_mais_frequente = ranking_frequencia[0]
        print(f"   🔄 Produto mais frequente: {produto_mais_frequente['nome']}")
        print(f"      {produto_mais_frequente['quantidade_solicitacoes']} solicitações")
    
    pausar()

def menu_relatorios():
    """MENU DE RELATÓRIOS EM PYTHON"""
    while True:
        exibir_cabecalho("RELATÓRIOS")
        # menu simples para escolha
        print("1. 📊 Relatório de Estoque")
        print("2. 📈 Relatório de Movimentações")
        print("3. 📋 Relatório de Pendências")
        print("4. 🏆 Ranking de Produtos Mais Solicitados")
        print("5. 🏠 Voltar")
        
        opcao = input("\n📋 Escolha uma opção: ")
        
        if opcao == '1':
            gerar_relatorio_estoque()
        elif opcao == '2':
            gerar_relatorio_movimentacoes()
        elif opcao == '3':
            gerar_relatorio_pendencias()
        elif opcao == '4': 
            gerar_relatorio_ranking_solicitacoes()
        elif opcao == '5':
            break
        else:
            print("❌ Opção inválida!")
            pausar()

# =============================================
# FUNÇÕES PARA EDITAR PENDÊNCIAS
# =============================================

def editar_pendencia_doador(pendencia):
    """
    EDITAR PENDÊNCIA DE DOAÇÃO - Para doadores
    Permite que o doador modifique os dados de uma doação pendente
    """
    exibir_cabecalho("EDITAR DOAÇÃO PENDENTE")
    
    print(f"📝 Editando Doação Pendente - ID: {pendencia['id']}")
    print("-" * 50)
    
    # 🔍 EXIBIÇÃO DOS DADOS ATUAIS
    print("📋 Dados atuais:")
    print(f"📦 Nome do produto: {pendencia['produto_nome']}")
    print(f"📄 Descrição: {pendencia.get('produto_descricao', 'Nenhuma')}")
    print(f"🏷️  Categoria: {pendencia.get('produto_categoria', 'Nenhuma')}")
    print(f"⚖️  Peso: {pendencia.get('produto_peso', 0)} kg")
    print(f"📊 Quantidade: {pendencia['quantidade']}")
    print(f"📅 Data de validade: {pendencia.get('produto_validade', 'Não informada')}")
    print("-" * 50)
    
    # ✏️ COLETA DE NOVOS DADOS
    print("📝 Digite os novos dados (deixe em branco para manter o valor atual):")
    
    novo_nome = input(f"📦 Novo nome do produto [{pendencia['produto_nome']}]: ").strip()
    nova_descricao = input(f"📄 Nova descrição [{pendencia.get('produto_descricao', '')}]: ").strip()
    nova_categoria = input(f"🏷️  Nova categoria [{pendencia.get('produto_categoria', '')}]: ").strip()
    novo_peso = input(f"⚖️  Novo peso (kg) [{pendencia.get('produto_peso', 0)}]: ").strip()
    nova_quantidade = input(f"📊 Nova quantidade [{pendencia['quantidade']}]: ").strip()
    nova_validade = input(f"📅 Nova data de validade (DD/MM/AAAA) [{pendencia.get('produto_validade', '')}]: ").strip()
    
    # 🔄 APLICAÇÃO DAS ALTERAÇÕES
    alteracoes = False
    
    if novo_nome and novo_nome != pendencia['produto_nome']:
        pendencia['produto_nome'] = novo_nome
        alteracoes = True
        print("✅ Nome do produto atualizado!")
    
    if nova_descricao != pendencia.get('produto_descricao', ''):
        pendencia['produto_descricao'] = nova_descricao
        alteracoes = True
        print("✅ Descrição atualizada!")
    
    if nova_categoria and nova_categoria != pendencia.get('produto_categoria', ''):
        pendencia['produto_categoria'] = nova_categoria
        alteracoes = True
        print("✅ Categoria atualizada!")
    
    # 🎯 VALIDAÇÃO DE CAMPOS NUMÉRICOS
    if novo_peso:
        try:
            novo_peso_float = float(novo_peso)
            if novo_peso_float != pendencia.get('produto_peso', 0):
                pendencia['produto_peso'] = novo_peso_float
                alteracoes = True
                print("✅ Peso atualizado!")
        except ValueError:
            print("❌ Peso inválido! Mantendo valor anterior.")
    
    if nova_quantidade:
        try:
            nova_quantidade_int = int(nova_quantidade)
            if nova_quantidade_int != pendencia['quantidade']:
                pendencia['quantidade'] = nova_quantidade_int
                alteracoes = True
                print("✅ Quantidade atualizada!")
        except ValueError:
            print("❌ Quantidade inválida! Mantendo valor anterior.")
    
    if nova_validade and nova_validade != pendencia.get('produto_validade', ''):
        pendencia['produto_validade'] = nova_validade
        alteracoes = True
        print("✅ Data de validade atualizada!")
    
    # 💾 SALVAMENTO E REGISTRO DE MODIFICAÇÃO
    if alteracoes:
        pendencia['data_modificacao'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        salvar_dados()
        print(f"\n🎉 Doação atualizada com sucesso!")
        print(f"📅 Última modificação: {pendencia['data_modificacao']}")
    else:
        print(f"\nℹ️  Nenhuma alteração foi realizada.")
    
    pausar()

def editar_pendencia_solicitante(pendencia):
    """
    EDITAR PENDÊNCIA DE SOLICITAÇÃO - Para solicitantes
    Permite que o solicitante altere a quantidade solicitada
    """
    exibir_cabecalho("EDITAR SOLICITAÇÃO PENDENTE")
    
    print(f"📝 Editando Solicitação Pendente - ID: {pendencia['id']}")
    print("-" * 50)
    
    # 📊 CONTEXTUALIZAÇÃO COM DADOS ATUAIS
    print("📋 Dados atuais:")
    print(f"📦 Produto: {pendencia['produto_nome']}")
    print(f"📊 Quantidade solicitada: {pendencia['quantidade']}")
    print("-" * 50)
    
    # 🔍 VERIFICAÇÃO DE ESTOQUE
    produto = next((p for p in produtos if p['id'] == pendencia['produto_id']), None)
    if produto:
        print(f"📦 Estoque disponível: {produto['quantidade']} unidades")
        print("-" * 50)
    
    # ✏️ COLETA DA NOVA QUANTIDADE
    print("📝 Digite os novos dados (deixe em branco para manter o valor atual):")
    nova_quantidade = input(f"📊 Nova quantidade desejada [{pendencia['quantidade']}]: ").strip()
    
    # 🔄 PROCESSAMENTO DA ALTERAÇÃO
    alteracoes = False
    
    if nova_quantidade:
        try:
            nova_quantidade_int = int(nova_quantidade)
            
            # 🚨 VALIDAÇÃO DE REGRA DE NEGÓCIO
            if produto and nova_quantidade_int > produto['quantidade']:
                print(f"❌ Quantidade solicitada ({nova_quantidade_int}) maior que estoque disponível ({produto['quantidade']})!")
                pausar()
                return
            
            # ✅ APLICA A ALTERAÇÃO SE VÁLIDA
            if nova_quantidade_int != pendencia['quantidade']:
                pendencia['quantidade'] = nova_quantidade_int
                alteracoes = True
                print("✅ Quantidade atualizada!")
        except ValueError:
            print("❌ Quantidade inválida! Mantendo valor anterior.")
    
    # 💾 SALVAMENTO COM REGISTRO
    if alteracoes:
        pendencia['data_modificacao'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        salvar_dados()
        print(f"\n🎉 Solicitação atualizada com sucesso!")
        print(f"📅 Última modificação: {pendencia['data_modificacao']}")
    else:
        print(f"\nℹ️  Nenhuma alteração foi realizada.")
    
    pausar()

def excluir_pendencia(pendencia):
    """
    "EXCLUIR" PENDÊNCIA - Soft Delete com experiência de exclusão
    
    O usuário acha que está excluindo permanentemente,
    mas está apenas marcando como desativada (Soft Delete)
    """
    exibir_cabecalho("EXCLUIR PENDÊNCIA")
    
    print(f"🗑️  Excluindo Pendência - ID: {pendencia['id']}")
    print("-" * 50)
    
    # Mostra o que será "excluído"
    if pendencia['tipo'] == 'ENTRADA':
        print(f"🎁 Doação: {pendencia['produto_nome']}")
        print(f"📊 Quantidade: {pendencia['quantidade']}")
    else:
        print(f"📦 Solicitação: {pendencia['produto_nome']}")
        print(f"📊 Quantidade: {pendencia['quantidade']}")
    
    print(f"📅 Data de solicitação: {pendencia['data_solicitacao']}")
    print("-" * 50)
    
    # Confirmação dramática
    print("\n⚠️  ATENÇÃO: Esta operação não pode ser desfeita!")
    confirmar = input("\n❓ Confirmar exclusão? (digite 'CONFIRMAR'): ").strip()
    
    if confirmar.upper() == 'CONFIRMAR':
        # 🔄 SOFT DELETE - apenas muda o status
        pendencia['status'] = 'Desativada'
        pendencia['data_exclusao'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        pendencia['excluido_por'] = usuario_logado['nome']
        
        salvar_dados()
        
        # Feedback de "exclusão bem-sucedida"
        print(f"\n✅ Pendência excluída com sucesso!")
        print(f"📛 Registro removido do sistema")
        print(f"⏰ Data da exclusão: {pendencia['data_exclusao']}")
    else:
        print(f"\n❌ Exclusão cancelada.")
    
    pausar()

def recuperar_pendencias_excluidas():
    """
    RECUPERAR PENDÊNCIAS "EXCLUÍDAS" - Apenas para administradores
    Esta função mostra a "parte oculta" do Soft Delete
    Enquanto usuários comuns acham que excluíram, administradores podem ver tudo
    """
    exibir_cabecalho("PENDÊNCIAS EXCLUÍDAS - ÁREA ADMINISTRATIVA")
    
    # 🔍 BUSCA APENAS PENDÊNCIAS DESATIVADAS (as "excluídas")
    pendencias_excluidas = [p for p in pendencias if p['status'] == 'Desativada']
    
    if not pendencias_excluidas:
        print("📭 Nenhuma pendência excluída encontrada.")
        pausar()
        return
    
    print("🔍 PENDÊNCIAS EXCLUÍDAS DO SISTEMA:")
    print("   (Esta área é restrita a administradores)")
    print("-" * 100)
    print(f"{'ID':<4} {'TIPO':<8} {'USUÁRIO':<20} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA EXCLUSÃO':<16}")
    print("-" * 100)
    
    for pend in pendencias_excluidas:
        tipo = "🎁 DOAÇÃO" if pend['tipo'] == 'ENTRADA' else "📦 SOLICITAÇÃO"
        print(f"{pend['id']:<4} {tipo:<8} {pend['usuario_nome'][:18]:<20} {pend['produto_nome'][:18]:<20} "
              f"{pend['quantidade']:<12} {pend.get('data_exclusao', 'N/A')[:16]:<16}")
    
    pausar()

def gerenciar_minhas_pendencias_doador():
    """
    GERENCIA PENDÊNCIAS DO DOADOR - Editar/Excluir
    """
    exibir_cabecalho("GERENCIAR MINHAS DOAÇÕES")
    
    # 🔍 FILTRO: Apenas pendências ATIVAS do usuário
    minhas_pendencias = [p for p in pendencias 
                        if p['usuario_id'] == usuario_logado['id'] 
                        and p['tipo'] == 'ENTRADA' 
                        and p['status'] == 'Pendente']
    
    if not minhas_pendencias:
        print("📭 Você não tem doações ativas para gerenciar.")
        pausar()
        return
    
    # 📋 LISTA APENAS PENDÊNCIAS ATIVAS
    print("🎁 SUAS DOAÇÕES ATIVAS:")
    print(f"{'ID':<4} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA':<16} {'MODIFICAÇÃO':<16}")
    print("-" * 80)
    
    for pend in minhas_pendencias:
        data_modificacao = pend.get('data_modificacao', 'Nunca')
        print(f"{pend['id']:<4} {pend['produto_nome'][:18]:<20} "
              f"{pend['quantidade']:<12} {pend['data_solicitacao']:<16} {data_modificacao[:16]:<16}")
    
    try:
        pendencia_id = int(input("\n📋 ID da pendência para gerenciar: "))
        pendencia = next((p for p in minhas_pendencias if p['id'] == pendencia_id), None)
        
        if pendencia:
            print(f"\n🎛️  Opções para Doação ID {pendencia_id}:")
            print("1. ✏️  Editar Doação")
            print("2. 🗑️  Excluir Doação")
            print("3. 🔙 Voltar")
            
            opcao = input("\n📋 Escolha uma opção: ")
            
            if opcao == '1':
                editar_pendencia_doador(pendencia)
            elif opcao == '2':
                excluir_pendencia(pendencia)
            elif opcao == '3':
                return
            else:
                print("❌ Opção inválida!")
                pausar()
        else:
            print("❌ Pendência não encontrada ou não pertence a você!")
            pausar()
            
    except ValueError:
        print("❌ Por favor, digite um ID válido!")
        pausar()

def gerenciar_minhas_pendencias_solicitante():
    """
    GERENCIA PENDÊNCIAS DO SOLICITANTE - Editar/Excluir
    """
    exibir_cabecalho("GERENCIAR MINHAS SOLICITAÇÕES")
    
    # 🔍 FILTRO: Apenas pendências ATIVAS do usuário
    minhas_pendencias = [p for p in pendencias 
                        if p['usuario_id'] == usuario_logado['id'] 
                        and p['tipo'] == 'SAIDA' 
                        and p['status'] == 'Pendente']
    
    if not minhas_pendencias:
        print("📭 Você não tem solicitações ativas para gerenciar.")
        pausar()
        return
    
    # 📋 LISTA APENAS SOLICITAÇÕES ATIVAS
    print("📋 SUAS SOLICITAÇÕES ATIVAS:")
    print(f"{'ID':<4} {'PRODUTO':<20} {'QUANTIDADE':<12} {'DATA':<16} {'MODIFICAÇÃO':<16}")
    print("-" * 80)
    
    for pend in minhas_pendencias:
        data_modificacao = pend.get('data_modificacao', 'Nunca')
        print(f"{pend['id']:<4} {pend['produto_nome'][:18]:<20} "
              f"{pend['quantidade']:<12} {pend['data_solicitacao']:<16} {data_modificacao[:16]:<16}")
    
    try:
        pendencia_id = int(input("\n📋 ID da pendência para gerenciar: "))
        pendencia = next((p for p in minhas_pendencias if p['id'] == pendencia_id), None)
        
        if pendencia:
            print(f"\n🎛️  Opções para Solicitação ID {pendencia_id}:")
            print("1. ✏️  Editar Solicitação")
            print("2. 🗑️  Excluir Solicitação")
            print("3. 🔙 Voltar")
            
            opcao = input("\n📋 Escolha uma opção: ")
            
            if opcao == '1':
                editar_pendencia_solicitante(pendencia)
            elif opcao == '2':
                excluir_pendencia(pendencia)
            elif opcao == '3':
                return
            else:
                print("❌ Opção inválida!")
                pausar()
        else:
            print("❌ Pendência não encontrada ou não pertence a você!")
            pausar()
            
    except ValueError:
        print("❌ Por favor, digite um ID válido!")
        pausar()

# =============================================
# MÓDULO SOBRE VENCIMENTO
# =============================================

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

def verificar_produtos_vencidos():
    """VERIFICA PRODUTOS JÁ VENCIDOS"""
    produtos_vencidos = []
    hoje = datetime.datetime.now()
    
    for produto in produtos:
        try:
            data_validade = datetime.datetime.strptime(produto['data_validade'], "%d/%m/%Y")
            if data_validade < hoje:  # Produtos com data anterior à atual
                produtos_vencidos.append(produto)
        except:
            continue
    
    return produtos_vencidos

def verificar_se_vencido(data_validade):
    """
    VERIFICA SE PRODUTO ESTÁ VENCIDO - Função auxiliar
    """
    try:
        # 📅 CONVERTE STRING PARA DATA
        data_validade_obj = datetime.datetime.strptime(data_validade, "%d/%m/%Y")
        hoje = datetime.datetime.now()
        
        # 🔍 COMPARA AS DATAS
        return data_validade_obj < hoje  # True se vencido
        
    except ValueError:
        # 🚨 SE HOUVER ERRO NA CONVERSÃO, CONSIDERA NÃO VENCIDO
        return False

def verificar_proximo_vencimento(data_validade):
    """
    VERIFICA SE PRODUTO ESTÁ PRÓXIMO DO VENCIMENTO - Função auxiliar
    """
    try:
        data_validade_obj = datetime.datetime.strptime(data_validade, "%d/%m/%Y")
        hoje = datetime.datetime.now()
        dias_para_vencer = (data_validade_obj - hoje).days
        
        return 0 <= dias_para_vencer <= 30  # True se vencer em até 30 dias
        
    except ValueError:
        return False

def remover_produtos_vencidos():
    """
    "REMOVER" PRODUTOS VENCIDOS - Soft Delete para produtos vencidos
    
    🎯 CONCEITO: Preservação de Dados Históricos
    - Mantemos registro de todos os produtos, mesmo os vencidos
    - Podemos gerar relatórios de produtos descartados
    - Temos controle de estoque histórico completo
    """
    exibir_cabecalho("REMOVER PRODUTOS VENCIDOS")
    
    # 🔍 IDENTIFICA PRODUTOS VENCIDOS (apenas os ATIVOS)
    produtos_vencidos = [p for p in produtos 
                        if p['ativo'] == True  # 👈 Apenas produtos ativos
                        and verificar_se_vencido(p['data_validade'])]
    
    if not produtos_vencidos:
        print("✅ Nenhum produto vencido encontrado!")
        pausar()
        return
    
    # 📊 EXIBE PRODUTOS VENCIDOS ENCONTRADOS
    print(f"🚨 Encontrados {len(produtos_vencidos)} produtos vencidos:")
    print("-" * 80)
    print(f"{'ID':<4} {'PRODUTO':<20} {'QUANTIDADE':<12} {'VALIDADE':<12} {'STATUS':<10}")
    print("-" * 80)
    
    for produto in produtos_vencidos:
        print(f"{produto['id']:<4} {produto['nome'][:18]:<20} "
              f"{produto['quantidade']:<12} {produto['data_validade']:<12} 💀 VENCIDO")
    
    # ⚠️ CONFIRMAÇÃO DE "REMOÇÃO"
    print(f"\n⚠️  ATENÇÃO: {len(produtos_vencidos)} produtos serão marcados como vencidos.")
    print("   Eles não aparecerão mais no estoque ativo, mas ficarão no histórico.")
    
    confirmar = input("\n❓ Confirmar remoção? (digite 'CONFIRMAR'): ").strip()
    
    if confirmar.upper() == 'CONFIRMAR':
        # 🔄 SOFT DELETE - Marca produtos como inativos
        produtos_removidos = 0
        for produto in produtos_vencidos:
            produto['ativo'] = False  # 👈 Soft Delete - marca como inativo
            produto['data_remocao'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            produto['removido_por'] = usuario_logado['nome']
            produto['motivo_remocao'] = 'Vencimento'
            produtos_removidos += 1
        
        salvar_dados()
        
        # ✅ FEEDBACK DE SUCESSO
        print(f"\n✅ {produtos_removidos} produtos vencidos removidos com sucesso!")
        print(f"📅 Data da remoção: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"👤 Removido por: {usuario_logado['nome']}")
        print(f"📊 Os produtos foram movidos para o histórico de vencidos.")
        
    else:
        print(f"\n❌ Operação cancelada. Os produtos permanecem no estoque.")
    
    pausar()

def gerar_relatorio_vencidos():
    """
    GERAR RELATÓRIO DE PRODUTOS VENCIDOS - Para administradores
    
    📈 Dados importantes para gestão:
    - Volume de produtos perdidos
    - Produtos com maior índice de vencimento
    - Controle de custos
    """
    exibir_cabecalho("RELATÓRIO DE PRODUTOS VENCIDOS")
    
    # 🔍 PRODUTOS VENCIDOS (inativos)
    produtos_vencidos = [p for p in produtos 
                        if p['ativo'] == False 
                        and p.get('motivo_remocao') == 'Vencimento']
    
    if not produtos_vencidos:
        print("📭 Nenhum produto vencido no histórico.")
        pausar()
        return
    
    # 📊 ESTATÍSTICAS DETALHADAS
    total_produtos = len(produtos_vencidos)
    total_unidades = sum(p['quantidade'] for p in produtos_vencidos)
    
    # 🏷️ AGRUPAMENTO POR CATEGORIA
    categorias = {}
    for produto in produtos_vencidos:
        cat = produto['categoria']
        if cat in categorias:
            categorias[cat] += produto['quantidade']
        else:
            categorias[cat] = produto['quantidade']
    
    print("📊 RELATÓRIO COMPLETO DE PRODUTOS VENCIDOS")
    print("=" * 50)
    print(f"📦 Total de produtos vencidos: {total_produtos}")
    print(f"🔢 Total de unidades perdidas: {total_unidades}")
    print(f"📅 Período: Todos os registros históricos")
    print("=" * 50)
    
    # 📈 DISTRIBUIÇÃO POR CATEGORIA
    if categorias:
        print("\n🏷️  DISTRIBUIÇÃO POR CATEGORIA:")
        for categoria, quantidade in categorias.items():
            percentual = (quantidade / total_unidades) * 100
            print(f"   📋 {categoria}: {quantidade} unidades ({percentual:.1f}%)")
    
    # 📋 DETALHES DOS PRODUTOS
    print(f"\n📋 DETALHES DOS PRODUTOS VENCIDOS:")
    print(f"{'PRODUTO':<20} {'CATEGORIA':<15} {'QUANTIDADE':<12} {'DATA VALIDADE':<14} {'DATA REMOÇÃO':<14}")
    print("-" * 80)
    
    for produto in produtos_vencidos:
        print(f"{produto['nome'][:18]:<20} {produto['categoria'][:13]:<15} "
              f"{produto['quantidade']:<12} {produto['data_validade']:<14} {produto.get('data_remocao', 'N/A')[:14]:<14}")
    
    pausar()

def visualizar_historico_vencidos():
    """
    VISUALIZAR HISTÓRICO DE PRODUTOS VENCIDOS - Para administradores
    
    📊 Benefícios do Soft Delete para produtos:
    - Controle de perdas por vencimento
    - Relatórios de gestão de estoque
    - Rastreabilidade completa
    """
    exibir_cabecalho("HISTÓRICO DE PRODUTOS VENCIDOS")
    
    # 🔍 FILTRA PRODUTOS MARCADOS COMO INATIVOS POR VENCIMENTO
    produtos_vencidos = [p for p in produtos 
                        if p['ativo'] == False 
                        and p.get('motivo_remocao') == 'Vencimento']
    
    if not produtos_vencidos:
        print("📭 Nenhum produto vencido no histórico.")
        pausar()
        return
    
    # 📊 ESTATÍSTICAS
    total_unidades = sum(p['quantidade'] for p in produtos_vencidos)
    total_produtos = len(produtos_vencidos)
    
    print(f"📊 HISTÓRICO DE VENCIDOS - {total_produtos} produtos ({total_unidades} unidades)")
    print("-" * 100)
    print(f"{'ID':<4} {'PRODUTO':<20} {'QUANTIDADE':<12} {'VALIDADE':<12} {'DATA REMOÇÃO':<16} {'REMOVIDO POR':<15}")
    print("-" * 100)
    
    # 📋 LISTA PRODUTOS VENCIDOS
    for produto in produtos_vencidos:
        print(f"{produto['id']:<4} {produto['nome'][:18]:<20} "
              f"{produto['quantidade']:<12} {produto['data_validade']:<12} "
              f"{produto.get('data_remocao', 'N/A')[:16]:<16} {produto.get('removido_por', 'Sistema')[:13]:<15}")
    
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
        print("3. 🛠️  Gerenciar Minhas Doações")
        print("4. 📊 Meu Histórico de Doações")
        print("5. 👤 Meu Perfil")
        print("6. 🎭 Trocar de Usuario")
        print("7. 🚪 Sair")
        

        opcao = input("\n📋 Escolha uma opção: ")
        
        if opcao == '1':
            registrar_doacao_pendente()
        elif opcao == '2':
            minhas_doacoes_pendentes()
        elif opcao == '3':  
            gerenciar_minhas_pendencias_doador()
        elif opcao == '4':
            meu_historico_doacoes()
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
        print("4. 🛠️  Gerenciar Minhas Solicitações")  
        print("5. 👤 Meu Perfil")
        print("6. 🎭 Trocar de Usuario")
        print("7. 🚪 Sair")
        
        opcao = input("\n📋 Escolha uma opção: ")
        
        if opcao == '1':
            visualizar_produtos_disponiveis()
        elif opcao == '2':
            nova_solicitacao_pendente()
        elif opcao == '3':
            minhas_solicitacoes_pendentes()
        elif opcao == '4':
            gerenciar_minhas_pendencias_solicitante()
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

def menu_administrador():
    """MENU PRINCIPAL PARA ADMINISTRADORES"""
    while True:
        exibir_cabecalho("MENU PRINCIPAL")
        print(f"👤 Usuário: {usuario_logado['nome']} | Perfil: {usuario_logado['perfil']}")
        print("-" * 40)
        
        print("1. ✅ Aprovar/Reprovar Pendências")
        print("2. 📦 Visualizar Estoque")
        print("3. 🗑️  Remover Produtos Vencidos")  
        print("4. 📊 Relatórios")
        print("5. 👥 Gerenciar Usuários")
        print("6. 🔍 Ver Pendências Excluídas")
        print("7. 💀 Histórico de Produtos Vencidos")
        print("8. 👤 Meu Perfil")
        print("9. 🎭 Trocar de Usuario")    
        print("10. 🚪 Sair")
        
        opcao = input("\n📋 Escolha uma opção: ")
        
        if opcao == '1':
            menu_aprovar_pendencias()
        elif opcao == '2':
            visualizar_estoque()
        elif opcao == '3':  
            remover_produtos_vencidos()
        elif opcao == '4':
            menu_relatorios()
        elif opcao == '5':
            menu_gerenciar_usuarios()
        elif opcao == '6':
            recuperar_pendencias_excluidas()
        elif opcao == '7':
            visualizar_historico_vencidos()
        elif opcao == '8':
            menu_meu_perfil()
        elif opcao == '9':
            if trocar_usuario():
                return True
        elif opcao == '10':
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

