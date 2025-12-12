import os
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
from scipy import stats


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

# %%
def detectar_mudancas_regime(serie, threshold=2.0):
    """
    Detecta mudanças significativas de regime na série temporal
    threshold: número de desvios padrão para considerar uma mudança
    """
    deltas = serie.diff()
    std_delta = deltas.std()
    mean_delta = deltas.mean()
    
    # Pontos onde houve mudança significativa
    mudancas = abs(deltas - mean_delta) > (threshold * std_delta)
    return mudancas

def projetar_com_regime_adaptativo(df_monthly_macro, df_projecoes, bot):
    """
    Projeta a retenção considerando:
    1. Identificação de regimes
    2. Tendência do regime atual
    3. Volatilidade histórica
    """
    
    # Filtrar dados do bot
    df_bot = df_monthly_macro[df_monthly_macro['chatbot'] == bot].copy()
    df_bot['session_month'] = pd.to_datetime(df_bot['session_month'].astype(str))
    df_bot = df_bot.sort_values('session_month')
    
    # Detectar mudanças de regime
    mudancas = detectar_mudancas_regime(df_bot['retencao_pct'])
    indices_mudanca = df_bot[mudancas].index.tolist()
    
    # Identificar o regime atual (após a última mudança significativa)
    if len(indices_mudanca) > 0:
        ultimo_regime_idx = max(indices_mudanca)
        df_regime_atual = df_bot.loc[ultimo_regime_idx:]
    else:
        # Se não houver mudanças detectadas, usar últimos 3 meses
        df_regime_atual = df_bot.tail(3)
    
    # Calcular tendência do regime atual
    if len(df_regime_atual) >= 2:
        x = np.arange(len(df_regime_atual))
        y = df_regime_atual['retencao_pct'].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    else:
        slope = 0
        intercept = df_regime_atual['retencao_pct'].iloc[-1]
    
    # Valor base: projeção de agosto
    valor_agosto = df_projecoes[df_projecoes['chatbot'] == bot]['retencao_proj_final_agosto'].iloc[0]
    
    # Calcular volatilidade do regime atual
    volatilidade = df_regime_atual['retencao_pct'].std()
    
    # Projetar setembro a dezembro
    meses_futuros = pd.date_range('2025-09', '2025-12', freq='M')
    projecoes = []
    
    for i, mes in enumerate(meses_futuros, start=1):
        # Projeção base: continuar tendência do regime atual
        valor_proj = valor_agosto + (slope * i)
        
        # Aplicar decay na tendência (assumir que mudanças se estabilizam)
        decay_factor = 0.8 ** i  # Reduz o impacto da tendência ao longo do tempo
        valor_proj = valor_agosto + (slope * i * decay_factor)
        
        # Limitar por min/max histórico com margem
        min_hist = df_bot['retencao_pct'].min() - volatilidade
        max_hist = df_bot['retencao_pct'].max() + volatilidade
        
        valor_proj = np.clip(valor_proj, max(0, min_hist), min(100, max_hist))
        
        projecoes.append({
            'chatbot': bot,
            'session_month': mes.strftime('%Y-%m'),
            'retencao_pct_proj': round(valor_proj, 2),
            'metodo': 'regime_adaptativo'
        })
    
    return pd.DataFrame(projecoes)

