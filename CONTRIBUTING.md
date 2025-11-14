# 🤝 Contributing to Pioneer Chat Example

Thank you for your interest in contributing! This project is meant to be an educational example, and we welcome improvements, bug fixes, and new ideas.

## Ways to Contribute

### 1. Report Issues
- Found a bug? Open an issue!
- Have a suggestion? We'd love to hear it!
- Documentation unclear? Let us know!

### 2. Improve Documentation
- Fix typos or unclear instructions
- Add more examples
- Translate to other languages

### 3. Add Features
Some ideas:
- Voice input/output
- Document upload for ingestion
- Multi-user support
- Deployment guides
- Docker support
- Different LLM integrations (Anthropic, Gemini, etc.)

### 4. Fix Bugs
- Check open issues
- Submit a PR with a fix
- Add tests if applicable

## Development Setup

1. Fork the repository
2. Clone your fork
3. Follow the setup instructions in SETUP.md
4. Create a branch for your changes: `git checkout -b feature/my-feature`
5. Make your changes
6. Test thoroughly
7. Commit with clear messages
8. Push and open a Pull Request

## Code Style

### Python
- Follow PEP 8
- Use meaningful variable names
- Add docstrings for functions
- Keep functions focused and small

### JavaScript/React
- Use functional components
- Keep components modular
- Use meaningful prop names
- Add comments for complex logic

## Testing Your Changes

Before submitting:

1. **Backend**: Ensure it starts without errors
   ```bash
   python backend/main.py
   ```

2. **Frontend**: Ensure it builds without errors
   ```bash
   cd frontend && npm run build
   ```

3. **Functionality**: Test the chat flow end-to-end

4. **Documentation**: Update README if you changed behavior

## Pull Request Process

1. **Description**: Clearly describe what your PR does
2. **Testing**: Explain how you tested it
3. **Screenshots**: Add screenshots for UI changes
4. **Documentation**: Update docs if needed
5. **Small PRs**: Keep changes focused on one thing

## Questions?

Open an issue for discussion before starting major work!

## License

By contributing, you agree your contributions will be licensed under the MIT License.

---

Thank you for helping make this project better! 🚀
