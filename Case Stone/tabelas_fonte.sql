CREATE TABLE silver_sessions (
    session_id STRING,
    session_date DATE,

    chatbot STRING,                   -- bot_a / bot_b
    fonte STRING,                     -- chat_a / chat_b
    tecnologia_do_chatbot STRING,     -- tech_a / tech_b

    topico_da_sessao STRING,
    assunto_da_sessao STRING,

    flag_sessao_retida BOOLEAN,       -- True = chatbot resolveu sozinho
    flag_pedido_atendimento BOOLEAN,  -- True = pediu humano

    dt_ingest TIMESTAMP
);

SELECT
    session_date,
    chatbot,
    fonte,
    tecnologia_do_chatbot,
    topico_da_sessao,
    assunto_da_sessao,

    COUNT(*) AS sessoes_total,
    SUM(CASE WHEN flag_sessao_retida = TRUE THEN 1 ELSE 0 END) AS sessoes_retidas,
    SUM(CASE WHEN flag_pedido_atendimento = TRUE THEN 1 ELSE 0 END) AS sessoes_com_pedido_de_atendimento

FROM silver_sessions
GROUP BY
    session_date,
    chatbot,
    fonte,
    tecnologia_do_chatbot,
    topico_da_sessao,
    assunto_da_sessao
