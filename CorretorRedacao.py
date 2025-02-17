import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
import json

gpt4o = 'gpt-4o'

llm = LLM(
    model="gpt-4",
    temperature=0.8
)

# Função para configurar o agente
def criar_musica(redacao):
    # Definindo o agente
    agent_corretor_gramatical = Agent(
        role="Corretor de Redação",
        goal="Corrigir erros de ortografia, acentuação, gramática, estrutura frasal, vocabulario do texto: {redacao}.",
        verbose=True,
        memory=True,
        llm=llm,
        backstory="""
			Você é um especialista em lingua portuguesa, com vasta experiência em correção de textos e redação de conteúdo.
			Seu objetivo é garantir que o texto seja claro, coeso e gramaticalmente correto, mantendo a essência e a mensagem original.
			Além disso, você deve garantir que o texto siga as normas da língua portuguesa e seja adequado ao público-alvo.
            Você é formado em Letras e possui experiência em revisão de textos acadêmicos, literários e publicitários.
            Você tem mestrado em Linguística e é apaixonado por línguas e culturas.
            Desde jovem você se destacou na escrita e na correção de redações, sendo premiado em diversos concursos literários.
        """
    )

    # Definindo a tarefa
    correcao_texto = Task(
        description="""
            Você irá entregar um texto revisado e corrigido, com base nas instruções fornecidas:
                        
            Instruções:
            - Aponte os erros de ortografia, acentuação, gramática, estrutura frasal, vocabulário e coesão do texto.
			- Garanta que o texto siga as normas da língua portuguesa e seja adequado ao público-alvo.			            
        """,
        expected_output="""
            - Um texto revisado, com base nas instruções fornecidas.
            Instruções:
            - Texto justificado, formatado.
            - Aponte os erros de ortografia, acentuação, gramática, estrutura frasal, vocabulário e coesão do texto e os coloque em negrito.			
			- Garanta que o texto siga as normas da língua portuguesa e seja adequado ao público-alvo.			
            - Escreva um bloco com o resumo da revisão realizada e justifique cada uma delas, formate o bloco com uma cor diferente.            
        """,
        agent=agent_corretor_gramatical
    )

    # Criando a tripulação
    equipe = Crew(
        agents=[agent_corretor_gramatical],
        tasks=[correcao_texto],
        process=Process.sequential
    )

    # Executando a tripulação
    result = equipe.kickoff(inputs={"redacao": redacao})

    return result

# Interface do Streamlit
st.title("Corretor de Redação")
st.write("Escreva sua redação e solicite que o Agente corrija os erros de ortografia, acentuação, gramática, estrutura frasal, vocabulário e coesão do texto.")

# Entrada do usuário
redacao = st.text_input(
    "Digite aqui a redação que deseja corrigir:",
	"A redação deve conter no mínimo 500 caracteres."
)

# Botão para gerar a correção
if st.button("Corrigir Redação"):
    with st.spinner("Corrigindo seu texto. Aguarde..."):
        try:
            resultado = criar_musica(redacao)

            st.success("Redação corrigida com sucesso!")

            # Processar e exibir o texto formatado
            st.markdown("### Redação Corrigida:")
            if isinstance(resultado, str):
                try:
                    # Tenta converter para JSON e extrair o campo `raw`
                    resultado_json = json.loads(resultado)
                    texto_formatado = resultado_json.get("raw", resultado)
                except json.JSONDecodeError:
                    # Caso não seja JSON, trata como texto normal
                    texto_formatado = resultado
            elif isinstance(resultado, dict):
                texto_formatado = resultado.get("raw", str(resultado))
            else:
                texto_formatado = str(resultado)

            # Exibir o texto formatado diretamente
            st.markdown(texto_formatado)

        except Exception as e:
            st.error("Ocorreu um erro ao compor a música.")
            st.write(str(e))
