# Analyst Guide

Generate reports on completion rates and learning bottlenecks.

## Analytics Dashboard

### System Metrics
- Total courses (published vs total)
- Total learners and enrollments
- System-wide completion rate
- Prerequisite graph depth and complexity

### Course Completion Statistics
Table showing per-course:
- Total enrollments
- Completed count
- Completion rate percentage
- Average score

### Bottleneck Detection

Courses flagged when they have:
- 2+ transitive prerequisites
- Completion rate below 50%

These represent learning bottlenecks where students struggle.

## Prerequisite Complexity

Metrics available via `AnalyticsService.get_prerequisite_complexity()`:
- Node count (courses)
- Edge count (prerequisite relationships)
- Maximum hierarchy depth
- Average prerequisites per course

## Exporting Data

For programmatic access, use the service layer:

```python
from lmpts.services.container import ServiceContainer

container = ServiceContainer()
report = container.analytics_service.generate_report()
print(report.system_metrics)
print(report.bottlenecks)
```

## Report Interpretation

| Metric | Good | Concerning |
|--------|------|------------|
| Completion rate | > 70% | < 50% |
| Graph depth | 3-5 levels | > 8 levels |
| Bottleneck count | 0-1 | 3+ |
