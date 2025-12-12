import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import os
import script 

sns.set(style="whitegrid")

APP_DIR = os.path.dirname(os.path.abspath(__file__))


# HELPER PARA FORMATAR PERCENTUAIS

def format_percent_columns(df: pd.DataFrame, extra_pct_cols=None) -> pd.DataFrame:
    """
    - Arredonda para 2 casas os campos de percentual
    - Acrescenta ' (%)' ao nome da coluna
    Critério:
      - Nome da coluna contém 'pct', 'percent', 'percentual', 'taxa' ou '%'
      - + colunas extras passadas explicitamente em extra_pct_cols
    """
    df_fmt = df.copy()
    pct_cols = [
        c for c in df_fmt.columns
        if any(k in c.lower() for k in ["pct", "percent", "percentual", "taxa", "%"])
    ]

    if extra_pct_cols:
        for c in extra_pct_cols:
            if c in df_fmt.columns and c not in pct_cols:
                pct_cols.append(c)

    if pct_cols:
        df_fmt[pct_cols] = df_fmt[pct_cols].round(2)
        df_fmt = df_fmt.rename(columns={c: f"{c} (%)" for c in pct_cols})

    return df_fmt


# RECUPERAR OBJETOS DO script.py
df = script.df
df_monthly_macro = script.df_monthly_macro
bots = script.bots
palette = script.palette

# Objetos da questão 2
df_mix_fonte = script.df_mix_fonte
df_mix_tecnologia = script.df_mix_tecnologia
df_mix_topico = script.df_mix_topico
df_mix_assunto = script.df_mix_assunto
deep_fonte = script.deep_fonte
topicos_criticos_por_bot = script.topicos_criticos_por_bot
assuntos_criticos_por_bot = script.assuntos_criticos_por_bot
topicos_positivos_por_bot = script.topicos_positivos_por_bot
assuntos_positivos_por_bot = script.assuntos_positivos_por_bot
dfs_topicos_criticos = script.dfs_topicos_criticos
dfs_assuntos_criticos = script.dfs_assuntos_criticos
dfs_topicos_positivos = script.dfs_topicos_positivos
dfs_assuntos_positivos = script.dfs_assuntos_positivos

# Objetos da questão 2 - resumo mês atual vs histórico
from script import resumo_mes_atual_vs_historico, df_daily
resumo, mes_atual, mes_anterior, max_day_atual = resumo_mes_atual_vs_historico(df_daily)

# Objetos da questão 3 (projeção)
df_projecoes = script.df_projecoes
df_future_trend = script.df_future_trend
df_2025_full = script.df_2025_full
df_indicador_anual = script.df_indicador_anual

# CONFIG STREAMLIT + ESTILO STONE

STONE_GREEN = "#00A94F"

st.set_page_config(
    page_title="Case - Data Analyst Stone - Cristiano Diniz",
    layout="wide"
)

