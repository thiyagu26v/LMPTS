# Project Overview

## Purpose

LMPTS (Learning Management & Prerequisite Tracking System) manages course catalogs, enforces prerequisite constraints, tracks learner progress, and recommends optimal learning paths.

## Problem Solved

Educational institutions struggle with:
- Manual prerequisite enforcement
- Circular dependency detection
- Learning path optimization
- Progress visibility across prerequisite chains

## Solution

A layered Python application with:
- Graph-based prerequisite modeling
- Automated enrollment validation
- Multiple path-finding strategies
- Analytics and reporting

## Key Stakeholders

| Actor | Role |
|-------|------|
| Administrator | Course/prerequisite management |
| Instructor | Student progress tracking |
| Learner | Self-service enrollment |
| Analyst | Completion reports |

## Technology Stack

- Python 3.10+
- SQLite
- Tkinter
- pytest

See [SYSTEM_ARCHITECTURE.md](architecture/SYSTEM_ARCHITECTURE.md) for technical details.
