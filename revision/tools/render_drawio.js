// Render a .drawio file (uncompressed mxGraphModel) to PDF and PNG with mxGraph in headless Chromium.
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const xml = fs.readFileSync(process.argv[2], 'utf8');
  const out = path.resolve(process.argv[3]);
  const src = path.resolve('node_modules/mxgraph/javascript/src');
  const lib = path.resolve('node_modules/mxgraph/javascript/mxClient.js');
  fs.writeFileSync('page.html', `<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;padding:0;background:#fff} #g{position:relative;overflow:visible}</style>
<script>var mxBasePath='file://${src}'; var mxLoadResources=false; var mxLoadStylesheets=false;</script>
<script src="file://${lib}"></script></head><body><div id="g"></div></body></html>`);
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 3 });
  await page.goto('file://' + path.resolve('page.html'));
  const dims = await page.evaluate((xml) => {
    const doc = mxUtils.parseXml(xml);
    const model = doc.getElementsByTagName('mxGraphModel')[0];
    const container = document.getElementById('g');
    const graph = new mxGraph(container);
    graph.setHtmlLabels(true); graph.setEnabled(false);
    new mxCodec(model.ownerDocument).decode(model, graph.getModel());
    const b = graph.getGraphBounds();
    graph.view.setTranslate(-b.x + 1, -b.y + 1);
    const w = Math.ceil(b.width + 2), h = Math.ceil(b.height + 2);
    container.style.width = w + 'px'; container.style.height = h + 'px';
    return { w, h };
  }, xml);
  await page.pdf({ path: out, width: dims.w + 'px', height: dims.h + 'px', printBackground: true, pageRanges: '1' });
  await page.screenshot({ path: out.replace(/\.pdf$/, '.png'), clip: { x: 0, y: 0, width: dims.w, height: dims.h } });
  console.log(JSON.stringify(dims));
  await browser.close();
})();
