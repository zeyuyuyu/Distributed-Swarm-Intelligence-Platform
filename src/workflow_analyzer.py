import time
from typing import Dict, List, Tuple
from collections import defaultdict

class WorkflowAnalyzer:
    def __init__(self):
        self.execution_times = defaultdict(list)
        self.node_loads = defaultdict(int)
        self.bottlenecks = []
        
    def record_task_execution(self, task_id: str, node_id: str, duration: float) -> None:
        """Record execution time for a task on a specific node"""
        self.execution_times[task_id].append((node_id, duration))
        self.node_loads[node_id] += 1

    def analyze_performance(self) -> Dict[str, float]:
        """Calculate key performance metrics for the workflow"""
        metrics = {
            'avg_task_duration': 0.0,
            'max_task_duration': 0.0,
            'total_tasks': 0,
            'load_balance_score': 0.0
        }
        
        all_durations = []
        for task_id, executions in self.execution_times.items():
            durations = [duration for _, duration in executions]
            all_durations.extend(durations)
            
        if all_durations:
            metrics['avg_task_duration'] = sum(all_durations) / len(all_durations)
            metrics['max_task_duration'] = max(all_durations)
            metrics['total_tasks'] = len(all_durations)
            
        # Calculate load balance score (0-1, higher is better)
        if self.node_loads:
            avg_load = sum(self.node_loads.values()) / len(self.node_loads)
            max_deviation = max(abs(load - avg_load) for load in self.node_loads.values())
            metrics['load_balance_score'] = 1.0 - (max_deviation / avg_load if avg_load > 0 else 0)
            
        return metrics

    def detect_bottlenecks(self) -> List[Tuple[str, str, float]]:
        """Identify performance bottlenecks in the workflow"""
        self.bottlenecks = []
        
        # Detect tasks that take significantly longer than average
        all_durations = [d for executions in self.execution_times.values() 
                        for _, d in executions]
        if not all_durations:
            return []
            
        avg_duration = sum(all_durations) / len(all_durations)
        std_dev = (sum((d - avg_duration) ** 2 for d in all_durations) 
                  / len(all_durations)) ** 0.5
        
        threshold = avg_duration + (2 * std_dev)
        
        for task_id, executions in self.execution_times.items():
            for node_id, duration in executions:
                if duration > threshold:
                    self.bottlenecks.append((
                        task_id,
                        node_id,
                        duration / avg_duration  # Slowdown factor
                    ))
                    
        return sorted(self.bottlenecks, key=lambda x: x[2], reverse=True)

    def generate_performance_report(self) -> str:
        """Generate a detailed performance report"""
        metrics = self.analyze_performance()
        bottlenecks = self.detect_bottlenecks()
        
        report = [
            'Workflow Performance Report',
            '=========================',
            f'Total Tasks: {metrics["total_tasks"]}',
            f'Average Task Duration: {metrics["avg_task_duration"]:.2f}s',
            f'Maximum Task Duration: {metrics["max_task_duration"]:.2f}s',
            f'Load Balance Score: {metrics["load_balance_score"]:.2f}',
            '',
            'Top Bottlenecks:',
            '---------------'
        ]
        
        for task_id, node_id, slowdown in bottlenecks[:5]:
            report.append(
                f'Task {task_id} on Node {node_id}: '
                f'{slowdown:.1f}x slower than average'
            )
            
        return '\n'.join(report)

    def reset_analytics(self) -> None:
        """Reset all analytics data"""
        self.execution_times.clear()
        self.node_loads.clear()
        self.bottlenecks.clear()