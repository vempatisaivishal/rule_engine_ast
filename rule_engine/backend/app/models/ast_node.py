from typing import Optional, Union, Dict
from pydantic import BaseModel
from enum import Enum

class NodeType(str, Enum):
    OPERATOR = "operator"
    OPERAND = "operand"

class OperatorType(str, Enum):
    AND = "AND"
    OR = "OR"
    GT = ">"
    LT = "<"
    EQ = "="
    GTE = ">="
    LTE = "<="

class Node(BaseModel):
    type: NodeType
    operator: Optional[OperatorType]
    field: Optional[str]
    value: Optional[Union[str, int, float]]
    left: Optional['Node']
    right: Optional['Node']

    class Config:
        use_enum_values = True

class Rule(BaseModel):
    id: str
    name: str
    description: Optional[str]
    ast: Node
    created_at: str
    updated_at: str

    class Config:
        schema_extra = {
            "example": {
                "id": "rule1",
                "name": "Sales Team Rule",
                "description": "Eligibility rule for sales team members",
                "ast": {
                    "type": "operator",
                    "operator": "AND",
                    "left": {
                        "type": "operator",
                        "operator": ">",
                        "field": "age",
                        "value": 30
                    },
                    "right": {
                        "type": "operator",
                        "operator": "=",
                        "field": "department",
                        "value": "Sales"
                    }
                },
                "created_at": "2024-10-18T10:00:00Z",
                "updated_at": "2024-10-18T10:00:00Z"
            }
        }