def projetar_com_media_movel_ponderada(df_monthly_macro, df_projecoes, bot, janela=3):
    """
    Projeta usando média móvel ponderada dos últimos meses
    Dá mais peso aos meses mais recentes
    """
    
    df_bot = df_monthly_macro[df_monthly_macro['chatbot'] == bot].copy()
    df_bot['session_month'] = pd.to_datetime(df_bot['session_month'].astype(str))
    df_bot = df_bot.sort_values('session_month')
    
    # Valor base: projeção de agosto
    valor_agosto = df_projecoes[df_projecoes['chatbot'] == bot]['retencao_proj_final_agosto'].iloc[0]
    
    # Calcular média móvel ponderada dos últimos meses
    ultimos_valores = df_bot.tail(janela)['retencao_pct'].values
    pesos = np.array([0.2, 0.3, 0.5])[-len(ultimos_valores):]  # Mais peso nos recentes
    pesos = pesos / pesos.sum()  # Normalizar
    
    media_ponderada = np.average(ultimos_valores, weights=pesos)
    
    # Calcular tendência suave
    if len(ultimos_valores) >= 2:
        tendencia = (ultimos_valores[-1] - ultimos_valores[0]) / len(ultimos_valores)
    else:
        tendencia = 0
    
    # Projetar setembro a dezembro
    meses_futuros = pd.date_range('2025-09', '2025-12', freq='M')
    projecoes = []
    
    for i, mes in enumerate(meses_futuros, start=1):
        # Mix entre agosto projetado e média ponderada, com tendência suave
        peso_agosto = 0.7 * (0.9 ** i)  # Reduz importância de agosto ao longo do tempo
        valor_proj = (valor_agosto * peso_agosto + media_ponderada * (1 - peso_agosto)) + (tendencia * i * 0.3)
        
        # Limitar entre 0 e 100
        valor_proj = np.clip(valor_proj, 0, 100)
        
        projecoes.append({
            'chatbot': bot,
            'session_month': mes.strftime('%Y-%m'),
            'retencao_pct_proj': round(valor_proj, 2),
            'metodo': 'media_movel_ponderada'
        })
    
    return pd.DataFrame(projecoes)

def projetar_conservador(df_monthly_macro, df_projecoes, bot):
    """
    Projeção conservadora: assume estabilização no valor de agosto
    com leve convergência para média histórica recente
    """
    
    df_bot = df_monthly_macro[df_monthly_macro['chatbot'] == bot].copy()
    
    # Valor base: projeção de agosto
    valor_agosto = df_projecoes[df_projecoes['chatbot'] == bot]['retencao_proj_final_agosto'].iloc[0]
    
    # Média dos últimos 6 meses
    media_recente = df_bot.tail(6)['retencao_pct'].mean()
    
    # Projetar setembro a dezembro
    meses_futuros = pd.date_range('2025-09', '2025-12', freq='M')
    projecoes = []
    
    for i, mes in enumerate(meses_futuros, start=1):
        # Convergência gradual para média histórica
        peso_agosto = 0.9 ** i  # Reduz ao longo do tempo
        valor_proj = valor_agosto * peso_agosto + media_recente * (1 - peso_agosto)
        
        projecoes.append({
            'chatbot': bot,
            'session_month': mes.strftime('%Y-%m'),
            'retencao_pct_proj': round(valor_proj, 2),
            'metodo': 'conservador'
        })
    
    return pd.DataFrame(projecoes)

# EXECUTAR PROJEÇÕES


# Lista de bots (assumindo que você tem a variável 'bots' definida)
# bots = df_monthly_macro['chatbot'].unique()

projecoes_finais = []

for bot in bots:
    print(f"\n{'='*60}")
    print(f"PROJEÇÕES PARA {bot}")
    print(f"{'='*60}\n")
    
    # Método 1: Regime Adaptativo
    proj_regime = projetar_com_regime_adaptativo(df_monthly_macro, df_projecoes, bot)
    print("Método 1 - Regime Adaptativo:")
    print(proj_regime[['session_month', 'retencao_pct_proj']])
    
    # Método 2: Média Móvel Ponderada
    proj_mm = projetar_com_media_movel_ponderada(df_monthly_macro, df_projecoes, bot)
    print("\nMétodo 2 - Média Móvel Ponderada:")
    print(proj_mm[['session_month', 'retencao_pct_proj']])
    
    # Método 3: Conservador
    proj_cons = projetar_conservador(df_monthly_macro, df_projecoes, bot)
    print("\nMétodo 3 - Conservador:")
    print(proj_cons[['session_month', 'retencao_pct_proj']])
    
    # Ensemble: média dos três métodos
    proj_ensemble = proj_regime.copy()
    proj_ensemble['retencao_pct_proj'] = (
        proj_regime['retencao_pct_proj'] + 
        proj_mm['retencao_pct_proj'] + 
        proj_cons['retencao_pct_proj']
    ) / 3
    proj_ensemble['retencao_pct_proj'] = proj_ensemble['retencao_pct_proj'].round(2)
    proj_ensemble['metodo'] = 'ensemble'
    
    print("\n*** PROJEÇÃO FINAL (Ensemble) ***:")
    print(proj_ensemble[['session_month', 'retencao_pct_proj']])
    
    projecoes_finais.append(proj_ensemble)

