import os
from typing import Dict, Any
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.agent_toolkits import MCPToolkit
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class CurrencyAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("EVOLUTION_API_KEY"),
            openai_api_base=os.getenv("EVOLUTION_API_BASE"),
            model_name="gpt-3.5-turbo",
            temperature=0
        )
        
        toolkit = MCPToolkit(
            mcp_server_command=["python", os.path.join(os.path.dirname(__file__), "../mcp_server/server.py")]
        )
        
        self.tools = toolkit.get_tools()
        
        prompt_template = """
        Ты финансовый ассистент для конвертации валют. Ты должен помогать пользователям:
        1. Конвертировать суммы между валютами
        2. Показывать текущие курсы валют
        3. Предоставлять список доступных валют
        
        Всегда уточняй валютные коды (3 буквы, например USD, EUR, RUB).
        При конвертации показывай не только результат, но и использованный курс.
        
        История чата:
        {chat_history}
        
        Вопрос: {input}
        
        {agent_scratchpad}
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["chat_history", "input", "agent_scratchpad"]
        )
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """Выполняет запрос к агенту"""
        try:
            result = self.agent_executor.invoke({"input": question})
            return {
                "success": True,
                "answer": result["output"],
                "source": "currency_mcp_agent"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "suggestion": "Попробуйте переформулировать запрос или уточнить валютные коды"
            }
    
    def clear_memory(self):
        """Очищает историю разговора"""
        self.memory.clear()

def create_simple_agent():
    """Создает упрощенного агента для демонстрации"""
    from langchain.agents import initialize_agent
    
    llm = ChatOpenAI(
        openai_api_key=os.getenv("EVOLUTION_API_KEY"),
        openai_api_base=os.getenv("EVOLUTION_API_BASE"),
        model_name="gpt-3.5-turbo",
        temperature=0
    )
    
    toolkit = MCPToolkit(
        mcp_server_command=["python", os.path.join(os.path.dirname(__file__), "../mcp_server/server.py")]
    )
    
    tools = toolkit.get_tools()
    
    return initialize_agent(
        tools=tools,
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True
    )

if __name__ == "__main__":
    agent = CurrencyAgent()
    
    examples = [
        "Сколько будет 100 долларов в рублях?",
        "Какой курс евро к доллару?",
        "Покажи список доступных валют",
        "Конвертируй 500 евро в японские йены"
    ]
    
    for example in examples:
        print(f"\nВопрос: {example}")
        result = agent.query(example)
        print(f"Ответ: {result}")
