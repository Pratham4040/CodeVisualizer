import ast
import operator
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --- FastAPI App Setup ---
app = FastAPI(
    title="AlgoVisualizer",
    description="A web application for visualizing algorithms and data structures.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodePayload(BaseModel):
    code: str

ITERATION_LIMIT = 1000


class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.scope = {}
        self.steps = []
        self.step_count = 0


    def _add_step(self, line, message):

        if self.step_count >= ITERATION_LIMIT:
            raise RecursionError("Exceeded maximum iteration limit")
        self.steps.append({
            "line": line,
            "message": message,
            "scope": self.scope.copy()
        })
        self.step_count += 1


    def generic_visit(self, node):
        super().generic_visit(node)


    def _evaluate_expr(self, node):

        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in self.scope:
                return self.scope[node.id]
            else:
                raise NameError(f"name '{node.id}' is not defined")
        elif isinstance(node, ast.BinOp):
            left = self._evaluate_expr(node.left)
            right = self._evaluate_expr(node.right)
            op_map = {
                ast.Add: operator.add, ast.Sub: operator.sub,
                ast.Mult: operator.mul, ast.Div: operator.truediv,
                ast.Mod: operator.mod,
            }
            if type(node.op) not in op_map:
                raise NotImplementedError(f"Operator {type(node.op)} not supported")

            return op_map[type(node.op)](left, right)
        elif isinstance(node, ast.Compare):
            left = self._evaluate_expr(node.left)
            right = self._evaluate_expr(node.comparators[0])
            op_map = {
                ast.Eq: operator.eq, ast.NotEq: operator.ne,
                ast.Lt: operator.lt, ast.LtE: operator.le,
                ast.Gt: operator.gt, ast.GtE: operator.ge,
            }
            if type(node.ops[0]) not in op_map:
                raise NotImplementedError(f"Comparison {type(node.ops[0])} not supported")
            return op_map[type(node.ops[0])](left, right)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'range':
                args = [self._evaluate_expr(arg) for arg in node.args]
                return range(*args)
            else:
                raise NotImplementedError(f"Function call '{getattr(node.func, 'id', 'N/A')}' not supported")
        else:
            raise NotImplementedError(f"Expression type '{type(node).__name__}' not supported")


    def visit_Assign(self, node):
        variable_name = node.targets[0].id
        value = self._evaluate_expr(node.value)
        self.scope[variable_name] = value
        
        self._add_step(
            node.lineno,
            f"Assigns {repr(value)} to variable '{variable_name}'"
        )

    
    def visit_If(self, node):
        test = self._evaluate_expr(node.test)
        self._add_step(node.lineno, f"Evaluates condition which is: {test}")
        if test:
            for child_node in node.body:
                self.visit(child_node)
        elif node.orelse:
            for child_node in node.orelse:
                self.visit(child_node)
    def visit_For(self, node):
        loop_var_name = node.target.id
        iterable = self._evaluate_expr(node.iter)
        self._add_step(node.lineno, f"Starts for-loop")
        for item in iterable:
            self.scope[loop_var_name] = item
            self._add_step(
                node.lineno,
                f"Loop variable '{loop_var_name}' is now {item}"
            )
            for child_node in node.body:
                self.visit(child_node)
    def visit_While(self, node):
        self._add_step(node.lineno, "Starts while-loop")
        while True:
            condition_val = self._evaluate_expr(node.test)
            self._add_step(node.lineno, f"Evaluates while-condition which is {condition_val}")
            if condition_val:
                for child_node in node.body:
                    self.visit(child_node)
            else:
                break
    def visit_Expr(self, node):
       if isinstance(node.value,ast.call):
           if isinstance(node.value.func,ast.Attribute):
               var_name = node.value.func.value.id
               method_name = node.value.func.attr
               if var_name in self.scope:
                   obj = self.scope[var_name]
                   args = [self._evaluate_expr(arg) for arg in node.value.args]
                   message=""
                   if isinstance(obj, list):
                       if method_name == "append":
                           obj.append(*args)
                           message = f"Appended {args[0]} to list '{var_name}'"
                       elif method_name == 'pop':
                           result = obj.pop(*args)
                           message = f"Pops {repr(result)} from list '{var_name}'"
                   elif isinstance(obj, dict):
                       if method_name == "update":
                           obj.update(*args)
                           message = f"Updated dictionary '{var_name}' with {args[0]}"
                       elif method_name == 'get':
                           result = obj.get(*args, None)
                           message = f"Gets {repr(result)} from dictionary '{var_name}'"
                       elif method_name == 'pop':
                            result = obj.pop(*args)
                            message = f"Pops key {repr(args[0])} from dict '{var_name}'"
                   if message:
                        self._add_step(node.lineno, message)
@app.post("/visualize")
async def visualize_code(payload: CodePayload):
    try:
        tree = ast.parse(payload.code)
        visitor = CodeVisitor()
        visitor.visit(tree)
        return {"status": "success", "steps": visitor.steps}
    except (SyntaxError, NameError, NotImplementedError, RecursionError) as e:
        raise HTTPException(status_code=400, detail=f"Execution Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)