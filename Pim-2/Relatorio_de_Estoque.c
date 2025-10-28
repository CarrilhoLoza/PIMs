/*
 * Relatorio_de_Estoque.c
 * Sistema de gerenciamento de estoque com relatórios
 * Desenvolvido para aprendizado de programação em C
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <locale.h>
#include "cJSON.h"  // Biblioteca para manipulação de JSON

// Detecção de plataforma (Windows vs Linux/Mac)
#ifdef _WIN32
    #include <windows.h>
    #define CLEAR_SCREEN "cls"  // Comando para limpar tela no Windows
#else
    #include <unistd.h>
    #define CLEAR_SCREEN "clear"  // Comando para limpar tela em Unix/Linux
#endif

// Definições de constantes para limites do sistema
#define MAX_PRODUTOS 100     // Número máximo de produtos suportados
#define MAX_NOME 100         // Tamanho máximo do nome do produto
#define MAX_CATEGORIA 50     // Tamanho máximo da categoria
#define MAX_DATA 20          // Tamanho máximo para data

// Definições de emojis para melhor visualização
// Emojis diferentes podem ser necessários em diferentes sistemas operacionais
#ifdef _WIN32
    #define EMOJI_VAZIO     "📭"
    #define EMOJI_RESUMO    "📊"
    #define EMOJI_PRODUTO   "📦"
    #define EMOJI_UNIDADE   "🔢"
    #define EMOJI_ALERTA    "⚠️ "
    #define EMOJI_VENCIMENTO "⏰"
    #define EMOJI_CATEGORIA "🏷️ "
    #define EMOJI_ESTOQUE_BAIXO "🔴"
    #define EMOJI_SETAS     "➡️ "
#else
    #define EMOJI_VAZIO     "📭"
    #define EMOJI_RESUMO    "📊"
    #define EMOJI_PRODUTO   "📦"
    #define EMOJI_UNIDADE   "🔢"
    #define EMOJI_ALERTA    "⚠️"
    #define EMOJI_VENCIMENTO "⏰"
    #define EMOJI_CATEGORIA "🏷️"
    #define EMOJI_ESTOQUE_BAIXO "🔴"
    #define EMOJI_SETAS     "➡️"
#endif

// Estrutura que representa um produto no estoque
typedef struct {
    int id;                          // Identificador único do produto
    char nome[MAX_NOME];             // Nome do produto
    char categoria[MAX_CATEGORIA];   // Categoria (ex: "Alimentício", "Limpeza")
    char data_validade[MAX_DATA];    // Data de validade (formato string)
    int quantidade;                  // Quantidade atual em estoque
    int quantidade_minima;           // Quantidade mínima necessária
} Produto;

// Variáveis globais
Produto produtos[MAX_PRODUTOS];  // Array para armazenar todos os produtos
int total_produtos = 0;          // Contador de produtos carregados

// Protótipos das funções (declarações)
int configurar_encoding_emojis();
void limpar_tela();
int carregar_produtos_json(const char* filename);
int verificar_produtos_proximos_vencimento(Produto proximos_vencer[]);
void gerar_relatorio_estoque();

/*
 * Configura o encoding do console para suportar emojis
 * Retorna 1 se bem-sucedido, 0 caso contrário
 */
int configurar_encoding_emojis() {
    int emojis_funcionam = 0;
    
    #ifdef _WIN32
        // No Windows: configura para UTF-8
        system("chcp 65001 > nul");
        SetConsoleOutputCP(65001);
        setlocale(LC_ALL, "Portuguese_Brazil.65001");
        emojis_funcionam = 1;
    #else
        // Em Unix/Linux: configura locale para UTF-8
        setlocale(LC_ALL, "pt_BR.UTF-8");
        emojis_funcionam = 1;
    #endif
    
    return emojis_funcionam;
}

/*
 * Limpa a tela do console usando o comando apropriado para cada SO
 */
void limpar_tela() {
    system(CLEAR_SCREEN);
}

/*
 * Carrega produtos de um arquivo JSON
 * Parâmetro: caminho_json - caminho para o arquivo JSON
 * Retorna: número de produtos carregados ou 0 em caso de erro
 */
