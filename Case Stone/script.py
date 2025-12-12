import os
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

pd.set_option('display.max_columns', None)

#%% Carregando e explorando dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Monta o caminho completo do Excel relativo a esse script
file_path = os.path.join(BASE_DIR, "Case_Data_Analyst_Pl.xlsx")
df = pd.read_excel(file_path)

### Conhecendo a base 
df.head()
df.columns
df.info()
df.describe()
df.session_date.unique()
df.topico_da_sessao.nunique()
df.assunto_da_sessao.nunique()

### Verificando valores nulos
df.isnull().sum()

### Criação do indicador de retenção
df['retencao_percent'] = ((df['sessoes_retidas']/ df['sessoes_total'])* 100).round(2)

### Criação da coluna mês para análise temporal
df['session_month'] = pd.to_datetime(df['session_date']).dt.to_period('M')

## fazer analise em loop para cada marca -> canal -> depois agrupar por tecnologias (dentro do canal, comparar as tecnologias)
#Resumo da retenção por marca, por canal para cada tecnologia
#Mensurar volume de sessões 
#Identificar blocos que chamam atenção para detalhar mais em topico da sessao e assunto da sessao
#Identificar padrões de comportamento ao longo dos meses e mudanças que ocorreram

### Olhar histórico geral de retenção por marca para referência]

#%% Visão Geral Mensal de Retenção vs Pedido de Atendimento por Chatbot para entender perfil histórico

df_monthly_macro = df.groupby(['session_month', 'chatbot']).agg(
    sessoes_total=('sessoes_total', 'sum'),
    sessoes_retidas=('sessoes_retidas', 'sum'),
    sessoes_com_pedido_de_atendimento = ('sessoes_com_pedido_de_atendimento', 'sum')

).reset_index()

df_monthly_macro['retencao_pct'] = (
    df_monthly_macro['sessoes_retidas'] / df_monthly_macro['sessoes_total'] * 100
).round(2)

df_monthly_macro['pct_pedido_atendimento'] = (
    (df_monthly_macro['sessoes_com_pedido_de_atendimento'] / df_monthly_macro['sessoes_total'] * 100).round(2)
)
df_monthly_macro['session_month'] = df_monthly_macro['session_month'].astype(str)

# Garante ordem fixa e paleta
bots = sorted(df_monthly_macro['chatbot'].unique())
base_colors = sns.color_palette("tab10", n_colors=len(bots))
palette = {bot: base_colors[i] for i, bot in enumerate(bots)}

fig, ax = plt.subplots(figsize=(14, 6))

# 1) Retenção - linha cheia
sns.lineplot(
    data=df_monthly_macro,
    x='session_month',
    y='retencao_pct',
    hue='chatbot',
    palette=palette,
    marker='o',
    linewidth=2,
    legend=False,
    ax=ax
)

# 2) Pedido de atendimento - linha tracejada
sns.lineplot(
    data=df_monthly_macro,
    x='session_month',
    y='pct_pedido_atendimento',
    hue='chatbot',
    palette=palette,
    marker='o',
    linewidth=2,
    linestyle='--', # Define o estilo tracejado no plot
    legend=False,
    ax=ax
)

ax.set_title('Histórico Mensal: Retenção vs Pedido de Atendimento por Chatbot')
ax.set_xlabel('Mês')
ax.set_ylabel('Percentual (%)')
plt.xticks(rotation=45)
ax.grid(True)

custom_lines = [
    # BOT A (Cor A, Sólido)
    Line2D([0], [0], color=palette[bots[0]], lw=2, marker='o', linestyle='-', label=f'{bots[0]} - Retenção'),
    # BOT A (Cor A, Tracejado)
    Line2D([0], [0], color=palette[bots[0]], lw=2, marker='', linestyle='--', label=f'{bots[0]} - Pedido de atendimento'),
    
    # BOT B (Cor B, Sólido)
    Line2D([0], [0], color=palette[bots[1]], lw=2, marker='o', linestyle='-', label=f'{bots[1]} - Retenção'),
    # BOT B (Cor B, Tracejado)
    Line2D([0], [0], color=palette[bots[1]], lw=2, marker='', linestyle='--', label=f'{bots[1]} - Pedido de atendimento')
]

ax.legend(handles=custom_lines, title='Métrica', loc='best')

fig.tight_layout()
plt.show()

