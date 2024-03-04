from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class TodoItemResponse(BaseModel):
    priority: Optional[Literal["A", "B", "C", "D", "E"]] = Field(None, description="the priority, if there is no priority information, it should be None.")
    description: str = Field(..., description="the description of the todo item, it should be in Chinese.")
    project: List[Literal["生活","工作"]] = Field([], description="the project names of the todo item，only support `生活` and `工作`.")
    context: List[str] = Field([], description="the context names of the todo item, here you can add any context name. For example, `电视剧`.")
    recurrence: Optional[str] = Field(None, pattern=r"rec:\d+[mwdhs]", description="the recurrence of the todo item, the number should be a positive integer, if not an integer, change it into an interger with `d` to calculate the recurrence time. If there is no recurrence information, it should be None.")
    due: Optional[datetime] = Field(None, description="the due date is use to alert the user to finish the todo item, it should be option")

class TodoItem(TodoItemResponse):
    completed: bool = False
    completion_date: Optional[datetime] = None
    creation_date: Optional[datetime] = datetime.now()

    @classmethod
    def from_response(cls, response:TodoItemResponse):
        return cls(
            priority=response.priority,
            description=response.description,
            project=response.project,
            context=response.context,
            recurrence=response.recurrence,
            due=response.due,
        )

    @classmethod
    def from_todostr(cls, todo_str:str):
        ## parse the todo item from todotxt format
        todo = todo_str.split(" ")
        if todo[0] == "x":
            completed = True
            todo = todo[1:]
        else:
            completed = False
        if todo[0].startswith("(") and todo[0].endswith(")"):
            priority = todo[0][1]
            todo = todo[1:]
        else:
            priority = None
        if completed is True and todo[0].count("-") == 2:
            completion_date = datetime.strptime(todo[0], "%Y-%m-%d")
            todo = todo[1:]
        else:
            completion_date = None
        if todo[0].count("-") == 2:
            creation_date = datetime.strptime(todo[0], "%Y-%m-%d")
            todo = todo[1:]
        else:
            creation_date = None
        description = todo[0]
        todo = todo[1:]
        project = []
        context = []
        recurrence = None
        due = None
        for t in todo:
            if t.startswith("+"):
                project.append(t[1:])
            elif t.startswith("@"):
                context.append(t[1:])
            elif t.startswith("rec:"):
                recurrence = t
            elif t.startswith("due:"):
                due = datetime.strptime(t[4:], "%Y-%m-%d")
        return cls(
            completed=completed,
            priority=priority,
            completion_date=completion_date,
            creation_date=creation_date,
            description=description,
            project=project,
            context=context,
            recurrence=recurrence,
            due=due,
        )

    @classmethod
    def from_todotxt(cls, todo_file:str) -> List["TodoItem"]:
        with open(todo_file, "r") as f:
            todos = f.readlines()
        return [cls.from_todostr(todo) for todo in todos]

    def __str__(self):
        todo = []
        if self.completed:
            todo.append("x")
        if self.priority:
            todo.append(f"({self.priority})")
        if self.completed and self.completion_date:
            todo.append(self.completion_date.strftime("%Y-%m-%d"))
        if self.creation_date:
            todo.append(self.creation_date.strftime("%Y-%m-%d"))
        todo.append(self.description)
        if self.project:
            todo.append(" ".join(f"+{p}" for p in self.project))
        if self.context:
            todo.append(" ".join(f"@{c}" for c in self.context))
        if self.recurrence:
            todo.append(self.recurrence)
        if self.due:
            todo.append(self.due.strftime("due:%Y-%m-%d"))
        return " ".join(todo)

