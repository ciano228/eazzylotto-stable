"""
Module de calculatrice sécurisée
Évalue les expressions mathématiques de manière sécurisée
"""
import ast
import operator
from typing import Union


# Opérateurs autorisés
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def evaluate_expression(expr: str) -> Union[int, float]:
    """
    Évalue une expression mathématique de manière sécurisée
    
    Args:
        expr: Expression mathématique sous forme de chaîne
        
    Returns:
        Résultat du calcul
        
    Raises:
        ValueError: Si l'expression contient des éléments non autorisés
    """
    try:
        # Parser l'expression
        node = ast.parse(expr, mode='eval')
        
        # Évaluer de manière sécurisée
        result = _eval_node(node.body)
        
        return result
        
    except SyntaxError:
        raise ValueError("Expression mathématique invalide")
    except Exception as e:
        raise ValueError(f"Erreur lors de l'évaluation: {str(e)}")


def _eval_node(node):
    """Évalue récursivement un nœud AST"""
    
    if isinstance(node, ast.Constant):
        # Nombre constant
        return node.value
    
    elif isinstance(node, ast.Num):
        # Nombre (compatibilité Python < 3.8)
        return node.n
    
    elif isinstance(node, ast.BinOp):
        # Opération binaire
        op_type = type(node.op)
        
        if op_type not in ALLOWED_OPERATORS:
            raise ValueError(f"Opérateur non autorisé: {op_type.__name__}")
        
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        
        return ALLOWED_OPERATORS[op_type](left, right)
    
    elif isinstance(node, ast.UnaryOp):
        # Opération unaire
        op_type = type(node.op)
        
        if op_type not in ALLOWED_OPERATORS:
            raise ValueError(f"Opérateur non autorisé: {op_type.__name__}")
        
        operand = _eval_node(node.operand)
        
        return ALLOWED_OPERATORS[op_type](operand)
    
    else:
        raise ValueError(f"Type de nœud non autorisé: {type(node).__name__}")


# Exemples d'utilisation
if __name__ == "__main__":
    # Tests
    test_expressions = [
        "2 + 2",
        "10 - 5",
        "3 * 4",
        "15 / 3",
        "2 ** 3",
        "(2 + 3) * 4",
        "-5 + 10",
    ]
    
    for expr in test_expressions:
        try:
            result = evaluate_expression(expr)
            print(f"{expr} = {result}")
        except ValueError as e:
            print(f"{expr} -> Erreur: {e}")
