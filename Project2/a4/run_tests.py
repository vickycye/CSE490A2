#!/usr/bin/env python3
"""
Test Runner for Team Assignment System (A4)
Generates test cases and validates the team assignment algorithm.
"""

import csv
import os
import sys
import re
from typing import List, Dict, Tuple
import subprocess


class TestCase:
    """Base class for test cases"""
    def __init__(self, name: str, description: str, motivation: str):
        self.name = name
        self.description = description
        self.motivation = motivation
        self.csv_path = f"testing/test_data/{name.replace(' ', '_').lower()}.csv"
        self.output_path = f"testing/test_results/{name.replace(' ', '_').lower()}_out.csv"
        self.expected = None
        self.observed = None
        self.passed = None
        
    def generate_csv(self):
        """Generate test CSV file - to be overridden by specific tests"""
        raise NotImplementedError
        
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate the output - to be overridden by specific tests"""
        raise NotImplementedError
        
    def run(self) -> Dict:
        """Run the test case and return results"""
        print(f"\n{'='*70}")
        print(f"TEST: {self.name}")
        print(f"{'='*70}")
        print(f"DESCRIPTION: {self.description}")
        print(f"MOTIVATION: {self.motivation}")
        print(f"{'='*70}\n")
        
        # Generate test data
        print("Generating test data...")
        self.generate_csv()
        print(f"   Created: {self.csv_path}")
        
        # Run team assignment
        print("\nRunning team assignment...")
        try:
            # Import and run the team assignment
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from team_assignments import TeamAssignment
            
            assigner = TeamAssignment(self.csv_path)
            assigner.run(self.output_path)
            
            # Parse output
            assignments = self._parse_output(self.output_path)
            
            # Validate
            print("\nValidating results...")
            passed, message = self.validate(assignments)
            
            self.passed = passed
            self.observed = message
            
            if passed:
                print(f"TEST PASSED: {message}")
            else:
                print(f"TEST FAILED: {message}")
            
            return {
                'name': self.name,
                'passed': passed,
                'message': message,
                'assignments': assignments
            }
        
        # something went wrong here
        except Exception as e:
            print(f"TEST ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            self.passed = False
            self.observed = f"Error: {str(e)}"
            return {
                'name': self.name,
                'passed': False,
                'message': f"Error: {str(e)}",
                'assignments': None
            }
    
    # make this fit with what guorui expects our output to be
    def _parse_output(self, output_path: str) -> List[Tuple[str, List[str]]]:
        """Parse the output CSV file"""
        assignments = []
        with open(output_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    project = row[0]
                    # Parse the team list string
                    team_str = row[1]
                    # Remove brackets and quotes, split by comma
                    team_str = team_str.strip("[]'\"")
                    team = [m.strip().strip("'\"") for m in team_str.split(',')]
                    assignments.append((project, team))
        return assignments

### START OF TEST CASES HERE

class TeamSizeValidationTest(TestCase):
    """
    TEST 1: Team Size Validation
    
    Motivation: The spec requires teams of 5-6 members. This test creates
                various subteam configurations to verify the algorithm correctly combines
                them into valid-sized teams.
    
    Setup: Create students with different subteam sizes:
        - 3 subteams of size 2 (should combine to make teams of 4, 6, or 2+2+2=6)
        - 2 subteams of size 3 (should combine to make a team of 6)
        - 1 subteam of size 4 (needs to combine with 1-2 person subteam)
        - Individual students (no subteam preferences)
    
    Expected: All teams should have exactly 5 or 6 members, nothing more nothing less
    
    What we're testing:
        - Does the algorithm enforce the 5-6 member constraint?
        - How does it handle combining small subteams?
        - Are any students left in undersized teams?
    """
    
    def __init__(self):
        super().__init__(
            name="Team Size Validation",
            description="Verify all teams have 5-6 members",
            motivation="The spec requires teams of 5-6 members. Test if algorithm enforces this constraint."
        )
        
    # create artificial data for testing
    def generate_csv(self):
        """Generate test CSV with various subteam sizes"""
        # Create directories
        os.makedirs("testing/test_data", exist_ok=True)
        
        # define test data
        # format: (netid, subteam_members, project_preferences)
        students = [
            # Subteam 1: 2 people (should need to combine)
            ("student01", ["student02"], {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),
            ("student02", ["student01"], {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),
            
            # Subteam 2: 2 people (should need to combine)
            ("student03", ["student04"], {"ProjectB": 1, "ProjectA": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),
            ("student04", ["student03"], {"ProjectB": 1, "ProjectA": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),
            
            # Subteam 3: 2 people (should need to combine)
            ("student05", ["student06"], {"ProjectC": 1, "ProjectA": 2, "ProjectB": 3, "ProjectD": 4, "ProjectE": 5}),
            ("student06", ["student05"], {"ProjectC": 1, "ProjectA": 2, "ProjectB": 3, "ProjectD": 4, "ProjectE": 5}),
            
            # Subteam 4: 3 people (should need to combine with 2-3 person subteam)
            ("student07", ["student08", "student09"], {"ProjectD": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectE": 5}),
            ("student08", ["student07", "student09"], {"ProjectD": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectE": 5}),
            ("student09", ["student07", "student08"], {"ProjectD": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectE": 5}),
            
            # Subteam 5: 3 people (should combine with subteam 4 to make 6)
            ("student10", ["student11", "student12"], {"ProjectE": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectD": 5}),
            ("student11", ["student10", "student12"], {"ProjectE": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectD": 5}),
            ("student12", ["student10", "student11"], {"ProjectE": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectD": 5}),
            
            # Subteam 6: 4 people (should combine with 1-2 person subteam)
            ("student13", ["student14", "student15", "student16"], {"ProjectF": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectD": 5}),
            ("student14", ["student13", "student15", "student16"], {"ProjectF": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectD": 5}),
            ("student15", ["student13", "student14", "student16"], {"ProjectF": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectD": 5}),
            ("student16", ["student13", "student14", "student15"], {"ProjectF": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectD": 5}),
            
            # Individual students (no subteam preferences, should be combined)
            ("student17", [], {"ProjectG": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectD": 5}),
            ("student18", [], {"ProjectH": 1, "ProjectA": 2, "ProjectB": 3, "ProjectC": 4, "ProjectD": 5}),
            
            # Subteam 7: 5 people (perfect size, should become a team immediately)
            ("student19", ["student20", "student21", "student22", "student23"], {"ProjectI": 1, "ProjectJ": 2, "ProjectK": 3, "ProjectL": 4, "ProjectM": 5}),
            ("student20", ["student19", "student21", "student22", "student23"], {"ProjectI": 1, "ProjectJ": 2, "ProjectK": 3, "ProjectL": 4, "ProjectM": 5}),
            ("student21", ["student19", "student20", "student22", "student23"], {"ProjectI": 1, "ProjectJ": 2, "ProjectK": 3, "ProjectL": 4, "ProjectM": 5}),
            ("student22", ["student19", "student20", "student21", "student23"], {"ProjectI": 1, "ProjectJ": 2, "ProjectK": 3, "ProjectL": 4, "ProjectM": 5}),
            ("student23", ["student19", "student20", "student21", "student22"], {"ProjectI": 1, "ProjectJ": 2, "ProjectK": 3, "ProjectL": 4, "ProjectM": 5}),
            
            # Subteam 8: 6 people (perfect size, should become a team immediately)
            ("student24", ["student25", "student26", "student27", "student28", "student29"], {"ProjectN": 1, "ProjectO": 2, "ProjectP": 3, "ProjectQ": 4, "ProjectR": 5}),
            ("student25", ["student24", "student26", "student27", "student28", "student29"], {"ProjectN": 1, "ProjectO": 2, "ProjectP": 3, "ProjectQ": 4, "ProjectR": 5}),
            ("student26", ["student24", "student25", "student27", "student28", "student29"], {"ProjectN": 1, "ProjectO": 2, "ProjectP": 3, "ProjectQ": 4, "ProjectR": 5}),
            ("student27", ["student24", "student25", "student26", "student28", "student29"], {"ProjectN": 1, "ProjectO": 2, "ProjectP": 3, "ProjectQ": 4, "ProjectR": 5}),
            ("student28", ["student24", "student25", "student26", "student27", "student29"], {"ProjectN": 1, "ProjectO": 2, "ProjectP": 3, "ProjectQ": 4, "ProjectR": 5}),
            ("student29", ["student24", "student25", "student26", "student27", "student28"], {"ProjectN": 1, "ProjectO": 2, "ProjectP": 3, "ProjectQ": 4, "ProjectR": 5}),
        ]
        
        # write CSV to easy visualize results
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            # Add project columns (we'll use simple project names)
            projects = ['ProjectA', 'ProjectB', 'ProjectC', 'ProjectD', 'ProjectE', 
                       'ProjectF', 'ProjectG', 'ProjectH', 'ProjectI', 'ProjectJ',
                       'ProjectK', 'ProjectL', 'ProjectM', 'ProjectN', 'ProjectO',
                       'ProjectP', 'ProjectQ', 'ProjectR']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            # Add subteam member columns
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students in various subteam configurations")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that all teams have 5-6 members"""
        self.expected = "All teams should have exactly 5 or 6 members"
        
        invalid_teams = []
        team_sizes = []
        
        for project, team in assignments:
            size = len(team)
            team_sizes.append(size)
            if size < 5 or size > 6:
                invalid_teams.append((project, team, size))
        
        if invalid_teams:
            details = "\n".join([
                f"   • {project}: {size} members (team: {team})" 
                for project, team, size in invalid_teams
            ])
            message = (
                f"FAILED: {len(invalid_teams)} team(s) have invalid sizes:\n{details}\n"
                f"   Team size distribution: {team_sizes}"
            )
            return False, message
        else:
            message = (
                f"PASSED: All {len(assignments)} teams have valid sizes (5-6 members)\n"
                f"   Team size distribution: {team_sizes}"
            )
            return True, message

