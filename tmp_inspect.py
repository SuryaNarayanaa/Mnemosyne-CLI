import asyncio
import json
from mnemosyne.mcp.github_client import list_tools_full, call_tool
import keyring

_pat = keyring.get_password('mnemosyne.github.mcp', 'pat')
if not _pat:
    raise SystemExit('PAT missing')
pat: str = _pat

async def main():
    data = await list_tools_full(pat)
    schema = data.get('list_repositories', {}).get('inputSchema')
    print('list_repositories schema:')
    print(json.dumps(schema, indent=2))
    try:
        result = await call_tool(pat, 'list_repositories', {})
    except Exception as exc:
        print('call_tool error type:', type(exc).__name__)
        print('call_tool error:', exc)
    else:
        print('call_tool result:', result)

asyncio.run(main())
