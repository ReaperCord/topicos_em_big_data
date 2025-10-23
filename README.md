# Dashboard Analítico de Segurança Pública (RJ)

Este projeto é um dashboard interativo construído em Streamlit, focado na análise de dados de segurança pública do Rio de Janeiro (baseados nos dados do ISP).

O objetivo é transformar dados brutos e complexos em insights estratégicos e acionáveis, utilizando clusterização para identificar "Perfis de Risco" em vez de analisar dezenas de áreas (AISPs) individualmente.

## 🎯 Contexto do Projeto

Os dados de segurança pública do estado do Rio de Janeiro, disponibilizados pelo Instituto de Segurança Pública (ISP), são vastos, granulares e complexos. Analisar esses dados brutos, que são divididos por dezenas de Áreas Integradas de Segurança Pública (AISP) e mais de 100 indicadores criminais, é um desafio para gestores, jornalistas e para o público.

O grande volume e a alta dimensionalidade dos dados dificultam a identificação de padrões claros:

* Uma área é "perigosa" por quê? Por roubo a pedestres ou por letalidade?
* Duas áreas com o mesmo número de roubos de veículo têm o mesmo perfil de crime?
* Como a resposta policial se compara em áreas com perfis de risco semelhantes?

Este projeto busca solucionar esse problema através da aplicação de técnicas de *data science* (clusterização) para agrupar AISPs com características de criminalidade semelhantes.

O resultado é este dashboard que, em vez de mostrar 41 AISPs individuais, apresenta **"Perfis de Risco"** estratégicos, permitindo uma análise mais inteligente sobre onde, como e quando o crime ocorre, e qual a eficácia da resposta para cada perfil.

## 🚀 Funcionalidades Principais

O dashboard é dividido em 4 abas analíticas:

* **📈 Tendência & Nível de Ameaça:** Analisa a evolução temporal dos crimes (KPI 5: Variação de Roubo de Rua) e o nível de ameaça de cada cluster (KPI 2: Média de Fuzis Apreendidos).
* **🛡️ Eficácia & Perfil do Crime:** Mede a eficiência da resposta policial (KPI 1: Taxa de Recuperação de Veículos) e o perfil da violência em cada cluster (KPI 3: Proporção Roubo vs. Furto e KPI 6: Proporção de Letalidade Policial).
* **🗺️ Matriz de Risco Resumido:** Apresenta um gráfico estratégico 2x2 (KPI 4: Risco à Vida vs. Risco ao Patrimônio) que posiciona cada cluster para uma visualização rápida de sua natureza.
* **🔎 Detalhe por Cluster:** Uma aba interativa com um **menu *dropdown***. O usuário seleciona um perfil de risco e vê uma análise detalhada ("storytelling"), o histórico temporal completo daquele cluster e a tabela de dados de todas as AISPs que o compõem.

## ⚙️ Stack de Tecnologias

* **Python** (Linguagem Principal)
* **Streamlit** (Framework do Dashboard)
* **Pandas** (Manipulação e Análise de Dados)
* **Plotly** (Gráficos Interativos)
* **Scikit-learn** (Utilizado para a normalização Min-Max na Matriz de Risco)

## 📁 Estrutura de Arquivos

Para que o dashboard funcione corretamente, os arquivos de dados devem estar localizados em uma subpasta chamada `data`:
```
seu-projeto/
│
├── data/ 
│ ├── gold_dashboard_data.csv # Dados temporais (fatos)
│ └── perfis_de_risco_k6.csv # Dados de perfil (dimensão)
│
├── app.py # O código-fonte do dashboard
└── README.md # Este arquivo
```

### Fontes de Dados

* **`gold_dashboard_data.csv`**: Arquivo principal contendo os dados temporais (mês a mês) de crimes por AISP. Deve conter colunas como `ano`, `mes`, `aisp`, `cluster_id`, `roubo_rua`, `total_roubos`, `total_furtos`, `recuperacao_veiculos`, etc.
* **`perfis_de_risco_k6.csv`**: Arquivo contendo as médias (centroides) de cada cluster, gerado pelo *notebook* de K-Means. Usado para os KPIs de perfil, como `armas_arma_fogo_fuzil`. (O `k6` pode ser ajustado no código se o seu número de clusters for diferente).

## 🛠️ Instalação e Execução

### 1. Pré-requisitos

Clone este repositório e certifique-se de ter o Python 3.8+ instalado.

### 2. Instalação das Dependências

(Opcional, mas recomendado) Crie um ambiente virtual:

```bash
python -m venv .venv
# No Windows:
.\.venv\Scripts\activate
# No macOS/Linux:
source .venv/bin/activate

# Instale as bibliotecas necessárias:

pip install streamlit pandas plotly scikit-learn

```
### 3. Executando o Dashboard

Certifique-se de que seus arquivos CSV estão na pasta **`./data/.`**
No seu terminal, na pasta raiz do projeto, execute:

```bash
streamlit run app.py
```

O dashboard será aberto automaticamente no seu navegador padrão.
