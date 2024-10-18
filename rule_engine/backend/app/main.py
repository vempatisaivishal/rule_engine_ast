from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from .models.ast_node import Rule, Node
from .services.rule_service import RuleService
from .models.database import Database, init_db

app = FastAPI(title="Rule Engine API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await Database.close_db()

@app.post("/rules/", response_model=Rule)
async def create_rule(rule_string: str, name: str, description: str = None):
    try:
        ast = RuleService.create_rule(rule_string)
        rule = Rule(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            ast=ast,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        
        await Database.get_rules_collection().insert_one(rule.dict())
        return rule
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/rules/", response_model=List[Rule])
async def get_rules():
    rules = await Database.get_rules_collection().find().to_list(length=None)
    return rules

@app.post("/rules/evaluate/")
async def evaluate_rules(rule_ids: List[str], data: Dict):
    try:
        rules = await Database.get_rules_collection().find(
            {"id": {"$in": rule_ids}}
        ).to_list(length=None)
        
        if not rules:
            raise HTTPException(status_code=404, detail="No rules found")
            
        combined_ast = RuleService.combine_rules([Rule(**rule) for rule in rules])
        result = RuleService.evaluate_rule(combined_ast, data)
        
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))