# Consolidar todas as projeções
df_projecoes_finais = pd.concat(projecoes_finais, ignore_index=True)

# ============================================================================
# VISUALIZAÇÃO
# ============================================================================

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for idx, bot in enumerate(bots):
    ax = axes[idx]
    
    # Histórico
    df_bot_hist = df_monthly_macro[df_monthly_macro['chatbot'] == bot].copy()
    df_bot_hist['session_month'] = pd.to_datetime(df_bot_hist['session_month'].astype(str))
    
    ax.plot(df_bot_hist['session_month'], df_bot_hist['retencao_pct'], 
            marker='o', linewidth=2, label='Histórico Real')
    
    # Agosto projetado
    valor_agosto = df_projecoes[df_projecoes['chatbot'] == bot]['retencao_proj_final_agosto'].iloc[0]
    ax.plot(pd.Timestamp('2025-08'), valor_agosto, 
            marker='o', color='orange', markersize=10, label='Agosto (Projetado)')
    
    # Projeções futuras
    df_bot_proj = df_projecoes_finais[df_projecoes_finais['chatbot'] == bot].copy()
    df_bot_proj['session_month'] = pd.to_datetime(df_bot_proj['session_month'])
    
    ax.plot(df_bot_proj['session_month'], df_bot_proj['retencao_pct_proj'], 
            marker='s', linewidth=2, linestyle='--', color='red', label='Projeção Set-Dez')
    
    ax.set_title(f'Projeção de Retenção 2025 - {bot}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Retenção (%)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()


# INDICADOR ANUAL 2025


# Consolidar série completa de 2025
df_2025_completo = []

# Real até julho
df_2025_real = df_monthly_macro[
    df_monthly_macro['session_month'].str.startswith('2025') & 
    (df_monthly_macro['session_month'] < '2025-08')
][['chatbot', 'session_month', 'retencao_pct']].copy()

df_2025_completo.append(df_2025_real)

# Agosto projetado
for _, row in df_projecoes.iterrows():
    df_2025_completo.append(pd.DataFrame([{
        'chatbot': row['chatbot'],
        'session_month': '2025-08',
        'retencao_pct': row['retencao_proj_final_agosto']
    }]))

# Set-Dez projetados
df_projecoes_finais_renamed = df_projecoes_finais[['chatbot', 'session_month', 'retencao_pct_proj']].copy()
df_projecoes_finais_renamed.columns = ['chatbot', 'session_month', 'retencao_pct']
df_2025_completo.append(df_projecoes_finais_renamed)

# Consolidar
df_2025_full = pd.concat(df_2025_completo, ignore_index=True)

# Calcular média anual por chatbot
df_indicador_anual = df_2025_full.groupby('chatbot')['retencao_pct'].mean().reset_index()
df_indicador_anual.columns = ['chatbot', 'retencao_media_2025']
df_indicador_anual['retencao_media_2025'] = df_indicador_anual['retencao_media_2025'].round(2)

print("\n" + "="*60)
print("INDICADOR DE RETENÇÃO PROJETADO - ANO 2025")
print("="*60)
print(df_indicador_anual.to_string(index=False))
print("\n")






