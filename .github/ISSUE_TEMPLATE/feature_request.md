---
name: 💡 Feature Request
description: Suggest an idea for the MikroTik Auto Backup Tool
title: "[Feature]: "
labels: ["enhancement", "needs-triage"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        Thank you for suggesting a new feature! Please provide as much detail as possible to help us understand your request.

  - type: textarea
    id: problem-description
    attributes:
      label: Is your feature request related to a problem? Please describe.
      description: |
        A clear and concise description of what the problem is. For example: "I'm always frustrated when..."
      placeholder: |
        I'm always frustrated when I have to manually backup each router individually.
        It would be much better if I could schedule automatic backups for all routers at once.
    validations:
      required: true

  - type: textarea
    id: solution-description
    attributes:
      label: Describe the solution you'd like
      description: |
        A clear and concise description of what you want to happen.
      placeholder: |
        I would like to be able to create backup schedules that can:
        - Run automatically at specified times
        - Apply to multiple routers at once
        - Support different backup types (full vs incremental)
        - Send email notifications when backups complete or fail
    validations:
      required: true

  - type: textarea
    id: alternatives-considered
    attributes:
      label: Describe alternatives you've considered
      description: |
        Are there any alternative solutions or features you've considered?
      placeholder: |
        I've considered using external cron jobs to trigger the API endpoints,
        but a built-in scheduler would be much more user-friendly and integrated.

  - type: textarea
    id: additional-context
    attributes:
      label: Additional Context
      description: |
        Add any other context, screenshots, or examples about the feature request here.
      placeholder: |
        This feature would be particularly useful for:
        - Enterprise environments with many routers
        - Remote management scenarios
        - Compliance requirements for regular backups

  - type: textarea
    id: implementation-suggestions
    attributes:
      label: Implementation Suggestions (Optional)
      description: |
        If you have any specific ideas about how this feature should be implemented,
        please share them here. This is completely optional but very helpful!
      placeholder: |
        The scheduling system could be implemented using:
        - APScheduler for Python-based scheduling
        - A simple cron-like syntax for defining schedules
        - A web interface for managing schedules
        - Email notifications using smtplib

  - type: checkboxes
    id: checks
    attributes:
      label: Before Submitting
      description: Please check the following before submitting this feature request.
      options:
        - label: I have searched the existing issues for similar feature requests
          required: true
        - label: I have provided a clear description of the problem and solution
          required: true
        - label: I understand that this is a volunteer-driven project and features are implemented based on community needs and maintainer availability
          required: true
+++++++ REPLACE</diff>
<task_progress>
- [x] Enhance README with professional GitHub profile styling
- [ ] Add social media previews and metadata
- [ ] Create project logo and branding
- [ ] Add funding/sponsorship information
- [ ] Create GitHub issue templates
- [ ] Add CODE_OF_CONDUCT.md
- [ ] Create professional project structure
</task_progress>
</write_to_file>