int carregar_produtos_json(const char* caminho_json) {
    // Abre o arquivo para leitura
    FILE* file = fopen(caminho_json, "r");
    if (!file) {
        printf("❌ Erro: não foi possível abrir '%s'.\n", caminho_json);
        return 0;
    }

    // Determina o tamanho do arquivo
    fseek(file, 0, SEEK_END);
    long tamanho = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    // Aloca memória para armazenar o conteúdo do arquivo
    char* buffer = malloc(tamanho + 1);
    fread(buffer, 1, tamanho, file);
    buffer[tamanho] = '\0';  // Adiciona terminador de string
    fclose(file);

    // Parse do JSON usando a biblioteca cJSON
    cJSON* json = cJSON_Parse(buffer);
    if (!json) {
        printf("❌ Erro ao interpretar o arquivo JSON!\n");
        free(buffer);
        return 0;
    }

    // Processa cada item do array JSON
    int quantidade_itens = cJSON_GetArraySize(json);
    total_produtos = 0;

    for (int i = 0; i < quantidade_itens && i < MAX_PRODUTOS; i++) {
        cJSON* item = cJSON_GetArrayItem(json, i);
        
        // Extrai cada campo do objeto JSON
        cJSON* id = cJSON_GetObjectItem(item, "id");
        cJSON* nome = cJSON_GetObjectItem(item, "nome");
        cJSON* categoria = cJSON_GetObjectItem(item, "categoria");
        cJSON* validade = cJSON_GetObjectItem(item, "data_validade");
        cJSON* qtd = cJSON_GetObjectItem(item, "quantidade");
        cJSON* qtd_min = cJSON_GetObjectItem(item, "quantidade_minima");

        // Verifica se todos os campos necessários estão presentes
        if (id && nome && categoria && validade && qtd && qtd_min) {
            // Preenche a estrutura do produto com os dados do JSON
            produtos[total_produtos].id = id->valueint;
            strcpy(produtos[total_produtos].nome, nome->valuestring);
            strcpy(produtos[total_produtos].categoria, categoria->valuestring);
            strcpy(produtos[total_produtos].data_validade, validade->valuestring);
            produtos[total_produtos].quantidade = qtd->valueint;
            produtos[total_produtos].quantidade_minima = qtd_min->valueint;
            total_produtos++;  // Incrementa o contador de produtos
        }
    }

    // Libera a memória alocada para o JSON
    cJSON_Delete(json);
    free(buffer);
    
    printf("✅ %d produtos carregados de '%s'\n", total_produtos, caminho_json);
    return total_produtos;
}

/*
 * Identifica produtos que estão próximos do vencimento (estoque baixo)
 * Parâmetro: proximos_vencer - array para armazenar os produtos encontrados
 * Retorna: número de produtos próximos do vencimento
 */
int verificar_produtos_proximos_vencimento(Produto proximos_vencer[]) {
    int count = 0;
    
    for (int i = 0; i < total_produtos; i++) {
        // Considera "próximo do vencimento" quando a quantidade está próxima do mínimo
        if (produtos[i].quantidade <= produtos[i].quantidade_minima + 5) {
            proximos_vencer[count] = produtos[i];  // Adiciona ao array de resultados
            count++;
            if (count >= MAX_PRODUTOS) break;  // Evita estourar o array
        }
    }
    return count;
}

/*
 * Gera um relatório completo do estoque com várias seções:
 * - Resumo geral
 * - Produtos por categoria
 * - Produtos com estoque baixo
 * - Produtos próximos do vencimento
 * - Lista completa de produtos
 */
