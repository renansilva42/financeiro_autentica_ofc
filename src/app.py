from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_session import Session
from services.omie_service import OmieService
from services.auth_service import AuthService
from services.background_service import background_service
from services.startup_service import initialize_startup_service
from services.cache_service import SupabaseCacheService
from services.progressive_loader import ProgressiveDataLoader
from services.api_endpoints import optimized_api, initialize_services
from utils.auth_decorators import login_required, logout_required
import json
import os
import asyncio
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

# Inicializar serviços otimizados
print("🚀 Inicializando serviços otimizados...")

# Inicializar cache inteligente
cache_service = None
try:
    cache_service = SupabaseCacheService()
    print("✅ Cache inteligente inicializado com sucesso")
except Exception as e:
    print(f"⚠️  Aviso: Cache inteligente não disponível: {e}")
    print("   A aplicação continuará funcionando com cache local apenas.")

# Inicializar serviço Omie
omie_service = OmieService()

# Configurar cache inteligente no OmieService se disponível
if cache_service:
    try:
        # Adicionar método para integração com cache inteligente
        omie_service.intelligent_cache = cache_service
        print("✅ Cache inteligente integrado ao OmieService")
    except Exception as e:
        print(f"⚠️  Erro ao integrar cache: {e}")

# Inicializar carregador progressivo
progressive_loader = None
if cache_service:
    try:
        progressive_loader = ProgressiveDataLoader(omie_service, cache_service)
        print("✅ Carregador progressivo inicializado")
    except Exception as e:
        print(f"⚠️  Erro ao inicializar carregador progressivo: {e}")

