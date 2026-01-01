## Development practices
- When creating new code follow DRY practices and do not repeat yourself
- Ensure there is no unused code left after any changes. If there is, remove it
- When implementing backend changes, use layered approach:
    - All of the database code should live in repositories
    - All business logic should stay in the services
- Apply functional core, imperative shell approach
