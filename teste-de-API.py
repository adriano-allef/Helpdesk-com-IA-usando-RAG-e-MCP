import google.generativeai as genai

# Substitua pela sua chave real temporariamente para testar
genai.configure(api_key="chaveapiaqui")

print("Modelos de Embedding disponíveis para a sua chave:")
# A função list_models() faz a mesma pergunta que o erro sugeriu!
for modelo in genai.list_models():
    # Filtramos apenas os modelos que suportam a criação de vetores (embedContent)
    if 'embedContent' in modelo.supported_generation_methods:
        print(f"- Nome: {modelo.name}")


print("Modelos Conversacionais disponíveis para a sua chave:")

for modelo in genai.list_models():
    # Agora estamos a filtrar pelos modelos de GERAÇÃO DE TEXTO/CHAT
    if 'generateContent' in modelo.supported_generation_methods:
        print(f"- Nome: {modelo.name}")