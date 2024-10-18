from typing import Dict, List, Union
import re
from datetime import datetime
import uuid
from ..models.ast_node import Node, NodeType, OperatorType, Rule

class RuleService:
    @staticmethod
    def create_rule(rule_string: str) -> Node:
        """Parse a rule string and create an AST."""
        tokens = RuleService._tokenize(rule_string)
        ast = RuleService._parse_tokens(tokens)
        return ast

    @staticmethod
    def combine_rules(rules: List[Rule]) -> Node:
        """Combine multiple rules into a single AST."""
        if not rules:
            raise ValueError("No rules provided")
        if len(rules) == 1:
            return rules[0].ast
            
        # Combine rules with OR operator
        combined = Node(
            type=NodeType.OPERATOR,
            operator=OperatorType.OR,
            left=rules[0].ast,
            right=RuleService.combine_rules(rules[1:])
        )
        return combined

    @staticmethod
    def evaluate_rule(ast: Node, data: Dict) -> bool:
        """Evaluate a rule against provided data."""
        if ast.type == NodeType.OPERAND:
            return RuleService._evaluate_operand(ast, data)
            
        if ast.type == NodeType.OPERATOR:
            left_result = RuleService.evaluate_rule(ast.left, data)
            right_result = RuleService.evaluate_rule(ast.right, data)
            
            if ast.operator == OperatorType.AND:
                return left_result and right_result
            elif ast.operator == OperatorType.OR:
                return left_result or right_result
                
        raise ValueError(f"Invalid node type: {ast.type}")

    @staticmethod
    def _tokenize(rule_string: str) -> List[str]:
        """Convert rule string into tokens."""
        # Add spaces around operators and parentheses
        rule_string = re.sub(r'([()><!=]|AND|OR)', r' \1 ', rule_string)
        return rule_string.split()

    @staticmethod
    def _parse_tokens(tokens: List[str]) -> Node:
        """Parse tokens into an AST."""
        # Implementation of recursive descent parser
        # This is a simplified version - you'd want to add more error handling
        if not tokens:
            raise ValueError("Empty token list")
            
        token = tokens.pop(0)
        
        if token == '(':
            left = RuleService._parse_tokens(tokens)
            operator = tokens.pop(0)
            right = RuleService._parse_tokens(tokens)
            closing = tokens.pop(0)
            if closing != ')':
                raise ValueError(f"Expected ), got {closing}")
                
            return Node(
                type=NodeType.OPERATOR,
                operator=operator,
                left=left,
                right=right
            )
        else:
            # Handle leaf nodes (conditions)
            field = token
            operator = tokens.pop(0)
            value = tokens.pop(0)
            
            return Node(
                type=NodeType.OPERAND,
                field=field,
                operator=operator,
                value=value
            )

    @staticmethod
    def _evaluate_operand(node: Node, data: Dict) -> bool:
        """Evaluate a leaf node against the data."""
        if node.field not in data:
            raise ValueError(f"Field {node.field} not found in data")
            
        actual_value = data[node.field]
        expected_value = node.value
        
        if node.operator == OperatorType.GT:
            return actual_value > expected_value
        elif node.operator == OperatorType.LT:
            return actual_value < expected_value
        elif node.operator == OperatorType.EQ:
            return actual_value == expected_value
        elif node.operator == OperatorType.GTE:
            return actual_value >= expected_value
        elif node.operator == OperatorType.LTE:
            return actual_value <= expected_value
            
        raise ValueError(f"Invalid operator: {node.operator}")