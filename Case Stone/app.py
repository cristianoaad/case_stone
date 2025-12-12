import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

# IMPORTA SEU SCRIPT DE ANÁLISE
import script  # <- seu arquivo script.py

sns.set(style="whitegrid")

# ------------------------------------------------------------------
# RECUPERA OBJETOS DO script.py
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# CONFIG STREAMLIT + ESTILO STONE
# ------------------------------------------------------------------
STONE_GREEN = "#00A94F"

st.set_page_config(
    page_title="Case - Data Analyst Stone - Cristiano Diniz",
    layout="wide"
)

# CSS com cores da Stone
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
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<h1 style="margin-bottom:0.5rem;">Case Técnico - Data Analyst (Chatbots)</h1>',
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

    st.subheader("Código SQL (arquivo Questao1-tabelas_fonte.sql)")
    try:
        with open("Questao1-tabelas_fonte.sql", "r", encoding="utf-8") as f:
            sql_text = f.read()
        st.code(sql_text, language="sql")
    except FileNotFoundError:
        st.warning("Arquivo `Questao1-tabelas_fonte.sql` não encontrado na pasta do app.")

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

    st.markdown(
        """
**Resumo da Questão 1**

- A tabela `silver_sessions` guarda o evento transacional por sessão, com flags de retenção e pedido de atendimento.
- O SELECT agrega para uma granularidade diária por bot / canal / tecnologia / tópico / assunto,
  que é exatamente a base utilizada nas análises das questões 2 e 3.
        """
    )

