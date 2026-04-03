from llm_service import LLMAgent
from models import Agent1Output, Agent2Output, Agent3Output, Agent4Output
import json

PROMPT_AGENT_1 = """
Ты senior IT рекрутер и аналитик рынка. 
Твоя задача: проанализировать специальность и выделить навыки.
Верни строго JSON соответствующий схеме:
{
  "skill_map": {
    "languages": [{"name": "...", "level": "critical/important/nice-to-have", "trend": "growing/stable/declining"}],
    "frameworks": [...],
    "infrastructure": [...],
    "soft_skills": [...]
  }
}
Не добавляй никакой текст кроме JSON.
"""

PROMPT_AGENT_2 = """
Ты эксперт по компенсациям в IT (C&B).
На основе предоставленного skill_map оцени зарплаты.
Регионы: Москва (RUB), Регионы РФ (RUB), Remote (USD).
Грейды: Junior, Middle, Senior, Lead.
Верни строго JSON:
{
  "salary_table": {
    "Junior": {"Moscow_rub": {"min": 0, "median": 0, "max": 0}, ... },
    ...
  },
  "market_trend": {"status": "growing/stable/declining", "reason": "short text"},
  "top_employers": ["Company 1", "Company 2"]
}
Цифры должны быть реалистичными для рынка РФ/Мира на 2026 год.
"""

PROMPT_AGENT_3 = """
Ты карьерный ментор в IT. Твоя задача — составить план развития на основе предоставленных навыков и зарплат.

Ты должен вернуть СТРОГО JSON объект, соответствующий следующей структуре. Не используй ключи вроде 'phase_1', 'phase_2'. Используй список объектов.

Структура ответа (пример):
{
  "learning_path": [
    {
      "phase": "Foundation",
      "duration_days": 30,
      "topics": ["Python Syntax", "Git Basics"],
      "resources": [
        {"title": "Python.org Tutorial", "type": "documentation"},
        {"title": "Stepik Course", "type": "course"}
      ],
      "milestone": "First commit to GitHub"
    },
    {
      "phase": "Practice",
      "duration_days": 30,
      "topics": ["Django ORM", "REST API"],
      "resources": [{"title": "Django Docs", "type": "documentation"}],
      "milestone": "Working API endpoint"
    },
    {
      "phase": "Portfolio",
      "duration_days": 30,
      "topics": ["Docker", "Deployment"],
      "resources": [{"title": "Docker Get Started", "type": "documentation"}],
      "milestone": "Deployed app"
    }
  ],
  "gap_analysis": {
    "quick_wins": ["Learn Docker CLI", "Basic SQL queries"],
    "long_term": ["System Design", "Kubernetes Architecture"]
  },
  "portfolio_project": {
    "title": "Task Manager API",
    "description": "RESTful API for managing tasks with auth.",
    "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Docker"]
  }
}

ВАЖНО:
1. Поле 'learning_path' должно быть СПИСКОМ (array), а не объектом.
2. В 'gap_analysis' ключи должны быть строго 'quick_wins' и 'long_term'.
3. В 'portfolio_project' обязательно наличие поля 'tech_stack' (список строк).
4. Не добавляй никакой текст до или после JSON.
"""

PROMPT_AGENT_4 = """
Ты технический директор (CTO), который проверяет отчет перед отправкой кандидату.
Проверь согласованность:
1. Соответствуют ли зарплаты уровню навыков?
2. Нет ли противоречий (например, declining навык в critical)?
Оцени качество отчета от 0 до 100.
Верни строго JSON:
{
  "quality_score": int,
  "is_consistent": bool,
  "warnings": ["warning 1", ...],
  "justification": "text"
}
"""


class CareerAgentSystem:
    def __init__(self, role: str):
        self.role = role
        self.llm = LLMAgent()
        self.report = {"role": role}

    def run(self):
        print(f" Запуск анализа для: {self.role}")

        #Agent 1
        print("Агент 1: Анализ рынка...")
        try:
            agent1_data = self.llm.ask(
                PROMPT_AGENT_1,
                f"Специальность: {self.role}",
                Agent1Output
            )
            self.report["agent_1_market_analysis"] = agent1_data
        except Exception as e:
            print("Ошибка агента 1:", e)
            return

        #Agent 2
        print("Агент 2: Оценка зарплат...")
        context_agent_2 = json.dumps(agent1_data, ensure_ascii=False)
        try:
            agent2_data = self.llm.ask(
                PROMPT_AGENT_2,
                f"Skill Map: {context_agent_2}",
                Agent2Output
            )
            self.report["agent_2_salary_assessment"] = agent2_data
        except Exception as e:
            print("Ошибка агента 2:", e)
            return

        #Agent 3
        print("Агент 3: Карьерный план...")
        context_agent_3 = json.dumps({
            "skills": agent1_data,
            "salaries": agent2_data
        }, ensure_ascii=False)
        try:
            agent3_data = self.llm.ask(
                PROMPT_AGENT_3,
                f"Контекст: {context_agent_3}",
                Agent3Output
            )
            self.report["agent_3_career_advice"] = agent3_data
        except Exception as e:
            print("Ошибка агента 3:", e)
            return

        #Agent 4
        print("Агент 4: Верификация...")
        full_context = json.dumps(self.report, ensure_ascii=False)
        try:
            agent4_data = self.llm.ask(
                PROMPT_AGENT_4,
                f"Полный отчет: {full_context}",
                Agent4Output
            )
            self.report["agent_4_verification"] = agent4_data
        except Exception as e:
            print("Ошибка агента 4:", e)
            return

        self._save_outputs()
        print("Готово!")

    def _save_outputs(self):
        with open("report.json", "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)

        r = self.report
        a1 = r.get("agent_1_market_analysis", {}).get("skill_map", {})
        a2 = r.get("agent_2_salary_assessment", {})
        a3 = r.get("agent_3_career_advice", {})
        a4 = r.get("agent_4_verification", {})

        md = [f"# {r['role']}\n"]

        # Skills
        md.append("## Навыки")
        for cat, items in a1.items():
            md.append(f"### {cat}")
            for i in items:
                md.append(f"- **{i['name']}**: {i['level']} ({i['trend']})")

        # Salary
        md.append("\n## Зарплаты (Middle, Москва)")
        try:
            s = a2["salary_table"]["Middle"]["Moscow_rub"]
            md.append(f"{s['min']} - {s['median']} - {s['max']} тыс. руб.")
        except:
            md.append("Н/Д")

        if a2.get("top_employers"):
            md.append(f"\n**Топ:** {', '.join(a2['top_employers'])}")

        # Career
        md.append("\n## План развития")
        for phase in a3.get("learning_path", []):
            md.append(f"**{phase['phase']}**: {phase['milestone']}")

        proj = a3.get("portfolio_project", {})
        if proj:
            md.append(f"\n**Проект:** {proj['title']} ({', '.join(proj.get('tech_stack', []))})")

        # Verification
        md.append(f"\n## Итог\nScore: {a4.get('quality_score')}/100 | Consistent: {a4.get('is_consistent')}")
        if a4.get("warnings"):
            for w in a4["warnings"]: md.append(f"- ⚠️ {w}")

        with open("report.md", "w", encoding="utf-8") as f:
            f.write("\n".join(md))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--role", type=str, required=True)
    args = parser.parse_args()

    system = CareerAgentSystem(args.role)
    system.run()