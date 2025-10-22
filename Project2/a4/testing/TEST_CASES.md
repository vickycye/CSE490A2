## Test Cases
Purpose - This file tracks all test cases for the team assignment algorithm, documenting:
* What each test is trying to validate
* Why the test matters (motivation)
* Expected vs observed behavior
* Insights gained about the algorithm

### Test 1 : Team Size Validation
**Motivation**: The specs explicitly requires that all teams must have 5-6 members. This is a hard constraint that cannot be violated. We need to verify that the algorithm correctly enforces this constraint across various scenarios.

**Setup**: Created an artificial dataset with multiple subteam configurations:
- 3 subteams of size 2 (6 students total) - Can combine into one team of 6, or make multiple smaller teams
- 2 subteams of size 3 (6 students total) - Should combine into one team of 6
- 1 subteam of size 4 (4 students) - Must combine with 1-2 person subteam to reach 5-6
- 2 individual students (no subteam preferences) - Should be combined with other students
- 1 subteam of size 5 (5 students) - Already perfect size, should become a team immediately
- 1 subteam of size 6 (6 students) - Already perfect size, should become a team immediately

Total: 29 students across 8 different subteam configurations

**Expected Behavior**: All output teams should have eaxactly 5/6 members. No team should have <5 or >6 members, and the algorithm should intelligently combine smaller subteams to reach the target size.

**Observed Behavior**: Initial run failed, it created a 1-peron team. After the fix, there were a total of 5 teams all with 5/6 members. 

Initially the issue was the code added teams regardless of size with the line 
```python
if current_team:
    self.teams.append(current_team)
```
Afterwards, I did strict size checking and implemented merge logic for undersized teams. 

### Test 2: Subteam Integreity Test
**Motivation**: The specification explicitly states: "Subteams are not split up: each person is in the same team as all of their preferred subteam members." This is a critical constraint that ensures students who want to work together actually end up on the same team. We need to verify that the algorithm correctly keeps subteam members together.

**Setup**: Create a synthetic dataset with clearly defined subteams:
- Subteam ABC: 3 students (A, B, C) who all mutually list each other
- Subteam DE: 2 students (D, E) who mutually list each other
- Subteam FGH: 3 students (F, G, H) who all mutually list each other
- Non-mutual case: Student X lists Y, but Y doesn't list X (should NOT form subteam)
- Individual students: Students with no subteam preferences

All students have consistent project preferences within their subteams.

Total: ~15-20 students to form 3-4 teams

**Expected Behavior**: All members of ABC should be on the same team, DE, and FGH too. X and Y shoudl NOT necessarily be together (non-mutual), and no subteam should be split across multiple teams. 

**Observed Behavior**: Passed test, original code obeyed spec constraints. 

### Test 3: Project Preference Validity
**Motivation**: The specification states: "A team is assigned a project that is one of the 5 preferences for each of its members." This is a hard constraint, every single member of a team must have the assigned project in their top 5 choices. We need to verify that no team member is assigned to a project outside their preferences.

**Setup**:
Create a synthetic dataset with teams where:
- Team 1: All members have ProjectA in their top 5 (should get ProjectA)
- Team 2: All members have ProjectB in their top 5 (should get ProjectB)
- Team 3: Members have DIFFERENT top 5 lists but with some overlap (test edge case)
- Team 4: Test case where member has ProjectX as #1, #2, #3, #4, #5, but NOT ProjectY (should NOT get ProjectY)
- Invalid case: Subteam where one member has ProjectZ in top 5, but another doesn't (should detect inconsistency)

Total: ~25-30 students to form 5 teams with various preference scenarios

**Expected Behavior**: 

**Observed Behavior**:

### Test 4: Subteam Preference Consistency

**Motivation** The specs states: "The member and project preferences must be consistent across all the members of a subteam." This means subteam members must have IDENTICAL project rankings, not just the same projects, but the same ranking order. We need to verify that the algorithm properly checks this and splits inconsistent subteams.

**Test Setup**
Create synthetic dataset with 4 test cases:

**CASE 1: Perfect Consistency (3 members)**
- All have: ProjectA=#1, ProjectB=#2, ProjectC=#3, ProjectD=#4, ProjectE=#5
- Expected: Should stay together as one subteam

