from pydantic import BaseModel


class AddRepoRequest(BaseModel):
    full_name: str
    local_path: str
    policy_path: str | None = None


class RunRequest(BaseModel):
    job_name: str = "polish"
    dry_run: bool = False


class LoopRequest(BaseModel):
    job_name: str = "polish"
    hours: int | None = None
    max_iterations: int | None = None
    dry_run: bool = False
