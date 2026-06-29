---
name: jira-ticket-writer
description: Generate Jira and Confluence ready engineering tickets from feature descriptions, issues and acceptance criteria.
---

# Purpose

Convert engineering requirements into structured Jira stories.

# When To Use

Use this skill when:
- User describes a feature
- User describes a bug
- User provides acceptance criteria
- User asks for Jira content
- User asks for Confluence-ready documentation

# Output Format

Always generate markdown.

Use the following structure:

# Story

## Summary

One paragraph summary.

## Problem Statement

Describe the issue being solved.

## Business Value

Explain why the work matters.

## Scope

List included work items.

## Acceptance Criteria

Convert criteria into Given/When/Then format.

## Technical Notes

Implementation considerations.

## Risks

Optional.

## Out Of Scope

Optional.

## Definition of Done

Checklist.

# Rules

- Write professionally.
- Expand vague requirements into clear language.
- Convert acceptance criteria into testable statements.
- Use bullet points where appropriate.
- Do not invent business requirements.
- Ask follow-up questions if information is missing.