### Correlação de pearson entre retenção e pedido de atendimento para cada chatbot
for bot in bots:
    print(f"\n===============================")
    print(f"Analisando correlação para o chatbot: {bot}")
    print(f"===============================\n")

    # Filtra o dataframe para o bot atual
    df_bot = df_monthly_macro[df_monthly_macro['chatbot'] == bot]

    # 1) Matriz de Correlação
    corr_matrix = df_bot[['retencao_pct', 'pct_pedido_atendimento']].corr(method='pearson')
    print("Matriz de correlação:")
    print(corr_matrix, "\n")

    # 2) Scatterplot individual
    plt.figure(figsize=(7,5))
    sns.scatterplot(
        data=df_bot,
        x='pct_pedido_atendimento',
        y='retencao_pct',
        s=120,
        color='blue'
    )
    plt.title(f"Scatterplot — {bot}\nRetenção vs Pedido de Atendimento")
    plt.xlabel("Pct Pedido de Atendimento (%)")
    plt.ylabel("Retenção (%)")
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.show()

    # 3) Regressão linear individual
    g = sns.lmplot(
        data=df_bot,
        x='pct_pedido_atendimento',
        y='retencao_pct',
        height=5,
        aspect=1.2,
        line_kws={'color': 'red'}
    )
    g.fig.suptitle(f"Regressão Linear — {bot}\nRelação entre Retenção e Pedido de Atendimento", y=1.03)
    plt.show()

    # 4) Heatmap da correlação
    plt.figure(figsize=(5,4))
    sns.heatmap(corr_matrix, annot=True, cmap="Blues", fmt=".2f", vmin=-1, vmax=1)
    plt.title(f"Matriz de Correlação — {bot}")
    plt.show()


### RESUMO DAS DESCOBERTAS
### Chatbot A com um crescimento na retenção entre julho e até o momento de agosto, apesar de ter um histórico inferior
### Chatbot B históricamente superior, mas com uma leve queda na retenção no mês de agosto após um crescimento relevante nos 2 meses anteriores
### Correlação relevante negativa entre retenção e pedido para chatbot B, indicando que quanto mais pedidos de atendimento, menor a retenção
### Correlação relevante positiva entre retenção e pedido para chatbot A, indicando que quanto mais pedidos de atendimento, maior a retenção - contra intuitivo 

### Hipóteses para investigar:
### 1) Mudanças nas tecnologias utilizadas - tecnologia_do_chatbot
### 2) Mudanças no mix de canais - fonte
### 3) Mudanças na volumetria de cada chatbot, podendo alterar a dinâmica de retenção - exemplo assuntos com alta retenção tiveram menor volumetria e vice versa - volumetria + assuntos 

# %% Análise diária + benchmark histórico para o mês atual
def construir_df_diario(df: pd.DataFrame) -> pd.DataFrame:
    df_daily = (
        df.groupby(["session_date", "chatbot"])
        .agg(
            sessoes_total=("sessoes_total", "sum"),
            sessoes_retidas=("sessoes_retidas", "sum"),
            sessoes_com_pedido_de_atendimento=(
                "sessoes_com_pedido_de_atendimento",
                "sum",
            ),
        )
        .reset_index()
    )

    df_daily["session_month"] = df_daily["session_date"].dt.to_period("M")
    df_daily["day"] = df_daily["session_date"].dt.day

    df_daily["retencao_pct"] = (
        df_daily["sessoes_retidas"] / df_daily["sessoes_total"] * 100
    ).round(2)

    df_daily["pct_pedido_atendimento"] = (
        df_daily["sessoes_com_pedido_de_atendimento"]
        / df_daily["sessoes_total"]
        * 100
    ).round(2)

    return df_daily

df_daily = construir_df_diario(df)

def obter_mes_atual_e_anterior(df: pd.DataFrame):
    meses_ordenados = sorted(df["session_month"].unique())
    if len(meses_ordenados) == 0:
        raise ValueError("Nenhum mês encontrado na base.")
    mes_atual = meses_ordenados[-1]
    mes_anterior = meses_ordenados[-2] if len(meses_ordenados) > 1 else None
    return mes_atual, mes_anterior


