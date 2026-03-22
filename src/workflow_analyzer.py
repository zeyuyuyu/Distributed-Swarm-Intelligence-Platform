import numpy as np
from typing import Dict, List, Optional
import time

class WorkflowAnalyzer:
    def __init__(self):
        self.performance_metrics = {}
        self.workflow_history = []
        self.optimization_threshold = 0.75

    def analyze_workflow(self, workflow_data: Dict) -> Dict:
        """Analyzes workflow performance and suggests optimizations."""
        workflow_id = workflow_data.get('id')
        start_time = time.time()
        
        metrics = self._calculate_metrics(workflow_data)
        self.performance_metrics[workflow_id] = metrics
        self.workflow_history.append(workflow_data)
        
        optimization_suggestions = self._generate_optimization_suggestions(metrics)
        
        return {
            'workflow_id': workflow_id,
            'metrics': metrics,
            'suggestions': optimization_suggestions,
            'analysis_time': time.time() - start_time
        }

    def _calculate_metrics(self, workflow_data: Dict) -> Dict:
        """Calculate performance metrics for a workflow."""
        tasks = workflow_data.get('tasks', [])
        resource_usage = workflow_data.get('resource_usage', {})
        
        metrics = {
            'task_count': len(tasks),
            'avg_task_duration': np.mean([t.get('duration', 0) for t in tasks]),
            'cpu_efficiency': self._calculate_cpu_efficiency(resource_usage),
            'memory_utilization': self._calculate_memory_utilization(resource_usage),
            'bottleneck_score': self._identify_bottlenecks(tasks)
        }
        
        return metrics

    def _calculate_cpu_efficiency(self, resource_usage: Dict) -> float:
        """Calculate CPU efficiency score."""
        if not resource_usage.get('cpu_metrics'):
            return 0.0
        
        cpu_usage = resource_usage['cpu_metrics']
        return np.mean([usage for usage in cpu_usage if usage is not None])

    def _calculate_memory_utilization(self, resource_usage: Dict) -> float:
        """Calculate memory utilization score."""
        if not resource_usage.get('memory_metrics'):
            return 0.0
            
        memory_usage = resource_usage['memory_metrics']
        return np.mean([usage for usage in memory_usage if usage is not None])

    def _identify_bottlenecks(self, tasks: List[Dict]) -> float:
        """Calculate bottleneck score based on task dependencies and duration."""
        if not tasks:
            return 0.0
            
        max_duration = max(t.get('duration', 0) for t in tasks)
        avg_duration = np.mean([t.get('duration', 0) for t in tasks])
        
        if avg_duration == 0:
            return 0.0
            
        return max_duration / avg_duration

    def _generate_optimization_suggestions(self, metrics: Dict) -> List[str]:
        """Generate optimization suggestions based on metrics."""
        suggestions = []
        
        if metrics['cpu_efficiency'] < self.optimization_threshold:
            suggestions.append('Consider reducing CPU allocation or parallelizing tasks')
            
        if metrics['memory_utilization'] < self.optimization_threshold:
            suggestions.append('Memory resources may be over-allocated')
            
        if metrics['bottleneck_score'] > 2.0:
            suggestions.append('Critical bottleneck detected - consider task redistribution')
            
        return suggestions

    def get_historical_performance(self, workflow_id: Optional[str] = None) -> Dict:
        """Retrieve historical performance data for analysis."""
        if workflow_id and workflow_id in self.performance_metrics:
            return {
                'workflow_id': workflow_id,
                'metrics': self.performance_metrics[workflow_id]
            }
            
        return {
            'workflows': len(self.workflow_history),
            'avg_metrics': self._calculate_average_metrics()
        }

    def _calculate_average_metrics(self) -> Dict:
        """Calculate average metrics across all workflows."""
        if not self.performance_metrics:
            return {}
            
        all_metrics = list(self.performance_metrics.values())
        
        return {
            'avg_task_count': np.mean([m['task_count'] for m in all_metrics]),
            'avg_cpu_efficiency': np.mean([m['cpu_efficiency'] for m in all_metrics]),
            'avg_memory_utilization': np.mean([m['memory_utilization'] for m in all_metrics]),
            'avg_bottleneck_score': np.mean([m['bottleneck_score'] for m in all_metrics])
        }

    def reset_analysis(self):
        """Reset all analysis data."""
        self.performance_metrics.clear()
        self.workflow_history.clear()