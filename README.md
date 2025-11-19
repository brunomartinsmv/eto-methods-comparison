# Trabalho Final - Teoria em Física Ambiental

## Descrição

Este repositório contém o trabalho final da disciplina de **Teoria em Física Ambiental** do mestrado em Física. O projeto visa analisar e comparar métodos empíricos e semi-empíricos para a estimativa da evapotranspiração de referência (ETo) em duas localidades brasileiras distintas: Piracicaba (São Paulo) e Manaus (Amazonas). Utiliza-se o método de Penman-Monteith como referência padrão para validação dos demais métodos.

## Objetivos

- Comparar a acurácia de diferentes métodos de estimativa de ETo: Thornthwaite, Thornthwaite-Camargo, Camargo, Hargreaves & Samani (original e corrigido), Priestley-Taylor.
- Avaliar o desempenho através de métricas estatísticas quantitativas: RMSE (Root Mean Square Error), MAE (Mean Absolute Error), MBE (Mean Bias Error), R² (coeficiente de determinação) e índice d de Willmott.
- Visualizar as comparações qualitativas utilizando Diagramas de Taylor para ambas as localidades.
- Analisar as diferenças de performance entre climas tropicais (Manaus) e subtropicais (Piracicaba).

## Metodologia

### Dados
- **Fonte**: Dados meteorológicos diários de 2024 para Piracicaba e Manaus.
- **Arquivo principal**: `Evapo.xlsx` contendo planilhas separadas para cada localidade.
- **Variáveis**: Estimativas diárias de ETo pelos diferentes métodos (em mm/dia).

### Processamento
1. Leitura e limpeza dos dados do Excel.
2. Cálculo das métricas estatísticas para cada método comparado ao Penman-Monteith.
3. Geração de Diagramas de Taylor para visualização gráfica das similaridades entre séries.

### Análises Estatísticas
- **RMSE**: Mede a magnitude média dos erros.
- **MAE**: Mede a magnitude absoluta média dos erros.
- **MBE**: Indica tendência de sub ou superestimativa.
- **R²**: Mede a proporção da variância explicada.
- **d de Willmott**: Índice de concordância (0-1, onde 1 é concordância perfeita).

### Métodos de Estimativa de Evapotranspiração (ETo)

Os métodos avaliados são classificados em empíricos (baseados apenas em temperatura) e semi-empíricos (incorporam outros parâmetros meteorológicos). Abaixo, uma breve descrição de cada método com suas equações principais:

- **Penman-Monteith (Referência)**: Método físico combinando balanço de energia e massa, considerado padrão internacional para ETo. Requer dados completos de radiação, temperatura, umidade e vento.

  $$ETo = \frac{0.408 \Delta (R_n - G) + \gamma \frac{900}{T+273} u_2 (e_s - e_a)}{\Delta + \gamma (1 + 0.34 u_2)}$$
  
  Onde: $\Delta$ = inclinação da curva de pressão de vapor (kPa/°C), $R_n$ = radiação líquida (MJ/m²/dia), $G$ = fluxo de calor no solo (MJ/m²/dia), $\gamma$ = constante psicrométrica (kPa/°C), $T$ = temperatura média (°C), $u_2$ = velocidade do vento a 2m (m/s), $e_s - e_a$ = déficit de pressão de vapor (kPa).

- **Thornthwaite**: Método empírico baseado exclusivamente na temperatura média mensal. Adequado para regiões com dados limitados, mas pode subestimar em climas úmidos.
  
  $$ETo = 16 \left( \frac{10T}{I} \right)^a \cdot \frac{N}{12} \cdot \frac{N_d}{30}$$
  
  Onde: $T$ = temperatura média mensal (°C), $I$ = índice de calor anual, $a$ = coeficiente empírico, $N$ = horas de luz do dia, $N_d$ = número de dias no mês.

- **Camargo**: Adaptação do método de Thornthwaite para regiões tropicais, ajustando coeficientes para melhor representar climas equatoriais com alta umidade.

