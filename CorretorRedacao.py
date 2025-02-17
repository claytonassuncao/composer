__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
import json


# Configurando o modelo usando a classe LLM nativa do CrewAI
llm = LLM(    
    model="gpt-4",
    temperature=0.8
)

# Função para configurar o agente
def criar_agente_corretor():
    return Agent(
        role="Corretor de Redação",
        goal="Corrigir erros de ortografia, acentuação, gramática, estrutura frasal e vocabulário do texto: {redacao}.",
        verbose=True,
        memory=True,
        llm=llm,
        backstory="""
            Você é um especialista em língua portuguesa, com vasta experiência em correção de textos e redação de conteúdo.
            Seu objetivo é garantir que o texto seja claro, coeso e gramaticalmente correto, mantendo a essência e a mensagem original.
            Você é formado em Letras, possui mestrado em Linguística e tem experiência em revisão de textos acadêmicos, literários e publicitários.
        """
    )

# Função para criar a tarefa de correção
def criar_tarefa_correcao(agente):
    return Task(
        description="""
            Você irá entregar um texto revisado e corrigido, com base nas instruções fornecidas:
                        
            Instruções:
            - Aponte os erros de ortografia, acentuação, gramática, estrutura frasal e vocabulário do texto.
            - Garanta que o texto siga as normas da língua portuguesa e seja adequado ao público-alvo.
        """,
        expected_output="""
            - Um texto revisado, formatado e corrigido.
            - Erros destacados em **negrito**.
            - Um bloco com o resumo das correções realizadas, formatado com uma cor diferente.
        """,
        agent=agente
    )

# Função para executar a correção
def corrigir_redacao(redacao):
    if len(redacao) < 500:
        return "O texto deve conter no mínimo 500 caracteres."

    agente = criar_agente_corretor()
    tarefa = criar_tarefa_correcao(agente)

    # Criando a tripulação
    equipe = Crew(
        agents=[agente],
        tasks=[tarefa],
        process=Process.sequential
    )

    # Executando a tripulação
    resultado = equipe.kickoff(inputs={"redacao": redacao})

    return resultado

# Interface do Streamlit
st.title("📝 Corretor de Redação")
st.write("Escreva sua redação e solicite que o Agente corrija os erros de ortografia, acentuação, gramática, estrutura frasal e vocabulário.")

# Entrada do usuário (múltiplas linhas)
redacao = st.text_area(
    "Digite aqui a redação que deseja corrigir:",
    height=200
)

# Botão para gerar a correção
if st.button("Corrigir Redação"):
    with st.spinner("Corrigindo seu texto. Aguarde..."):
        try:
            resultado = corrigir_redacao(redacao)

            if isinstance(resultado, str) and resultado == "O texto deve conter no mínimo 500 caracteres.":
                st.warning(resultado)
            else:
                st.success("✅ Redação corrigida com sucesso!")

                # Processar e exibir o texto formatado em HTML
                st.markdown("### ✍️ Redação Corrigida:")

                if isinstance(resultado, str):
                    try:
                        resultado_json = json.loads(resultado)
                        texto_formatado = resultado_json.get("raw", resultado)
                    except json.JSONDecodeError:
                        texto_formatado = resultado
                elif isinstance(resultado, dict):
                    texto_formatado = resultado.get("raw", str(resultado))
                else:
                    texto_formatado = str(resultado)

                # Formatando o texto corrigido em HTML
                texto_html = f"""
                    <div style="text-align: justify; font-size: 16px; line-height: 1.6;">
                        {texto_formatado}
                    </div>
                """

                # Bloco de resumo estilizado
                resumo_html = """
                    <div style="background-color:#f0f0f0; padding:15px; border-radius:5px; margin-top:20px;">
                        <strong>📌 Resumo das correções:</strong><br>
                        - Ortografia e gramática corrigidas.<br>
                        - Estrutura frasal aprimorada.<br>
                        - Coesão e coerência reforçadas.<br>
                    </div>
                """

                # Exibir no Streamlit com suporte a HTML
                st.markdown(texto_html, unsafe_allow_html=True)
                st.markdown(resumo_html, unsafe_allow_html=True)

        except Exception as e:
            st.error("❌ Ocorreu um erro ao corrigir a redação.")
            st.write(str(e))

