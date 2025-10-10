---
name: 🐛 Bug Report
description: Create a report to help us improve the MikroTik Auto Backup Tool
title: "[Bug]: "
labels: ["bug", "needs-triage"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report! Please provide as much detail as possible.

  - type: textarea
    id: description
    attributes:
      label: Describe the Bug
      description: A clear and concise description of what the bug is.
      placeholder: |
        When I try to [describe what you were doing], [what happens] instead of [what you expected].

        Steps to reproduce:
        1. Go to '...'
        2. Click on '....'
        3. Scroll down to '....'
        4. See error
    validations:
      required: true

  - type: textarea
    id: expected-behavior
    attributes:
      label: Expected Behavior
      description: What did you expect to happen?
      placeholder: I expected [describe expected behavior] to happen.
    validations:
      required: true

  - type: textarea
    id: actual-behavior
    attributes:
      label: Actual Behavior
      description: What actually happened?
      placeholder: Instead, [describe what actually happened].
    validations:
      required: true

  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: |
        Please provide details about your environment:
        - OS: [e.g. Windows 10, Ubuntu 20.04, macOS 12.1]
        - Python version: [e.g. 3.9.7]
        - Browser: [e.g. Chrome 96, Firefox 95]
        - MikroTik RouterOS version: [e.g. 7.6]
      placeholder: |
        - OS: Windows 11
        - Python: 3.10.0
        - Browser: Chrome 96.0.4664.110
        - RouterOS: 7.6
    validations:
      required: true

  - type: textarea
    id: reproduction-steps
    attributes:
      label: Steps to Reproduce
      description: Provide detailed steps to reproduce the issue.
      placeholder: |
        1. Start the application with `python backend/app.py`
        2. Open browser to `http://localhost:5000`
        3. Click on 'Add Router'
        4. Fill in router details
        5. Click 'Test Connection'
        6. See the error message
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Relevant Log Output
      description: |
        Please copy and paste any relevant log output. This will be automatically formatted into code, so no need for backticks.
      render: shell

  - type: textarea
    id: additional-context
    attributes:
      label: Additional Context
      description: Add any other context about the problem here.
      placeholder: |
        - This happens only on specific router models
        - The issue started after updating RouterOS
        - Similar issues occur with other routers

  - type: checkboxes
    id: checks
    attributes:
      label: Before Submitting
      description: Please check the following before submitting this bug report.
      options:
        - label: I have searched the existing issues for similar problems
          required: true
        - label: I have provided detailed steps to reproduce the issue
          required: true
        - label: I have included my environment details
          required: true
        - label: I have checked that this issue hasn't been fixed in the latest version
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