- **Thornthwaite-Camargo**: Combinação dos métodos Thornthwaite e Camargo, visando equilibrar as limitações de ambos em diferentes condições climáticas.

- **Hargreaves & Samani**: Método semi-empírico que utiliza amplitude térmica diária como proxy para radiação solar. Simples e eficaz em regiões com dados de temperatura disponíveis.
  
  $$ETo = 0.0023 R_a (T_{max} - T_{min})^{0.5} (T_{mean} + 17.8) $$
  
  Onde: $R_a$ = radiação extraterrestre (MJ/m²/dia), $T_{max}$, $T_{min}$, $T_{mean}$ = temperaturas máxima, mínima e média (°C).

- **Hargreaves & Samani (corrigido)**: Versão modificada do método original, com ajustes para melhorar a acurácia em condições específicas.

- **Priestley-Taylor**: Método semi-empírico baseado no balanço de energia, assumindo que a transpiração é proporcional à radiação. Adequado para superfícies bem irrigadas.
- 
  $$ETo = \alpha \frac{\Delta}{\Delta + \gamma} \frac{R_n}{\lambda}$$
  
  Onde: $\alpha \approx 1.26$ (coeficiente empírico), $\lambda$ = calor latente de vaporização (MJ/kg).

## Estrutura do Projeto

```
fisicambiental/
├── calculo.ipynb              # Notebook principal com todas as análises
├── Evapo.xlsx                 # Dados brutos de evapotranspiração
├── Dados/                     # Pasta com dados originais
│   ├── manaus.csv
│   ├── PETROLINA.csv
│   └── piracicaba.csv
├── corrigido/                 # Pasta com dados processados
│   ├── Manaus_interpolado.csv
│   ├── Manaus_medias_diarias.csv
│   ├── Manaus.csv
│   └── Petrolina.csv
└── README.md                  # Este arquivo
```

## Dependências

- Python 3.8+
- pandas >= 1.3.0
- numpy >= 1.20.0
- matplotlib >= 3.3.0

## Instalação e Execução

### Pré-requisitos
1. Instalar Python 3.x
2. Criar um ambiente virtual (recomendado):
   ```bash
   python -m venv .venv
   # No Windows: .venv\Scripts\activate
   # No Linux/Mac: source .venv/bin/activate
   ```

### Instalação das Dependências
```bash
pip install pandas numpy matplotlib
```

### Execução
1. Abra o Jupyter Notebook:
   ```bash
   jupyter notebook
   ```
2. Navegue até `calculo.ipynb` e execute as células sequencialmente.
3. Os resultados incluem tabelas de métricas e diagramas de Taylor.

## Resultados Principais

### Piracicaba (SP)
- Melhor performance: [baseado no notebook, mas como não executado, descrever genericamente]
- Análise climática: Clima subtropical com estação seca definida.

### Manaus (AM)
- Desafios específicos: Clima equatorial úmido com alta variabilidade.
- Comparações entre métodos empíricos e semi-empíricos.

Os Diagramas de Taylor fornecem uma representação visual da proximidade entre cada método e a referência, considerando desvio padrão, correlação e erro padrão centrado na raiz quadrada da média (CRMSD).

## Discussão

Este trabalho contribui para a compreensão da aplicabilidade de métodos simplificados de estimativa de ETo em diferentes contextos climáticos brasileiros, auxiliando na escolha de abordagens adequadas para regiões com dados meteorológicos limitados.

## Autor

[Seu Nome Completo]  
Mestrando em Física  
Universidade [Nome da Universidade]  
Email: [seu.email@universidade.edu.br]

## Orientador

[Nome do Orientador]  
Doutor em Física Ambiental  
Universidade [Nome da Universidade]

## Data de Apresentação

18 de novembro de 2025

## Licença

Este projeto é parte de um trabalho acadêmico e não possui licença específica para distribuição comercial. Para uso acadêmico, cite apropriadamente.

---

**Nota**: Os dados utilizados são proprietários ou de fontes públicas e devem ser tratados com confidencialidade acadêmica.