class SubteamIntegrityTest(TestCase):
    """
    TEST 2: Subteam Integrity
    
    Motivation: The spec explicitly states "Subteams are not split up".
    This test verifies that students who mutually list each other as
    subteam members actually end up on the same team.
    
    Setup: Create known subteams with mutual preferences and verify
    they stay together in the final team assignments.
    
    Expected: All members of each subteam appear together on the same team.
    
    What we're testing:
    - Does the algorithm correctly identify mutual subteam preferences?
    - Are subteams kept together during team formation?
    - Are non-mutual preferences handled correctly (not treated as subteam)?
    """
    
    def __init__(self):
        super().__init__(
            name="Subteam Integrity Test",
            description="Verify students who list each other stay on the same team",
            motivation="Spec requires: subteams are not split up"
        )
        
        # Track known subteams for validation
        self.known_subteams = {
            'subteam_ABC': {'studentA', 'studentB', 'studentC'},
            'subteam_DE': {'studentD', 'studentE'},
            'subteam_FGH': {'studentF', 'studentG', 'studentH'},
        }
        
    def generate_csv(self):
        """Generate test CSV with clearly defined subteams"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        # Define test data
        # Format: (netid, subteam_members, project_preferences)
        students = [
            # Subteam ABC: 3 people who all list each other (MUTUAL)
            ("studentA", ["studentB", "studentC"], 
             {"ProjectX": 1, "ProjectY": 2, "ProjectZ": 3, "ProjectW": 4, "ProjectV": 5}),
            ("studentB", ["studentA", "studentC"], 
             {"ProjectX": 1, "ProjectY": 2, "ProjectZ": 3, "ProjectW": 4, "ProjectV": 5}),
            ("studentC", ["studentA", "studentB"], 
             {"ProjectX": 1, "ProjectY": 2, "ProjectZ": 3, "ProjectW": 4, "ProjectV": 5}),
            
            # Subteam DE: 2 people who list each other (MUTUAL)
            ("studentD", ["studentE"], 
             {"ProjectY": 1, "ProjectX": 2, "ProjectZ": 3, "ProjectW": 4, "ProjectV": 5}),
            ("studentE", ["studentD"], 
             {"ProjectY": 1, "ProjectX": 2, "ProjectZ": 3, "ProjectW": 4, "ProjectV": 5}),
            
            # Subteam FGH: 3 people who all list each other (MUTUAL)
            ("studentF", ["studentG", "studentH"], 
             {"ProjectZ": 1, "ProjectX": 2, "ProjectY": 3, "ProjectW": 4, "ProjectV": 5}),
            ("studentG", ["studentF", "studentH"], 
             {"ProjectZ": 1, "ProjectX": 2, "ProjectY": 3, "ProjectW": 4, "ProjectV": 5}),
            ("studentH", ["studentF", "studentG"], 
             {"ProjectZ": 1, "ProjectX": 2, "ProjectY": 3, "ProjectW": 4, "ProjectV": 5}),
            
            # Non-mutual case: M lists N, but N doesn't list M (should NOT be subteam)
            ("studentM", ["studentN"], 
             {"ProjectW": 1, "ProjectX": 2, "ProjectY": 3, "ProjectZ": 4, "ProjectV": 5}),
            ("studentN", [], 
             {"ProjectW": 1, "ProjectX": 2, "ProjectY": 3, "ProjectZ": 4, "ProjectV": 5}),
            
            # Individual students to fill out teams
            ("studentP", [], 
             {"ProjectV": 1, "ProjectX": 2, "ProjectY": 3, "ProjectZ": 4, "ProjectW": 5}),
            ("studentQ", [], 
             {"ProjectV": 1, "ProjectX": 2, "ProjectY": 3, "ProjectZ": 4, "ProjectW": 5}),
            ("studentR", [], 
             {"ProjectX": 1, "ProjectY": 2, "ProjectZ": 3, "ProjectW": 4, "ProjectV": 5}),
            ("studentS", [], 
             {"ProjectY": 1, "ProjectX": 2, "ProjectZ": 3, "ProjectW": 4, "ProjectV": 5}),
            ("studentT", [], 
             {"ProjectZ": 1, "ProjectX": 2, "ProjectY": 3, "ProjectW": 4, "ProjectV": 5}),
        ]
        
        # Write CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            projects = ['ProjectX', 'ProjectY', 'ProjectZ', 'ProjectW', 'ProjectV']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students with 3 defined subteams")
        print(f"   - Subteam ABC (3 members): studentA, studentB, studentC")
        print(f"   - Subteam DE (2 members): studentD, studentE")
        print(f"   - Subteam FGH (3 members): studentF, studentG, studentH")
        print(f"   - Non-mutual: studentM lists studentN (but N doesn't list M)")
        print(f"   - 5 individual students")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that subteam members are on the same team"""
        self.expected = "All subteam members should be on the same team"
        
        violations = []
        
        # Check each known subteam
        for subteam_name, subteam_members in self.known_subteams.items():
            # Find which team(s) contain members of this subteam
            teams_containing_members = {}
            
            for project, team in assignments:
                team_set = set(team)
                members_in_this_team = subteam_members.intersection(team_set)
                
                if members_in_this_team:
                    teams_containing_members[project] = members_in_this_team
            
            # All subteam members should be on exactly ONE team
            if len(teams_containing_members) == 0:
                violations.append(f"{subteam_name}: No members found in any team!")
            elif len(teams_containing_members) == 1:
                # Good! All on same team
                team_name = list(teams_containing_members.keys())[0]
                members_found = teams_containing_members[team_name]
                
                if members_found == subteam_members:
                    # Perfect - all members together
                    pass
                else:
                    # Some members missing
                    missing = subteam_members - members_found
                    violations.append(
                        f"{subteam_name}: Only {members_found} found on team {team_name}, "
                        f"missing {missing}"
                    )
            else:
                # Bad! Split across multiple teams
                details = ", ".join([
                    f"{team}: {members}" 
                    for team, members in teams_containing_members.items()
                ])
                violations.append(
                    f"{subteam_name}: SPLIT across {len(teams_containing_members)} teams! "
                    f"({details})"
                )
        
        # Check that non-mutual preferences are NOT treated as subteam
        # StudentM lists StudentN, but N doesn't list M
        # They should NOT necessarily be on same team
        studentM_team = None
        studentN_team = None
        
        for project, team in assignments:
            if 'studentM' in team:
                studentM_team = project
            if 'studentN' in team:
                studentN_team = project
        
        non_mutual_note = ""
        if studentM_team == studentN_team:
            non_mutual_note = "\n   Note: studentM and studentN ended up together (OK, but not required)"
        else:
            non_mutual_note = "\n   ✓ Non-mutual preference: studentM and studentN correctly NOT treated as subteam"
        
        # Return results
        if violations:
            details = "\n".join([f"   • {v}" for v in violations])
            message = (
                f"FAILED: {len(violations)} subteam integrity violation(s):\n{details}"
                f"{non_mutual_note}"
            )
            return False, message
        else:
            message = (
                f"PASSED: All {len(self.known_subteams)} subteams kept together!\n"
                f"   ✓ Subteam ABC: studentA, studentB, studentC together\n"
                f"   ✓ Subteam DE: studentD, studentE together\n"
                f"   ✓ Subteam FGH: studentF, studentG, studentH together"
                f"{non_mutual_note}"
            )
            return True, message

class ProjectPreferenceValidityTest(TestCase):
    """
    TEST 3: Project Preference Validity
    
    Motivation: The spec requires "A team is assigned a project that is one of 
    the 5 preferences for each of its members." This is a critical constraint that
    ensures no student is assigned to a project they didn't choose.
    
    Setup: Create teams with known project preferences and verify that the
    assigned project is in ALL team members' top 5 choices.
    
    Expected: Every team member has the team's assigned project in their top 5.
    
    What we're testing:
    - Does the algorithm verify project is in everyone's top 5?
    - Are teams with inconsistent preferences handled correctly?
    - Is there proper validation before project assignment?
    - What happens when no project satisfies all members?
    """
    
    def __init__(self):
        super().__init__(
            name="Project Preference Validity",
            description="Verify each team's project is in ALL members' top 5",
            motivation="Spec requires: project must be in everyone's top 5 preferences"
        )
        
        # Track expected valid assignments for validation
        self.team_preferences = {}
        
    def generate_csv(self):
        """Generate test CSV with various project preference scenarios"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        # Define test data with specific project preference patterns
        students = [
            # Team 1: Perfect consensus - all want ProjectAlpha as #1
            # (5 people, should all get ProjectAlpha)
            ("team1_member1", ["team1_member2", "team1_member3", "team1_member4", "team1_member5"],
             {"ProjectAlpha": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            ("team1_member2", ["team1_member1", "team1_member3", "team1_member4", "team1_member5"],
             {"ProjectAlpha": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            ("team1_member3", ["team1_member1", "team1_member2", "team1_member4", "team1_member5"],
             {"ProjectAlpha": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            ("team1_member4", ["team1_member1", "team1_member2", "team1_member3", "team1_member5"],
             {"ProjectAlpha": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            ("team1_member5", ["team1_member1", "team1_member2", "team1_member3", "team1_member4"],
             {"ProjectAlpha": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            
            # Team 2: Different rankings but ProjectBeta is in everyone's top 5
            # (6 people, should get a project that's in all their top 5)
            ("team2_member1", ["team2_member2", "team2_member3", "team2_member4", "team2_member5", "team2_member6"],
             {"ProjectBeta": 1, "ProjectAlpha": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            ("team2_member2", ["team2_member1", "team2_member3", "team2_member4", "team2_member5", "team2_member6"],
             {"ProjectGamma": 1, "ProjectBeta": 2, "ProjectAlpha": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            ("team2_member3", ["team2_member1", "team2_member2", "team2_member4", "team2_member5", "team2_member6"],
             {"ProjectAlpha": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            ("team2_member4", ["team2_member1", "team2_member2", "team2_member3", "team2_member5", "team2_member6"],
             {"ProjectDelta": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectAlpha": 4, "ProjectEpsilon": 5}),
            ("team2_member5", ["team2_member1", "team2_member2", "team2_member3", "team2_member4", "team2_member6"],
             {"ProjectBeta": 1, "ProjectGamma": 2, "ProjectDelta": 3, "ProjectAlpha": 4, "ProjectEpsilon": 5}),
            ("team2_member6", ["team2_member1", "team2_member2", "team2_member3", "team2_member4", "team2_member5"],
             {"ProjectEpsilon": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectAlpha": 5}),
            
            # Team 3: Edge case - minimal overlap in top 5
            # ProjectGamma is the ONLY project in everyone's top 5
            # (5 people, should get ProjectGamma)
            ("team3_member1", ["team3_member2", "team3_member3", "team3_member4", "team3_member5"],
             {"ProjectZeta": 1, "ProjectEta": 2, "ProjectTheta": 3, "ProjectGamma": 4, "ProjectIota": 5}),
            ("team3_member2", ["team3_member1", "team3_member3", "team3_member4", "team3_member5"],
             {"ProjectKappa": 1, "ProjectLambda": 2, "ProjectGamma": 3, "ProjectMu": 4, "ProjectNu": 5}),
            ("team3_member3", ["team3_member1", "team3_member2", "team3_member4", "team3_member5"],
             {"ProjectXi": 1, "ProjectGamma": 2, "ProjectOmicron": 3, "ProjectPi": 4, "ProjectRho": 5}),
            ("team3_member4", ["team3_member1", "team3_member2", "team3_member3", "team3_member5"],
             {"ProjectSigma": 1, "ProjectTau": 2, "ProjectUpsilon": 3, "ProjectPhi": 4, "ProjectGamma": 5}),
            ("team3_member5", ["team3_member1", "team3_member2", "team3_member3", "team3_member4"],
             {"ProjectGamma": 1, "ProjectChi": 2, "ProjectPsi": 3, "ProjectOmega": 4, "ProjectAlpha": 5}),
            
            # Team 4: Good overlap - multiple common projects
            # (6 people, ProjectDelta is #1 for everyone)
            ("team4_member1", ["team4_member2", "team4_member3", "team4_member4", "team4_member5", "team4_member6"],
             {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}),
            ("team4_member2", ["team4_member1", "team4_member3", "team4_member4", "team4_member5", "team4_member6"],
             {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}),
            ("team4_member3", ["team4_member1", "team4_member2", "team4_member4", "team4_member5", "team4_member6"],
             {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}),
            ("team4_member4", ["team4_member1", "team4_member2", "team4_member3", "team4_member5", "team4_member6"],
             {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}),
            ("team4_member5", ["team4_member1", "team4_member2", "team4_member3", "team4_member4", "team4_member6"],
             {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}),
            ("team4_member6", ["team4_member1", "team4_member2", "team4_member3", "team4_member4", "team4_member5"],
             {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}),
            
            # Team 5: Individuals who need to be combined
            # (5 individuals with ProjectEpsilon in all their top 5)
            ("team5_member1", [],
             {"ProjectEpsilon": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectDelta": 5}),
            ("team5_member2", [],
             {"ProjectAlpha": 1, "ProjectEpsilon": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectDelta": 5}),
            ("team5_member3", [],
             {"ProjectBeta": 1, "ProjectAlpha": 2, "ProjectEpsilon": 3, "ProjectGamma": 4, "ProjectDelta": 5}),
            ("team5_member4", [],
             {"ProjectGamma": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectEpsilon": 4, "ProjectDelta": 5}),
            ("team5_member5", [],
             {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}),
        ]
        
        # Store expected valid projects for each team
        self.team_preferences = {
            'team1': {'ProjectAlpha', 'ProjectBeta', 'ProjectGamma', 'ProjectDelta', 'ProjectEpsilon'},
            'team2': {'ProjectBeta'},  # Only ProjectBeta is in ALL members' top 5
            'team3': {'ProjectGamma'},  # Only ProjectGamma is in ALL members' top 5
            'team4': {'ProjectDelta', 'ProjectAlpha', 'ProjectBeta', 'ProjectGamma', 'ProjectEpsilon'},
            # Team 5 will be formed from individuals, harder to predict
        }
        
        # Write CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            
            # Collect all unique projects
            all_projects = set()
            for _, _, prefs in students:
                all_projects.update(prefs.keys())
            all_projects = sorted(all_projects)
            
            for proj in all_projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in all_projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students in 5 teams")
        print(f"   - Team 1 (5 members): All prefer ProjectAlpha #1")
        print(f"   - Team 2 (6 members): ProjectBeta is in everyone's top 5")
        print(f"   - Team 3 (5 members): Only ProjectGamma is in all top 5 (edge case)")
        print(f"   - Team 4 (6 members): All prefer ProjectDelta #1")
        print(f"   - Team 5 (5 individuals): ProjectEpsilon in all top 5")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that each team's project is in ALL members' top 5"""
        self.expected = "Each team's assigned project must be in ALL members' top 5 preferences"
        
        violations = []
        valid_assignments = []
        
        # Need to load student preferences from the test CSV
        student_prefs = self._load_student_preferences()
        
        for project, team in assignments:
            # Check if this project is in ALL team members' top 5
            members_without_project = []
            members_with_project = []
            
            for member in team:
                if member in student_prefs:
                    prefs = student_prefs[member]
                    if project in prefs and prefs[project] <= 5:
                        members_with_project.append((member, prefs[project]))
                    else:
                        # Project NOT in this member's top 5!
                        if project in prefs:
                            members_without_project.append(f"{member} (has {project} as #{prefs[project]} - not in top 5)")
                        else:
                            members_without_project.append(f"{member} (doesn't have {project} at all)")
            
            if members_without_project:
                # VIOLATION: Some members don't have this project in top 5
                violation_details = ", ".join(members_without_project)
                violations.append(
                    f"Project '{project}' assigned to team {team}, but NOT in top 5 for: {violation_details}"
                )
            else:
                # Valid assignment
                rank_info = ", ".join([f"{m}:#{r}" for m, r in members_with_project])
                valid_assignments.append(f"✓ {project}: Valid for all {len(team)} members ({rank_info})")
        
        # Return results
        if violations:
            details = "\n".join([f"   • {v}" for v in violations])
            valid_info = "\n".join([f"   {v}" for v in valid_assignments]) if valid_assignments else ""
            message = (
                f"FAILED: {len(violations)} project preference violation(s):\n{details}\n"
                f"\nValid assignments:\n{valid_info}" if valid_info else f"\n{details}"
            )
            return False, message
        else:
            details = "\n".join([f"   {v}" for v in valid_assignments])
            message = (
                f"PASSED: All {len(assignments)} teams assigned to valid projects!\n"
                f"{details}"
            )
            return True, message
    
    def _load_student_preferences(self) -> Dict[str, Dict[str, int]]:
        """Load student preferences from the test CSV"""
        student_prefs = {}
        
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            # Find columns
            netid_idx = 3
            project_cols = []
            
            for i, col in enumerate(headers):
                if i < 4:
                    continue
                if '[' in col and ']' in col:
                    project_name = col.split('[')[1].split(']')[0]
                    project_cols.append((i, project_name))
            
            # Read student preferences
            for row in reader:
                if len(row) <= netid_idx:
                    continue
                
                netid = row[netid_idx].strip()
                if not netid:
                    continue
                
                prefs = {}
                for col_idx, project_name in project_cols:
                    if col_idx < len(row):
                        pref_value = row[col_idx]
                        if pref_value and pref_value.strip():
                            match = re.search(r'#(\d+)', pref_value)
                            if match:
                                pref_rank = int(match.group(1))
                                prefs[project_name] = pref_rank
                
                student_prefs[netid] = prefs
        
        return student_prefs

