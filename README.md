# Relatorio - Bolsas ENEM com Algoritmo Genetico

## Contexto

Fundacao educacional seleciona **100 bolsistas** a partir dos microdados ENEM 2024,
otimizando desempenho academico, diversidade socioeconomica/racial e cobertura geografica.

Fonte oficial: [Microdados ENEM - INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)

## Mapeamento de variaveis (PDF vs microdados 2024)

| PDF | Coluna real | Observacao |
|-----|-------------|------------|
| NU_NOTA_RED | NU_NOTA_REDACAO | Nota da redacao |
| TP_ESCOLA | Q023 | Tipo de escola no EM |
| Q006 (renda) | Q007 | Renda familiar |
| Q002 | Q002 | Escolaridade da mae |
| SG_UF_RESIDENCIA | SG_UF_PROVA | Proxy geografico (UF da prova) |

## Preparacao dos dados

- Join PARTICIPANTES + RESULTADOS por ordem de linha (mesma estrategia do trabalho OLAP).
- Filtro: presenca em todas as areas e notas validas.
- Pool estratificado: **40000** candidatos em **27** UFs.

## Algoritmo genetico

- Cromossomo: 100 indices unicos no pool.
- Populacao: 20 | Geracoes: 100
- Fitness = 0.5*notas + 0.3*diversidade + 0.2*cobertura (pesos configuraveis na WEB)

### Resultado da ultima execucao

```json
{
  "best_fitness": 0.7808888179356532,
  "components": {
    "notas": 0.6283767535070148,
    "diversidade": 0.8890014706071527,
    "cobertura": 1.0,
    "penalty": 0.0,
    "ufs": 27.0
  },
  "group_size": 100
}
```

## Grupo ideal (amostra)

| NU_INSCRICAO | MEDIA_NOTAS | UF | COR_RACA |
|--------------|-------------|----|---------|
| 210062870255 | 813.1 | BA | 3 |
| 210064767251 | 780.5 | BA | 3 |
| 210063869852 | 772.7 | DF | 3 |
| 210063382136 | 794.0 | RJ | 1 |
| 210066162312 | 795.9 | AL | 1 |
| 210063745547 | 812.1 | RJ | 2 |
| 210064794809 | 731.5 | AM | 3 |
| 210063972260 | 769.2 | RR | 3 |
| 210062619700 | 796.0 | SP | 2 |
| 210063610847 | 750.1 | AL | 2 |

## Graficos

![Notas](data/processed/charts/notas_boxplot.png)
![Diversidade](data/processed/charts/diversidade_barras.png)
![Geografia](data/processed/charts/geo_uf.png)

## Limitacoes

- UF de prova como proxy de residencia.
- Pool amostrado (~40k) para viabilidade computacional.
- Questionario: renda em Q007 (nao Q006).

## Video demonstracao

[Assistir ao video demonstrativo](video/video-enem-bolsa.mp4)

Arquivo local: `video/video-enem-bolsa.mp4`

### Roteiro

1. Executar `scripts/01_prepare_data.py`
2. Abrir interface WEB (`uvicorn` + `npm run dev`)
3. Ajustar pesos e rodar GA (grafo de evolucao)
4. Mostrar paginas Grupo Ideal e Analises
5. Destacar trade-off entre nota, diversidade e cobertura

---

# AV2 - Bolsas ENEM com Algoritmo Genetico

Selecao automatica de 100 bolsistas a partir dos microdados ENEM 2024, usando algoritmo genetico com objetivos de desempenho, diversidade e cobertura geografica.

## Requisitos

- Python 3.11+
- Node.js 18+ (interface WEB)

## Instalacao

```powershell
cd h:\UNI7\SAD-Lina\AV2-TRABALHO-3-ENEM-BOLSA
python -m pip install -r requirements.txt
cd web
npm install
```

## Passo 1 - Preparar dados

```powershell
python scripts/01_prepare_data.py --pool-size 40000 --cap-per-uf 2000
```

Gera `data/processed/candidates.parquet`.

## Passo 2 - Executar GA (CLI)

```powershell
python scripts/02_run_ga_cli.py --population 20 --generations 100
```

Saidas: `best_group.csv`, `ga_history.json`, `ga_summary.json`.

## Passo 3 - Relatorio

```powershell
python scripts/03_generate_report.py
```

Gera `docs/RELATORIO_BOLSAS_ENEM.md` e graficos em `data/processed/charts/`.

## Interface WEB (Bonus - estilo Obsidian)

Terminal 1 (API):

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

Terminal 2 (Frontend):

```powershell
cd web
npm run dev
```

Abra http://localhost:5173

Paginas:
- **Processamento**: sliders de pesos, execucao do GA, grafo de evolucao
- **Grupo Ideal**: tabela dos 100 selecionados
- **Analises**: graficos de notas, diversidade e UF

## Telas da interface WEB

### Processamento

Configuracao dos pesos, execucao do algoritmo genetico e visualizacao da evolucao (grafo de geracoes).

![Tela Processamento](docs/screenshots/tela-processamento.png)

### Grupo Ideal

Tabela com os 100 bolsistas selecionados, metricas do grupo e atributos socioeconomicos com rotulos descritivos.

![Tela Grupo Ideal](docs/screenshots/tela-grupo-ideal.png)

### Analises

Graficos de notas por area, diversidade (cor/raca e renda) e distribuicao geografica por UF.

![Tela Analises](docs/screenshots/tela-analises.png)

## Fonte de dados

Microdados: baixar do [portal INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem) e extrair em `microdados_enem_2024/` (pasta nao versionada no GitHub).

Documentacao INEP: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem

Roteiro detalhado: [docs/ROTEIRO_VIDEO.md](docs/ROTEIRO_VIDEO.md)

**Video demonstracao:** [video/video-enem-bolsa.mp4](video/video-enem-bolsa.mp4)

## Roteiro do video (5-8 min)

1. Contexto do problema (3 objetivos)
2. `01_prepare_data.py` e pool estratificado
3. Interface WEB: ajuste de pesos e execucao com grafo
4. Pagina Grupo Ideal e Analises
5. Insights: trade-off nota vs diversidade vs cobertura

## Mapeamento PDF vs dados 2024

| PDF | Coluna real |
|-----|-------------|
| NU_NOTA_RED | NU_NOTA_REDACAO |
| TP_ESCOLA | Q023 |
| Q006 renda | Q007 |
| SG_UF_RESIDENCIA | SG_UF_PROVA |
