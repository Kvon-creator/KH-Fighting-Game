"""Talk to the Blender MCP add-on's socket (localhost:9876) when the plugin's own MCP server is not connected.
Start Blender with the add-on's server running (nothing is saved to the preferences):
  blender.exe <file.blend> --python-expr "import bpy, addon_utils; addon_utils.enable('blender_mcp');
                                          bpy.context.scene.blendermcp_auto_start_server = True"
Usage: python blender_mcp_client.py <command> [json params]     e.g. get_scene_info
       python blender_mcp_client.py code <file.py>              runs the file's Python inside the open Blender
"""
import json
import socket
import sys

cmd = sys.argv[1]
if cmd == 'code':
    cmd, params = 'execute_code', {'code': open(sys.argv[2], encoding='utf-8').read()}
else:
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
s = socket.create_connection(('localhost', 9876), timeout=180)
s.sendall(json.dumps({'type': cmd, 'params': params}).encode('utf-8'))
buf = b''
while True:
    chunk = s.recv(65536)
    if not chunk:
        break
    buf += chunk
    try:
        out = json.loads(buf.decode('utf-8'))
        break
    except ValueError:
        continue
print(json.dumps(out, indent=1)[:6000])