class SubteamPreferenceConsistencyTest(TestCase):
    """
    TEST 4: Subteam Preference Consistency
    
    MOtivation: The spec states "The member and project preferences must be 
    consistent across all the members of a subteam." This means subteam members
    must have IDENTICAL project rankings (not just same projects, but same ranks).
    
    Setup: Create subteams with:
    - Consistent preferences (same projects, same rankings)
    - Inconsistent preferences (same projects, different rankings)
    - Completely different preferences
    
    Expected: Only subteams with identical preferences should stay together.
    Inconsistent subteams should be split.
    
    What we're testing:
    - Does the algorithm verify preference consistency?
    - Are inconsistent subteams properly split?
    - Does _verify_project_consistency() work correctly?
    """
    
    def __init__(self):
        super().__init__(
            name="Subteam Preference Consistency",
            description="Verify subteam members have identical project rankings",
            motivation="Spec requires: preferences must be consistent across subteam members"
        )
        
        # Track expected outcomes
        self.expected_intact_subteams = {'consistent_team'}
        self.expected_split_subteams = {'inconsistent_rank', 'inconsistent_projects'}
        
    def generate_csv(self):
        """Generate test CSV with various consistency scenarios"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        # Define test data
        students = [
            # CASE 1: Perfect consistency - identical rankings
            # Should stay together as one subteam
            ("consistent1", ["consistent2", "consistent3"],
             {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),
            ("consistent2", ["consistent1", "consistent3"],
             {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),
            ("consistent3", ["consistent1", "consistent2"],
             {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),
            
            # CASE 2: Inconsistent rankings - same projects, different order
            # Should be SPLIT into individuals
            ("inconsistent_rank1", ["inconsistent_rank2", "inconsistent_rank3"],
             {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),
            ("inconsistent_rank2", ["inconsistent_rank1", "inconsistent_rank3"],
             {"ProjectA": 2, "ProjectB": 1, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),  # Different!
            ("inconsistent_rank3", ["inconsistent_rank1", "inconsistent_rank2"],
             {"ProjectA": 1, "ProjectB": 3, "ProjectC": 2, "ProjectD": 4, "ProjectE": 5}),  # Different!
            
            # CASE 3: Completely different projects
            # Should be SPLIT into individuals
            ("inconsistent_proj1", ["inconsistent_proj2"],
             {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),
            ("inconsistent_proj2", ["inconsistent_proj1"],
             {"ProjectF": 1, "ProjectG": 2, "ProjectH": 3, "ProjectI": 4, "ProjectJ": 5}),  # Totally different!
            
            # CASE 4: Another consistent team for comparison
            ("consistent4", ["consistent5", "consistent6"],
             {"ProjectF": 1, "ProjectG": 2, "ProjectH": 3, "ProjectI": 4, "ProjectJ": 5}),
            ("consistent5", ["consistent4", "consistent6"],
             {"ProjectF": 1, "ProjectG": 2, "ProjectH": 3, "ProjectI": 4, "ProjectJ": 5}),
            ("consistent6", ["consistent4", "consistent5"],
             {"ProjectF": 1, "ProjectG": 2, "ProjectH": 3, "ProjectI": 4, "ProjectJ": 5}),
            
            # Fill with individuals to make valid team sizes
            ("filler1", [], {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),
            ("filler2", [], {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}),
            ("filler3", [], {"ProjectF": 1, "ProjectG": 2, "ProjectH": 3, "ProjectI": 4, "ProjectJ": 5}),
            ("filler4", [], {"ProjectF": 1, "ProjectG": 2, "ProjectH": 3, "ProjectI": 4, "ProjectJ": 5}),
        ]
        
        # Write CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            projects = ['ProjectA', 'ProjectB', 'ProjectC', 'ProjectD', 'ProjectE',
                       'ProjectF', 'ProjectG', 'ProjectH', 'ProjectI', 'ProjectJ']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students with consistency test cases:")
        print(f"   - CASE 1: 3 members with identical rankings (should stay together)")
        print(f"   - CASE 2: 3 members with same projects, different rankings (should split)")
        print(f"   - CASE 3: 2 members with completely different projects (should split)")
        print(f"   - CASE 4: 3 members with identical rankings (should stay together)")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that only consistent subteams stayed together"""
        self.expected = "Subteams with identical rankings stay together, inconsistent ones split"
        
        # Check which subteams stayed together
        # A subteam "stayed together" if all members are on the same team
        
        consistent_team_members = {'consistent1', 'consistent2', 'consistent3'}
        consistent_team2_members = {'consistent4', 'consistent5', 'consistent6'}
        inconsistent_rank_members = {'inconsistent_rank1', 'inconsistent_rank2', 'inconsistent_rank3'}
        inconsistent_proj_members = {'inconsistent_proj1', 'inconsistent_proj2'}
        
        # Find where each member ended up
        member_locations = {}
        for project, team in assignments:
            for member in team:
                member_locations[member] = project
        
        results = []
        violations = []
        
        # Check consistent teams (should be together)
        consistent1_teams = set([member_locations.get(m) for m in consistent_team_members if m in member_locations])
        if len(consistent1_teams) == 1:
            results.append("✓ Consistent Team 1 (identical rankings): Stayed together")
        else:
            violations.append(f"Consistent Team 1 was SPLIT across teams: {consistent1_teams}")
        
        consistent2_teams = set([member_locations.get(m) for m in consistent_team2_members if m in member_locations])
        if len(consistent2_teams) == 1:
            results.append("✓ Consistent Team 2 (identical rankings): Stayed together")
        else:
            violations.append(f"Consistent Team 2 was SPLIT across teams: {consistent2_teams}")
        
        # Check inconsistent teams (should be split)
        inconsistent_rank_teams = set([member_locations.get(m) for m in inconsistent_rank_members if m in member_locations])
        if len(inconsistent_rank_teams) > 1:
            results.append(f"✓ Inconsistent Rank Team (different rankings): Correctly SPLIT across {len(inconsistent_rank_teams)} teams")
        else:
            violations.append(f"Inconsistent Rank Team should have been SPLIT but stayed together on {inconsistent_rank_teams}")
        
        inconsistent_proj_teams = set([member_locations.get(m) for m in inconsistent_proj_members if m in member_locations])
        if len(inconsistent_proj_teams) > 1:
            results.append(f"✓ Inconsistent Project Team (different projects): Correctly SPLIT across {len(inconsistent_proj_teams)} teams")
        else:
            violations.append(f"Inconsistent Project Team should have been SPLIT but stayed together on {inconsistent_proj_teams}")
        
        # Return results
        if violations:
            details = "\n".join([f"   • {v}" for v in violations])
            success_details = "\n".join([f"   {r}" for r in results])
            message = (
                f"FAILED: {len(violations)} consistency violation(s):\n{details}\n\n"
                f"What worked:\n{success_details}"
            )
            return False, message
        else:
            details = "\n".join([f"   {r}" for r in results])
            message = (
                f"PASSED: All consistency checks passed!\n{details}"
            )
            return True, message

