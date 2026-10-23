# -*- coding: utf-8 -*-
import urllib.request, urllib.error, json, time, sys, base64, io

BASE = "http://localhost:8000"
PASS, FAIL = [], []

def req(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def check(name, condition, detail=""):
    if condition:
        PASS.append(name)
        print(f"  PASS  {name}")
    else:
        FAIL.append(name)
        print(f"  FAIL  {name}  ---  {detail}")

ts = int(time.time())
username = f"tester_{ts}"
email    = f"tester_{ts}@archivision.ai"
password = "Archivision2024"

print("\n=== ARCHIVISION STUDIO - FULL API TEST ===\n")

# 1. Root
print("[1] Root endpoint")
s, b = req("GET", "/")
check("GET /", s == 200)
check("status=operational", b.get("status") == "operational")

# 2. Register
print("\n[2] Registration")
s, b = req("POST", "/auth/register", {"username": username, "email": email, "password": password})
check("POST /auth/register -> 200", s == 200, b)
check("Returns username", b.get("username") == username)
check("Returns id", "id" in b)
user_id = b.get("id")

# 3. Duplicate register blocked
print("\n[3] Duplicate blocked")
s, b = req("POST", "/auth/register", {"username": username, "email": email, "password": password})
check("Duplicate -> 400", s == 400)

# 4. Login
print("\n[4] Login")
s, b = req("POST", "/auth/login", {"username": username, "password": password})
check("POST /auth/login -> 200", s == 200, b)
check("Returns access_token", "access_token" in b)
token = b.get("access_token", "")

# 5. Wrong password blocked
print("\n[5] Wrong password blocked")
s, b = req("POST", "/auth/login", {"username": username, "password": "wrongpass"})
check("Wrong password -> 401", s == 401)

# 6. /auth/me
print("\n[6] Auth /me")
s, b = req("GET", "/auth/me", token=token)
check("GET /auth/me -> 200", s == 200, b)
check("Correct username returned", b.get("username") == username)

# 7. No token blocked
print("\n[7] Auth guard")
s, b = req("GET", "/auth/me")
check("No token -> 401", s == 401)

# 8. Create project
print("\n[8] Create project")
s, b = req("POST", "/projects/", {"title": "Test Arch Project"}, token=token)
check("POST /projects/ -> 200", s == 200, b)
check("Returns project title", b.get("title") == "Test Arch Project")
check("Returns project id", "id" in b)
pid = b.get("id")

# 9. List projects
print("\n[9] List projects")
s, b = req("GET", "/projects/", token=token)
check("GET /projects/ -> 200", s == 200)
check("Returns list", isinstance(b, list))
check("Project in list", any(p["id"] == pid for p in b))

# 10. Get project by id
print("\n[10] Get project by id")
s, b = req("GET", f"/projects/{pid}", token=token)
check(f"GET /projects/{pid} -> 200", s == 200)

# 11. Update project
print("\n[11] Update project")
s, b = req("PUT", f"/projects/{pid}", {"title": "Updated Title", "canvas_json_state": "{}"}, token=token)
check("PUT /projects/:id -> 200", s == 200, b)
check("Title updated", b.get("title") == "Updated Title")

# 12. Get renders (empty)
print("\n[12] Render history")
s, b = req("GET", f"/projects/{pid}/renders", token=token)
check("GET /projects/:id/renders -> 200", s == 200)
check("Returns list", isinstance(b, list))

# 13. Tunnel status
print("\n[13] Tunnel status")
s, b = req("GET", "/synthesis/tunnel-status")
check("GET /synthesis/tunnel-status -> 200", s == 200, b)
check("Returns connected field", "connected" in b)

# 14. Text-to-Image generation (local fallback)
print("\n[14] Text-to-Image generation (local fallback)")
payload = {
    "project_id": pid,
    "generation_mode": "text",
    "positive_prompt": "minimalist interior, natural light, 8k",
    "negative_prompt": "blurry, deformed",
    "style_preset": "Minimalist",
    "seed": 42,
    "num_inference_steps": 10,
    "guidance_scale": 7.5,
    "controlnet_conditioning_scale": 0.8,
}
s, b = req("POST", "/synthesis/generate", payload, token=token)
check("POST /synthesis/generate (text) -> 200", s == 200, b)
check("Returns rendered_image_b64", bool(b.get("rendered_image_b64")))
check("Returns seed_used", b.get("seed_used") is not None)
check("Returns latency", b.get("inference_latency_seconds") is not None)

# 15. Sketch-to-Image generation (local fallback)
print("\n[15] Sketch-to-Image generation (local fallback)")
from PIL import Image
img = Image.new("RGB", (512, 512), "white")
buf = io.BytesIO()
img.save(buf, format="PNG")
sketch_b64 = base64.b64encode(buf.getvalue()).decode()

payload_sk = {
    "project_id": pid,
    "generation_mode": "sketch",
    "positive_prompt": "brutalist concrete building",
    "negative_prompt": "",
    "style_preset": "Brutalism",
    "seed": 99,
    "num_inference_steps": 10,
    "guidance_scale": 7.5,
    "controlnet_conditioning_scale": 0.8,
    "sketch_b64": sketch_b64,
}
s, b = req("POST", "/synthesis/generate", payload_sk, token=token)
check("POST /synthesis/generate (sketch) -> 200", s == 200, b)
check("Returns rendered_image_b64", bool(b.get("rendered_image_b64")))
check("Returns IoU score", b.get("edge_similarity_score") is not None)
check("Returns edge_overlay_b64", bool(b.get("edge_overlay_b64")))

# 16. Delete project
print("\n[16] Delete project")
s, b = req("DELETE", f"/projects/{pid}", token=token)
check("DELETE /projects/:id -> 200", s == 200)

# Summary
print("\n==========================================")
print(f"  PASSED : {len(PASS)}/{len(PASS)+len(FAIL)}")
print(f"  FAILED : {len(FAIL)}/{len(PASS)+len(FAIL)}")
if FAIL:
    print("\n  FAILURES:")
    for f in FAIL:
        print(f"    ✗ {f}")
else:
    print("\n  ALL TESTS PASSED")
print("==========================================\n")
sys.exit(0 if not FAIL else 1)
