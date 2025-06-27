from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_session import Session
from services.omie_service import OmieService
from services.auth_service import AuthService
from services.background_service import background_service
from services.startup_service import initialize_startup_service
from utils.auth_decorators import login_required, logout_required
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Em produção, use uma chave mais segura

# Configurar sessões
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# Inicializar serviços
omie_service = OmieService()

# Inicializar serviço de startup para pré-carregamento
startup_service = initialize_startup_service(omie_service)

# Inicializar serviço de autenticação com tratamento de erro
auth_service = None
try:
    auth_service = AuthService()
    print("✅ Serviço de autenticação inicializado com sucesso")
except Exception as e:
    print(f"⚠️  Aviso: Não foi possível inicializar o serviço de autenticação: {e}")
    print("   Verifique se as variáveis SUPABASE_URL e SUPABASE_KEY estão configuradas corretamente no arquivo .env")
    print("   A aplicação continuará funcionando, mas sem autenticação.")

# Iniciar pré-carregamento de dados
print("🚀 Iniciando pré-carregamento de dados...")
startup_service.start_preload()

@app.context_processor
def inject_current_year():
    """Injeta o ano atual em todos os templates"""
    return {'current_year': datetime.now().year}

@app.context_processor
def inject_user():
    """Injeta dados do usuário logado em todos os templates"""
    user_data = None
    if auth_service and 'user_id' in session:
        try:
            user_data = auth_service.get_user_by_id(session['user_id'])
        except Exception as e:
            print(f"Erro ao buscar dados do usuário: {e}")
    return {'current_user': user_data}