# CSS
st.markdown(
    f"""
    <style>
    h1, h2, h3 {{
        color: {STONE_GREEN};
    }}
    .stone-box {{
        background-color: rgba(0, 169, 79, 0.08);
        padding: 1rem 1.25rem;
        border-radius: 0.5rem;
        border-left: 4px solid {STONE_GREEN};
        margin-bottom: 1rem;
    }}
    .stone-badge {{
        display: inline-block;
        padding: 0.1rem 0.5rem;
        border-radius: 999px;
        background-color: rgba(0, 169, 79, 0.12);
        color: {STONE_GREEN};
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    
    .profile-header {{
        background: #052011;
        border-left: 4px solid #00A85A;
        padding: 10px 16px;
        margin-bottom: 10px;
        color: #E6F4EC;
        font-size: 13px;
        font-family: "Roboto", "Helvetica", sans-serif;
    }}
    .profile-header b {{
        font-size: 14px;
    }}
    .profile-header a {{
        color: #3DD68C;
        text-decoration: none;
    }}
    .profile-header a:hover {{
        text-decoration: underline;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# BLOCO FIXO DE HEADER - para todas as abas

st.markdown(
    """
    <div class="profile-header">
        <b>Cristiano Araújo Abreu Diniz</b><br>
        dinizcristiano04@gmail.com<br>
        <a href="https://www.linkedin.com/in/cristianoaadiniz" target="_blank">
            linkedin.com/in/cristianoaadiniz
        </a><br>
        12/12/2025
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown(
    f'<h1 style="margin-bottom:0.5rem;">Case Técnico - Data Analyst Stone</h1>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(
    ["Questão 1 - Modelagem & Tabelas",
     "Questão 2 - Diagnóstico & Próximos Passos",
     "Questão 3 - Projeções 2025"]
)

# ------------------------------------------------------------------
# ABA 1 - QUESTÃO 1
# ------------------------------------------------------------------
with tab1:
    st.header("Questão 1 - Construção das Tabelas de Fonte")

    st.markdown(
        """
<div class="stone-box">
<div class="stone-badge">Resumo executivo questão 1</div>

- A tabela `silver_sessions` guarda o evento transacional por sessão, com flags de retenção e pedido de atendimento.
- O SELECT agrega para uma granularidade diária por bot / canal / tecnologia / tópico / assunto,
  que é exatamente a base utilizada nas análises das questões 2 e 3.
 </div>
 """,
        unsafe_allow_html=True,
    )

    st.subheader("Código SQL (arquivo tabelas_fonte.sql)")
    try:
        sql_path = os.path.join(APP_DIR, "tabelas_fonte.sql")
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_text = f.read()
        st.code(sql_text, language="sql")
    except FileNotFoundError:
        st.warning("Arquivo `tabelas_fonte.sql` não encontrado na pasta do app.")

    st.subheader("Esquema da Tabela `silver_sessions`")

    schema_data = [
        ("session_id", "STRING", "Identificador único da sessão"),
        ("session_date", "DATE", "Data da sessão"),
        ("chatbot", "STRING", "Identificador do bot (BOT_A / BOT_B)"),
        ("fonte", "STRING", "Canal de origem (Chat_A / Chat_B / Chat_C)"),
        ("tecnologia_do_chatbot", "STRING", "Tecnologia utilizada (TECH_A / TECH_B)"),
        ("topico_da_sessao", "STRING", "Tópico macro da sessão"),
        ("assunto_da_sessao", "STRING", "Assunto específico da sessão"),
        ("flag_sessao_retida", "BOOLEAN", "True se o bot resolveu sem humano"),
        ("flag_pedido_atendimento", "BOOLEAN", "True se houve pedido de atendimento humano"),
        ("dt_ingest", "TIMESTAMP", "Timestamp de ingestão no pipeline"),
    ]
    schema_df = pd.DataFrame(schema_data, columns=["Coluna", "Tipo", "Descrição"])
    st.dataframe(schema_df, use_container_width=True)

    st.subheader("Tabela Agregada de Sessões (granularidade da saída do SELECT)")
    agg_schema = [
        ("session_date", "DATE", "Data da sessão"),
        ("chatbot", "STRING", "Bot"),
        ("fonte", "STRING", "Canal"),
        ("tecnologia_do_chatbot", "STRING", "Tecnologia"),
        ("topico_da_sessao", "STRING", "Tópico"),
        ("assunto_da_sessao", "STRING", "Assunto"),
        ("sessoes_total", "INT", "Total de sessões no granularidade acima"),
        ("sessoes_retidas", "INT", "Sessões resolvidas pelo bot"),
        ("sessoes_com_pedido_de_atendimento", "INT", "Sessões com pedido de humano"),
    ]
    agg_df = pd.DataFrame(agg_schema, columns=["Coluna", "Tipo", "Descrição"])
    st.dataframe(agg_df, use_container_width=True)

# ------------------------------------------------------------------
# ABA 2 - QUESTÃO 2
# ------------------------------------------------------------------
with tab2:
    st.header("Questão 2 - Diagnóstico da Retenção & Próximos Passos")
    
    # 1) CONCLUSÕES GERAIS
    st.subheader("Diagnóstico de Agosto")

    st.markdown(
        """
        <div class="stone-box">
        <div class="stone-badge">Resumo executivo questão 2 - Diagnóstico</div>

        <b>Estamos indo bem em agosto?</b><br>
        • No <b>geral</b>, agosto não é um mês de crise: o BOT_B continua com retenção alta e o BOT_A já mostra recuperação depois da piora entre maio e julho.<br>
        • Por outro lado, o mês expõe <b>pontos de risco</b> claros (principalmente no canal Chat_C do BOT_A e em alguns tópicos/assuntos) que, se não forem tratados, podem derrubar a retenção nos próximos meses.<br>
        • Por isso, agosto deve ser encarado como um <b>mês de ajuste</b>: o resultado agregado ainda é bom, mas já aponta onde precisamos atuar para evitar deterioração e consolidar ganhos.<br>
        <br>
        
        <b>Highlights (pontos positivos):</b><br>
        • <b>BOT_B</b> mantém retenção em nível alto, mesmo com uma leve declínio na prévia de agosto.<br>
        • <b>BOT_A</b> sai da trajetória de queda e mostra <b>movimento de recuperação</b> na parcial de agosto.<br>
        • Conseguimos identificar <b>tópicos e assuntos com melhora consistente</b> de retenção, que podem servir de referência para ajustes nos demais fluxos.<br>
        <br>
        
        <b>Lowlights (pontos de atenção):</b><br>
        • Canal <b>Chat_C – BOT_A</b> com períodos de <b>retenção zerada</b> em agosto, afetando um volume relevante de sessões e destoando completamente do histórico (&gt; 60%).<br>
        • Conjunto de tópicos e assuntos com <b>retenção muito baixa e queda forte vs. julho</b>, concentrando boa parte da perda de performance do mês.<br>
        • <b>Oscilação diária elevada</b> em diversos assuntos (dias muito bons alternando com dias de retenção zero), sugerindo fragilidade operacional ou dependência de fatores externos ainda não mapeados.<br>
        <br>

        <b>Principais descobertas:</b><br>
        • Até maio/2025, os dois bots apresentam um comportamento de retenção relativamente estável; a partir daí, há um <b>ponto de virada</b>, possivelmente ligado a mudança de regras de negócio e/ou tecnologia.<br>
        • O <b>BOT_B</b> opera em um patamar estruturalmente mais alto de retenção, com <b>crescimento forte de maio a julho</b> e apenas um leve declínio em agosto, ainda em nível considerado saudável.<br>
        • O <b>BOT_A</b> historicamente retém menos que o BOT_B, mas mantém um gap estável. Após a queda observada em maio, a parcial de agosto indica <b>retomada</b> em relação a julho e aproximação do padrão pré-mudança.<br>
        • No canal <b>Chat_C do BOT_A</b>, a combinação de <b>retenção zero em agosto + histórico médio acima de 60%</b> indica mais um possível problema de fluxo ou de medição do que apenas piora real da experiência do cliente.<br>
        • Alguns <b>tópicos e assuntos específicos</b> apresentam queda acentuada (retenção &lt; 20% e queda &gt; 10 p.p. versus julho), enquanto outros mostram melhora relevante, porém ainda com comportamento instável — reforçando a necessidade de olhar caso a caso.<br>
        • Na análise de correlação, o <b>BOT_B</b> segue o padrão esperado: mais pedidos de atendimento se associam a menor retenção. Já o <b>BOT_A</b> apresenta relação positiva, o que é contraintuitivo e levanta hipóteses de <b>inconsistência na forma como as flags são registradas</b> em alguns cenários.<br>
        • As projeções indicam que, <b>corrigindo as anomalias de canal e dos tópicos/assuntos críticos</b>, ambos os bots tendem a encerrar agosto em um nível de retenção igual ou ligeiramente superior ao observado nos meses recentes após a mudança de maio.<br>
            </div>

        """,
        unsafe_allow_html=True,
    )

    # 2) PROJEÇÃO DE AGOSTO
    st.subheader("Projeção de Fechamento de Agosto (por Chatbot)")

    st.markdown(
        """
A projeção de agosto responde ao pedido **“Faça uma projeção de como fecharemos agosto”**:

- Usa a retenção média observada nos **dias 1-14**;
- Calcula um **fator histórico 1-14 → 15-31** com base em maio, junho e julho;
- Combina os dois para estimar a **retenção projetada para o mês cheio** por chatbot.
        """
    )
    st.dataframe(format_percent_columns(df_projecoes, ['media_dias_1_14', 'proj_dias_15_31', 'retencao_proj_final_agosto']), use_container_width=True)
    
    st.subheader("Conclusão da Questão 2 - Próximos Passos Recomendados")
    st.markdown(
        """
1. **Investigar profundamente o canal `Chat_C` do BOT_A**

   - Revisar fluxos, intents e regras de roteamento específicos desse canal.
   - Validar se há erro de logging ou cálculo de `flag_sessao_retida`.
   - Amostrar conversas dos dias com retenção zerada para entender se o problema é
     de experiência do cliente ou de mensuração.

2. **Atacar os tópicos e assuntos críticos mapeados**

   - Focar em segmentos com retenção atual < 20% e queda > 10 p.p. versus o mês anterior.
   - Para cada um, revisar conteúdo, fluxos de fallback e alterações recentes de negócio.

3. **Monitorar de perto assuntos com performance positiva, mas volátil**

   - Assuntos que melhoraram em agosto, mas ainda têm dias com retenção zerada,
     indicam inconsistência operacional.
   - Comparar dias bons vs ruins, checando relação com campanhas e sazonalidade.

4. **Criar rotina de monitoramento (dashboard / alertas)**

   - Acompanhar diariamente retenção por bot / canal / tópico / assunto e volume de sessões.
   - Implementar alertas para quedas bruscas ou retenção zero em segmentos relevantes.
        """
    )

    # Subdivisão de apêndice
    st.header("Apêndice: Racional Construído para Diagnóstico e Prescrição de Próximos Passos")

    # 3) GRÁFICO HISTÓRICO
    st.subheader("Histórico Mensal: Retenção x Pedido de Atendimento por Chatbot")

    st.markdown(
        """
- **BOT_A**: histórico de retenção inferior ao BOT_B, com trajetória de recuperação na parcial de agosto após queda recente.
- **BOT_B**: trajetória de alta entre maio até julho, com pequeno recuo no parcial de agosto, ainda em patamar elevado frente ao histórico.
        """
    )

    fig_hist, ax = plt.subplots(figsize=(12, 5))

    import numpy as np
    # Retenção - linha cheia
    sns.lineplot(
        data=df_monthly_macro,
        x="session_month",
        y="retencao_pct",
        hue="chatbot",
        palette=palette,
        marker="o",
        linewidth=2,
        legend=False,
        ax=ax,
    )

    # Pedido de atendimento - linha tracejada
    sns.lineplot(
        data=df_monthly_macro,
        x="session_month",
        y="pct_pedido_atendimento",
        hue="chatbot",
        palette=palette,
        marker="o",
        linewidth=2,
        linestyle="--",
        legend=False,
        ax=ax,
    )

    ax.set_xlabel("Mês")
    ax.set_ylabel("Percentual (%)")
    ax.set_title("Histórico Mensal: Retenção x Pedido de Atendimento por Chatbot")
    plt.xticks(rotation=45)
    ax.grid(True)

    custom_lines = [
        Line2D([0], [0], color=palette[bots[0]], lw=2, marker="o", linestyle="-",
               label=f"{bots[0]} - Retenção"),
        Line2D([0], [0], color=palette[bots[0]], lw=2, marker="", linestyle="--",
               label=f"{bots[0]} - Pedido de atendimento"),
        Line2D([0], [0], color=palette[bots[1]], lw=2, marker="o", linestyle="-",
               label=f"{bots[1]} - Retenção"),
        Line2D([0], [0], color=palette[bots[1]], lw=2, marker="", linestyle="--",
               label=f"{bots[1]} - Pedido de atendimento"),
    ]
    ax.legend(handles=custom_lines, title="Métrica", loc="best")

    st.pyplot(fig_hist)

    # 4) MÊS ATUAL vs HISTÓRICO
    st.subheader("Mês Atual x Média Histórica (mesma janela de dias)")

    st.markdown(
        """
Esse comparativo mostra, por bot:

- Como a retenção parcial de agosto se posiciona versus a **média histórica** na mesma janela de dias;
- Como está a relação entre retenção e **pedido de atendimento** frente ao mês imediatamente anterior.
        """
    )
    st.dataframe(format_percent_columns(resumo), use_container_width=True)

    # 5) CORRELAÇÃO (NÍVEL MÉDIO)
    st.subheader("Correlação entre Retenção e Pedido de Atendimento (por Chatbot)")

    st.markdown(
        """
- Para o **BOT_B**, a correlação negativa indica que, em média, mais pedidos de atendimento se associam a menor retenção, como esperado.
- Para o **BOT_A**, a correlação positiva sugere um padrão contra-intuitivo, levantando dúvidas e pontos de atenção sobre possível eficácia do fallback do bot e problemas na mensuração das métricas.
        """
    )

    for bot in bots:
        st.markdown(f"**Chatbot: {bot}**")
        df_bot = df_monthly_macro[df_monthly_macro["chatbot"] == bot]
        corr_matrix = df_bot[["retencao_pct", "pct_pedido_atendimento"]].corr(method="pearson")

        col1, col2 = st.columns(2)
        with col1:
            st.write("Matriz de correlação")
            # aqui NÃO formato, porque correlação não é percentual
            st.dataframe(corr_matrix, use_container_width=True)
        with col2:
            fig_corr, ax_corr = plt.subplots(figsize=(4, 3))
            sns.heatmap(
                corr_matrix,
                annot=True,
                cmap="Blues",
                fmt=".2f",
                vmin=-1,
                vmax=1,
                ax=ax_corr,
            )
            ax_corr.set_title(f"Correlação - {bot}")
            st.pyplot(fig_corr)

    # 6) DETALHAMENTO EM TABELAS
    st.subheader("Detalhamento em Tabelas - Mix, Tópicos e Assuntos")

    st.markdown(
        """
A partir daqui, descemos a granularidade para explicar **o porquê** do comportamento observado:

- Mudanças de mix de **canal** e **tecnologia**;
- Tópicos e assuntos específicos que puxam a retenção para cima ou para baixo;
- Anomalias claras, como o caso de `Chat_C` no BOT_A.
        """
    )

    # --- Mix por canal / tecnologia / tópico / assunto ---
    with st.expander("Mix por Fonte (Canal) - mês atual vs anterior"):
        st.dataframe(format_percent_columns(df_mix_fonte), use_container_width=True)

    with st.expander("Mix por Tecnologia - mês atual vs anterior"):
        st.dataframe(format_percent_columns(df_mix_tecnologia), use_container_width=True)

    with st.expander("Mix por Tópico da Sessão - mês atual vs anterior"):
        st.dataframe(format_percent_columns(df_mix_topico), use_container_width=True)

    with st.expander("Mix por Assunto da Sessão - mês atual vs anterior"):
        st.dataframe(format_percent_columns(df_mix_assunto), use_container_width=True)

    # --- Deep dive Chat_C BOT_A ---
    st.subheader("Deep Dive 1 - Canal `Chat_C` para BOT_A (Retenção Zerada em Agosto)")

    st.markdown(
        """
- **Anomalia clara:** `Chat_C` para BOT_A apresenta retenção zerada em agosto,
  em diversos dias, com ~4,7k sessões impactadas.
- Historicamente, esse canal tinha retenção média em torno de **63%**,
  reforçando a hipótese de **problema de fluxo ou de registro de métrica**.
        """
    )

    st.dataframe(format_percent_columns(deep_fonte), use_container_width=True)
   
    # --- Tópicos e assuntos críticos / positivos ---
    st.subheader("Deep Dive 2 - Tópicos e Assuntos Críticos / Positivos")
    st.markdown(
        """
- **Chatbot A** apresentou 1 tópico crítico com retenção zerada em agosto, mas apenas com 1 dia de amostra, necessitando de mais dados para analisar e decretar alguma anomalia relevante.
- **Chatbot B** apresentou nenhum tópico crítico, todos mantiveram retenção acima de 58%.
- Assuntos críticos identificados para cada chatbot, mostrando consistentemente em todos os meses dias com retenção zerada, no mês de agosto tendo um volume maior de sessões com retenção zerada.
- Em ambos chatbots as tecnologias relacionadas aos assuntos críticos se mostram constantes, no caso do chatbot A a tecnologia TECH_A e no chatbot B a tecnologia TECH_B.
- Assuntos positivos (deltas positivos relevantes na retenção versus mes anterior) identificados para cada chatbot, porém apresentando uma oscilação grande, possuindo dias com retenção zerada.
- Resumo: ambos chatbots apresentaram muita oscilação em diversos assuntos, possuindo dias com retenção zerada e outros dias com retenção alta, mesmo com uma volumetria relevante em cada dia amostral, levantando dúvidas sobre a estabilidade das métricas e dos fluxos em certos assuntos.

        """
    )

    for bot in bots:
        st.markdown(f"### Chatbot {bot}")

        st.markdown("**Tópicos críticos (retencao_atual_pct < 20 e delta_retencao_pp < -10 p.p.)**")
        if topicos_criticos_por_bot[bot]:
            st.write(pd.DataFrame({"topico_da_sessao": topicos_criticos_por_bot[bot]}))
            st.write("Detalhe dos tópicos críticos (mês de agosto):")
            st.dataframe(format_percent_columns(dfs_topicos_criticos[bot]), use_container_width=True)
        else:
            st.write("Nenhum tópico crítico identificado.")

        st.markdown("**Assuntos críticos (retencao_atual_pct < 20 e delta_retencao_pp < -10 p.p.)**")
        if assuntos_criticos_por_bot[bot]:
            st.write(pd.DataFrame({"assunto_da_sessao": assuntos_criticos_por_bot[bot]}))
            st.write("Detalhe dos assuntos críticos (mês de agosto):")
            st.dataframe(format_percent_columns(dfs_assuntos_criticos[bot]), use_container_width=True)
        else:
            st.write("Nenhum assunto crítico identificado.")

        st.markdown("**Tópicos com variação positiva relevante (retencao_atual_pct > 20 e delta_retencao_pp > 10 p.p.)**")
        if topicos_positivos_por_bot[bot]:
            st.write(pd.DataFrame({"topico_da_sessao": topicos_positivos_por_bot[bot]}))
            st.dataframe(format_percent_columns(dfs_topicos_positivos[bot]), use_container_width=True)
        else:
            st.write("Nenhum tópico com variação positiva relevante identificado.")

        st.markdown("**Assuntos com variação positiva relevante**")
        if assuntos_positivos_por_bot[bot]:
            st.dataframe(format_percent_columns(dfs_assuntos_positivos[bot]), use_container_width=True)
        else:
            st.write("Nenhum assunto com variação positiva relevante identificado.")

# ------------------------------------------------------------------
# ABA 3 - QUESTÃO 3
# ------------------------------------------------------------------
with tab3:
    st.header("Questão 3 - Projeção da Retenção até o Final de 2025")

    st.markdown(
        """
<div class="stone-box">
<div class="stone-badge">Resumo executivo questão 3</div>

- O **BOT_A** tende a fechar 2025 em patamar acima do início do ano,
  sustentando a recuperação pós-maio, desde que as anomalias de canal/tópico sejam endereçadas.
- O **BOT_B** deve encerrar o ano em nível elevado de retenção, com leve acomodação após o pico de julho,
  mas ainda acima da média histórica.
- O indicador anual projetado resume o nível esperado de eficiência de cada bot em 2025,
  combinando histórico, projeção de agosto e tendência dos meses futuros.
 </div>
        """,  
        unsafe_allow_html=True,
    )

    st.subheader("Projeção Mensal - Setembro a Dezembro (Tendência Linear Pós-Maio)")
    st.dataframe(format_percent_columns(df_future_trend), use_container_width=True)

    st.subheader("Série 2025 Completa - Real + Agosto Projetado + Projeção Futura")
    st.dataframe(
        format_percent_columns(df_2025_full.sort_values(["chatbot", "session_month"])),
        use_container_width=True,
    )

    st.subheader("Gráfico - Retenção 2025 por Chatbot (Real vs Projetado)")

    for bot in bots:
        df_bot_2025 = df_2025_full[df_2025_full["chatbot"] == bot].copy()
        df_bot_2025 = df_bot_2025.sort_values("session_month")

        df_bot_2025["tipo"] = df_bot_2025["session_month"].apply(
            lambda m: "Projetado" if m >= "2025-08" else "Real"
        )

        fig_bot, ax_bot = plt.subplots(figsize=(10, 4))
        sns.lineplot(
            data=df_bot_2025[df_bot_2025["tipo"] == "Real"],
            x="session_month",
            y="retencao_pct",
            marker="o",
            label="Real",
            ax=ax_bot,
        )
        sns.lineplot(
            data=df_bot_2025[df_bot_2025["tipo"] == "Projetado"],
            x="session_month",
            y="retencao_pct",
            marker="o",
            linestyle="--",
            label="Projetado",
            ax=ax_bot,
        )
        ax_bot.set_title(f"Retenção 2025 - {bot}")
        ax_bot.set_xlabel("Mês")
        ax_bot.set_ylabel("Retenção (%)")
        plt.xticks(rotation=45)
        ax_bot.grid(True)
        st.pyplot(fig_bot)

    st.subheader("Indicador Anual Projetado - Retenção Média 2025")
    st.dataframe(
        format_percent_columns(df_indicador_anual, extra_pct_cols=["retencao_media_2025"]),
        use_container_width=True,
    )

    st.subheader("Racional para desenvolvimento da projeção")
    st.markdown(
"""
Para projetar o restante de 2025, eu parti de uma premissa bem clara:  
**depois de agosto, não estou assumindo nenhuma nova mudança estrutural** (nova tecnologia, mudança forte de regra de negócio etc.).  
Ou seja: a partir de agosto, o bot entra em um **novo platô** e eu quero estimar como esse platô tende a se comportar.

#### 1. Primeiro, entendi como os platôs se comportam no histórico

- Olhei para toda a série mensal de cada bot e marquei os pontos de **disrupção**: meses em que a retenção muda mais de **1,5 p.p. vs mês anterior**.  
  Esses pontos são os “degraus”: mudança de tecnologia, regra, fluxo etc.
- Entre esses degraus, ficam os trechos em que a retenção varia pouco mês a mês.  
  Esses trechos eu trato como **platôs operacionais**, onde o bot já está rodando em “modo normal”.
- Dentro de cada platô, eu analisei apenas as **variações pequenas (≤ 1,5 p.p.)** e calculei:
  - a **variação média por mês** (se o platô costuma subir de leve, cair de leve ou praticamente ficar parado);  
  - o **comportamento de fim de platô**: se, perto do fim, a série costuma dar uma leve caída ou uma leve subida.

#### 2. Depois, transformei isso em um “drift de platô” por bot

- A partir dessas variações, estimei um **drift mensal típico** para cada bot (em p.p./mês).  
  Ele pode ser levemente positivo ou negativo – o que reflete exatamente o que já aconteceu na prática.
- Para evitar projeções irreais, eu **limito o tamanho desse drift por mês**  
  (por exemplo, não deixo passar de ±0,4 p.p. em cada mês projetado).
- Além disso, eu uso o padrão de **fim dos platôs históricos** para definir o **sinal** do drift:
  - se, historicamente, os platôs daquele bot terminam com uma leve queda, o drift projetado tende a ser negativo;
  - se terminam com uma leve alta, o drift tende a ser positivo.

#### 3. Por fim, aplico esse platô aprendido a partir de agosto

- Eu uso a **retenção projetada de agosto** como ponto de partida do novo platô.  
- A partir de setembro, aplico o **drift de platô aprendido** mês a mês, mantendo os valores dentro de uma faixa coerente com o histórico do próprio bot.
- O resultado é um **platô pós-agosto** com pequenas oscilações mensais, parecido com o comportamento que já vimos em platôs anteriores, e não uma reta infinita de crescimento ou queda.

---

### Por que eu não usei regressão linear “reta única”?

Eu decidi **não** usar uma regressão linear simples por alguns motivos:

- A série de retenção não é linear: ela é feita de **saltos (degraus)** seguidos de períodos mais estáveis.  
  Uma reta única mistura esses dois mundos (mudanças estruturais + flutuações normais) e acaba gerando projeções distorcidas.
- Tenho **poucos pontos mensais em cada regime**. Se eu ajusto uma reta só nos últimos meses, o risco é **exagerar a tendência de curtíssimo prazo** (por exemplo, pegar 2–3 meses de alta e assumir que isso vai continuar o ano inteiro).
- Para o negócio, considero mais realista assumir que, **sem nova grande mudança**, o bot entra em um **novo patamar** e oscila em torno dele, em vez de crescer ou cair indefinidamente.

---

### Por que essa estratégia de platô faz sentido aqui?

- Ela conversa diretamente com o que o histórico mostra:  
  **degraus quando algo grande muda + platôs com pequenas oscilações** depois disso.
- É **fácil de explicar**: eu posso dizer literalmente que  
  “**a partir de agosto, o bot tende a se comportar como nos platôs anteriores, com pequenas variações mensais**”.
- A projeção vira um **cenário-base conservador**:
  - mantém o nível de retenção em um intervalo crível, baseado no que já aconteceu;
  - abre espaço para simular cenários:  
    *“e se eu fizer uma nova mudança de tecnologia e criar um novo degrau?”*,
    *“e se eu resolver o problema de Chat_C?”* etc.

Em resumo, eu projetei setembro–dezembro assumindo que **agosto inaugura um novo platô** e que esse platô tende a se comportar de forma parecida com os anteriores do mesmo bot, com pequenos ajustes mensais em vez de uma reta artificial de alta ou queda.
    """ 
    )
















