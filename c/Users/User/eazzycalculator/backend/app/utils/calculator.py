"""
Module de calcul sécurisé pour EazzyCalculator.
Fournit des fonctions pour évaluer des expressions mathématiques de manière sécurisée.
"""
import ast
import operator
import logging

logger = logging.getLogger(__name__)

# Opérateurs mathématiques autorisés
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def evaluate_expression(expr: str) -> float:
    """
    Évalue une expression mathématique de manière sécurisée.
    
    Args:
        expr (str): L'expression mathématique à évaluer
        
    Returns:
        float: Le résultat du calcul
        
    Raises:
        ValueError: Si l'expression contient des opérations non autorisées
        SyntaxError: Si l'expression est mal formée
    """
    try:
        # Parser l'expression
        parsed = ast.parse(expr, mode='eval')
        
        # Vérifier qu'il n'y a pas d'appels de fonctions ou d'attributs
        for node in ast.walk(parsed):
            if isinstance(node, (ast.Call, ast.Attribute)):
                raise ValueError("Les appels de fonctions ne sont pas autorisés")
                
        # Évaluer l'expression
        return _eval_node(parsed.body)
        
    except SyntaxError as e:
        logger.error(f"Erreur de syntaxe dans l'expression: {expr}")
        raise ValueError(f"Erreur de syntaxe dans l'expression: {str(e)}") from e
    except Exception as e:
        logger.error(f"Erreur lors de l'évaluation de l'expression: {expr}")
        raise ValueError(f"Erreur lors de l'évaluation: {str(e)}") from e

def _eval_node(node: ast.AST) -> float:
    """
    Évalue récursivement un nœud AST.
    
    Args:
        node: Le nœud AST à évaluer
        
    Returns:
        float: Le résultat de l'évaluation
        
    Raises:
        ValueError: Si une opération non autorisée est rencontrée
    """
    # Nombres
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Type de constante non supporté: {type(node.value).__name__}")
    
    # Nombres (compatibilité Python < 3.8)
    elif isinstance(node, ast.Num):
        return float(node.n)
    
    # Opérations unaires
    elif isinstance(node, ast.UnaryOp):
        operator_func = OPERATORS.get(type(node.op))
        if operator_func is None:
            raise ValueError(f"Opérateur unaire non supporté: {type(node.op).__name__}")
        return operator_func(_eval_node(node.operand))
    
    # Opérations binaires
    elif isinstance(node, ast.BinOp):
        operator_func = OPERATORS.get(type(node.op))
        if operator_func is None:
            raise ValueError(f"Opérateur binaire non supporté: {type(node.op).__name__}")
        return operator_func(_eval_node(node.left), _eval_node(node.right))
    
    # Autres types de nœuds non supportés
    raise ValueError(f"Expression non supportée: {type(node).__name__}")