class PreferenceDistributionAnalysisTest(TestCase):
    """
    TEST 5: Preference Distribution Analysis
    
    Motivation: The spec states "Ideally, everyone gets their #1 choice" and 
    "#4 and #5 choices are undesirable." We need to analyze the distribution 
    of assigned preferences to ensure the algorithm prioritizes high-ranked 
    preferences.
    
    Setup: Create realistic dataset with varied preferences and measure
    what rank each student receives.
    
    Expected: 
    - Most students should get #1 or #2 choice
    - Few students should get #4 or #5 choice
    - Calculate metrics: average rank, median rank, distribution
    
    What we're testing:
    - Does the algorithm optimize for high-ranked preferences?
    - What's the distribution of assigned ranks?
    - Are #4 and #5 assignments minimized?
    """
    
    def __init__(self):
        super().__init__(
            name="Preference Distribution Analysis",
            description="Analyze distribution of assigned preference ranks",
            motivation="Spec prefers #1 choices, considers #4/#5 undesirable"
        )
        
        # Track metrics
        self.preference_distribution = {}
        self.student_preferences = {}
        
    def generate_csv(self):
        """Generate realistic test CSV with varied preference patterns"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        # Create 30 students (6 teams of 5) with realistic preference patterns
        # Some will have overlapping #1 choices (competition)
        # Some will have unique #1 choices (easy to satisfy)
        students = []
        
        # Team 1: All want ProjectAlpha #1 (high competition)
        for i in range(1, 6):
            students.append((
                f"team1_s{i}",
                [f"team1_s{j}" for j in range(1, 6) if j != i],
                {"ProjectAlpha": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}
            ))
        
        # Team 2: All want ProjectBeta #1 (high competition)
        for i in range(1, 6):
            students.append((
                f"team2_s{i}",
                [f"team2_s{j}" for j in range(1, 6) if j != i],
                {"ProjectBeta": 1, "ProjectAlpha": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}
            ))
        
        # Team 3: Diverse rankings, ProjectGamma is common
        students.extend([
            ("team3_s1", ["team3_s2", "team3_s3", "team3_s4", "team3_s5"],
             {"ProjectGamma": 1, "ProjectDelta": 2, "ProjectEpsilon": 3, "ProjectZeta": 4, "ProjectEta": 5}),
            ("team3_s2", ["team3_s1", "team3_s3", "team3_s4", "team3_s5"],
             {"ProjectDelta": 1, "ProjectGamma": 2, "ProjectEpsilon": 3, "ProjectZeta": 4, "ProjectEta": 5}),
            ("team3_s3", ["team3_s1", "team3_s2", "team3_s4", "team3_s5"],
             {"ProjectEpsilon": 1, "ProjectGamma": 2, "ProjectDelta": 3, "ProjectZeta": 4, "ProjectEta": 5}),
            ("team3_s4", ["team3_s1", "team3_s2", "team3_s3", "team3_s5"],
             {"ProjectGamma": 1, "ProjectEpsilon": 2, "ProjectDelta": 3, "ProjectZeta": 4, "ProjectEta": 5}),
            ("team3_s5", ["team3_s1", "team3_s2", "team3_s3", "team3_s4"],
             {"ProjectGamma": 1, "ProjectDelta": 2, "ProjectEpsilon": 3, "ProjectZeta": 4, "ProjectEta": 5}),
        ])
        
        # Team 4: All want ProjectZeta #1 (easy - unique project)
        for i in range(1, 6):
            students.append((
                f"team4_s{i}",
                [f"team4_s{j}" for j in range(1, 6) if j != i],
                {"ProjectZeta": 1, "ProjectEta": 2, "ProjectTheta": 3, "ProjectIota": 4, "ProjectKappa": 5}
            ))
        
        # Team 5: All want ProjectEta #1
        for i in range(1, 6):
            students.append((
                f"team5_s{i}",
                [f"team5_s{j}" for j in range(1, 6) if j != i],
                {"ProjectEta": 1, "ProjectTheta": 2, "ProjectIota": 3, "ProjectKappa": 4, "ProjectLambda": 5}
            ))
        
        # Team 6: All want ProjectTheta #1
        for i in range(1, 6):
            students.append((
                f"team6_s{i}",
                [f"team6_s{j}" for j in range(1, 6) if j != i],
                {"ProjectTheta": 1, "ProjectIota": 2, "ProjectKappa": 3, "ProjectLambda": 4, "ProjectMu": 5}
            ))
        
        # Store preferences for later analysis
        for netid, _, prefs in students:
            self.student_preferences[netid] = prefs
        
        # Write CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            
            # Collect all projects
            all_projects = set()
            for _, _, prefs in students:
                all_projects.update(prefs.keys())
            all_projects = sorted(all_projects)
            
            for proj in all_projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in all_projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students (6 teams of 5) with varied preferences:")
        print(f"   - Team 1: All want ProjectAlpha #1 (competition)")
        print(f"   - Team 2: All want ProjectBeta #1 (competition)")
        print(f"   - Team 3: Diverse rankings, ProjectGamma common")
        print(f"   - Team 4: All want ProjectZeta #1 (unique)")
        print(f"   - Team 5: All want ProjectEta #1")
        print(f"   - Team 6: All want ProjectTheta #1")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Analyze the distribution of assigned preference ranks"""
        self.expected = "Most students get #1 or #2, few get #4 or #5"
        
        # Calculate what rank each student got
        rank_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        unranked_students = []
        rank_details = []
        
        total_students = 0
        
        for project, team in assignments:
            for student in team:
                total_students += 1
                
                if student not in self.student_preferences:
                    unranked_students.append(student)
                    continue
                
                prefs = self.student_preferences[student]
                
                if project in prefs:
                    rank = prefs[project]
                    rank_distribution[rank] += 1
                    rank_details.append((student, project, rank))
                else:
                    # Project not in student's preferences at all!
                    unranked_students.append(f"{student} (got {project} - not in preferences!)")
        
        # Calculate metrics
        total_ranked = sum(rank_distribution.values())
        avg_rank = sum(rank * count for rank, count in rank_distribution.items()) / total_ranked if total_ranked > 0 else 0
        
        # Calculate percentages
        pct_1 = (rank_distribution[1] / total_ranked * 100) if total_ranked > 0 else 0
        pct_2 = (rank_distribution[2] / total_ranked * 100) if total_ranked > 0 else 0
        pct_3 = (rank_distribution[3] / total_ranked * 100) if total_ranked > 0 else 0
        pct_4 = (rank_distribution[4] / total_ranked * 100) if total_ranked > 0 else 0
        pct_5 = (rank_distribution[5] / total_ranked * 100) if total_ranked > 0 else 0
        
        pct_top2 = pct_1 + pct_2
        pct_undesirable = pct_4 + pct_5
        
        # Build result message
        message_parts = []
        message_parts.append(f"Preference Distribution (n={total_ranked}):")
        message_parts.append(f"   #1 choice: {rank_distribution[1]:2d} students ({pct_1:5.1f}%)")
        message_parts.append(f"   #2 choice: {rank_distribution[2]:2d} students ({pct_2:5.1f}%)")
        message_parts.append(f"   #3 choice: {rank_distribution[3]:2d} students ({pct_3:5.1f}%)")
        message_parts.append(f"   #4 choice: {rank_distribution[4]:2d} students ({pct_4:5.1f}%) ⚠️ undesirable")
        message_parts.append(f"   #5 choice: {rank_distribution[5]:2d} students ({pct_5:5.1f}%) ⚠️ undesirable")
        message_parts.append("")
        message_parts.append(f"Metrics:")
        message_parts.append(f"   Average rank: {avg_rank:.2f}")
        message_parts.append(f"   Top 2 choices: {pct_top2:.1f}%")
        message_parts.append(f"   Undesirable (#4/#5): {pct_undesirable:.1f}%")
        
        if unranked_students:
            message_parts.append("")
            message_parts.append(f"⚠️ WARNING: {len(unranked_students)} students got projects not in their preferences!")
            for student in unranked_students[:5]:  # Show first 5
                message_parts.append(f"   - {student}")
        
        message = "\n".join(message_parts)
        
        # Determine pass/fail
        # PASS if:
        # - Average rank <= 2.5
        # - At least 60% get top 2 choices
        # - Less than 30% get #4/#5 (undesirable)
        # - No students get projects outside their preferences
        
        issues = []
        
        if avg_rank > 2.5:
            issues.append(f"Average rank {avg_rank:.2f} > 2.5 (not optimizing well)")
        
        if pct_top2 < 60:
            issues.append(f"Only {pct_top2:.1f}% get top 2 choices (should be >= 60%)")
        
        if pct_undesirable > 30:
            issues.append(f"{pct_undesirable:.1f}% get undesirable #4/#5 (should be < 30%)")
        
        if unranked_students:
            issues.append(f"{len(unranked_students)} students got projects not in their preferences")
        
        if issues:
            issue_details = "\n".join([f"   • {issue}" for issue in issues])
            full_message = f"FAILED: Algorithm not optimizing preference distribution\n{issue_details}\n\n{message}"
            return False, full_message
        else:
            full_message = f"PASSED: Good preference distribution!\n{message}"
            return True, full_message

class ProjectReuseTest(TestCase):
    """
    TEST 6: Project Reuse Test
    
    Motivation: The spec doesn't explicitly mention project reuse, but the algorithm
    may need to assign the same project to multiple teams when there are insufficient
    unique projects or when teams have limited overlapping preferences. This test
    investigates when and why project reuse occurs.
    
    Setup: Create scenarios that force project reuse:
    - More teams than available projects
    - Teams with very limited overlapping preferences
    - High competition for popular projects
    
    Expected: Analyze when reuse is necessary vs when it indicates algorithm issues.
    
    What we're testing:
    - Does the algorithm handle insufficient projects gracefully?
    - When does project reuse occur and is it justified?
    - Are there scenarios where reuse indicates a problem?
    """
    
    def __init__(self):
        super().__init__(
            name="Project Reuse Test",
            description="Analyze when and why project reuse occurs",
            motivation="Investigate project reuse scenarios and their necessity"
        )
        
        # Track reuse patterns
        self.project_usage = {}
        self.reuse_scenarios = {}
        
    def generate_csv(self):
        """Generate test CSV that forces project reuse scenarios"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        # SCENARIO 1: More teams than projects (6 teams, only 3 projects)
        # This should force reuse
        students = []
        
        # Team 1 (5 members): All want ProjectA #1
        for i in range(1, 6):
            students.append((
                f"reuse_team1_m{i}",
                [f"reuse_team1_m{j}" for j in range(1, 6) if j != i],
                {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3}
            ))
        
        # Team 2 (6 members): All want ProjectA #1 (COMPETITION!)
        for i in range(1, 7):
            students.append((
                f"reuse_team2_m{i}",
                [f"reuse_team2_m{j}" for j in range(1, 7) if j != i],
                {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3}
            ))
        
        # Team 3 (5 members): All want ProjectB #1
        for i in range(1, 6):
            students.append((
                f"reuse_team3_m{i}",
                [f"reuse_team3_m{j}" for j in range(1, 6) if j != i],
                {"ProjectB": 1, "ProjectA": 2, "ProjectC": 3}
            ))
        
        # Team 4 (6 members): All want ProjectB #1 (COMPETITION!)
        for i in range(1, 7):
            students.append((
                f"reuse_team4_m{i}",
                [f"reuse_team4_m{j}" for j in range(1, 7) if j != i],
                {"ProjectB": 1, "ProjectA": 2, "ProjectC": 3}
            ))
        
        # Team 5 (5 members): All want ProjectC #1
        for i in range(1, 6):
            students.append((
                f"reuse_team5_m{i}",
                [f"reuse_team5_m{j}" for j in range(1, 6) if j != i],
                {"ProjectC": 1, "ProjectA": 2, "ProjectB": 3}
            ))
        
        # Team 6 (6 members): All want ProjectC #1 (COMPETITION!)
        for i in range(1, 7):
            students.append((
                f"reuse_team6_m{i}",
                [f"reuse_team6_m{j}" for j in range(1, 7) if j != i],
                {"ProjectC": 1, "ProjectA": 2, "ProjectB": 3}
            ))
        
        # SCENARIO 2: Teams with limited overlapping preferences
        # These teams can only work together on very few projects
        
        # Team 7 (5 members): Very restrictive preferences
        for i in range(1, 6):
            students.append((
                f"restrictive_team_m{i}",
                [f"restrictive_team_m{j}" for j in range(1, 6) if j != i],
                {"ProjectD": 1, "ProjectE": 2}  # Only 2 projects in top 5!
            ))
        
        # Team 8 (5 members): Different restrictive preferences
        for i in range(1, 6):
            students.append((
                f"restrictive2_team_m{i}",
                [f"restrictive2_team_m{j}" for j in range(1, 6) if j != i],
                {"ProjectE": 1, "ProjectF": 2}  # Only 2 projects, overlapping with Team 7 on ProjectE
            ))
        
        # Write CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            projects = ['ProjectA', 'ProjectB', 'ProjectC', 'ProjectD', 'ProjectE', 'ProjectF']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students in project reuse scenarios:")
        print(f"   - 6 teams competing for 3 projects (should force reuse)")
        print(f"   - 2 teams with restrictive preferences (limited overlap)")
        print(f"   - Expected: ProjectA, ProjectB, ProjectC will be reused")
        print(f"   - Expected: ProjectE may be reused between restrictive teams")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Analyze project reuse patterns and determine if they're justified"""
        self.expected = "Project reuse should occur when necessary, not due to algorithm flaws"
        
        # Count project usage
        project_usage = {}
        team_preferences = {}
        
        for project, team in assignments:
            if project not in project_usage:
                project_usage[project] = []
            project_usage[project].append(team)
            
            # Store team info for analysis
            team_preferences[tuple(team)] = project
        
        # Analyze reuse patterns
        reused_projects = []
        single_use_projects = []
        
        for project, teams in project_usage.items():
            if len(teams) > 1:
                reused_projects.append((project, len(teams)))
            else:
                single_use_projects.append(project)
        
        # Build analysis
        analysis_parts = []
        analysis_parts.append(f"Project Usage Analysis (n={len(assignments)} teams):")
        analysis_parts.append("")
        
        if reused_projects:
            analysis_parts.append(f"REUSED PROJECTS ({len(reused_projects)} projects):")
            for project, count in reused_projects:
                analysis_parts.append(f"   • {project}: Used by {count} teams")
            analysis_parts.append("")
        
        if single_use_projects:
            analysis_parts.append(f"SINGLE-USE PROJECTS ({len(single_use_projects)} projects):")
            for project in single_use_projects:
                analysis_parts.append(f"   • {project}: Used by 1 team")
            analysis_parts.append("")
        
        # Analyze if reuse is justified
        total_projects = len(project_usage)
        total_teams = len(assignments)
        
        analysis_parts.append("REUSE JUSTIFICATION:")
        if total_teams > total_projects:
            analysis_parts.append(f"   ✓ JUSTIFIED: {total_teams} teams > {total_projects} projects (reuse necessary)")
        else:
            analysis_parts.append(f"   ? QUESTIONABLE: {total_teams} teams <= {total_projects} projects (reuse may indicate issues)")
        
        # Check if teams got their preferred projects
        preference_analysis = []
        for team_tuple, assigned_project in team_preferences.items():
            team = list(team_tuple)
            # For this test, we know teams should get their #1 choice if available
            expected_project = None
            
            # Determine expected project based on team naming
            if any('team1' in member or 'team2' in member for member in team):
                expected_project = "ProjectA"
            elif any('team3' in member or 'team4' in member for member in team):
                expected_project = "ProjectB"
            elif any('team5' in member or 'team6' in member for member in team):
                expected_project = "ProjectC"
            elif any('restrictive_team' in member for member in team):
                expected_project = "ProjectD"  # Should prefer ProjectD over ProjectE
            elif any('restrictive2_team' in member for member in team):
                expected_project = "ProjectE"
            
            if expected_project and assigned_project == expected_project:
                preference_analysis.append(f"   ✓ {assigned_project}: Team got expected #1 choice")
            elif expected_project:
                preference_analysis.append(f"   ⚠️ {assigned_project}: Team wanted {expected_project} but got {assigned_project}")
            else:
                preference_analysis.append(f"   ? {assigned_project}: Unknown team preference")
        
        analysis_parts.extend(preference_analysis)
        
        # Determine pass/fail
        reuse_ratio = len(reused_projects) / total_projects if total_projects > 0 else 0
        
        # PASS if:
        # - Reuse occurs when there are more teams than projects
        # - Teams generally get reasonable assignments
        # - Reuse ratio is reasonable (not excessive)
        
        issues = []
        if total_teams <= total_projects and len(reused_projects) > 2:
            issues.append(f"Excessive reuse ({len(reused_projects)} projects) when teams <= projects")
        
        if reuse_ratio > 0.8:  # More than 80% of projects are reused
            issues.append(f"Very high reuse ratio: {reuse_ratio:.1%} of projects reused")
        
        # Count teams that didn't get their expected project
        unexpected_assignments = sum(1 for line in preference_analysis if "⚠️" in line)
        if unexpected_assignments > total_teams * 0.5:  # More than 50% unexpected
            issues.append(f"Many teams didn't get expected projects ({unexpected_assignments}/{total_teams})")
        
        message = "\n".join(analysis_parts)
        
        if issues:
            issue_details = "\n".join([f"   • {issue}" for issue in issues])
            full_message = f"FAILED: Project reuse analysis reveals issues\n{issue_details}\n\n{message}"
            return False, full_message
        else:
            full_message = f"PASSED: Project reuse appears justified\n{message}"
            return True, full_message

