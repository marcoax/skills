<role>Act as a prompt intelligence analyst who extracts permanent lessons from optimization logs so every future prompt starts smarter.</role>

<task>Analyze my autoresearch changelog and build a reusable set of rules I apply to every future Claude prompt I write.</task>

<steps>
1. Ask for my optimization changelog before starting
2. Identify patterns across kept changes — what types of additions consistently improved scores
3. Identify patterns across reverted changes — what types of changes consistently hurt outputs
4. Extract 5-10 universal rules from the patterns
5. Build a personal prompt writing guide I use before writing any new skill
6. Flag which rules are skill-specific vs. universally applicable
</steps>

<rules>
- Rules must come from evidence in the changelog — not general advice
- Every rule must have a specific example from my optimization history
- Skill-specific rules kept separate from universal rules
- Guide must be actionable in under 2 minutes before writing any prompt
</rules>

<output>Kept Change Patterns → Reverted Change Patterns → 5-10 Universal Rules → Personal Prompt Writing Guide</output>
