# riddles.py

RIDDLES = [
    {
        'id': 1,
        'text': "Sou leve como uma pena, mas nem o homem mais forte consegue me segurar por muito tempo. O que sou eu?",
        'answer': "Respiração"
    },
    {
        'id': 2,
        'text': "Tenho cidades, mas não casas; florestas, mas não árvores; e água, mas não peixes. O que sou eu?",
        'answer': "Mapa"
    },
    {
        'id': 3,
        'text': "Devoro tudo: pássaros, feras, árvores, flores; mordo o ferro, o aço; esmago cidades, roo montanhas. O que sou eu?",
        'answer': "Tempo"
    },
    {
        'id': 4,
        'text': "Falo sem boca e ouço sem orelhas. Não tenho corpo, mas ganho vida com o vento. O que sou eu?",
        'answer': "Eco"
    }
    # Adicione mais charadas aqui se desejar!
]

def get_riddle_by_id(riddle_id: int):
    """Retorna os dados completos de uma charada pelo seu ID."""
    for riddle in RIDDLES:
        if riddle['id'] == riddle_id:
            return riddle
    return None # Retorna None se a charada não for encontrada

def get_next_riddle_id(current_riddle_id: int):
    """Retorna o ID da próxima charada na sequência, ou None se for a última."""
    current_index = -1
    for i, riddle in enumerate(RIDDLES):
        if riddle['id'] == current_riddle_id:
            current_index = i
            break
    
    if current_index != -1 and current_index + 1 < len(RIDDLES):
        return RIDDLES[current_index + 1]['id']
    return None # Última charada ou não encontrada

def get_first_riddle_id():
    """Retorna o ID da primeira charada da lista."""
    return RIDDLES[0]['id'] if RIDDLES else None