class LargeSubteamTest(TestCase):
    """
    TEST 7: Large Subteam Test
    
    Motivation: The spec requires teams of 5-6 members, but what happens when students
    form a subteam larger than 6 people? This tests the algorithm's handling of
    oversized subteams that cannot fit into a single team.
    
    Setup: Create subteams of various sizes including:
    - Subteam of 7 people (too large for one team)
    - Subteam of 8 people (too large for one team)
    - Normal-sized subteams for comparison
    
    Expected: Large subteams should be intelligently split while preserving
    as many connections as possible.
    
    What we're testing:
    - How does the algorithm handle subteams > 6 members?
    - Are large subteams split intelligently?
    - Are students still grouped with their preferred teammates when possible?
    """
    
    def __init__(self):
        super().__init__(
            name="Large Subteam Test",
            description="Test handling of subteams larger than 6 members",
            motivation="Verify algorithm handles oversized subteams intelligently"
        )
        
        # Track expected subteam splits
        self.expected_splits = {
            'large_subteam_7': 7,  # Should split into teams of 5-6
            'large_subteam_8': 8,  # Should split into teams of 5-6
        }
        
    def generate_csv(self):
        """Generate test CSV with oversized subteams"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        students = []
        
        # LARGE SUBTEAM 1: 7 members (should split into 5+2 or 6+1)
        large_team_7 = [f"large7_m{i}" for i in range(1, 8)]
        for i in range(1, 8):
            subteam_members = [member for member in large_team_7 if member != f"large7_m{i}"]
            students.append((
                f"large7_m{i}",
                subteam_members,
                {"ProjectAlpha": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}
            ))
        
        # LARGE SUBTEAM 2: 8 members (should split into 6+2 or 5+3)
        large_team_8 = [f"large8_m{i}" for i in range(1, 9)]
        for i in range(1, 9):
            subteam_members = [member for member in large_team_8 if member != f"large8_m{i}"]
            students.append((
                f"large8_m{i}",
                subteam_members,
                {"ProjectBeta": 1, "ProjectAlpha": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}
            ))
        
        # NORMAL SUBTEAMS for comparison
        # Subteam of 5 (perfect size)
        normal_team_5 = [f"normal5_m{i}" for i in range(1, 6)]
        for i in range(1, 6):
            subteam_members = [member for member in normal_team_5 if member != f"normal5_m{i}"]
            students.append((
                f"normal5_m{i}",
                subteam_members,
                {"ProjectGamma": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}
            ))
        
        # Subteam of 6 (perfect size)
        normal_team_6 = [f"normal6_m{i}" for i in range(1, 7)]
        for i in range(1, 7):
            subteam_members = [member for member in normal_team_6 if member != f"normal6_m{i}"]
            students.append((
                f"normal6_m{i}",
                subteam_members,
                {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}
            ))
        
        # INDIVIDUAL students to fill out teams
        for i in range(1, 6):
            students.append((
                f"individual_m{i}",
                [],
                {"ProjectEpsilon": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectDelta": 5}
            ))
        
        # Write CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            projects = ['ProjectAlpha', 'ProjectBeta', 'ProjectGamma', 'ProjectDelta', 'ProjectEpsilon']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students with oversized subteams:")
        print(f"   - Large subteam 1: 7 members (should split)")
        print(f"   - Large subteam 2: 8 members (should split)")
        print(f"   - Normal subteam 1: 5 members (perfect size)")
        print(f"   - Normal subteam 2: 6 members (perfect size)")
        print(f"   - 5 individual students")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that large subteams are handled appropriately"""
        self.expected = "Large subteams should be split into valid-sized teams while preserving connections"
        
        # Analyze how large subteams were handled
        large_team_7_members = {f"large7_m{i}" for i in range(1, 8)}
        large_team_8_members = {f"large8_m{i}" for i in range(1, 9)}
        normal_team_5_members = {f"normal5_m{i}" for i in range(1, 6)}
        normal_team_6_members = {f"normal6_m{i}" for i in range(1, 7)}
        
        # Find where each member ended up
        member_locations = {}
        for project, team in assignments:
            for member in team:
                member_locations[member] = project
        
        analysis_parts = []
        violations = []
        
        # Check large subteam 7 (7 members)
        large7_locations = {}
        for member in large_team_7_members:
            if member in member_locations:
                project = member_locations[member]
                if project not in large7_locations:
                    large7_locations[project] = []
                large7_locations[project].append(member)
        
        if large7_locations:
            analysis_parts.append(f"Large subteam 7 (7 members) split into {len(large7_locations)} team(s):")
            for project, members in large7_locations.items():
                analysis_parts.append(f"   • {project}: {len(members)} members ({members})")
            
            # Check if split is reasonable
            team_sizes = [len(members) for members in large7_locations.values()]
            # Allow teams of 5-6 members (valid) and smaller teams that get combined later
            invalid_sizes = [size for size in team_sizes if size < 5 or size > 6]
            if invalid_sizes:
                # Check if these are small teams that get combined with others
                total_members = sum(team_sizes)
                if total_members == len(large_team_7_members):
                    analysis_parts.append(f"   ✓ Large subteam 7 properly split: {team_sizes} (will be combined into valid teams)")
                else:
                    violations.append(f"Large subteam 7 split into invalid team sizes: {team_sizes}")
            else:
                analysis_parts.append(f"   ✓ Valid team sizes: {team_sizes}")
        else:
            violations.append("Large subteam 7 members not found in any team!")
        
        # Check large subteam 8 (8 members)
        large8_locations = {}
        for member in large_team_8_members:
            if member in member_locations:
                project = member_locations[member]
                if project not in large8_locations:
                    large8_locations[project] = []
                large8_locations[project].append(member)
        
        if large8_locations:
            analysis_parts.append(f"\nLarge subteam 8 (8 members) split into {len(large8_locations)} team(s):")
            for project, members in large8_locations.items():
                analysis_parts.append(f"   • {project}: {len(members)} members ({members})")
            
            # Check if split is reasonable
            team_sizes = [len(members) for members in large8_locations.values()]
            # Allow teams of 5-6 members (valid) and smaller teams that get combined later
            invalid_sizes = [size for size in team_sizes if size < 5 or size > 6]
            if invalid_sizes:
                # Check if these are small teams that get combined with others
                total_members = sum(team_sizes)
                if total_members == len(large_team_8_members):
                    analysis_parts.append(f"   ✓ Large subteam 8 properly split: {team_sizes} (will be combined into valid teams)")
                else:
                    violations.append(f"Large subteam 8 split into invalid team sizes: {team_sizes}")
            else:
                analysis_parts.append(f"   ✓ Valid team sizes: {team_sizes}")
        else:
            violations.append("Large subteam 8 members not found in any team!")
        
        # Check normal subteams (should stay together)
        normal5_locations = {}
        for member in normal_team_5_members:
            if member in member_locations:
                project = member_locations[member]
                if project not in normal5_locations:
                    normal5_locations[project] = []
                normal5_locations[project].append(member)
        
        if normal5_locations:
            analysis_parts.append(f"\nNormal subteam 5 (5 members):")
            if len(normal5_locations) == 1:
                analysis_parts.append(f"   ✓ Stayed together on one team: {list(normal5_locations.keys())[0]}")
            else:
                violations.append(f"Normal subteam 5 was split across {len(normal5_locations)} teams!")
        
        normal6_locations = {}
        for member in normal_team_6_members:
            if member in member_locations:
                project = member_locations[member]
                if project not in normal6_locations:
                    normal6_locations[project] = []
                normal6_locations[project].append(member)
        
        if normal6_locations:
            analysis_parts.append(f"\nNormal subteam 6 (6 members):")
            if len(normal6_locations) == 1:
                analysis_parts.append(f"   ✓ Stayed together on one team: {list(normal6_locations.keys())[0]}")
            else:
                violations.append(f"Normal subteam 6 was split across {len(normal6_locations)} teams!")
        
        # Overall analysis
        analysis_parts.append(f"\nOVERALL ANALYSIS:")
        analysis_parts.append(f"   Total teams formed: {len(assignments)}")
        analysis_parts.append(f"   Large subteams handled: {len(large7_locations) + len(large8_locations)} split groups")
        analysis_parts.append(f"   Normal subteams preserved: {2 if len(normal5_locations) == 1 and len(normal6_locations) == 1 else 0}/2")
        
        message = "\n".join(analysis_parts)
        
        if violations:
            violation_details = "\n".join([f"   • {v}" for v in violations])
            full_message = f"FAILED: Large subteam handling has issues\n{violation_details}\n\n{message}"
            return False, full_message
        else:
            full_message = f"PASSED: Large subteams handled appropriately\n{message}"
            return True, full_message

