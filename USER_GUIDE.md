# User Guide

## Getting Started

Launch the application with `python main.py`.

## Admin Panel

### Create a Course
1. Fill in Code, Name, Description, Difficulty, Duration, Instructor
2. Click **Create Course**
3. Click **Publish** to make it available for enrollment

### Manage Prerequisites
1. Enter Prerequisite code and Dependent code
2. Click **Add**
3. System blocks circular dependencies with an error message

### Search Courses
Type in the Search box to filter the course catalog.

## Learner Portal

### Register
1. Enter Learner ID, Name, Email
2. Click **Register**

### Enroll in a Course
1. Select learner from dropdown
2. Enter course code
3. Click **Validate** to check prerequisites
4. Click **Enroll** if validation passes

### Complete a Course
1. Enter course code and optional score (0-100)
2. Click **Mark Complete**

### View Progress
Click **Load Progress** to see completion rate and suggested courses.

## Learning Paths

1. Enter Start course (e.g., CS101) and Target course (e.g., CS301)
2. Select strategy: shortest, difficulty, or minimum_duration
3. Click **Find Path** for a single path or **Find All Paths** for alternatives

## Analytics Dashboard

Click **Refresh Analytics** to view:
- System-wide metrics (courses, learners, completion rate)
- Per-course completion statistics
- Bottleneck courses (high prerequisites, low completion)

## Error Messages

| Message | Meaning |
|---------|---------|
| Missing prerequisites | Complete required courses first |
| Already enrolled | Duplicate enrollment prevented |
| Would create cycle | Prerequisite creates circular dependency |
| Course not published | Only published courses allow enrollment |
