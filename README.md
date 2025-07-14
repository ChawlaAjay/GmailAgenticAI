# Gmail MCP Server

An implementation of the Model Context Protocol (MCP) server for Gmail integration, enabling AI agents to interact with Gmail accounts through a standardized interface.

## Features

- **Gmail Integration**: Secure access to Gmail accounts using OAuth2
- **MCP Protocol Support**: Standardized interface for AI agent interactions
- **Resource Access**: Read inbox, sent items, and labels
- **Tool Operations**: Send emails, search messages, manage labels
- **Secure Authentication**: OAuth2 flow with automatic token refresh
- **Robust Logging**: Comprehensive logging with configurable levels

## Prerequisites

- Python 3.8+
- Gmail account
- Google Cloud Platform project with Gmail API enabled
- OAuth 2.0 credentials for desktop application

## Installation

1. Clone the repository:
```sh
git clone https://github.com/ChawlaAjay/GmailAgenticAI.git
cd GmailAgenticAI
```

2. Create and activate virtual environment:
```sh
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```sh
pip install -r requirements.txt
```

4. Set up Google Cloud credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download `credentials.json` and place in `config/` directory

## Usage

1. Start the MCP server:
```sh
python main.py
```

2. First run will open browser for Gmail OAuth authentication
3. After authentication, the server will start handling MCP requests

## Available MCP Resources

- `gmail://inbox` - Access Gmail inbox messages
- `gmail://sent` - Access sent messages
- `gmail://labels` - Access Gmail labels

## Available MCP Tools

- `send_email` - Send new emails
- `search_emails` - Search messages using Gmail query syntax
- `get_message` - Get full message content
- `mark_as_read` - Mark messages as read
- `add_label` - Add labels to messages

## Project Structure

```
├──gmail_mcp_server/
    ├── main.py
    ├── requirements.txt
    ├── README.md
    ├── config/
    │   ├── __init__.py
    │   ├── settings.py
    │   └── credentials.json
    ├── auth/
    │   ├── __init__.py
    │   ├── gmail_auth.py
    │   └── token.json
    ├── handlers/
    │   ├── __init__.py
    │   ├── resource_handlers.py
    │   ├── tool_handlers.py
    │   └── message_handlers.py
    ├── models/
    │   ├── __init__.py
    │   └── gmail_models.py
    ├── utils/
    │   ├── __init__.py
    │   ├── email_utils.py
    │   └── logging_config.py
    └── server/
    ├── __init__.py
    └── mcp_server.py
```

## Security

- Uses OAuth 2.0 for secure authentication
- Credentials stored locally in `auth/token.json`
- Token refresh handled automatically
- All communication uses HTTPS

## Development

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Model Context Protocol (MCP) Specification](https://github.com/microsoft/mcp)