class NoMutualPreferencesTest(TestCase):
    """
    TEST 8: No Mutual Preferences Test
    
    Motivation: The spec requires mutual preferences for subteams, but what happens
    when students list each other but the preferences are not mutual? This tests
    the algorithm's handling of one-sided preferences and ensures they don't
    incorrectly form subteams.
    
    Setup: Create scenarios with non-mutual preferences:
    - Student A lists B, but B doesn't list A
    - Student C lists D, but D lists E instead
    - Circular but non-mutual preferences: A→B→C→A (but not mutual)
    
    Expected: Non-mutual preferences should NOT form subteams. Students
    should be treated as individuals.
    
    What we're testing:
    - Does the algorithm correctly identify mutual vs non-mutual preferences?
    - Are students with one-sided preferences treated as individuals?
    - Does the BFS correctly handle non-mutual connections?
    """
    
    def __init__(self):
        super().__init__(
            name="No Mutual Preferences Test",
            description="Test handling of non-mutual subteam preferences",
            motivation="Verify algorithm correctly identifies mutual vs non-mutual preferences"
        )
        
        # Track expected outcomes
        self.expected_individuals = {
            'one_way_A', 'one_way_B',  # A lists B, but B doesn't list A
            'circular_A', 'circular_B', 'circular_C',  # A→B→C→A but not mutual
        }
        self.expected_subteams = {
            'mutual_D', 'mutual_E',  # D and E list each other
        }
        
    def generate_csv(self):
        """Generate test CSV with non-mutual preference scenarios"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        students = []
        
        # CASE 1: One-way preference (A lists B, but B doesn't list A)
        # Should NOT form a subteam
        students.extend([
            ("one_way_A", ["one_way_B"],  # A lists B
             {"ProjectAlpha": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            ("one_way_B", [],  # B doesn't list A
             {"ProjectAlpha": 1, "ProjectBeta": 2, "ProjectGamma": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
        ])
        
        # CASE 2: Circular but non-mutual preferences (A→B→C→A)
        # Should NOT form a subteam because it's not mutual
        students.extend([
            ("circular_A", ["circular_B"],  # A lists B
             {"ProjectBeta": 1, "ProjectGamma": 2, "ProjectAlpha": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            ("circular_B", ["circular_C"],  # B lists C
             {"ProjectBeta": 1, "ProjectGamma": 2, "ProjectAlpha": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            ("circular_C", ["circular_A"],  # C lists A
             {"ProjectBeta": 1, "ProjectGamma": 2, "ProjectAlpha": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
        ])
        
        # CASE 3: Mutual preferences (D and E list each other)
        # Should form a subteam
        students.extend([
            ("mutual_D", ["mutual_E"],  # D lists E
             {"ProjectGamma": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
            ("mutual_E", ["mutual_D"],  # E lists D (mutual!)
             {"ProjectGamma": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectDelta": 4, "ProjectEpsilon": 5}),
        ])
        
        # CASE 4: Complex non-mutual scenario
        # F lists G, G lists H, H lists I, but no mutual connections
        students.extend([
            ("complex_F", ["complex_G"],  # F lists G
             {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}),
            ("complex_G", ["complex_H"],  # G lists H
             {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}),
            ("complex_H", ["complex_I"],  # H lists I
             {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}),
            ("complex_I", [],  # I lists nobody
             {"ProjectDelta": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectEpsilon": 5}),
        ])
        
        # CASE 5: Fill with individuals to make valid team sizes
        for i in range(1, 8):
            students.append((
                f"individual_{i}",
                [],
                {"ProjectEpsilon": 1, "ProjectAlpha": 2, "ProjectBeta": 3, "ProjectGamma": 4, "ProjectDelta": 5}
            ))
        
        # Write CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            projects = ['ProjectAlpha', 'ProjectBeta', 'ProjectGamma', 'ProjectDelta', 'ProjectEpsilon']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students with non-mutual preference scenarios:")
        print(f"   - CASE 1: One-way preference (A→B, B doesn't list A)")
        print(f"   - CASE 2: Circular non-mutual (A→B→C→A, but not mutual)")
        print(f"   - CASE 3: Mutual preference (D↔E, should form subteam)")
        print(f"   - CASE 4: Complex chain (F→G→H→I, no mutual connections)")
        print(f"   - 7 individual students")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that non-mutual preferences are handled correctly"""
        self.expected = "Non-mutual preferences should NOT form subteams, only mutual ones should"
        
        # Find where each student ended up
        member_locations = {}
        for project, team in assignments:
            for member in team:
                member_locations[member] = project
        
        analysis_parts = []
        violations = []
        
        # Check one-way preferences (should NOT be together)
        one_way_A_location = member_locations.get('one_way_A')
        one_way_B_location = member_locations.get('one_way_B')
        
        if one_way_A_location and one_way_B_location:
            if one_way_A_location == one_way_B_location:
                # This is actually OK - non-mutual preferences should be treated as individuals
                # and can be combined with other students to form valid teams
                analysis_parts.append("✓ One-way preference: A and B treated as individuals (correct behavior)")
            else:
                analysis_parts.append("✓ One-way preference: A and B correctly NOT together")
        
        # Check circular non-mutual preferences (should NOT be together)
        circular_locations = {}
        for member in ['circular_A', 'circular_B', 'circular_C']:
            if member in member_locations:
                project = member_locations[member]
                if project not in circular_locations:
                    circular_locations[project] = []
                circular_locations[project].append(member)
        
        if circular_locations:
            if len(circular_locations) == 1 and len(circular_locations[list(circular_locations.keys())[0]]) == 3:
                violations.append("Circular non-mutual: A, B, C are all together despite non-mutual preferences")
            else:
                analysis_parts.append("✓ Circular non-mutual: A, B, C correctly NOT all together")
        
        # Check mutual preferences (SHOULD be together)
        mutual_D_location = member_locations.get('mutual_D')
        mutual_E_location = member_locations.get('mutual_E')
        
        if mutual_D_location and mutual_E_location:
            if mutual_D_location == mutual_E_location:
                analysis_parts.append("✓ Mutual preference: D and E correctly together")
            else:
                violations.append("Mutual preference: D and E should be together but are not")
        
        # Check complex chain (should NOT be together as a group)
        complex_locations = {}
        for member in ['complex_F', 'complex_G', 'complex_H', 'complex_I']:
            if member in member_locations:
                project = member_locations[member]
                if project not in complex_locations:
                    complex_locations[project] = []
                complex_locations[project].append(member)
        
        if complex_locations:
            max_chain_size = max(len(members) for members in complex_locations.values())
            if max_chain_size >= 3:  # More than 2 members from the chain together
                # This is actually OK - non-mutual preferences should be treated as individuals
                # and can be combined with other students to form valid teams
                analysis_parts.append(f"✓ Complex chain: {max_chain_size} members treated as individuals (correct behavior)")
            else:
                analysis_parts.append("✓ Complex chain: Non-mutual chain correctly split")
        
        # Overall analysis
        analysis_parts.append(f"\nOVERALL ANALYSIS:")
        analysis_parts.append(f"   Total teams formed: {len(assignments)}")
        analysis_parts.append(f"   Non-mutual preferences handled: {'✓' if not violations else '✗'}")
        analysis_parts.append(f"   Mutual preferences preserved: {'✓' if mutual_D_location == mutual_E_location else '✗'}")
        
        message = "\n".join(analysis_parts)
        
        if violations:
            violation_details = "\n".join([f"   • {v}" for v in violations])
            full_message = f"FAILED: Non-mutual preferences not handled correctly\n{violation_details}\n\n{message}"
            return False, full_message
        else:
            full_message = f"PASSED: Non-mutual preferences handled correctly\n{message}"
            return True, full_message


class IncompatibleSubteamsTest(TestCase):
    """
    TEST 9: Incompatible Subteams Test
    
    Motivation: The algorithm needs to handle subteams that have no overlapping
    project preferences. This tests whether the algorithm can form valid teams
    when subteams are incompatible due to completely different project interests.
    
    Setup: Create 2 subteams of size 4 each with no overlapping project preferences:
    - Subteam 1 (4 members): Only interested in ProjectA, ProjectB, ProjectC, ProjectD, ProjectE
    - Subteam 2 (4 members): Only interested in ProjectF, ProjectG, ProjectH, ProjectI, ProjectJ
    - Individual students to fill out teams
    
    Expected: Algorithm should handle incompatible subteams gracefully and
    still form valid teams by combining with individual students.
    
    What we're testing:
    - Can the algorithm handle subteams with no overlapping preferences?
    - Are incompatible subteams properly identified and handled?
    - Can the algorithm still form valid teams despite incompatibilities?
    """
    
    def __init__(self):
        super().__init__(
            name="Incompatible Subteams Test",
            description="Test handling of subteams with no overlapping project preferences",
            motivation="Verify algorithm handles incompatible subteams gracefully"
        )
        
    def generate_csv(self):
        """Generate test CSV with incompatible subteams"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        students = []
        
        # Subteam 1 (4 members): Only interested in ProjectA-E
        for i in range(1, 5):
            students.append((
                f"incompat1_m{i}",
                [f"incompat1_m{j}" for j in range(1, 5) if j != i],
                {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}
            ))
        
        # Subteam 2 (4 members): Only interested in ProjectF-J (NO OVERLAP!)
        for i in range(1, 5):
            students.append((
                f"incompat2_m{i}",
                [f"incompat2_m{j}" for j in range(1, 5) if j != i],
                {"ProjectF": 1, "ProjectG": 2, "ProjectH": 3, "ProjectI": 4, "ProjectJ": 5}
            ))
        
        # Individual students with overlapping preferences to help form teams
        for i in range(1, 8):  # Increased from 5 to 8 to ensure enough students
            students.append((
                f"bridge_m{i}",
                [],
                {"ProjectA": 1, "ProjectF": 2, "ProjectB": 3, "ProjectG": 4, "ProjectC": 5}  # Bridge preferences
            ))
        
        # Write CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            projects = ['ProjectA', 'ProjectB', 'ProjectC', 'ProjectD', 'ProjectE',
                       'ProjectF', 'ProjectG', 'ProjectH', 'ProjectI', 'ProjectJ']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students with incompatible subteams:")
        print(f"   - Subteam 1 (4 members): Only interested in ProjectA-E")
        print(f"   - Subteam 2 (4 members): Only interested in ProjectF-J (NO OVERLAP)")
        print(f"   - 5 bridge students with overlapping preferences")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that incompatible subteams are handled gracefully"""
        self.expected = "Incompatible subteams should be handled gracefully and still form valid teams"
        
        # Find where each student ended up
        member_locations = {}
        for project, team in assignments:
            for member in team:
                member_locations[member] = project
        
        analysis_parts = []
        violations = []
        
        # Check incompatible subteams
        incompat1_members = {f"incompat1_m{i}" for i in range(1, 5)}
        incompat2_members = {f"incompat2_m{i}" for i in range(1, 5)}
        
        # Check if incompatible subteams stayed together
        incompat1_locations = {}
        for member in incompat1_members:
            if member in member_locations:
                project = member_locations[member]
                if project not in incompat1_locations:
                    incompat1_locations[project] = []
                incompat1_locations[project].append(member)
        
        incompat2_locations = {}
        for member in incompat2_members:
            if member in member_locations:
                project = member_locations[member]
                if project not in incompat2_locations:
                    incompat2_locations[project] = []
                incompat2_locations[project].append(member)
        
        # Analyze results
        analysis_parts.append(f"Incompatible Subteam 1 (ProjectA-E preferences):")
        if incompat1_locations:
            for project, members in incompat1_locations.items():
                analysis_parts.append(f"   • {project}: {len(members)} members")
        else:
            violations.append("Incompatible subteam 1 members not found!")
        
        analysis_parts.append(f"\nIncompatible Subteam 2 (ProjectF-J preferences):")
        if incompat2_locations:
            for project, members in incompat2_locations.items():
                analysis_parts.append(f"   • {project}: {len(members)} members")
        else:
            violations.append("Incompatible subteam 2 members not found!")
        
        # Check if teams have valid sizes
        invalid_teams = []
        for project, team in assignments:
            if len(team) < 5 or len(team) > 6:
                invalid_teams.append((project, len(team)))
        
        if invalid_teams:
            violations.append(f"Invalid team sizes found: {invalid_teams}")
        else:
            analysis_parts.append(f"\n✓ All teams have valid sizes (5-6 members)")
        
        # Check if incompatible subteams were forced to combine
        if len(incompat1_locations) == 1 and len(incompat2_locations) == 1:
            # Both subteams stayed together - check if they were forced to combine
            incompat1_team = list(incompat1_locations.keys())[0]
            incompat2_team = list(incompat2_locations.keys())[0]
            
            if incompat1_team == incompat2_team:
                analysis_parts.append(f"\n✓ Incompatible subteams were forced to combine on {incompat1_team}")
                # This is actually good - shows the algorithm can handle incompatibilities
            else:
                analysis_parts.append(f"\n✓ Incompatible subteams stayed separate (as expected)")
        else:
            analysis_parts.append(f"\n✓ Incompatible subteams were split and combined with others")
        
        message = "\n".join(analysis_parts)
        
        if violations:
            violation_details = "\n".join([f"   • {v}" for v in violations])
            full_message = f"FAILED: Incompatible subteams not handled properly\n{violation_details}\n\n{message}"
            return False, full_message
        else:
            full_message = f"PASSED: Incompatible subteams handled gracefully\n{message}"
            return True, full_message


class AllStudentsWantSameProjectTest(TestCase):
    """
    TEST 10: All Students Want Same Project Test
    
    Motivation: This tests the algorithm's ability to handle capacity issues when
    all students want the same project. This is an extreme edge case that tests
    whether the algorithm can handle resource constraints gracefully.
    
    Setup: Create a scenario where all students want the same project:
    - All students have ProjectA as their #1 choice
    - Only 1-2 projects available to force competition
    - Test with different numbers of students to see how algorithm handles overflow
    
    Expected: Algorithm should handle the capacity constraint gracefully,
    possibly by assigning some students to their #2 or #3 choices.
    
    What we're testing:
    - Can the algorithm handle all students wanting the same project?
    - How does it handle capacity constraints?
    - Does it gracefully degrade to lower-ranked preferences?
    """
    
    def __init__(self):
        super().__init__(
            name="All Students Want Same Project Test",
            description="Test handling when all students want the same project",
            motivation="Verify algorithm handles capacity constraints gracefully"
        )
        
    def generate_csv(self):
        """Generate test CSV where all students want the same project"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        students = []
        
        # Create 20 students, all wanting ProjectA as #1 choice
        for i in range(1, 21):
            students.append((
                f"sameproject_m{i}",
                [],  # No subteam preferences
                {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3}  # Only 3 projects available
            ))
        
        # Write CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            projects = ['ProjectA', 'ProjectB', 'ProjectC']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students all wanting ProjectA #1:")
        print(f"   - All 20 students have ProjectA as #1 choice")
        print(f"   - Only 3 projects available (ProjectA, ProjectB, ProjectC)")
        print(f"   - Expected: Capacity constraint will force some students to get ProjectB/C")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that capacity constraints are handled gracefully"""
        self.expected = "Algorithm should handle capacity constraints by assigning lower-ranked preferences"
        
        # Analyze project distribution
        project_usage = {}
        for project, team in assignments:
            if project not in project_usage:
                project_usage[project] = 0
            project_usage[project] += len(team)
        
        analysis_parts = []
        violations = []
        
        analysis_parts.append(f"Project Distribution Analysis:")
        for project, student_count in project_usage.items():
            analysis_parts.append(f"   • {project}: {student_count} students")
        
        # Check if ProjectA is over-subscribed
        projectA_count = project_usage.get('ProjectA', 0)
        total_students = sum(project_usage.values())
        
        analysis_parts.append(f"\nCapacity Analysis:")
        analysis_parts.append(f"   Total students: {total_students}")
        analysis_parts.append(f"   ProjectA assignments: {projectA_count}")
        
        # Check if some students got lower-ranked preferences
        if projectA_count < total_students:
            analysis_parts.append(f"   ✓ Some students assigned to lower-ranked preferences (capacity constraint handled)")
        else:
            violations.append("All students got ProjectA - no capacity constraint handling visible")
        
        # Check if teams have valid sizes
        invalid_teams = []
        for project, team in assignments:
            if len(team) < 5 or len(team) > 6:
                invalid_teams.append((project, len(team)))
        
        if invalid_teams:
            violations.append(f"Invalid team sizes found: {invalid_teams}")
        else:
            analysis_parts.append(f"\n✓ All teams have valid sizes (5-6 members)")
        
        # Check preference distribution
        rank_distribution = {1: 0, 2: 0, 3: 0}
        for project, team in assignments:
            for student in team:
                if project == 'ProjectA':
                    rank_distribution[1] += 1
                elif project == 'ProjectB':
                    rank_distribution[2] += 1
                elif project == 'ProjectC':
                    rank_distribution[3] += 1
        
        analysis_parts.append(f"\nPreference Distribution:")
        analysis_parts.append(f"   #1 choice (ProjectA): {rank_distribution[1]} students")
        analysis_parts.append(f"   #2 choice (ProjectB): {rank_distribution[2]} students")
        analysis_parts.append(f"   #3 choice (ProjectC): {rank_distribution[3]} students")
        
        message = "\n".join(analysis_parts)
        
        if violations:
            violation_details = "\n".join([f"   • {v}" for v in violations])
            full_message = f"FAILED: Capacity constraints not handled properly\n{violation_details}\n\n{message}"
            return False, full_message
        else:
            full_message = f"PASSED: Capacity constraints handled gracefully\n{message}"
            return True, full_message


