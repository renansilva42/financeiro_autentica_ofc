from flask import Flask, render_template, request, jsonify, redirect, url_for
from services.omie_service import OmieService
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Em produção, use uma chave mais segura

# Inicializar o serviço do Omie
omie_service = OmieService()

@app.context_processor
def inject_current_year():
    """Injeta o ano atual em todos os templates"""
    return {'current_year': datetime.now().year}

@app.route('/')
def index():
    """Página inicial com dashboard"""
    try:
        stats = omie_service.get_clients_stats()
        return render_template('index.html', stats=stats)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/clients')
def clients():
    """Lista todos os clientes com paginação"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        per_page = 20
        
        if search:
            all_clients = omie_service.search_clients(search)
        else:
            all_clients = omie_service.get_all_clients()
        
        # Paginação manual
        total = len(all_clients)
        start = (page - 1) * per_page
        end = start + per_page
        clients_page = all_clients[start:end]
        
        # Calcular informações de paginação
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': page - 1 if has_prev else None,
            'next_num': page + 1 if has_next else None
        }
        
        return render_template('clients.html', 
                             clients=clients_page, 
                             pagination=pagination,
                             search=search)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/client/<int:client_id>')
def client_detail(client_id):
    """Detalhes de um cliente específico"""
    try:
        client = omie_service.get_client_by_id(client_id)
        if not client:
            return render_template('error.html', error='Cliente não encontrado')
        
        return render_template('client_detail.html', client=client)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/api/clients')
def api_clients():
    """API endpoint para buscar clientes"""
    try:
        search = request.args.get('search', '', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if search:
            clients = omie_service.search_clients(search)
        else:
            clients = omie_service.get_all_clients()
        
        # Paginação
        total = len(clients)
        start = (page - 1) * per_page
        end = start + per_page
        clients_page = clients[start:end]
        
        return jsonify({
            'clients': clients_page,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/client/<int:client_id>')
def api_client_detail(client_id):
    """API endpoint para buscar um cliente específico"""
    try:
        client = omie_service.get_client_by_id(client_id)
        if not client:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
        return jsonify(client)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint para estatísticas"""
    try:
        stats = omie_service.get_clients_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.template_filter('format_cpf_cnpj')
def format_cpf_cnpj(value):
    """Filtro para formatar CPF/CNPJ"""
    if not value:
        return ''
    
    # Remove caracteres não numéricos
    numbers = ''.join(filter(str.isdigit, value))
    
    if len(numbers) == 11:  # CPF
        return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:9]}-{numbers[9:]}"
    elif len(numbers) == 14:  # CNPJ
        return f"{numbers[:2]}.{numbers[2:5]}.{numbers[5:8]}/{numbers[8:12]}-{numbers[12:]}"
    else:
        return value

@app.template_filter('format_phone')
def format_phone(ddd, number):
    """Filtro para formatar telefone"""
    if not ddd or not number:
        return ''
    
    # Remove caracteres não numéricos
    ddd_clean = ''.join(filter(str.isdigit, ddd))
    number_clean = ''.join(filter(str.isdigit, number))
    
    if len(number_clean) == 9:  # Celular
        return f"({ddd_clean}) {number_clean[:5]}-{number_clean[5:]}"
    elif len(number_clean) == 8:  # Fixo
        return f"({ddd_clean}) {number_clean[:4]}-{number_clean[4:]}"
    else:
        return f"({ddd_clean}) {number_clean}"

@app.template_filter('format_date')
def format_date(value):
    """Filtro para formatar data"""
    if not value:
        return ''
    
    try:
        # Assumindo formato dd/mm/yyyy
        if '/' in value:
            day, month, year = value.split('/')
            return f"{day}/{month}/{year}"
        return value
    except:
        return value

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Página não encontrada'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Erro interno do servidor'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)