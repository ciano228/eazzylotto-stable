import ast
import operator
from typing import Union

class SafeEvaluator:
    """
    Évaluateur sécurisé d'expressions mathématiques simples.
    N'autorise que les opérations arithmétiques de base.
    """
    
    def __init__(self):
        self.operators_map = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
        }
        
        self.unary_operators_map = {
            ast.UAdd: lambda x: x,
            ast.USub: operator.neg,
        }
    
    def _eval_node(self, node: ast.AST) -> Union[int, float]:
        """Évalue récursivement un nœud AST"""
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)
            
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Type de constante non supporté: {type(node.value).__name__}")
            
        if isinstance(node, ast.Num):  # Pour les versions plus anciennes de Python
            return node.n
            
        if isinstance(node, ast.UnaryOp) and type(node.op) in self.unary_operators_map:
            val = self._eval_node(node.operand)
            return self.unary_operators_map[type(node.op)](val)
            
        if isinstance(node, ast.BinOp) and type(node.op) in self.operators_map:
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            
            if isinstance(node.op, ast.Div) and right == 0:
                raise ValueError("Division par zéro")
                
            return self.operators_map[type(node.op)](left, right)
            
        raise ValueError(f"Expression non supportée: {type(node).__name__}")
    
    def evaluate(self, expr: str) -> Union[int, float]:
        """
        Évalue une expression mathématique en toute sécurité.
        
        Args:
            expr: L'expression à évaluer (ex: "2 + 3 * (4 - 1)")
            
        Returns:
            Le résultat de l'évaluation
            
        Raises:
            ValueError: Si l'expression n'est pas valide ou utilise des opérations non autorisées
        """
        try:
            parsed = ast.parse(expr, mode="eval")
            
            # Vérifier que seuls les nœuds autorisés sont utilisés
            for node in ast.walk(parsed):
                if not isinstance(node, (
                    ast.Expression, ast.BinOp, ast.UnaryOp,
                    ast.Num, ast.Constant, ast.Load,
                    ast.Add, ast.Sub, ast.Mult, ast.Div,
                    ast.Pow, ast.Mod, ast.UAdd, ast.USub
                )):
                    raise ValueError(f"Élément d'expression non autorisé: {type(node).__name__}")
            
            return self._eval_node(parsed)
            
        except SyntaxError as e:
            raise ValueError(f"Erreur de syntaxe dans l'expression: {e}") from e
