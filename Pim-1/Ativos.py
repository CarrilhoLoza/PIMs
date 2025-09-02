import os
import locale
#informa o Local da Moeda "pt_BR"
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

lista_ativos = []

def cadastrar_ativo():

   # Verifica se ID do ativo ja exite
    id = input('ID do Ativo: ')
    for ativo in lista_ativos:
        while ativo['Id'] == id:
                print('-'*55)
                input('❌ ID já existente \npressione enter para tentar outro ID...')
                os.system('cls')
                id = input('ID do Ativo: ')
                
   # Coleta dados
    descricao = input('Descrição do Ativo: ')
    valor_unitario = round(float(input('Valor Unitario do Ativo: ')), 2)
    quantidade = int(input('Quantidade de Ativos: '))
    nota_fiscal = input('Numero da Nota Fiscal: ')
    status = input('A Situação (Ativo ou Inativo) é: ').lower()
    
    #Filtra a variavel Status para que so receba o valor ativo e inativo
    while status not in ['ativo','inativo',]:
        print('-'*55 ,'\n❌ Status inválido. Digite apenas "Ativo" ou "Inativo:')
        status = input().lower()


    # Calcula o valor total
    valor_total = round(quantidade * valor_unitario, 2)

    # Cria o dicionário com a ordem desejada
    ativo = {
        'Id': id,
        'Descrição': descricao,
        'Quantidade': quantidade,
        'Valor Unitario': valor_unitario,
        'Valor Total': valor_total,
        'Nota Fiscal': nota_fiscal,
        'Status': status
    }

    # Adiciona à lista
    lista_ativos.append(ativo)
    print('-'*40)
    print('Ativo Cadastrado com Sucesso')

def listar_ativos():
    # verifica se a lista está vazia, senão percorrerá a lista
    if not lista_ativos:
        print("Nenhum ativo cadastrado.")

    else:
        #percorre a lista
        print('-'*30)
        for ativo in lista_ativos: 
            #gera uma tabela de cada dicionario existente na lista
            for chave,valor in ativo.items():
                #se forem valores monetarios serão convertidos automaticamente pelo If, se não, apenas exibidos pelo else
                if chave in ['Valor Unitario', 'Valor Total']:
                    print(f'{chave}: {locale.currency(valor, grouping=True)}')
                else:
                    print(f'{chave}: {valor}')
            print('-'*30)

def consultar_ativo():
    # verifica se a lista está vazia, senão executará normalmente
    if not lista_ativos:
        print('Não existem Ativos para consultar')

    else:
        buscar_id= input('Digite o ID do Ativo: ')  
        print('~'*35)

        for ativo in lista_ativos:
            if ativo['Id'] == buscar_id:    #sistema de busca, o for percorre a lista e se id = a busca que fiz, encontra o dicionario certo e imprime ele na tela
                for chave,valor in ativo.items():
                    if chave in ['Valor Unitario', 'Valor Total']:
                        print(f'{chave}: {locale.currency(valor, grouping=True)}')
                    else:
                        print(f'{chave}: {valor}')
                print('~'*35)
                break

        else:
            os.system('cls')
            print('O Ativo não existe \n')  #se eu colocar uma Id ainda não registrada caira nesse else
           
def gerar_relatorios():
    # verifica se a lista está vazia, senão executara normalmente
    if not lista_ativos:
        print('não existem Ativos para gerar relatorios')

    else:
        print('relatorios de Ativos:')
        print('~' * 20)
        print('-' * 20)

        for ativo in lista_ativos:    #imprime relatorios na tela
            print(f' ID:{ativo["Id"]} \n Descrição:{ativo["Descrição"]} \n Status:{ativo["Status"]}')
            print('-' * 20)
        print('~' * 20)

def alternar_ativo_inativo():
    # verifica se a lista está vazia, senão executara normalmente
    if not lista_ativos:
        print('não existem Ativos')

    else:

        #faz um relatorio para ajudar o usuario a ver os Id's
        print('-' * 20)
        for ativo in lista_ativos:
            print(f' ID:{ativo["Id"]} \n Descrição:{ativo["Descrição"]} \n Status:{ativo["Status"]}')
            print('-' * 20)

        #faz busca do dicionario especifico
        buscar_id = input('Digite o ID do ativo para alterar status: ')  
        os.system('cls')
        for ativo in lista_ativos:
            
            if ativo['Id'] == buscar_id:    #dentro do dicionario que a busca foi localizada altera os status de ativo para inativo e vice versa
                if ativo['Status'] == 'ativo':
                    ativo['Status'] = 'inativo'
                    print(f'O Status do ID {ativo['Id']} foi alterado para inativo')
                    break
                elif ativo['Status'] == 'inativo':
                    ativo['Status'] = 'ativo'
                    print(f'O Status do ID {ativo['Id']} foi alterado para ativo')
                    break
        else:
            print('o ativo não existe ') #se não localizar o ID (passar pelo If) cai direto  no else

def remover_ativo():
    # verifica se a lista está vazia, senão executara normalmente
    if not lista_ativos:
        print('não há ativos para remover')
    else:
        #faz um relatorio para ajudar o usuario a ver os Id's
        print('-' * 20)
        for ativo in lista_ativos:
            print(f' ID:{ativo["Id"]} \n Descrição:{ativo["Descrição"]} \n Status:{ativo["Status"]}')
            print('-' * 20)
        #seleciona qual o ID do ativo a remover
        escolha = input('qual ID do ativo que você deseja remover? \nID:')

        for ativo in lista_ativos:
            if escolha == ativo['Id']:
                lista_ativos.remove(ativo)
                os.system('cls')
                print('Ativo removido com Sucesso')

            elif escolha != ativo['Id']:
                os.system('cls')
                print('esse ID não está registrado')

def menu():
    #while para smpre que sair de uma função retornar aqui
    while True:
        os.system('cls')
        print('~'*25)
        print('1 - Cadastrar Ativo')
        print('2 - Listar Ativos')
        print('3 - Consultar Ativo')
        print('4 - Gerar Relatorios')
        print('5 - Tornar Ativo/Inativo')
        print('6 - Remover Ativo')
        print('7 - Sair')
        print('~'*25)

        escolha = int(input('Digite o numero de sua escolha: '))

        if escolha == 1:
            os.system('cls')
            cadastrar_ativo()
            input('\nPressione Enter para voltar ao menu...')

        elif escolha == 2:
            os.system('cls')
            listar_ativos()
            input('\nPressione Enter para voltar ao menu...')

        elif escolha == 3:
            os.system('cls')
            consultar_ativo()
            input('\nPressione Enter para voltar ao menu...')

        elif escolha == 4:
            os.system('cls')
            gerar_relatorios()
            input('\nPressione Enter para voltar ao menu...')

        elif escolha == 5:
            os.system('cls')
            alternar_ativo_inativo()
            input('\nPressione Enter para voltar ao menu...')

        elif escolha == 6:
            os.system('cls')
            remover_ativo()
            input('\nPressione Enter para voltar ao menu...')

            
        elif escolha == 7:
            os.system('cls')
            print('Encerrando programa... \n')
            break

        else:
            os.system('cls')
            print('Escolha Invalida, Tente Novamente \n')
            input('\nPressione Enter para voltar ao menu...')

menu()