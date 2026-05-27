# Roteiro do Video Demonstrativo (5-8 min)

## 1. Introducao (1 min)

- Contexto: fundacao seleciona 100 bolsistas via ENEM 2024
- Tres objetivos: notas, diversidade socioeconomica/racial, cobertura geografica
- Fonte: microdados INEP (link oficial)

## 2. Preparacao dos dados (1 min)

- Mostrar pasta `microdados_enem_2024/DADOS`
- Executar: `python scripts/01_prepare_data.py`
- Explicar pool estratificado (~40 mil candidatos, 27 UFs)

## 3. Algoritmo genetico na interface WEB (3 min)

- Subir API: `python -m uvicorn api.main:app --reload --port 8000`
- Subir frontend: `cd web && npm run dev`
- Pagina **Processamento**:
  - Ajustar pesos (0.5 / 0.3 / 0.2)
  - Clicar em **Executar selecao**
  - Mostrar grafo de evolucao e log por geracao

## 4. Resultados (2 min)

- Pagina **Grupo Ideal**: tabela com 100 bolsistas, media e UFs
- Pagina **Analises**: graficos de notas, diversidade e distribuicao por UF
- Mencionar fitness final (~0.78) e trade-offs observados

## 5. Encerramento (30 s)

- Mostrar `docs/RELATORIO_BOLSAS_ENEM.md` e graficos em `data/processed/charts/`
- Limitacoes: UF de prova como proxy, pool amostrado