def resumo_mes_atual_vs_historico(df_daily: pd.DataFrame):
    """
    Compara o mês atual (parcial) com:
    - média histórica de meses anteriores, considerando mesma janela de dias
    - mês imediatamente anterior, também na mesma janela

    Isso responde se o mês atual está "indo bem ou mal" com base em benchmarks.
    """
    mes_atual, mes_anterior = obter_mes_atual_e_anterior(df_daily)

    df_atual = df_daily[df_daily["session_month"] == mes_atual].copy()
    max_day_atual = df_atual["day"].max()  # janela parcial (ex.: até dia 14)

    # Histórico (todos os meses < mes_atual) na mesma janela de dias
    df_hist = df_daily[
        (df_daily["session_month"] < mes_atual)
        & (df_daily["day"] <= max_day_atual)
    ].copy()

    # Mês anterior na mesma janela de dias
    if mes_anterior is not None:
        df_mes_ant = df_daily[
            (df_daily["session_month"] == mes_anterior)
            & (df_daily["day"] <= max_day_atual)
        ].copy()
    else:
        df_mes_ant = pd.DataFrame(columns=df_daily.columns)

    # Agrupar por chatbot para comparar
    def agrega(df_in):
        if df_in.empty:
            return pd.DataFrame(
                columns=[
                    "chatbot",
                    "sessoes_total",
                    "sessoes_retidas",
                    "retencao_pct",
                    "pct_pedido_atendimento",
                ]
            )
        agg = df_in.groupby("chatbot").agg(
            sessoes_total=("sessoes_total", "sum"),
            sessoes_retidas=("sessoes_retidas", "sum"),
            sessoes_com_pedido_de_atendimento=(
                "sessoes_com_pedido_de_atendimento",
                "sum",
            ),
        )
        agg["retencao_pct"] = (
            agg["sessoes_retidas"] / agg["sessoes_total"] * 100
        ).round(2)
        agg["pct_pedido_atendimento"] = (
            agg["sessoes_com_pedido_de_atendimento"]
            / agg["sessoes_total"]
            * 100
        ).round(2)
        return agg.reset_index()

    resumo_atual = agrega(df_atual)
    resumo_hist = agrega(df_hist)
    resumo_ant = agrega(df_mes_ant)

    resumo_atual = resumo_atual.rename(
        columns={
            "sessoes_total": "sessoes_total_atual",
            "sessoes_retidas": "sessoes_retidas_atual",
            "retencao_pct": "retencao_atual_pct",
            "pct_pedido_atendimento": "pct_pedido_atual",
        }
    )

    resumo_hist = resumo_hist.rename(
        columns={
            "sessoes_total": "sessoes_total_hist",
            "sessoes_retidas": "sessoes_retidas_hist",
            "retencao_pct": "retencao_hist_pct",
            "pct_pedido_atendimento": "pct_pedido_hist",
        }
    )

    resumo_ant = resumo_ant.rename(
        columns={
            "sessoes_total": "sessoes_total_ant",
            "sessoes_retidas": "sessoes_retidas_ant",
            "retencao_pct": "retencao_ant_pct",
            "pct_pedido_atendimento": "pct_pedido_ant",
        }
    )

    # Merge para um resumo único
    resumo = resumo_atual.merge(resumo_hist, on="chatbot", how="left").merge(
        resumo_ant, on="chatbot", how="left"
    )

    # Diferenças em pontos percentuais
    resumo["delta_retencao_atual_vs_hist_pp"] = (
        resumo["retencao_atual_pct"] - resumo["retencao_hist_pct"]
    ).round(2)

    resumo["delta_retencao_atual_vs_ant_pp"] = (
        resumo["retencao_atual_pct"] - resumo["retencao_ant_pct"]
    ).round(2)

    resumo["delta_pedido_atual_vs_hist_pp"] = (
        resumo["pct_pedido_atual"] - resumo["pct_pedido_hist"]
    ).round(2)

    resumo["delta_pedido_atual_vs_ant_pp"] = (
        resumo["pct_pedido_atual"] - resumo["pct_pedido_ant"]
    ).round(2)

    print("\n===============================")
    print(f"RESUMO MÊS ATUAL (parcial até dia {max_day_atual})")
    print(f"Mês atual (session_month): {mes_atual}")
    if mes_anterior is not None:
        print(f"Mês anterior (session_month): {mes_anterior}")
    print("===============================\n")

    print(resumo.to_string(index=False))

    return resumo, mes_atual, mes_anterior, max_day_atual

resumo, mes_atual, mes_anterior, max_day_atual = resumo_mes_atual_vs_historico(df_daily)