# ------------------------------------------------------------------
# ABA 2 - QUESTÃO 2
# ------------------------------------------------------------------
with tab2:
    st.header("Questão 2 - Diagnóstico da Retenção & Próximos Passos")

    # =========================
    # 1) CONCLUSÕES GERAIS
    # =========================
    st.markdown(

        """
        <div class="stone-box">
        <div class="stone-badge">Resumo executivo</div>
        <b>Principais achados até o momento:</b><br>
        • Ambos chatbots apresentam uma retenção relativamente estável até maio/2025, quando ocorre um ponto de disrupção (provável ajuste de regras e/ou mudança tecnológica).<br>
        • O <b>BOT_B</b> opera em patamar de retenção historicamente mais alto, com forte crescimento entre maio e julho e leve acomodação na parcial de agosto, ainda em nível elevado.<br>
        • O <b>BOT_A</b> tem retenção histórica inferior, mas mantém um gap relativamente estável para o <b>BOT_B</b>. Após a queda observada em maio, apresenta sinais de <b>recuperação em agosto</b> em relação a julho e ao histórico pré-disrupção.<br>
        • Há <b>anomalia clara</b> no canal <b>Chat_C do BOT_A</b>, com retenção zerada em agosto apesar de histórico médio &gt; 60%, indicando potencial problema de fluxo ou de marcação de métrica e não apenas piora de performance do bot.<br>
        • Alguns <b>tópicos/assuntos específicos</b> puxam a retenção para baixo em agosto (retenção &lt; 20% e queda &gt; 10 p.p. vs julho), enquanto outros mostram evolução positiva, porém com comportamento ainda volátil (dias muito bons e dias com retenção zerada).<br>
        • A análise de correlação mostra que, para o <b>BOT_B</b>, mais pedidos de atendimento tendem a se associar a menor retenção (relação negativa esperada), enquanto para o <b>BOT_A</b> há relação positiva contraintuitiva, levantando hipóteses de problemas de logging/definição de flags em alguns segmentos.<br>
        • A projeção de agosto indica que, <b>uma vez tratadas as anomalias de canal e dos principais tópicos/assuntos</b>, ambos os bots tendem a fechar o mês em patamar igual ou ligeiramente superior ao histórico recente pós-maio.<br>
        <br>
        <b>Highlights (pontos positivos):</b><br>
        • BOT_B sustentando retenção em nível alto mesmo com acomodação em agosto.<br>
        • BOT_A mostrando trajetória de recuperação na parcial de agosto, após a queda entre maio e julho.<br>
        • Identificação clara de segmentos com variação positiva de retenção, que podem ser usados como referências de boas práticas.<br>
        <br>
        <b>Lowlights (pontos de atenção):</b><br>
        • Retenção zerada recorrente em <b>Chat_C - BOT_A</b> no mês de agosto, com volume relevante de sessões impactadas.<br>
        • Tópicos e assuntos com retenção muito baixa e queda forte vs julho, concentrando boa parte da perda de performance do mês.<br>
        • Alta volatilidade diária em vários assuntos (dias com retenção alta alternando com dias zerados), sugerindo fragilidade operacional ou dependência de condições externas ainda não mapeadas.<br>
        <br>
        <b>Estamos indo bem em agosto?</b><br>
        • Em termos de <b>nível geral</b>, agosto não representa um cenário de crise: o BOT_B permanece em patamar alto e o BOT_A recupera parte da perda após maio.<br>
        • Porém, o mês expõe <b>pontos estruturais de risco</b> (principalmente em Chat_C do BOT_A e em alguns tópicos/assuntos específicos) que, se não forem tratados, podem deteriorar a retenção nos próximos meses.<br>
        • Portanto, agosto deve ser lido como um <b>mês de atenção e correção</b>: o agregado ainda é bom, mas há sinais claros de onde a performance pode deteriorar ou ser consolidada.
        </div>

        """,
        unsafe_allow_html=True,
    )

    # =========================
    # 2) GRÁFICO HISTÓRICO
    # =========================
    st.subheader("Histórico Mensal: Retenção x Pedido de Atendimento por Chatbot")

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

    st.markdown(
        """
- **BOT_A**: histórico de retenção inferior ao BOT_B, com trajetória de recuperação na parcial de agosto após queda recente.
- **BOT_B**: trajetória de alta entre maio até julho, com pequeno recuo no parcial de agosto, ainda em patamar elevado frente ao histórico.
        """
    )

    # =========================
    # 3) MÊS ATUAL vs HISTÓRICO
    # =========================
    st.subheader("Mês Atual x Média Histórica (mesma janela de dias)")
    st.dataframe(resumo, use_container_width=True)

    st.markdown(
        """
Esse comparativo mostra, por bot:

- Como a retenção parcial de agosto se posiciona versus a **média histórica** na mesma janela de dias;
- Como está a relação entre retenção e **pedido de atendimento** frente ao mês imediatamente anterior.
        """
    )

    # =========================
    # 4) PROJEÇÃO DE AGOSTO
    # =========================
    st.subheader("Projeção de Fechamento de Agosto (por Chatbot)")
    st.dataframe(df_projecoes, use_container_width=True)

    st.markdown(
        """
A projeção de agosto responde ao pedido **“Faça uma projeção de como fecharemos agosto”**:

- Usa a retenção média observada nos **dias 1-14**;
- Calcula um **fator histórico 1-14 → 15-31** com base em maio, junho e julho;
- Combina os dois para estimar a **retenção projetada para o mês cheio** por chatbot.
        """
    )

    # =========================
    # 5) CORRELAÇÃO (NÍVEL MÉDIO)
    # =========================
    st.subheader("Correlação entre Retenção e Pedido de Atendimento (por Chatbot)")

    for bot in bots:
        st.markdown(f"**Chatbot: {bot}**")
        df_bot = df_monthly_macro[df_monthly_macro["chatbot"] == bot]
        corr_matrix = df_bot[["retencao_pct", "pct_pedido_atendimento"]].corr(method="pearson")

        col1, col2 = st.columns(2)
        with col1:
            st.write("Matriz de correlação")
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

    st.markdown(
        """
- Para o **BOT_B**, a correlação negativa indica que, em média, mais pedidos de atendimento se associam a menor retenção, como esperado.
- Para o **BOT_A**, a correlação positiva sugere um padrão contra-intuitivo, levantando dúvidas e pontos de atenção sobre possível eficácia do fallback do bot e problemas na mensuração das métricas.
        """
    )

    # =========================
    # 6) DETALHAMENTO EM TABELAS
    # =========================
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
        st.dataframe(df_mix_fonte, use_container_width=True)

    with st.expander("Mix por Tecnologia - mês atual vs anterior"):
        st.dataframe(df_mix_tecnologia, use_container_width=True)

    with st.expander("Mix por Tópico da Sessão - mês atual vs anterior"):
        st.dataframe(df_mix_topico, use_container_width=True)

    with st.expander("Mix por Assunto da Sessão - mês atual vs anterior"):
        st.dataframe(df_mix_assunto, use_container_width=True)

    # --- Deep dive Chat_C BOT_A ---
    st.subheader("Deep Dive 1 - Canal `Chat_C` para BOT_A (Retenção Zerada em Agosto)")
    st.dataframe(deep_fonte, use_container_width=True)
    st.markdown(
        """
- **Anomalia clara:** `Chat_C` para BOT_A apresenta retenção zerada em agosto,
  em diversos dias, com ~4,7k sessões impactadas.
- Historicamente, esse canal tinha retenção média em torno de **63%**,
  reforçando a hipótese de **problema de fluxo ou de registro de métrica**.
        """
    )

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
            st.dataframe(dfs_topicos_criticos[bot], use_container_width=True)
        else:
            st.write("Nenhum tópico crítico identificado.")

        st.markdown("**Assuntos críticos (retencao_atual_pct < 20 e delta_retencao_pp < -10 p.p.)**")
        if assuntos_criticos_por_bot[bot]:
            st.write(pd.DataFrame({"assunto_da_sessao": assuntos_criticos_por_bot[bot]}))
            st.write("Detalhe dos assuntos críticos (mês de agosto):")
            st.dataframe(dfs_assuntos_criticos[bot], use_container_width=True)
        else:
            st.write("Nenhum assunto crítico identificado.")

        st.markdown("**Tópicos com variação positiva relevante (retencao_atual_pct > 20 e delta_retencao_pp > 10 p.p.)**")
        if topicos_positivos_por_bot[bot]:
            st.write(pd.DataFrame({"topico_da_sessao": topicos_positivos_por_bot[bot]}))
            st.dataframe(dfs_topicos_positivos[bot], use_container_width=True)
        else:
            st.write("Nenhum tópico com variação positiva relevante identificado.")

        st.markdown("**Assuntos com variação positiva relevante**")
        if assuntos_positivos_por_bot[bot]:
            st.write(pd.DataFrame({"assunto_da_sessao": assuntos_positivos_por_bot[bot]}))
            st.dataframe(dfs_assuntos_positivos[bot], use_container_width=True)
        else:
            st.write("Nenhum assunto com variação positiva relevante identificado.")

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