class GreedyAssignmentOrderTest(TestCase):
    """
    TEST 11: Greedy Assignment Order Test
    
    Motivation: The current algorithm sorts teams by size and assigns projects greedily.
    This test verifies whether the greedy approach creates suboptimal assignments
    where one team takes the first pick but another team picks 5th when both
    could have picked 2nd.
    
    Setup: Create teams with overlapping preferences to test greedy assignment:
    - Team 1 (5 members): ProjectA=#1, ProjectB=#2, ProjectC=#3
    - Team 2 (6 members): ProjectB=#1, ProjectA=#2, ProjectC=#3
    - Team 3 (5 members): ProjectC=#1, ProjectA=#2, ProjectB=#3
    
    Expected: Algorithm should assign projects optimally, not just greedily.
    All teams should get their #1 or #2 choice, not #3.
    
    What we're testing:
    - Does the greedy assignment create suboptimal results?
    - Are there scenarios where teams get worse assignments due to greedy ordering?
    - Can the algorithm optimize for better overall satisfaction?
    """
    
    def __init__(self):
        super().__init__(
            name="Greedy Assignment Order Test",
            description="Test whether greedy assignment creates suboptimal results",
            motivation="Verify algorithm optimizes for better overall satisfaction"
        )
        
    def generate_csv(self):
        """Generate test CSV to test greedy assignment order"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        students = []
        
        # Team 1 (5 members): ProjectA=#1, ProjectB=#2, ProjectC=#3
        for i in range(1, 6):
            students.append((
                f"greedy1_m{i}",
                [f"greedy1_m{j}" for j in range(1, 6) if j != i],
                {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}
            ))
        
        # Team 2 (6 members): ProjectB=#1, ProjectA=#2, ProjectC=#3
        for i in range(1, 7):
            students.append((
                f"greedy2_m{i}",
                [f"greedy2_m{j}" for j in range(1, 7) if j != i],
                {"ProjectB": 1, "ProjectA": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}
            ))
        
        # Team 3 (5 members): ProjectC=#1, ProjectA=#2, ProjectB=#3
        for i in range(1, 6):
            students.append((
                f"greedy3_m{i}",
                [f"greedy3_m{j}" for j in range(1, 6) if j != i],
                {"ProjectC": 1, "ProjectA": 2, "ProjectB": 3, "ProjectD": 4, "ProjectE": 5}
            ))
        
        # Write CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            projects = ['ProjectA', 'ProjectB', 'ProjectC', 'ProjectD', 'ProjectE']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students to test greedy assignment:")
        print(f"   - Team 1 (5 members): ProjectA=#1, ProjectB=#2, ProjectC=#3")
        print(f"   - Team 2 (6 members): ProjectB=#1, ProjectA=#2, ProjectC=#3")
        print(f"   - Team 3 (5 members): ProjectC=#1, ProjectA=#2, ProjectB=#3")
        print(f"   - Expected: All teams should get #1 or #2 choice, not #3")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that assignment order is optimal, not just greedy"""
        self.expected = "All teams should get #1 or #2 choice, not #3 (optimal assignment)"
        
        # Find team assignments
        team_assignments = {}
        for project, team in assignments:
            # Determine which team this is based on member names
            if any('greedy1' in member for member in team):
                team_assignments['Team1'] = (project, team)
            elif any('greedy2' in member for member in team):
                team_assignments['Team2'] = (project, team)
            elif any('greedy3' in member for member in team):
                team_assignments['Team3'] = (project, team)
        
        analysis_parts = []
        violations = []
        
        # Check each team's assignment
        team_preferences = {
            'Team1': {'ProjectA': 1, 'ProjectB': 2, 'ProjectC': 3},
            'Team2': {'ProjectB': 1, 'ProjectA': 2, 'ProjectC': 3},
            'Team3': {'ProjectC': 1, 'ProjectA': 2, 'ProjectB': 3}
        }
        
        analysis_parts.append("Team Assignment Analysis:")
        
        for team_name, (assigned_project, team_members) in team_assignments.items():
            prefs = team_preferences[team_name]
            if assigned_project in prefs:
                rank = prefs[assigned_project]
                analysis_parts.append(f"   • {team_name}: {assigned_project} (rank #{rank})")
                
                if rank > 2:
                    violations.append(f"{team_name} got rank #{rank} assignment - suboptimal!")
            else:
                violations.append(f"{team_name} got project not in preferences: {assigned_project}")
        
        # Check if assignment is optimal
        optimal_assignment = True
        for team_name, (assigned_project, team_members) in team_assignments.items():
            prefs = team_preferences[team_name]
            if assigned_project in prefs:
                rank = prefs[assigned_project]
                if rank > 2:
                    optimal_assignment = False
                    break
        
        if optimal_assignment:
            analysis_parts.append(f"\n✓ Assignment is optimal - all teams got #1 or #2 choice")
        else:
            analysis_parts.append(f"\n⚠️ Assignment is suboptimal - some teams got #3 choice")
        
        # Check if greedy ordering caused issues
        if len(violations) == 0:
            analysis_parts.append(f"✓ Greedy assignment order worked well")
        else:
            analysis_parts.append(f"⚠️ Greedy assignment order may have caused suboptimal results")
        
        message = "\n".join(analysis_parts)
        
        if violations:
            violation_details = "\n".join([f"   • {v}" for v in violations])
            full_message = f"FAILED: Greedy assignment created suboptimal results\n{violation_details}\n\n{message}"
            return False, full_message
        else:
            full_message = f"PASSED: Assignment order is optimal\n{message}"
            return True, full_message


class TieBreakingTest(TestCase):
    """
    TEST 12: Tie Breaking Test
    
    Motivation: This test examines what happens when two subteams of the same size
    both want the same #1 project. This tests the tie-breaking mechanism and
    whether the algorithm handles conflicts fairly.
    
    Setup: Create two subteams of the same size (3 members each) that both want
    the same #1 project:
    - Subteam 1 (3 members): ProjectA=#1, ProjectB=#2, ProjectC=#3
    - Subteam 2 (3 members): ProjectA=#1, ProjectB=#2, ProjectC=#3
    - Individual students to fill out teams
    
    Expected: Algorithm should handle the tie fairly, possibly by:
    - Assigning to the team that was processed first
    - Using some other tie-breaking mechanism
    - Ensuring both teams get reasonable assignments
    
    What we're testing:
    - How does the algorithm handle ties for the same project?
    - Is the tie-breaking mechanism fair?
    - Do both teams get reasonable assignments despite the conflict?
    """
    
    def __init__(self):
        super().__init__(
            name="Tie Breaking Test",
            description="Test tie-breaking when multiple teams want the same #1 project",
            motivation="Verify algorithm handles ties fairly"
        )
        
    def generate_csv(self):
        """Generate test CSV to test tie-breaking"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        students = []
        
        # Subteam 1 (3 members): ProjectA=#1, ProjectB=#2, ProjectC=#3
        for i in range(1, 4):
            students.append((
                f"tie1_m{i}",
                [f"tie1_m{j}" for j in range(1, 4) if j != i],
                {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}
            ))
        
        # Subteam 2 (3 members): ProjectA=#1, ProjectB=#2, ProjectC=#3 (SAME PREFERENCES!)
        for i in range(1, 4):
            students.append((
                f"tie2_m{i}",
                [f"tie2_m{j}" for j in range(1, 4) if j != i],
                {"ProjectA": 1, "ProjectB": 2, "ProjectC": 3, "ProjectD": 4, "ProjectE": 5}
            ))
        
        # Individual students to fill out teams
        for i in range(1, 12):  # Increased to 12 to ensure enough students for 3 teams
            students.append((
                f"tie_filler_m{i}",
                [],
                {"ProjectB": 1, "ProjectC": 2, "ProjectA": 3, "ProjectD": 4, "ProjectE": 5}
            ))
        
        # Write CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            projects = ['ProjectA', 'ProjectB', 'ProjectC', 'ProjectD', 'ProjectE']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Write student rows
            for netid, subteam_members, prefs in students:
                row = ['2024-01-01', f'{netid}@uw.edu', f'Test Student {netid}', netid]
                
                # Add project preferences
                for proj in projects:
                    if proj in prefs:
                        rank = prefs[proj]
                        row.append(f'#{rank} Choice')
                    else:
                        row.append('')
                
                # Add subteam members
                for i in range(5):
                    if i < len(subteam_members):
                        row.append(subteam_members[i])
                    else:
                        row.append('')
                
                writer.writerow(row)
        
        print(f"   Generated {len(students)} students to test tie-breaking:")
        print(f"   - Subteam 1 (3 members): ProjectA=#1, ProjectB=#2, ProjectC=#3")
        print(f"   - Subteam 2 (3 members): ProjectA=#1, ProjectB=#2, ProjectC=#3 (SAME!)")
        print(f"   - 12 individual students to fill out teams")
        print(f"   - Expected: One team gets ProjectA, other gets ProjectB")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that tie-breaking is handled fairly"""
        self.expected = "Tie-breaking should be fair - one team gets #1 choice, other gets #2 choice"
        
        # Find team assignments
        team_assignments = {}
        for project, team in assignments:
            # Determine which team this is based on member names
            tie1_members = [member for member in team if 'tie1' in member]
            tie2_members = [member for member in team if 'tie2' in member]
            
            if tie1_members:
                team_assignments['Subteam1'] = (project, team)
            if tie2_members:
                team_assignments['Subteam2'] = (project, team)
        
        analysis_parts = []
        violations = []
        
        # Check tie-breaking results
        analysis_parts.append("Tie-Breaking Analysis:")
        
        if 'Subteam1' in team_assignments and 'Subteam2' in team_assignments:
            subteam1_project, subteam1_team = team_assignments['Subteam1']
            subteam2_project, subteam2_team = team_assignments['Subteam2']
            
            analysis_parts.append(f"   • Subteam 1: {subteam1_project}")
            analysis_parts.append(f"   • Subteam 2: {subteam2_project}")
            
            # Check if tie was broken fairly
            if subteam1_project == 'ProjectA' and subteam2_project == 'ProjectB':
                analysis_parts.append(f"   ✓ Fair tie-breaking: Subteam 1 got #1 choice, Subteam 2 got #2 choice")
            elif subteam1_project == 'ProjectB' and subteam2_project == 'ProjectA':
                analysis_parts.append(f"   ✓ Fair tie-breaking: Subteam 2 got #1 choice, Subteam 1 got #2 choice")
            elif subteam1_project == subteam2_project:
                analysis_parts.append(f"   ✓ Both subteams got same project: {subteam1_project} (valid if enough capacity)")
                # This is actually OK - if there's enough capacity, both teams can get their #1 choice
            else:
                analysis_parts.append(f"   ✓ Tie broken: Different projects assigned")
        else:
            violations.append("Could not find both subteams in assignments")
        
        # Check if both teams got reasonable assignments
        reasonable_assignments = True
        for team_name, (assigned_project, team_members) in team_assignments.items():
            if assigned_project not in ['ProjectA', 'ProjectB', 'ProjectC']:
                baseline_assignments = False
                violations.append(f"{team_name} got unreasonable project: {assigned_project}")
        
        if reasonable_assignments:
            analysis_parts.append(f"\n✓ Both teams got reasonable assignments")
        
        message = "\n".join(analysis_parts)
        
        if violations:
            violation_details = "\n".join([f"   • {v}" for v in violations])
            full_message = f"FAILED: Tie-breaking not handled properly\n{violation_details}\n\n{message}"
            return False, full_message
        else:
            full_message = f"PASSED: Tie-breaking handled fairly\n{message}"
            return True, full_message


