import ast
from typing import Dict, List, Optional
from pathlib import Path

class WorkflowAnalyzer:
    def __init__(self):
        self.metrics = {
            'cognitive_complexity': 0,
            'maintainability_index': 0,
            'code_smells': []
        }

    def analyze_file(self, file_path: Path) -> Dict:
        """Analyzes a Python file and returns code quality metrics."""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            tree = ast.parse(code)
            self._reset_metrics()
            self._analyze_tree(tree)
            return self.metrics
        except Exception as e:
            return {'error': str(e)}

    def _reset_metrics(self) -> None:
        """Reset metrics before new analysis."""
        self.metrics = {
            'cognitive_complexity': 0,
            'maintainability_index': 0,
            'code_smells': []
        }

    def _analyze_tree(self, tree: ast.AST) -> None:
        """Traverse AST and collect metrics."""
        self._analyze_complexity(tree)
        self._detect_code_smells(tree)
        self._calculate_maintainability(tree)

    def _analyze_complexity(self, tree: ast.AST) -> None:
        """Calculate cognitive complexity score."""
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
                self.nesting = 0

            def visit_If(self, node):
                self.complexity += (1 + self.nesting)
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

            def visit_For(self, node):
                self.complexity += (1 + self.nesting)
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

            def visit_While(self, node):
                self.complexity += (1 + self.nesting)
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

        visitor = ComplexityVisitor()
        visitor.visit(tree)
        self.metrics['cognitive_complexity'] = visitor.complexity

    def _detect_code_smells(self, tree: ast.AST) -> None:
        """Detect common code smells."""
        class SmellDetector(ast.NodeVisitor):
            def __init__(self):
                self.smells = []

            def visit_FunctionDef(self, node):
                if len(node.args.args) > 5:
                    self.smells.append({
                        'type': 'too_many_parameters',
                        'message': f'Function {node.name} has too many parameters',
                        'line': node.lineno
                    })
                if len(node.body) > 20:
                    self.smells.append({
                        'type': 'long_function',
                        'message': f'Function {node.name} is too long',
                        'line': node.lineno
                    })
                self.generic_visit(node)

        detector = SmellDetector()
        detector.visit(tree)
        self.metrics['code_smells'] = detector.smells

    def _calculate_maintainability(self, tree: ast.AST) -> None:
        """Calculate maintainability index."""
        # Simplified MI calculation
        loc = len(ast.unparse(tree).splitlines())
        cc = self.metrics['cognitive_complexity']
        self.metrics['maintainability_index'] = max(0, 100 - (cc * 0.5 + loc * 0.1))

    def get_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        if self.metrics['cognitive_complexity'] > 15:
            recommendations.append(
                'Consider breaking down complex functions into smaller, more manageable pieces'
            )
            
        if self.metrics['maintainability_index'] < 65:
            recommendations.append(
                'Code maintainability is low. Focus on reducing complexity and improving documentation'
            )
            
        for smell in self.metrics['code_smells']:
            recommendations.append(f'Line {smell["line"]}: {smell["message"]}')
            
        return recommendations

    def generate_report(self, file_path: Path) -> Dict:
        """Generate a comprehensive analysis report."""
        analysis = self.analyze_file(file_path)
        return {
            'file': str(file_path),
            'metrics': self.metrics,
            'recommendations': self.get_recommendations(),
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> str:
        """Generate a brief summary of the analysis."""
        mi = self.metrics['maintainability_index']
        if mi >= 85:
            quality = 'excellent'
        elif mi >= 65:
            quality = 'good'
        else:
            quality = 'needs improvement'
            
        return f'Code quality is {quality} with a maintainability index of {mi:.1f}'
