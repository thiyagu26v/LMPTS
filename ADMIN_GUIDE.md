# Admin Guide

Administrators manage the course catalog, prerequisites, and system configuration.

## Responsibilities

- Create and publish courses
- Define prerequisite relationships
- Monitor system analytics
- Archive obsolete courses

## Course Lifecycle

```
Draft → Published → Archived
```

- **Draft:** Not visible to learners
- **Published:** Available for enrollment
- **Archived:** Cannot enroll; data preserved

## Prerequisite Rules

1. Both courses must exist before adding a prerequisite
2. Self-prerequisites are blocked
3. Circular chains (A→B→C→A) are prevented
4. Deleting a course cascades to its prerequisites and enrollments

## Best Practices

- Publish courses only when content is ready
- Keep prerequisite chains shallow when possible
- Review bottleneck courses in Analytics tab
- Use meaningful course codes (e.g., CS101, MATH201)

## Monitoring

Check Analytics Dashboard for:
- Total courses and learners
- System completion rate
- Courses with low completion despite high prerequisites
