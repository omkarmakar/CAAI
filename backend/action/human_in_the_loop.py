from typing import Dict, Any, List

class HumanInTheLoop:
    """
    Manages tasks that require human review and approval.
    """
    def __init__(self):
        self.review_queue: List[Dict[str, Any]] = []
        self.next_task_id = 1

    def flag_for_review(self, task: Dict[str, Any], reason: str) -> int:
        """
        Flags a task for human review and adds it to the queue.

        Args:
            task (Dict[str, Any]): The task that needs review.
            reason (str): The reason for flagging the task.
        
        Returns:
            int: The ID of the task in the review queue.
        """
        task_id = self.next_task_id
        self.review_queue.append({
            "id": task_id,
            "task": task,
            "reason": reason,
            "status": "pending"
        })
        self.next_task_id += 1
        print(f"\n--- PENDING APPROVAL (Task ID: {task_id}) ---")
        print(f"Reason: {reason}")
        print(f"Action: {task.get('action')}")
        print(f"Params: {task.get('params')}")
        print("------------------------------------")
        return task_id

    def get_user_approval(self, task_id: int) -> bool:
        """
        Prompts the user for approval for a specific task.

        Args:
            task_id (int): The ID of the task to approve.

        Returns:
            bool: True if the user approves, False otherwise.
        """
        try:
            task_item = next(item for item in self.review_queue if item["id"] == task_id)
        except StopIteration:
            print(f"Error: Task with ID {task_id} not found.")
            return False

        while True:
            response = input(f"Approve task {task_id}? (yes/no): ").lower()
            if response in ["yes", "y"]:
                task_item["status"] = "approved"
                print("Task approved by user.")
                return True
            elif response in ["no", "n"]:
                task_item["status"] = "rejected"
                print("Task rejected by user.")
                return False
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")