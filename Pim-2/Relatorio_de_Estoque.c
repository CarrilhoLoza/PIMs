#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <locale.h>
#include "cJSON.h"

// Detecção de plataforma
#ifdef _WIN32
    #include <windows.h>
    #define CLEAR_SCREEN "cls"
#else
    #include <unistd.h>
    #define CLEAR_SCREEN "clear"
#endif

#define MAX_PRODUTOS 100
#define MAX_NOME 100
#define MAX_CATEGORIA 50
#define MAX_DATA 20

// Definições de emojis
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

typedef struct {
    int id;
    char nome[MAX_NOME];
    char categoria[MAX_CATEGORIA];
    char data_validade[MAX_DATA];
    int quantidade;
    int quantidade_minima;
} Produto;

Produto produtos[MAX_PRODUTOS];
int total_produtos = 0;

// Protótipos das funções
int configurar_encoding_emojis();
void limpar_tela();
int carregar_produtos_json(const char* filename);
int verificar_produtos_proximos_vencimento(Produto proximos_vencer[]);
void gerar_relatorio_estoque();

int configurar_encoding_emojis() {
    int emojis_funcionam = 0;
    
    #ifdef _WIN32
        system("chcp 65001 > nul");
        SetConsoleOutputCP(65001);
        setlocale(LC_ALL, "Portuguese_Brazil.65001");
        emojis_funcionam = 1;
    #else
        setlocale(LC_ALL, "pt_BR.UTF-8");
        emojis_funcionam = 1;
    #endif
    
    return emojis_funcionam;
}

void limpar_tela() {
    system(CLEAR_SCREEN);
}

int carregar_produtos_json(const char* caminho_json) {
    FILE* file = fopen(caminho_json, "r");
    if (!file) {
        printf("❌ Erro: não foi possível abrir '%s'.\n", caminho_json);
        return 0;
    }

    fseek(file, 0, SEEK_END);
    long tamanho = ftell(file);
    fseek(file, 0, SEEK_SET);
    char* buffer = malloc(tamanho + 1);
    fread(buffer, 1, tamanho, file);
    buffer[tamanho] = '\0';
    fclose(file);

    cJSON* json = cJSON_Parse(buffer);
    if (!json) {
        printf("❌ Erro ao interpretar o arquivo JSON!\n");
        free(buffer);
        return 0;
    }

    int quantidade_itens = cJSON_GetArraySize(json);
    total_produtos = 0;

    for (int i = 0; i < quantidade_itens && i < MAX_PRODUTOS; i++) {
        cJSON* item = cJSON_GetArrayItem(json, i);
        cJSON* id = cJSON_GetObjectItem(item, "id");
        cJSON* nome = cJSON_GetObjectItem(item, "nome");
        cJSON* categoria = cJSON_GetObjectItem(item, "categoria");
        cJSON* validade = cJSON_GetObjectItem(item, "data_validade");
        cJSON* qtd = cJSON_GetObjectItem(item, "quantidade");
        cJSON* qtd_min = cJSON_GetObjectItem(item, "quantidade_minima");

        if (id && nome && categoria && validade && qtd && qtd_min) {
            produtos[total_produtos].id = id->valueint;
            strcpy(produtos[total_produtos].nome, nome->valuestring);
            strcpy(produtos[total_produtos].categoria, categoria->valuestring);
            strcpy(produtos[total_produtos].data_validade, validade->valuestring);
            produtos[total_produtos].quantidade = qtd->valueint;
            produtos[total_produtos].quantidade_minima = qtd_min->valueint;
            total_produtos++;
        }
    }

    cJSON_Delete(json);
    free(buffer);
    printf("✅ %d produtos carregados de '%s'\n", total_produtos, caminho_json);
    return total_produtos;
}

int verificar_produtos_proximos_vencimento(Produto proximos_vencer[]) {
    int count = 0;
    
    for (int i = 0; i < total_produtos; i++) {
        if (produtos[i].quantidade <= produtos[i].quantidade_minima + 5) {
            proximos_vencer[count] = produtos[i];
            count++;
            if (count >= MAX_PRODUTOS) break;
        }
    }
    return count;
}

void gerar_relatorio_estoque() {
    limpar_tela();
    printf("\n✨========================================✨\n");
    printf("   📦 RELATÓRIO DE ESTOQUE 📦\n");
    printf("✨========================================✨\n");
    
    if (total_produtos == 0) {
        printf(EMOJI_VAZIO " Nenhum produto carregado no sistema.\n");
        return;
    }
    
    int total_unidades = 0;
    int produtos_baixo_estoque_count = 0;
    Produto produtos_baixo_estoque[MAX_PRODUTOS];
    Produto produtos_proximos_vencer[MAX_PRODUTOS];
    int count_proximos_vencer = verificar_produtos_proximos_vencimento(produtos_proximos_vencer);
    
    for (int i = 0; i < total_produtos; i++) {
        total_unidades += produtos[i].quantidade;
        if (produtos[i].quantidade <= produtos[i].quantidade_minima) {
            produtos_baixo_estoque[produtos_baixo_estoque_count++] = produtos[i];
        }
    }
    
    printf("\n" EMOJI_RESUMO " RESUMO DO ESTOQUE:\n");
    printf("   " EMOJI_PRODUTO " Total de produtos: %d\n", total_produtos);
    printf("   " EMOJI_UNIDADE " Total de unidades: %d\n", total_unidades);
    printf("   " EMOJI_ALERTA " Produtos com estoque baixo: %d\n", produtos_baixo_estoque_count);
    printf("   " EMOJI_VENCIMENTO " Produtos próximos do vencimento: %d\n", count_proximos_vencer);
    printf("----------------------------------------\n");
    
    char categorias[MAX_PRODUTOS][MAX_CATEGORIA];
    int quantidades_categoria[MAX_PRODUTOS] = {0};
    int total_categorias = 0;
    
    for (int i = 0; i < total_produtos; i++) {
        int encontrada = 0;
        for (int j = 0; j < total_categorias; j++) {
            if (strcmp(categorias[j], produtos[i].categoria) == 0) {
                quantidades_categoria[j]++;
                encontrada = 1;
                break;
            }
        }
        if (!encontrada && total_categorias < MAX_PRODUTOS) {
            strcpy(categorias[total_categorias], produtos[i].categoria);
            quantidades_categoria[total_categorias] = 1;
            total_categorias++;
        }
    }
    
    printf("\n" EMOJI_CATEGORIA " PRODUTOS POR CATEGORIA:\n");
    for (int i = 0; i < total_categorias; i++) {
        printf("   " EMOJI_SETAS " %s: %d produtos\n", categorias[i], quantidades_categoria[i]);
    }
    
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

int main() {
    // Configurar encoding para emojis
    configurar_encoding_emojis();
    
    // Carregar produtos do JSON
    if (carregar_produtos_json("produtos.json")) {
        // Gerar relatório
        gerar_relatorio_estoque();
    } else {
        printf("❌ Falha ao carregar produtos. Verifique o arquivo produtos.json\n");
        return 1;
    }
    
    return 0;
}