@app.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    """Página de login"""
    # Verificar se o serviço de autenticação está disponível
    if not auth_service:
        flash('Serviço de autenticação não disponível. Verifique a configuração do Supabase.', 'error')
        return render_template('login.html')
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email e senha são obrigatórios.', 'error')
            return render_template('login.html')
        
        try:
            # Validar formato do email
            if not auth_service.validate_email(email):
                flash('Formato de email inválido.', 'error')
                return render_template('login.html')
            
            # Tentar autenticar o usuário
            user = auth_service.authenticate_user(email, password)
            
            if user:
                # Login bem-sucedido
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                session['user_name'] = user.get('name', email)
                
                flash(f'Bem-vindo, {user.get("name", email)}!', 'success')
                
                # Redirecionar para a página que o usuário tentou acessar ou para o dashboard
                next_url = session.pop('next_url', None)
                return redirect(next_url or url_for('index'))
            else:
                flash('Email ou senha incorretos.', 'error')
        except Exception as e:
            flash(f'Erro na autenticação: {str(e)}', 'error')
            print(f"Erro na autenticação: {e}")
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    user_name = session.get('user_name', 'Usuário')
    session.clear()
    flash(f'Até logo, {user_name}!', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Página inicial com dashboard"""
    try:
        stats = omie_service.get_clients_stats()
        return render_template('index.html', stats=stats)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/clients')
@login_required
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
@login_required
def client_detail(client_id):
    """Detalhes de um cliente específico"""
    try:
        client = omie_service.get_client_by_id(client_id)
        if not client:
            return render_template('error.html', error='Cliente não encontrado')
        
        return render_template('client_detail.html', client=client)
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/services')
@login_required
def services():
    """Dashboard de Serviços"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        month_filter = request.args.get('month', '', type=str)
        per_page = 20
        
        # Verificar se há dados em cache primeiro
        print(f"Buscando ordens de serviço - página {page}, busca: '{search}', mês: '{month_filter}'")
        
        # Tentar buscar do cache primeiro (com tempo de vida estendido para serviços)
        cache_key = omie_service._get_cache_key("get_all_service_orders", max_pages=None)
        cached_orders = omie_service._get_from_cache(cache_key, use_service_expiry=True)
        
        if cached_orders is not None:
            print(f"Dados carregados do cache: {len(cached_orders)} ordens")
            all_orders = cached_orders
        else:
            print("Cache vazio, carregando dados da API...")
            # Se não há cache, carregar com estratégia otimizada
            all_orders = omie_service.get_all_service_orders()
            print(f"Total de ordens carregadas da API: {len(all_orders)}")
        
        # Buscar mapeamento de clientes (código -> nome)
        print("Buscando mapeamento de nomes de clientes...")
        try:
            client_name_mapping = omie_service.get_client_name_mapping()
        except Exception as e:
            print(f"Erro ao carregar mapeamento de clientes: {str(e)}")
            client_name_mapping = {}
        
        # Buscar mapeamento de vendedores (código -> nome)
        print("Buscando mapeamento de nomes de vendedores...")
        try:
            seller_name_mapping = omie_service.get_seller_name_mapping()
        except Exception as e:
            print(f"Erro ao carregar mapeamento de vendedores: {str(e)}")
            seller_name_mapping = {}
        
        # Filtrar por mês se especificado
        if month_filter:
            filtered_orders = []
            for order in all_orders:
                cabecalho = order.get('Cabecalho', {})
                date_str = cabecalho.get('dDtPrevisao', '')
                if date_str:
                    try:
                        # Extrair mês/ano da data (formato dd/mm/yyyy)
                        month_year = "/".join(date_str.split("/")[1:])  # mm/yyyy
                        if month_year == month_filter:
                            filtered_orders.append(order)
                    except:
                        pass
            all_orders = filtered_orders
        
        # Filtrar por busca se necessário
        if search:
            search_lower = search.lower()
            filtered_orders = []
            for order in all_orders:
                cabecalho = order.get('Cabecalho', {})
                observacoes = order.get('Observacoes', {})
                
                # Buscar nome do cliente
                client_code = cabecalho.get('nCodCli', '')
                client_name = client_name_mapping.get(client_code, '').lower()
                
                # Buscar nome do vendedor
                seller_code = cabecalho.get('nCodVend', '')
                seller_name = seller_name_mapping.get(seller_code, '').lower()
                
                # Buscar nos campos corretos da estrutura da API, incluindo nome do cliente e vendedor
                if (search_lower in str(client_code).lower() or
                    search_lower in client_name or
                    search_lower in str(cabecalho.get('cNumOS', '')).lower() or
                    search_lower in str(cabecalho.get('nCodOS', '')).lower() or
                    search_lower in str(cabecalho.get('nCodVend', '')).lower() or
                    search_lower in seller_name or
                    search_lower in observacoes.get('cObsOS', '').lower()):
                    filtered_orders.append(order)
            all_orders = filtered_orders
        
        # Ordenar por data de previsão (mais recentes primeiro)
        def parse_date(date_str):
            """Converte data dd/mm/yyyy para objeto datetime para ordenação"""
            try:
                if date_str:
                    day, month, year = date_str.split('/')
                    return datetime(int(year), int(month), int(day))
                return datetime.min  # Data mínima para ordens sem data
            except:
                return datetime.min
        
        all_orders.sort(key=lambda order: parse_date(order.get('Cabecalho', {}).get('dDtPrevisao', '')), reverse=True)
        
        # Paginação manual
        total = len(all_orders)
        start = (page - 1) * per_page
        end = start + per_page
        orders_page = all_orders[start:end]
        
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
        
        # Buscar estatísticas (sem filtro para manter visão geral) com tratamento de erro
        print("Buscando estatísticas de ordens de serviço...")
        try:
            stats = omie_service.get_service_orders_stats()
        except Exception as e:
            print(f"Erro ao carregar estatísticas: {str(e)}")
            stats = {
                "total_orders": len(all_orders),
                "total_value": 0,
                "average_value": 0,
                "by_client": {},
                "top_clients": [],
                "by_status": {},
                "by_service_type": {},
                "top_services": [],
                "by_technician": {},
                "monthly_stats": {},
                "monthly_values": {}
            }
        
        # Se há filtro de mês, calcular estatísticas específicas do mês
        monthly_stats = None
        if month_filter:
            print(f"Buscando estatísticas mensais para {month_filter}...")
            try:
                monthly_stats = omie_service.get_monthly_service_stats(month_filter)
            except Exception as e:
                print(f"Erro ao carregar estatísticas mensais: {str(e)}")
                monthly_stats = None
        
        # Buscar lista de meses disponíveis para o filtro
        print("Buscando meses disponíveis...")
        try:
            available_months = omie_service.get_available_months_for_services()
        except Exception as e:
            print(f"Erro ao carregar meses disponíveis: {str(e)}")
            available_months = []
        
        return render_template('services.html', 
                             orders=orders_page, 
                             pagination=pagination,
                             stats=stats,
                             monthly_stats=monthly_stats,
                             search=search,
                             month_filter=month_filter,
                             available_months=available_months,
                             client_name_mapping=client_name_mapping,
                             seller_name_mapping=seller_name_mapping)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/api/clients')
@login_required
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
@login_required
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
@login_required
def api_stats():
    """API endpoint para estatísticas"""
    try:
        stats = omie_service.get_clients_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/services')
@login_required
def api_services():
    """API endpoint para ordens de serviço"""
    try:
        search = request.args.get('search', '', type=str)
        month_filter = request.args.get('month', '', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Buscar todas as ordens de serviço
        orders = omie_service.get_all_service_orders()
        
        # Buscar mapeamento de clientes
        try:
            client_name_mapping = omie_service.get_client_name_mapping()
        except Exception as e:
            print(f"Erro ao carregar mapeamento de clientes na API: {str(e)}")
            client_name_mapping = {}
        
        # Buscar mapeamento de vendedores
        try:
            seller_name_mapping = omie_service.get_seller_name_mapping()
        except Exception as e:
            print(f"Erro ao carregar mapeamento de vendedores na API: {str(e)}")
            seller_name_mapping = {}
        
        # Filtrar por mês se especificado
        if month_filter:
            filtered_orders = []
            for order in orders:
                cabecalho = order.get('Cabecalho', {})
                date_str = cabecalho.get('dDtPrevisao', '')
                if date_str:
                    try:
                        # Extrair mês/ano da data (formato dd/mm/yyyy)
                        month_year = "/".join(date_str.split("/")[1:])  # mm/yyyy
                        if month_year == month_filter:
                            filtered_orders.append(order)
                    except:
                        pass
            orders = filtered_orders
        
        # Filtrar por busca se necessário
        if search:
            search_lower = search.lower()
            filtered_orders = []
            for order in orders:
                cabecalho = order.get('Cabecalho', {})
                observacoes = order.get('Observacoes', {})
                
                # Buscar nome do cliente
                client_code = cabecalho.get('nCodCli', '')
                client_name = client_name_mapping.get(client_code, '').lower()
                
                # Buscar nome do vendedor
                seller_code = cabecalho.get('nCodVend', '')
                seller_name = seller_name_mapping.get(seller_code, '').lower()
                
                # Buscar nos campos corretos da estrutura da API, incluindo nome do cliente e vendedor
                if (search_lower in str(client_code).lower() or
                    search_lower in client_name or
                    search_lower in str(cabecalho.get('cNumOS', '')).lower() or
                    search_lower in str(cabecalho.get('nCodOS', '')).lower() or
                    search_lower in str(cabecalho.get('nCodVend', '')).lower() or
                    search_lower in seller_name or
                    search_lower in observacoes.get('cObsOS', '').lower()):
                    filtered_orders.append(order)
            orders = filtered_orders
        
        # Ordenar por data de previsão (mais recentes primeiro)
        def parse_date(date_str):
            """Converte data dd/mm/yyyy para objeto datetime para ordenação"""
            try:
                if date_str:
                    day, month, year = date_str.split('/')
                    return datetime(int(year), int(month), int(day))
                return datetime.min  # Data mínima para ordens sem data
            except:
                return datetime.min
        
        orders.sort(key=lambda order: parse_date(order.get('Cabecalho', {}).get('dDtPrevisao', '')), reverse=True)
        
        # Paginação
        total = len(orders)
        start = (page - 1) * per_page
        end = start + per_page
        orders_page = orders[start:end]
        
        return jsonify({
            'orders': orders_page,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
            'client_name_mapping': client_name_mapping,
            'seller_name_mapping': seller_name_mapping
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services/stats')
@login_required
def api_services_stats():
    """API endpoint para estatísticas de serviços"""
    try:
        stats = omie_service.get_service_orders_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/background/load-full-data', methods=['POST'])
@login_required
def api_start_background_loading():
    """Inicia carregamento completo de dados em background"""
    try:
        task_id = "full_data_load"
        
        # Verificar se já há uma tarefa rodando
        if background_service.is_task_running(task_id):
            return jsonify({
                'status': 'already_running',
                'task_id': task_id,
                'message': 'Carregamento já está em andamento'
            })
        
        # Iniciar nova tarefa
        background_service.start_task(
            task_id,
            omie_service.load_full_data_background
        )
        
        return jsonify({
            'status': 'started',
            'task_id': task_id,
            'message': 'Carregamento completo iniciado em background'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/background/status/<task_id>')
@login_required
def api_background_task_status(task_id):
    """Verifica o status de uma tarefa em background"""
    try:
        status = background_service.get_task_status(task_id)
        
        if not status:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/clear', methods=['POST'])
@login_required
def api_clear_cache():
    """Limpa o cache do serviço Omie"""
    try:
        omie_service.clear_cache()
        print("Cache limpo - dados serão recarregados na próxima requisição")
        return jsonify({
            'status': 'success',
            'message': 'Cache limpo com sucesso - dados serão recarregados na próxima requisição'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/clear-services', methods=['POST'])
@login_required
def api_clear_services_cache():
    """Limpa especificamente o cache de serviços"""
    try:
        # Limpar cache específico de serviços
        omie_service.clear_cache_by_pattern("get_service_name_mapping")
        omie_service.clear_cache_by_pattern("get_all_services")
        omie_service.clear_cache_by_pattern("get_service_orders_stats")
        print("Cache de serviços limpo - mapeamento será recarregado")
        return jsonify({
            'status': 'success',
            'message': 'Cache de serviços limpo com sucesso'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/startup/status')
@login_required
def api_startup_status():
    """Verifica o status do pré-carregamento de dados"""
    try:
        status = startup_service.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/startup/restart', methods=['POST'])
@login_required
def api_restart_preload():
    """Reinicia o pré-carregamento de dados"""
    try:
        startup_service.start_preload()
        return jsonify({
            'status': 'started',
            'message': 'Pré-carregamento reiniciado'
        })
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

@app.template_filter('format_currency')
def format_currency(value):
    """Filtro para formatar valores monetários"""
    if not value:
        return 'R$ 0,00'
    
    try:
        # Converte para float se for string
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        # Formata como moeda brasileira
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return f"R$ {value}"

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Página não encontrada'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Erro interno do servidor'), 500

def cleanup_background_tasks():
    """Limpa tarefas antigas em background"""
    try:
        background_service.cleanup_old_tasks(max_age_hours=24)
    except Exception as e:
        print(f"Erro ao limpar tarefas antigas: {e}")

if __name__ == '__main__':
    # Limpar tarefas antigas na inicialização
    cleanup_background_tasks()
    
    # Configuração para desenvolvimento
    port = int(os.getenv('PORT', 8002))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)