# %% Comparação de mix por canal/tecnologia/tópico/assunto (mês atual vs anterior)
def comparar_mix_mes(
    df: pd.DataFrame,
    mes_atual,
    mes_anterior,
    chatbot: str,
    feature: str, 
    max_day : int = None,
) -> pd.DataFrame:
    """
    Compara o mix de um feature (fonte, tecnologia, topico, assunto) entre
    mês atual e mês anterior para um chatbot específico.

    - Quando não há sessões no mês atual (ou anterior) para aquele feature,
      os percentuais ficam como NaN (não 0), evitando explosão de delta.
    """

    # Filtrar apenas o bot desejado
    df_bot = df[df["chatbot"] == chatbot].copy()

    # Focar apenas nos meses de interesse
    df_bot["session_month"] = df_bot["session_date"].dt.to_period("M")
    df_curr = df_bot[df_bot["session_month"] == mes_atual].copy()
    df_prev = df_bot[df_bot["session_month"] == mes_anterior].copy()

    def agrega(df_in):
        g = (
            df_in.groupby(feature)
            .agg(
                sessoes_total=("sessoes_total", "sum"),
                sessoes_retidas=("sessoes_retidas", "sum"),
                sessoes_com_pedido_de_atendimento=(
                    "sessoes_com_pedido_de_atendimento",
                    "sum",
                ),
            )
            .reset_index()
        )

        # Evita divisão por zero: se sessoes_total == 0, fica NaN
        g["retencao_pct"] = np.where(
            g["sessoes_total"] > 0,
            (g["sessoes_retidas"] / g["sessoes_total"] * 100).round(2),
            np.nan,
        )

        g["pct_pedido_atendimento"] = np.where(
            g["sessoes_total"] > 0,
            (g["sessoes_com_pedido_de_atendimento"] / g["sessoes_total"] * 100).round(2),
            np.nan,
        )

        total = g["sessoes_total"].sum()
        g["share_pct"] = np.where(
            total > 0,
            (g["sessoes_total"] / total * 100).round(2),
            np.nan,
        )

        return g

    curr = agrega(df_curr)
    prev = agrega(df_prev)

    # Renomeia colunas para diferenciar atual x anterior
    curr = curr.rename(
        columns={
            "sessoes_total": "sessoes_total_atual",
            "sessoes_retidas": "sessoes_retidas_atual",
            "sessoes_com_pedido_de_atendimento": "sessoes_pedido_atual",
            "retencao_pct": "retencao_atual_pct",
            "pct_pedido_atendimento": "pct_pedido_atual",
            "share_pct": "share_atual_pct",
        }
    )

    prev = prev.rename(
        columns={
            "sessoes_total": "sessoes_total_ant",
            "sessoes_retidas": "sessoes_retidas_ant",
            "sessoes_com_pedido_de_atendimento": "sessoes_pedido_ant",
            "retencao_pct": "retencao_ant_pct",
            "pct_pedido_atendimento": "pct_pedido_ant",
            "share_pct": "share_ant_pct",
        }
    )

    # Outer merge para pegar features que existem só em um dos meses
    resumo_mix = prev.merge(curr, on=feature, how="outer")

    # Preenche com 0 apenas CONTAGENS e shares.
    # NÃO preenche com 0 as colunas de percentual (retencao/pedido),
    # para que fiquem como NaN quando não há sessões.
    cols_zero = [
        "sessoes_total_atual",
        "sessoes_retidas_atual",
        "sessoes_pedido_atual",
        "share_atual_pct",
        "sessoes_total_ant",
        "sessoes_retidas_ant",
        "sessoes_pedido_ant",
        "share_ant_pct",
    ]

    for col in cols_zero:
        if col in resumo_mix.columns:
            resumo_mix[col] = resumo_mix[col].fillna(0)

    # As colunas de percentual ficam como NaN se não houver dado:
    # - retencao_atual_pct
    # - retencao_ant_pct
    # - pct_pedido_atual
    # - pct_pedido_ant

    # Deltas em p.p. (se um dos lados for NaN, delta fica NaN também)
    resumo_mix["delta_share_pp"] = (
        resumo_mix["share_atual_pct"] - resumo_mix["share_ant_pct"]
    )

    resumo_mix["delta_retencao_pp"] = (
        resumo_mix["retencao_atual_pct"] - resumo_mix["retencao_ant_pct"]
    )

    resumo_mix["delta_pedido_pp"] = (
        resumo_mix["pct_pedido_atual"] - resumo_mix["pct_pedido_ant"]
    )

    # Ordenar pelos maiores impactos em retenção (pior primeiro)
    resumo_mix = resumo_mix.sort_values(
        by="delta_retencao_pp", ascending=True
    ).reset_index(drop=True)

    print("\n===============================")
    print(f"Comparação de mix - Chatbot: {chatbot} | Feature: {feature}")
    print(f"Mês atual: {mes_atual} x Mês anterior: {mes_anterior}")
    print("===============================\n")
    print(resumo_mix.to_string(index=False))

    return resumo_mix
features = ['fonte', 'tecnologia_do_chatbot', 'topico_da_sessao', 'assunto_da_sessao']
resultados_por_feature = {}

for feature in features:
    dfs_bots = [] 

    for bot in bots:
        df_mix = comparar_mix_mes(
            df=df,
            mes_atual=mes_atual,
            mes_anterior=mes_anterior,
            chatbot=bot,
            feature=feature,
            max_day=max_day_atual,
        )

        # garantir que o bot apareça como coluna (se não estiver vindo do comparar_mix_mes)
        if "chatbot" not in df_mix.columns:
            df_mix["chatbot"] = bot

        dfs_bots.append(df_mix)

    # concatena todos os bots num df só para essa feature
    resultados_por_feature[feature] = pd.concat(dfs_bots, ignore_index=True)

df_mix_fonte = resultados_por_feature['fonte']
df_mix_tecnologia = resultados_por_feature['tecnologia_do_chatbot']
df_mix_topico = resultados_por_feature['topico_da_sessao']
df_mix_assunto = resultados_por_feature['assunto_da_sessao']

### Anomalias detectadas:
### Chatbot A - Fonte: Chat_c com retenção em zero, apesar de uma media histórica relevante - 63%

