import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class BackgroundTaskService:
    """Serviço para executar tarefas em background"""
    
    def __init__(self):
        self.tasks = {}
        self.results = {}
        self.lock = threading.Lock()
    
    def start_task(self, task_id: str, target_function, *args, **kwargs) -> str:
        """Inicia uma tarefa em background"""
        with self.lock:
            if task_id in self.tasks and self.tasks[task_id].is_alive():
                return task_id  # Tarefa já está rodando
            
            # Criar e iniciar thread
            thread = threading.Thread(
                target=self._run_task,
                args=(task_id, target_function, args, kwargs)
            )
            thread.daemon = True
            thread.start()
            
            self.tasks[task_id] = thread
            self.results[task_id] = {
                'status': 'running',
                'started_at': datetime.now(),
                'result': None,
                'error': None
            }
            
            return task_id
    
    def _run_task(self, task_id: str, target_function, args, kwargs):
        """Executa a tarefa e armazena o resultado"""
        try:
            print(f"Iniciando tarefa em background: {task_id}")
            result = target_function(*args, **kwargs)
            
            with self.lock:
                self.results[task_id].update({
                    'status': 'completed',
                    'completed_at': datetime.now(),
                    'result': result,
                    'error': None
                })
            print(f"Tarefa concluída: {task_id}")
            
        except Exception as e:
            print(f"Erro na tarefa {task_id}: {str(e)}")
            with self.lock:
                self.results[task_id].update({
                    'status': 'error',
                    'completed_at': datetime.now(),
                    'result': None,
                    'error': str(e)
                })
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retorna o status de uma tarefa"""
        with self.lock:
            return self.results.get(task_id)
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Retorna o resultado de uma tarefa se estiver concluída"""
        with self.lock:
            task_info = self.results.get(task_id)
            if task_info and task_info['status'] == 'completed':
                return task_info['result']
            return None
    
    def is_task_running(self, task_id: str) -> bool:
        """Verifica se uma tarefa está rodando"""
        with self.lock:
            task_info = self.results.get(task_id)
            return task_info and task_info['status'] == 'running'
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove tarefas antigas dos resultados"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        with self.lock:
            tasks_to_remove = []
            for task_id, task_info in self.results.items():
                completed_at = task_info.get('completed_at')
                if completed_at and completed_at < cutoff_time:
                    tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self.results[task_id]
                if task_id in self.tasks:
                    del self.tasks[task_id]
            
            if tasks_to_remove:
                print(f"Removidas {len(tasks_to_remove)} tarefas antigas")

# Instância global do serviço
background_service = BackgroundTaskService()