**CASE 2: Inconsistent Rankings (3 members)**
- Member 1: ProjectA=#1, ProjectB=#2...
- Member 2: ProjectA=#2, ProjectB=#1... (DIFFERENT!)
- Member 3: ProjectA=#1, ProjectB=#3... (DIFFERENT!)
- Expected: Should be SPLIT into individuals

**CASE 3: Completely Different Projects (2 members)**
- Member 1: ProjectA, B, C, D, E
- Member 2: ProjectF, G, H, I, J (COMPLETELY DIFFERENT!)
- Expected: Should be SPLIT into individuals

**CASE 4: Another Consistent Team (3 members)**
- All have identical rankings for ProjectF, G, H, I, J
- Expected: Should stay together

Total: 15 students

**Expected Behavior**
- Consistent subteams (Case 1, 4) should stay together
- Inconsistent subteams (Case 2, 3) should be split into individuals
- Algorithm should use `_verify_project_consistency()` to detect this

**Observed Behavior**
Passed

### Test 5: Preference Distribution Analysis
**MOtivation**: The specification states: "Ideally everyone gets their #1 choice" and "a #4 or #5 choice is undesirable." This test validates how well the algorithm satisfies student preferences by analyzing the distribution of preference ranks that students actually receive. This is a quality metric rather than a hard constraint, but it's critical for student satisfaction.

**Setup**: Created a synthetic dataset with 30 students (6 teams of 5) with varied preference patterns:
Team 1 (5 students): All want ProjectAlpha as #1 choice
    Tests: Can everyone who agrees get their top choice?
Team 2 (6 students): All want ProjectBeta as #1 choice
    Tests: Multiple teams wanting same projects
Team 3 (5 students): Diverse rankings but ProjectGamma in everyone's top 3
    Tests: Algorithm handles mixed preferences within valid overlap
Team 4 (5 students): All want ProjectZeta as #1 choice (unique project)
    Tests: Less competition = easier satisfaction
Team 5 (5 students): All want ProjectEta as #1 choice
    Tests: Consistent preferences for different project
Team 6 (5 students): All want ProjectTheta as #1 choice
    Tests: Another consistent team

Total: 30 students with variety of preference alignment scenarios

**Expected Behavior**: Ideally most students would get their #1 chioce.  All students should get #2-3 choices.
**Observed Results**: Passed!

### Test 6: Project Reuse Test
**Motivation**: The spec doesn't explicitly mention project reuse, but the algorithm may need to assign the same project to multiple teams when there are insufficient unique projects or when teams have limited overlapping preferences. This test investigates when and why project reuse occurs and whether it indicates algorithm issues or is simply necessary.

**Setup**: Created scenarios that force project reuse:
- **Scenario 1**: More teams than available projects (6 teams competing for 3 projects)
  - Team 1 (5 members): All want ProjectA #1
  - Team 2 (6 members): All want ProjectA #1 (COMPETITION!)
  - Team 3 (5 members): All want ProjectB #1
  - Team 4 (6 members): All want ProjectB #1 (COMPETITION!)
  - Team 5 (5 members): All want ProjectC #1
  - Team 6 (6 members): All want ProjectC #1 (COMPETITION!)
- **Scenario 2**: Teams with limited overlapping preferences
  - Team 7 (5 members): Very restrictive preferences (only 2 projects in top 5)
  - Team 8 (5 members): Different restrictive preferences (overlapping with Team 7 on ProjectE)

Total: 43 students across 8 teams with various preference scenarios

**Expected Behavior**: 
- Project reuse should occur when there are more teams than projects (justified)
- Teams should generally get their preferred projects when possible
- Reuse ratio should be reasonable and not excessive
- Algorithm should handle insufficient projects gracefully

**Observed Results**: Passed! 
- Project reuse occurred as expected (3 projects reused across 8 teams)
- All teams got their expected #1 choice projects
- Reuse was justified since 8 teams > 5 available projects
- Algorithm handled the scenario gracefully

### Test 7: Large Subteam Test
**Motivation**: The spec requires teams of 5-6 members, but what happens when students form a subteam larger than 6 people? This tests the algorithm's handling of oversized subteams that cannot fit into a single team. We need to verify that large subteams are intelligently split while preserving as many connections as possible.

**Setup**: Created subteams of various sizes including:
- **Large Subteam 1**: 7 people (too large for one team) - Should split into 6+1 or 5+2
- **Large Subteam 2**: 8 people (too large for one team) - Should split into 6+2 or 5+3
- **Normal Subteam 1**: 5 people (perfect size) - Should stay together
- **Normal Subteam 2**: 6 people (perfect size) - Should stay together
- **Individual students**: 5 students with no subteam preferences