''' #%% Análise de tópicos com menor taxa de retenção no período total -> escolha por tópicos por serem mais agregadores - 60 topicos vs 700 assuntos
df_topicos = df.groupby(['chatbot', 'topico_da_sessao']).agg(
    sessoes_total = ('sessoes_total', 'sum'),
    sessoes_retidas = ('sessoes_retidas', 'sum'),
    sessoes_com_pedido_de_atendimento = ('sessoes_com_pedido_de_atendimento', 'sum')
).reset_index()

df_topicos['retencao_pct'] = ((df_topicos['sessoes_retidas']/ df_topicos['sessoes_total'])* 100).round(2)
df_topicos['pct_pedido_atendimento'] = ((df_topicos['sessoes_com_pedido_de_atendimento']/ df_topicos['sessoes_total'])* 100).round(2)

for c in df_topicos['chatbot'].unique().tolist():
    print(f"\n===============================")
    print(f"Analisando tópicos para o chatbot: {c}")
    print(f"===============================\n")
    df_bot = df_topicos[df_topicos['chatbot'] == c]
    df_bot_sorted = df_bot.sort_values(by='retencao_pct', ascending=True)
    print(df_bot_sorted[['topico_da_sessao', 'sessoes_total', 'retencao_pct', 'pct_pedido_atendimento']])

#Testar Hipóteses para aprofundar avaliação do mês de Agosto

### Agrupamento mensal 
df_monthly = df.groupby(['session_month','chatbot', 'fonte', 'tecnologia_do_chatbot', 'topico_da_sessao', 'assunto_da_sessao']).agg(
    sessoes_total = ('sessoes_total', 'sum'),
    sessoes_retidas = ('sessoes_retidas', 'sum'),
    sessoes_com_pedido_de_atendimento = ('sessoes_com_pedido_de_atendimento', 'sum')
).reset_index()

marcas = df_monthly['chatbot'].unique().tolist()
features = ['fonte', 'tecnologia_do_chatbot', 'topico_da_sessao', 'assunto_da_sessao']

for marca in marcas:
    print(f"\n===============================")
    print(f"Analisando hipóteses para o chatbot: {marca}")
    print(f"===============================\n")
    df_marca = df[df['chatbot'] == marca]

    for feature in features:
        df_marca_grouped = df_marca.groupby([feature]).agg(
            sessoes_total=('sessoes_total', 'sum'),
            sessoes_retidas=('sessoes_retidas', 'sum'),
            sessoes_com_pedido_de_atendimento = ('sessoes_com_pedido_de_atendimento', 'sum')
        ).reset_index()

        df_marca_grouped['retencao_pct'] = ((df_marca_grouped['sessoes_retidas']/ df_marca_grouped['sessoes_total'])* 100).round(2)
        df_marca_grouped['pct_pedido_atendimento'] = ((df_marca_grouped['sessoes_com_pedido_de_atendimento']/ df_marca_grouped['sessoes_total'])* 100).round(2)

'''


#%% Deep Dive

### DEEP DIVE 1 - Fonte : Chat_C BOT A - Retenção Zero
###Historico do Chat_C para BOT A para ver se é um comportamento recorrente a oscilação ou se realmente há algo de errado no mês de agosto
deep_fonte = (df[(df.chatbot == "BOT_A") & (df.fonte == "Chat_C")].groupby(['session_month', 'fonte']).agg(
                sessoes_total=("sessoes_total", "sum"),
                sessoes_retidas=("sessoes_retidas", "sum"),
                sessoes_com_pedido_de_atendimento=("sessoes_com_pedido_de_atendimento","sum",)
                )).reset_index()
deep_fonte["retencao_pct"] = np.where(
            deep_fonte["sessoes_total"] > 0,
            (deep_fonte["sessoes_retidas"] / deep_fonte["sessoes_total"] * 100).round(2),
            np.nan,
        )

deep_fonte["pct_pedido_atendimento"] = np.where(
deep_fonte["sessoes_total"] > 0,
(deep_fonte["sessoes_com_pedido_de_atendimento"] / deep_fonte["sessoes_total"] * 100).round(2),
np.nan,
)

total = deep_fonte["sessoes_total"].sum()
deep_fonte["share_pct"] = np.where(
total > 0,
(deep_fonte["sessoes_total"] / total * 100).round(2),
np.nan,
)

### Inconsistência comprovada - Chat_C BOT A com retenção zero no mês de agosto - em 6 dias diferentes com total de 4756 todas com retenção zerada - , apesar de um histórico relevante - 63% de retenção média dos ultimos meses


### DEEP DIVE 2 - Tópico da Sessão e Assunto da Sessão com distorções negativas relevantes
#Ambos com os maiores deltas de retenção vs mês de julho, para assunto e tópico para o chatbot A 
df[(df.topico_da_sessao == 'db1e24b9c4ec37948ce0acccd0716e08a01ee28d3bbd1c8adfd19f617fd4c3bb') & (df.session_month == '2025-08')]
df[(df.assunto_da_sessao == 'ee84ca1ecf3b016b684c8a91f78153ddb59f8a716fcf203a1a5fb1d7c9b7c665') & (df.session_month == '2025-08')]
# Ambos com retenção zerada em 1 dia de registro para cada, ambos na fonte  CHAT_B e tecnologia TECH_A



### Conhecendo a base de mix topico e mix assunto
rows = []
for chatbot in bots:
    df_mix_assunto[df_mix_assunto.chatbot == chatbot ]['retencao_atual_pct'].describe()
    df_mix_topico[df_mix_topico.chatbot == chatbot]['retencao_atual_pct'].describe()
    #Salvar quantis 
     # --- Assunto ---
    q10_assunto = (
        df_mix_assunto[df_mix_assunto.chatbot == chatbot]['retencao_atual_pct']
        .quantile(0.10)
    )
    rows.append({
        "chatbot": chatbot,
        "feature": "assunto_da_sessao",
        "q10_retencao": q10_assunto
    })

    # --- Tópico ---
    q10_topico = (
        df_mix_topico[df_mix_topico.chatbot == chatbot]['retencao_atual_pct']
        .quantile(0.10)
    )
    rows.append({
        "chatbot": chatbot,
        "feature": "topico_da_sessao",
        "q10_retencao": q10_topico
    })
