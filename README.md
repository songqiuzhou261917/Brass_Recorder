# 🚂 Brass_Recorder

A highly-disciplined, terminal-based live event tracking and data logging engine tailored for the heavy strategy board game **Brass: Birmingham**.

Designed with clean data engineering principles, this tool acts as a runtime game-state logger. It captures fine-grained player actions, financial shifts, and era-specific progressions during live gameplay, generating clean, normalized datasets perfectly formatted for downstream data warehousing and advanced strategy analytics (e.g., Google BigQuery & Looker Studio).

---

## 📂 Repository Structure

The project strictly follows a **data-code decoupling architecture**:

```text
Brass_Recorder/
├── .gitignore             # Shields local .venv and production datasets from version control
├── README.md              # Project documentation and technical overview
├── run_tracker.py         # Main execution script and state-machine core
└── data/                  # Decoupled storage for local analytical datasets
    ├── fact_match_players.csv    # Match metadata (Player seating, chosen colors, date)
    └── fact_action_events.csv     # Granular transaction fact table (Actions, costs, income)