# Inicializar endpoints otimizados
if cache_service:
    try:
        initialize_services(omie_service, cache_service)
        app.register_blueprint(optimized_api)
        print("✅ Endpoints otimizados registrados")
    except Exception as e:
        print(f"⚠️  Erro ao registrar endpoints otimizados: {e}")

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
    """Página inicial com dashboard otimizado"""
    try:
        # Carregar estatísticas básicas do cache primeiro
        stats = None
        
        # Tentar carregar do cache inteligente se disponível
        if cache_service:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    cache_key = "dashboard_basic_stats"
                    stats = loop.run_until_complete(
                        cache_service.get(cache_key, "dashboard")
                    )
                    if stats:
                        print(f"Dashboard stats carregadas do cache inteligente")
                finally:
                    loop.close()
            except Exception as cache_error:
                print(f"Erro ao acessar cache para dashboard: {cache_error}")
        
        # Se não há cache, carregar estatísticas básicas rapidamente
        if not stats:
            print("Carregando estatísticas básicas para dashboard...")
            try:
                # Usar timeout menor para não travar o dashboard
                stats = omie_service.get_clients_stats()
                
                # Salvar no cache inteligente para próximas consultas
                if cache_service and stats:
                    try:
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            cache_key = "dashboard_basic_stats"
                            loop.run_until_complete(
                                cache_service.set(cache_key, stats, "dashboard", 0.5)  # 30 minutos
                            )
                            print("Dashboard stats salvas no cache inteligente")
                        finally:
                            loop.close()
                    except Exception as cache_error:
                        print(f"Erro ao salvar stats no cache: {cache_error}")
                        
            except Exception as stats_error:
                print(f"Erro ao carregar estatísticas: {stats_error}")
                # Usar estatísticas vazias para não quebrar o dashboard
                stats = {
                    "total_clients": 0,
                    "active_clients": 0,
                    "inactive_clients": 0,
                    "pessoa_fisica": 0,
                    "pessoa_juridica": 0,
                    "by_state": {}
                }
        
        return render_template('index.html', stats=stats)
        
    except Exception as e:
        print(f"Erro crítico no dashboard: {str(e)}")
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
        service_filter = request.args.get('service', '', type=str)
        month_filter = request.args.get('month', '', type=str)
        week_filter = request.args.get('week', '', type=str)
        year_filter = request.args.get('year', '', type=str)
        per_page = 20
        
        # Se não há nenhum filtro aplicado, usar o ano atual como padrão
        current_year = str(datetime.now().year)
        if not search and not month_filter and not week_filter and not year_filter:
            year_filter = current_year
            print(f"Aplicando filtro padrão para o ano atual: {year_filter}")
        
        # Verificar se há dados em cache primeiro
        print(f"Buscando ordens de serviço - página {page}, busca: '{search}', ano: '{year_filter}', mês: '{month_filter}', semana: '{week_filter}'")
        
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
        
        # Manter apenas ordens de serviço faturadas
        all_orders = [o for o in all_orders if o.get('Cabecalho', {}).get('cEtapa') == '60']

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

        # Lista dinâmica de serviços disponíveis
        print("Buscando lista de serviços disponíveis...")
        try:
            service_name_mapping = omie_service.get_service_name_mapping()
            available_services = sorted(service_name_mapping.values())
        except Exception as e:
            print(f"Erro ao carregar serviços disponíveis: {str(e)}")
            available_services = []
        
        # Filtrar por ano se especificado (tem prioridade sobre semana e mês)
        if year_filter:
            filtered_orders = []
            for order in all_orders:
                cabecalho = order.get('Cabecalho', {})
                date_str = cabecalho.get('dDtPrevisao', '')
                if date_str:
                    try:
                        # Extrair ano da data (formato dd/mm/yyyy)
                        year = date_str.split("/")[2]  # yyyy
                        if year == year_filter:
                            filtered_orders.append(order)
                    except:
                        pass
            all_orders = filtered_orders
        # Filtrar por semana se especificado (tem prioridade sobre mês, mas não sobre ano)
        elif week_filter:
            try:
                # Extrair datas de início e fim da semana
                start_date_str, end_date_str = week_filter.split("_")
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                
                filtered_orders = []
                for order in all_orders:
                    cabecalho = order.get('Cabecalho', {})
                    date_str = cabecalho.get('dDtPrevisao', '')
                    if date_str:
                        try:
                            # Converter data dd/mm/yyyy para datetime
                            day, month, year = date_str.split("/")
                            order_date = datetime(int(year), int(month), int(day))
                            
                            # Verificar se a data está dentro da semana
                            if start_date <= order_date <= end_date:
                                filtered_orders.append(order)
                        except:
                            pass
                all_orders = filtered_orders
            except Exception as e:
                print(f"Erro ao filtrar por semana: {str(e)}")
        # Filtrar por mês se especificado (apenas se não há filtro de ano ou semana)
        elif month_filter:
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
        
        # Filtrar por tipo de serviço se necessário (antes de busca para reduzir dataset)
        if service_filter:
            filtered_orders = []
            for order in all_orders:
                servicos = order.get('ServicosPrestados', [])
                if any(s.get('cDescServ', '').strip() == service_filter for s in servicos):
                    filtered_orders.append(order)
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
        
        # Buscar estatísticas adaptáveis aos filtros aplicados
        print("Buscando estatísticas de ordens de serviço...")
        try:
            # Gerar estatísticas utilizando o mesmo conjunto filtrado de ordens para manter consistência
            # Isso garante que as estatísticas reflitam exatamente os dados filtrados
            stats = omie_service.get_service_orders_stats(faturada_only=False, orders=all_orders, service_filter=service_filter)
            
            # Adicionar informações sobre os filtros aplicados para contexto
            stats['applied_filters'] = {
                'search': search,
                'service_filter': service_filter,
                'year_filter': year_filter,
                'month_filter': month_filter,
                'week_filter': week_filter,
                'total_filtered_orders': len(all_orders)
            }
            
            print(f"Estatísticas calculadas para {len(all_orders)} ordens filtradas")
            
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
                "monthly_values": {},
                "applied_filters": {
                    'search': search,
                    'service_filter': service_filter,
                    'year_filter': year_filter,
                    'month_filter': month_filter,
                    'week_filter': week_filter,
                    'total_filtered_orders': len(all_orders)
                }
            }
        
        # Se há filtro de ano, calcular estatísticas específicas do ano
        yearly_stats = None
        if year_filter:
            print(f"Buscando estatísticas anuais para {year_filter}...")
            try:
                yearly_stats = omie_service.get_yearly_service_stats(year_filter)
            except Exception as e:
                print(f"Erro ao carregar estatísticas anuais: {str(e)}")
                yearly_stats = None
        
        # Se há filtro de semana (e não de ano), calcular estatísticas específicas da semana
        weekly_stats = None
        if week_filter and not year_filter:
            print(f"Buscando estatísticas semanais para {week_filter}...")
            try:
                weekly_stats = omie_service.get_weekly_service_stats(week_filter)
            except Exception as e:
                print(f"Erro ao carregar estatísticas semanais: {str(e)}")
                weekly_stats = None
        
        # Se há filtro de mês (e não de ano ou semana), calcular estatísticas específicas do mês
        monthly_stats = None
        if month_filter and not year_filter and not week_filter:
            print(f"Buscando estatísticas mensais para {month_filter}...")
            try:
                monthly_stats = omie_service.get_monthly_service_stats(month_filter)
            except Exception as e:
                print(f"Erro ao carregar estatísticas mensais: {str(e)}")
                monthly_stats = None
        
        # Buscar lista de anos disponíveis para o filtro
        print("Buscando anos disponíveis...")
        try:
            available_years = omie_service.get_available_years_for_services()
        except Exception as e:
            print(f"Erro ao carregar anos disponíveis: {str(e)}")
            available_years = []
        
        # Buscar lista de meses disponíveis para o filtro
        print("Buscando meses disponíveis...")
        try:
            available_months = omie_service.get_available_months_for_services()
        except Exception as e:
            print(f"Erro ao carregar meses disponíveis: {str(e)}")
            available_months = []
        
        # Buscar lista de semanas disponíveis para o filtro (com preenchimento de lacunas)
        print("Buscando semanas disponíveis...")
        try:
            available_weeks = omie_service.get_available_weeks_for_services(fill_gaps=True)
        except Exception as e:
            print(f"Erro ao carregar semanas disponíveis: {str(e)}")
            available_weeks = []
        
        return render_template('services.html', 
                             orders=orders_page, 
                             pagination=pagination,
                             stats=stats,
                             yearly_stats=yearly_stats,
                             monthly_stats=monthly_stats,
                             weekly_stats=weekly_stats,
                             search=search,
                             service_filter=service_filter,
                             year_filter=year_filter,
                             month_filter=month_filter,
                             week_filter=week_filter,
                             available_years=available_years,
                             available_months=available_months,
                             available_weeks=available_weeks,
                             available_services=available_services,
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

@app.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    """API endpoint otimizado para estatísticas do dashboard"""
    try:
        # Tentar carregar do cache inteligente primeiro
        stats = None
        
        if cache_service:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    cache_key = "dashboard_basic_stats"
                    stats = loop.run_until_complete(
                        cache_service.get(cache_key, "dashboard")
                    )
                    if stats:
                        return jsonify({
                            'status': 'success',
                            'data': stats,
                            'from_cache': True,
                            'timestamp': datetime.now().isoformat()
                        })
                finally:
                    loop.close()
            except Exception as cache_error:
                print(f"Erro ao acessar cache: {cache_error}")
        
        # Se não há cache, carregar da API
        print("Carregando estatísticas da API para dashboard...")
        stats = omie_service.get_clients_stats()
        
        # Salvar no cache para próximas consultas
        if cache_service and stats:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    cache_key = "dashboard_basic_stats"
                    loop.run_until_complete(
                        cache_service.set(cache_key, stats, "dashboard", 0.5)  # 30 minutos
                    )
                finally:
                    loop.close()
            except Exception as cache_error:
                print(f"Erro ao salvar no cache: {cache_error}")
        
        return jsonify({
            'status': 'success',
            'data': stats,
            'from_cache': False,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/dashboard/quick-stats')
@login_required
def api_dashboard_quick_stats():
    """API endpoint para estatísticas rápidas do dashboard (apenas cache)"""
    try:
        if not cache_service:
            return jsonify({
                'status': 'unavailable',
                'message': 'Cache não disponível'
            }), 503
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            cache_key = "dashboard_basic_stats"
            stats = loop.run_until_complete(
                cache_service.get(cache_key, "dashboard")
            )
            
            if stats:
                return jsonify({
                    'status': 'success',
                    'data': stats,
                    'from_cache': True,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'status': 'no_cache',
                    'message': 'Dados não disponíveis em cache'
                })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/services')
@login_required
def api_services():
    """API endpoint para ordens de serviço"""
    try:
        search = request.args.get('search', '', type=str)
        month_filter = request.args.get('month', '', type=str)
        week_filter = request.args.get('week', '', type=str)
        year_filter = request.args.get('year', '', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Se não há nenhum filtro aplicado, usar o ano atual como padrão
        current_year = str(datetime.now().year)
        if not search and not month_filter and not week_filter and not year_filter:
            year_filter = current_year
        
        # Buscar todas as ordens de serviço
        orders = omie_service.get_all_service_orders()
        # Manter apenas ordens de serviço faturadas
        orders = [o for o in orders if o.get('Cabecalho', {}).get('cEtapa') == '60']
        
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
        
        # Filtrar por ano se especificado (tem prioridade sobre semana e mês)
        if year_filter:
            filtered_orders = []
            for order in orders:
                cabecalho = order.get('Cabecalho', {})
                date_str = cabecalho.get('dDtPrevisao', '')
                if date_str:
                    try:
                        # Extrair ano da data (formato dd/mm/yyyy)
                        year = date_str.split("/")[2]  # yyyy
                        if year == year_filter:
                            filtered_orders.append(order)
                    except:
                        pass
            orders = filtered_orders
        # Filtrar por semana se especificado (tem prioridade sobre mês, mas não sobre ano)
        elif week_filter:
            try:
                # Extrair datas de início e fim da semana
                start_date_str, end_date_str = week_filter.split("_")
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                
                filtered_orders = []
                for order in orders:
                    cabecalho = order.get('Cabecalho', {})
                    date_str = cabecalho.get('dDtPrevisao', '')
                    if date_str:
                        try:
                            # Converter data dd/mm/yyyy para datetime
                            day, month, year = date_str.split("/")
                            order_date = datetime(int(year), int(month), int(day))
                            
                            # Verificar se a data está dentro da semana
                            if start_date <= order_date <= end_date:
                                filtered_orders.append(order)
                        except:
                            pass
                orders = filtered_orders
            except Exception as e:
                print(f"Erro ao filtrar por semana na API: {str(e)}")
        # Filtrar por mês se especificado (apenas se não há filtro de ano ou semana)
        elif month_filter:
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
        # Garantir que apenas ordens faturadas sejam consideradas nas estatísticas
        stats = omie_service.get_service_orders_stats(faturada_only=True)
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

@app.route('/api/cache/clear-weeks', methods=['POST'])
@login_required
def api_clear_weeks_cache():
    """Limpa especificamente o cache de semanas disponíveis"""
    try:
        omie_service.clear_weeks_cache()
        return jsonify({
            'status': 'success',
            'message': 'Cache de semanas limpo com sucesso - sequência será recalculada'
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

@app.route('/api/progressive/dashboard', methods=['GET'])
@login_required
def api_progressive_dashboard():
    """Endpoint para carregamento progressivo do dashboard"""
    try:
        if not progressive_loader:
            # Fallback para carregamento tradicional
            stats = omie_service.get_clients_stats()
            return jsonify({
                'status': 'success',
                'data': {'stats': stats},
                'from_cache': False,
                'progressive': False,
                'timestamp': datetime.now().isoformat()
            })
        
        # Executar carregamento progressivo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            data = loop.run_until_complete(progressive_loader.load_dashboard_data())
            return jsonify({
                'status': 'success',
                'data': data,
                'progressive': True,
                'timestamp': datetime.now().isoformat()
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/progressive/status', methods=['GET'])
@login_required
def api_progressive_status():
    """Endpoint para verificar status do carregamento progressivo"""
    try:
        if not progressive_loader:
            return jsonify({
                'status': 'unavailable',
                'message': 'Carregamento progressivo não disponível'
            })
        
        status = progressive_loader.get_current_status()
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/intelligent/stats', methods=['GET'])
@login_required
def api_intelligent_cache_stats():
    """Endpoint para estatísticas do cache inteligente"""
    try:
        if not cache_service:
            return jsonify({
                'status': 'unavailable',
                'message': 'Cache inteligente não disponível'
            })
        
        stats = cache_service.get_cache_stats()
        sync_status = cache_service.get_sync_status()
        
        return jsonify({
            'status': 'success',
            'cache_stats': stats,
            'sync_status': sync_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/cache/intelligent/clear', methods=['POST'])
@login_required
def api_intelligent_cache_clear():
    """Endpoint para limpeza inteligente do cache"""
    try:
        if not cache_service:
            return jsonify({
                'status': 'unavailable',
                'message': 'Cache inteligente não disponível'
            }), 400
        
        data = request.get_json() or {}
        pattern = data.get('pattern')
        data_type = data.get('data_type')
        
        cache_service.clear_cache(pattern=pattern, data_type=data_type)
        
        return jsonify({
            'status': 'success',
            'message': 'Cache inteligente limpo com sucesso',
            'pattern': pattern,
            'data_type': data_type,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

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