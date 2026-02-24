import google.generativeai as genai

# Substitua pela sua chave real temporariamente para testar
genai.configure(api_key="cole a chave aqui")

print("Modelos de Embedding disponíveis para a sua chave:")
# A função list_models() faz a mesma pergunta que o erro sugeriu!
for modelo in genai.list_models():
    # Filtramos apenas os modelos que suportam a criação de vetores (embedContent)
    if 'embedContent' in modelo.supported_generation_methods:
        print(f"- Nome: {modelo.name}")