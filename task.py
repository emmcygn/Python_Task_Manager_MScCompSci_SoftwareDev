class Task:
    def __init__(self, name, category, priority, due_date) -> None:
        self.name = name
        self.category = category    
        self.priority = priority
        self.due_date = due_date    
    
    def __repr__(self):
        return f"<Task: {self.name}, {self.category}, {self.priority}, {self.due_date} >"