df_q10 = pd.DataFrame(rows)

#Análise de quantis se mostrou não aplicável, uma vez que tópicos e assuntos possuem retenção relativamente alta. 
#Para capturar outliers, vamos considerar um percentual inferior a 20% de retenção como critério para identificar tópicos e assuntos críticos
# Além disso, vamos considerar apenas aqueles com delta negativo relevante (abaixo de -10 p.p.) para garantir que houve uma anomalia relevante entre um mês e outro

# Criar dicionários onde cada chatbot terá sua lista própria
topicos_criticos_por_bot = {}
assuntos_criticos_por_bot = {}

for chatbot in bots:
    # Filtrar tópicos críticos do BOT
    topicos_criticos = df_mix_topico[
        (df_mix_topico.chatbot == chatbot)
        & (df_mix_topico['retencao_atual_pct'] < 20)
        & (df_mix_topico['delta_retencao_pp'] < -10)
    ]['topico_da_sessao'].unique().tolist()

    # Filtrar assuntos críticos do BOT
    assuntos_criticos = df_mix_assunto[
        (df_mix_assunto.chatbot == chatbot)
        & (df_mix_assunto['retencao_atual_pct'] < 20)
        & (df_mix_assunto['delta_retencao_pp'] < -10)
    ]['assunto_da_sessao'].unique().tolist()

    # Salvar no dicionário final
    topicos_criticos_por_bot[chatbot] = topicos_criticos
    assuntos_criticos_por_bot[chatbot] = assuntos_criticos

# Filtrar os dataframes originais para os tópicos e assuntos críticos identificados para cada chatbot 
dfs_topicos_criticos = {}
dfs_assuntos_criticos = {}

for bot in bots:
    # Tópicos críticos por bot
    dfs_topicos_criticos[bot] = df[
        (df["session_month"].astype(str) == "2025-08")
        & (df["chatbot"] == bot)
        & (df["topico_da_sessao"].isin(topicos_criticos_por_bot[bot]))
    ]
    
    # Assuntos críticos por bot
    dfs_assuntos_criticos[bot] = df[
        (df["session_month"].astype(str) == "2025-08")
        & (df["chatbot"] == bot)
        & (df["assunto_da_sessao"].isin(assuntos_criticos_por_bot[bot]))
    ]

### Assuntos críticos identificados para cada chatbot, mostrando consistentemente em todos os meses dias com retenção zerada, no mês de agosto tendo um volume maior de sessões com retenção zerada
### Em ambos chatbots as tecnologias relacionadas aos assuntos se mostram constantes, no caso do chatbot A a tecnologia TECH_A e no chatbot B a tecnologia TECH_B

### Chatbot A apresentou 1 tópico crítico com retenção zerada em agosto, mas apenas com 1 dia de amostra, necessitando de mais dados para analisar e decretar alguma anomalia relevante
### Chatbot B apresentou nenhum tópico crítico, todos mantiveram retenção acima de 58%


### Analise de topicos e assuntos positivos

# Criar dicionários onde cada chatbot terá sua lista própria
topicos_positivos_por_bot = {}
assuntos_positivos_por_bot = {}

for chatbot in bots:
    # Filtrar tópicos críticos do BOT
    topicos_positivos = df_mix_topico[
        (df_mix_topico.chatbot == chatbot)
        & (df_mix_topico['retencao_atual_pct'] > 20)
        & (df_mix_topico['delta_retencao_pp'] > 10)
    ]['topico_da_sessao'].unique().tolist()

    # Filtrar assuntos críticos do BOT
    assuntos_positivos = df_mix_assunto[
        (df_mix_assunto.chatbot == chatbot)
        & (df_mix_assunto['retencao_atual_pct'] > 20)
        & (df_mix_assunto['delta_retencao_pp'] > 10)
    ]['assunto_da_sessao'].unique().tolist()

    # Salvar no dicionário final
    topicos_positivos_por_bot[chatbot] = topicos_positivos
    assuntos_positivos_por_bot[chatbot] = assuntos_positivos

# Filtrar os dataframes originais para os tópicos e assuntos com variancia positiva relevante identificados para cada chatbot 
dfs_topicos_positivos = {}
dfs_assuntos_positivos = {}

for bot in bots:
    # Tópicos críticos por bot
    dfs_topicos_positivos[bot] = df[
        (df["session_month"].astype(str) == "2025-08")
        & (df["chatbot"] == bot)
        & (df["topico_da_sessao"].isin(topicos_positivos_por_bot[bot]))
    ]
    
    # Assuntos críticos por bot
    dfs_assuntos_positivos[bot] = df[
        (df["session_month"].astype(str) == "2025-08")
        & (df["chatbot"] == bot)
        & (df["assunto_da_sessao"].isin(assuntos_positivos_por_bot[bot]))
    ]

