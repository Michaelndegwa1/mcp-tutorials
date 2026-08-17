# Calculator MCP Server (Python)

A feature-rich **Model Context Protocol (MCP)** server for mathematical calculations, scientific functions, unit conversions, financial metrics, and statistical analysis.

Built with Python 3.10+, the official `mcp` SDK (`FastMCP`), and `sympy`. Supports both **`stdio`** (Claude Desktop) and **`sse`** (Claude Web / Remote HTTP Connectors) transport modes.

---

## 🚀 Features & Exposed Tools

- **`evaluate_math_expression`**: Evaluates custom mathematical expressions safely using SymPy (e.g. `2 * (3 + 4)`, `sqrt(144) + sin(pi / 2)`, `log(100, 10)`, `5^3`).
- **`perform_arithmetic`**: Basic arithmetic (`add`, `subtract`, `multiply`, `divide`) on arrays of numbers.
- **`scientific_calculation`**: Powers, roots (`sqrt`, `cbrt`), factorials, logarithms (`log`, `ln`), and trigonometric functions (`sin`, `cos`, `tan`).
- **`convert_unit`**: Physical unit conversions (Length, Mass/Weight, Temperature, Volume, Time).
- **`financial_calculator`**: Simple interest, Compound interest, Loan EMI calculations, and Percentages.
- **`calculate_statistics`**: Summary statistics (`mean`, `median`, `mode`, `variance`, `stdev`, `summary`).

---

## 📦 Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Run Automated Unit Tests**:
   ```bash
   pytest
   ```

---

## 💻 1. Connecting to Claude Desktop (Stdio Mode)

Your `claude_desktop_config.json` has been automatically created at:
`C:\Users\ADMIN\AppData\Roaming\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "calculator": {
      "command": "C:\\Users\\ADMIN\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
      "args": [
        "-m",
        "calculator_mcp.server"
      ],
      "env": {
        "PYTHONPATH": "E:/mcp tutorials"
      }
    }
  }
}
```

### Usage in Claude Desktop:
1. Fully exit and restart **Claude Desktop**.
2. Open a chat and look for the **🔨 (hammer/tools icon)** at the bottom right of the message bar.
3. Ask Claude: *"What is sqrt(144) + sin(pi / 2)?"* or *"Convert 100 degC to degF"*.

---

## 🌐 2. Connecting to Claude Web & Remote Web Clients (SSE HTTP Mode)

To run the Calculator MCP as a web HTTP service (for web-based platforms, web connectors, or remote AI agents):

1. **Start the SSE Web Server**:
   ```bash
   python -m calculator_mcp.server --transport sse --port 8000
   ```

2. **Web Client Configuration**:
   ```json
   {
     "mcpServers": {
       "calculator-web": {
         "serverUrl": "http://localhost:8000/sse"
       }
     }
   }
   ```

3. **Public Tunneling for Remote Web Apps (Optional)**:
   If your web client (like remote Claude Web) is hosted outside your local network, expose port 8000 using `ngrok` or `localtunnel`:
   ```bash
   npx localtunnel --port 8000
   # Or using ngrok:
   ngrok http 8000
   ```
   Then use the generated public HTTPS URL: `https://<your-subdomain>.loca.lt/sse` in your Web MCP connector configuration.

---

## 🔍 Interactive Testing via Web Interface (MCP Inspector)

You can launch the official Model Context Protocol interactive Web Inspector UI to visually test all tools in your browser:

```bash
mcp dev calculator_mcp/server.py
```

Or via Node:
```bash
npx @modelcontextprotocol/inspector@0.4.1 python -m calculator_mcp.server
```