void gerar_relatorio_estoque() {
    limpar_tela();
    
    // Cabeçalho do relatório
    printf("\n✨========================================✨\n");
    printf("   📦 RELATÓRIO DE ESTOQUE 📦\n");
    printf("✨========================================✨\n");
    
    // Verifica se há produtos carregados
    if (total_produtos == 0) {
        printf(EMOJI_VAZIO " Nenhum produto carregado no sistema.\n");
        return;
    }
    
    // Variáveis para estatísticas
    int total_unidades = 0;
    int produtos_baixo_estoque_count = 0;
    Produto produtos_baixo_estoque[MAX_PRODUTOS];
    Produto produtos_proximos_vencer[MAX_PRODUTOS];
    
    // Identifica produtos próximos do vencimento
    int count_proximos_vencer = verificar_produtos_proximos_vencimento(produtos_proximos_vencer);
    
    // Processa todos os produtos para calcular estatísticas
    for (int i = 0; i < total_produtos; i++) {
        total_unidades += produtos[i].quantidade;  // Soma total de unidades
        
        // Verifica estoque baixo (quantidade <= quantidade mínima)
        if (produtos[i].quantidade <= produtos[i].quantidade_minima) {
            produtos_baixo_estoque[produtos_baixo_estoque_count++] = produtos[i];
        }
    }
    
    // Seção 1: Resumo do estoque
    printf("\n" EMOJI_RESUMO " RESUMO DO ESTOQUE:\n");
    printf("   " EMOJI_PRODUTO " Total de produtos: %d\n", total_produtos);
    printf("   " EMOJI_UNIDADE " Total de unidades: %d\n", total_unidades);
    printf("   " EMOJI_ALERTA " Produtos com estoque baixo: %d\n", produtos_baixo_estoque_count);
    printf("   " EMOJI_VENCIMENTO " Produtos próximos do vencimento: %d\n", count_proximos_vencer);
    printf("----------------------------------------\n");
    
    // Seção 2: Produtos por categoria
    char categorias[MAX_PRODUTOS][MAX_CATEGORIA];  // Array para armazenar categorias únicas
    int quantidades_categoria[MAX_PRODUTOS] = {0}; // Contador para cada categoria
    int total_categorias = 0;                      // Número de categorias diferentes
    
    // Agrupa produtos por categoria
    for (int i = 0; i < total_produtos; i++) {
        int encontrada = 0;
        
        // Verifica se a categoria já foi registrada
        for (int j = 0; j < total_categorias; j++) {
            if (strcmp(categorias[j], produtos[i].categoria) == 0) {
                quantidades_categoria[j]++;  // Incrementa contador da categoria
                encontrada = 1;
                break;
            }
        }
        
        // Se é uma categoria nova, adiciona ao array
        if (!encontrada && total_categorias < MAX_PRODUTOS) {
            strcpy(categorias[total_categorias], produtos[i].categoria);
            quantidades_categoria[total_categorias] = 1;
            total_categorias++;
        }
    }
    
    // Exibe produtos por categoria
    printf("\n" EMOJI_CATEGORIA " PRODUTOS POR CATEGORIA:\n");
    for (int i = 0; i < total_categorias; i++) {
        printf("   " EMOJI_SETAS " %s: %d produtos\n", categorias[i], quantidades_categoria[i]);
    }
    
    // Seção 3: Produtos com estoque baixo
    if (produtos_baixo_estoque_count > 0) {
        printf("\n" EMOJI_ESTOQUE_BAIXO " PRODUTOS COM ESTOQUE BAIXO:\n");
        for (int i = 0; i < produtos_baixo_estoque_count; i++) {
            printf("   " EMOJI_PRODUTO " %s - %d unidades (mínimo: %d)\n", 
                   produtos_baixo_estoque[i].nome, 
                   produtos_baixo_estoque[i].quantidade,
                   produtos_baixo_estoque[i].quantidade_minima);
        }
    } else {
        printf("\n✅ Nenhum produto com estoque baixo.\n");
    }
    
    // Seção 4: Produtos próximos do vencimento
    if (count_proximos_vencer > 0) {
        printf("\n" EMOJI_VENCIMENTO " PRODUTOS PRÓXIMOS DO VENCIMENTO:\n");
        for (int i = 0; i < count_proximos_vencer; i++) {
            printf("   " EMOJI_PRODUTO " %s - Vence: %s - Estoque: %d/%d\n", 
                   produtos_proximos_vencer[i].nome, 
                   produtos_proximos_vencer[i].data_validade,
                   produtos_proximos_vencer[i].quantidade,
                   produtos_proximos_vencer[i].quantidade_minima);
        }
    } else {
        printf("\n✅ Nenhum produto próximo do vencimento.\n");
    }
    
    // Seção 5: Lista completa de todos os produtos
    printf("\n📋 LISTA COMPLETA DE PRODUTOS:\n");
    for (int i = 0; i < total_produtos; i++) {
        printf("   %d. %s - %d unidades - %s\n", 
               produtos[i].id, 
               produtos[i].nome, 
               produtos[i].quantidade,
               produtos[i].categoria);
    }
    printf("\n");
}

/*
 * Função principal do programa
 * Orquestra todo o fluxo de execução
 */
int main() {
    // Configura o encoding para suportar emojis
    configurar_encoding_emojis();
    
    // Carrega produtos do arquivo JSON
    if (carregar_produtos_json("produtos.json")) {
        // Se carregou com sucesso, gera o relatório
        gerar_relatorio_estoque();
    } else {
        printf("❌ Falha ao carregar produtos. Verifique o arquivo produtos.json\n");
        return 1;  // Retorna código de erro
    }
    
    return 0;  // Retorna sucesso
}