### Assuntos positivos identificados para cada chatbot, mostrando um aumento relevante na retenção no mês de agosto porém ainda mantendo uma oscilação grande, possuindo dias com retenção zerada

### Resultado final encontrado acerca de assuntos: ambos chatbots apresentaram muita oscilação em diversos assuntos, possuindo dias com retenção zerada e outros dias com retenção alta, mesmo com uma volumetria relevante em cada dia amostral 
### Necessário um monitoramento mais frequente para entender o que está causando essa oscilação, visto que não há um padrão claro de tecnologia ou canal que justifique tais variações


#%% Projeção para o fechamento de Agosto 
### Como evidenciado anteriormente, o mês de Maio trouxe uma mudança relevante na dinâmica de retenção dos chatbots, possivelmente por mudanças nas tecnologias ou canais utilizados
### Dessa forma, para projetar o fechamento de agosto, vamos considerar a média móvel dos últimos 3 meses (Maio, Junho e Julho) para projetar o mês de Agosto


# 2. Definir meses de interesse (maio em diante)

mes_inicio = "2025-05"
df_recent = df_daily[df_daily['session_month'] >= mes_inicio]

# Identificar meses disponíveis
meses = sorted(df_recent['session_month'].unique())

# Último mês é agosto (parcial)
mes_atual = meses[-1]


# 3. Função para calcular fatores históricos por chatbot

def calcular_fator_historico(df_recent, chatbot, mes_atual):
    fatores = []

    # Iterar meses anteriores ao atual
    for mes in meses:
        if mes == mes_atual:
            continue
        
        df_mes = df_recent[(df_recent['chatbot'] == chatbot) &
                           (df_recent['session_month'] == mes)]

        # Cálculo da retenção média nos dias 1–14
        r_1_14 = df_mes[df_mes['day'] <= 14]['retencao_pct'].mean()

        # Cálculo da retenção nos dias 15–31 (ou até onde houver dados)
        r_15_31 = df_mes[df_mes['day'] > 14]['retencao_pct'].mean()

        if pd.notnull(r_1_14) and pd.notnull(r_15_31) and r_1_14 > 0:
            fatores.append(r_15_31 / r_1_14)

    if len(fatores) == 0:
        return np.nan

    return np.mean(fatores)  # fator médio pós-disrupção



# 4. Projetar agosto por chatbot

projecoes = []

for bot in df_recent['chatbot'].unique():

    # Dados do mês atual (agosto)
    df_mes_atual = df_recent[(df_recent['chatbot'] == bot) &
                             (df_recent['session_month'] == mes_atual)]

    # Retenção média dias 1–14
    r_atual_1_14 = df_mes_atual[df_mes_atual['day'] <= 14]['retencao_pct'].mean()

    # Fator histórico (1–14 → 15–31)
    fator = calcular_fator_historico(df_recent, bot, mes_atual)

    # Projeção para dias 15–31
    r_atual_15_31_proj = r_atual_1_14 * fator if pd.notnull(fator) else np.nan

    # Projeção ponderada final (31 dias)
    r_final = ((14 * r_atual_1_14) + (17 * r_atual_15_31_proj)) / 31

    projecoes.append({
        "chatbot": bot,
        "media_dias_1_14": r_atual_1_14,
        "fator_historico_1_14_para_15_31": fator,
        "proj_dias_15_31": r_atual_15_31_proj,
        "retencao_proj_final_agosto": r_final
    })

df_projecoes = pd.DataFrame(projecoes)

print("\n=========== PROJEÇÃO DE AGOSTO — MÉTODO HISTÓRICO (1-14 → 15-31) ===========\n")
print(df_projecoes.to_string(index=False))

#%% Projeção para os meses de setembro a dezembro de 2025 - pergunta 3 

# 1. Garantir que session_month é string
df_monthly_macro["session_month"] = df_monthly_macro["session_month"].astype(str)

# 2. Substituir agosto pelo valor projetado (para usar na série inteira)
df_trend = df_monthly_macro.copy()

for _, row in df_projecoes.iterrows():
    mask = (
        (df_trend["chatbot"] == row["chatbot"]) &
        (df_trend["session_month"] == "2025-08")
    )
    df_trend.loc[mask, "retencao_pct"] = row["retencao_proj_final_agosto"]


# ------------------------------
# Função: medir "drift de platô"
# ------------------------------
import numpy as np