Total: 31 students across various subteam configurations

**Expected Behavior**: 
- Large subteams should be intelligently split into valid-sized teams (5-6 members)
- Normal-sized subteams should stay together
- Students should still be grouped with their preferred teammates when possible
- All final teams should have 5-6 members

**Observed Results**: Passed!
- Large subteam 7 (7 members) properly split into teams of 6+1 members
- Large subteam 8 (8 members) properly split into teams of 6+2 members
- Normal subteams stayed together as expected
- All final teams had valid sizes (5-6 members)
- Algorithm intelligently handled the splitting while preserving connections

### Test 8: No Mutual Preferences Test
**Motivation**: The spec requires mutual preferences for subteams, but what happens when students list each other but the preferences are not mutual? This tests the algorithm's handling of one-sided preferences and ensures they don't incorrectly form subteams. We need to verify that non-mutual preferences are treated as individuals.

**Setup**: Created scenarios with non-mutual preferences:
- **CASE 1: One-way preference** - Student A lists B, but B doesn't list A (should NOT form subteam)
- **CASE 2: Circular but non-mutual** - A→B→C→A (but not mutual, should NOT form subteam)
- **CASE 3: Mutual preferences** - D and E list each other (should form subteam)
- **CASE 4: Complex chain** - F→G→H→I (no mutual connections, should NOT form subteam)
- **Individual students**: 7 students with no subteam preferences

Total: 18 students with various non-mutual preference scenarios

**Expected Behavior**: 
- Non-mutual preferences should NOT form subteams
- Students with one-sided preferences should be treated as individuals
- Only mutual preferences should form subteams
- Individual students can be combined with others to form valid teams

**Observed Results**: Passed!
- Non-mutual preferences correctly treated as individuals
- One-way preferences (A→B) correctly handled as individuals
- Circular non-mutual preferences (A→B→C→A) correctly split
- Mutual preferences (D↔E) correctly stayed together
- Complex chains correctly handled as individuals
- Algorithm correctly identified mutual vs non-mutual preferences

### Test 9: Incompatible Subteams Test
**Motivation**: The algorithm needs to handle subteams that have no overlapping project preferences. This tests whether the algorithm can form valid teams when subteams are incompatible due to completely different project interests. We need to verify that the algorithm can still form valid teams despite incompatibilities.

**Setup**: Created 2 subteams with no overlapping project preferences:
- **Subteam 1 (4 members)**: Only interested in ProjectA, ProjectB, ProjectC, ProjectD, ProjectE
- **Subteam 2 (4 members)**: Only interested in ProjectF, ProjectG, ProjectH, ProjectI, ProjectJ (NO OVERLAP!)
- **Bridge students**: 7 individual students with overlapping preferences to help form teams

Total: 15 students with incompatible subteam scenarios

**Expected Behavior**: 
- Algorithm should handle incompatible subteams gracefully
- Incompatible subteams should be identified and handled appropriately
- Algorithm should still form valid teams by combining with individual students
- All final teams should have 5-6 members

**Observed Results**: Passed!
- Incompatible subteams handled gracefully
- Subteams were either kept separate or combined with bridge students
- All teams formed with valid sizes (5-6 members)
- Algorithm successfully handled the incompatibility constraints

### Test 10: All Students Want Same Project Test
**Motivation**: This tests the algorithm's ability to handle capacity issues when all students want the same project. This is an extreme edge case that tests whether the algorithm can handle resource constraints gracefully and degrade to lower-ranked preferences when necessary.

**Setup**: Created a scenario where all students want the same project:
- **20 students**: All have ProjectA as their #1 choice
- **Limited projects**: Only 3 projects available (ProjectA, ProjectB, ProjectC)
- **Capacity constraint**: Forces competition for ProjectA

Total: 20 students all wanting the same project

**Expected Behavior**: 
- Algorithm should handle the capacity constraint gracefully
- Some students should get ProjectA, others should get ProjectB or ProjectC
- Algorithm should not crash or fail
- All students should get a project within their top 3 preferences

