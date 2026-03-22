import os
import json
from typing import List, Dict

class WorkflowAnalyzer:
    def __init__(self, workflow_config_file: str):
        self.workflow_config = self._load_workflow_config(workflow_config_file)
        self.task_dependencies: Dict[str, List[str]] = self._analyze_task_dependencies()
        self.task_resources: Dict[str, Dict[str, float]] = self._analyze_task_resources()
        self.node_resources: Dict[str, Dict[str, float]] = self._analyze_node_resources()

    def _load_workflow_config(self, config_file: str) -> Dict:
        with open(config_file, 'r') as f:
            return json.load(f)

    def _analyze_task_dependencies(self) -> Dict[str, List[str]]:
        task_dependencies = {}
        for workflow in self.workflow_config['workflows']:
            for task in workflow['tasks']:
                task_dependencies[task['name']] = [dep['name'] for dep in task['dependencies']]
        return task_dependencies

    def _analyze_task_resources(self) -> Dict[str, Dict[str, float]]:
        task_resources = {}
        for workflow in self.workflow_config['workflows']:
            for task in workflow['tasks']:
                task_resources[task['name']] = task['resources']
        return task_resources

    def _analyze_node_resources(self) -> Dict[str, Dict[str, float]]:
        node_resources = {}
        for node in self.workflow_config['nodes']:
            node_resources[node['name']] = node['resources']
        return node_resources

    def optimize_workflow(self) -> Dict[str, List[str]]:
        workflow_schedule = {}
        available_nodes = list(self.node_resources.keys())
        for workflow in self.workflow_config['workflows']:
            workflow_schedule[workflow['name']] = self._schedule_workflow(workflow, available_nodes)
        return workflow_schedule

    def _schedule_workflow(self, workflow: Dict, available_nodes: List[str]) -> List[str]:
        scheduled_tasks = []
        unscheduled_tasks = [task['name'] for task in workflow['tasks']]
        while unscheduled_tasks:
            scheduled = self._schedule_tasks(unscheduled_tasks, available_nodes)
            scheduled_tasks.extend(scheduled)
            unscheduled_tasks = [task for task in unscheduled_tasks if task not in scheduled]
        return scheduled_tasks

    def _schedule_tasks(self, tasks: List[str], available_nodes: List[str]) -> List[str]:
        scheduled = []
        for task in tasks:
            dependencies = self.task_dependencies[task]
            if all(dep in scheduled for dep in dependencies):
                best_node = self._find_best_node(task, available_nodes)
                if best_node:
                    scheduled.append(task)
                    available_nodes.remove(best_node)
        return scheduled

    def _find_best_node(self, task: str, available_nodes: List[str]) -> str:
        best_fit = None
        best_score = 0
        task_resources = self.task_resources[task]
        for node in available_nodes:
            node_resources = self.node_resources[node]
            score = sum(node_resources[res] / task_resources[res] for res in task_resources)
            if score > best_score:
                best_fit = node
                best_score = score
        return best_fit