def calcular_drift_plato(df_hist, chatbot,
                         lim_jump=1.5,     # > 1.5 p.p. = salto estrutural (disrupção)
                         lim_plato=1.5,    # ≤ 1.5 p.p. = movimento dentro do platô
                         max_step_proj=0.25):  # p.p. máx por mês na projeção
    """
    Identifica saltos grandes na série (degraus) e calcula qual costuma ser
    o drift médio durante os períodos de platô entre esses saltos.

    - Disrupção: |delta| > lim_jump
    - Platô: |delta| ≤ lim_plato

    Usa TODO o histórico disponível para o chatbot (não só 2025).
    Depois limita esse drift por mês (max_step_proj) para não projetar
    quedas/subidas irreais.
    """
    df_bot = (
        df_hist[df_hist["chatbot"] == chatbot]
        .sort_values("session_month")
        .reset_index(drop=True)
    )
    vals = df_bot["retencao_pct"].values
    if len(vals) < 3:
        return 0.0

    # deltas mensais
    deltas = np.diff(vals)   # tamanho n-1

    # índices onde houve "salto" (degrau estrutural): i -> i+1
    jump_idx = np.where(np.abs(deltas) > lim_jump)[0]

    # se não achar nenhum salto, drift ~ 0 (série bem estável)
    if len(jump_idx) == 0:
        return 0.0

    # separar segmentos entre saltos
    # ex: [-1] -> primeiro trecho começa em 0
    seg_starts = np.concatenate(([-1], jump_idx))
    seg_ends   = np.concatenate((jump_idx, [len(vals) - 1]))

    drifts_por_seg = []

    for s, e in zip(seg_starts, seg_ends):
        # valores do segmento: s+1 .. e
        seg_vals = vals[s+1:e+1]
        if len(seg_vals) < 2:
            continue

        seg_deltas = np.diff(seg_vals)

        # deltas dentro do platô: |Δ| ≤ lim_plato
        plateau_deltas = seg_deltas[np.abs(seg_deltas) <= lim_plato]
        if len(plateau_deltas) > 0:
            drifts_por_seg.append(plateau_deltas.mean())

    if len(drifts_por_seg) == 0:
        drift = 0.0
    else:
        # drift médio típico de platô (pode ser levemente negativo ou positivo)
        drift = float(np.mean(drifts_por_seg))

    # limitar quanto vamos usar na projeção (máx 0.25 p.p./mês, por ex.)
    drift = float(np.clip(drift, -max_step_proj, max_step_proj))
    return drift


# 3. Projeção set–dez usando "drift de platô"
meses_futuros = ["2025-09", "2025-10", "2025-11", "2025-12"]
linhas_future = []

for bot in bots:
    # série histórica completa do bot (já com agosto projetado)
    df_bot = (
        df_trend[df_trend["chatbot"] == bot]
        .sort_values("session_month")
        .reset_index(drop=True)
    )
    vals = df_bot["retencao_pct"].values

    # valor base para projeção = agosto projetado (último ponto)
    base_aug = vals[-1]

    # drift típico de platô, calculado com base em TODO o histórico
    drift_plato = calcular_drift_plato(df_trend, chatbot=bot)

    # limites razoáveis com base no histórico (não sair muito do intervalo)
    y_min_hist = vals.min()
    y_max_hist = vals.max()
    lower_bound = max(0, y_min_hist - 2)   # até 2 p.p. abaixo do mínimo histórico
    upper_bound = min(100, y_max_hist + 2) # até 2 p.p. acima do máximo histórico

    for i, mes in enumerate(meses_futuros, start=1):
        # projeção = valor de agosto + i * drift de platô
        valor = base_aug + i * drift_plato

        # clamp em limites históricos (curva não pode cair muito nem explodir)
        valor = float(np.clip(valor, lower_bound, upper_bound))

        linhas_future.append({
            "chatbot": bot,
            "session_month": mes,
            "retencao_pct_proj": round(valor, 2),
        })

df_future_trend = pd.DataFrame(linhas_future)

print("\n=========== PROJEÇÃO SET–DEZ COM COMPORTAMENTO DE PLATÔ ===========\n")
print(df_future_trend.to_string(index=False))


# 4) Montar série 2025 completa (real + agosto proj + futuro)

# reais até JULHO
df_2025_real = df_monthly_macro[
    (df_monthly_macro["session_month"].str.startswith("2025")) &
    (df_monthly_macro["session_month"] < "2025-08")
][["chatbot", "session_month", "retencao_pct"]].copy()

# Agosto projetado
df_ago_proj = []
for _, row in df_projecoes.iterrows():
    df_ago_proj.append({
        "chatbot": row["chatbot"],
        "session_month": "2025-08",
        "retencao_pct": row["retencao_proj_final_agosto"],
    })
df_ago_proj = pd.DataFrame(df_ago_proj)

# Futuro renomeado
df_future_trend_ren = df_future_trend.rename(columns={"retencao_pct_proj": "retencao_pct"})

# Série completa 2025
df_2025_full = pd.concat(
    [df_2025_real, df_ago_proj, df_future_trend_ren],
    ignore_index=True,
)

# 5) Indicador anual (média da retenção 2025)
df_indicador_anual = (
    df_2025_full
    .groupby("chatbot")["retencao_pct"]
    .mean()
    .reset_index()
    .rename(columns={"retencao_pct": "retencao_media_2025"})
)

print("\n=========== INDICADOR DE RETENÇÃO PROJETADO — ANO 2025 ===========\n")
print(df_indicador_anual.to_string(index=False))




