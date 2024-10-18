# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from rule_engine.models.ast_node import Node
from rule_engine.parser import RuleParser
from rule_engine.evaluator import RuleEvaluator
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RuleCreate(BaseModel):
    rule_string: str

class RuleCombine(BaseModel):
    rules: List[str]

class RuleEvaluate(BaseModel):
    rule_ast: Dict[str, Any]
    data: Dict[str, Any]

@app.post("/api/rules/create")
async def create_rule(rule_request: RuleCreate):
    try:
        parser = RuleParser()
        ast = parser.parse(rule_request.rule_string)
        return ast.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/rules/combine")
async def combine_rules(rule_request: RuleCombine):
    try:
        parser = RuleParser()
        # Combine rules with OR operator
        combined_ast = None
        for rule_string in rule_request.rules:
            ast = parser.parse(rule_string)
            if combined_ast is None:
                combined_ast = ast
            else:
                combined_ast = Node(
                    type=NodeType.OPERATOR,
                    operator=Operator.OR,
                    left=combined_ast,
                    right=ast
                )
        return combined_ast.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/rules/evaluate")
async def evaluate_rule(rule_request: RuleEvaluate):
    try:
        ast = Node.from_dict(rule_request.rule_ast)
        result = RuleEvaluator.evaluate(ast, rule_request.data)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Run with: uvicorn main:app --reload