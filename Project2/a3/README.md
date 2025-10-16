# Team Assignment System

This project automatically assigns students to teams of 5-6 members and matches them with projects based on their preferences.

## Overview

The system:
- Parses student preferences from a CSV file
- Forms subteams based on mutual student preferences
- Combines subteams into teams of 5-6 members
- Assigns projects to maximize preference satisfaction
- Outputs results in CSV format

## Requirements

- Python 3.x (standard library only, no external dependencies)

## Files

- `team_assignment.py` - Main assignment algorithm
- `run.sh` - Shell script to execute the program
- `requirements.txt` - Dependencies (none required)
- `cse403-preferences.csv` - Input data (student preferences)
- `successes.txt` - Documentation of successful AI-assisted development
- `failures.txt` - Documentation of challenges and limitations
- `test_output.py` - Optional test script to verify output format

## Usage

### Local Execution

```bash
./run.sh
```

This will generate `out.csv` at `/workspace/out.csv`.

### Docker Execution (Linux/macOS)

```bash
docker run --rm -it -v "$(pwd)":/workspace -w /workspace ubuntu bash -lc "\
export DEBIAN_FRONTEND=noninteractive && \
apt-get update && apt-get install -y unzip python3 && \
unzip -o a3.zip && \
cd a3 && \
chmod +x run.sh && \
./run.sh"
```

### Docker Execution (Windows PowerShell)

```powershell
docker run --rm -it -v "${PWD}:/workspace" -w /workspace ubuntu bash -lc "\
export DEBIAN_FRONTEND=noninteractive && \
apt-get update && apt-get install -y unzip python3 && \
unzip -o a3.zip && \
cd a3 && \
chmod +x run.sh && \
./run.sh"
```

## Input Format

The input CSV (`cse403-preferences.csv`) should have:
- Column D: Student netID
- Columns E-AY: Project preferences (with project name in brackets)
- Columns AZ-BE: Subteam member preferences

## Output Format

The output CSV (`out.csv`) contains:
- Column 1: Project name
- Column 2: List of team member netIDs (as Python list string)

Example:
```
CookiesShallNotPass,"['m1', 'm2', 'm3', 'm4', 'm5', 'm6']"
```

## Algorithm

1. **Parse CSV**: Extract netIDs, project preferences, and subteam preferences
2. **Form Subteams**: Use BFS to find mutually-connected students
3. **Validate Consistency**: Ensure subteam members have matching project preferences
4. **Combine Teams**: Merge subteams to form teams of 5-6 members
5. **Assign Projects**: Greedy assignment prioritizing highest preferences
6. **Output Results**: Write team assignments to CSV

## Constraints

- Teams must have 5-6 members
- Subteam members must stay together
- Each team is assigned a project from their top 5 preferences
- Larger subteams (5-6) get priority for their #1 choice

## Testing

To verify the output format:

```bash
python3 test_output.py
```

## Results

For the CSE403 dataset:
- 87 students processed
- 47 projects identified  
- 36 subteams formed
- 16 final teams created (all size 5-6)

## Known Limitations

1. Uses greedy assignment (not globally optimal)
2. Some projects may be assigned to multiple teams
3. Subteams with inconsistent preferences are split
4. No detailed satisfaction metrics generated

See `failures.txt` for complete list of limitations and potential improvements.

## Author

Created with AI assistance (Claude) for CSE490A2 Project 2.

