# Changelog

All notable changes and features of the OpenClawde Supervisor.

## [1.0.0] - 2024-02-20

### Initial Release

Complete OpenClaw-compatible supervisor for managing OpenCode agent workflows with human oversight.

### Features

#### Core Functionality
- **Plan Extraction** - Automatically parses and extracts executable actions from OpenCode plan agent output
- **Approval Gates** - Configurable approval mode requiring human authorization before execution
- **State Management** - Persistent state tracking across sessions in `state.json`
- **Policy Enforcement** - Automatic rejection of plans containing forbidden keywords
- **Session Continuity** - Seamless OpenCode session management across approval boundaries

#### Plan Detection & Validation
- Parses JSON actions from markdown code blocks in agent responses
- Detects multiple action blocks in single response
- Validates executable plan exists before requesting approval
- Rejects empty or non-actionable plans with clear error messages
- Extracts session IDs from event streams

#### Approval Workflow
- Human-readable plan formatting showing all actions and arguments
- Clear approval signals: `🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED`
- Session ID emission for external system integration
- Status checking at any time during execution
- Approve/reject commands to control execution flow

#### CLI Interface
- `python supervisor.py <task>` - Start new task
- `python supervisor.py status` - Check current status and planned actions
- `python supervisor.py approve` - Approve plan and continue to build phase
- `python supervisor.py reject` - Reject plan and abort execution

#### OpenClaw Skill Integration
- Full OpenClaw skill compatibility
- `/dev run <task>` - Start task via OpenClaw
- `/dev status` - Check status via OpenClaw
- `/dev approve` - Approve via OpenClaw
- `/dev reject` - Reject via OpenClaw
- Automatic installation via `install.sh`
- Environment variable setup (`OPENCLAW_SUPERVISOR_HOME`)

#### Configuration
- JSON-based configuration (`config.json`)
- Configurable approval modes (approve_after_plan, auto)
- Customizable project path
- Adjustable action loop limits
- User-defined forbidden keyword list

#### Error Handling
- Comprehensive error messages with stdout and stderr
- Build failure detection and logging
- Missing session ID validation
- State persistence on errors
- Clear status values for all states

#### State Tracking
States include:
- `planning` - Initial planning phase
- `no_plan` - No executable plan generated
- `plan_rejected` - Policy or user rejection
- `awaiting_approval` - Waiting for approval
- `exploring` - Executing exploration actions
- `building` - Build phase in progress
- `build_failed` - Build encountered error
- `done` - Completed successfully
- `rejected` - User rejected plan

#### Safety Features
- Forbidden keyword detection
- Plan validation before execution
- Approval gates in sensitive mode
- All changes logged to state file
- Session tracking for auditability

#### Integration Support
- Signal emission for external monitoring
- State file for programmatic access
- Event stream parsing (NDJSON)
- OpenClaw skill interface
- Standalone CLI mode

### Documentation
- **README.md** - Complete feature documentation and configuration guide
- **QUICKSTART.md** - 5-minute getting started guide
- **WORKFLOW_EXAMPLE.md** - Detailed workflow examples and integration guides
- **CHANGELOG.md** - This file

### Installation
- Automated installation script (`install.sh`)
- OpenClaw skill manifest (`skill.json`)
- Skill execution wrapper (`run.sh`)
- No external dependencies (stdlib only)

### Technical Details
- Python 3.x compatible
- Uses OpenCode CLI (`opencode`)
- NDJSON event stream parsing
- JSON-based configuration and state
- Session management via OpenCode sessions
- Plan agent for task planning
- Build agent for execution

### Supported Operations
- Task planning and analysis
- Code exploration and examination
- File creation and editing
- Code refactoring
- Bug fixing
- Documentation generation
- Test creation
- And any OpenCode-supported operation

## Future Enhancements

### Planned Features
- [ ] Additional approval modes (per-action approval)
- [ ] Regex-based policy rules
- [ ] AST analysis for complex validations
- [ ] Integration with notification systems (Slack, Discord, Email)
- [ ] Web UI for approval workflows
- [ ] Enhanced logging and observability
- [ ] Metrics and statistics tracking
- [ ] Multiple project support
- [ ] Rollback capabilities
- [ ] Dry-run mode

### Community Contributions
We welcome contributions! Areas of interest:
- Notification integrations
- Additional OpenClaw commands
- Enhanced policy rules
- UI/UX improvements
- Documentation improvements
- Testing and bug reports

## Installation Requirements

### Prerequisites
- Python 3.x
- OpenCode CLI tool
- Git (for installation)
- OpenClaw (optional, for skill integration)

### Compatibility
- ✅ Linux
- ✅ macOS
- ✅ Windows (with bash/WSL)
- ✅ OpenClaw skill system
- ✅ Standalone usage

## Version History

### [1.0.0] - 2024-02-20
- Initial release with full feature set
- OpenClaw skill compatibility
- Complete documentation suite
- Approval workflow implementation
- Policy enforcement system
- State management
- Error handling

---

## Contributing

See [README.md](README.md) for contribution guidelines.

## License

See project root for license information.

## Support

- **Issues**: https://github.com/shasankp000/OpenClawde-Dev/issues
- **Documentation**: See README.md and WORKFLOW_EXAMPLE.md
- **Quick Start**: See QUICKSTART.md

---

**Note**: Version numbers follow [Semantic Versioning](https://semver.org/).