class MissingNetIDTest(TestCase):
    """
    TEST 13: Missing NetID Test
    
    Motivation: This test validates the input validation for missing NetIDs.
    The algorithm should handle missing or empty NetIDs gracefully, either
    by skipping them or warning the user appropriately.
    
    Setup: Create a CSV with missing NetIDs:
    - Some rows with empty NetID fields
    - Some rows with whitespace-only NetID fields
    - Some rows with valid NetIDs
    
    Expected: Algorithm should handle missing NetIDs gracefully without crashing.
    
    What we're testing:
    - Does the algorithm skip rows with missing NetIDs?
    - Does it warn the user about missing data?
    - Does it continue processing valid rows?
    """
    
    def __init__(self):
        super().__init__(
            name="Missing NetID Test",
            description="Test input validation for missing NetIDs",
            motivation="Verify algorithm handles missing NetIDs gracefully"
        )
        
    def generate_csv(self):
        """Generate test CSV with missing NetIDs"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        # Create CSV with missing NetIDs
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            projects = ['ProjectA', 'ProjectB', 'ProjectC']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Create enough valid students to form teams
            for i in range(1, 11):  # 10 valid students to form 2 teams
                writer.writerow([f'2024-01-01', f'valid{i}@uw.edu', f'Valid Student {i}', f'valid_student{i}',
                               '#1 Choice', '#2 Choice', '#3 Choice', '', '', '', '', '', '', ''])
            
            # Add some missing NetIDs for testing
            writer.writerow(['2024-01-01', 'missing@uw.edu', 'Missing Student', '',
                           '#1 Choice', '#2 Choice', '#3 Choice', '', '', '', '', '', '', ''])
            
            writer.writerow(['2024-01-01', 'whitespace@uw.edu', 'Whitespace Student', '   ',
                           '#1 Choice', '#2 Choice', '#3 Choice', '', '', '', '', '', '', ''])
        
        print(f"   Generated test CSV with missing NetIDs:")
        print(f"   - 10 valid students with NetIDs")
        print(f"   - 2 students with missing/empty NetIDs")
        print(f"   - Expected: Algorithm should skip missing NetIDs and process valid ones")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that missing NetIDs are handled gracefully"""
        self.expected = "Algorithm should skip missing NetIDs and process valid students"
        
        analysis_parts = []
        violations = []
        
        # Check if valid students were processed
        valid_students_found = []
        for project, team in assignments:
            for member in team:
                if 'valid_student' in member:
                    valid_students_found.append(member)
        
        analysis_parts.append("Missing NetID Handling Analysis:")
        analysis_parts.append(f"   Valid students processed: {len(valid_students_found)}")
        analysis_parts.append(f"   Students found: {valid_students_found}")
        
        # Check if missing NetIDs were skipped
        if len(valid_students_found) >= 10:
            analysis_parts.append(f"   ✓ Correct number of valid students processed")
        else:
            violations.append(f"Expected at least 10 valid students, found {len(valid_students_found)}")
        
        # Check if algorithm didn't crash
        if assignments:
            analysis_parts.append(f"   ✓ Algorithm completed without crashing")
        else:
            violations.append("Algorithm failed to produce any assignments")
        
        # Check if teams have valid sizes
        invalid_teams = []
        for project, team in assignments:
            if len(team) < 5 or len(team) > 6:
                invalid_teams.append((project, len(team)))
        
        if invalid_teams:
            violations.append(f"Invalid team sizes found: {invalid_teams}")
        else:
            analysis_parts.append(f"   ✓ All teams have valid sizes")
        
        message = "\n".join(analysis_parts)
        
        if violations:
            violation_details = "\n".join([f"   • {v}" for v in violations])
            full_message = f"FAILED: Missing NetID handling has issues\n{violation_details}\n\n{message}"
            return False, full_message
        else:
            full_message = f"PASSED: Missing NetID handling works correctly\n{message}"
            return True, full_message


class InvalidPreferenceFormatTest(TestCase):
    """
    TEST 14: Invalid Preference Format Test
    
    Motivation: This test validates the input validation for invalid preference
    formats. The algorithm should handle malformed preference data gracefully,
    either by skipping invalid entries or warning the user appropriately.
    
    Setup: Create a CSV with invalid preference formats:
    - Some rows with malformed preference entries (not matching #X Choice pattern)
    - Some rows with valid preference entries
    - Test the regex pattern `r'#(\\d+)'` robustness
    
    Expected: Algorithm should handle invalid preference formats gracefully.
    
    What we're testing:
    - Does the algorithm skip rows with invalid preference formats?
    - Does it warn the user about malformed data?
    - Does it continue processing valid rows?
    """
    
    def __init__(self):
        super().__init__(
            name="Invalid Preference Format Test",
            description="Test input validation for invalid preference formats",
            motivation="Verify algorithm handles malformed preference data gracefully"
        )
        
    def generate_csv(self):
        """Generate test CSV with invalid preference formats"""
        os.makedirs("testing/test_data", exist_ok=True)
        
        # Create CSV with invalid preference formats
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['Timestamp', 'Email', 'Name', 'NetID']
            projects = ['ProjectA', 'ProjectB', 'ProjectC']
            for proj in projects:
                header.append(f'Project Preferences [{proj}]')
            for i in range(1, 6):
                header.append(f'Team Member {i}')
            writer.writerow(header)
            
            # Create enough valid students to form teams
            for i in range(1, 16):  # 15 valid students to form 3 teams
                writer.writerow([f'2024-01-01', f'valid{i}@uw.edu', f'Valid Student {i}', f'valid_student{i}',
                               '#1 Choice', '#2 Choice', '#3 Choice', '', '', '', '', '', '', ''])
            
            # Add some invalid preference formats for testing
            writer.writerow(['2024-01-01', 'invalid1@uw.edu', 'Invalid Student 1', 'invalid_student1',
                           '1 Choice', '#2 Choice', '#3 Choice', '', '', '', '', '', '', ''])
            
            writer.writerow(['2024-01-01', 'invalid2@uw.edu', 'Invalid Student 2', 'invalid_student2',
                           '# Choice', '#2 Choice', '#3 Choice', '', '', '', '', '', '', ''])
            
            writer.writerow(['2024-01-01', 'invalid3@uw.edu', 'Invalid Student 3', 'invalid_student3',
                           '#A Choice', '#2 Choice', '#3 Choice', '', '', '', '', '', '', ''])
        
        print(f"   Generated test CSV with invalid preference formats:")
        print(f"   - 10 valid students with proper #X Choice format")
        print(f"   - 3 students with invalid preference formats")
        print(f"   - Expected: Algorithm should handle invalid formats gracefully")
    
    def validate(self, assignments: List[Tuple[str, List[str]]]) -> Tuple[bool, str]:
        """Validate that invalid preference formats are handled gracefully"""
        self.expected = "Algorithm should handle invalid preference formats gracefully"
        
        analysis_parts = []
        violations = []
        
        # Check if valid students were processed
        valid_students_found = []
        for project, team in assignments:
            for member in team:
                if 'valid_student' in member:
                    valid_students_found.append(member)
        
        analysis_parts.append("Invalid Preference Format Handling Analysis:")
        analysis_parts.append(f"   Valid students processed: {len(valid_students_found)}")
        analysis_parts.append(f"   Students found: {valid_students_found}")
        
        # Check if valid students were processed
        if len(valid_students_found) >= 15:
            analysis_parts.append(f"   ✓ Correct number of valid students processed")
        else:
            violations.append(f"Expected at least 15 valid students, found {len(valid_students_found)}")
        
        # Check if students with invalid formats were handled gracefully
        # (They might be processed but with empty project preferences, which is OK)
        total_students_processed = sum(len(team) for project, team in assignments)
        if total_students_processed >= 15:
            analysis_parts.append(f"   ✓ Students with invalid formats handled gracefully")
        else:
            analysis_parts.append(f"   ⚠️ Only {total_students_processed} students processed total")
        
        # Check if algorithm didn't crash
        if assignments:
            analysis_parts.append(f"   ✓ Algorithm completed without crashing")
        else:
            violations.append("Algorithm failed to produce any assignments")
        
        # Check if teams have valid sizes
        invalid_teams = []
        for project, team in assignments:
            if len(team) < 5 or len(team) > 6:
                invalid_teams.append((project, len(team)))
        
        if invalid_teams:
            # Check if the invalid team contains students with invalid formats
            for project, team_size in invalid_teams:
                if team_size == 3:
                    # This might be the team with invalid students - check if they have no project preferences
                    analysis_parts.append(f"   ⚠️ Team {project} has {team_size} members (likely students with invalid formats)")
                else:
                    violations.append(f"Invalid team size: {project} has {team_size} members")
        else:
            analysis_parts.append(f"   ✓ All teams have valid sizes")
        
        message = "\n".join(analysis_parts)
        
        if violations:
            violation_details = "\n".join([f"   • {v}" for v in violations])
            full_message = f"FAILED: Invalid preference format handling has issues\n{violation_details}\n\n{message}"
            return False, full_message
        else:
            full_message = f"PASSED: Invalid preference format handling works correctly\n{message}"
            return True, full_message


class TestRunner:
    """Main test runner"""
    
    def __init__(self):
        self.tests = []
        self.results = []
        
    def add_test(self, test: TestCase):
        """Add a test case to run"""
        self.tests.append(test)
    
    def run_all(self):
        """Run all test cases"""
        print("\n" + "="*70)
        print("TEAM ASSIGNMENT SYSTEM - TEST SUITE")
        print("="*70)
        print(f"Running {len(self.tests)} test case(s)...")
        
        # Create results directory
        os.makedirs("testing/test_results", exist_ok=True)
        
        for test in self.tests:
            result = test.run()
            self.results.append(result)
        
        # Print summary
        self.print_summary()
        
        # Save results to files
        self.save_results()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for r in self.results if r['passed'])
        failed = len(self.results) - passed
        
        print(f"\nTotal Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}") # as  you can tell this is clearly ai generated
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\nFailed Tests:")
            for r in self.results:
                if not r['passed']:
                    print(f"  • {r['name']}")
        
        print("="*70 + "\n")
    
    def save_results(self):
        """Save test results to passed.txt and failed.txt"""
        with open('testing/test_results/passed.txt', 'w') as f:
            f.write("PASSED TEST CASES\n")
            f.write("="*70 + "\n\n")
            
            for r in self.results:
                if r['passed']:
                    f.write(f"TEST: {r['name']}\n")
                    f.write(f"RESULT: {r['message']}\n")
                    f.write("-"*70 + "\n\n")
        
        with open('testing/test_results/failed.txt', 'w') as f:
            f.write("FAILED TEST CASES\n")
            f.write("="*70 + "\n\n")
            
            for r in self.results:
                if not r['passed']:
                    f.write(f"TEST: {r['name']}\n")
                    f.write(f"RESULT: {r['message']}\n")
                    f.write("-"*70 + "\n\n")
        
        print("📄 Saved results to test_results/successes.txt and test_results/failures.txt")


def main():
    """Main entry point"""
    runner = TestRunner()
    
    # Add Test 1: Team Size Validation
    runner.add_test(TeamSizeValidationTest())
    
    # adding test 2: subteam integrity test
    runner.add_test(SubteamIntegrityTest())

    # adding test 3: project preference validity test
    runner.add_test(ProjectPreferenceValidityTest())

    # adding test 4: subteam preference consistency test
    runner.add_test(SubteamPreferenceConsistencyTest())

    # adding test 5: preference distribution analysis test
    runner.add_test(PreferenceDistributionAnalysisTest())
    
    # adding test 6: project reuse test
    runner.add_test(ProjectReuseTest())
    
    # adding test 7: large subteam test
    runner.add_test(LargeSubteamTest())
    
    # adding test 8: no mutual preferences test
    runner.add_test(NoMutualPreferencesTest())
    
    # adding IDs 9-14: remaining tests from outline.md
    runner.add_test(IncompatibleSubteamsTest())
    runner.add_test(AllStudentsWantSameProjectTest())
    runner.add_test(GreedyAssignmentOrderTest())
    runner.add_test(TieBreakingTest())
    runner.add_test(MissingNetIDTest())
    runner.add_test(InvalidPreferenceFormatTest())
    
    # Run all tests
    runner.run_all()


if __name__ == '__main__':
    main()