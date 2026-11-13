"""The dashboard re-scores in JavaScript. Check it agrees with the Python engine."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from sre import config, cli

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(shutil.which("node"), "node not installed")
class ParityTest(unittest.TestCase):
    def test_js_matches_python(self):
        cfg = config.load()
        _, scored, _, _ = cli.run(cfg)
        html = (ROOT / "dashboard" / "index.html").read_text()
        engine = re.search(r"/\*ENGINE_START\*/(.*?)/\*ENGINE_END\*/", html, re.S).group(1)
        accounts = [{k: v for k, v in r.items() if k != "result"} for r in scored]
        script = engine + "\nconst cfg=" + json.dumps(cfg) + ";const accs=" + json.dumps(accounts) + \
            ";const rows=accs.map(a=>({...a,r:scoreAccount(a,cfg)}));" + \
            "console.log(JSON.stringify({rows:rows.map(x=>[x.r.churn_probability,x.r.band,x.r.expansion.pipeline_value,x.r.primary_driver]),glide:glidePath(cfg,rows)}));"
        res = json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)
        _, _, _, summary = cli.run(cfg)
        for qp, qj in zip(summary["glide"]["quarters"], res["glide"]["quarters"]):
            self.assertAlmostEqual(qp["total_floor"], qj["total_floor"], delta=2)
            self.assertAlmostEqual(qp["total_expected"], qj["total_expected"], delta=2)
        for r, (p, band, pipe, drv) in zip(scored, res["rows"]):
            self.assertAlmostEqual(r["result"]["churn_probability"], p, places=2, msg=r["id"])
            self.assertEqual(r["result"]["band"], band, r["id"])
            self.assertAlmostEqual(r["result"]["expansion"]["pipeline_value"], pipe, delta=1, msg=r["id"])
            self.assertEqual(r["result"]["primary_driver"], drv, r["id"])


if __name__ == "__main__":
    unittest.main()
