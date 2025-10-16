#!/usr/bin/env python3
"""
Team Assignment System
Assigns students to teams of 5-6 and matches them with projects based on preferences.
"""

import csv
import re
from collections import defaultdict
from typing import List, Dict, Set, Tuple
import sys


class TeamAssignment:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.students = {}  # netid -> {name, projects, subteam_members}
        self.projects = set()
        self.subteams = []
        self.teams = []
        
    def parse_csv(self):
        """Parse the CSV file to extract student preferences."""
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            # Column D is netID (index 3)
            netid_idx = 3
            
            # Find project columns (E-AY, indices 4 onwards until subteam columns)
            # Subteam columns are AZ-BE
            project_cols = []
            subteam_cols = []
            
            for i, col in enumerate(headers):
                if i < 4:  # Skip timestamp, email, name, netid
                    continue
                # If column header contains brackets, it's a project
                if '[' in col and ']' in col:
                    project_name = col.split('[')[1].split(']')[0]
                    project_cols.append((i, project_name))
                    self.projects.add(project_name)
                # If column header contains "Team Member", it's a subteam column
                elif 'Team Member' in col:
                    subteam_cols.append(i)
            
            # Process each student
            for row in reader:
                if len(row) <= netid_idx:
                    continue
                    
                netid = row[netid_idx].strip()
                if not netid:
                    continue
                    
                # Get project preferences
                project_prefs = {}
                for col_idx, project_name in project_cols:
                    if col_idx < len(row):
                        pref_value = row[col_idx]
                        if pref_value and pref_value.strip():
                            # Extract preference number from "#1 Choice", "#2 Choice", etc.
                            match = re.search(r'#(\d+)', pref_value)
                            if match:
                                pref_rank = int(match.group(1))
                                project_prefs[project_name] = pref_rank
                
                # Get subteam members
                subteam_members = set()
                for col_idx in subteam_cols:
                    if col_idx < len(row):
                        member_value = row[col_idx]
                        if member_value and member_value.strip():
                            # Extract netid from entries like "Name, netid"
                            member_str = member_value.strip()
                            # Try different formats
                            if ',' in member_str:
                                parts = member_str.split(',')
                                member_netid = parts[-1].strip()
                            else:
                                # Just the netid
                                member_netid = member_str
                            
                            # Clean up the netid
                            member_netid = member_netid.replace('@uw.edu', '').strip()
                            if member_netid and member_netid != netid:
                                subteam_members.add(member_netid)
                
                self.students[netid] = {
                    'netid': netid,
                    'projects': project_prefs,
                    'subteam_members': subteam_members
                }
        
        print(f"Parsed {len(self.students)} students and {len(self.projects)} projects")
    
    def form_subteams(self):
        """Form subteams based on mutual preferences."""
        visited = set()
        
        for netid in self.students:
            if netid in visited:
                continue
            
            # Find all students who mutually list each other
            subteam = self._find_connected_subteam(netid, visited)
            
            if subteam:
                # Verify project preferences are consistent
                if self._verify_project_consistency(subteam):
                    self.subteams.append(subteam)
                    visited.update(subteam)
                else:
                    # If not consistent, treat each as individual
                    print(f"Warning: Subteam {subteam} has inconsistent preferences, splitting")
                    for student in subteam:
                        self.subteams.append([student])
                        visited.add(student)
        
        print(f"Formed {len(self.subteams)} subteams")
        for i, subteam in enumerate(self.subteams):
            print(f"  Subteam {i+1}: {len(subteam)} members")
    
    def _find_connected_subteam(self, start_netid: str, visited: Set[str]) -> List[str]:
        """Find all mutually connected students forming a subteam."""
        if start_netid in visited:
            return []
        
        # Use BFS to find all connected members
        subteam = {start_netid}
        to_check = [start_netid]
        
        while to_check:
            current = to_check.pop(0)
            if current not in self.students:
                continue
                
            # Get members this student wants
            wanted_members = self.students[current]['subteam_members']
            
            for member in wanted_members:
                if member in subteam or member in visited:
                    continue
                if member not in self.students:
                    continue
                
                # Check if it's mutual
                their_members = self.students[member]['subteam_members']
                if current in their_members:
                    subteam.add(member)
                    to_check.append(member)
        
        return list(subteam)
    
    def _verify_project_consistency(self, subteam: List[str]) -> bool:
        """Verify that all members have the same project preferences."""
        if len(subteam) <= 1:
            return True
        
        # Get the first member's preferences
        first_prefs = self.students[subteam[0]]['projects']
        
        # Check that all members have the same preferences
        for netid in subteam[1:]:
            if self.students[netid]['projects'] != first_prefs:
                return False
        
        return True
    
    def form_teams(self):
        """Combine subteams into teams of 5-6 members."""
        # Sort subteams by size (larger first)
        sorted_subteams = sorted(self.subteams, key=len, reverse=True)
        
        # Subteams of size 5-6 become teams immediately
        for subteam in sorted_subteams[:]:
            if 5 <= len(subteam) <= 6:
                self.teams.append(subteam)
                sorted_subteams.remove(subteam)
        
        # Try to combine smaller subteams
        used = set()
        for i, subteam in enumerate(sorted_subteams):
            if i in used:
                continue
            
            current_team = subteam[:]
            used.add(i)
            
            # Try to add more subteams to reach 5-6
            for j, other_subteam in enumerate(sorted_subteams):
                if j in used:
                    continue
                
                new_size = len(current_team) + len(other_subteam)
                if new_size <= 6:
                    current_team.extend(other_subteam)
                    used.add(j)
                    if new_size >= 5:
                        break
            
            # Add the team even if it's not perfect size
            if current_team:
                self.teams.append(current_team)
        
        print(f"Formed {len(self.teams)} teams")
        for i, team in enumerate(self.teams):
            print(f"  Team {i+1}: {len(team)} members")
    
    def assign_projects(self):
        """Assign projects to teams based on preferences."""
        project_assignments = []
        used_projects = defaultdict(int)
        
        # Sort teams by size (larger teams with exact preferences first)
        def team_priority(team):
            size = len(team)
            # Prioritize teams of exact size (5-6)
            if 5 <= size <= 6:
                return (0, -size)
            else:
                return (1, -size)
        
        sorted_teams = sorted(self.teams, key=team_priority)
        
        for team in sorted_teams:
            # Get the first member's preferences (should be same for subteam)
            first_member = team[0]
            prefs = self.students[first_member]['projects']
            
            # Try to assign best available project
            assigned_project = None
            for pref_rank in range(1, 6):
                # Find projects with this rank
                for project, rank in prefs.items():
                    if rank == pref_rank:
                        # Check availability (limit reuse)
                        if used_projects[project] < 2:  # Allow some reuse if needed
                            assigned_project = project
                            used_projects[project] += 1
                            break
                
                if assigned_project:
                    break
            
            # If no project found, assign the first preference anyway
            if not assigned_project and prefs:
                assigned_project = min(prefs.items(), key=lambda x: x[1])[0]
                used_projects[assigned_project] += 1
            
            if assigned_project:
                project_assignments.append((assigned_project, team))
            else:
                # Assign a random project if no preferences (shouldn't happen)
                project = list(self.projects)[0]
                project_assignments.append((project, team))
                print(f"Warning: No preferences found for team {team}")
        
        return project_assignments
    
    def save_output(self, assignments: List[Tuple[str, List[str]]], output_path: str):
        """Save the assignments to a CSV file."""
        import os
        
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError:
                # If we can't create /workspace, use current directory
                output_path = 'out.csv'
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for project, team in assignments:
                team_str = str(team)
                writer.writerow([project, team_str])
        print(f"Saved output to {output_path}")
    
    def run(self, output_path: str):
        """Run the complete assignment process."""
        print("Starting team assignment process...")
        self.parse_csv()
        self.form_subteams()
        self.form_teams()
        assignments = self.assign_projects()
        self.save_output(assignments, output_path)
        
        # Print summary
        print("\n=== ASSIGNMENT SUMMARY ===")
        for project, team in assignments:
            print(f"{project}: {team}")
        
        return assignments


def main():
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = '../cse403-preferences.csv'
    
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = '/workspace/out.csv'
    
    assigner = TeamAssignment(csv_path)
    assigner.run(output_path)


if __name__ == '__main__':
    main()