# ------------------------------------------------------------------
# ABA 3 - QUESTÃO 3
# ------------------------------------------------------------------
with tab3:
    st.header("Questão 3 - Projeção da Retenção até o Final de 2025")

    st.subheader("Projeção Mensal - Setembro a Dezembro (Tendência Linear Pós-Maio)")
    st.dataframe(df_future_trend, use_container_width=True)

    st.markdown(
        """
Para projetar setembro a dezembro:

- Utilizamos a série mais recente (maio, junho, julho + agosto projetado);
- Ajustamos uma **tendência linear** por chatbot;
- Projetamos os pontos correspondentes a setembro-dezembro, limitando os valores a 0-100%.

Isso captura a tendência recente dos bots sem depender de suposições irreais.
        """
    )

    st.subheader("Série 2025 Completa - Real + Agosto Projetado + Projeção Futura")
    st.dataframe(df_2025_full.sort_values(["chatbot", "session_month"]),
                 use_container_width=True)

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
    st.dataframe(df_indicador_anual, use_container_width=True)

    st.markdown(
        """
**Resumo executivo da questão 3:**

- O **BOT_A** tende a fechar 2025 em patamar acima do início do ano,
  sustentando a recuperação pós-maio, desde que as anomalias de canal/tópico sejam endereçadas.
- O **BOT_B** deve encerrar o ano em nível elevado de retenção, com leve acomodação após o pico de julho,
  mas ainda acima da média histórica.
- O indicador anual projetado resume o nível esperado de eficiência de cada bot em 2025,
  combinando histórico, projeção de agosto e tendência dos meses futuros.
        """
    )
