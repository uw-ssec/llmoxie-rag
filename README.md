# project-template

Blank project repository template for General SSEC projects.

This includes some default
[community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file#supported-file-types)
such as a code of conduct and license file.

## Prerequisites

This project uses [Pixi](https://pixi.sh) for dependency management and task
execution. Install Pixi by following the
[installation instructions](https://pixi.sh/latest/#installation).

## Getting Started

### GitHub Codespaces / Dev Containers

The repository ships a [`.devcontainer/`](.devcontainer/) configuration. Open it
in GitHub Codespaces (or VS Code Dev Containers) to get a container with Pixi
and the Claude Code, Codex, Copilot CLI, and OpenCode agent CLIs preinstalled;
the Pixi environment is installed and auto-activated on first start.

### Installation

Install dependencies:

```bash
# Install dependencies (Pixi will automatically create the environment)
pixi install
```

### Onboarding

For first-time setup, use the onboarding environment to configure your
development environment:

```bash
pixi run -e onboard onboard
```

This will:

- Install pre-commit hooks in your git repository
- Set up shell completion for ssec-cli
- Run the SSEC onboarding process

## Project Structure

This project is organized using Pixi features for modular dependency management:

- **`pre-commit`**: Code quality and consistency checks
- **`gh-cli`**: GitHub CLI for repository interactions
- **`okf`**: The `okf` CLI for reading and writing project memory in
  `knowledge/`
- **`onboard`**: Tools for project onboarding and setup

## Available Environments

- **`default`**: Standard development environment with pre-commit hooks, GitHub
  CLI, and the `okf` CLI
- **`onboard`**: Extended environment including onboarding tools

## Development

### Using Different Environments

Switch between environments as needed:

```bash
# Use default environment
pixi shell

# Use onboard environment
pixi shell -e onboard
```

### Adding Dependencies

Conda packages come from a single channel, the prefix.dev mirror of conda-forge
(`https://prefix.dev/conda-forge`).

Edit `pixi.toml` to add new dependencies:

```toml
[dependencies]
your-package = ">=1.0.0"
```

Then run:

```bash
pixi install
```

or

Directly add packages (this will edit the pixi toml and install):

```bash
pixi add your-package
```

## AI Agents

The template is set up for AI coding agents such as Claude Code, Codex, Copilot,
Cursor, and Gemini CLI:

- [`AGENTS.md`](AGENTS.md) is the agent entry point. It points to the rules in
  [`.agents/rules/`](.agents/rules/), which agents load on demand.
- [`.agents/skills/`](.agents/skills/) holds task skills such as `commit`,
  `push`, `create-pr`, `merge-pr`, and `okf-memory`; `.claude/skills` links
  there so Claude Code finds them.
- [`knowledge/`](knowledge/) is project memory: an OKF bundle that agents read
  and write with `pixi run okf`, as the `okf-memory` skill describes.

A project that doesn't want project memory can remove the `okf` feature from the
`default` environment in `pixi.toml`, then delete `.agents/skills/okf-memory/`
and `knowledge/`.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of
conduct and the process for submitting pull requests. If you use AI tools while
contributing, read the [AI Policy](AI_POLICY.md) first: it covers disclosure,
review responsibility, and how to credit AI assistance in commits.

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE)
file.
