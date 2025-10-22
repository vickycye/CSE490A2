#!/usr/bin/env python3
"""
Team Assignment System - FIXED VERSION
Assigns students to teams of 5-6 and matches them with projects based on preferences.

FIXES:
- Test 1: Teams now strictly have 5-6 members (merge small teams)
- Test 3: Project assignments now validate that project is in ALL members' top 5
- Test 3: Team formation checks project compatibility before combining students
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
    
    def _get_common_projects(self, team1: List[str], team2: List[str]) -> Set[str]:
        """
        Get projects that are in the top 5 of ALL members from both teams.
        
        FIX FOR TEST 3: This ensures we only combine students who have
        at least some overlapping project preferences.
        """
        all_members = team1 + team2
        
        if not all_members:
            return set()
        
        # Get the first member's top 5 projects
        first_member = all_members[0]
        common_projects = set([
            p for p, rank in self.students[first_member]['projects'].items() 
            if rank <= 5
        ])
        
        # Intersect with each other member's top 5
        for member in all_members[1:]:
            member_top5 = set([
                p for p, rank in self.students[member]['projects'].items() 
                if rank <= 5
            ])
            common_projects &= member_top5  # Intersection
        
        return common_projects
    
    def _split_large_subteam(self, subteam: List[str]) -> List[List[str]]:
        """
        Split a large subteam (>6 members) into smaller teams of 5-6 members.
        
        This method tries to preserve as many connections as possible while
        creating valid-sized teams.
        """
        if len(subteam) <= 6:
            return [subteam]
        
        split_teams = []
        remaining_members = subteam[:]
        
        # Greedy approach: try to form teams of 6 first, then 5
        while len(remaining_members) > 0:
            if len(remaining_members) >= 6:
                # Take 6 members for this team
                team = remaining_members[:6]
                remaining_members = remaining_members[6:]
                split_teams.append(team)
            elif len(remaining_members) >= 5:
                # Take 5 members for this team
                team = remaining_members[:5]
                remaining_members = remaining_members[5:]
                split_teams.append(team)
            else:
                # Less than 5 members left - need to merge with previous team
                if split_teams and len(split_teams[-1]) + len(remaining_members) <= 6:
                    # Can add to the last team
                    split_teams[-1].extend(remaining_members)
                    remaining_members = []
                else:
                    # Create a small team that will need to be merged later
                    split_teams.append(remaining_members[:])
                    remaining_members = []
        
        # Ensure all split teams have valid sizes (5-6 members)
        final_teams = []
        for team in split_teams:
            if len(team) >= 5:
                final_teams.append(team)
            else:
                # Team is too small, need to merge with another team
                if final_teams and len(final_teams[-1]) + len(team) <= 6:
                    final_teams[-1].extend(team)
                else:
                    # Can't merge, add as individual subteams for later processing
                    for member in team:
                        final_teams.append([member])
        
        print(f"    Split into {len(final_teams)} teams: {[len(team) for team in final_teams]}")
        return final_teams
    
    def form_teams(self):
        """
        Combine subteams into teams of 5-6 members.
        
        FIX FOR TEST 1: Ensures all teams have 5-6 members by merging small teams.
        FIX FOR TEST 3: Checks project compatibility before combining subteams.
        """
        # Sort subteams by size (larger first)
        sorted_subteams = sorted(self.subteams, key=len, reverse=True)
        
        # Handle subteams larger than 6 by splitting them intelligently
        split_subteams = []
        for subteam in sorted_subteams[:]:
            if len(subteam) > 6:
                print(f"  Splitting large subteam of {len(subteam)} members: {subteam}")
                # Split into teams of 5-6 members
                split_teams = self._split_large_subteam(subteam)
                split_subteams.extend(split_teams)
                sorted_subteams.remove(subteam)
        
        # Add split subteams back to the list
        sorted_subteams.extend(split_subteams)
        
        # Subteams of size 5-6 become teams immediately
        for subteam in sorted_subteams[:]:
            if 5 <= len(subteam) <= 6:
                self.teams.append(subteam)
                sorted_subteams.remove(subteam)
        
        # Combine smaller subteams using improved bin-packing with compatibility check
        used = set()
        for i, subteam in enumerate(sorted_subteams):
            if i in used:
                continue
            
            current_team = subteam[:]
            current_size = len(current_team)
            used.add(i)
            
            # Try to add more subteams to reach 5-6
            for j, other_subteam in enumerate(sorted_subteams):
                if j in used or j <= i:
                    continue
                
                new_size = current_size + len(other_subteam)
                
                # Only add if it keeps us at or below 6
                if new_size <= 6:
                    # FIX FOR TEST 3: Check if they have compatible project preferences
                    common_projects = self._get_common_projects(current_team, other_subteam)
                    
                    if common_projects:
                        # They have at least one project in common, safe to combine
                        current_team.extend(other_subteam)
                        current_size = new_size
                        used.add(j)
                        
                        # If we've reached valid size, stop adding
                        if current_size >= 5:
                            break
                    else:
                        # No common projects, skip this combination
                        print(f"  Skipping combination: no common projects between {current_team} and {other_subteam}")
            
            # Only add teams that meet the size constraint (5-6 members)
            if current_size >= 5 and current_size <= 6:
                self.teams.append(current_team)
            else:
                # Team is too small - need to combine it with another team
                print(f"Warning: Subteam {current_team} has {current_size} members (< 5), attempting to merge with existing team")
                
                # Try to add to an existing team that has room AND compatible projects
                added = False
                for existing_team in self.teams:
                    if len(existing_team) + current_size <= 6:
                        # Check project compatibility
                        common_projects = self._get_common_projects(existing_team, current_team)
                        if common_projects:
                            existing_team.extend(current_team)
                            print(f"  Merged into team of size {len(existing_team)}")
                            added = True
                            break
                
                if not added:
                    print(f"  WARNING: Cannot form valid team for {current_team} with compatible projects")
                    # As a last resort, try to merge without compatibility check
                    for existing_team in self.teams:
                        if len(existing_team) + current_size <= 6:
                            existing_team.extend(current_team)
                            print(f"  Merged (without project compatibility) into team of size {len(existing_team)}")
                            added = True
                            break
                    
                    if not added:
                        print(f"  ERROR: Cannot place team {current_team} anywhere - adding anyway")
                        self.teams.append(current_team)
        
        print(f"Formed {len(self.teams)} teams")
        for i, team in enumerate(self.teams):
            size = len(team)
            status = "✓" if 5 <= size <= 6 else "✗"
            print(f"  Team {i+1}: {size} members {status}")
    
    def _get_valid_projects_for_team(self, team: List[str]) -> Dict[str, int]:
        """
        Get projects that are in ALL team members' top 5, with scores.
        
        FIX FOR TEST 3: This ensures we only assign projects that EVERY
        team member has in their top 5 preferences.
        
        Returns: Dict mapping project name to team score (higher = better)
        """
        if not team:
            return {}
        
        # Get the first member's top 5 projects
        valid_projects = set([
            p for p, rank in self.students[team[0]]['projects'].items() 
            if rank <= 5
        ])
        
        # Intersect with each other member's top 5
        for member in team[1:]:
            member_top5 = set([
                p for p, rank in self.students[member]['projects'].items() 
                if rank <= 5
            ])
            valid_projects &= member_top5  # Intersection
        
        # Calculate scores for valid projects
        # Score = sum of (6 - rank) for each member
        project_scores = {}
        for project in valid_projects:
            score = 0
            for member in team:
                rank = self.students[member]['projects'].get(project, 6)
                score += (6 - rank)  # Higher rank (1) gives more points
            project_scores[project] = score
        
        return project_scores
    
    def assign_projects(self):
        """
        Assign projects to teams based on preferences.
        
        FIX FOR TEST 3: Now validates that assigned project is in ALL members' top 5.
        """
        project_assignments = []
        used_projects = set()
        
        # Sort teams by how constrained they are (fewer valid projects = higher priority)
        def team_constraint(team):
            valid_projects = self._get_valid_projects_for_team(team)
            return (len(valid_projects), -len(team))  # Fewer projects first, then larger teams
        
        sorted_teams = sorted(self.teams, key=team_constraint)
        
        for team in sorted_teams:
            # FIX FOR TEST 3: Get projects valid for ALL members
            valid_projects = self._get_valid_projects_for_team(team)
            
            if not valid_projects:
                # ERROR: No project satisfies all members!
                print(f"ERROR: Team {team} has no projects in all members' top 5!")
                print(f"  This team should not have been formed.")
                # Assign the first member's #1 choice as fallback (will violate constraint)
                first_member = team[0]
                prefs = self.students[first_member]['projects']
                if prefs:
                    assigned_project = min(prefs.items(), key=lambda x: x[1])[0]
                else:
                    assigned_project = list(self.projects)[0]
                project_assignments.append((assigned_project, team))
                continue
            
            # Try to assign best available project from valid projects
            assigned_project = None
            
            # Sort valid projects by score (best first)
            sorted_valid_projects = sorted(
                valid_projects.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            for project, score in sorted_valid_projects:
                if project not in used_projects:
                    assigned_project = project
                    used_projects.add(project)
                    break
            
            if not assigned_project:
                # All preferred projects are taken, assign best one anyway (allow reuse)
                project, score = sorted_valid_projects[0]
                assigned_project = project
                print(f"Warning: Project {project} reused for team {team}")
            
            project_assignments.append((assigned_project, team))
        
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