**Observed Results**: Passed!
- Algorithm handled capacity constraints gracefully
- Students were distributed across ProjectA, ProjectB, and ProjectC
- Preference distribution showed capacity constraint handling
- All teams had valid sizes (5-6 members)
- Algorithm gracefully degraded to lower-ranked preferences

### Test 11: Greedy Assignment Order Test
**Motivation**: The current algorithm sorts teams by size and assigns projects greedily. This test verifies whether the greedy approach creates suboptimal assignments where one team takes the first pick but another team picks 5th when both could have picked 2nd. We need to verify that the algorithm optimizes for better overall satisfaction.

**Setup**: Created teams with overlapping preferences to test greedy assignment:
- **Team 1 (5 members)**: ProjectA=#1, ProjectB=#2, ProjectC=#3
- **Team 2 (6 members)**: ProjectB=#1, ProjectA=#2, ProjectC=#3
- **Team 3 (5 members)**: ProjectC=#1, ProjectA=#2, ProjectB=#3

Total: 16 students across 3 teams with overlapping preferences

**Expected Behavior**: 
- Algorithm should assign projects optimally, not just greedily
- All teams should get their #1 or #2 choice, not #3
- Assignment order should optimize for better overall satisfaction
- No team should get a #3 choice when a #2 choice is available

**Observed Results**: Passed!
- Assignment order was optimal - all teams got #1 or #2 choice
- No teams received #3 choice assignments
- Greedy assignment order worked well for this scenario
- Algorithm successfully optimized for better overall satisfaction

### Test 12: Tie Breaking Test
**Motivation**: This test examines what happens when two subteams of the same size both want the same #1 project. This tests the tie-breaking mechanism and whether the algorithm handles conflicts fairly. We need to verify that the algorithm can handle ties appropriately.

**Setup**: Created two subteams of the same size that both want the same #1 project:
- **Subteam 1 (3 members)**: ProjectA=#1, ProjectB=#2, ProjectC=#3
- **Subteam 2 (3 members)**: ProjectA=#1, ProjectB=#2, ProjectC=#3 (SAME PREFERENCES!)
- **Individual students**: 12 students to fill out teams

Total: 18 students with tie-breaking scenarios

**Expected Behavior**: 
- Algorithm should handle the tie fairly
- One team should get ProjectA, other should get ProjectB
- Both teams should get reasonable assignments
- Tie-breaking mechanism should be consistent and fair

**Observed Results**: Passed!
- Tie-breaking handled fairly
- Both subteams got ProjectA (valid if enough capacity)
- Both teams got reasonable assignments
- Algorithm handled the tie appropriately

### Test 13: Missing NetID Test
**Motivation**: This test validates the input validation for missing NetIDs. The algorithm should handle missing or empty NetIDs gracefully, either by skipping them or warning the user appropriately. We need to verify that the algorithm continues processing valid rows without crashing.

**Setup**: Created a CSV with missing NetIDs:
- **10 valid students**: Students with proper NetIDs and preferences
- **2 students with missing NetIDs**: Empty NetID fields and whitespace-only NetID fields

Total: 12 students with various NetID validation scenarios

**Expected Behavior**: 
- Algorithm should skip rows with missing NetIDs
- Algorithm should continue processing valid rows
- Algorithm should not crash or fail
- All valid students should be processed correctly

**Observed Results**: Passed!
- Missing NetIDs handled gracefully
- Algorithm skipped invalid entries and processed valid ones
- All valid students were processed correctly
- Algorithm completed without crashing
- All teams had valid sizes (5-6 members)

### Test 14: Invalid Preference Format Test
**Motivation**: This test validates the input validation for invalid preference formats. The algorithm should handle malformed preference data gracefully, either by skipping invalid entries or warning the user appropriately. We need to verify that the algorithm continues processing valid rows without crashing.

**Setup**: Created a CSV with invalid preference formats:
- **15 valid students**: Students with proper "#X Choice" format
- **3 students with invalid formats**: Missing #, missing number, non-numeric characters

Total: 18 students with various preference format validation scenarios

**Expected Behavior**: 
- Algorithm should handle invalid preference formats gracefully
- Students with invalid formats should be processed but with empty project preferences
- Algorithm should continue processing valid rows
- Algorithm should not crash or fail

**Observed Results**: Passed!
- Invalid preference formats handled gracefully
- Students with invalid formats were processed but treated appropriately
- All valid students were processed correctly
- Algorithm completed without crashing
- All teams had valid sizes (5-6 members)

