Types of test cases to consider:
- Constraint validation tests
    -> team size validation - spec requires 5-6 members in each team.
    -> subteam integrity test - verify students who listed each other as subteam members are indeed on the same team
    -> project preference validity -> check if each team's assigned project is in ALL members' top 5 preferences.

- Consistency Tests
    -> subteam preference consistency - for each subteam, verify all members listed identical project rankings. 

- Optimization Tests
    -> preference distribution analysis - calculate how many students got their #1, 2, 3, 4, 5 choice, because the spec says ideally everyone gets #1 choice and 4/5 is undesirable. 
    -> project reuse test - is project reusing necessary? does this mean there are insufficient projects? The spec doesn't mention anything about this.

- Edge Case Tests
    -> Large subteam test - create input with a subteam of 7 people (too large fro one team), how should this be handled?
    -> No mutual preferences - student A lists student B as subteam member, but B doesn't list A. 
    -> Incompatible subteams - Create 2 subteams of size 4 each with no overlapping project pref. undersized teams?
    -> All students want same project - can handle capacity issues?

- Algorithm behavior tests
    -> greedy assignment order test - current code sorts teams by size and then assigns projects greedily. does greedy create suboptimal assignents? one team taking first pick but another picking 5th when both could pick 2nd is bad.
    -> Tie breaking test - what happens when two subteams of size 3 both want the same #1 project?

- Input Validation Tests
    -> Missing netID test - `if not netid: continue `, does it skip or should it warn the user?
    -> Invalid preference format - project preference doesn't match #X Choice pattern, currently the code regex is `r'#(\d+)`. 
    -> circular subteam preferences - A lists B, B lists C, C lists A (but not mutual), tests if BFS correctly identifies mutual connections. 




general notes:
- used Claude to understand what typical types of tests cases SWEs usually use for their code

