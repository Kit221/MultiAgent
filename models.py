from pydantic import BaseModel, Field
from typing import List, Dict, Optional

#Агент 1: Навыки
class SkillItem(BaseModel):
    name: str
    level: str = Field(..., description="critical, important, or nice-to-have")
    trend: str = Field(..., description="growing, stable, or declining")

class SkillMap(BaseModel):
    languages: List[SkillItem]
    frameworks: List[SkillItem]
    infrastructure: List[SkillItem]
    soft_skills: List[SkillItem]

class Agent1Output(BaseModel):
    skill_map: SkillMap

#Агент 2: Зарплаты
class SalaryRange(BaseModel):
    min: int = 0
    median: int = 0
    max: int = 0

class GradeSalaries(BaseModel):
    Moscow_rub: Optional[SalaryRange] = None
    Regions_rub: Optional[SalaryRange] = None
    Remote_usd: Optional[SalaryRange] = None

class MarketTrend(BaseModel):
    status: str
    reason: str

class Agent2Output(BaseModel):
    salary_table: Dict[str, GradeSalaries]
    market_trend: MarketTrend
    top_employers: List[str]

#Агент 3: Карьера
class Resource(BaseModel):
    title: str
    type: str # course, book, doc

class LearningPhase(BaseModel):
    phase: str
    duration_days: int
    topics: List[str]
    resources: List[Resource]
    milestone: str

class GapAnalysis(BaseModel):
    quick_wins: List[str]
    long_term: List[str]

class PortfolioProject(BaseModel):
    title: str
    description: str
    tech_stack: List[str]

class Agent3Output(BaseModel):
    learning_path: List[LearningPhase]
    gap_analysis: GapAnalysis
    portfolio_project: PortfolioProject

#Агент 4: Критик
class Agent4Output(BaseModel):
    quality_score: int = Field(..., ge=0, le=100)
    is_consistent: bool
    warnings: List[str]
    justification: str